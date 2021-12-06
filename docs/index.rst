Vesta
=====

.. image:: _static/logo.png
    :alt: Vesta: A Vestaboard client library
    :align: center
    :target: https://github.com/jparise/vesta

Vesta is a `Vestaboard <https://www.vestaboard.com/>`_ client library for
Python. It provides an API client and character encoding utilities.

Installation
------------

Vesta requires Python 3.6 or later. It can be installed `via PyPI
<https://pypi.org/project/vesta/>`_::

    $ python -m pip install vesta

It's only runtime dependency is the `Requests`_ library, which will be
installed automatically.

.. _Requests: https://requests.readthedocs.io/

API Client
----------

.. autoclass:: vesta.Client
    :members:

Character Encoding
------------------

All Vestaboard characters (letters, numbers, symbols, and colors) are encoded
as integer `character codes <https://docs.vestaboard.com/characters>`_. Vesta
includes some useful routines for working with these character codes.

.. autoclass:: vesta.Color
    :show-inheritance:
    :members:
    :undoc-members:
    :exclude-members: ansi

.. autofunction:: vesta.encode
.. autofunction:: vesta.encode_row
.. autofunction:: vesta.encode_text

.. autofunction:: vesta.pprint

Message Posting
---------------

Messages can be posted (using :py:meth:`vesta.Client.post_message`) as either
text strings or two-dimensional arrays of character codes representing the
exact positions of characters on the board.

If `text` is specified, lines will be centered horizontally and vertically if
possible. Character codes will be inferred for alphanumeric and punctuation, or
can be explicitly specified in-line in the message with curly braces containing
the character code (such as ``{5}`` or ``{65}``).
