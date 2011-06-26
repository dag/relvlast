from __future__          import absolute_import
from inspect             import isclass, ismethod, getargspec

from venusian            import attach
from werkzeug.exceptions import NotFound
from werkzeug.routing    import Map, Rule, Submount, Subdomain, EndpointPrefix
from werkzeug.utils      import cached_property, redirect, import_string

from ramverk.utils       import Bunch


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


class URLMapAdapterRequestMixin(object):
    """Request mixin for binding the request to the application's
    :attr:`~URLMapMixin.url_map`."""

    @cached_property
    def url_map_adapter(self):
        """A :class:`~werkzeug.routing.MapAdapter` for the
        :attr:`~URLMapMixin.url_map` bound to the request environment."""
        return self.app.url_map.bind_to_environ(self.environ)

    @cached_property
    def url_map_adapter_match(self):
        return self.url_map_adapter.match(return_rule=True)

    @cached_property
    def url_rule(self):
        """The :class:`~werkzeug.routing.Rule` that matched this
        request."""
        return self.url_map_adapter_match[0]

    @cached_property
    def endpoint(self):
        """The :term:`endpoint name` for the matched :attr:`url_rule`."""
        return self.url_rule.endpoint

    @cached_property
    def segments(self):
        """The converted values that matched the placeholders in the
        :attr:`url_rule` as a :class:`~ramverk.utils.Bunch`."""
        return Bunch(self.url_map_adapter_match[1])

    def absolute_endpoint(self, endpoint):
        """Expand the relative `endpoint` description to a fully qualified
        endpoint name. Given an application in ``myapp`` and a current
        endpoint of ``myapp.frontend:index``, ``:about`` resolves to
        ``myapp.frontend:about`` and ``.backend:index`` to
        ``myapp.backend:index``."""
        if endpoint.startswith('.'):
            return self.app.module + endpoint
        if endpoint.startswith(':') and ':' in self.endpoint:
            module = self.endpoint.split(':', 1)[0]
            return module + endpoint
        return endpoint

    def build_url(self, endpoint=None, values=None, method=None,
                  force_external=False, append_unknown=True):
        if endpoint is None:
            endpoint = self.endpoint
            values = dict(self.segments, **values)
        else:
            endpoint = self.absolute_endpoint(endpoint)
            self.app.update_endpoint_values(endpoint, values)
        return self.url_map_adapter.build(endpoint, values, method,
                                          force_external, append_unknown)

    def url_for(self, endpoint=None, **values):
        """Build a URL for the route that matches `endpoint` (expanded with
        :meth:`absolute_endpoint`) and `values` (updated with
        :meth:`~URLMapMixin.update_endpoint_values`). If the endpoint is
        :const:`None`, the current URL is returned with the values used as
        overrides."""
        return self.build_url(endpoint, values, force_external=True)

    def path_to(self, endpoint=None, **values):
        """Like :meth:`url_for` but as an absolute path."""
        return self.build_url(endpoint, values)

    def redirect_to(self, endpoint=None, **values):
        """Create a response that redirects to the route for `endpoint`
        with `values`."""
        return redirect(self.path_to(endpoint, **values))


class URLMapMixin(object):
    """Application mixin dispatching requests using a URL
    :class:`~werkzeug.routing.Map`."""

    @cached_property
    def url_map(self):
        """Map of URLs to :attr:`endpoints`."""
        return Map()

    def update_endpoint_values(self, endpoint, values):
        """Called to update `values` in-place when building a URL for
        `endpoint`. Useful in combination with
        :meth:`~werkzeug.routing.Map.is_endpoint_expecting` to set defaults
        allowing you to avoid extraneous repetition."""

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

    def respond(self):
        """Match the request to an endpoint and call it with
        :meth:`call_as_endpoint` to produce a response."""
        try:
            endpoint = self.request.endpoint
        except NotFound:
            return super(URLMapMixin, self).respond()
        return self.call_as_endpoint(import_string(endpoint))


class MethodDispatch(object):
    """Dispatch a class-based endpoint by HTTP method."""

    def __call__(self, request, call_as_endpoint):
        method = getattr(self, request.method.lower())
        return call_as_endpoint(method)
