from inspect             import getargspec
from werkzeug.exceptions import NotFound
from werkzeug.routing    import Map, Rule
from werkzeug.utils      import cached_property, redirect

from ramverk.utils       import request_property, class_dict


class RoutingMixin(object):
    """Add URL dispatching to an application."""

    @cached_property
    def app(self):
        """Reference to itself, to allow views to access the
        application."""
        return self

    def route(self, rulefactory):
        """Add a :class:`~werkzeug.routing.Rule` or rule factory to
        :attr:`url_map`."""
        self.url_map.add(rulefactory)

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

    def redirect(self, endpoint, **values):
        """Create a response that redirects to the route for `endpoint`
        with `values`."""
        return redirect(self.path(endpoint, **values))

    @class_dict
    def endpoints(cls):
        """A :class:`~ramverk.utils.class_dict` mapping endpoints to "view"
        functions that are passed as keyword arguments the application
        attributes listed in their signature, and should return responses
        or WSGI applications."""
        return {}

    @classmethod
    def endpoint(cls, function):
        """Register `function` in :attr:`endpoints` by function name."""
        cls.endpoints[function.__name__] = function
        return function

    @property
    def route_values(self):
        """The values that matched the route in the :attr:`url_map`."""
        return self.local.route_values

    def get_view(self, endpoint):
        """Get a view function for `endpoint`. Default behavior looks it up
        in :attr:`endpoints`."""
        return self.endpoints[endpoint]

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
        with :meth:`get_view`."""
        try:
            endpoint, values = self.url_adapter.match()
        except NotFound:
            return super(RoutingMixin, self).respond()
        self.local.endpoint = endpoint
        self.local.route_values = values
        view = self.get_view(endpoint)
        return self.call_view(view)
