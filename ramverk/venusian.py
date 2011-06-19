from __future__     import absolute_import
from venusian       import Scanner
from werkzeug.utils import import_string


class VenusianMixin(object):
    """Adds support for scanning for deferred decorators using Venusian."""

    def scan(self, package=None, categories=('ramverk',), **scanner_args):
        """Scan `package` (or otherwise the
        :attr:`~ramverk.application.BaseApplication.module`) for objects
        with venusian callbacks attached."""
        scanner = Scanner(app=self, **scanner_args)
        if package is None:
            package = self.module
        if isinstance(package, basestring):
            package = import_string(package)
        scanner.scan(package, categories)
