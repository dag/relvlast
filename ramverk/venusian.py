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

    def scan(self, package=None, categories=('ramverk',), **scanner_args):
        """Scan a module or (recursively) a package and configure the
        application according to the instructions embedded in top-level
        objects. If `package` is a string it is treated as a :term:`dotted
        name` that gets imported, and if it is :const:`None` the
        application :attr:`~ramverk.application.BaseApplication.module` is
        scanned. The `scanner_args` are passed down to and read by the
        decorators to allow parametric registration of the instructions."""
        scanner = Scanner(app=self, **scanner_args)
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
