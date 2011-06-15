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


class ForcePropertiesCalled(object):
    """Iterate over all attributes on instance creation, forcing properties
    to be called and cached properties to be initiated."""

    def __new__(cls, *args, **kwargs):
        self = super(ForcePropertiesCalled, cls).__new__(cls, *args, **kwargs)
        for name in dir(self):
            getattr(self, name)
        return self
