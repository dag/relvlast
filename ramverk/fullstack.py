from __future__          import absolute_import

from werkzeug.utils      import cached_property
from werkzeug.wrappers   import Response
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


class Application(TransactionMixin,
                  ZODBMixin,
                  GenshiMixin,
                  RoutingMixin,
                  LogbookMixin,
                  AbstractApplication):
    """Full-stack application."""

    response = HTMLResponse

    @cached_property
    def log_handler(self):
        return ColorizedStderrHandler()
