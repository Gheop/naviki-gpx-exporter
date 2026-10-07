import importlib.util
import pathlib
import sys

import pytest

# Le script n'est pas importable (tiret dans le nom) : on le charge une seule
# fois sous le nom naviki_exporter. Un rechargement par fichier de test créait
# plusieurs objets module, et patch("naviki_exporter.x") ne visait que le dernier.
_spec = importlib.util.spec_from_file_location(
    "naviki_exporter",
    pathlib.Path(__file__).resolve().parent.parent / "naviki-gpx-exporter.py",
)
_module = importlib.util.module_from_spec(_spec)
sys.modules["naviki_exporter"] = _module
_spec.loader.exec_module(_module)


@pytest.fixture(autouse=True)
def isolated_config_dir(tmp_path, monkeypatch):
    """Empêche les tests de lire ou d'écrire le .env réel du dépôt."""
    config = tmp_path / "config"
    config.mkdir()
    monkeypatch.setenv("NAVIKI_CONFIG_DIR", str(config))
    # Des identifiants exportés dans le shell du développeur fausseraient
    # les tests au même titre qu'un .env
    for name in ("NAVIKI_USERNAME", "NAVIKI_PASSWORD", "NAVIKI_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    return config


@pytest.fixture(autouse=True)
def no_network_login(request, monkeypatch):
    """
    Le login HTTP partirait sur le vrai naviki.org : par défaut il échoue,
    et main() retombe sur Selenium, que les tests simulent déjà.
    Les tests marqués http_login gardent la vraie fonction.
    """
    if request.node.get_closest_marker("http_login") is None:
        monkeypatch.setattr(_module, "get_oauth_token_http", lambda u, p: None)
