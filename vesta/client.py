from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from urllib.parse import urljoin

import requests

__all__ = ["Client"]


class Session(requests.Session):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    def request(self, method: str, url: str, *args, **kwargs) -> requests.Response:
        url = urljoin(self.base_url, url)
        return super().request(method, url, *args, **kwargs)


class Client:
    """Vestaboard API Client"""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        *,
        base_url: str = "https://platform.vestaboard.com",
        headers: Optional[Mapping[str, str]] = None,
    ):
        self.session = Session(base_url)
        self.session.headers.update(
            {
                "X-Vestaboard-Api-Key": api_key,
                "X-Vestaboard-Api-Secret": api_secret,
            }
        )
        if headers:
            self.session.headers.update(headers)

    def __repr__(self):
        return f"{type(self).__name__}(base_url={self.session.base_url!r})"

    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Lists all subscriptions to which the viewer has access."""
        r = self.session.get("/subscriptions")
        r.raise_for_status()
        return r.json().get("subscriptions", [])

    def get_viewer(self) -> Dict[str, Any]:
        """Describes the currently authenticated viewer."""
        r = self.session.get("/viewer")
        r.raise_for_status()
        return r.json()

    def post_message(
        self,
        subscription_id: str,
        message: Union[str, list],
    ) -> Dict[str, Any]:
        """Post of a new message to a subscription.

        The authenticated viewer must have access to the subscription.

        `message` can be either a string of text or a two-dimensional array of
        character codes representing the exact positions of characters on the
        board.

        If text is specified, lines will be centered horizontally and
        vertically if possible. Character codes will be inferred for
        alphanumeric and punctuation, or can be explicitly specified in-line in
        the message with curly braces containing the character code.
        """
        if isinstance(message, str):
            data = {"text": message}
        elif isinstance(message, list):
            data = {"characters": message}
        else:
            raise TypeError(f"unsupported message type: {type(message)}")

        r = self.session.post(
            f"/subscriptions/{subscription_id}/message",
            json=data,
        )
        r.raise_for_status()
        return r.json()
