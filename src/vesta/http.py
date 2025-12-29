# Copyright (c) Jon Parise <jon@indelible.org>
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

import urllib.error
import urllib.request
from json import JSONDecodeError
from json import dumps as json_dumps
from json import loads as json_loads
from typing import Any
from typing import Dict
from typing import Literal
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from urllib.parse import urljoin

# Re-export as a convenience
HTTPError = urllib.error.HTTPError


class Response(NamedTuple):
    """HTTP response tuple."""

    status: int
    body: bytes
    headers: Dict[str, str]

    def json(self, default: Any = None):
        try:
            return json_loads(self.body)
        except JSONDecodeError:
            return default


class Client:
    """HTTP client with connection pooling and session management.

    Uses urllib.request for HTTP operations with automatic connection reuse.
    """

    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Mapping[str, str]] = None,
    ):
        self.base_url = base_url
        self.headers: Dict[str, str] = dict(headers) if headers else {}
        self._opener = urllib.request.build_opener()

    def request(
        self,
        method: Literal["GET", "POST"],
        url: str,
        *,
        json: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Response:
        """Execute HTTP request and return Response.

        Raises urllib.error.HTTPError for 4xx/5xx responses.
        Raises urllib.error.URLError for connection errors.
        """
        full_url = urljoin(self.base_url, url.lstrip("/"))

        request_headers = dict(self.headers)
        if headers:
            request_headers.update(headers)

        data = None
        if json is not None:
            data = json_dumps(json, separators=(",", ":")).encode("utf-8")
            request_headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            full_url,
            data=data,
            headers=request_headers,
            method=method,
        )

        with self._opener.open(request) as response:
            return Response(
                response.getcode(),
                response.read(),
                dict(response.headers.items()),
            )
