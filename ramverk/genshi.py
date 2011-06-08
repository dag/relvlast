from __future__        import absolute_import
from genshi.template   import TemplateLoader, loader
from werkzeug.utils    import cached_property
from ramverk.rendering import TemplatingMixin


class GenshiMixin(TemplatingMixin):
    """Add Genshi templating to an application."""

    @cached_property
    def renderers(self):
        renderers = super(GenshiMixin, self).renderers
        renderers['.html'] = self.__create_renderer(serializer='html',
                                                    doctype='html5')
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
        pass

    def __create_renderer(self, serializer=None,
                                doctype=None,
                                cls=None,
                                mimetype=None):
        def renderer(template_name, **context):
            context = self.create_template_context(context)
            template = self.__loader.load(template_name, cls=cls)
            stream = template.generate(**context)
            if doctype is None:
                rendering = stream.render(serializer)
            else:
                rendering = stream.render(serializer, doctype=doctype)
            return self.response(rendering).using(mimetype=mimetype)
        return renderer
