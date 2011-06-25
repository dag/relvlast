from __future__          import absolute_import
from inspect             import isclass, ismethod, getargspec

from venusian            import attach
from werkzeug.exceptions import NotFound
from werkzeug.routing    import Map, Rule, Submount, Subdomain, EndpointPrefix
from werkzeug.utils      import cached_property, redirect, import_string

from ramverk.utils       import Bunch, request_property


def _add_rules(scanner, rules, ob):
    rules = [EndpointPrefix(ob.__module__ + ':', rules)]
    if hasattr(scanner, 'submount'):
        rules = [Submount(scanner.submount, rules)]
    if hasattr(scanner, 'subdomain'):
        rules = [Subdomain(scanner.subdomain, rules)]
    for rule in rules:
        scanner.app.url_map.add(rule)


def router(generator):
    """Decorator for use with :class:`~ramverk.venusian.VenusianMixin` for
    callables that return an iterable of routing rules."""
    def route(scanner, name, ob):
        _add_rules(scanner, ob(), ob)
    attach(generator, route, category='ramverk')
    return generator


def route(*args, **kwargs):
    """Venusian decorator for routing a single URL rule."""
    def decorator(endpoint):
        def route_endpoint(scanner, name, ob):
            kwargs.setdefault('endpoint', name)
            rule = Rule(*args, **kwargs)
            _add_rules(scanner, [rule], ob)
        attach(endpoint, route_endpoint, category='ramverk')
        return endpoint
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
        """Expand the relative `endpoint` description to a fully qualified
        endpoint name. Given an application in ``myapp`` and a current
        endpoint of ``myapp.frontend:index``, ``:about`` resolves to
        ``myapp.frontend:about`` and ``.backend:index`` to
        ``myapp.backend:index``."""
        if endpoint.startswith('.'):
            return self.module + endpoint
        if endpoint.startswith(':') and ':' in self.local.endpoint:
            module = self.local.endpoint.split(':', 1)[0]
            return module + endpoint
        return endpoint

    def update_endpoint_values(self, endpoint, values):
        """Called to update `values` in-place when building a URL for
        `endpoint`. Useful in combination with
        :meth:`~werkzeug.routing.Map.is_endpoint_expecting` to set defaults
        allowing you to avoid extraneous repetition."""

    def __build_url(self, endpoint=None,
                    values=None, method=None,
                    force_external=False, append_unknown=True):
        if endpoint is None:
            endpoint = self.local.endpoint
            values = dict(self.segments, **values)
        else:
            endpoint = self.absolute_endpoint(endpoint)
            self.update_endpoint_values(endpoint, values)
        return self.url_adapter.build(endpoint, values, method,
                                      force_external, append_unknown)

    def url(self, endpoint=None, **values):
        """Build a URL for the route that matches `endpoint` (expanded with
        :meth:`absolute_endpoint`) and `values` (updated with
        :meth:`update_endpoint_values`). If the endpoint is :const:`None`,
        the current URL is returned with the values used as overrides."""
        return self.__build_url(endpoint, values, force_external=True)

    def path(self, endpoint=None, **values):
        """Like :meth:`url` but as an absolute path."""
        return self.__build_url(endpoint, values)

    def redirect(self, endpoint=None, **values):
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

    def call_as_endpoint(self, callable, **kwargs):
        """Call the `callable` with `kwargs` using endpoint semantics: the
        default is to fetch missing arguments in the callable's signature, from
        the attributes of the application."""
        if isclass(callable):
            wants = getargspec(callable.__init__).args[1:]
            initargs = dict(kwargs, **dict((name, getattr(self, name))
                                           for name in wants
                                           if name not in kwargs))
            callable = callable(**initargs).__call__
        wants = getargspec(callable).args
        if ismethod(callable):
            wants = wants[1:]
        kwargs.update((name, getattr(self, name))
                      for name in wants
                      if name not in kwargs)
        return callable(**kwargs)

    def match_request_to_endpoint(self):
        endpoint, args = self.url_adapter.match()
        self.local.endpoint = endpoint
        self.local.endpoint_args = args
        return endpoint, args

    def respond(self):
        """Match the request to an endpoint and call it with
        :meth:`call_as_endpoint` to produce a response."""
        try:
            endpoint, args = self.match_request_to_endpoint()
        except NotFound:
            return super(URLMapMixin, self).respond()
        return self.call_as_endpoint(import_string(endpoint))


class RoutingMixin(RoutingHelpersMixin, URLMapMixin):
    """Add complete URL dispatching to an application."""


class MethodDispatch(object):
    """Dispatch a class-based endpoint by HTTP method."""

    def __call__(self, request, call_as_endpoint):
        method = getattr(self, request.method.lower())
        return call_as_endpoint(method)
