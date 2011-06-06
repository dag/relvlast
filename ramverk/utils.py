from functools import update_wrapper


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


class Dict(dict):
    """A dict with mutable attributes so we can use
    :func:`~functools.update_wrapper` on it."""


class class_dict(object):
    """A class property for a :class:`dict` with unique copies for
    instances."""

    def __init__(self, method):
        self.method = method
        self.classes = {}

    # FIXME inherit mappings from bases
    def __get__(self, instance, owner):
        if instance is None:
            if owner not in self.classes:
                d = Dict(self.method(owner))
                update_wrapper(d, self.method)
                self.classes[owner] = d
            return self.classes[owner]
        name = self.method.__name__
        instance.__dict__[name] = dict(getattr(owner, name))
        return instance.__dict__[name]
