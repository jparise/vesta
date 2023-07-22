from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from vesta.chars import COLS
from vesta.chars import ROWS
from vesta.clients import Client
from vesta.clients import LocalClient
from vesta.clients import ReadWriteClient

if TYPE_CHECKING:
    from respx import MockRouter


@pytest.fixture
def client():
    return Client("key", "secret")


@pytest.fixture
def local_client():
    return LocalClient("key")


@pytest.fixture
def rw_client():
    return ReadWriteClient("key")


class TestClient:
    def test_base_url(self):
        base_url = "https://www.example.com"
        client = Client("key", "secret", base_url=base_url)
        assert client.http.base_url == base_url
        assert base_url in repr(client)

    def test_headers(self):
        client = Client("key", "secret", headers={"User-Agent": "Vesta"})
        assert client.http.headers["X-Vestaboard-Api-Key"] == "key"
        assert client.http.headers["X-Vestaboard-Api-Secret"] == "secret"
        assert client.http.headers["User-Agent"] == "Vesta"

    def test_get_subscriptions(self, client: Client, respx_mock: MockRouter):
        subscriptions = [True]
        respx_mock.get("https://platform.vestaboard.com/subscriptions").respond(
            json={"subscriptions": subscriptions}
        )
        assert client.get_subscriptions() == subscriptions

    def test_get_viewer(self, client: Client, respx_mock: MockRouter):
        viewer = {"_id": 1}
        respx_mock.get("https://platform.vestaboard.com/viewer").respond(json=viewer)
        assert client.get_viewer() == viewer

    def test_post_message_text(self, client: Client, respx_mock: MockRouter):
        text = "abc"
        respx_mock.post(
            "https://platform.vestaboard.com/subscriptions/sub_id/message",
            json={"text": text},
        ).respond(json={})
        client.post_message("sub_id", text)

    def test_post_message_list(self, client: Client, respx_mock: MockRouter):
        chars = [[0] * COLS] * ROWS
        respx_mock.post(
            "https://platform.vestaboard.com/subscriptions/sub_id/message",
            json={"characters": chars},
        ).respond(json={})
        client.post_message("sub_id", chars)

    def test_post_message_list_dimensions(self, client: Client):
        with pytest.raises(ValueError, match=rf"expected a \({COLS}, {ROWS}\) array"):
            client.post_message("sub_id", [])

    def test_post_message_type(self, client: Client):
        with pytest.raises(TypeError, match=r"unsupported message type"):
            client.post_message("sub_id", True)  # type: ignore


class TestLocalClient:
    def test_base_url(self):
        base_url = "http://example.local"
        local_client = LocalClient("key", base_url=base_url)
        assert local_client.http.base_url == base_url
        assert base_url in repr(local_client)

    def test_api_key_init(self):
        local_api_key = "key"
        local_client = LocalClient(local_api_key)
        assert local_client.enabled
        assert local_client.api_key == local_api_key

    def test_api_key_property(self):
        local_client = LocalClient()
        assert not local_client.enabled
        assert local_client.api_key is None

        local_api_key = "key"
        local_client.api_key = local_api_key
        assert local_client.enabled
        assert local_client.api_key == local_api_key

    def test_enable(self, respx_mock: MockRouter):
        local_client = LocalClient()
        local_api_key = "key"
        respx_mock.post("http://vestaboard.local:7000/local-api/enablement").respond(
            json={"apiKey": local_api_key},
        )
        rv = local_client.enable("enablement_token")
        assert rv == local_api_key
        assert local_client.api_key == local_api_key
        assert local_client.enabled
        assert respx_mock.calls.called
        assert (
            respx_mock.calls.last.request.headers.get(
                "X-Vestaboard-Local-Api-Enablement-Token"
            )
            == "enablement_token"
        )

    def test_enable_failure(self, respx_mock: MockRouter):
        local_client = LocalClient()
        respx_mock.post("http://vestaboard.local:7000/local-api/enablement")
        rv = local_client.enable("enablement_token")
        assert rv is None
        assert not local_client.api_key
        assert not local_client.enabled

    def test_not_enabled(self):
        local_client = LocalClient()
        with pytest.raises(RuntimeError, match=r"Local API has not been enabled"):
            local_client.read_message()
        with pytest.raises(RuntimeError, match=r"Local API has not been enabled"):
            local_client.write_message([])

    def test_read_message(self, local_client: LocalClient, respx_mock: MockRouter):
        chars = [[0] * COLS] * ROWS
        respx_mock.get("http://vestaboard.local:7000/local-api/message").respond(
            json={"message": chars}
        )
        message = local_client.read_message()
        assert message == chars

    def test_read_message_empty(
        self, local_client: LocalClient, respx_mock: MockRouter
    ):
        respx_mock.get("http://vestaboard.local:7000/local-api/message")
        message = local_client.read_message()
        assert message is None

    def test_write_message(self, local_client: LocalClient, respx_mock: MockRouter):
        chars = [[0] * COLS] * ROWS
        respx_mock.post("http://vestaboard.local:7000/local-api/message").respond(201)
        assert local_client.write_message(chars)
        assert respx_mock.calls.called
        assert respx_mock.calls.last.request.content == json.dumps(chars).encode()

    def test_write_message_dimensions(self, local_client: LocalClient):
        with pytest.raises(ValueError, match=rf"expected a \({COLS}, {ROWS}\) array"):
            local_client.write_message([])


class TestReadWriteClient:
    def test_base_url(self):
        base_url = "http://example.local"
        rw_client = ReadWriteClient("key", base_url=base_url)
        assert rw_client.http.base_url == base_url
        assert base_url in repr(rw_client)

    def test_headers(self):
        client = ReadWriteClient("key", headers={"User-Agent": "Vesta"})
        assert client.http.headers["X-Vestaboard-Read-Write-Key"] == "key"
        assert client.http.headers["User-Agent"] == "Vesta"

    def test_read_message(self, rw_client: ReadWriteClient, respx_mock: MockRouter):
        chars = [[0] * COLS] * ROWS
        respx_mock.get("https://rw.vestaboard.com/").respond(
            json={"currentMessage": {"layout": json.dumps(chars)}},
        )
        message = rw_client.read_message()
        assert message == chars

    def test_read_message_empty(
        self, rw_client: ReadWriteClient, respx_mock: MockRouter
    ):
        respx_mock.get("https://rw.vestaboard.com/")
        message = rw_client.read_message()
        assert message is None

    def test_write_message_text(
        self, rw_client: ReadWriteClient, respx_mock: MockRouter
    ):
        text = "abc"
        respx_mock.post("https://rw.vestaboard.com/").respond(200)
        rw_client.write_message(text)

    def test_write_message_list(
        self, rw_client: ReadWriteClient, respx_mock: MockRouter
    ):
        chars = [[0] * COLS] * ROWS
        respx_mock.post("https://rw.vestaboard.com/").respond(200)
        assert rw_client.write_message(chars)
        assert respx_mock.calls.called
        assert respx_mock.calls.last.request.content == json.dumps(chars).encode()

    def test_write_message_list_dimensions(self, rw_client: ReadWriteClient):
        with pytest.raises(ValueError, match=rf"expected a \({COLS}, {ROWS}\) array"):
            rw_client.write_message([])

    def test_write_message_type(self, rw_client: ReadWriteClient):
        with pytest.raises(TypeError, match=r"unsupported message type"):
            rw_client.write_message(True)  # type: ignore
