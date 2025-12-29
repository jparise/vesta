from __future__ import annotations

import http.client
import io
import urllib.error

import pytest

from vesta.http import Client
from vesta.http import HTTPError
from vesta.http import Response


@pytest.fixture
def mock_response(monkeypatch):
    """Fixture that returns a factory for mocking successful HTTP responses."""

    def _mock(client, status_code=200, body=b"{}"):
        last_request = {}

        def fake_open(request):
            last_request.update(
                {
                    "method": request.get_method(),
                    "url": request.get_full_url(),
                    "data": request.data,
                    "headers": dict(request.headers),
                }
            )

            class FakeSocket:
                def __init__(self, response_bytes):
                    self._file = io.BytesIO(response_bytes)

                def makefile(self, mode):
                    return self._file

            response_text = (
                f"HTTP/1.1 {status_code} OK\r\nContent-Length: {len(body)}\r\n\r\n"
            ).encode() + body

            sock = FakeSocket(response_text)
            resp = http.client.HTTPResponse(sock)
            resp.begin()

            return resp

        monkeypatch.setattr(client._opener, "open", fake_open)
        return last_request

    return _mock


class TestClient:
    def test_success(self, mock_response):
        client = Client(base_url="https://api.example.com")
        mock = mock_response(client, status_code=200, body=b'{"result":"ok"}')

        resp = client.request("GET", "/test")

        assert resp.status == 200
        assert resp.json() == {"result": "ok"}
        assert mock["url"] == "https://api.example.com/test"

    def test_http_error(self, monkeypatch):
        """Test that urllib.error.HTTPError is raised and propagated correctly."""
        client = Client(base_url="https://api.example.com")

        def raise_error(request):
            raise urllib.error.HTTPError(
                request.get_full_url(), 404, "Not Found", {}, None
            )

        monkeypatch.setattr(client._opener, "open", raise_error)

        with pytest.raises(HTTPError) as exc_info:
            client.request("GET", "/not-found")

        assert exc_info.value.code == 404
        assert exc_info.value.url == "https://api.example.com/not-found"


class TestResponse:
    def test_json_success(self):
        resp = Response(200, b'{"key": "value"}', {})
        assert resp.json() == {"key": "value"}

    def test_json_decode_error(self):
        resp = Response(200, b"not json", {})
        assert resp.json() is None
        assert resp.json(default={}) == {}
        assert resp.json(default=[]) == []
