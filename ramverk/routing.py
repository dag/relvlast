from __future__          import absolute_import
from functools           import partial
from inspect             import isclass, ismethod, getargspec

from venusian            import attach
from werkzeug.exceptions import NotFound
from werkzeug.routing    import Map, Rule, Submount, Subdomain, EndpointPrefix
from werkzeug.utils      import cached_property, redirect, import_string

from ramverk.utils       import Bunch, Alias


def _add_rules(scanner, rules, ob):
    if hasattr(scanner, 'rulefactory'):
        if isinstance(scanner.rulefactory, tuple):
            scanner.rulefactory = partial(*scanner.rulefactory)
        rules = [scanner.rulefactory(rules)]
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


class URLMapAdapterMixin(object):
    """Environment mixin that binds the application
    :attr:`~URLMapMixin.url_map` for the request in a
    :class:`~werkzeug.routing.MapAdapter` and dispatches to the matching
    endpoint if there was one."""

    def respond(self):
        try:
            endpoint = self.endpoint
        except NotFound:
            return super(URLMapAdapterMixin, self).respond()
        return self.application.dispatch_to_endpoint(import_string(endpoint))

    @cached_property
    def url_map_adapter(self):
        """A :class:`~werkzeug.routing.MapAdapter` for the
        :attr:`~URLMapMixin.url_map` bound to the request environment."""
        return self.application.url_map.bind_to_environ(self.environ)

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
            return self.application.module + endpoint
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
            self.application.update_endpoint_values(endpoint, values)
        return self.url_map_adapter.build(endpoint, values, method,
                                          force_external, append_unknown)

    def url(self, endpoint=None, **values):
        """Build a URL for the route that matches `endpoint` (expanded with
        :meth:`absolute_endpoint`) and `values` (updated with
        :meth:`~URLMapMixin.update_endpoint_values`). If the endpoint is
        :const:`None`, the current URL is returned with the values used as
        overrides."""
        return self.build_url(endpoint, values, force_external=True)

    def path(self, endpoint=None, **values):
        """Like :meth:`url` but as an absolute path."""
        return self.build_url(endpoint, values)

    def redirect(self, endpoint=None, **values):
        """Create a response that redirects to the route for `endpoint`
        with `values`."""
        return redirect(self.path(endpoint, **values))


class URLHelpersMixin(object):
    """Template context mixin with helpers for URL building."""

    url = Alias('environment.url',
                ':meth:`~URLMapAdapterEnvironmentMixin.url`')

    path = Alias('environment.path',
                 ':meth:`~URLMapAdapterEnvironmentMixin.path`')


class URLMapMixin(object):
    """Application mixin for dispatching to endpoints by matching the
    requested URL against a map of rules."""

    @cached_property
    def url_map(self):
        """An empty :class:`~werkzeug.routing.Map` that you can add rules
        to or replace with your own map of rules."""
        return Map()

    def update_endpoint_values(self, endpoint, values):
        """This method is called when a URL for `endpoint` is being built
        using `values` to fill in the placeholder variables of the URL
        rule. By overriding this you can modify the `values` mapping
        in-place to set defaults so you don't have to specify them manually
        every time. This is particularly useful in combination with
        :meth:`~werkzeug.routing.Map.is_endpoint_expecting` for example if
        you have a placeholder for a language code in the rule."""

    def dispatch_to_endpoint(self, endpoint, **kwargs):
        """Implements the logic for dispatching a request to an endpoint.
        Applications can override this to customize how endpoints are
        called. To simplify unit testing `kwargs` should be included in the
        keyword arguments as overrides for those keywords. The default
        implementation inspects the call signature of the endpoint, mapping
        the keyword arguments to attributes on the :class:`environment
        <ramverk.environment.BaseEnvironment>`."""
        if isclass(endpoint):
            wants = getargspec(endpoint.__init__).args[1:]
            initargs = dict(kwargs, **dict((name, getattr(self.local, name))
                                           for name in wants
                                           if name not in kwargs))
            endpoint = endpoint(**initargs).__call__
        wants = getargspec(endpoint).args
        if ismethod(endpoint):
            wants = wants[1:]
        kwargs.update((name, getattr(self.local, name))
                      for name in wants
                      if name not in kwargs)
        return endpoint(**kwargs)


class MethodDispatch(object):
    """Dispatch a class-based endpoint by HTTP method."""

    def __call__(self, request, application):
        method = getattr(self, request.method.lower())
        return application.dispatch_to_endpoint(method)
