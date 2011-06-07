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
defaults, add methods to the root object, and access children as
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
         placeholder="Enter a greeting"/>

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


Framework Design
----------------

In my experience with Flask I've noticed a few things:

#. Rather soon you will want to use the application factory pattern.
#. Sooner or later you'll need to subclass the Flask application class.
#. There's an ever-growing need to hook parts of the framework; blinker
   signals are used for this.

Ramverk uses subclassing from start which also gives us application
factories for free - just create an instance. Everything is built with
cooperative mixins using multiple-inheritance, taking care to do very
little, specific things in every method and treating the methods as the
signals. All hooking is done with overrides and all mixins and subclasses
are assumed to be well-behaved and call :func:`super` where needed. They
are of course also free to not call super if that makes sense for any
particular case.

This is an immensely powerful approach but demands a certain level of
expertise from the programmer. I'm writing Ramverk for my own personal use
and expect that any other potential (however unlikely) users are capable
programmers who aren't afraid to dig into the guts of the source code.

It has been said that extending through subclassing a framework's classes
is a `bad idea`_ but I think this is primarily relevant when the classes
are not designed for it from the start. It could also be said that
cooperative overrides suffer from issues similar to those of Rails'
``alias_method_chain`` but again I would say the issue there is (or was)
the lack of a clearly defined public API and the hooking of private
internals.

.. _bad idea:
  http://be.groovie.org/post/1347858988/why-extending-through-subclassing-a-frameworks

To paraphrase an old saying,

  He who does not understand OOP is bound to reinvent it.

I'm sure Armin understands OOP very well, much better than me even, and
this of course is meant to be tongue-in-cheek. The point is that if you
don't use classes where they make sense, you'll end up implementing similar
behavior yourself. It seems sensible to me to instead use the constructs
the language provides for it.

Another thing that I've noticed is that at least before 0.7, routing in
Flask is substandard to Werkzeug. A solution to this problem is to keep
Werkzeug's separation of rules/endpoints and "view" functions, and not
require of view functions that they read *all* the rule variables.  This
lets us use rule factories like :class:`~werkzeug.routing.Submount` easily.

Frameworks also face the problem of making view functions friendly to unit
testing. Flask requires a fake request context be pushed to a stack and
uses blinker signals for rendered templates. Some think this makes the
functions a little too complicated and Pyramid instead passes the request
to the views and lets views return a mapping to be used as the context for
a "renderer", i.e. a template.

My approach in Ramverk is to let views be explicit about what they need
from an application and pass application attributes based on the signature
of the view function. Attributes include the request object and a render
method for templating. In unit tests, views can instead be passed fake
request objects and a dumbed-down render function that, say, just return
its arguments as-is. Given the sample application above we might do::

  from werkzeug.wrappers import Request
  from werkzeug.test     import create_environ

  def render(template_name, **context):
      return template_name, context

  def test():
      request = Request(create_environ())
      template, context = index(request=request,
                                render=render,
                                db=app.db,
                                redirect=app.redirect)

      assert context['greeting'] == 'Hello'

As you can see it would similarly be trivial to fake the `db` or for
example hook redirections.


The Full Stack
--------------


.. automodule:: ramverk.fullstack

  .. autoclass:: Application
    :members:
    :show-inheritance:

    .. inheritance-diagram:: Application
      :parts: 1

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
      :attr:`log` must be set.

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
