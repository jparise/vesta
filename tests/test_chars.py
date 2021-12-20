import unittest

from vesta.chars import CHARCODES
from vesta.chars import COLS
from vesta.chars import ROWS
from vesta.chars import Color
from vesta.chars import encode
from vesta.chars import encode_row
from vesta.chars import encode_text


class EncodeTests(unittest.TestCase):
    def test_printable_characters(self):
        for c in CHARCODES:
            encode(c)

    def test_character_codes(self):
        for i in range(0, 70):
            encode(f"{{{i}}}")

    def test_bad_characters(self):
        self.assertRaisesRegex(ValueError, "unsupported characters", encode, "<>")
        self.assertRaisesRegex(ValueError, "unsupported characters", encode, "{20")
        self.assertRaisesRegex(ValueError, "unsupported characters", encode, "{999}")
        self.assertRaisesRegex(ValueError, "bad character code", encode, "{99}")


class EncodeRowTests(unittest.TestCase):
    def test_maximum_length(self):
        encode_row("a" * 21 + "{10}")
        self.assertRaisesRegex(Exception, "30 characters", encode_row, "a" * 30)
        self.assertRaisesRegex(
            Exception, "23 characters", encode_row, "a" * 22 + "{10}"
        )

    def test_align_left(self):
        self.assertEqual(
            [1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            encode_row("abc", align="left"),
        )

    def test_align_center(self):
        self.assertEqual(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            encode_row("abc", align="center"),
        )

    def test_align_right(self):
        self.assertEqual(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3],
            encode_row("abc", align="right"),
        )

    def test_unknown_alignment(self):
        self.assertRaisesRegex(
            ValueError, "unknown alignment", encode_row, "a", align="unknown"
        )

    def test_fill(self):
        self.assertEqual(
            [1, 2, 3] + [int(Color.GREEN)] * (COLS - 3),
            encode_row("abc", align="left", fill=Color.GREEN),
        )


class EncodeTextTests(unittest.TestCase):
    def test_newlines(self):
        self.assertEqual(
            [
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            encode_text("a\nb\nc"),
        )

    def test_align_left(self):
        self.assertEqual(
            # fmt: off
            [
                [20, 8, 9, 19, 0, 9, 19, 0, 1, 0, 20, 5, 19, 20, 0, 15, 6, 0, 12, 5, 6, 20],
                [1, 12, 9, 7, 14, 13, 5, 14, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [25, 1, 25, 37, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            # fmt: on
            encode_text("This is a test of left alignment\nYay!", align="left"),
        )

    def test_align_center(self):
        self.assertEqual(
            # fmt: off
            [
                [0, 0, 20, 8, 9, 19, 0, 9, 19, 0, 1, 0, 20, 5, 19, 20, 0, 15, 6, 0, 0, 0],
                [0, 0, 0, 3, 5, 14, 20, 5, 18, 0, 1, 12, 9, 7, 14, 13, 5, 14, 20, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 1, 25, 37, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            # fmt: on
            encode_text("This is a test of center alignment\nYay!", align="center"),
        )

    def test_align_right(self):
        self.assertEqual(
            # fmt: off
            [
                [0, 0, 0, 0, 0, 20, 8, 9, 19, 0, 9, 19, 0, 1, 0, 20, 5, 19, 20, 0, 15, 6],
                [0, 0, 0, 0, 0, 0, 0, 18, 9, 7, 8, 20, 0, 1, 12, 9, 7, 14, 13, 5, 14, 20],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 1, 25, 37],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            # fmt: on
            encode_text("This is a test of right alignment\nYay!", align="right"),
        )

    def test_valign_top(self):
        self.assertEqual(
            [
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            encode_text("a\nb", valign="top"),
        )

    def test_valign_middle(self):
        self.assertEqual(
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            encode_text("a\nb", valign="middle"),
        )

    def test_valign_bottom(self):
        self.assertEqual(
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            encode_text("a\nb", valign="bottom"),
        )

    def test_unknown_alignments(self):
        self.assertRaisesRegex(
            ValueError, "unknown alignment", encode_text, "a", align="unknown"
        )
        self.assertRaisesRegex(
            ValueError, "unknown vertical alignment", encode_text, "a", valign="unknown"
        )

    def test_maximum_rows(self):
        self.assertRaisesRegex(
            ValueError, f"results in {ROWS + 1} lines", encode_text, "a\n" * (ROWS + 1)
        )

    def test_margin(self):
        self.assertEqual(
            [
                [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            encode_text("a" * COLS, margin=1),
        )

    def test_fill(self):
        self.assertEqual(
            [
                [1, 2, 3] + [int(Color.GREEN)] * (COLS - 3),
                [Color.GREEN] * COLS,
                [Color.GREEN] * COLS,
                [Color.GREEN] * COLS,
                [Color.GREEN] * COLS,
                [Color.GREEN] * COLS,
            ],
            encode_text("abc", align="left", fill=Color.GREEN),
        )

    def test_breaks(self):
        self.assertEqual(
            # fmt: off
            [
                [23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 0, 0],
                [23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 0, 0],
                [23, 15, 18, 4, 0, 23, 15, 18, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            # fmt: on
            encode_text(" ".join(["word"] * 10)),
        )
