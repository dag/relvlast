from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.local      import Local, release_local
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import Request, BaseResponse
from werkzeug.wsgi       import responder

from ramverk.utils       import Bunch, request_property
from ramverk.wrappers    import ResponseUsingMixin


class Response(ResponseUsingMixin, BaseResponse):
    """A minimal response object."""


class BaseApplication(object):
    """Base for applications."""

    #: Factory for default response objects, by default a
    #: :class:`~ramverk.application.Response`.
    response = Response

    def __init__(self, **settings):
        """Create a new application object using `settings`."""
        self.settings.update(settings)
        self.setup()

    @cached_property
    def settings(self):
        """Environmental configuration in a
        :class:`~ramverk.utils.Bunch`."""
        return Bunch(debug=False, name=self.__class__.__name__)

    @property
    def module(self):
        """Name of the module containing the application, for locating
        templates and such. Defaults to ``__module__`` but needs to be set
        to a fixed value for subclasses of complete applications."""
        return self.__module__

    @cached_property
    def log(self):
        """Log channel for this application."""
        from logging import getLogger
        return getLogger(self.settings.name)

    def setup(self):
        """Called after :meth:`__init__` and meant to be overridden by
        applications to do post-init setup."""

    @cached_property
    def local(self):
        """Per-request container object."""
        return Local()

    @request_property
    def request(self):
        """Representative object for the currently processed request."""
        return Request(self.local.environ)

    def respond(self):
        """Called to return a response, or raise an HTTPException, after the
        request environment has been bound to the context :attr:`local`.
        Default raises :exc:`~werkzeug.exceptions.NotFound`."""
        raise NotFound

    def error_response(self, error):
        """Called to create a response for an
        :exc:`~werkzeug.exceptions.HTTPException` if one was raised during
        dispatch. Returns it as-is by default as they are basic responses.
        Override for custom 404 pages etc."""
        return error

    def __enter__(self):
        """Called after :meth:`bind_to_environ` and before :meth:`respond`."""

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called after :meth:`respond` and :meth:`error_response`;
        arguments are `None` unless an exception was raised from the
        dispatch. Should return `True` to suppress that exception."""

    def bind_to_environ(self, environ):
        """Called to bind the application to the WSGI `environ`."""
        release_local(self.local)
        self.local.environ = environ

    @responder
    def __call__(self, environ, start_response):
        """WSGI interface to this application."""
        self.bind_to_environ(environ)
        with self:
            try:
                response = self.respond()
            except HTTPException as e:
                response = self.error_response(e)
        return response
