# Vesta

Vesta is a [Vestaboard](https://www.vestaboard.com/) client library for Python.
It provides an API client and character encoding utilities.

## Installation

Vesta requires Python 3.7 or later. It can be installed [via PyPI][pypi]:

```sh
$ python -m pip install vesta
```

It's only runtime dependency is the [Requests library][requests], which will be
installed automatically.

[pypi]: https://pypi.org/project/vesta/
[requests]: https://requests.readthedocs.io/

## Usage

### API Client

The `Client` type is initialized with an API key and secret:

```python
>>> import vesta
>>> client = vesta.Client(API_KEY, API_SECRET)
```

Then, you can make API calls using one of the provided methods:

```python
>>> client.get_viewer()
{'_id': ..., '_created': '1629081092624', 'type': 'installation', 'installation': {'_id': ...}}

>>> client.get_subscriptions()
[{'_id': ..., '_created': '1629081092624', 'title': None, 'icon': None, 'installation': {'_id': ..., 'installable': {'_id': ...}}, 'boards': [{'_id': ...}]}]

>>> client.post_message(SUBSCRIPTION_ID, "Hello, World")
{'message': {'id': ..., 'text': 'Hello, World', 'created': '1635801572442'}}
```

### Character Encoding

All Vestaboard characters (letters, numbers, symbols, and colors) are encoded
as integer [character codes](https://docs.vestaboard.com/characters). Vesta
includes some useful routines for working with these character codes.

`encode()` encodes a string as a list of character codes. In addition to
printable characters, the string can contain character code sequences inside
curly braces, such as `{5}` or `{65}`.

```python
>>> vesta.encode("{67} Hello, World {68}")
[67, 0, 8, 5, 12, 12, 15, 55, 0, 23, 15, 18, 12, 4, 0, 68]
```

`encode_row()` encodes a string as a row of character codes. It builds on
`encode()` by providing alignment control.

```python
>>> vesta.encode_row("{67} Hello, World {68}", align="center")
[0, 0, 0, 67, 0, 8, 5, 12, 12, 15, 55, 0, 23, 15, 18, 12, 4, 0, 68, 0, 0, 0]
```

`encode_text()` encodes a string of text into rows of character codes, further
building on `encode()` and `encode_row()` with the addition of alignment,
margin control, and line breaks.

```python
>>> encode_text("multiple\nlines\nof\ntext", align="center", valign="middle")
[
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 13, 21, 12, 20, 9, 16, 12, 5, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 12, 9, 14, 5, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 5, 24, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
```

Lastly, `pprint()` can be used to pretty-print encoded characters to the
console, which can be useful during development.

```python
>>> vesta.pprint([0, 0, 0, 67, 0, 8, 5, 12, 12, 15, 55, 0, 23, 15, 18, 12, 4, 0, 68, 0, 0, 0])
| | | |◼︎| |H|E|L|L|O|,| |W|O|R|L|D| |◼︎| | | |
```

### Message Posting

Messages can be posted as either text strings or two-dimensional arrays of
character codes representing the exact positions of characters on the board.

If text is specified, lines will be centered horizontally and vertically if
possible. Character codes will be inferred for alphanumeric and punctuation, or
can be explicitly specified in-line in the message with curly braces containing
the character code.

## License

This project is licensed under the terms of the [MIT license](LICENSE).
