from __future__          import absolute_import
from abc                 import ABCMeta, abstractmethod
from functools           import partial
from inspect             import isclass, ismethod, getargspec

from werkzeug.exceptions import NotFound, MethodNotAllowed
from werkzeug.routing    import Map, Rule, Submount, Subdomain, EndpointPrefix
from werkzeug.utils      import cached_property, redirect, import_string

from ramverk.http        import HTTP_METHODS
from ramverk.utils       import Bunch, Alias
from ramverk.venusian    import decorator


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
        scanner.application.url_map.add(rule)


@decorator
def router(scanner, name, ob):
    """Decorator for adding URL rules to an application by calling the
    router (passing the preferred :attr:`~URLMapMixin.url_rule_class`)
    which should return an iterable of rules. Typically a router is a
    generator or a function that return a list."""
    _add_rules(scanner, ob(scanner.application.url_rule_class), ob)


def route(string, **kwargs):
    """Decorator for adding a single URL rule using the arguments to the
    decorator and inferring the endpoint name from the decorated
    function/class."""
    @decorator
    def route_endpoint(scanner, name, ob):
        opts = getattr(ob, '__rule_options__', dict)()
        opts.update(kwargs)
        opts.setdefault('endpoint', name)
        rule = scanner.application.url_rule_class(string, **opts)
        _add_rules(scanner, [rule], ob)
    return route_endpoint


for method in HTTP_METHODS:
    name = method.lower()
    func = partial(route, methods=(method,))
    func.__name__ = name
    func.__doc__ = """
        Like ``@route(methods=[{0!r}])``.
    """.format(method)
    globals()[name] = func


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
        endpoint = import_string(endpoint)
        return self.application.dispatch_to_endpoint(endpoint, self)

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
        """The :attr:`~URLMapMixin.url_rule_class` instance that matched
        this request."""
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
                ':meth:`~URLMapAdapterMixin.url`')

    path = Alias('environment.path',
                 ':meth:`~URLMapAdapterMixin.path`')


class URLMapMixin(object):
    """Application mixin for dispatching to endpoints by matching the
    requested URL against a map of rules."""

    url_rule_class = Rule
    """The class used for URL rules."""

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

    def dispatch_to_endpoint(self, endpoint, environment, **kwargs):
        """Implements the logic for dispatching from an environment to an
        endpoint. Applications can override this to customize how
        endpoints are called."""
        if isclass(endpoint):
            return endpoint(environment)()
        args = getargspec(endpoint).args
        if ismethod(endpoint):
            del args[0]  # 'self'
        for name in args:
            if name not in kwargs:
                kwargs[name] = getattr(environment, name)
        return endpoint(**kwargs)


class AbstractEndpoint(object):
    """Optional base for endpoint classes that must implement
    :meth:`__call__`."""

    __metaclass__ = ABCMeta

    environment = None
    """The environment object for the current request."""

    @classmethod
    def __rule_options__(cls):
        """The :func:`route` family of decorators look for this attribute
        and call it if available, using the returned dict as the base for
        the keyword arguments that get passed to the URL rule being
        created."""
        return {}

    def __init__(self, environment):
        self.environment = environment
        self.__create__()
        self.configure()

    def __create__(self):
        """Called to let mixins configure instances."""

    def configure(self):
        """Called to let the endpoint instance configure itself."""

    @abstractmethod
    def __call__(self):
        """Abstract method that must be implemented to return a
        response."""


class MethodDispatch(AbstractEndpoint):
    """Base for endpoint classes that dispatches the request to the
    instance method whose name is the HTTP request method in lower case."""

    @classmethod
    def __rule_options__(cls):
        methods = [m for m in HTTP_METHODS if hasattr(cls, m.lower())]
        return dict(methods=methods)

    def __call__(self):
        request = self.environment.request
        application = self.environment.application
        method = getattr(self, request.method.lower(), None)
        if method is None:
            valid = [m for m in HTTP_METHODS if hasattr(self, m.lower())]
            raise MethodNotAllowed(valid)
        return application.dispatch_to_endpoint(method, self.environment)
