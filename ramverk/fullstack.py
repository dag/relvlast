from __future__          import absolute_import

from ZODB.FileStorage    import FileStorage
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import Request, Response
from logbook             import NestedSetup, NullHandler, StderrHandler
from logbook.more        import ColorizedStderrHandler

from ramverk.application import BaseApplication
from ramverk.genshi      import GenshiMixin
from ramverk.logbook     import LogbookMixin
from ramverk.rendering   import JSONMixin
from ramverk.routing     import RoutingMixin
from ramverk.scss        import SCSSMixin
from ramverk.transaction import TransactionMixin
from ramverk.utils       import request_property
from ramverk.wrappers    import ResponseUsingMixin
from ramverk.wsgi        import SharedDataMiddlewareMixin
from ramverk.zodb        import ZODBMixin


class HTMLResponse(ResponseUsingMixin, Response):
    """Full-fledged response object with a HTML mimetype default."""

    default_mimetype = 'text/html'


class Application(LogbookMixin,
                  TransactionMixin,
                  ZODBMixin,
                  GenshiMixin,
                  JSONMixin,
                  SCSSMixin,
                  RoutingMixin,
                  SharedDataMiddlewareMixin,
                  BaseApplication):
    """Full-stack application."""

    response = HTMLResponse
    """Overloaded with a more capable :class:`HTMLResponse`."""

    @request_property
    def request(self):
        """Overloaded to use the more capable
        :class:`~werkzeug.wrappers.Request` class."""
        return Request(self.local.environ)

    @cached_property
    def settings(self):
        settings = super(Application, self).settings
        settings.storage = lambda: FileStorage(settings.name.lower() + '.db')
        return settings

    @cached_property
    def log_handler(self): #pragma: no cover
        """A :class:`~logbook.more.ColorizedStderrHandler` if the `debug`
        setting is true, otherwise only logging warnings and above in plain
        text to stderr."""
        if self.settings.debug:
            return ColorizedStderrHandler(
                format_string='{record.level_name:>8}: '
                              '{record.channel}: {record.message}')
        return NestedSetup([NullHandler(),
                            StderrHandler(level='WARNING')])
