"""
Tests de bout en bout : main() avec la vraie pile requests, seul le réseau
est simulé (responses)
"""

import pathlib
import subprocess
import sys
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
import responses

import naviki_exporter  # noqa: E402  (chargé par conftest.py)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "naviki-gpx-exporter.py"
LIST_URL = "https://www.naviki.org/naviki/api/v6/Way/2/findUserWaysByFilter/"
DOWNLOAD_URL = "https://www.naviki.org/naviki/api/v6/Util/wayToFileWithUser/"

WAYS = [
    {"uuid": "uuid-1", "title": "16/10/2025, 07:20", "crdate": 1760599200},
    {"uuid": "uuid-2", "title": "Balade à Paris", "crdate": 1760599200},
]


def run_main(out_dir):
    argv = ["prog", "--token", "Bearer tok-123", "--output", str(out_dir)]
    with patch("sys.argv", argv):
        naviki_exporter.main()


@responses.activate
def test_full_run_writes_every_gpx(tmp_path):
    responses.add(responses.GET, LIST_URL, json={"ways": WAYS})
    responses.add(responses.GET, LIST_URL, json={"ways": []})
    responses.add(responses.POST, DOWNLOAD_URL, body='<?xml version="1.0"?><gpx/>')
    out_dir = tmp_path / "traces"

    run_main(out_dir)

    assert sorted(p.name for p in out_dir.iterdir()) == [
        "2025-10-16_07-20_Naviki.gpx",
        "2025-10-16_07-20_UTC_Balade_à_Paris.gpx",
    ]
    first_list = responses.calls[0].request
    query = parse_qs(urlparse(first_list.url).query)
    assert query["limit"] == [str(naviki_exporter.WAYS_PAGE_SIZE)]
    assert query["offset"] == ["0"]
    assert first_list.headers["Authorization"] == "Bearer tok-123"
    downloads = [c.request for c in responses.calls if c.request.method == "POST"]
    assert len(downloads) == 2
    # le token passe dans le formulaire, pas dans l'en-tête
    assert all("oauth_token=tok-123" in r.body for r in downloads)
    assert all("Authorization" not in r.headers for r in downloads)


@responses.activate
def test_second_run_downloads_nothing(tmp_path):
    out_dir = tmp_path / "traces"
    out_dir.mkdir()
    (out_dir / "2025-10-16_07-20_Naviki.gpx").write_text("<?xml")
    (out_dir / "2025-10-16_07-20_UTC_Balade_à_Paris.gpx").write_text("<?xml")
    responses.add(responses.GET, LIST_URL, json={"ways": WAYS})
    responses.add(responses.GET, LIST_URL, json={"ways": []})

    run_main(out_dir)

    assert all(c.request.method == "GET" for c in responses.calls)


@responses.activate
def test_rejected_token_exits_1(tmp_path):
    responses.add(responses.GET, LIST_URL, status=401, json={})

    with pytest.raises(SystemExit) as exit_info:
        run_main(tmp_path / "traces")

    assert exit_info.value.code == 1


class TestCommandLine:
    """Interface en ligne de commande, dans un vrai processus"""

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
        )

    def test_help_command(self):
        result = self.run_cli("--help")

        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "--username" in result.stdout
        assert "--token" in result.stdout

    def test_missing_password(self):
        result = self.run_cli("--username", "test")

        assert result.returncode != 0
        assert "password" in result.stderr.lower()
