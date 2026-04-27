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

from collections.abc import Mapping
from typing import Any
from typing import Literal
from typing import TypedDict

from .chars import Rows

__all__ = ["Component", "Props", "Style"]

#: Map of dynamic properties that can be injected into message templates.
Props = Mapping[str, str]

#: Horizontal alignment options.
Justification = Literal["left", "right", "center", "justified"]

#: Vertical alignment options.
Alignment = Literal["top", "bottom", "center"]


class Position(TypedDict):
    """A Position defines an absolute position on a board."""

    x: int  #: X coordinate
    y: int  #: Y coordinate


class Style(TypedDict, total=False):
    """A Style defines a set of values that will be applied to a
    :py:class:`Component`.
    """

    #: The height of the current component (1-6). Defaults to 6.
    height: int

    #: The width of the current component (1-22). Defaults to 22.
    width: int

    #: The horizontal alignment of the message. Defaults to ``left``.
    justify: Justification

    #: The vertical alignment of a message. Defaults to ``top``.
    align: Alignment

    #: An exact position on the board. Bounded by ``width`` and ``height``.
    absolutePosition: Position


# Component is defined as a simple class so that we can provide good typing and
# a nice constructor.
#
# A TypedDict would correctly represent the API shape of a Component, but it
# doesn't support making the 'template' field "required" and the 'style' field
# "optional" until Python 3.11+, nor can we provide a custom constructor or
# "builder" class method.
#
# Using a dataclass results in an overall more complex class that also can't
# represent an "optional" field as "not present". (Dataclass optional fields
# are always set to their default values when an explicit value isn't given.)
class Component:
    """A Component defines a template with optional :py:class:`Style` values.

    Template is a message template string. It can contain any supported
    Vestaboard character as well as valid character code sequences inside curly
    braces, such as ``{5}`` or ``{65}`` and interpolated :py:class:`Props`
    using double bracket notation (``{{propName}}``). Any lowercase letters
    will be cast to uppercase. A new row can be forced by inserting a newline
    (``\\n``) sequence.

    Alternatively, a ``raw_characters`` character array can be provided to set
    the initial (background) state of the component. ``raw_characters`` takes
    precedence over ``template``.

    A ``style`` dictionary can be provided. Individual :py:class:`Style` values
    can also be given as keyword arguments (``height``, ``width``, ``justify``,
    ``align``, ``absolute_position``), and they will override any values from
    the ``style`` dictionary.
    """

    __slots__ = ["raw_characters", "style", "template"]

    def __init__(
        self,
        template: str | None = None,
        raw_characters: Rows | None = None,
        style: Style | None = None,
        *,
        height: int | None = None,
        width: int | None = None,
        justify: Justification | None = None,
        align: Alignment | None = None,
        absolute_position: Position | None = None,
    ):
        if not (template is not None or raw_characters is not None):
            raise ValueError("expected template or raw_characters")

        self.template = template
        self.raw_characters = raw_characters
        self.style: Style = style or {}
        if height is not None:
            self.style["height"] = height
        if width is not None:
            self.style["width"] = width
        if justify is not None:
            self.style["justify"] = justify
        if align is not None:
            self.style["align"] = align
        if absolute_position is not None:
            self.style["absolutePosition"] = absolute_position

    def asdict(self) -> dict[str, Any]:
        """Returns the component's JSON dictionary representation."""
        d: dict[str, Any] = {}
        if self.raw_characters is not None:
            d["rawCharacters"] = self.raw_characters
        else:
            assert self.template is not None
            d["template"] = self.template
        if self.style:
            d["style"] = self.style
        return d
