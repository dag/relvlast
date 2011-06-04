from logbook             import Logger

from werkzeug.exceptions import HTTPException
from werkzeug.local      import Local, release_local
from werkzeug.routing    import Map, Rule
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import Request, Response
from werkzeug.wsgi       import responder

from ramverk.utils       import request_property


class HTMLResponse(Response):
    """Full-fledged response object with a HTML mimetype default."""

    default_mimetype = 'text/html'


class Application(object):
    """Primary super-class for Ramverk applications."""

    #: Enable development niceties that shouldn't be enabled in production
    #: deployments.
    debug = False

    #: Factory for default response objects.
    response = HTMLResponse

    def __init__(self, **overrides):
        """Create a new application object, overriding attributes with
        `overrides`."""
        for key, value in overrides.iteritems():
            setattr(self, key, value)
        self.setup()

    def setup(self):
        """Called when a new application has been created, easier to
        override cleanly than :meth:`__init__`."""
        pass

    def route(self, string, function, **kwargs):
        """Add a :class:`~werkzeug.routing.Rule` for `string` to the
        :attr:`url_map`, using the name of `function` as the endpoint and
        map that endpoint to the function. The remaining arguments are
        passed to the Rule."""
        endpoint = kwargs.pop('endpoint', function.__name__)
        self.url_map.add(Rule(string, endpoint=endpoint, **kwargs))
        self.endpoints[endpoint] = function

    @cached_property
    def local(self):
        """Per-request container object."""
        return Local()

    @cached_property
    def log(self):
        """Log channel for this application."""
        return Logger(self.__class__.__name__)

    @request_property
    def request(self):
        """Representative object for the currently processed request."""
        return Request(self.local.environ)

    @cached_property
    def url_map(self):
        """Map of URLs to :attr:`endpoints`."""
        return Map()

    @request_property
    def url_adapter(self):
        """Adapter for :attr:`url_map` bound to the current request."""
        return self.url_map.bind_to_environ(self.local.environ)

    def url(self, endpoint, **values):
        """Build a URL for a route to `endpoint` with `values`."""
        return self.url_adapter.build(endpoint, values, force_external=True)

    def path(self, endpoint, **values):
        """Like :meth:`url` but as an absolute path."""
        return self.url_adapter.build(endpoint, values)

    def __enter__(self):
        """Called after :attr:`local` has been bound to a request and
        before :meth:`dispatch` is called."""
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called after :meth:`dispatch`; arguments are `None` unless an
        exception was raised from the dispatch. Should return `True` to
        suppress that exception."""
        pass

    @cached_property
    def endpoints(self):
        """Mapping of endpoints to "view" functions."""
        return {}

    def dispatch(self, endpoint, values):
        """Called to create a response for the `endpoint` and `values`.
        Looks up a function in :attr:`endpoints` and calls it with the
        application and `values` as keyword arguments, by default."""
        view = self.endpoints[endpoint]
        return view(self, **values)

    def error_response(self, error):
        """Called to create a response for an
        :exc:`~werkzeug.exceptions.HTTPException` if one was raised during
        dispatch. Returns it as-is by default as they are basic responses.
        Override for custom 404 pages etc."""
        return error

    @responder
    def __call__(self, environ, start_response):
        """WSGI interface to this application. Clears :attr:`local` and
        adds the `environ` to it before dispatching."""
        release_local(self.local)
        self.local.environ = environ
        with self:
            try:
                response = self.url_adapter.dispatch(self.dispatch)
            except HTTPException as e:
                response = self.error_response(e)
        return response
