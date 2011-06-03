from __future__      import absolute_import
from genshi.template import TemplateLoader, loader, Context
from werkzeug.utils  import cached_property


class GenshiMixin(object):
    """Add Genshi templating to an
    :class:`~ramverk.application.Application`."""

    #: Serializer used by :meth:`render`.
    serializer = 'html'

    #: Doctype used by :meth:`render`.
    doctype = 'html5'

    @cached_property
    def __loader(self):
        """Loads templates from ``templates/`` under the module of the
        application. (Note: name-mangled!)"""
        return TemplateLoader([loader.package(self.__module__, 'templates')],
                              auto_reload=self.debug,
                              callback=self.template_loaded)

    def template_loaded(self, template):
        """Called when `template` is first loaded; override to do Babel and
        Flatland installation and such."""
        pass

    def context(self, overrides):
        """Create a :class:`~genshi.template.Context` to render a template
        in, including `overrides`. Override to add globals. Includes
        `request`, `url` and `path` from the application, and the
        application as `self`, by default."""
        context = Context(request=self.request,
                          url=self.url,
                          path=self.path)
        context['self'] = self
        context.update(overrides)
        return context

    def render(self, template_name, **context):
        """Render `template_name` in `context` to a response."""
        template = self.__loader.load(template_name)
        stream = template.generate(self.context(context))
        rendering = stream.serialize(self.serializer, doctype=self.doctype)
        return self.response(rendering)
