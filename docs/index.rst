Ramverk
=======

The Full Stack
--------------

.. automodule:: ramverk.fullstack

  .. autoclass:: Application
    :members:
    :show-inheritance:

.. autoclass:: HTMLResponse


The Base of Applications
------------------------

.. automodule:: ramverk.application

  .. autoclass:: AbstractApplication
    :members:

    :param settings:
      Used to update :attr:`settings`.


Dispatching Requests by URL
---------------------------

.. automodule:: ramverk.routing
  :members:


Logging with Logbook
--------------------

.. automodule:: ramverk.logbook

  .. autoclass:: LogbookMixin
    :members:

    .. note::

      Should be mixed in at the top of the inheritance chain of the
      application so that all log records during requests pass through
      :attr:`log_handler`.


Persisting Objects with ZODB
----------------------------

.. automodule:: ramverk.transaction

  .. autoclass:: TransactionMixin

    .. note::

      Should be mixed in before anything that relies on transactions, such
      as :class:`~ramverk.zodb.ZODBMixin`.

.. automodule:: ramverk.zodb
  :members:


Rendering HTML with Genshi
--------------------------

.. automodule:: ramverk.genshi
  :members:
  :show-inheritance:

.. automodule:: ramverk.templating
  :members:


Common Utilities
----------------

.. automodule:: ramverk.utils

  .. autoclass:: Bunch
    :show-inheritance:

  .. autoclass:: request_property

    Like :class:`~werkzeug.utils.cached_property` but cached in the
    object's `local` attribute, which in applications are cleared for every
    request. Can be used to create lazily cached request-local properties.
