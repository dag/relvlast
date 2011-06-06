from __future__          import absolute_import

from ZODB.FileStorage    import FileStorage
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import Response
from logbook             import NestedSetup, NullHandler, StderrHandler
from logbook.more        import ColorizedStderrHandler

from ramverk.application import AbstractApplication
from ramverk.genshi      import GenshiMixin
from ramverk.logbook     import LogbookMixin
from ramverk.routing     import RoutingMixin
from ramverk.transaction import TransactionMixin
from ramverk.zodb        import ZODBMixin


class HTMLResponse(Response):
    """Full-fledged response object with a HTML mimetype default."""

    default_mimetype = 'text/html'


class Application(LogbookMixin,
                  TransactionMixin,
                  ZODBMixin,
                  GenshiMixin,
                  RoutingMixin,
                  AbstractApplication):
    """Full-stack application."""

    response = HTMLResponse

    @cached_property
    def settings(self):
        settings = super(Application, self).settings
        settings.storage = lambda: FileStorage(self.name.lower() + '.db')
        return settings

    @cached_property
    def log_handler(self):
        """A :class:`~logbook.more.ColorizedStderrHandler` if the `debug`
        setting is true, otherwise only logging warnings and above in plain
        text to stderr."""
        if self.settings.debug:
            return ColorizedStderrHandler()
        return NestedSetup([NullHandler(),
                            StderrHandler(level='WARNING')])
