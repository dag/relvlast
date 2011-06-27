from inspect import isclass, isroutine
from functools import update_wrapper
from werkzeug.utils import cached_property


class Bunch(dict):
    """Attribute-accessible :class:`dict`."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class request_property(object):
    """Like :class:`~werkzeug.utils.cached_property` but cached in the
    object's `local` attribute, which in applications are cleared for every
    request. Can be used to create lazily cached request-local
    properties."""

    def __init__(self, method):
        update_wrapper(self, method)
        self.method = method

    def __get__(self, instance, owner):
        if instance is None:
            return self
        name = self.method.__name__
        if not hasattr(instance.local, name):
            setattr(instance.local, name, self.method(instance))
        return getattr(instance.local, name)


class delegated_property(object):

    def __init__(self, path, doc=None):
        if isinstance(path, basestring):
            path = path.split('.')
        self.path = path
        if doc is None:
            doc = ':attr:`{0}`'.format('.'.join(path))
        self.__doc__ = 'Alias of {0}.'.format(doc)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return reduce(getattr, [instance] + self.path)


def has(**properties):
    """Class decorator sugar for adding simple cached properties. Keyword
    arguments name the properties and the values are factory callables for
    constructing new values."""
    def decorator(class_):
        for name, factory in properties.iteritems():
            def new(self, factory=factory):
                return factory()
            setattr(class_, name, cached_property(new, name))
        return class_
    return decorator


class EagerCachedProperties(object):
    """Visit all cached properties during instance allocation, forcing them
    to fix their value."""

    def __new__(cls, *args, **kwargs):
        self = super(EagerCachedProperties, cls).__new__(cls, *args, **kwargs)
        for name, value in vars(cls).iteritems():
            if isinstance(value, cached_property):
                getattr(self, name)
        return self


class ReprAttributes(object):
    """Add an informative :func:`repr` to an object, listing attributes and
    their values."""

    def __repr__(self):
        name = self.__class__.__name__
        ns = dict(vars(self.__class__), **vars(self))
        attrs = ', '.join('{0}={1!r}'.format(name, getattr(self, name))
                          for (name, value) in ns.iteritems()
                          if not name.startswith('_')
                          and not isroutine(value)
                          and not isclass(value))
        if not attrs:
            return '<{0}>'.format(name)
        return '<{0} {1}>'.format(name, attrs)


class InitFromArgs(object):
    """Add a convenience :meth:`__init__` based on :attr:`__args__` that
    accepts both positional and keyword arguments, setting unspecified args
    to none."""

    __args__ = ()

    def __init__(self, *args, **kwargs):
        for name in self.__args__:
            setattr(self, name, None)
        vars(self).update(zip(self.__args__, args))
        vars(self).update(kwargs)
        self.__create__()

    def __create__(self):
        """Called after :meth:`__init__` for cleaner overriding."""


def args(*names):
    """Class decorator sugar for setting :attr:`__args__`."""
    def decorator(class_):
        class_.__args__ = names
        return class_
    return decorator
