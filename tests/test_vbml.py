import pytest

from vesta.vbml import Component


class TestComponent:
    def test_template(self):
        assert Component("template").asdict() == {"template": "template"}

    def test_raw_characters(self):
        assert Component(raw_characters=[]).asdict() == {"rawCharacters": []}

    def test_template_and_raw_characters(self):
        assert Component("t", raw_characters=[]).asdict() == {"rawCharacters": []}

    def test_template_or_raw_characters_required(self):
        with pytest.raises(ValueError, match="expected template or raw_characters"):
            Component()

    def test_style(self):
        assert Component("template", style={}).asdict() == {"template": "template"}
        assert Component(
            "template",
            style={"height": 4, "width": 10, "justify": "left", "align": "top"},
        ).asdict() == {
            "template": "template",
            "style": {"height": 4, "width": 10, "justify": "left", "align": "top"},
        }

    def test_height(self):
        assert Component("template", height=4).asdict() == {
            "template": "template",
            "style": {"height": 4},
        }

    def test_width(self):
        assert Component("template", width=10).asdict() == {
            "template": "template",
            "style": {"width": 10},
        }

    def test_justify(self):
        assert Component("template", justify="left").asdict() == {
            "template": "template",
            "style": {"justify": "left"},
        }

    def test_align(self):
        assert Component("template", align="top").asdict() == {
            "template": "template",
            "style": {"align": "top"},
        }

    def test_absolute_position(self):
        assert Component("template", absolute_position={"x": 1, "y": 2}).asdict() == {
            "template": "template",
            "style": {"absolutePosition": {"x": 1, "y": 2}},
        }
