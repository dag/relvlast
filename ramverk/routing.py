from inspect             import getargspec

from venusian            import Scanner, attach
from werkzeug.exceptions import NotFound
from werkzeug.routing    import Map, Submount, Subdomain, EndpointPrefix
from werkzeug.utils      import cached_property, redirect, import_string

from ramverk.utils       import Bunch, request_property


def router(generator):
    """Decorate a callable as a router, i.e. returns an iterable of rules
    and rule factories."""
    def route(scanner, name, ob):
        rules = ob()
        if scanner.submount is not None:
            rules = [Submount(scanner.submount, rules)]
        if scanner.endpoint_prefix is not None:
            rules = [EndpointPrefix(scanner.endpoint_prefix, rules)]
        if scanner.subdomain is not None:
            rules = [Subdomain(scanner.subdomain, rules)]
        for rule in rules:
            scanner.app.route(rule)
    attach(generator, route, category='ramverk.routing')
    return generator


def endpoint(view):
    """Decorate a callable as a view for the endpoint with the same
    name."""
    def register_endpoint(scanner, name, ob):
        if scanner.endpoint_prefix is not None:
            name = scanner.endpoint_prefix + name
        scanner.app.endpoints[name] = ob
    attach(view, register_endpoint, category='ramverk.routing')
    return view


class RoutingScannerMixin(object):
    """Add support for scanning for :func:`router` and :func:`endpoint`
    functions to an application with URL dispatch."""

    def scan(self, package=None,
                   submount=None,
                   endpoint_prefix=None,
                   subdomain=None,
                   categories=('ramverk.routing',)):
        """Scan `package` (or otherwise the
        :attr:`~ramverk.application.BaseApplication.module`) for routers
        and endpoints."""
        scanner = Scanner(app=self,
                          submount=submount,
                          endpoint_prefix=endpoint_prefix,
                          subdomain=subdomain)
        if package is None:
            package = self.module
        if isinstance(package, basestring):
            package = import_string(package)
        scanner.scan(package, categories)


class RoutingHelpersMixin(object):
    """Add some convenient helpers for applications with URL dispatch."""

    @property
    def segments(self):
        """The values that matched the route in the :attr:`url_map` as a
        :class:`~ramverk.utils.Bunch`."""
        return Bunch(self.local.endpoint_args)

    @cached_property
    def app(self): #pragma: no cover
        """Reference to itself, to allow views to access the
        application."""
        return self

    def url(self, endpoint, **values):
        """Build a URL for a route to `endpoint` with `values`."""
        return self.url_adapter.build(endpoint, values, force_external=True)

    def path(self, endpoint, **values):
        """Like :meth:`url` but as an absolute path."""
        return self.url_adapter.build(endpoint, values)

    def redirect(self, endpoint, **values):
        """Create a response that redirects to the route for `endpoint`
        with `values`."""
        return redirect(self.path(endpoint, **values))


class URLMapMixin(object):
    """Add URL dispatch using a :class:`~werkzeug.routing.Map` to an
    application."""

    @cached_property
    def url_map(self):
        """Map of URLs to :attr:`endpoints`."""
        return Map()

    def route(self, rulefactory):
        """Add a :class:`~werkzeug.routing.Rule` or rule factory to
        :attr:`url_map`."""
        self.url_map.add(rulefactory)

    @request_property
    def url_adapter(self):
        """Adapter for :attr:`url_map` bound to the current request."""
        return self.url_map.bind_to_environ(self.local.environ)

    @cached_property
    def endpoints(self):
        """Mapping of endpoints to views."""
        return {}

    def call_view(self, view, **kwargs):
        """Call the `view` callable with `kwargs` using view semantics: the
        default is to fetch missing arguments in the view's signature, from
        the attributes of the application."""
        wants = getargspec(view).args
        kwargs.update((name, getattr(self, name))
                      for name in wants
                      if name not in kwargs)
        return view(**kwargs)

    def respond(self):
        """Match the environment to an endpoint and then :meth:`call_view`
        the corresponding view."""
        try:
            endpoint, args = self.url_adapter.match()
        except NotFound:
            return super(URLMapMixin, self).respond()
        self.local.endpoint = endpoint
        self.local.endpoint_args = args
        view = self.endpoints[endpoint]
        return self.call_view(view)


class RoutingMixin(RoutingScannerMixin,
                   RoutingHelpersMixin,
                   URLMapMixin):
    """Add complete URL dispatching to an application."""
