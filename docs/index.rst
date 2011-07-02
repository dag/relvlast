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

.. sidebar:: ZODB

  The :term:`ZODB` is a transactional persistence system with ACID
  properties acting as an object database for Python. Whoa, what now? Well,
  it lets you use Python objects as if you ran a single process that never
  needed restarting and had close-to infinite memory. Sounds like magic,
  right? In reality it's just the :mod:`pickle` module with scalability
  added.

Our sample application is writable which means we'll need persistence. To
that end we create an object that we will use as the root of our persistent
object tree. We use the :class:`~persistent.Persistent` base class which is
simply an :func:`object` that tracks modifications so it is only saved when
needed.

::

  from persistent import Persistent

  class Root(Persistent):

      greeting = 'Hello'

For convenience we write a property for accessing the root object, creating
one if needed. This is achieved by extending the "environment" - a
thread-safe object created for every request.

::

  from werkzeug.utils import cached_property
  from ramverk import fullstack

  class Environment(fullstack.Environment):

      @cached_property
      def db(self):
          return self.persistent.setdefault('greeter', Root())

To expose the object over HTTP we route some endpoints that decide what to
do with requests matching certain paths or methods. The endpoints receive
attributes from the environment as keyword arguments, but only the
attributes they ask for::

  from ramverk.routing import get, post

  @get('/')
  def greet_visitor(render, db):
      return render('index.html', greeting=db.greeting)

  @post('/')
  def set_greeting(db, request, redirect):
      db.greeting = request.form['greeting']
      return redirect(':greet_visitor')

Fairly straight-forward. The
:meth:`~ramverk.routing.URLMapAdapterMixin.redirect` function takes the
name of an endpoint. Endpoints are named by the fully qualified
:term:`dotted name` of the endpoint function or class but functions like
redirect also accept :term:`relative endpoint` names that are resolved in
the context of the request. In this case, the request endpoint is
``greeter:set_greeting`` (assuming we put the application in
:file:`greeter.py`) which means that ``:greet_visitor`` is resolved to
``greeter:greet_visitor``.

But wait a minute: what sort of sorcery is this that these functions become
exposed on the web server just by being decorated as endpoints?  Actually,
there is no magic - these decorators are "declarative" more than they are
"imperative" - to use these endpoints we must first register them with an
application. We can automate this procedure by scanning modules and
packages, looking for decorated objects defined in the top-level namespace.
Our application also needs to be told to use our custom environment class
so the endpoints can use our :attr:`db` property::

  class Greeter(fullstack.Application):

      environment = Environment

      def configure(self):
          self.scan()

The default behavior of :meth:`~ramverk.venusian.VenusianMixin.scan` is to
look in the module the application is defined in, so in this simple case we
don't need to pass it any arguments.

.. sidebar:: Genshi

  :term:`Genshi` templates are markup streams which means that we don't
  have to worry about escaping markup and don't need to bother with
  ensuring well-formed output. It also means we can change the
  serialization and doctype on the fly, extract messages for translation
  directly from the markup and that we can apply filters and
  transformations on the stream before it renders. This comes at the cost
  of speed but for most uses it is fast enough.

One thing left to do before we can rock this application! Can you guess
what? We need to write the :file:`index.html` template that we're rendering
in our :func:`greet_visitor` endpoint. We'll use :term:`Genshi` for its raw
power and parse templates with :term:`Compact XML` because no one likes to
write XML by hand.

.. sourcecode:: compactxml+genshi

    <html
        <body
            ?indent restart

    <h1
        "$greeting, World!

    <form
        @action=${path(':set_greeting')}
        @method=POST

        <input
            @name=greeting
            @placeholder=Enter a greeting
            @type=text

That wasn't so hard was it? Compact XML is a dialect of XML that, like
Python and YAML, bases the syntactical structure on the indentation of each
line meaning we don't need to write closing tags and don't need to quote
attributes even if they contain spaces. The "indent restart" just means to
continue at the first column while keeping the nesting level, so we can
nest deeply while keeping our sanity intact. The
:meth:`~ramverk.routing.URLMapAdapterMixin.path` function takes an
:term:`endpoint name` just like the :func:`redirect` function we used
earlier, and returns an absolute path on the web server that routes to the
specified endpoint. This way we can change the routes or mount the
application at a subdirectory on the webserver without changing our
template, but in this simple scenario the path function will simply return
``/``.

To run the application in development mode we can use :term:`Paver`.
Ramverk includes a few helpful tasks that we can import in our
:file:`pavement.py` and configure to use the Greeter application::

  from paver.easy import options
  from ramverk.paver import *

  options.app = 'greeter:Greeter'

.. code-block:: console

  $ paver serve
  ---> ramverk.paver.serve
      INFO: werkzeug:  * Running on http://localhost:8008/
      INFO: werkzeug:  * Restarting with reloader: stat() polling
  ---> ramverk.paver.serve

As a bonus we also got a ``paver shell`` task that imports everything
in our application module to a bpython_ console and creates an instance of
our application as `app` bound to a fake request which means we get access
to an environment and our persistent objects:

>>> app
<greeter.Greeter object at ...>
>>> app.local
<greeter.Environment object at ...>
>>> app.local.db
   DEBUG: Greeter: connecting ZODB
<greeter.Root object at ...>
>>> app.local.db.greeting
'Hello'  # or whatever we set it to in the web interface


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


Full Stack Configuration
------------------------

.. automodule:: ramverk.fullstack


.. centered:: Components

.. glossary::

  Application
    Implements the application logic and configuration. Usually one
    instance per process.

  Environment
    Each request creates an Environment instance wrapping the application
    and the WSGI environment. These objects are stacked on a context-local
    stack so that they can be retreived safely from threads and greenlets.
    This object is the place for application request logic.

  Request
    This object wraps only the WSGI environment and expose a more
    high-level interface to it. It is similar in many ways to the
    Environment object but usually not application-bound and usually not
    implementing any logic, only representing the incoming HTTP request as
    data. The request object lives on the environment object.

  Response
    High-level interface for composing the application response to an HTTP
    request. Not usually created automatically by the framework. Instances
    are callable as WSGI applications which is the only interface the
    framework expects, meaning any WSGI application can be used as a
    response.

  Template Context
    Namespace that templates render in, in addition to the keyword
    arguments passed to the renderer. Instances are passed the environment
    object.


.. autoclass:: Application
  :show-inheritance:

  .. inheritance-diagram:: Application
    :parts: 1

  .. attribute:: settings.secret_key

    :default:
      :class:`~ramverk.session.SecretKey` based on the `name` setting.

  .. attribute:: settings.storage

    :default: File storage based on the `name` setting.

  .. autoattribute:: log_handler

  .. autoattribute:: environment

    :default: :class:`Environment`

  .. autoattribute:: request

    :default: :class:`Request`

  .. autoattribute:: response

    :default: :class:`Response`

  .. autoattribute:: template_context

    :default: :class:`TemplateContext`


.. autoclass:: Environment
  :members:
  :show-inheritance:

  .. inheritance-diagram:: Environment
    :parts: 1


.. autoclass:: Request
  :members:
  :show-inheritance:

  .. inheritance-diagram:: Request
    :parts: 1


.. autoclass:: Response
  :members:
  :show-inheritance:

  .. inheritance-diagram:: Response
    :parts: 1


.. autoclass:: TemplateContext
  :members:
  :show-inheritance:

  .. inheritance-diagram:: TemplateContext
    :parts: 1


Minimal Configuration
---------------------

.. automodule:: ramverk.application


.. autoclass:: BaseApplication
  :show-inheritance:

  :param settings:
    Keyword arguments can be passed to the constructor and are added to
    :attr:`settings`.

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

  .. autoattribute:: environment

    :default: :class:`~ramverk.environment.BaseEnvironment`

  .. autoattribute:: request

    :default: :class:`~werkzeug.wrappers.BaseRequest`

  .. autoattribute:: response

    :default: :class:`~werkzeug.wrappers.BaseResponse`

  .. autoattribute:: stack

  .. automethod:: contextbound(environ)

  .. automethod:: __call__(environ, start_response)


.. automodule:: ramverk.environment
  :members:
  :show-inheritance:


Context-Local Environment Stack
"""""""""""""""""""""""""""""""

.. automodule:: ramverk.local

  A context-local object is a container that associates data with the
  identity of the thread or greenlet of the calling context. The implication
  of this is that global state can be imitated in a thread- and greenlet-safe
  manner. Even so, it is usually not a good idea to rely on context-local
  objects as it can complicate code and make it less explicit, but in certain
  cases like internationalization it can be impractical to avoid them.

  .. attribute:: stack

    A :class:`~werkzeug.local.LocalStack` that applications share by
    default.

  .. autofunction:: get_current

    Raises an :exc:`UnboundContextError` if called in a context not bound
    to a request environment.

  .. attribute:: current

    :class:`Proxy` to the current context-local. Operations like accessing
    attributes are forwarded to the current object and return proper,
    non-proxy results but be aware that if you pass something the proxy
    itself, then that's what the receiver will get: a proxy, forwarding to
    whatever is the current object of *their* context and which might
    change at any time. To get the actual current object of your context,
    use :func:`get_current`.

    Forwarding operations raise :exc:`UnboundContextError` if there is no
    environment to forward to.

  .. autoclass:: Proxy

  .. autoexception:: UnboundContextError


Dispatching Requests by URL
---------------------------

.. automodule:: ramverk.routing


Mixins
""""""

.. autoclass:: URLMapMixin

  .. autoattribute:: url_rule_class

    :default: :class:`~werkzeug.routing.Rule`

  .. autoattribute:: url_map

  .. automethod:: update_endpoint_values

  .. automethod:: dispatch_to_endpoint

    :param ramverk.environment.BaseEnvironment environment:
      Environment object wrapping the request to dispatch from.
    :param endpoint:
      A function, method or class that should produce a response for the
      request `environment`.

    For functions and methods, the default implementation will inspect
    the call signature and map keyword arguments to attributes on the
    `environment`. For classes it creates an instance, passing along the
    environment, and then calls the instance.

    To simplify unit testing `kwargs` should be included as overrides
    when dispatching to an endpoint with keyword arguments, i.e. the case
    with functions and methods in the default implementation.

.. autoclass:: URLMapAdapterMixin
  :members:

.. autoclass:: URLHelpersMixin
  :members:


Decorators
""""""""""

.. automodule:: ramverk.venusian

  .. autoclass:: VenusianMixin

    The decorators attach callbacks but do not otherwise alter the
    decorated function/class in any way. Applications can later scan for
    these callbacks in modules and packages and call them with a reference
    to itself and any optional parameters, thereby allowing the callbacks
    to register the decorated function/class with the application in the
    manner they see fit.

    .. automethod:: scan

      If `package` is a string it is treated as a :term:`dotted name` that
      gets imported, and if it is :const:`None` the application
      :attr:`~ramverk.application.BaseApplication.module` is scanned. The
      `parameters` set attributes on the scanner that is passed to the
      callbacks and can be used to configure the behavior of decorators for
      individual scans. In addition the `application` attribute is set to
      the application running the scan.

  .. autofunction:: decorator

    For reference consider the canonical example from the Venusian
    documentation::

      def jsonify(wrapped):
          def callback(scanner, name, ob):
              def jsonified(request):
                  result = wrapped(request)
                  return json.dumps(result)
              scanner.registry.add(name, jsonified)
          venusian.attach(wrapped, callback)
          return wrapped

    Using the :func:`decorator` decorator we can simplify it a little::

      @decorator
      def jsonify(scanner, name, ob):
          def jsonified(request):
              result = ob(request)
              return json.dumps(result)
          scanner.registry.add(name, jsonified)

  .. autofunction:: configurator

    Example:

    .. centered:: :file:`pkg/conf.py`

    ::

      @configurator
      def configure(application, submount):
          application.scan('pkg.frontend', submount=submount)
          application.scan('pkg.pages', submount=submount + '/pages')

    .. centered:: :file:`app.py`

    ::

      class App(Application):

          def configure(self):
              self.scan('pkg.conf', submount='/pkg')


.. currentmodule:: ramverk.routing

.. autofunction:: router

  These scan parameters are recognized:

  :param str submount:
    The rules are wrapped in a :class:`~werkzeug.routing.Submount` rule
    factory created with this string, effectively prepending the string to
    each rule.
  :param str subdomain:
    Like `submount` but for the :class:`~werkzeug.routing.Subdomain`
    factory.
  :param rulefactory:
    Wrap the rules in an arbitrary rule factory. Should be a callable that
    accept the list of rules as a single argument, or a tuple that is used
    to create a :func:`~functools.partial`.

  The rules are also wrapped in an
  :class:`~werkzeug.routing.EndpointPrefix` factory for the name of the
  module the router is located in plus a colon.

  Here's a non-trivial example::

    @router
    def urls(rule):
        yield rule('/show', endpoint='message')

    def localized_message(response):
        return response('Howdy')

    class App(Application):

        def configure(self):
            self.scan(submount='/<locale>',
                      rulefactory=(EndpointPrefix, 'localized_'))

  The scan in this example adds a rule that looks something like this::

    Submount('/<locale>', [
        EndpointPrefix(__name__ + ':', [
            EndpointPrefix('localized_', [
                Rule('/show', endpoint='message')
            ])
        ])
    ])

  In more simple terms it is essentially this rule::

    Rule('/<locale>/show', endpoint='name.of.module:localized_message')

.. autofunction:: route(string, defaults=None, subdomain=None, methods=None)

  The recognized scan parameters are the same as that of :func:`router` as
  is the use of the module name to prefix endpoints. Variants for the
  different HTTP methods are also available:

  .. autofunction:: connect(string, defaults=None, subdomain=None)

  .. autofunction:: delete(string, defaults=None, subdomain=None)

  .. autofunction:: get(string, defaults=None, subdomain=None)

  .. autofunction:: head(string, defaults=None, subdomain=None)

  .. autofunction:: options(string, defaults=None, subdomain=None)

  .. autofunction:: patch(string, defaults=None, subdomain=None)

  .. autofunction:: post(string, defaults=None, subdomain=None)

  .. autofunction:: put(string, defaults=None, subdomain=None)

  .. autofunction:: trace(string, defaults=None, subdomain=None)

  Example::

    @get('/')
    def index(response):
        return response('Howdy')


Endpoint Classes
""""""""""""""""

.. autoclass:: AbstractEndpoint
  :members: __rule_options__, environment, __call__

.. autoclass:: MethodDispatch

  If no corresponding method exists a
  :exc:`~werkzeug.exceptions.MethodNotAllowed` is raised with a list of
  valid methods. If routed with the :func:`route` decorator the resulting
  rule will by default only match HTTP methods implemented in the class.

  The methods are called with :meth:`~URLMapMixin.dispatch_to_endpoint`
  meaning they behave like endpoint functions by default.

  .. method:: connect

    Respond to a CONNECT request.

  .. method:: delete

    Respond to a DELETE request.

  .. method:: get

    Respond to a GET request.

  .. method:: head

    Respond to a HEAD request.

  .. method:: options

    Respond to an OPTIONS request.

  .. method:: patch

    Respond to a PATCH request.

  .. method:: post

    Respond to a POST request.

  .. method:: put

    Respond to a PUT request.

  .. method:: trace

    Respond to a TRACE request.

  Example::

    @route('/')
    class Index(MethodDispatch):

        renderer = 'index.html'

        def configure(self):
            self.greeting = self.environment.db.greeting

        def get(self, render):
            return render(self.renderer, greeting=self.greeting)


Rendering Content
-----------------

.. automodule:: ramverk.wrappers

  .. autoclass:: DeferredResponseInitMixin
    :members:

.. automodule:: ramverk.rendering

  .. autoclass:: RenderingMixinBase
    :members:

  .. autoclass:: RenderingEnvironmentMixin
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

.. autoclass:: ramverk.rendering.BaseTemplateContext
  :members:


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

  .. autoclass:: EnvironmentCompilerMixin


Styling with SCSS
-----------------

.. automodule:: ramverk.scss

  .. autoclass:: SCSSMixin
    :show-inheritance:

    Compiles Sassy stylesheets in :file:`{source}.scss` files into
    :file:`{compiled}.css` responses.


Tracking the Session of a User
------------------------------

.. automodule:: ramverk.session

  .. autoclass:: SessionMixin
    :members:

    .. attribute:: settings.secret_key

      A secret key to sign the session cookie with.

  .. autoclass:: SecureJSONCookie

  .. autoclass:: SecretKey


Persisting Objects with ZODB
----------------------------

.. automodule:: ramverk.zodb

  .. autoclass:: ZODBStorageMixin

    .. attribute:: settings.storage

        Must be set to a callable returning a ZODB storage object.

  .. autoclass:: ZODBConnectionMixin
    :show-inheritance:
    :members:


.. automodule:: ramverk.transaction

  .. autoclass:: TransactionMixin
    :members:

    .. important::

      Should be mixed in before anything that relies on transactions, such
      as :class:`~ramverk.zodb.ZODBConnectionMixin`.

  .. autoclass:: TransactionalMixinBase
    :members:


Logging with Logbook
--------------------

.. automodule:: ramverk.logbook

  .. autoclass:: LogbookLoggerMixin
    :members:

  .. autoclass:: LogbookHandlerMixin

    .. important::

      Should be mixed in at the top of the inheritance chain of the
      environment so that all log records during requests pass through
      :attr:`~LogbookLoggerMixin.log_handler`.


Task Management with Paver
--------------------------

.. automodule:: ramverk.paver

  .. attribute:: options.app

    Set this to your application class or an application instance,
    optionally as a :term:`dotted name`.

  .. attribute:: options.settings

    Settings to use when creating application instances. Values are
    converted with :func:`~ast.literal_eval` where possible, as Paver
    doesn't process options coming from the command-line in any way and
    simply stores them as strings. This conversion means you can override
    settings directly on the command-line with literal Python types such as
    booleans and numbers, for example:

    .. code-block:: console

      $ paver settings.debug=False serve

  .. attribute:: options.settings.debug

    :default: :const:`True`

  Example :file:`pavement.py`::

    from paver.easy    import options
    from ramverk.paver import *

    options.app = 'my.own:Application'

  .. autofunction:: serve()

    .. attribute:: options.serve.hostname

      Host to listen on.

      :default: ``localhost``

    .. attribute:: options.serve.port

      Port number to listen on.

      :default: ``8008``

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

  .. autofunction:: routes()

    .. code-block:: console

      $ paver routes
      ---> ramverk.paver.routes

        /static/<path:name>
          -> static

        /compiled/<path:name>
          -> compiled

        [HEAD|GET] /
          -> greeter:greet_visitor

        [POST] /
          -> greeter:set_greeting


WSGI Middlewares
----------------

.. automodule:: ramverk.wsgi

  .. autoclass:: SharedDataMixin
    :members: __create__, shared_data

  .. autofunction:: mixin

    Example::

      from werkzeug._internal import _easteregg

      class App(mixin(_easteregg), BaseApplication):
          pass

  .. autofunction:: middleware

    Example::

      from werkzeug._internal import _easteregg

      @middleware
      class EasterEggMixin(object):

          def pipeline(self, app):
              return _easteregg(app)

      class App(EasterEggMixin, BaseApplication):
          pass


Common Utilities
----------------

.. automodule:: ramverk.utils

  .. autoclass:: Configurable
    :members: __create__, configure

    This class exists primarily to avoid repeating documentation for the
    same pattern, and is mostly abstract in itself.

  .. autofunction:: super

  .. autoclass:: Bunch
    :show-inheritance:

  .. autoclass:: Alias

    :param path:
      Path to the delegated attribute from "self", as a dotted string or a
      list of strings.
    :param doc:
      ReST markup for a link to the delegated attribute.

    Example::

      class DelegatingObject(object):

          message = 'Howdy'

          yell = Alias('message.upper', ':meth:`~str.upper`')

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
    :show-inheritance:

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
