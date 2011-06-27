from werkzeug.utils import cached_property
from ramverk.utils  import delegated_property


class BaseEnvironment(object):
    """Environment base class."""

    def __init__(self, application, environ):

        self.application = application
        """Application that received the request of this environment."""

        self.environ = environ
        """WSGI environment."""

    def __enter__(self):
        self.application.local_stack.push(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.application.local_stack.pop()

    @cached_property
    def request(self):
        """A :attr:`~ramverk.application.BaseApplication.request` wrapping
        this :attr:`environ`."""
        return self.application.request(self.environ)

    response = delegated_property(
        'application.response',
        ':attr:`~ramverk.application.BaseApplication.response`')
