from werkzeug.wrappers   import Response

from ramverk.application import AbstractApplication
from ramverk.logbook     import LogbookMixin
from ramverk.routing     import RoutingMixin
from ramverk.genshi      import GenshiMixin
from ramverk.zodb        import TransactionMixin, ZODBMixin


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
