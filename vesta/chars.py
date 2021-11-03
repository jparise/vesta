import enum
import math
import re
import sys
from typing import List
from typing import TextIO
from typing import Union
from typing import cast

ROWS = 6
COLS = 22
PRINTABLE = " ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$() - +&=;: '\"%,.  /? °"
CHARCODES = {c: index for index, c in enumerate(PRINTABLE)}

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
    [67, 61, 8, 5, 12, 12, 15, 55, 61, 23, 15, 18, 12, 4, 61, 68]
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
                        maximum number of support characters

    >>> encode_row("{67} Hello, World {68}", align="center")
    [0, 0, 0, 67, 61, 8, 5, 12, 12, 15, 55, 61, 23, 15, 18, 12, 4, 61, 68, 0, 0, 0]
    """
    row = encode(s)

    if len(row) > COLS:
        raise ValueError(f"{s!r} results in {len(row)} characters (max {COLS})")

    if align == "left":
        row = row + [fill] * (COLS - len(row))
    elif align == "right":
        row = [fill] * (COLS - len(row)) + row
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

    >>> pprint([67, 61, 8, 5, 12, 12, 15, 55, 61, 23, 15, 18, 12, 4, 61, 68])
    |◼︎| |H|E|L|L|O|,| |W|O|R|L|D| |◼︎|
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
