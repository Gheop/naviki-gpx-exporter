"""
Tests du téléchargement parallèle : mêmes résultats que l'ancien mode séquentiel
"""

import time
from unittest.mock import MagicMock, patch

import pytest

import naviki_exporter  # noqa: E402  (chargé par conftest.py)

SAME_MINUTE = "16/10/2025, 07:20"


def run_main(out, ways, gpx_responses, expected_exit=None):
    session = MagicMock()
    session.get.side_effect = [
        MagicMock(status_code=200, json=lambda: {"ways": ways}),
        MagicMock(status_code=200, json=lambda: {"ways": []}),
    ]
    session.post.side_effect = [MagicMock(text=t) for t in gpx_responses]
    argv = ["prog", "--token", "tok", "--output", str(out)]
    with (
        patch("sys.argv", argv),
        patch("naviki_exporter.requests.Session", return_value=session),
    ):
        if expected_exit is None:
            naviki_exporter.main()
        else:
            with pytest.raises(SystemExit) as exit_info:
                naviki_exporter.main()
            assert exit_info.value.code == expected_exit
    return session


def test_many_ways_all_downloaded(tmp_path, capsys):
    out_dir = tmp_path / "traces"
    ways = [
        {"uuid": f"u{i}", "title": f"{i + 1:02d}/10/2025, 07:20", "crdate": 0}
        for i in range(20)
    ]
    session = run_main(out_dir, ways, ["<?xml ok"] * 20)

    assert session.post.call_count == 20
    assert len(list(out_dir.iterdir())) == 20
    assert "✅ Téléchargés: 20" in capsys.readouterr().out


def test_duplicate_name_skipped_after_success(tmp_path, capsys):
    out_dir = tmp_path / "traces"
    ways = [
        {"uuid": "a", "title": SAME_MINUTE, "crdate": 0},
        {"uuid": "b", "title": SAME_MINUTE, "crdate": 0},
    ]
    session = run_main(out_dir, ways, ["<?xml first"])

    out = capsys.readouterr().out
    assert session.post.call_count == 1
    assert "✅ Téléchargés: 1" in out
    assert "⏭️  Ignorés (déjà présents): 1" in out
    assert (out_dir / "2025-10-16_07-20_Naviki.gpx").read_text() == "<?xml first"


def test_duplicate_name_retried_after_failure(tmp_path, capsys):
    out_dir = tmp_path / "traces"
    ways = [
        {"uuid": "a", "title": SAME_MINUTE, "crdate": 0},
        {"uuid": "b", "title": SAME_MINUTE, "crdate": 0},
    ]
    session = run_main(out_dir, ways, ["not xml", "<?xml second"], expected_exit=1)

    out = capsys.readouterr().out
    assert session.post.call_count == 2
    assert "✅ Téléchargés: 1" in out
    assert "❌ Erreurs: 1" in out
    assert (out_dir / "2025-10-16_07-20_Naviki.gpx").read_text() == "<?xml second"


def test_every_request_has_a_timeout(tmp_path):
    ways = [{"uuid": "a", "title": "16/10/2025, 07:20", "crdate": 0}]
    session = run_main(tmp_path / "traces", ways, ["<?xml ok"])

    for call in session.get.call_args_list + session.post.call_args_list:
        assert call.kwargs["timeout"] == naviki_exporter.HTTP_TIMEOUT


def test_network_error_on_list_exits_1(tmp_path, capsys):
    session = MagicMock()
    session.get.side_effect = naviki_exporter.requests.Timeout("read timed out")
    argv = ["prog", "--token", "tok", "--output", str(tmp_path / "traces")]
    with (
        patch("sys.argv", argv),
        patch("naviki_exporter.requests.Session", return_value=session),
        pytest.raises(SystemExit) as exit_info,
    ):
        naviki_exporter.main()

    assert exit_info.value.code == 1
    assert "Erreur réseau sur la liste des trajets" in capsys.readouterr().out


def test_ctrl_c_cancels_queued_downloads(tmp_path):
    """Ctrl-C pendant la pagination : seuls les téléchargements démarrés finissent"""
    ways = [
        {"uuid": f"u{i}", "title": f"{i + 1:02d}/10/2025, 07:20", "crdate": 0}
        for i in range(20)
    ]
    session = MagicMock()
    session.get.side_effect = [
        MagicMock(status_code=200, json=lambda: {"ways": ways}),
        KeyboardInterrupt,
    ]

    def slow_download(*args, **kwargs):
        time.sleep(0.2)
        return MagicMock(text="<?xml ok")

    session.post.side_effect = slow_download
    argv = ["prog", "--token", "tok", "--output", str(tmp_path / "traces")]
    with (
        patch("sys.argv", argv),
        patch("naviki_exporter.requests.Session", return_value=session),
        pytest.raises(SystemExit) as exit_info,
    ):
        naviki_exporter.main()

    assert exit_info.value.code == 130
    time.sleep(0.5)  # laisse finir les téléchargements déjà démarrés
    assert session.post.call_count <= naviki_exporter.DOWNLOAD_WORKERS
