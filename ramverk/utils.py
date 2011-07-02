import __builtin__ as builtins
from inspect import currentframe, getmro, isfunction, isclass, isroutine
from werkzeug.utils import cached_property


class Configurable(object):
    """Base for a common pattern for hooking instance creation cleanly."""

    def __create__(self):
        """Should be called by the "configurable" class after
        :meth:`__init__` to allow cooperative mixins and other base classes
        to configure the instance without needing to mess with
        :meth:`__init__` directly."""
        self.configure()

    def configure(self):
        """Called after :meth:`__create__` to allow the instance to
        configure itself without bothering with :func:`python:super`."""


class Omitted(object):

    class __metaclass__(type):

        def __repr__(cls):
            return cls.__name__


def super(type=Omitted, instance=Omitted):
    """Variant of :func:`python:super` that mimics the behavior in Python 3 with
    no arguments."""
    if type is Omitted:
        frame = currentframe(1)
        instance = frame.f_locals[frame.f_code.co_varnames[0]]
        for type in getmro(builtins.type(instance)):
            for var in vars(type).itervalues():
                if not isfunction(var):
                    continue
                if var.__code__ is frame.f_code:
                    break
            else:
                continue
            break
        else:
            raise SystemError('super(): no arguments')
    if instance is Omitted:
        return builtins.super(type)
    return builtins.super(type, instance)


class Bunch(dict):
    """Attribute-accessible :class:`dict`."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Alias(object):
    """Property that delegates to a distant attribute."""

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


class InitFromArgs(Configurable):
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


def args(*names):
    """Class decorator sugar for setting :attr:`__args__`."""
    def decorator(class_):
        class_.__args__ = names
        return class_
    return decorator


from ramverk.inventory import members
__all__ = members[__name__]
