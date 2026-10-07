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


def test_interrupted_write_leaves_no_gpx(tmp_path):
    """Un échec avant le renommage ne laisse aucun faux « déjà présent »"""
    tmp_path.mkdir(exist_ok=True)
    save_path = tmp_path / "2025-10-16_07-20_Naviki.gpx"
    session = MagicMock()
    session.post.return_value = MagicMock(text="<?xml ok")

    with patch("naviki_exporter.os.replace", side_effect=OSError("disk full")):
        ok = naviki_exporter.download_gpx(session, "tok", "u1", save_path)

    assert ok is False
    assert not save_path.exists()

    # le run suivant réécrit le fichier normalement
    assert naviki_exporter.download_gpx(session, "tok", "u1", save_path) is True
    assert save_path.read_text() == "<?xml ok"
    assert [p.name for p in tmp_path.iterdir() if p.suffix == ".part"] == []


def test_main_renames_legacy_file_instead_of_downloading(tmp_path, capsys):
    out_dir = tmp_path / "traces"
    out_dir.mkdir()
    (out_dir / "3001-20-24_00-00_UTC_Naviki.gpx").write_text("<?xml archive")
    ways = [{"uuid": "a", "title": "Gouter30012024", "crdate": 0}]

    session = run_main(out_dir, ways, [])

    session.post.assert_not_called()
    assert [p.name for p in out_dir.iterdir()] == ["2024-01-30_00-00_UTC_Naviki.gpx"]
    out = capsys.readouterr().out
    assert "🔁 Renommé" in out and "⏭️  Ignorés (déjà présents): 1" in out
