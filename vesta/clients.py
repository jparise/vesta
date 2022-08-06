# Copyright (c) 2021-2022 Jon Parise <jon@indelible.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from typing import cast
from urllib.parse import urljoin

import requests

from .chars import COLS
from .chars import ROWS
from .chars import Rows

__all__ = ["Client", "LocalClient"]


class Session(requests.Session):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    def request(
        self,
        method: Union[str, bytes],
        url: Union[str, bytes],
        *args,
        **kwargs,
    ) -> requests.Response:
        url = urljoin(self.base_url, url if isinstance(url, str) else url.decode())
        return super().request(method, url, *args, **kwargs)


class Client:
    """Provides a Vestaboard API client interface.

    Credentials must be provided as an ``api_key`` and ``api_secret``.

    Optionally, an alternate ``base_url`` can be specified, as well as any
    additional HTTP ``headers`` that should be sent with every request
    (such as a custom `User-Agent` header).
    """

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
        message: Union[str, Rows],
    ) -> Dict[str, Any]:
        """Post a new message to a subscription.

        The authenticated viewer must have access to the subscription.

        `message` can be either a string of text or a two-dimensional (6, 22)
        array of character codes representing the exact positions of characters
        on the board.

        If text is specified, lines will be centered horizontally and
        vertically if possible. Character codes will be inferred for
        alphanumeric and punctuation, or can be explicitly specified in-line in
        the message with curly braces containing the character code.

        :raises ValueError: if `message` is a list with unsupported dimensions
        """
        data: Dict[str, Union[str, Rows]]
        if isinstance(message, str):
            data = {"text": message}
        elif isinstance(message, list):
            if len(message) != ROWS or not all(len(row) == COLS for row in message):
                raise ValueError(
                    f"expected a ({ROWS}, {COLS}) array of encoded characters"
                )
            data = {"characters": message}
        else:
            raise TypeError(f"unsupported message type: {type(message)}")

        r = self.session.post(
            f"/subscriptions/{subscription_id}/message",
            json=data,
        )
        r.raise_for_status()
        return r.json()


class LocalClient:
    """Provides a Vestaboard Local API client interface.

    A Local API key is required to read or write messages. This key is obtained
    by enabling the Vestaboard's Local API using a Local API Enablement Token.

    If you've already enabled your Vestaboard's Local API, that key can be
    provided immediately. Otherwise, it can be set after the client is
    constructed by calling :py:meth:`~enable`, which also returns the Local API
    key for future reuse.

    An alternate ``base_url`` can also be specified.

    .. versionadded:: 0.8.0
    """

    def __init__(
        self,
        local_api_key: Optional[str] = None,
        *,
        base_url: str = "http://vestaboard.local:7000",
    ):
        self.session = Session(base_url)
        if local_api_key is not None:
            self.api_key = local_api_key

    def __repr__(self):
        return f"{type(self).__name__}(base_url={self.session.base_url!r})"

    @property
    def api_key(self) -> Optional[str]:
        """The client's Local API key."""
        return cast(
            Optional[str],
            self.session.headers.get("X-Vestaboard-Local-Api-Key"),
        )

    @api_key.setter
    def api_key(self, value: str) -> None:
        self.session.headers["X-Vestaboard-Local-Api-Key"] = value

    @property
    def enabled(self) -> bool:
        """Check if :py:attr:`~api_key` has been set, indicating that Local API
        support has been enabled."""
        return self.api_key is not None

    def enable(self, enablement_token) -> Optional[str]:
        """Enable the Vestaboard's Local API using a Local API Enablement Token.

        If successful, the Vestaboard's Local API key will be returned and the
        client's :py:attr:`~api_key` property will be updated to the new value.
        """
        r = self.session.post(
            "/local-api/enablement",
            headers={"X-Vestaboard-Local-Api-Enablement-Token": enablement_token},
        )
        r.raise_for_status()

        try:
            local_api_key = r.json().get("apiKey")
        except requests.JSONDecodeError:
            local_api_key = None

        if local_api_key:
            self.api_key = local_api_key

        return local_api_key

    def read_message(self) -> Optional[Rows]:
        """Read the Vestaboard's current message."""
        if not self.enabled:
            raise RuntimeError("Local API has not been enabled")
        r = self.session.get("/local-api/message")
        r.raise_for_status()
        try:
            return r.json().get("message")
        except requests.JSONDecodeError:
            return None

    def write_message(self, message: Rows) -> bool:
        """Write a message to the Vestaboard.

        `message` must be a two-dimensional (6, 22) array of character codes
        representing the exact positions of characters on the board.

        :raises ValueError: if `message` is a list with unsupported dimensions
        """
        if not self.enabled:
            raise RuntimeError("Local API has not been enabled")
        if len(message) != ROWS or not all(len(row) == COLS for row in message):
            raise ValueError(f"expected a ({ROWS}, {COLS}) array of encoded characters")
        r = self.session.post("/local-api/message", json=message)
        r.raise_for_status()
        return r.status_code == requests.codes.CREATED
