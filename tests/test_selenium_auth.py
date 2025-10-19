#!/usr/bin/env python3
"""
Tests pour l'authentification Selenium avec mocks
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "naviki_exporter",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "naviki-gpx-exporter.py",
    ),
)
naviki_exporter = importlib.util.module_from_spec(spec)
# Register in sys.modules so patches can find it
sys.modules['naviki_exporter'] = naviki_exporter
spec.loader.exec_module(naviki_exporter)


class TestSeleniumAuth:
    """Tests pour get_oauth_token_with_selenium avec mocks"""

    @patch("naviki_exporter.webdriver.Firefox")
    def test_successful_authentication_headless(self, mock_firefox):
        """Test authentification réussie en mode headless"""
        # Setup mock driver
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        # Mock localStorage containing the token
        mock_driver.execute_script.return_value = "test-token-12345"

        # Mock form elements
        mock_username_field = MagicMock()
        mock_password_field = MagicMock()
        mock_submit_button = MagicMock()

        mock_driver.find_element.side_effect = [
            mock_password_field,
            mock_submit_button,
        ]

        # Mock WebDriverWait
        with patch("naviki_exporter.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = mock_username_field

            # Call function
            token = naviki_exporter.get_oauth_token_with_selenium(
                "testuser", "testpass", headless=True
            )

            # Assertions
            assert token == "test-token-12345"
            mock_firefox.assert_called_once()
            mock_driver.quit.assert_called_once()

    @patch("naviki_exporter.webdriver.Firefox")
    def test_successful_authentication_visible(self, mock_firefox):
        """Test authentification réussie en mode visible"""
        # Setup mock driver
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        # Mock localStorage containing the token
        mock_driver.execute_script.return_value = "test-token-visible"

        # Mock form elements
        mock_username_field = MagicMock()
        mock_password_field = MagicMock()
        mock_submit_button = MagicMock()

        mock_driver.find_element.side_effect = [
            mock_password_field,
            mock_submit_button,
        ]

        # Mock WebDriverWait
        with patch("naviki_exporter.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = mock_username_field

            # Call function with headless=False
            token = naviki_exporter.get_oauth_token_with_selenium(
                "testuser", "testpass", headless=False
            )

            # Assertions
            assert token == "test-token-visible"
            mock_driver.quit.assert_called_once()

    @patch("naviki_exporter.webdriver.Firefox")
    @patch("naviki_exporter.time.sleep")  # Speed up test
    def test_authentication_timeout(self, mock_sleep, mock_firefox):
        """Test timeout si le token n'apparaît pas"""
        # Setup mock driver
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        # Mock localStorage never returning a token
        mock_driver.execute_script.return_value = None

        # Mock body element for error checking
        mock_body = MagicMock()
        mock_body.text = "normal page content"
        mock_driver.find_element.return_value = mock_body

        # Mock form elements
        mock_username_field = MagicMock()
        mock_password_field = MagicMock()
        mock_submit_button = MagicMock()

        # Mock WebDriverWait
        with patch("naviki_exporter.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = mock_username_field

            # We need to set up find_element to return different things
            def find_element_side_effect(by, value):
                if value == "password":
                    return mock_password_field
                elif value == "submit" or "submit" in str(value):
                    return mock_submit_button
                elif value == "body":
                    return mock_body
                return MagicMock()

            mock_driver.find_element.side_effect = find_element_side_effect

            # Call function - should timeout and return None
            token = naviki_exporter.get_oauth_token_with_selenium(
                "testuser", "testpass", headless=True
            )

            # Assertions
            assert token is None
            mock_driver.quit.assert_called_once()
            mock_driver.save_screenshot.assert_called_once()

    @patch("naviki_exporter.webdriver.Firefox")
    def test_authentication_with_error_page(self, mock_firefox):
        """Test détection d'erreur de connexion"""
        # Setup mock driver
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        # Mock localStorage never returning a token
        mock_driver.execute_script.return_value = None

        # Mock body element with error message
        mock_body = MagicMock()
        mock_body.text = "Error: Invalid credentials"
        mock_driver.find_element.return_value = mock_body

        # Mock form elements
        mock_username_field = MagicMock()
        mock_password_field = MagicMock()

        # Mock WebDriverWait
        with patch("naviki_exporter.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = mock_username_field

            def find_element_side_effect(by, value):
                if value == "password":
                    return mock_password_field
                elif value == "body":
                    return mock_body
                return MagicMock()

            mock_driver.find_element.side_effect = find_element_side_effect

            # Mock time.sleep to speed up test
            with patch("naviki_exporter.time.sleep"):
                token = naviki_exporter.get_oauth_token_with_selenium(
                    "testuser", "wrongpass", headless=True
                )

                # Assertions
                assert token is None
                mock_driver.quit.assert_called_once()

    @patch("naviki_exporter.webdriver.Firefox")
    def test_webdriver_exception(self, mock_firefox):
        """Test gestion des erreurs WebDriver"""
        from selenium.common.exceptions import WebDriverException

        # Make Firefox constructor raise an exception
        mock_firefox.side_effect = WebDriverException(
            "geckodriver not found"
        )

        # Call function
        token = naviki_exporter.get_oauth_token_with_selenium(
            "testuser", "testpass", headless=True
        )

        # Should return None on error
        assert token is None

    @patch("naviki_exporter.webdriver.Firefox")
    def test_timeout_exception(self, mock_firefox):
        """Test gestion du timeout sur le formulaire"""
        from selenium.common.exceptions import TimeoutException

        # Setup mock driver
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        # Mock localStorage returning a token after timeout
        mock_driver.execute_script.return_value = "token-after-timeout"

        # Mock WebDriverWait raising TimeoutException
        with patch("naviki_exporter.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.side_effect = TimeoutException(
                "Form not found"
            )

            # Mock time.sleep to speed up test
            with patch("naviki_exporter.time.sleep"):
                token = naviki_exporter.get_oauth_token_with_selenium(
                    "testuser", "testpass", headless=True
                )

                # Even with timeout, it might get token from localStorage
                assert token == "token-after-timeout"
                mock_driver.quit.assert_called_once()

    @patch("naviki_exporter.webdriver.Firefox")
    def test_form_submit_fallback(self, mock_firefox):
        """Test soumission du formulaire en fallback"""
        # Setup mock driver
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver

        # Mock localStorage containing the token
        mock_driver.execute_script.return_value = "test-token-submit"

        # Mock form elements
        mock_username_field = MagicMock()
        mock_password_field = MagicMock()

        # Mock find_element to not find submit button (triggers fallback)
        def find_element_side_effect(by, value):
            if value == "password":
                return mock_password_field
            raise Exception("Button not found")

        mock_driver.find_element.side_effect = find_element_side_effect

        # Mock WebDriverWait
        with patch("naviki_exporter.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = mock_username_field

            # Call function
            token = naviki_exporter.get_oauth_token_with_selenium(
                "testuser", "testpass", headless=True
            )

            # Should use password_field.submit() as fallback
            assert token == "test-token-submit"
            mock_password_field.submit.assert_called_once()
            mock_driver.quit.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
