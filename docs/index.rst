Ramverk
=======


Sample Application: Hello World with Writable Greeting
------------------------------------------------------

First we need some boring imports::

  from persistent        import Persistent
  from werkzeug.routing  import Rule
  from ramverk.fullstack import Application
  from ramverk.utils     import request_property

We also make a persistent object that we will use as the root of our tree
of persistent objects. The actual root of the persistent storage is a dict
but using a virtual root like this is more maintainable - we can set
defaults, add methods to the root object, and access childrens as
attributes. Note that this object is just an object and does nothing fancy
except knowing when it's been mutated and needs to be written to the
storage.

::

  class Root(Persistent):

      greeting = 'Hello'

Now, we'll write the class for our application. We're using the "fullstack"
base to get all the bells and whistles and some nice defaults. Our
"virtual" root is simply a property, cached for each request, that reads a
specific key in the real root object. We also route a rule for ``/`` to the
`index` endpoint.

::

  class Greeter(Application):

      @request_property
      def db(self):
          if 'greeter' not in self.root_object:
              self.root_object['greeter'] = Root()
          return self.root_object['greeter']

      def setup(self):
          self.route(Rule(
              '/',
                  endpoint='index',
                  methods=('GET', 'POST')))

The function that handles the `index` endpoint is added with a decorator
classmethod. The arguments can be any or none and refer to attributes on
the application, which the dispatcher will then pass to the function.

::

  @Greeter.endpoint
  def index(request, render, db, redirect):

      if request.method == 'GET':
          return render('index.html', greeting=db.greeting)

      if request.method == 'POST':
          db.greeting = request.form.get('greeting')
          return redirect('index')

We also need to write the :file:`index.html` template:

.. sourcecode:: html+genshi

  <html>
    <body>
      <h1>$greeting, World!</h1>

      <form
       method="POST"
       action="${path('index')}">

        <input
         type="text"
         name="greeting"
         placeholder="Enter a greeting" />

      </form>
    </body>
  </html>

For a development server we can use Paver and write a :file:`pavement.py`::

  from paver.easy import task

  @task
  def serve():
      """Run the development server."""
      from werkzeug.serving import run_simple
      from greeter          import Greeter

      app = Greeter(debug=True)
      run_simple('localhost', 8080, app,
                 use_reloader=True,
                 use_debugger=True,
                 use_evalex  =True)


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
