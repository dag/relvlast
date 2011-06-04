from __future__         import absolute_import
from genshi.template    import TemplateLoader, loader, Context
from werkzeug.utils     import cached_property
from ramverk.templating import TemplatingMixin


class GenshiMixin(TemplatingMixin):
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
        return TemplateLoader([loader.package(self.module, 'templates')],
                              auto_reload=self.debug,
                              callback=self.template_loaded)

    def template_loaded(self, template):
        """Called when `template` is first loaded; override to do Babel and
        Flatland installation and such."""
        pass

    def render(self, template_name, **context):
        """Render `template_name` in `context` to a response."""
        context = self.create_template_context(context)

        # Need this to pass 'self' to generate()
        genshi_context = Context()
        genshi_context.update(context)

        template = self.__loader.load(template_name)
        stream = template.generate(genshi_context)
        rendering = stream.serialize(self.serializer, doctype=self.doctype)
        return self.response(rendering)
