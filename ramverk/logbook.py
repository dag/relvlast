from __future__     import absolute_import
from logbook        import Logger
from werkzeug.utils import cached_property


class LogbookMixin(object):
    """Add a Logbook log channel to an application."""

    @cached_property
    def log(self):
        """Log channel for this application."""
        return Logger(self.__class__.__name__)
