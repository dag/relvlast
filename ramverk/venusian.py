from __future__     import absolute_import
from functools      import wraps
from venusian       import Scanner, attach
from werkzeug.utils import import_string


class VenusianMixin(object):
    """Application mixin that uses :term:`Venusian` to provide support for
    building modular applications with simple declarative decorators and
    plain old Python modules. The decorators attach callback functions
    but do not otherwise alter the decorated function/class in any way.
    Applications can later scan for these callbacks in modules and packages
    and call them with a reference to itself and any optional parameters,
    thereby allowing the callbacks to register the decorated function/class
    with the application in the manner they see fit."""

    def scan(self, package=None, categories=('ramverk',), **parameters):
        """Scan a module or (recursively) a package and configure the
        application using the callbacks attached to top-level objects."""
        scanner = Scanner(application=self, **parameters)
        if package is None:
            package = self.module
        if isinstance(package, basestring):
            package = import_string(package)
        scanner.scan(package, categories)


def decorator(callback):
    """A decorator for turning a Venusian callback into a decorator that
    attaches the callback."""
    @wraps(callback)
    def wrapper(target):
        attach(target, callback, category='ramverk')
        return target
    return wrapper
