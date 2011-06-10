from __future__        import absolute_import
from genshi.template   import TemplateLoader, loader, NewTextTemplate
from werkzeug.utils    import cached_property
from ramverk.rendering import TemplatingMixin


class GenshiRenderer(object):
    """Genshi renderer with fixed configuration."""

    serializer = None
    """The method to use when serializing the stream."""

    doctype = None
    """Set a doctype for rendered documents."""

    mimetype = None
    """Set a mimetype on the returned response object."""

    cls = None
    """Template class if not
    :class:`~genshi.template.markup.MarkupTemplate`."""

    lazy = False
    """Serialize lazily, can misbehave with databases."""

    def __init__(self, app, serializer=None, doctype=None,
                 mimetype=None, cls=None, lazy=False):
        self.app, self.serializer, self.doctype = app, serializer, doctype
        self.mimetype, self.cls, self.lazy = mimetype, cls, lazy

    def __call__(self, template_name, **context):
        self.app.update_template_context(context)
        loader = self.app._GenshiMixin__loader
        template = loader.load(template_name, cls=self.cls)
        stream = template.generate(**context)
        serialize = stream.serialize if self.lazy else stream.render
        if self.doctype is None:
            rendering = serialize(self.serializer)
        else:
            rendering = serialize(self.serializer, doctype=self.doctype)
        return self.app.response(rendering).using(mimetype=self.mimetype)


class GenshiMixin(TemplatingMixin):
    """Add Genshi templating to an application. Requires a
    :attr:`~ramverk.application.BaseApplication.response` implementing
    :class:`~ramverk.wrappers.ResponseUsingMixin`."""

    @cached_property
    def renderers(self):
        renderers = super(GenshiMixin, self).renderers
        renderers['.html'] = GenshiRenderer(self, serializer='html',
                                                  doctype='html5')
        renderers['.txt']  = GenshiRenderer(self, serializer='text',
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
