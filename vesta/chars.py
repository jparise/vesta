import enum
import math
import re
import sys
from typing import AbstractSet
from typing import List
from typing import TextIO
from typing import Tuple
from typing import Union
from typing import cast

ROWS = 6
COLS = 22
PRINTABLE = " ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$() - +&=;: '\"%,.  /? °"
CHARCODES = {c: idx for idx, c in enumerate(PRINTABLE) if idx == 0 or c != " "}

# Regular expression that matches supported characters.
VALID_RE = re.compile(
    r"""
    (?:
        [ A-Za-z0-9!@#$()\-+&=;:'\"%,./?°]  # Printable Characters
        |                                   # or
        (?:\{\d{1,2}\})                     # Character Codes ({5} or {65})
    )*
    """,
    re.VERBOSE,
)


class Color(enum.IntEnum):
    """Color chips"""

    ansi: str

    def __new__(cls, value: int, ansi: str):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.ansi = ansi
        return obj

    # fmt: off
    BLACK   = (0,  "\033[0m")   # noqa: E221
    RED     = (63, "\033[31m")  # noqa: E221
    ORANGE  = (64, "\033[33m")  # noqa: E221
    YELLOW  = (65, "\033[93m")  # noqa: E221
    GREEN   = (66, "\033[32m")  # noqa: E221
    BLUE    = (67, "\033[94m")  # noqa: E221
    VIOLET  = (68, "\033[95m")  # noqa: E221
    WHITE   = (69, "\033[97m")  # noqa: E221
    # fmt: on


def iscode(n: int) -> bool:
    """Checks if an integer value is a valid character code."""
    return 0 <= n <= 69


def encode(s: str) -> List[int]:
    """Encodes a string as a list of character codes.

    In addition to printable characters, the string can contain character code
    sequences inside curly braces, such as ``{5}`` or ``{65}``.

    :raises ValueError: if the string contains unsupported characters or codes

    >>> encode("{67} Hello, World {68}")
    [67, 0, 8, 5, 12, 12, 15, 55, 0, 23, 15, 18, 12, 4, 0, 68]
    """
    if VALID_RE.fullmatch(s) is None:
        raise ValueError(f"{s!r} contains unsupported characters or character codes")

    out = []
    skip_to = 0
    for i, c in enumerate(s.upper()):
        if i < skip_to:
            continue

        if c == "{":
            if s[i + 2] == "}":
                out.append(int(s[i + 1]))
                skip_to = i + 3
            elif s[i + 3] == "}":
                out.append(int(s[i + 1 : i + 3]))
                skip_to = i + 4
            else:
                raise ValueError(f"{i+1}: unmatched '{{'")  # pragma: no cover
            if not iscode(out[-1]):
                raise ValueError(f"{i+2}: bad character code: {out[-1]}")
        else:
            out.append(CHARCODES[c])

    return out


def encode_row(s: str, align: str = "left", fill: int = Color.BLACK) -> List[int]:
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
    align: str = "left",
    valign: str = "top",
    margin: int = 0,
    fill: int = Color.BLACK,
    breaks: AbstractSet[int] = frozenset({0}),
) -> List[List[int]]:
    """Encodes a string of text into six full rows of character codes.

    In addition to printable characters, the string can contain character code
    sequences inside curly braces, such as ``{5}`` or ``{65}``.

    ``align`` controls the text's alignment within the row: `left`, `right`, or
    `center`. ``valign`` controls the text's vertical alignment within the full
    board: `top`, `middle`, or `bottom`.

    ``margin`` specifies the width (in columns) of the left and right margins.
    The ``fill`` character code (generally a :py:class:`Color`) is used to fill
    out any additional space.

    ``breaks`` is the set of character codes used to compute line breaks. If a
    line of text won't fit in the available columns, it will be "broken" at the
    first preceding break character, and the remaining characters will continue
    on the next row (potentially subject to additional breaks). If a break
    cannot be found, the line will be broken at the column limit (potentially
    mid-"word").

    :raises ValueError: if the string contains unsupported characters or codes,
                        or if the resulting encoding sequence would exceed the
                        maximum number of supported rows

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
    rows: List[List[int]] = []

    def find_break(line: List[int]) -> Tuple[int, int]:
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

    nrows = len(rows)
    if nrows < ROWS:
        empty = [fill] * COLS
        if valign == "top":
            rows += [empty] * (ROWS - nrows)
        elif valign == "bottom":
            rows = [empty] * (ROWS - nrows) + rows
        elif valign == "middle":
            pad = (ROWS - nrows) / 2
            rows = [empty] * math.floor(pad) + rows + [empty] * math.ceil(pad)
        else:
            raise ValueError(f"unknown vertical alignment: {valign}")
    elif nrows > ROWS:
        raise ValueError(f"{s!r} results in {nrows} lines (max {ROWS})")

    return rows


def _format_row(row: List[int], align: str, margin: int, fill: int) -> List[int]:
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
    data: Union[List[int], List[List[int]]],
    stream: TextIO = sys.stdout,
    *,
    sep: str = "|",
    block: str = "◼︎",
):
    """Prints a console-formatted representation of encoded character data.

    ``data`` may be a single list or a two-dimensional array of character codes.
    """
    rows = cast(
        List[List[int]],
        data if data and isinstance(data[0], list) else [data],
    )

    # Assume all TTYs support color.
    colors = stream.isatty()
    if colors:
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
