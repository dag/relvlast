from abc                 import ABCMeta, abstractmethod

from werkzeug.exceptions import HTTPException
from werkzeug.local      import Local, release_local
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import Request, Response
from werkzeug.wsgi       import responder

from ramverk.logbook     import LogbookMixin
from ramverk.routing     import RoutingMixin
from ramverk.utils       import request_property


class HTMLResponse(Response):
    """Full-fledged response object with a HTML mimetype default."""

    default_mimetype = 'text/html'


class AbstractApplication(object):
    """Abstract base for applications."""

    __metaclass__ = ABCMeta

    #: Enable development niceties that shouldn't be enabled in production
    #: deployments.
    debug = False

    #: Factory for default response objects.
    response = HTMLResponse

    def __init__(self, **overrides):
        """Create a new application object, overriding attributes with
        `overrides`."""
        self.self = self
        for key, value in overrides.iteritems():
            setattr(self, key, value)
        self.setup()

    def setup(self):
        """Called when a new application has been created, easier to
        override cleanly than :meth:`__init__`."""

    @cached_property
    def local(self):
        """Per-request container object."""
        return Local()

    @request_property
    def request(self):
        """Representative object for the currently processed request."""
        return Request(self.local.environ)

    @abstractmethod
    def respond(self):
        """Called to return a response, or raise an HTTPException, after the
        request environment has been bound to the context :attr:`local`."""

    def error_response(self, error):
        """Called to create a response for an
        :exc:`~werkzeug.exceptions.HTTPException` if one was raised during
        dispatch. Returns it as-is by default as they are basic responses.
        Override for custom 404 pages etc."""
        return error

    def __enter__(self):
        """Called after :attr:`local` has been bound to a request and
        before :meth:`dispatch` is called."""

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called after :meth:`dispatch`; arguments are `None` unless an
        exception was raised from the dispatch. Should return `True` to
        suppress that exception."""

    @responder
    def __call__(self, environ, start_response):
        """WSGI interface to this application. Clears :attr:`local` and
        adds the `environ` to it before dispatching."""
        release_local(self.local)
        self.local.environ = environ
        with self:
            try:
                response = self.respond()
            except HTTPException as e:
                response = self.error_response(e)
        return response


class Application(RoutingMixin, LogbookMixin, AbstractApplication):
    """Application with URL dispatching and a log channel."""
