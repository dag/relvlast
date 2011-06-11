from werkzeug.routing import Rule
from werkzeug.utils   import cached_property
from werkzeug.wsgi    import SharedDataMiddleware, responder


def mixin_from_middleware(middleware):
    """Create a mixin from a middleware."""

    class MiddlewareMixin(object):

        @cached_property
        def _middlewares(self):
            return {}

        @responder
        def __call__(self, environ, start_response):
            app = super(MiddlewareMixin, self).__call__
            if middleware not in self._middlewares:
                self._middlewares[middleware] = middleware(app)
            return self._middlewares[middleware]

    MiddlewareMixin.__name__ =\
            'mixin_from_middleware({0})'.format(middleware.__name__)
    return MiddlewareMixin



def middleware_mixin(mixin):
    """Decorate a class as a middleware mixin. A special `pipeline` method
    is passed the WSGI application to wrap, and the pipeline is transformed
    into a cooperative :meth:`__call__` override."""
    pipeline = mixin.pipeline
    del mixin.pipeline

    @cached_property
    def _middlewares(self):
        return {}

    @responder
    def __call__(self, environ, start_response):
        app = super(mixin, self).__call__
        if mixin not in self._middlewares:
            self._middlewares[mixin] = pipeline(self, app)
        return self._middlewares[mixin]

    mixin._middlewares = _middlewares
    mixin.__call__ = __call__
    return mixin


@middleware_mixin
class SharedDataMiddlewareMixin(object):
    """Serve static files for an application."""

    def setup_mixins(self):
        """Configures a build-only endpoint called `static` if the
        application has a :meth:`~ramverk.routing.URLMapMixin.route`
        method."""
        super(SharedDataMiddlewareMixin, self).setup_mixins()
        if hasattr(self, 'route'):
            self.route(Rule('/static/<path:name>',
                       endpoint='static',
                       build_only=True))

    @cached_property
    def shared_data(self):
        """Mapping of public paths to files/directories or tuples of
        ``(module, directory)``. The default serves up the `static`
        directory under the application module on ``/static``. See
        :class:`~werkzeug.wsgi.SharedDataMiddleware` for more
        information."""
        return {'/static': (self.module, 'static')}

    def pipeline(self, app):
        return SharedDataMiddleware(app, self.shared_data)


@middleware_mixin
class EasterEggMiddlewareMixin(object): #pragma: no cover

    def pipeline(self, app):
        from werkzeug._internal import _easteregg
        return _easteregg(app)
