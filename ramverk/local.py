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
    of the :attr:`stack` and normally an instance of some subclass of
    :class:`~ramverk.environment.BaseEnvironment`."""
    return stack.top


stack = LocalStack()
"""A :class:`~werkzeug.local.LocalStack` that applications share by
default."""


current = Proxy(get_current)
""":class:`Proxy` to the current context-local. Operations like accessing
attributes are forwarded to the current object and return proper, non-proxy
results but be aware that if you pass something the proxy itself, then
that's what the receiver will get: a proxy, forwarding to whatever is the
current object of *their* context and which might change at any time. To
get the actual current object of your context, use :func:`get_current`."""
