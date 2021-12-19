import unittest

from vesta.client import Client


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = Client("key", "secret")

    def test_post_message_dimensions(self):
        self.assertRaisesRegex(
            ValueError, "expected a \\(6, 22\\) array", self.client.post_message, "", []
        )
