#!/usr/bin/env python3
"""
Tests pour l'analyse des arguments de ligne de commande
"""

import importlib.util
import os
import sys

import pytest
from unittest.mock import patch

# Add parent directory to path to import the main script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

spec = importlib.util.spec_from_file_location(
    "naviki_exporter",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "naviki-gpx-exporter.py",
    ),
)
naviki_exporter = importlib.util.module_from_spec(spec)


class TestParseArguments:
    """Tests pour la fonction parse_arguments"""

    def test_parse_with_username_password(self, monkeypatch):
        """Test parsing avec username et password"""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "naviki-gpx-exporter.py",
                "--username",
                "testuser",
                "--password",
                "pass123",
            ],
        )

        spec.loader.exec_module(naviki_exporter)
        args = naviki_exporter.parse_arguments()

        assert args.username == "testuser"
        assert args.password == "pass123"
        assert args.token is None
        assert args.headless is True  # Default

    def test_parse_with_token(self, monkeypatch):
        """Test parsing avec token OAuth"""
        monkeypatch.setattr(
            sys,
            "argv",
            ["naviki-gpx-exporter.py", "--token", "abc123-token-xyz"],
        )

        spec.loader.exec_module(naviki_exporter)
        args = naviki_exporter.parse_arguments()

        assert args.token == "abc123-token-xyz"
        assert args.username is None
        assert args.password is None

    def test_parse_with_output_dir(self, monkeypatch):
        """Test parsing avec dossier de sortie personnalisé"""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "naviki-gpx-exporter.py",
                "--username",
                "user",
                "--password",
                "pass",
                "--output",
                "/custom/path",
            ],
        )

        spec.loader.exec_module(naviki_exporter)
        args = naviki_exporter.parse_arguments()

        assert args.output == "/custom/path"

    def test_parse_with_custom_types(self, monkeypatch):
        """Test parsing avec types de routes personnalisés"""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "naviki-gpx-exporter.py",
                "--username",
                "user",
                "--password",
                "pass",
                "--types",
                "recordedMy",
            ],
        )

        spec.loader.exec_module(naviki_exporter)
        args = naviki_exporter.parse_arguments()

        assert args.types == "recordedMy"

    def test_parse_with_headless_flag(self, monkeypatch):
        """Test parsing avec flag headless explicite"""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "naviki-gpx-exporter.py",
                "--username",
                "user",
                "--password",
                "pass",
                "--headless",
            ],
        )

        spec.loader.exec_module(naviki_exporter)
        args = naviki_exporter.parse_arguments()

        assert args.headless is True
        assert args.visible is False

    def test_parse_with_visible_flag(self, monkeypatch):
        """Test parsing avec flag visible"""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "naviki-gpx-exporter.py",
                "--username",
                "user",
                "--password",
                "pass",
                "--visible",
            ],
        )

        spec.loader.exec_module(naviki_exporter)
        args = naviki_exporter.parse_arguments()

        assert args.visible is True

    def test_parse_username_without_password_fails(self, monkeypatch):
        """Test que username sans password échoue"""
        monkeypatch.setattr(
            sys, "argv", ["naviki-gpx-exporter.py", "--username", "user"]
        )

        spec.loader.exec_module(naviki_exporter)

        with pytest.raises(SystemExit):
            naviki_exporter.parse_arguments()

    def test_parse_login_alias(self, monkeypatch):
        """Test que --login fonctionne comme alias de --username"""
        monkeypatch.setattr(
            sys,
            "argv",
            ["naviki-gpx-exporter.py", "--login", "testuser", "--password", "pass123"],
        )

        spec.loader.exec_module(naviki_exporter)
        args = naviki_exporter.parse_arguments()

        assert args.username == "testuser"
        assert args.password == "pass123"

    def test_parse_default_values(self, monkeypatch):
        """Test les valeurs par défaut"""
        monkeypatch.setattr(
            sys,
            "argv",
            ["naviki-gpx-exporter.py", "--username", "user", "--password", "pass"],
        )

        spec.loader.exec_module(naviki_exporter)
        args = naviki_exporter.parse_arguments()

        assert args.output == "./traces"  # Default output
        assert args.types == "routedAll,recordedMy,recordedOthers"  # Default types
        assert args.headless is True  # Default headless


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestEnvironmentCredentials:
    """Identifiants depuis l'environnement, sans les passer en argument"""

    def parse(self, argv):
        # module partagé chargé par conftest.py, pas la copie privée du fichier
        exporter = sys.modules["naviki_exporter"]
        with patch("sys.argv", ["prog", *argv]):
            return exporter.parse_arguments()

    def test_environment_provides_credentials(self, monkeypatch):
        monkeypatch.setenv("NAVIKI_USERNAME", "alice")
        monkeypatch.setenv("NAVIKI_PASSWORD", "s3cret")

        args = self.parse([])

        assert (args.username, args.password) == ("alice", "s3cret")

    def test_command_line_wins_over_environment(self, monkeypatch):
        monkeypatch.setenv("NAVIKI_USERNAME", "alice")
        monkeypatch.setenv("NAVIKI_PASSWORD", "s3cret")

        args = self.parse(["--username", "bob", "--password", "pw"])

        assert (args.username, args.password) == ("bob", "pw")

    def test_environment_wins_over_env_file(self, monkeypatch, isolated_config_dir):
        (isolated_config_dir / ".env").write_text(
            "NAVIKI_USERNAME=from_file\nNAVIKI_PASSWORD=file_pw\n"
        )
        monkeypatch.setenv("NAVIKI_PASSWORD", "env_pw")

        args = self.parse([])

        assert (args.username, args.password) == ("from_file", "env_pw")
