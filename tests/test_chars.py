import unittest

from vesta.chars import CHARCODES
from vesta.chars import Color
from vesta.chars import encode
from vesta.chars import encode_row


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
            encode_row("abc", align='left'),
        )

    def test_align_center(self):
        self.assertEqual(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            encode_row("abc", align='center'),
        )

    def test_align_right(self):
        self.assertEqual(
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3],
            encode_row("abc", align='right'),
        )

    def test_unknown_alignment(self):
        self.assertRaisesRegex(
            ValueError, "unknown alignment", encode_row, "a", align="unknown"
        )

    def test_fill(self):
        self.assertEqual(
            [1, 2, 3] + [int(Color.GREEN)] * 19,
            encode_row("abc", align="left", fill=Color.GREEN),
        )
