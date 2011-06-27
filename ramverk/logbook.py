from __future__     import absolute_import
from logbook        import Logger, default_handler
from werkzeug.utils import cached_property


class LogbookHandlerMixin(object):
    """Environment mixin binding the request to the application's
    :attr:`~LogbookMixin.log_handler`."""

    def __enter__(self):
        self.application.log_handler.push_thread()
        return super(LogbookHandlerMixin, self).__enter__()

    def __exit__(self, *exc_info):
        value = super(LogbookHandlerMixin, self).__exit__(*exc_info)
        self.application.log_handler.pop_thread()
        return value


class LogbookLoggerMixin(object):
    """Application mixin dispatching log records with :term:`Logbook`."""

    @cached_property
    def log(self):
        """A Logbook logging channel for this application."""
        return Logger(self.settings.name)

    log_handler = default_handler
    """The Logbook handler used by the :class:`LogbookHandlerMixin`.
    The default is the Logbook default, which is an
    :class:`~logbook.handlers.StderrHandler`."""
