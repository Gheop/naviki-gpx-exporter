"""
Tests du login HTTP sans navigateur, et du repli sur Selenium
"""

import argparse
from unittest.mock import patch

import pytest
import requests
import responses

import naviki_exporter  # noqa: E402  (chargé par conftest.py)

pytestmark = pytest.mark.http_login

OAUTH = naviki_exporter.OAUTH_URL
DISPATCHER = naviki_exporter.AJAX_DISPATCHER_URL
REDIRECT = naviki_exporter.OAUTH_REDIRECT_URI


def mock_login_flow(location, fesession_body):
    responses.add(responses.GET, OAUTH, body="<form></form>")
    headers = {"Location": location} if location else {}
    responses.add(
        responses.POST, OAUTH, status=302 if location else 200, headers=headers
    )
    responses.add(responses.GET, DISPATCHER, json=fesession_body)


@responses.activate
def test_http_login_returns_access_token():
    mock_login_flow(
        f"{REDIRECT}?code=abc",
        {"status": True, "accessToken": "at-1", "refreshToken": "rt-1"},
    )

    assert naviki_exporter.get_oauth_token_http("alice", "pw") == "at-1"

    post = responses.calls[1].request
    assert "username=alice" in post.body and "password=pw" in post.body
    exchange = responses.calls[2].request.url
    assert "request%5Baction%5D=feSession" in exchange
    assert "request%5Barguments%5D%5Bcode%5D=abc" in exchange


@responses.activate
def test_rejected_password_returns_none():
    # le serveur réaffiche le formulaire, sans redirection ni code
    mock_login_flow(None, {})

    assert naviki_exporter.get_oauth_token_http("alice", "wrong") is None
    assert len(responses.calls) == 2


@responses.activate
def test_refused_code_exchange_returns_none():
    mock_login_flow(f"{REDIRECT}?code=abc", {"status": False})

    assert naviki_exporter.get_oauth_token_http("alice", "pw") is None


@responses.activate
def test_network_error_returns_none():
    responses.add(responses.GET, OAUTH, body=requests.ConnectionError("down"))

    assert naviki_exporter.get_oauth_token_http("alice", "pw") is None


def make_args(visible=False):
    return argparse.Namespace(
        username="alice",
        password="pw",
        visible=visible,
        headless=not visible,
        output="./traces",
    )


def test_login_uses_http_and_skips_firefox():
    with (
        patch.object(naviki_exporter, "get_oauth_token_http", return_value="at-http"),
        patch.object(naviki_exporter, "get_oauth_token_with_selenium") as selenium,
    ):
        assert naviki_exporter.login_or_exit(make_args()) == "at-http"

    selenium.assert_not_called()


def test_login_falls_back_to_firefox():
    with (
        patch.object(naviki_exporter, "get_oauth_token_http", return_value=None),
        patch.object(
            naviki_exporter, "get_oauth_token_with_selenium", return_value="at-ff"
        ) as selenium,
    ):
        assert naviki_exporter.login_or_exit(make_args()) == "at-ff"

    selenium.assert_called_once_with("alice", "pw", headless=True)


def test_visible_mode_goes_straight_to_firefox():
    with (
        patch.object(naviki_exporter, "get_oauth_token_http") as http,
        patch.object(
            naviki_exporter, "get_oauth_token_with_selenium", return_value="at-ff"
        ),
    ):
        assert naviki_exporter.login_or_exit(make_args(visible=True)) == "at-ff"

    http.assert_not_called()
