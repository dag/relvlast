from inspect             import getargspec
from werkzeug.routing    import Map, Rule
from werkzeug.utils      import cached_property

from ramverk.utils       import request_property


class RoutingMixin(object):
    """Add URL dispatching to an application."""

    def route(self, string, function, **kwargs):
        """Add a :class:`~werkzeug.routing.Rule` for `string` to the
        :attr:`url_map`, using the name of `function` as the endpoint and
        map that endpoint to the function. The remaining arguments are
        passed to the Rule."""
        endpoint = kwargs.pop('endpoint', function.__name__)
        self.url_map.add(Rule(string, endpoint=endpoint, **kwargs))
        self.endpoints[endpoint] = function

    @cached_property
    def url_map(self):
        """Map of URLs to :attr:`endpoints`."""
        return Map()

    @request_property
    def url_adapter(self):
        """Adapter for :attr:`url_map` bound to the current request."""
        return self.url_map.bind_to_environ(self.local.environ)

    def url(self, endpoint, **values):
        """Build a URL for a route to `endpoint` with `values`."""
        return self.url_adapter.build(endpoint, values, force_external=True)

    def path(self, endpoint, **values):
        """Like :meth:`url` but as an absolute path."""
        return self.url_adapter.build(endpoint, values)

    @cached_property
    def endpoints(self):
        """Mapping of endpoints to "view" functions."""
        return {}

    @property
    def route_values(self):
        return self.local.route_values

    def dispatch(self, endpoint, values):
        """Called to create a response for the `endpoint` and `values`.
        Looks up a function in :attr:`endpoints` and calls it with the
        application and `values` as keyword arguments, by default."""
        self.local.route_values = values
        view = self.endpoints[endpoint]
        wants = getargspec(view).args
        args = dict((name, getattr(self, name)) for name in wants)
        return view(**args)

    def respond(self):
        return self.url_adapter.dispatch(self.dispatch)
