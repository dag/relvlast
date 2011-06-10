from __future__        import absolute_import
from genshi.template   import TemplateLoader, loader, NewTextTemplate
from werkzeug.utils    import cached_property
from ramverk.rendering import TemplatingMixin


class GenshiMixin(TemplatingMixin):
    """Add Genshi templating to an application. Requires a
    :attr:`~ramverk.application.BaseApplication.response` implementing
    :class:`~ramverk.wrappers.ResponseUsingMixin`."""

    @cached_property
    def renderers(self):
        renderers = super(GenshiMixin, self).renderers
        renderers['.html'] = self.genshi_renderer(serializer='html',
                                                  doctype='html5')
        renderers['.txt'] = self.genshi_renderer(serializer='text',
                                                 mimetype='text/plain',
                                                 cls=NewTextTemplate)
        return renderers

    @cached_property
    def __loader(self):
        """A :func:`~genshi.template.loader.package`
        :class:`~genshi.template.loader.TemplateLoader` for the
        ``templates/`` directory under the module of the application."""
        return TemplateLoader([loader.package(self.module, 'templates')],
                              auto_reload=self.settings.debug,
                              callback=self.template_loaded)

    def template_loaded(self, template):
        """Called when `template` is first loaded; override to do Babel and
        Flatland installation and such."""

    def genshi_renderer(self,
                        serializer=None,
                        doctype=None,
                        mimetype=None,
                        cls=None,
                        lazy=False):
        """Create a Genshi renderer."""
        def renderer(template_name, **context):
            self.update_template_context(context)
            template = self.__loader.load(template_name, cls=cls)
            stream = template.generate(**context)
            serialize = stream.serialize if lazy else stream.render
            if doctype is None:
                rendering = serialize(serializer)
            else:
                rendering = serialize(serializer, doctype=doctype)
            return self.response(rendering).using(mimetype=mimetype)
        return renderer
