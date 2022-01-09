import pytest
from requests_mock import Mocker

from vesta.chars import COLS
from vesta.chars import ROWS
from vesta.client import Client


@pytest.fixture
def client():
    return Client("key", "secret")


def test_base_url():
    base_url = "https://www.example.com"
    client = Client("key", "secret", base_url=base_url)
    assert client.session.base_url == base_url
    assert base_url in repr(client)


def test_headers():
    client = Client("key", "secret", headers={"User-Agent": "Vesta"})
    assert client.session.headers["X-Vestaboard-Api-Key"] == "key"
    assert client.session.headers["X-Vestaboard-Api-Secret"] == "secret"
    assert client.session.headers["User-Agent"] == "Vesta"


def test_get_subscriptions(client: Client, requests_mock: Mocker):
    subscriptions = [True]
    requests_mock.get(
        "https://platform.vestaboard.com/subscriptions",
        json={"subscriptions": subscriptions},
    )
    assert client.get_subscriptions() == subscriptions


def test_get_viewer(client: Client, requests_mock: Mocker):
    viewer = {"_id": 1}
    requests_mock.get("https://platform.vestaboard.com/viewer", json=viewer)
    assert client.get_viewer() == viewer


def test_post_message_text(client: Client, requests_mock: Mocker):
    text = "abc"

    def match_json(request) -> bool:
        return request.json() == {"text": text}

    requests_mock.post(
        "https://platform.vestaboard.com/subscriptions/sub_id/message",
        additional_matcher=match_json,
        json={},
    )
    client.post_message("sub_id", text)


def test_post_message_list(client: Client, requests_mock: Mocker):
    chars = [[0] * COLS] * ROWS

    def match_json(request) -> bool:
        return request.json() == {"characters": chars}

    requests_mock.post(
        "https://platform.vestaboard.com/subscriptions/sub_id/message",
        additional_matcher=match_json,
        json={},
    )
    client.post_message("sub_id", chars)


def test_post_message_list_dimensions(client: Client):
    with pytest.raises(ValueError, match=rf"expected a \({ROWS}, {COLS}\) array"):
        client.post_message("sub_id", [])


def test_post_message_type(client: Client):
    with pytest.raises(TypeError, match=r"unsupported message type"):
        client.post_message("sub_id", True)  # type: ignore
