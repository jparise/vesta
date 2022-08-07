=====
Vesta
=====

Vesta is a `Vestaboard <https://www.vestaboard.com/>`_ client library for
Python. It provides API clients and character encoding utilities.

Installation
============

Vesta requires Python 3.7 or later. It can be installed `via PyPI
<https://pypi.org/project/vesta/>`_::

    $ python -m pip install vesta

It's only runtime dependency is the `Requests`_ library, which will be
installed automatically.

.. _Requests: https://requests.readthedocs.io/

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
<https://docs.vestaboard.com/local>`_.

.. important::

    Vestaboard owners must first request a `Local API enablement token
    <https://www.vestaboard.com/local-api>`_ in order to use the Local API.

.. autoclass:: vesta.LocalClient
    :members:

Character Encoding
==================

All Vestaboard characters (letters, numbers, symbols, and colors) are encoded
as integer `character codes <https://docs.vestaboard.com/characters>`_. Vesta
includes some helpful routines for working with these character codes.

.. automodule:: vesta.chars
   :members: Row, Rows

.. autoclass:: vesta.Color
    :show-inheritance:
    :members:
    :undoc-members:
    :exclude-members: ansi

.. autofunction:: vesta.encode
.. autofunction:: vesta.encode_row
.. autofunction:: vesta.encode_text

.. autofunction:: vesta.pprint
