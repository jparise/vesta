=====
Vesta
=====

Vesta is a `Vestaboard <https://www.vestaboard.com/>`_ client library for
Python. It provides API clients and character encoding utilities.

.. toctree::
   :hidden:

   changelog

Installation
============

Vesta requires Python 3.8 or later. It can be installed `via PyPI
<https://pypi.org/project/vesta/>`_::

    $ python -m pip install vesta

It's only runtime dependency is the `HTTPX`_ library, which will be
installed automatically.

.. _HTTPX: https://www.python-httpx.org/

API Clients
===========

``Client``
----------

.. autoclass:: vesta.Client
    :members:

``LocalClient``
---------------

:py:class:`vesta.LocalClient` provides a client interface for interacting with
a Vestaboard over the local network using `Vestaboard's Local API
<https://docs.vestaboard.com/docs/local-api/introduction>`_.

.. important::

    Vestaboard owners must first request a `Local API enablement token
    <https://www.vestaboard.com/local-api>`_ in order to use the Local API.

.. autoclass:: vesta.LocalClient
    :members:

``ReadWriteClient``
-------------------

:py:class:`vesta.ReadWriteClient` provides a client interface for interacting
with a Vestaboard using the `Read / Write API
<https://docs.vestaboard.com/docs/read-write-api/introduction>`_.

.. important::

    A Read / Write API key is required to read or write messages. This key is
    obtained by enabling the Vestaboard's Read / Write API via the Settings
    section of the mobile app or from the Developer section of the web app.

.. autoclass:: vesta.ReadWriteClient
    :members:

``VBMLClient``
--------------

:py:class:`vesta.VBMLClient` provides a client interface for Vestaboard's
`VBML (Vestaboard Markup Language) <https://docs.vestaboard.com/docs/vbml>`_
API.

.. autoclass:: vesta.VBMLClient
    :members:

Character Encoding
==================

All Vestaboard characters (letters, numbers, symbols, and colors) are encoded
as integer `character codes <https://docs.vestaboard.com/docs/characterCodes>`_.
Vesta includes some helpful routines for working with these character codes.

.. automodule:: vesta.chars
   :members: COLS, ROWS, Row, Rows

.. autoclass:: vesta.Color
    :show-inheritance:
    :members:
    :undoc-members:
    :exclude-members: ansi

.. autofunction:: vesta.encode
.. autofunction:: vesta.encode_row
.. autofunction:: vesta.encode_text

.. autofunction:: vesta.pprint

VBML
====

`VBML (Vestaboard Markup Language) <https://docs.vestaboard.com/docs/vbml>`_
defines a language for composing static and dynamic messages.

.. automodule:: vesta.vbml
   :members:  Component, Props, Style
   :member-order: groupwise
