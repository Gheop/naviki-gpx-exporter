"""
Tests du téléchargement parallèle : mêmes résultats que l'ancien mode séquentiel
"""

from unittest.mock import MagicMock, patch

import naviki_exporter  # noqa: E402  (chargé par conftest.py)

SAME_MINUTE = "16/10/2025, 07:20"


def run_main(out, ways, gpx_responses):
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
        naviki_exporter.main()
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
    session = run_main(out_dir, ways, ["not xml", "<?xml second"])

    out = capsys.readouterr().out
    assert session.post.call_count == 2
    assert "✅ Téléchargés: 1" in out
    assert "❌ Erreurs: 1" in out
    assert (out_dir / "2025-10-16_07-20_Naviki.gpx").read_text() == "<?xml second"
