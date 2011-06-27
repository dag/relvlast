try:
    import simplejson as json
except ImportError: #pragma: no cover
    import json

from werkzeug.utils import cached_property
from ramverk.utils  import Bunch, Alias


class RenderingMixinBase(object):
    """Base class for renderer mixins."""

    @cached_property
    def renderers(self):
        """Mapping of renderer names to rendering callables. A name is
        either a plain string like ``'json'`` or starts with a dot to
        represent a file extension, e.g. ``'.html'``."""
        return {}

    def render(self, renderer_name, **context):
        """Look up a renderer and call it with the name and context. The
        name is cut at the first dot such that ``'index.html'`` gets the
        ``'.html'`` renderer."""
        if '.' in renderer_name:
            renderer = renderer_name[renderer_name.index('.'):]
        else:
            renderer = renderer_name
        renderer = self.renderers[renderer]
        return renderer(renderer_name, **context)


class RenderingEnvironmentMixin(object):

    render = Alias('application.render',
                   ':meth:`~RenderingMixinBase.render`')


class BaseTemplateContext(object):
    """Base class for template contexts."""

    def __init__(self, environment):

        self.environment = environment
        """The context-bound environment
        :attr:`~ramverk.application.BaseApplication.local`."""

    application = Alias('environment.application',
        ':attr:`~ramverk.environment.BaseEnvironment.application`')

    request = Alias('environment.request',
        ':attr:`~ramverk.environment.BaseEnvironment.request`')


class TemplatingMixinBase(RenderingMixinBase):
    """Base class for templating mixins."""

    template_context = BaseTemplateContext
    """Template context class."""

    def update_template_context(self, context):
        namespace = self.template_context(self.local)
        for name in dir(namespace):
            if not name.startswith('_'):
                context.setdefault(name, getattr(namespace, name))

    @cached_property
    def template_loaders(self):
        """A :class:`~ramverk.utils.Bunch` of template engines mapping to
        lists of loaders."""
        return Bunch()


class JSONMixin(RenderingMixinBase):
    """Add a ``'json'`` renderer to an application."""

    @cached_property
    def renderers(self):
        renderers = super(JSONMixin, self).renderers
        renderers['json'] = self.__render
        return renderers

    def __default(self, obj):
        """Called to return a serializable representation (that is, using
        types that map cleanly to JSON equivalents) of `obj`, or raise
        :exc:`TypeError` (the default)."""
        raise TypeError

    def __render(self, _, **kwargs):
        serialized = json.dumps(kwargs, default=self.__default,
                                indent=4 if self.settings.debug else None)
        return self.response(serialized, mimetype='application/json')
