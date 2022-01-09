import io

import pytest

from vesta.chars import CHARCODES
from vesta.chars import CHARMAP
from vesta.chars import COLS
from vesta.chars import ROWS
from vesta.chars import Color
from vesta.chars import encode
from vesta.chars import encode_row
from vesta.chars import encode_text
from vesta.chars import pprint


def test_encode_printable_characters():
    for c in CHARMAP:
        encode(c)


def test_encode_character_codes():
    for i in CHARCODES:
        encode(f"{{{i}}}")


def test_encode_bad_characters():
    pytest.raises(ValueError, encode, "<>").match("unsupported character: <")
    pytest.raises(ValueError, encode, "{99}").match("unsupported character code: 99")
    pytest.raises(ValueError, encode, "{20").match("missing }")
    pytest.raises(ValueError, encode, "{999}").match("missing }")


class TestEncodeRow:
    def test_maximum_length(self):
        encode_row("a" * 21 + "{10}")
        pytest.raises(Exception, encode_row, "a" * 30).match("30 characters")
        pytest.raises(Exception, encode_row, "a" * 22 + "{10}").match("23 characters")

    def test_align_left(self):
        chars = [1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        assert encode_row("abc", align="left") == chars

    def test_align_center(self):
        chars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        assert encode_row("abc", align="center") == chars

    def test_align_right(self):
        chars = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3]
        assert encode_row("abc", align="right") == chars

    def test_unknown_alignment(self):
        with pytest.raises(ValueError, match="unknown alignment"):
            encode_row("a", align="unknown")

    def test_fill(self):
        chars = [1, 2, 3] + [int(Color.GREEN)] * (COLS - 3)
        assert encode_row("abc", align="left", fill=Color.GREEN) == chars


class TestEncodeText:
    def test_newlines(self):
        chars = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert encode_text("a\nb\nc") == chars

    def test_align_left(self):
        chars = [
            [20, 8, 9, 19, 0, 9, 19, 0, 1, 0, 20, 5, 19, 20, 0, 15, 6, 0, 12, 5, 6, 20],
            [1, 12, 9, 7, 14, 13, 5, 14, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [25, 1, 25, 37, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert (
            encode_text("This is a test of left alignment\nYay!", align="left") == chars
        )

    def test_align_center(self):
        chars = [
            [0, 0, 20, 8, 9, 19, 0, 9, 19, 0, 1, 0, 20, 5, 19, 20, 0, 15, 6, 0, 0, 0],
            [0, 0, 0, 3, 5, 14, 20, 5, 18, 0, 1, 12, 9, 7, 14, 13, 5, 14, 20, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 1, 25, 37, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert (
            encode_text("This is a test of center alignment\nYay!", align="center")
            == chars
        )

    def test_align_right(self):
        chars = [
            [0, 0, 0, 0, 0, 20, 8, 9, 19, 0, 9, 19, 0, 1, 0, 20, 5, 19, 20, 0, 15, 6],
            [0, 0, 0, 0, 0, 0, 0, 18, 9, 7, 8, 20, 0, 1, 12, 9, 7, 14, 13, 5, 14, 20],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 1, 25, 37],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert (
            encode_text("This is a test of right alignment\nYay!", align="right")
            == chars
        )

    def test_valign_top(self):
        chars = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert encode_text("a\nb", valign="top") == chars

    def test_valign_middle(self):
        chars = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert encode_text("a\nb", valign="middle") == chars

    def test_valign_bottom(self):
        chars = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert encode_text("a\nb", valign="bottom") == chars

    def test_valign_none(self):
        chars = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert encode_text("a\nb", valign=None) == chars

    def test_unknown_alignments(self):
        with pytest.raises(ValueError, match="unknown alignment"):
            encode_text("a", align="unknown")

        with pytest.raises(ValueError, match="unknown vertical alignment"):
            encode_text("a", valign="unknown")

    def test_maximum_rows(self):
        with pytest.raises(ValueError, match=f"results in {ROWS + 1} lines"):
            encode_text("a\n" * (ROWS + 1))

    def test_margin(self):
        chars = [
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        assert encode_text("a" * COLS, margin=1) == chars

    def test_fill(self):
        chars = [
            [1, 2, 3] + [int(Color.GREEN)] * (COLS - 3),
            [Color.GREEN] * COLS,
            [Color.GREEN] * COLS,
            [Color.GREEN] * COLS,
            [Color.GREEN] * COLS,
            [Color.GREEN] * COLS,
        ]
        assert encode_text("abc", align="left", fill=Color.GREEN) == chars

    def test_breaks(self):
        chars = [
            # fmt: off
            [23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 0, 0],
            [23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 0, 0],
            [23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            # fmt: on
        ]
        assert encode_text(" ".join(["word"] * 10)) == chars


class TestPrint:
    def pprint(self, data, **kwargs) -> str:
        output = io.StringIO()
        pprint(data, stream=output, **kwargs)
        return output.getvalue()

    def test_row(self):
        chars = encode_row("{63} Centered {63}", align="center")
        assert self.pprint(chars) == (
            "| | | | | |◼︎| |C|E|N|T|E|R|E|D| |◼︎| | | | | |\n"
        )

    def test_rows(self):
        chars = encode_text("{63} Centered {63}", align="center", valign="middle")
        assert self.pprint(chars) == (
            "| | | | | | | | | | | | | | | | | | | | | | |\n"
            "| | | | | | | | | | | | | | | | | | | | | | |\n"
            "| | | | | |◼︎| |C|E|N|T|E|R|E|D| |◼︎| | | | | |\n"
            "| | | | | | | | | | | | | | | | | | | | | | |\n"
            "| | | | | | | | | | | | | | | | | | | | | | |\n"
            "| | | | | | | | | | | | | | | | | | | | | | |\n"
        )

    def test_sep(self):
        chars = encode_row("{63} Centered {63}", align="center")
        assert self.pprint(chars, sep="") == "     ◼︎ CENTERED ◼︎     \n"

    def test_block(self):
        chars = encode_row("{63} Centered {63}", align="center")
        assert self.pprint(chars, block="_") == (
            "| | | | | |_| |C|E|N|T|E|R|E|D| |_| | | | | |\n"
        )

    def test_colors(self, monkeypatch):
        output = io.StringIO()
        monkeypatch.setattr(output, "isatty", lambda: True)
        pprint([65], stream=output)
        assert (
            output.getvalue() == "\x1b[90m|\x1b[0m\x1b[93m◼︎\x1b[0m\x1b[90m|\x1b[0m\n"
        )

    def test_unknown_character_code(self):
        pytest.raises(ValueError, pprint, [99]).match("unknown character code: 99")
