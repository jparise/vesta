=====
Vesta
=====

Vesta is a `Vestaboard <https://www.vestaboard.com/>`_ client library for
Python. It provides API clients and character encoding utilities.

.. toctree::
   :hidden:

   changelog
   GitHub Project <https://github.com/jparise/vesta>

Installation
============

Vesta requires Python 3.9 or later. It can be installed `via PyPI
<https://pypi.org/project/vesta/>`_::

    $ python -m pip install vesta

Vesta has no runtime dependencies and uses only the Python standard library.

API Clients
===========

Cloud API
---------

:py:class:`vesta.CloudClient` provides a client interface for interacting with
a Vestaboard using the `Cloud API
<https://docs.vestaboard.com/docs/read-write-api/endpoints>`_, which supersedes
the Read / Write API (:py:class:`vesta.ReadWriteClient`). It supports reading
and writing messages and configuring `message transitions
<https://docs.vestaboard.com/blog/transitions-api/>`_.

.. important::

    A Vestaboard API token is required. This token can be obtained from the
    `Developer section of the web app <https://web.vestaboard.com/>`_.

.. autoclass:: vesta.CloudClient
    :members:

Subscription API
----------------

:py:class:`vesta.SubscriptionClient` provides a client interface for interacting
with multiple Vestaboards using the `Subscription API
<https://docs.vestaboard.com/docs/subscription-api/introduction>`_.

.. important::

    An API secret and key is required to get subscriptions or send messages.
    These credentials can be created from the `Developer section of the web
    app <https://web.vestaboard.com/>`_.

.. autoclass:: vesta.SubscriptionClient
    :members:

Local API
---------

:py:class:`vesta.LocalClient` provides a client interface for interacting with
a Vestaboard over the local network using `Vestaboard's Local API
<https://docs.vestaboard.com/docs/local-api/introduction>`_.

.. important::

    Vestaboard owners must first request a `Local API enablement token
    <https://www.vestaboard.com/local-api>`_ in order to use the Local API.

.. autoclass:: vesta.LocalClient
    :members:

VBML API
--------

:py:class:`vesta.VBMLClient` provides a client interface for Vestaboard's
`VBML (Vestaboard Markup Language) <https://docs.vestaboard.com/docs/vbml>`_
API.

.. autoclass:: vesta.VBMLClient
    :members:

Read / Write API
----------------

:py:class:`vesta.ReadWriteClient` provides a client interface for interacting
with a Vestaboard using the **deprecated** Read / Write API.

.. warning::

    Vestaboard has renamed the Read / Write API to the Cloud API. This client
    is **deprecated**; switch to :py:class:`vesta.CloudClient`, which offers
    the same functionality plus message transitions.

.. autoclass:: vesta.ReadWriteClient
    :members:

Platform API
------------

:py:class:`vesta.Client` provides a client interface for interacting with the
**deprecated** `Vestaboard Platform API <https://docs-v1.vestaboard.com/introduction>`_.

.. warning::

    This is the original Vestaboard Platform API. It is **deprecated** and has
    been superseded by the other APIs listed above. In particular, Vestaboard
    encourages users of the Platform API to switch to the Subscription API,
    which offers nearly identical functionality.

.. autoclass:: vesta.Client
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
   :members:  Component, Position, Props, Style
   :member-order: groupwise
