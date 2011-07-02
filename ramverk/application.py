from contextlib          import contextmanager

from werkzeug.exceptions import HTTPException
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import BaseRequest, BaseResponse
from werkzeug.wsgi       import responder

from ramverk.environment import BaseEnvironment
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
    def stack(self):
        """Stack of environments, by default a globally shared
        :attr:`~ramverk.local.stack`."""
        from ramverk.local import stack
        return stack

    @contextmanager
    def contextbound(self, environ):
        """Context manager stacking the WSGI `environ` wrapped in
        :attr:`environment`."""
        env = self.environment(self, environ)
        self.stack.push(env)
        try:
            with env:
                yield env
        finally:
            self.stack.pop()

    def response_from_error(self, environment, error):
        return error

    @responder
    def __call__(self, environ, start_response):
        """WSGI interface to this application."""
        with self.contextbound(environ) as env:
            try:
                response = env()
            except HTTPException as error:
                response = self.response_from_error(env, error)
        return response
