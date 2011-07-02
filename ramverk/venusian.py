from __future__     import absolute_import
from functools      import wraps
from venusian       import Scanner, attach
from werkzeug.utils import import_string, validate_arguments


class VenusianMixin(object):
    """Application mixin that uses :term:`Venusian` to provide support for
    building modular applications with simple decorators and plain Python
    modules."""

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


@decorator
def configurator(scanner, name, ob):
    """Generic decorator for configuring the scanning application. The
    decorated function is called with the scan parameters listed in the
    signature (which can include the implicit `application`)."""
    params = vars(scanner).copy()
    args, kwargs = validate_arguments(ob, (), params)
    ob(*args, **kwargs)


from ramverk.inventory import members
__all__ = members[__name__]
