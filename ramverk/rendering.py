try:
    import simplejson as json
except ImportError: #pragma: no cover
    import json

from werkzeug.utils import cached_property


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


class TemplatingMixinBase(RenderingMixinBase):
    """Base class for templating mixins."""

    def update_template_context(self, context):
        """Add templating "globals" to `context`. Override to add your own
        globals.  Includes `request`, `url` and `path` from the
        application, and the application as `app`, by default."""
        context.setdefault('app', self)
        context.setdefault('request', self.request)
        context.setdefault('url', self.url)
        context.setdefault('path', self.path)
        return context


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
        return self.response(json.dumps(kwargs, default=self.__default))\
                   .using(mimetype='application/json')
