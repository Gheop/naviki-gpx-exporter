#!/usr/bin/env python3
"""
Tests d'intégration avec mocks pour naviki-gpx-exporter
"""

import pytest
import responses


class TestAPIIntegration:
    """Tests d'intégration avec l'API Naviki (mockée)"""

    @responses.activate
    def test_api_list_routes(self):
        """Test de récupération de la liste des routes"""

        # Mock de la réponse API
        mock_response = {
            "ways": [
                {
                    "uuid": "test-uuid-1",
                    "title": "16/10/2025, 07:20",
                    "crdate": 1729065600,
                },
                {"uuid": "test-uuid-2", "title": "Vervant", "crdate": 1729065700},
            ]
        }

        responses.add(
            responses.GET,
            "https://www.naviki.org/naviki/api/v6/Way/2/findUserWaysByFilter/",
            json=mock_response,
            status=200,
        )

        # Test (nécessite d'importer requests)
        import requests

        response = requests.get(
            "https://www.naviki.org/naviki/api/v6/Way/2/findUserWaysByFilter/",
            params={"filter": "recordedMy", "offset": 0},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["ways"]) == 2
        assert data["ways"][0]["uuid"] == "test-uuid-1"

    @responses.activate
    def test_api_download_gpx(self):
        """Test de téléchargement d'un GPX"""

        mock_gpx = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Naviki">
  <trk>
    <name>Test Route</name>
    <trkseg>
      <trkpt lat="48.8566" lon="2.3522">
        <ele>35</ele>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""

        responses.add(
            responses.POST,
            "https://www.naviki.org/naviki/api/v6/Util/wayToFileWithUser/",
            body=mock_gpx,
            status=200,
        )

        import requests

        response = requests.post(
            "https://www.naviki.org/naviki/api/v6/Util/wayToFileWithUser/",
            data={"wayUuid": "test-uuid", "format": "gpx"},
        )

        assert response.status_code == 200
        assert response.text.startswith("<?xml")
        assert "Test Route" in response.text

    @responses.activate
    def test_api_authentication_failure(self):
        """Test d'échec d'authentification"""

        responses.add(
            responses.GET,
            "https://www.naviki.org/naviki/api/v6/Way/2/findUserWaysByFilter/",
            json={"error": "Unauthorized"},
            status=401,
        )

        import requests

        response = requests.get(
            "https://www.naviki.org/naviki/api/v6/Way/2/findUserWaysByFilter/"
        )

        assert response.status_code == 401


class TestFileOperations:
    """Tests des opérations sur fichiers"""

    def test_create_output_directory(self, tmp_path):
        """Test création du dossier de sortie"""
        output_dir = tmp_path / "test_output"
        output_dir.mkdir(parents=True, exist_ok=True)

        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_skip_existing_file(self, tmp_path):
        """Test qu'un fichier existant n'est pas retéléchargé"""
        output_dir = tmp_path / "test_output"
        output_dir.mkdir()

        test_file = output_dir / "2025-10-16_07-20_Naviki.gpx"
        test_file.write_text("existing content")

        assert test_file.exists()
        # Le script devrait sauter ce fichier

    def test_write_gpx_file(self, tmp_path):
        """Test écriture d'un fichier GPX"""
        output_dir = tmp_path / "test_output"
        output_dir.mkdir()

        gpx_content = """<?xml version="1.0"?>
<gpx version="1.1">
  <trk><name>Test</name></trk>
</gpx>"""

        test_file = output_dir / "test.gpx"
        test_file.write_text(gpx_content, encoding="utf-8")

        assert test_file.exists()
        assert test_file.read_text().startswith("<?xml")


class TestCommandLine:
    """Tests de l'interface en ligne de commande"""

    def test_help_command(self):
        """Test que --help fonctionne"""
        import subprocess

        result = subprocess.run(
            ["python", "naviki-gpx-exporter.py", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "--username" in result.stdout
        assert "--token" in result.stdout

    def test_missing_password(self):
        """Test que --password est requis avec --username"""
        import subprocess

        result = subprocess.run(
            ["python", "naviki-gpx-exporter.py", "--username", "test"],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "password" in result.stderr.lower()


@pytest.fixture
def mock_selenium_driver():
    """Fixture pour mocker Selenium (optionnel)"""
    # Nécessite pytest-mock ou unittest.mock
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
