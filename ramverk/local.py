from __future__     import absolute_import
from werkzeug.local import LocalStack, LocalProxy


class UnboundContextError(Exception):
    """Raised if :func:`get_current` or :attr:`current` is used when the
    :attr:`stack` is empty."""

    def __str__(self):
        return 'attempted to read context-local in unbound context'


class Proxy(LocalProxy):
    """A :class:`~werkzeug.local.LocalProxy` that prepends the proxy type
    to the :func:`repr` to avoid confusion. Proxies do not fully behave
    like the object they proxy so it can be helpful to know if you're
    dealing with one."""

    def __repr__(self):
        actual = super(Proxy, self).__repr__()
        proxy = self.__class__.__name__
        return '@'.join([proxy, actual])


def get_current(stack=None):
    """Fetch the current object local to the caller context, i.e. the tip
    of the :attr:`stack` and normally an instance of some
    :class:`~ramverk.environment.BaseEnvironment` subclass."""
    if stack is None:
        stack = globals()['stack']
    try:
        return stack._local.stack[-1]
    except (AttributeError, IndexError):
        raise UnboundContextError


stack = LocalStack()
current = Proxy(get_current)


from ramverk.inventory import members
__all__ = members[__name__]
