try:
    import simplejson as json
except ImportError:
    import json

from werkzeug.utils import cached_property


class RenderingMixin(object):
    """Generic mixins for adding support for "renderers" to an
    application."""

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


class TemplatingMixin(RenderingMixin):
    """Add common functionality for templating to an application."""

    def update_template_context(self, context):
        """Create a context mapping to render a template
        in, including `overrides`. Override to add globals. Includes
        `request`, `url` and `path` from the application, and the
        application as `app`, by default."""
        context.setdefault('app', self)
        context.setdefault('request', self.request)
        context.setdefault('url', self.url)
        context.setdefault('path', self.path)
        return context


class JSONRenderingMixin(RenderingMixin):
    """Add a `json` renderer to an application."""

    @cached_property
    def renderers(self):
        renderers = super(JSONRenderingMixin, self).renderers
        renderers['json'] = self.__render
        return renderers

    def __default(self, obj):
        raise TypeError

    def __render(self, _, **kwargs):
        return self.response(json.dumps(kwargs, default=self.__default))\
                   .using(mimetype='application/json')
