from werkzeug.exceptions import NotFound
from werkzeug.utils      import cached_property
from ramverk.utils       import delegated_property


class BaseEnvironment(object):
    """Environment base class."""

    def __init__(self, application, environ):

        self.application = application
        """Application that received the request of this environment."""

        self.environ = environ
        """WSGI environment."""

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def respond(self):
        """Respond to this request or raise an HTTP exception. Default
        raises a :exc:`~werkzeug.exceptions.NotFound`."""
        raise NotFound

    def respond_for_error(self, error):
        """If :meth:`respond` raised an HTTP exception, this is called with
        the exception and should return an error response. The default
        returns the exception which is a basic response."""
        return error

    @cached_property
    def request(self):
        """A :attr:`~ramverk.application.BaseApplication.request` wrapping
        this :attr:`environ`."""
        return self.application.request(self.environ)

    response = delegated_property(
        'application.response',
        ':attr:`~ramverk.application.BaseApplication.response`')
