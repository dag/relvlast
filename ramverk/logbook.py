from __future__     import absolute_import
from logbook        import Logger, StderrHandler
from werkzeug.utils import cached_property


class LogbookMixin(object):
    """Add a Logbook log channel to an application."""

    @cached_property
    def log(self):
        """Log channel for this application."""
        return Logger(self.name)

    @cached_property
    def log_handler(self):
        """Log handler bound to requests. Defaults to
        :class:`~logbook.StderrHandler`."""
        return StderrHandler()

    def __enter__(self):
        self.log_handler.push_thread()
        return super(LogbookMixin, self).__enter__()

    def __exit__(self, *exc_info):
        value = super(LogbookMixin, self).__exit__(*exc_info)
        self.log_handler.pop_thread()
        return value
