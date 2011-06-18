Ramverk
=======

.. toctree::
  :hidden:

  relvlast


Sample Application: Hello World with Writable Greeting
------------------------------------------------------

First we need some boring imports::

  from persistent        import Persistent
  from werkzeug.routing  import Rule
  from ramverk.fullstack import Application
  from ramverk.utils     import request_property
  from ramverk.routing   import router, endpoint, get, post

.. sidebar:: ZODB

  The ZODB is a transactional persistence system with ACID properties
  acting as an object database for Python. Whoa, what now? Well, it lets
  you use Python objects as if you ran a single process that never needed
  restarting and had close-to infinite memory. Sounds like magic, right? In
  reality it's just the :mod:`pickle` module with scalability added.

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
specific key in the persistent mapping. We also scan the module to register
the router and endpoint we'll add next.

::

  class Greeter(Application):

      @request_property
      def db(self):
          return self.persistent.setdefault('greeter', Root())

      def setup(self):
          self.scan()

This "scan" will look for functions decorated as routers and endpoints in
the same module as the application (because we passed no argument). A
"router" is a function that returns a list of URL patterns that map to
"endpoints" which in turn are functions that respond to requests.

The arguments to the endpoint function can be any or none and refer to
attributes on the application, which the dispatcher will then pass to the
function.

::

  @router
  def urls():
      yield Rule('/', endpoint='index', methods=('GET', 'POST'))

  @endpoint
  def index(request, render, db, redirect):

      if request.method == 'GET':
          return render('index.html', greeting=db.greeting)

      if request.method == 'POST':
          db.greeting = request.form.get('greeting')
          return redirect('index')

Optionally we could have written that in a style reminiscent of the Bottle
framework which is more limiting but sufficient for most situations::

  @get('/')
  def greet_visitor(render, db):
      return render('index.html', greeting=db.greeting)

  @post('/')
  def set_greeting(db, request, redirect):
      db.greeting = request.form.get('greeting')
      return redirect('greet_visitor')

.. sidebar:: Genshi

  Genshi templates are XML streams which means that we don't have to worry
  about escaping markup and don't need to bother with ensuring well-formed
  output. It also means we can change the serialization and doctype on the
  fly, extract messages for translation directly from the markup and that
  we can apply filters and transformations on the stream before it renders.
  This comes at the cost of speed but for most uses it is fast enough.

We also need to write the :file:`index.html` template:

.. sourcecode:: html+genshi

  <html>
    <body>
      <h1>$greeting, World!</h1>

      <form action="${path('index')}"
        method="POST">

        <input name="greeting"
          placeholder="Enter a greeting"
          type="text"/>

      </form>
    </body>
  </html>

For a development server we can use Paver and write a :file:`pavement.py`::

  from paver.easy    import options
  from ramverk.paver import serve

  options.ramverk.app = 'greeter:Greeter'

.. code-block:: console

  $ paver serve
  ---> ramverk.paver.serve
      INFO: Greeter:  * Running on http://localhost:8008/
      INFO: Greeter:  * Restarting with reloader: stat() polling
  ---> ramverk.paver.serve


Framework Design
----------------

In my experience with Flask I've noticed a few things:

.. rubric::
  Sooner or later you will want to use the application factory pattern.

Flask applications are singletons, built imperatively. This quickly becomes
an issue when you want to build the application conditionally based on some
arguments. The problem is easily solved by wrapping the creation of the
application in a function but what we end up with is effectively a sort of
custom object model to get the effects of class instances. Ramverk
applications use the language construct that exists to solve this very
problem: class-based OOP. Classes also know their name and containing
module so there's no need for passing ``__name__`` to anything.

.. rubric::
  At some point you'll need to subclass the Flask application class.

Because Ramverk uses the class construct, we're prepared for this up front
and don't need to refactor the application later. It isn't difficult to do
this refactoring with Flask but the premise of it seems to scare people:
they think of the Flask class as some opaque thing you shouldn't mess with.

.. rubric::
  There's always a use case for hooking parts of the framework.

Flask solves this by emitting blinker signals and providing decorators with
which to register callback functions for different situations, such as
"before request" or "handle this http error". The former case covers only
cases where a signal has specifically been emitted and the latter case
requires Flask to know how to deal with multiple callbacks and how they
interact with each other. Both of these cases are really, again,
reimplementations of OOP constructs: signals correspond to method
overloading and callback handling to the method resolution order. Ramverk is
designed for cooperative multiple inheritance; as an effect of this you
can, and in fact, are expected to hook *any* part of the framework and you
are in control of how your hooks interact. In Ramverk, "everything is a
mixin" and "everything is a cooperative method". Flask is actually well
designed for this kind of usage as well, but it isn't the *primary* way you
use the framework.

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

.. rubric::
  Coupling routing with views eventually leads to pain.

Another thing that I've noticed is that at least before 0.7, routing in
Flask is substandard to Werkzeug. This is in part because routes are
directly associated with views so without going around it we can only use
"rules" and not "rule factories"; in part because views are expected to
read *all* values that matched in the rule. The result of this is that it's
inconvenient to add a "submount" for say a locale code.

A solution to this problem is to keep Werkzeug's separation of
rules/endpoints and "view" functions, and not require of view functions
that they read all the rule variables. This lets us use rule factories
like :class:`~werkzeug.routing.Submount` easily.

----

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
    :show-inheritance:

    .. inheritance-diagram:: Application
      :parts: 1

    .. attribute:: settings.storage

      :default: File storage based on the `name` setting.

    .. autoattribute:: log_handler

    .. autoattribute:: request

      .. inheritance-diagram:: werkzeug.wrappers.Request
        :parts: 1

    .. autoattribute:: response

      .. inheritance-diagram:: HTMLResponse
        :parts: 1

  .. autoclass:: HTMLResponse
    :members:
    :show-inheritance:


Minimal Base for Applications
-----------------------------

.. automodule:: ramverk.application

  .. autoclass:: BaseApplication
    :members:

    The call stack for WSGI requests looks like this:

    .. digraph:: request

      __call__ -> bind_to_environ;
      bind_to_environ -> __enter__;
      bind_to_environ -> respond;
      respond -> response;
      respond -> error_response -> response;
      bind_to_environ -> __exit__;

    :param settings:
      Used to update :attr:`settings`.

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

    .. automethod:: __call__(environ, start_response)

  .. autoclass:: Response
    :members:
    :show-inheritance:


Dispatching Requests by URL
---------------------------

The call stack for WSGI requests with URL dispatch adds this:

.. digraph:: dispatch

  "endpoint name" [fontname="Ubuntu Italic"];
  "view function" [fontname="Ubuntu Italic"];
  respond -> url_adapter -> "endpoint name" -> endpoints -> "view function" -> call_view;

.. automodule:: ramverk.routing

  .. autofunction:: router

  .. autofunction:: endpoint

  .. autofunction:: route

  .. autofunction:: get

  .. autofunction:: post

  .. autofunction:: put

  .. autofunction:: delete

  .. autoclass:: RoutingScannerMixin
    :members:

  .. autoclass:: RoutingHelpersMixin
    :members:

  .. autoclass:: URLMapMixin
    :members:

  .. autoclass:: RoutingMixin
    :members:
    :show-inheritance:


Rendering Content
-----------------

.. automodule:: ramverk.wrappers
  :members:

.. automodule:: ramverk.rendering

  .. autoclass:: RenderingMixinBase
    :members:

  .. autoclass:: JSONMixin
    :members:
    :show-inheritance:

    .. automethod:: _JSONMixin__default


Templating with Genshi
----------------------

.. automodule:: ramverk.genshi

  .. autoclass:: GenshiMixin
    :show-inheritance:

    These renderers are configured by default:

    .. list-table::
      :header-rows: 1

      * - Renderer
        - Serializer
        - Doctype
        - Mimetype
        - Class
      * - ``'.html'``
        - :class:`HTML <genshi.output.HTMLSerializer>`
        - HTML 5
        - :mimetype:`text/html`
        - MarkupTemplate_
      * - ``'.xhtml'``
        - :class:`XML <genshi.output.XMLSerializer>`
        - XHTML 1.1
        - :mimetype:`application/xhtml+xml`
        - MarkupTemplate_
      * - ``'.atom'``
        - :class:`XML <genshi.output.XMLSerializer>`
        -
        - :mimetype:`application/atom+xml`
        - MarkupTemplate_
      * - ``'.svg'``
        - :class:`XML <genshi.output.XMLSerializer>`
        - SVG
        - :mimetype:`image/svg+xml`
        - MarkupTemplate_
      * - ``'.xml'``
        - :class:`XML <genshi.output.XMLSerializer>`
        -
        - :mimetype:`application/xml`
        - MarkupTemplate_
      * - ``'.txt'``
        - :class:`Text <genshi.output.TextSerializer>`
        -
        - :mimetype:`text/plain`
        - NewTextTemplate_

    .. admonition:: Notes

      * None of the preconfigured renderers serialize lazily by default.
      * You probably don't want to use the XHTML renderer.

    .. _MarkupTemplate: http://genshi.readthedocs.org/en/latest/xml-templates/

    .. _NewTextTemplate: http://genshi.readthedocs.org/en/latest/text-templates/

    .. automethod:: _GenshiMixin__loader

    .. automethod:: template_loaded

  .. autoclass:: GenshiRenderer

    .. autoattribute:: serializer

        ============= ========= ========== ======== =======
        input         xml       xhtml      html     text
        ============= ========= ========== ======== =======
        ``<hr></hr>`` ``<hr/>`` ``<hr />`` ``<hr>`` *empty*
        ``<a>b</a>``  *same*    *same*     *same*   ``b``
        ============= ========= ========== ======== =======

      See :func:`~genshi.output.get_serializer` for more information.

    .. autoattribute:: doctype

      Can be a string or a tuple, see :class:`~genshi.output.DocType` for
      more information.

    .. autoattribute:: mimetype

    .. autoattribute:: class_

    .. autoattribute:: lazy


    Example::

      def setup(self):
          self.renderers['.svg'] = GenshiRenderer(self, 'xml', 'svg', 'image/svg+xml')

.. autoclass:: ramverk.rendering.TemplatingMixinBase
  :members:
  :show-inheritance:


Compiling Static Resources On-Demand
------------------------------------

.. automodule:: ramverk.compiling

  .. autoclass:: CompilerMixinBase
    :members:
    :show-inheritance:

    A "compiler" is like a middleground between static files and renderers.
    Unlike renderers there is no "context", everything needed to compile
    the source should be in the source. Unlike static files, these sources
    need preprocessing before their rendered state can be sent to clients.
    This is primarily a convenience for development where these sources may
    change at any time but for production deployments these files should
    usually be precompiled up front and served as static files.

    Compilation sources are stored in :file:`{package}/compiled` and are
    compiled on-demand for GET requests to ``/compiled/`` at the
    application root. The file extension is mapped to a compiler in
    :attr:`compilers` which compiles a corresponding file (usually with a
    different file extension) into a response. A ``'compiled'`` endpoint is
    set up so you can build URLs e.g. ``path('compiled',
    name='main.css')`` → ``'/compiled/main.css'`` which in turn sends a
    compiled version of :file:`compiled/main.scss` if the mixin below is
    used.


Styling with SCSS
-----------------

.. automodule:: ramverk.scss

  .. autoclass:: SCSSMixin
    :show-inheritance:

    Compiles Sassy stylesheets in :file:`{source}.scss` files into
    :file:`{compiled}.css` responses.


Persisting Objects with ZODB
----------------------------

.. automodule:: ramverk.zodb

  .. autoclass:: ZODBMixin
    :members:

    .. attribute:: settings.storage

        Must be set to a callable returning a ZODB storage object.

    .. autoattribute:: _ZODBMixin__db

    .. autoattribute:: _ZODBMixin__connection


.. automodule:: ramverk.transaction

  .. autoclass:: TransactionMixin
    :members:

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


Task Management with Paver
--------------------------

.. automodule:: ramverk.paver

  :file:`pavement.py`::

    from paver.easy    import options
    from ramverk.paver import serve, shell

    options.ramverk.app = 'dotted.path.to:AppClass'


  .. autofunction:: serve()

  .. autofunction:: shell()

    This will create an app bound to a fake request and add it to the shell
    locals as `app`. If installed, `bpython`_ is used, otherwise a normal
    Python console.

    .. _bpython: http://bpython-interpreter.org/


WSGI Middlewares
----------------

.. automodule:: ramverk.wsgi

  .. autoclass:: SharedDataMiddlewareMixin
    :members:

  .. autofunction:: mixin_from_middleware

    Example::

      from werkzeug._internal import _easteregg

      class App(mixin_from_middleware(_easteregg), BaseApplication):
          pass

  .. autofunction:: middleware_mixin

    Example::

      from werkzeug._internal import _easteregg

      @middleware_mixin
      class EasterEggMiddlewareMixin(object):

          def pipeline(self, app):
              return _easteregg(app)

      class App(EasterEggMiddlewareMixin, BaseApplication):
          pass


Common Utilities
----------------

.. automodule:: ramverk.utils

  .. autoclass:: Bunch
    :show-inheritance:

  .. autoclass:: request_property

  .. autofunction:: has

    This is useful for setting attribute defaults for mutable types or
    deferred values. Example::

      @has(comments=list, timestamp=datetime.utcnow)
      class Post(object):
          author = None

    Note that the values aren't initialized until asked for - in the
    example above the timestamp isn't necessarily that of the post
    creation. A solution for that case is to inherit from
    :class:`EagerCachedProperties`.

  .. autoclass:: EagerCachedProperties

  .. autoclass:: ReprAttributes

  .. autoclass:: InitFromArgs
    :members: __create__

  .. autofunction:: args

    Example::

      @args('question', 'answer')
      class QA(InitFromArgs):
          pass

    >>> vars(QA())
    {'answer': None, 'question': None}
    >>> vars(QA('What is the ultimate answer?'))
    {'answer': None, 'question': 'What is the ultimate answer?'}
    >>> vars(QA('What is the ultimate answer?', 42))
    {'answer': 42, 'question': 'What is the ultimate answer?'}
    >>> vars(QA(answer=42, question='What is the ultimate answer?'))
    {'answer': 42, 'question': 'What is the ultimate answer?'}
    >>> vars(QA(answer=42))
    {'answer': 42, 'question': None}
