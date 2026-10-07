#!/usr/bin/env python3
"""
Tests pour la fonction main et la logique de téléchargement
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import naviki_exporter  # noqa: E402  (chargé par conftest.py)


class TestMainFunction:
    """Tests pour la fonction main avec mocks"""

    @patch("sys.argv", ["prog", "--token", "test-token-123"])
    @patch("naviki_exporter.requests.Session")
    @patch("naviki_exporter.pathlib.Path")
    @patch("builtins.open", new_callable=mock_open)
    # open est simulé : le renommage du .part ne trouverait pas de fichier
    @patch("naviki_exporter.os.replace", lambda src, dst: None)
    def test_main_with_token_success(self, mock_file, mock_path, mock_session):
        """Test main avec token fourni et téléchargement réussi"""

        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ways": [
                {
                    "uuid": "test-uuid-1",
                    "title": "16/10/2025, 07:20",
                    "crdate": 1729065600,
                }
            ]
        }

        # First call returns ways, second call returns empty to stop loop
        mock_session_instance.get.side_effect = [
            mock_response,
            MagicMock(status_code=200, json=lambda: {"ways": []}),
        ]

        # Mock download response
        mock_download = MagicMock()
        mock_download.text = "<?xml version='1.0'?><gpx>test</gpx>"
        mock_session_instance.post.return_value = mock_download

        # Mock path
        mock_output_dir = MagicMock()
        mock_path.return_value = mock_output_dir
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = False
        mock_output_dir.joinpath.return_value = mock_file_path

        # Call main
        naviki_exporter.main()

        # Assertions
        assert mock_session_instance.get.call_count == 2
        mock_session_instance.post.assert_called_once()
        mock_output_dir.mkdir.assert_called_once()

    @patch("sys.argv", ["prog", "--username", "testuser", "--password", "testpass"])
    @patch("naviki_exporter.get_oauth_token_with_selenium")
    @patch("naviki_exporter.sys.exit", side_effect=SystemExit(1))
    def test_main_with_failed_auth(self, mock_exit, mock_auth):
        """Test main quand l'authentification échoue"""

        # Auth fails
        mock_auth.return_value = None

        with pytest.raises(SystemExit):
            naviki_exporter.main()

        # Should call sys.exit(1)
        mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["prog", "--token", "test-token-123"])
    @patch("naviki_exporter.requests.Session")
    @patch("naviki_exporter.pathlib.Path")
    def test_main_with_api_error(self, mock_path, mock_session):
        """Test main avec erreur API"""

        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock API error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_session_instance.get.return_value = mock_response

        # Mock path
        mock_output_dir = MagicMock()
        mock_path.return_value = mock_output_dir

        # Arrêt sur l'erreur, code de sortie 1 pour un cron
        with pytest.raises(SystemExit) as exit_info:
            naviki_exporter.main()

        assert exit_info.value.code == 1
        mock_session_instance.post.assert_not_called()

    @patch("sys.argv", ["prog", "--token", "test-token-123"])
    @patch("naviki_exporter.requests.Session")
    @patch("naviki_exporter.pathlib.Path")
    @patch("builtins.open", new_callable=mock_open)
    def test_main_skip_existing_file(self, mock_file, mock_path, mock_session):
        """Test main ignore les fichiers existants"""

        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ways": [
                {
                    "uuid": "test-uuid-1",
                    "title": "16/10/2025, 07:20",
                    "crdate": 1729065600,
                }
            ]
        }

        mock_session_instance.get.side_effect = [
            mock_response,
            MagicMock(status_code=200, json=lambda: {"ways": []}),
        ]

        # Mock path - file exists
        mock_output_dir = MagicMock()
        mock_path.return_value = mock_output_dir
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True  # File exists
        mock_output_dir.joinpath.return_value = mock_file_path

        # Call main
        naviki_exporter.main()

        # Should not download if file exists
        mock_session_instance.post.assert_not_called()

    @patch("sys.argv", ["prog", "--token", "test-token-123"])
    @patch("naviki_exporter.requests.Session")
    @patch("naviki_exporter.pathlib.Path")
    @patch("builtins.open", new_callable=mock_open)
    # open est simulé : le renommage du .part ne trouverait pas de fichier
    @patch("naviki_exporter.os.replace", lambda src, dst: None)
    def test_main_handle_custom_title(self, mock_file, mock_path, mock_session):
        """Test main avec titre personnalisé (sans date)"""

        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock API response with custom title
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ways": [
                {
                    "uuid": "test-uuid-1",
                    "title": "Route de la Chapelle",  # No date
                    "crdate": 1729065600,
                }
            ]
        }

        mock_session_instance.get.side_effect = [
            mock_response,
            MagicMock(status_code=200, json=lambda: {"ways": []}),
        ]

        # Mock download response
        mock_download = MagicMock()
        mock_download.text = "<?xml version='1.0'?><gpx>test</gpx>"
        mock_session_instance.post.return_value = mock_download

        # Mock path
        mock_output_dir = MagicMock()
        mock_path.return_value = mock_output_dir
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = False
        mock_output_dir.joinpath.return_value = mock_file_path

        # Call main
        naviki_exporter.main()

        # Should still download using crdate
        mock_session_instance.post.assert_called_once()

    @patch("sys.argv", ["prog", "--token", "test-token-123"])
    @patch("naviki_exporter.requests.Session")
    @patch("naviki_exporter.pathlib.Path")
    def test_main_handle_download_error(self, mock_path, mock_session):
        """Test main gère les erreurs de téléchargement"""

        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ways": [
                {
                    "uuid": "test-uuid-1",
                    "title": "16/10/2025, 07:20",
                    "crdate": 1729065600,
                }
            ]
        }

        mock_session_instance.get.side_effect = [
            mock_response,
            MagicMock(status_code=200, json=lambda: {"ways": []}),
        ]

        # Mock download response - invalid GPX
        mock_download = MagicMock()
        mock_download.text = "Error: not a GPX file"  # Doesn't start with <?xml
        mock_session_instance.post.return_value = mock_download

        # Mock path
        mock_output_dir = MagicMock()
        mock_path.return_value = mock_output_dir
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = False
        mock_output_dir.joinpath.return_value = mock_file_path

        # Le téléchargement échoue : pas de plantage, mais code de sortie 1
        with pytest.raises(SystemExit) as exit_info:
            naviki_exporter.main()

        assert exit_info.value.code == 1
        mock_session_instance.post.assert_called_once()

    @patch("sys.argv", ["prog", "--username", "testuser", "--password", "testpass"])
    # pathlib.Path est simulé : le cache de token ne peut pas fonctionner ici
    @patch("naviki_exporter.load_cached_token", lambda username: None)
    @patch("naviki_exporter.save_cached_token", lambda username, token: None)
    @patch("naviki_exporter.requests.Session")
    @patch("naviki_exporter.pathlib.Path")
    @patch("builtins.open", new_callable=mock_open)
    @patch("selenium.webdriver.Firefox")
    @patch("naviki_exporter.time.sleep")
    def test_main_with_username_password(
        self, mock_sleep, mock_firefox, mock_file, mock_path, mock_session
    ):
        """Test main avec username/password (authentification Selenium)"""

        # Mock Firefox to return a token
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver
        mock_driver.execute_script.return_value = "selenium-token-123"

        # Mock form elements
        mock_username_field = MagicMock()
        mock_password_field = MagicMock()
        mock_submit_button = MagicMock()
        mock_driver.find_element.side_effect = [
            mock_password_field,
            mock_submit_button,
        ]

        # Mock WebDriverWait
        with patch("selenium.webdriver.support.ui.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = mock_username_field

            # Setup mock session
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance

            # Mock API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ways": []}
            mock_session_instance.get.return_value = mock_response

            # Mock path
            mock_output_dir = MagicMock()
            mock_path.return_value = mock_output_dir

            # Call main
            naviki_exporter.main()

            # Verify Firefox was called (authentication happened)
            mock_firefox.assert_called_once()

    @patch("sys.argv", ["prog", "--token", "Bearer test-token-123"])
    @patch("naviki_exporter.requests.Session")
    @patch("naviki_exporter.pathlib.Path")
    def test_main_bearer_token_strip(self, mock_path, mock_session):
        """Test main retire le préfixe Bearer du token"""

        # Setup mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ways": []}
        mock_session_instance.get.return_value = mock_response

        # Mock path
        mock_output_dir = MagicMock()
        mock_path.return_value = mock_output_dir

        # Call main
        naviki_exporter.main()

        # Check that Bearer was stripped in the session headers
        calls = mock_session_instance.headers.update.call_args_list
        auth_header = None
        for call in calls:
            if "Authorization" in call[0][0]:
                auth_header = call[0][0]["Authorization"]
                break

        assert auth_header == "Bearer test-token-123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
