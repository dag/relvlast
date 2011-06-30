from __future__     import absolute_import
from werkzeug.local import LocalStack, LocalProxy


class Proxy(LocalProxy):
    """A :class:`~werkzeug.local.LocalProxy` that prepends the proxy type
    to the :func:`repr` to avoid confusion. Proxies do not fully behave
    like the object they proxy so it can be helpful to know if you're
    dealing with one."""

    def __repr__(self):
        actual = super(Proxy, self).__repr__()
        proxy = self.__class__.__name__
        return '@'.join([proxy, actual])


def get_current():
    """Fetch the current object local to the caller context, i.e. the tip
    of the :attr:`stack` and normally an instance of some
    :class:`~ramverk.environment.BaseEnvironment` subclass."""
    return stack.top


stack = LocalStack()
current = Proxy(get_current)
