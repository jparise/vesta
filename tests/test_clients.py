from __future__ import annotations

from json import dumps as json_dumps

import pytest

from vesta.chars import COLS
from vesta.chars import ROWS
from vesta.clients import Client
from vesta.clients import LocalClient
from vesta.clients import ReadWriteClient
from vesta.clients import SubscriptionClient
from vesta.clients import VBMLClient
from vesta.http import Response
from vesta.vbml import Component


@pytest.fixture
def mock_response(monkeypatch):
    """Fixture that returns a factory for mocking HTTP responses."""

    def _mock(client, status_code=200, body=None, json=None):
        last_request = {}

        if body is not None:
            response_body = body
        elif json is not None:
            response_body = json_dumps(json).encode("utf-8")
        else:
            response_body = b"{}"

        def fake_request(method, url, **kwargs):
            last_request.update({"method": method, "url": url, **kwargs})
            return Response(status_code, response_body, {})

        monkeypatch.setattr(client.http, "request", fake_request)
        return last_request

    return _mock


@pytest.fixture
def client():
    return Client("key", "secret")


@pytest.fixture
def local_client():
    return LocalClient("key")


@pytest.fixture
def rw_client():
    return ReadWriteClient("key")


@pytest.fixture
def subscription_client():
    return SubscriptionClient("key", "secret")


@pytest.fixture
def vbml_client():
    return VBMLClient()


@pytest.mark.filterwarnings("ignore:Vestaboard has deprecated the Platform API")
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

    def test_get_subscriptions(self, client: Client, mock_response):
        subscriptions = [True]
        mock_response(client, json={"subscriptions": subscriptions})
        assert client.get_subscriptions() == subscriptions

    def test_get_viewer(self, client: Client, mock_response):
        viewer = {"_id": 1}
        mock_response(client, json=viewer)
        assert client.get_viewer() == viewer

    def test_post_message_text(self, client: Client, mock_response):
        text = "abc"
        mock = mock_response(client)
        client.post_message("sub_id", text)

        assert mock["url"] == "/subscriptions/sub_id/message"
        assert mock["json"] == {"text": text}

    def test_post_message_list(self, client: Client, mock_response):
        chars = [[0] * COLS] * ROWS
        mock = mock_response(client)
        client.post_message("sub_id", chars)

        assert mock["url"] == "/subscriptions/sub_id/message"
        assert mock["json"] == {"characters": chars}

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

    def test_enable(self, mock_response):
        local_client = LocalClient()
        local_api_key = "key"
        mock = mock_response(local_client, json={"apiKey": local_api_key})
        rv = local_client.enable("enablement_token")
        assert rv == local_api_key
        assert local_client.api_key == local_api_key
        assert local_client.enabled

        assert mock["url"] == "/local-api/enablement"
        assert (
            mock["headers"]["X-Vestaboard-Local-Api-Enablement-Token"]
            == "enablement_token"
        )

    def test_enable_failure(self, mock_response):
        local_client = LocalClient()
        mock_response(local_client)
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

    def test_read_message(self, local_client: LocalClient, mock_response):
        chars = [[0] * COLS] * ROWS
        mock_response(local_client, json={"message": chars})
        message = local_client.read_message()
        assert message == chars

    def test_read_message_empty(self, local_client: LocalClient, mock_response):
        mock_response(local_client)
        message = local_client.read_message()
        assert message is None

    def test_write_message(self, local_client: LocalClient, mock_response):
        chars = [[0] * COLS] * ROWS
        mock = mock_response(local_client, status_code=201, body=b"")
        assert local_client.write_message(chars)

        assert mock["url"] == "/local-api/message"
        assert mock["json"] == chars

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

    def test_read_message(self, rw_client: ReadWriteClient, mock_response):
        chars = [[0] * COLS] * ROWS
        mock_response(rw_client, json={"currentMessage": {"layout": json_dumps(chars)}})
        message = rw_client.read_message()
        assert message == chars

    def test_read_message_empty(self, rw_client: ReadWriteClient, mock_response):
        mock_response(rw_client)
        message = rw_client.read_message()
        assert message is None

    def test_read_message_empty_layout(self, rw_client: ReadWriteClient, mock_response):
        mock_response(rw_client, json={"currentMessage": {"layout": ""}})
        message = rw_client.read_message()
        assert message is None

    def test_write_message_text(self, rw_client: ReadWriteClient, mock_response):
        text = "abc"
        mock_response(rw_client)
        rw_client.write_message(text)

    def test_write_message_list(self, rw_client: ReadWriteClient, mock_response):
        chars = [[0] * COLS] * ROWS
        mock = mock_response(rw_client)
        assert rw_client.write_message(chars)

        assert mock["url"] == ""
        assert mock["json"] == chars

    def test_write_message_list_dimensions(self, rw_client: ReadWriteClient):
        with pytest.raises(ValueError, match=rf"expected a \({COLS}, {ROWS}\) array"):
            rw_client.write_message([])

    def test_write_message_type(self, rw_client: ReadWriteClient):
        with pytest.raises(TypeError, match=r"unsupported message type"):
            rw_client.write_message(True)  # type: ignore


class TestSubscriptionClient:
    def test_base_url(self):
        base_url = "https://www.example.com"
        client = SubscriptionClient("key", "secret", base_url=base_url)
        assert client.http.base_url == base_url
        assert base_url in repr(client)

    def test_headers(self):
        client = SubscriptionClient("key", "secret", headers={"User-Agent": "Vesta"})
        assert client.http.headers["x-vestaboard-api-key"] == "key"
        assert client.http.headers["x-vestaboard-api-secret"] == "secret"
        assert client.http.headers["User-Agent"] == "Vesta"

    def test_get_subscriptions(
        self, subscription_client: SubscriptionClient, mock_response
    ):
        subscriptions = [True]
        mock_response(subscription_client, json=subscriptions)
        assert subscription_client.get_subscriptions() == subscriptions

    def test_send_message_text(
        self, subscription_client: SubscriptionClient, mock_response
    ):
        text = "abc"
        mock = mock_response(subscription_client)
        subscription_client.send_message("sub_id", text)

        assert mock["url"] == "/subscriptions/sub_id/message"
        assert mock["json"] == {"text": text}

    def test_send_message_list(
        self, subscription_client: SubscriptionClient, mock_response
    ):
        chars = [[0] * COLS] * ROWS
        mock = mock_response(subscription_client)
        subscription_client.send_message("sub_id", chars)

        assert mock["url"] == "/subscriptions/sub_id/message"
        assert mock["json"] == {"characters": chars}

    def test_send_message_list_dimensions(
        self, subscription_client: SubscriptionClient
    ):
        with pytest.raises(ValueError, match=rf"expected a \({COLS}, {ROWS}\) array"):
            subscription_client.send_message("sub_id", [])

    def test_send_message_type(self, subscription_client: SubscriptionClient):
        with pytest.raises(TypeError, match=r"unsupported message type"):
            subscription_client.send_message("sub_id", True)  # type: ignore


class TestVBMLClient:
    def test_base_url(self):
        base_url = "http://example.local"
        client = VBMLClient(base_url=base_url)
        assert client.http.base_url == base_url
        assert base_url in repr(client)

    def test_headers(self):
        client = VBMLClient(headers={"User-Agent": "Vesta"})
        assert client.http.headers["User-Agent"] == "Vesta"

    def test_compose(self, vbml_client: VBMLClient, mock_response):
        chars = [[0] * COLS] * ROWS
        mock = mock_response(vbml_client, json=chars)

        component = Component("template")
        props = {"prop": "value"}
        assert vbml_client.compose([component], props=props) == chars

        assert mock["url"] == "/compose"
        assert mock["json"] == {
            "components": [component.asdict()],
            "props": props,
        }

    def test_component_no_components(self, vbml_client: VBMLClient):
        with pytest.raises(ValueError, match=r"expected at least one component"):
            vbml_client.compose([])

    def test_format(self, vbml_client: VBMLClient, mock_response):
        chars = [[0] * COLS] * ROWS
        mock = mock_response(vbml_client, json=chars)

        assert vbml_client.format("message") == chars
        assert mock["url"] == "/format"
