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

import enum
import math
import sys
from typing import Container
from typing import Final
from typing import List
from typing import Literal
from typing import Optional
from typing import TextIO
from typing import Tuple
from typing import Union
from typing import cast

PRINTABLE = " ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$() - +&=;: '\"%,.  /? °"
CHARMAP = {c: i for i, c in enumerate(PRINTABLE) if i == 0 or c != " "}

#: The number of columns on a board.
COLS: Final[int] = 22

#: The number of rows on a board.
ROWS: Final[int] = 6

#: A row of character codes.
Row = List[int]

#: A list of rows, forming a character grid.
Rows = List[Row]


def validate_rows(rows: Rows) -> None:
    """Check if ``rows`` is a well-formed grid of character codes.

    :raises ValueError: if ``rows`` does not have the correct dimensions
    """
    if len(rows) != ROWS or not all(len(row) == COLS for row in rows):
        raise ValueError(f"expected a ({COLS}, {ROWS}) array of encoded characters")


class Color(enum.IntEnum):
    """Color chips"""

    ansi: str

    def __new__(cls, value: int, ansi: str) -> "Color":
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.ansi = ansi
        return obj

    # fmt: off
    BLANK   = (0,  "\033[0m")   # noqa: E221
    RED     = (63, "\033[31m")  # noqa: E221
    ORANGE  = (64, "\033[33m")  # noqa: E221
    YELLOW  = (65, "\033[93m")  # noqa: E221
    GREEN   = (66, "\033[32m")  # noqa: E221
    BLUE    = (67, "\033[94m")  # noqa: E221
    VIOLET  = (68, "\033[95m")  # noqa: E221
    WHITE   = (69, "\033[97m")  # noqa: E221
    BLACK   = (70, "\033[0m")   # noqa: E221
    FILLED  = (71, "\033[97m")  # noqa: E221
    # fmt: on


# The set of all supported character codes.
CHARCODES = frozenset(CHARMAP.values()).union(Color)


def encode(s: str) -> Row:
    """Encodes a string as a list of character codes.

    In addition to printable characters, the string can contain character code
    sequences inside curly braces, such as ``{5}`` or ``{65}``.

    :raises ValueError: if the string contains unsupported characters or codes

    >>> encode("{67} Hello, World {68}")
    [67, 0, 8, 5, 12, 12, 15, 55, 0, 23, 15, 18, 12, 4, 0, 68]
    """
    out = []
    lens = len(s)
    skip_to = 0
    for i, c in enumerate(s.upper()):
        if i < skip_to:
            continue

        if c == "{":
            if lens > i + 2 and s[i + 2] == "}":
                out.append(int(s[i + 1]))
                skip_to = i + 3
            elif lens > i + 3 and s[i + 3] == "}":
                out.append(int(s[i + 1 : i + 3]))
                skip_to = i + 4
            else:
                raise ValueError(f"{i+1}: missing }} at index {i+2} or {i+3}")
            if out[-1] not in CHARCODES:
                raise ValueError(f"{i+2}: unsupported character code: {out[-1]}")
        else:
            try:
                out.append(CHARMAP[c])
            except KeyError:
                raise ValueError(f"{i+1}: unsupported character: {c}")

    return out


def encode_row(
    s: str,
    align: Literal["left", "center", "right"] = "left",
    fill: int = Color.BLANK,
) -> Row:
    """Encodes a string as a row of character codes.

    In addition to printable characters, the string can contain character code
    sequences inside curly braces, such as ``{5}`` or ``{65}``.

    ``align`` controls the text's alignment within the row: `left`, `right`, or
    `center`. The ``fill`` character code (generally a :py:class:`Color`) is
    used to fill out any additional space.

    :raises ValueError: if the string contains unsupported characters or codes,
                        or if the resulting encoding sequence would exceed the
                        maximum number of supported columns

    >>> encode_row("{67} Hello, World {68}", align="center")
    [0, 0, 0, 67, 0, 8, 5, 12, 12, 15, 55, 0, 23, 15, 18, 12, 4, 0, 68, 0, 0, 0]
    """
    row = encode(s)

    if len(row) > COLS:
        raise ValueError(f"{s!r} results in {len(row)} characters (max {COLS})")

    return _format_row(row, align, 0, int(fill))


def encode_text(
    s: str,
    align: Literal["left", "center", "right"] = "left",
    valign: Optional[Literal["top", "middle", "bottom"]] = "top",
    max_rows: int = ROWS,
    margin: int = 0,
    fill: int = Color.BLANK,
    breaks: Container[int] = frozenset({0}),
) -> Rows:
    """Encodes a string of text into rows of character codes.

    In addition to printable characters, the string can contain character code
    sequences inside curly braces, such as ``{5}`` or ``{65}``.

    ``align`` controls the text's alignment within the row: `left`, `right`, or
    `center`. ``valign`` controls the text's vertical alignment within the full
    board (up to ``max_rows``): `top`, `middle`, `bottom`, or None (to never add
    rows, potentially resulting in a partial board).

    ``max_rows`` determines the maximum number of rows that will be returned,
    potentially truncating the result. When ``max_rows`` is zero, the row count
    is unlimited.

    ``margin`` specifies the width (in columns) of the left and right margins.
    The ``fill`` character code (generally a :py:class:`Color`) is used to fill
    out any additional space.

    ``breaks`` is the set of character codes used to compute line breaks. If a
    line of text won't fit in the available columns, it will be "broken" at the
    first preceding break character, and the remaining characters will continue
    on the next row (potentially subject to additional breaks). If a break
    cannot be found, the line will be broken at the column limit (potentially
    mid-"word").

    :raises ValueError: if the string contains unsupported characters or codes

    >>> encode_text('multiple\\nlines\\nof\\ntext', align="center", valign="middle")
    ... # doctest: +NORMALIZE_WHITESPACE
    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 13, 21, 12, 20, 9, 16, 12, 5, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 12, 9, 14, 5, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 5, 24, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    """
    fill = int(fill)
    max_cols = COLS - margin * 2
    rows: Rows = []

    def find_break(line: Row) -> Tuple[int, int]:
        end = min(len(line), max_cols)
        for pos in range(end, 0, -1):
            if line[pos] in breaks:
                return pos, pos + 1
        return end, end

    for line in map(encode, s.splitlines()):
        while len(line) > max_cols:
            pos, resume = find_break(line)
            rows.append(_format_row(line[:pos], align, margin, fill))
            line = line[resume:]

        rows.append(_format_row(line, align, margin, fill))

    if max_rows < 1:  # unlimited rows
        return rows

    nrows = len(rows)
    if nrows < max_rows and valign is not None:
        empty = [fill] * COLS
        if valign == "top":
            rows += [empty] * (max_rows - nrows)
        elif valign == "bottom":
            rows = [empty] * (max_rows - nrows) + rows
        elif valign == "middle":
            pad = (max_rows - nrows) / 2
            rows = [empty] * math.floor(pad) + rows + [empty] * math.ceil(pad)
        else:
            raise ValueError(f"unknown vertical alignment: {valign}")
    elif nrows > max_rows:
        rows = rows[:max_rows]

    return rows


def _format_row(row: Row, align: str, margin: int, fill: int) -> Row:
    assert len(row) <= COLS - margin * 2

    if align == "left":
        row = [fill] * margin + row + [fill] * (COLS - len(row) - margin)
    elif align == "right":
        row = [fill] * (COLS - len(row) - margin) + row + [fill] * margin
    elif align == "center":
        pad = (COLS - len(row)) / 2
        row = [fill] * math.floor(pad) + row + [fill] * math.ceil(pad)
    else:
        raise ValueError(f"unknown alignment: {align}")

    assert len(row) == COLS

    return row


def pprint(
    data: Union[Row, Rows],
    stream: TextIO = sys.stdout,
    *,
    sep: str = "|",
    block: str = "◼︎",
) -> None:
    """Prints a console-formatted representation of encoded character data.

    ``data`` may be a single list or a two-dimensional array of character codes.
    """
    rows = cast(Rows, data if data and isinstance(data[0], list) else [data])

    # Assume all TTYs support color.
    colors = stream.isatty()
    if colors and sep:
        sep = f"\033[90m{sep}\033[0m"

    def symbol(code: int) -> str:
        if 0 <= code < len(PRINTABLE):
            return PRINTABLE[code]
        try:
            color = Color(code)  # type: ignore
        except ValueError:
            raise ValueError(f"unknown character code: {code}")
        return f"{color.ansi}{block}\033[0m" if colors else block

    lines = [sep + sep.join(map(symbol, row)) + sep for row in rows]
    stream.write("\n".join(lines) + "\n")
