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
    return config
