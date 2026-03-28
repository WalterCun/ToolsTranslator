"""Unit tests for HttpClient — retry behavior, error handling."""

import json
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

import pytest

from translator.adapters.http_client import HttpClient, SimpleHttpResponse


class TestSimpleHttpResponse:
    def test_json_returns_payload(self) -> None:
        resp = SimpleHttpResponse(200, {"key": "value"})
        assert resp.json() == {"key": "value"}

    def test_raise_for_status_ok(self) -> None:
        resp = SimpleHttpResponse(200, {})
        resp.raise_for_status()  # should not raise

    def test_raise_for_status_error(self) -> None:
        resp = SimpleHttpResponse(500, {})
        with pytest.raises(HTTPError):
            resp.raise_for_status()

    def test_raise_for_status_400(self) -> None:
        resp = SimpleHttpResponse(400, {})
        with pytest.raises(HTTPError):
            resp.raise_for_status()


class TestHttpClientRetry:
    @patch("translator.adapters.http_client.urlopen")
    def test_retry_on_timeout(self, mock_urlopen: MagicMock) -> None:
        """Should retry on TimeoutError."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"ok": true}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # First two calls timeout, third succeeds
        mock_urlopen.side_effect = [
            TimeoutError("timeout"),
            TimeoutError("timeout"),
            mock_response,
        ]

        client = HttpClient(retries=3, base_delay=0.01)
        resp = client.get("http://example.com")
        assert resp.json() == {"ok": True}
        assert mock_urlopen.call_count == 3

    @patch("translator.adapters.http_client.urlopen")
    def test_no_retry_on_404(self, mock_urlopen: MagicMock) -> None:
        """Should NOT retry on HTTP 404 (client error)."""
        mock_urlopen.side_effect = HTTPError(
            url="http://example.com", code=404, msg="Not Found", hdrs=None, fp=None
        )

        client = HttpClient(retries=3, base_delay=0.01)
        with pytest.raises(HTTPError) as exc_info:
            client.get("http://example.com")
        assert exc_info.value.code == 404
        assert mock_urlopen.call_count == 1  # no retry

    @patch("translator.adapters.http_client.urlopen")
    def test_retry_on_500(self, mock_urlopen: MagicMock) -> None:
        """Should retry on HTTP 500 (server error)."""
        mock_urlopen.side_effect = HTTPError(
            url="http://example.com", code=500, msg="Internal Server Error", hdrs=None, fp=None
        )

        client = HttpClient(retries=3, base_delay=0.01)
        with pytest.raises(HTTPError):
            client.get("http://example.com")
        assert mock_urlopen.call_count == 3

    @patch("translator.adapters.http_client.urlopen")
    def test_retry_on_429(self, mock_urlopen: MagicMock) -> None:
        """Should retry on HTTP 429 (Too Many Requests)."""
        mock_urlopen.side_effect = HTTPError(
            url="http://example.com", code=429, msg="Too Many Requests", hdrs=None, fp=None
        )

        client = HttpClient(retries=3, base_delay=0.01)
        with pytest.raises(HTTPError):
            client.get("http://example.com")
        assert mock_urlopen.call_count == 3

    @patch("translator.adapters.http_client.urlopen")
    def test_retry_on_url_error(self, mock_urlopen: MagicMock) -> None:
        """Should retry on URLError (connection refused, DNS, etc)."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"ok": true}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [
            URLError("connection refused"),
            mock_response,
        ]

        client = HttpClient(retries=3, base_delay=0.01)
        resp = client.get("http://example.com")
        assert resp.json() == {"ok": True}

    @patch("translator.adapters.http_client.urlopen")
    def test_all_retries_exhausted(self, mock_urlopen: MagicMock) -> None:
        """Should raise after all retries exhausted."""
        mock_urlopen.side_effect = URLError("always fails")

        client = HttpClient(retries=3, base_delay=0.01)
        with pytest.raises(URLError):
            client.get("http://example.com")
        assert mock_urlopen.call_count == 3
