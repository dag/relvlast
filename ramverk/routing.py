from __future__          import absolute_import
from inspect             import getargspec

from venusian            import attach
from werkzeug.exceptions import NotFound
from werkzeug.routing    import Map, Rule, Submount, Subdomain, EndpointPrefix
from werkzeug.utils      import cached_property, redirect, import_string

from ramverk.utils       import Bunch, request_property


def _endpoint_name(function):
    return ':'.join((function.__module__, function.__name__))


def _add_rules(scanner, rules, ob):
    rules = [EndpointPrefix(ob.__module__ + ':', rules)]
    if hasattr(scanner, 'submount'):
        rules = [Submount(scanner.submount, rules)]
    if hasattr(scanner, 'subdomain'):
        rules = [Subdomain(scanner.subdomain, rules)]
    for rule in rules:
        scanner.app.url_map.add(rule)


def router(generator):
    """Decorate a callable as a router, i.e. returns an iterable of rules
    and rule factories."""
    def route(scanner, name, ob):
        _add_rules(scanner, ob(), ob)
    attach(generator, route, category='ramverk')
    return generator


def route(*args, **kwargs):
    """Route a single rule to the decorated endpoint view."""
    def decorator(view):
        def route_endpoint(scanner, name, ob):
            kwargs.setdefault('endpoint', name)
            rule = Rule(*args, **kwargs)
            _add_rules(scanner, [rule], ob)
        attach(view, route_endpoint, category='ramverk')
        return view
    return decorator


def get(*args, **kwargs):
    """Like :func:`route` with method defaulting to GET."""
    kwargs.setdefault('methods', ('GET',))
    return route(*args, **kwargs)


def post(*args, **kwargs):
    """Like :func:`route` with method defaulting to POST."""
    kwargs.setdefault('methods', ('POST',))
    return route(*args, **kwargs)


def put(*args, **kwargs):
    """Like :func:`route` with method defaulting to PUT."""
    kwargs.setdefault('methods', ('PUT',))
    return route(*args, **kwargs)


def delete(*args, **kwargs):
    """Like :func:`route` with method defaulting to DELETE."""
    kwargs.setdefault('methods', ('DELETE',))
    return route(*args, **kwargs)


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

    def absolute_endpoint(self, endpoint):
        if endpoint.startswith('.'):
            return self.module + endpoint
        if endpoint.startswith(':') and ':' in self.local.endpoint:
            module = self.local.endpoint.split(':', 1)[0]
            return module + endpoint
        return endpoint

    def url(self, endpoint, **values):
        """Build a URL for a route to `endpoint` with `values`."""
        endpoint = self.absolute_endpoint(endpoint)
        return self.url_adapter.build(endpoint, values, force_external=True)

    def path(self, endpoint, **values):
        """Like :meth:`url` but as an absolute path."""
        endpoint = self.absolute_endpoint(endpoint)
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

    @request_property
    def url_adapter(self):
        """Adapter for :attr:`url_map` bound to the current request."""
        return self.url_map.bind_to_environ(self.local.environ)

    def call_view(self, view, **kwargs):
        """Call the `view` callable with `kwargs` using view semantics: the
        default is to fetch missing arguments in the view's signature, from
        the attributes of the application."""
        wants = getargspec(view).args
        kwargs.update((name, getattr(self, name))
                      for name in wants
                      if name not in kwargs)
        return view(**kwargs)

    def match_request_to_endpoint(self):
        endpoint, args = self.url_adapter.match()
        self.local.endpoint = endpoint
        self.local.endpoint_args = args
        return endpoint, args

    def respond(self):
        """Match the environment to an endpoint and then :meth:`call_view`
        the corresponding view."""
        try:
            endpoint, args = self.match_request_to_endpoint()
        except NotFound:
            return super(URLMapMixin, self).respond()
        view = import_string(endpoint)
        return self.call_view(view)


class RoutingMixin(RoutingHelpersMixin, URLMapMixin):
    """Add complete URL dispatching to an application."""
