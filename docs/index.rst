Ramverk
=======

.. toctree::
  :hidden:

  relvlast

:term:`Ramverk` is a :term:`Werkzeug` framework built around
:term:`cooperative mixins <cooperative mixin>`. At the base is a WSGI
application class implementing the "least common denominator". Framework
components such as data persistence and markup templating are all
composable mixins building on the application base that can be combined and
cherry-picked to create a custom-tailored application. For the most part
Ramverk is a collection of small pieces of glue for third-party
technologies and Ramverk itself tries to do and be as little as possible.

Though the source code is published on GitHub_, there are currently no
plans to release Ramverk officially. Ramverk is being built as a custom
Werkzeug configuration for me personally and this document serves as
documentation for contributors to Ramverk applications and as a design
document under construction, for discussing choices with other developers
and as a memory aid for myself.

.. _GitHub: https://github.com/dag/relvlast

I welcome you to study my decisions and maybe learn from them, or
conversely teach me why I should do something differently. I advice against
using Ramverk for yourself however, unless you create your own fork. One
upside to not comitting to a release is that I can change anything at any
time and not bother myself with backwards-compatibility. In the end if
something useful and stable emerges and there is interest, I'll reconsider
releasing, but really, there's an abundance of great frameworks in
existence and if you want something more custom I recommend you do like me
and build your own glue around Werkzeug. It's easier than you might think
and a fun, rewarding activity that gives you insight into what makes other
frameworks tick and why they do what they do.


Sample Application: Hello World with Writable Greeting
------------------------------------------------------

First we need some boring imports::

  from persistent        import Persistent
  from werkzeug.routing  import Rule
  from ramverk.fullstack import Application
  from ramverk.utils     import request_property
  from ramverk.routing   import MethodDispatch, router, route, get, post

.. sidebar:: ZODB

  The :term:`ZODB` is a transactional persistence system with ACID
  properties acting as an object database for Python. Whoa, what now? Well,
  it lets you use Python objects as if you ran a single process that never
  needed restarting and had close-to infinite memory. Sounds like magic,
  right? In reality it's just the :mod:`pickle` module with scalability
  added.

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
specific key in the persistent mapping. We also :term:`scan <Venusian>` the
module to register the :term:`router` and :term:`endpoint` we'll add next.

::

  class Greeter(Application):

      @request_property
      def db(self):
          return self.persistent.setdefault('greeter', Root())

      def configure(self):
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

  def index(request, render, db, redirect):

      if request.method == 'GET':
          return render('index.html', greeting=db.greeting)

      if request.method == 'POST':
          db.greeting = request.form.get('greeting')
          return redirect(':index')

Optionally we could have written that in a style reminiscent of the Bottle
framework which is more limiting but sufficient for most situations::

  @get('/')
  def greet_visitor(render, db):
      return render('index.html', greeting=db.greeting)

  @post('/')
  def set_greeting(db, request, redirect):
      db.greeting = request.form.get('greeting')
      return redirect(':greet_visitor')

Or why not a class::

  @route('/')
  class Index(MethodDispatch):

      def get(self, render, db):
          return render('index.html', greeting=db.greeting)

      def post(self, db, request, redirect):
          db.greeting = request.form.get('greeting')
          return redirect(':Index')

The argument to the redirect function is an endpoint name. Scanned
endpoints are named by the fully qualified dotted name of the view function
and a prefixing colon means "relative to current endpoint". A dot prefix is
also allowed which prepends the module of the application to the endpoint
and is useful when the application is a Python package with views spread
out in modules.

.. sidebar:: Genshi

  :term:`Genshi` templates are markup streams which means that we don't
  have to worry about escaping markup and don't need to bother with
  ensuring well-formed output. It also means we can change the
  serialization and doctype on the fly, extract messages for translation
  directly from the markup and that we can apply filters and
  transformations on the stream before it renders. This comes at the cost
  of speed but for most uses it is fast enough.

We also need to write the :file:`index.html` template. We'll use
:term:`Genshi` with the :term:`Compact XML` dialect:

.. sourcecode:: compactxml+genshi

    <html
        <body
            ?indent restart

    <h1
        "$greeting, World!

    <form
        @action=${path(':index')}
        @method=POST

        <input
            @name=greeting
            @placeholder=Enter a greeting
            @type=text

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


    .. centered:: Application

    .. automethod:: configure

    .. autoattribute:: settings

    .. attribute:: settings.debug

      Enable development niceties that shouldn't be enabled in production.
      May be read by mixins and have no particular effect in itself.

      :default: :const:`False`

    .. attribute:: settings.name

      Name of the application, may be used for log channels and database
      defaults and such.

      :default: The name of the class.

    .. autoattribute:: module

      Used by mixins to locate templates and endpoints and such. Defaults
      to the module the application class was defined in, which is usually
      what you want.

    .. autoattribute:: log


    .. centered:: Context Locals

    .. automethod:: request_context(environ)

    .. autoattribute:: local_stack

    .. autoattribute:: local

    .. attribute:: local.environ

      WSGI environment of the current request.

    .. attribute:: local.application

      This application object; mainly useful when :attr:`local_stack` is
      shared between multiple applications, which is the default: inside
      request contexts, :attr:`stack.top.application <ramverk.local.stack>`
      is the active application.

    .. autoattribute:: request


    .. centered:: WSGI

    .. autoattribute:: response

    .. automethod:: respond

    .. automethod:: respond_for_error

    .. automethod:: __call__(environ, start_response)


    .. centered:: Hooking-points for Mixins

    .. automethod:: __create__

    .. automethod:: __enter__

    .. automethod:: __exit__


.. automodule:: ramverk.local

  .. attribute:: stack

    Shared :class:`~werkzeug.local.LocalStack` used as the default by
    applications.


Dispatching Requests by URL
---------------------------


.. automodule:: ramverk.routing

  .. autofunction:: router

    Endpoints will be prefixed with the module of the decorated callable
    plus a colon. The scan can optionally take the keywords `submount` and
    `subdomain` as strings which will wrap the rules in the corresponding
    rule factories. Example::

      @router
      def urls():
          yield Rule('/', endpoint='index')

      def index(response):
          return response('Howdy')

      class App(Application):
          def configure(self):
              self.scan(submount='/<locale>')

  .. autofunction:: route

    The dotted name of the decorated callable will be used as the endpoint
    and a :class:`~werkzeug.routing.Rule` using the arguments of the
    decorator will be created and added. Example::

      @route('/')
      def index(response):
          return response('Howdy')

  .. autofunction:: get

  .. autofunction:: post

  .. autofunction:: put

  .. autofunction:: delete

  .. autoclass:: RoutingHelpersMixin
    :members:

  .. autoclass:: URLMapMixin
    :members:

  .. autoclass:: RoutingMixin
    :members:
    :show-inheritance:

  .. autoclass:: MethodDispatch

    Example::

      @route('/')
      class Index(MethodDispatch):

          renderer = 'index.html'

          def __init__(self, db):
              self.greeting = db.greeting

          def get(self, render):
              return render(self.renderer, greeting=self.greeting)


.. automodule:: ramverk.venusian
  :members:


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
        - Dialect
      * - ``'.html'``
        - :class:`HTML <genshi.output.HTMLSerializer>`
        - HTML 5
        - :mimetype:`text/html`
        - :class:`CompactHTMLTemplate`
      * - ``'.xhtml'``
        - :class:`XML <genshi.output.XMLSerializer>`
        - XHTML 1.1
        - :mimetype:`application/xhtml+xml`
        - :class:`CompactTemplate`
      * - ``'.atom'``
        - :class:`XML <genshi.output.XMLSerializer>`
        -
        - :mimetype:`application/atom+xml`
        - :class:`CompactTemplate`
      * - ``'.svg'``
        - :class:`XML <genshi.output.XMLSerializer>`
        - SVG
        - :mimetype:`image/svg+xml`
        - :class:`CompactTemplate`
      * - ``'.xml'``
        - :class:`XML <genshi.output.XMLSerializer>`
        -
        - :mimetype:`application/xml`
        - :class:`CompactTemplate`
      * - ``'.txt'``
        - :class:`Text <genshi.output.TextSerializer>`
        -
        - :mimetype:`text/plain`
        - `NewTextTemplate <http://genshi.readthedocs.org/en/latest/text-templates/>`_

    .. admonition:: Notes

      * None of the preconfigured renderers serialize lazily by default.
      * You probably don't want to use the XHTML renderer.
      * See the documentation for `XML templates
        <http://genshi.readthedocs.org/en/latest/xml-templates/>`_ for both
        :class:`HTMLTemplate` and :class:`CompactTemplate`.

    .. autoattribute:: template_loaders

    .. autoattribute:: genshi_loader

    .. automethod:: configure_genshi_template

    .. automethod:: filter_genshi_stream

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

    .. autoattribute:: dialect

    .. autoattribute:: lazy

    .. automethod:: filter

    Example::

      def configure(self):
          self.renderers['.svg'] = GenshiRenderer(self, 'xml', 'svg', 'image/svg+xml')

  .. autoclass:: CompactTemplate
    :members:

    Less talkative than XML while still as predictable and consistent, but
    less standard and familiar than either XML or HTML. Subclass to
    override the option attributes.

  .. autoclass:: CompactHTMLTemplate

  .. autoclass:: HTMLTemplate
    :members:

    This allows for less verbose HTML templates by allowing unclosed tags
    and unquoted attributes and not requiring all namespaces be declarated
    explicitly, but is less predictable and generic than the more strict
    XML dialect.

.. autoclass:: ramverk.rendering.TemplatingMixinBase
  :members:
  :show-inheritance:


Compiling Static Resources On-Demand
------------------------------------

.. automodule:: ramverk.compiling

  .. autoclass:: CompilerMixinBase
    :members:

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

  .. attribute:: options.ramverk.app

    :term:`Dotted name` of your application class.

  Example :file:`pavement.py`::

    from paver.easy    import options
    from ramverk.paver import serve, shell

    options.ramverk.app = 'my.own:Application'

  .. autofunction:: serve()

    .. attribute:: options.serve.hostname

      Host to listen on.

      :default: ``localhost``

    .. attribute:: options.serve.port

      Port number to listen on.

      :default: ``8008``

    .. attribute:: options.serve.debug

      Sets the :attr:`~ramverk.application.BaseApplication.settings.debug`
      setting for the served application.

      :default: :const:`True`

  .. autofunction:: shell()

    This will create an app bound to a fake request and add it to the shell
    locals as `app`. If installed, `bpython`_ is used, otherwise a normal
    Python console.

    .. _bpython: http://bpython-interpreter.org/

    .. attribute:: options.shell.namespace

      :term:`Dotted name` of a module to use as the namespace inside the
      shell.

      :default:
        The :attr:`~ramverk.application.BaseApplication.module` of the
        :attr:`~ramverk.paver.options.ramverk.app`.

    .. attribute:: options.shell.fake_request

      Path to fake a request to before entering the shell.

      :default: ``/``


WSGI Middlewares
----------------

.. automodule:: ramverk.wsgi

  .. autoclass:: SharedDataMiddlewareMixin
    :members: __create__, shared_data

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


Glossary
--------

.. centered:: Technologies

.. glossary::

  Ramverk
    Swedish for *framework* and a nod to :term:`Werkzeug` which in turn is
    German for *utility*.

  Werkzeug
    `Werkzeug <http://werkzeug.pocoo.org/>`_ is a swiss army knife for
    WSGI, similar in scope to `Paste <http://pythonpaste.org/>`_ and `WebOb
    <http://pythonpaste.org/webob/>`_. Ramverk uses Werkzeug's
    request/response wrappers and its routing module for URL dispatch,
    among other things.

  Genshi
    `Genshi <http://genshi.edgewall.org/>`_ is primarily an engine for XML
    templating, useful for generating XML-like content for the web, such as
    HTML or Atom feeds. It is an optional mixin in Ramverk and included
    with the full-stack.

  Compact XML
    `Compact XML <http://packages.python.org/compactxml/>`_ is a language
    that compiles to XML, using indentation for nesting similar to Python.

  Flatland
    `Flatland <http://readthedocs.org/docs/flatland/en/latest/>`_ is a
    toolkit for processing and validating flat datastructures against
    schemata defined in declarative Python code and is useful for
    sanitizing user input in HTML forms among other things.

  SCSS
    `SCSS <http://sass-lang.com/>`_ or "Sassy CSS" is a superset of CSS
    that adds rule nesting, mixins, constants and other such things making
    stylesheets more maintainable.

  ZODB
    `ZODB <http://zodb.readthedocs.org/en/latest/>`_ is a scalable
    :mod:`pickle`, adding transactions and support for multi-process
    setups.

  Venusian
    `Venusian <http://docs.pylonsproject.org/projects/venusian/dev/>`_ is a
    library for implementing decorators that are activated by scanning.
    This allows decorators to be reusable and decoupled from applications
    without the use of a global registry.

  Babel
    `Babel <http://babel.edgewall.org/>`_ is a toolkit for
    internationalizing Python applications and includes a system for
    extracting translation messages and a repository of locale data.

  Logbook
    `Logbook <http://packages.python.org/Logbook/>`_ is a modern logging
    system for Python built with the demands of complex web deployments in
    mind.

  Paver
    `Paver <http://paver.github.com/paver/>`_ is a tool for scripting tasks
    with Python and is useful for managing a project in development.


.. centered:: Terminology

.. glossary::
  :sorted:

  dotted name
    String representation of the import path to an object, in the form
    ``package.module:member.attribute`` or any variation thereof. These can
    be dereferenced with :func:`~werkzeug.utils.import_string` and are used
    for endpoints in Ramverk.

  endpoint name
    Identifier associated with URL rules, in Ramverk usually a
    :term:`dotted name` for the :term:`endpoint` function or class.

  endpoint
    In Ramverk, a function or class that responds to a request matching a
    URL rule. In :term:`Werkzeug`, an arbitrary object otherwise the same
    as an :term:`endpoint name`.

  relative endpoint
    A partial endpoint name, expanded to its full form using the endpoint
    of the current request and the module name of the application.

  router
    Callable returning an iterable of :class:`URL rules
    <werkzeug.routing.Rule>`; usually a generator function.

  mixin
    Class meant to be *mixed in* with at least one base class in an
    inheritance chain, and *not* used alone or as a base itself.

  cooperative mixin
    :term:`Mixin` that calls :func:`super` in overridden methods to
    cooperate with other mixins and base classes.
