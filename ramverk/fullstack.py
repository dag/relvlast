from __future__          import absolute_import

from ZODB.FileStorage    import FileStorage
from werkzeug.utils      import cached_property, get_content_type
from werkzeug.wrappers   import Response
from logbook             import NestedSetup, NullHandler, StderrHandler
from logbook.more        import ColorizedStderrHandler

from ramverk.application import BaseApplication
from ramverk.genshi      import GenshiMixin
from ramverk.logbook     import LogbookMixin
from ramverk.routing     import RoutingMixin
from ramverk.transaction import TransactionMixin
from ramverk.zodb        import ZODBMixin


class HTMLResponse(Response):
    """Full-fledged response object with a HTML mimetype default."""

    default_mimetype = 'text/html'

    def using(self, response=None,
                    status=None,
                    headers=None,
                    mimetype=None,
                    content_type=None,
                    direct_passthrough=None):
        """Convenience method that works like ``__init__`` on
        already-created instances. Useful with things that return response
        objects, for example ``return render(template).using(status=202)``."""

        if headers is not None:
            self.headers.extend(headers)

        if content_type is None:
            if mimetype is not None:
                mimetype = get_content_type(mimetype, self.charset)
            content_type = mimetype
        if content_type is not None:
            self.headers['Content-Type'] = content_type

        if status is not None:
            if isinstance(status, (int, long)):
                self.status_code = status
            else:
                self.status = status

        if direct_passthrough is not None:
            self.direct_passthrough = direct_passthrough

        if response is not None:
            if isinstance(response, basestring):
                self.data = response
            else:
                self.response = response

        return self


class Application(LogbookMixin,
                  TransactionMixin,
                  ZODBMixin,
                  GenshiMixin,
                  RoutingMixin,
                  BaseApplication):
    """Full-stack application."""

    response = HTMLResponse

    @cached_property
    def settings(self):
        settings = super(Application, self).settings
        settings.storage = lambda: FileStorage(settings.name.lower() + '.db')
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
