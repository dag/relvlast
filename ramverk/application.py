from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import BaseRequest, BaseResponse
from werkzeug.wsgi       import responder

from ramverk.environment import BaseEnvironment
from ramverk.local       import stack
from ramverk.utils       import Bunch


class BaseApplication(object):
    """Base for applications."""

    environment = BaseEnvironment
    """Environment class."""

    request = BaseRequest
    """Request class."""

    response = BaseResponse
    """Response class."""

    def __init__(self, **settings):
        """Create a new application object using `settings`."""
        self.settings.update(settings)
        self.__create__()
        self.configure()

    def __create__(self):
        """Called after :meth:`__init__` and meant to be hooked by
        cooperative mixins who are expected to call :func:`super` as
        needed."""

    def configure(self):
        """Called after :meth:`__init__` and meant to be overloaded by
        applications who do not need to call :func:`super`, to configure
        new instances."""

    @cached_property
    def settings(self):
        """Environmental configuration in a
        :class:`~ramverk.utils.Bunch`."""
        return Bunch(debug=False, name=self.__class__.__name__)

    @property
    def module(self):
        """:term:`Dotted name` of the module or package the application
        belongs to."""
        return self.__module__

    @cached_property
    def log(self):
        """Log channel for this application."""
        from logging import getLogger
        return getLogger(self.settings.name)

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

    @responder
    def __call__(self, environ, start_response):
        """WSGI interface to this application."""
        with self.environment(self, environ):
            try:
                response = self.respond()
            except HTTPException as e:
                response = self.respond_for_error(e)
        return response
