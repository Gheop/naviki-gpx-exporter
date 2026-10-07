"""
Tests du cache de token : Firefox n'est lancé que si le cache manque ou expire
"""

import json
import os
import stat
from unittest.mock import MagicMock, patch

import naviki_exporter  # noqa: E402  (chargé par conftest.py)

CACHE = naviki_exporter.TOKEN_CACHE_NAME


def write_cache(config, username, token):
    (config / CACHE).write_text(json.dumps({"username": username, "token": token}))


def run_main(tmp_path, list_statuses, login_token="fresh-token"):
    """Lance main() en mode identifiants ; renvoie (session, mock de login)."""
    session = MagicMock()
    session.headers = {}
    responses = [
        MagicMock(status_code=code, json=lambda: {"ways": []}) for code in list_statuses
    ]
    session.get.side_effect = responses
    argv = ["prog", "--username", "alice", "--password", "pw"]
    argv += ["--output", str(tmp_path / "traces")]
    with (
        patch("sys.argv", argv),
        patch("naviki_exporter.requests.Session", return_value=session),
        patch(
            "naviki_exporter.get_oauth_token_with_selenium", return_value=login_token
        ) as login,
    ):
        naviki_exporter.main()
    return session, login


def test_cached_token_skips_firefox(tmp_path, isolated_config_dir):
    write_cache(isolated_config_dir, "alice", "cached-token")

    session, login = run_main(tmp_path, [200])

    login.assert_not_called()
    assert session.headers["Authorization"] == "Bearer cached-token"


def test_cache_of_other_account_is_ignored(tmp_path, isolated_config_dir):
    write_cache(isolated_config_dir, "bob", "bob-token")

    session, login = run_main(tmp_path, [200])

    login.assert_called_once()
    assert session.headers["Authorization"] == "Bearer fresh-token"


def test_expired_cache_triggers_login(tmp_path, isolated_config_dir):
    write_cache(isolated_config_dir, "alice", "expired-token")

    session, login = run_main(tmp_path, [401, 200])

    login.assert_called_once()
    assert session.get.call_count == 2
    assert session.headers["Authorization"] == "Bearer fresh-token"
    cached = json.loads((isolated_config_dir / CACHE).read_text())
    assert cached == {"username": "alice", "token": "fresh-token"}


def test_login_writes_private_cache(tmp_path, isolated_config_dir):
    run_main(tmp_path, [200])

    path = isolated_config_dir / CACHE
    assert json.loads(path.read_text())["token"] == "fresh-token"
    # Windows ignore les droits POSIX : chmod n'y règle que la lecture seule
    if os.name != "nt":
        assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_failed_login_writes_no_cache(tmp_path, isolated_config_dir):
    with patch("naviki_exporter.sys.exit", side_effect=SystemExit(1)):
        try:
            run_main(tmp_path, [200], login_token=None)
        except SystemExit:
            pass

    assert not (isolated_config_dir / CACHE).exists()


def test_corrupt_cache_is_ignored(tmp_path, isolated_config_dir):
    (isolated_config_dir / CACHE).write_text("{pas du json")

    _, login = run_main(tmp_path, [200])

    login.assert_called_once()
