import pytest


@pytest.fixture(autouse=True)
def isolated_config_dir(tmp_path, monkeypatch):
    """Empêche les tests de lire ou d'écrire le .env réel du dépôt."""
    config = tmp_path / "config"
    config.mkdir()
    monkeypatch.setenv("NAVIKI_CONFIG_DIR", str(config))
    return config
