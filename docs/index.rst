Ramverk
=======

The Full Stack
--------------

.. automodule:: ramverk.fullstack

  .. autoclass:: Application
    :members:
    :show-inheritance:

    .. attribute:: settings.storage

      :default: File storage based on the `name` setting.

.. autoclass:: HTMLResponse
  :show-inheritance:


The Base of Applications
------------------------

.. automodule:: ramverk.application

  .. autoclass:: AbstractApplication
    :members:

    :param settings:
      Used to update :attr:`settings`.

    :abstract:
      :attr:`log` must be set and :meth:`respond` must be implemented.

    .. attribute:: settings.debug

      Enable development niceties that shouldn't be enabled in production.
      May be read by mixins and have no particular effect in itself.

      :default: :const:`False`

    .. attribute:: settings.name

      Name of the application, may be used for log channels and database
      defaults and such.

      :default: The name of the class.

    .. automethod:: __enter__

    .. automethod:: __exit__

    .. automethod:: __call__


Dispatching Requests by URL
---------------------------

.. automodule:: ramverk.routing

  .. autoclass:: RoutingMixin
    :members:

    .. autoattribute:: endpoints


Rendering HTML with Genshi
--------------------------

.. automodule:: ramverk.genshi

  .. autoclass:: GenshiMixin
    :members:
    :show-inheritance:

    .. automethod:: _GenshiMixin__loader

.. automodule:: ramverk.templating
  :members:


Persisting Objects with ZODB
----------------------------

.. automodule:: ramverk.zodb

  .. autoclass:: ZODBMixin
    :members:

    .. attribute:: settings.storage

        Must be set to a callable returning a ZODB storage object.

.. automodule:: ramverk.transaction

  .. autoclass:: TransactionMixin

    .. important::

      Should be mixed in before anything that relies on transactions, such
      as :class:`~ramverk.zodb.ZODBMixin`.


Logging with Logbook
--------------------

.. automodule:: ramverk.logbook

  .. autoclass:: LogbookMixin
    :members:

    .. important::

      Should be mixed in at the top of the inheritance chain of the
      application so that all log records during requests pass through
      :attr:`log_handler`.


Common Utilities
----------------

.. automodule:: ramverk.utils

  .. autoclass:: Bunch
    :show-inheritance:

  .. autoclass:: request_property

  .. autoclass:: class_dict
