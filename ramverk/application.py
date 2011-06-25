from contextlib          import contextmanager

from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import BaseRequest, BaseResponse
from werkzeug.wsgi       import responder

from ramverk.local       import stack
from ramverk.utils       import Bunch, request_property


class BaseApplication(object):
    """Base for applications."""

    response = BaseResponse
    """Factory for response objects, defaulting to a minimal
    :class:`~werkzeug.wrappers.BaseResponse`."""

    def __init__(self, **settings):
        """Create a new application object using `settings`."""
        self.settings.update(settings)
        self.__create__()
        self.configure()

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

    def __create__(self):
        """Called after :meth:`__init__` and meant to be hooked by
        cooperative mixins who are expected to call :func:`super` as
        needed."""

    def configure(self):
        """Called after :meth:`__init__` and meant to be overloaded by
        applications who do not need to call :func:`super`, to configure
        new instances."""

    @cached_property
    def local_stack(self):
        """Stack of context-locals, by default the globally shared
        :attr:`~ramverk.local.stack`."""
        return stack

    @property
    def local(self):
        """Per-request container object, by default the top-most object on
        the :attr:`local_stack`."""
        return self.local_stack.top

    @request_property
    def request(self):
        """The currently processed request wrapped in a
        :class:`~werkzeug.wrappers.BaseRequest`."""
        return BaseRequest(self.local.environ)

    def respond(self):
        """Called to return a response, or raise an HTTPException, after the
        request environment has been bound to the context :attr:`local`.
        Default raises :exc:`~werkzeug.exceptions.NotFound`."""
        raise NotFound

    def respond_for_error(self, error):
        """Called to create a response for an
        :exc:`~werkzeug.exceptions.HTTPException` if one was raised during
        dispatch. Returns it as-is by default as they are basic responses.
        Override for custom 404 pages etc."""
        return error

    @contextmanager
    def request_context(self, environ):
        """Context manager in which :attr:`local` is bound to `environ`.
        Default is to push a :class:`~ramverk.utils.Bunch` containing the
        environment and application, on the :attr:`local_stack`."""
        local = Bunch(application=self, environ=environ)
        self.local_stack.push(local)
        try:
            yield local
        finally:
            self.local_stack.pop()

    def __enter__(self):
        """Called inside :meth:`request_context` before :meth:`respond`."""

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called after :meth:`respond` and :meth:`respond_for_error`;
        arguments are `None` unless an exception was raised from the
        dispatch. Should return `True` to suppress that exception."""

    @responder
    def __call__(self, environ, start_response):
        """WSGI interface to this application."""
        with self.request_context(environ):
            with self:
                try:
                    response = self.respond()
                except HTTPException as e:
                    response = self.respond_for_error(e)
        return response
