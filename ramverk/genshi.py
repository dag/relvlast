from __future__        import absolute_import
from genshi.template   import TemplateLoader, loader, NewTextTemplate
from werkzeug.utils    import cached_property
from ramverk.rendering import TemplatingMixinBase


class GenshiRenderer(object):
    """Genshi renderer with fixed configuration."""

    serializer = None
    """The method to use when serializing the stream."""

    doctype = None
    """Set a doctype for rendered documents."""

    mimetype = None
    """Set a mimetype on the returned response object."""

    class_ = None
    """Template class if not
    :class:`~genshi.template.markup.MarkupTemplate`."""

    lazy = False
    """Serialize lazily, can misbehave with databases."""

    def __init__(self, app, serializer=None, doctype=None,
                 mimetype=None, class_=None, lazy=False):
        self.app, self.serializer, self.doctype = app, serializer, doctype
        self.mimetype, self.class_, self.lazy = mimetype, class_, lazy

    def __call__(self, template_name, **context):
        self.app.update_template_context(context)
        template = self.app.genshi_loader.load(template_name, cls=self.class_)
        stream = template.generate(**context)
        serialize = stream.serialize if self.lazy else stream.render
        if self.doctype is None:
            rendering = serialize(self.serializer)
        else:
            rendering = serialize(self.serializer, doctype=self.doctype)
        return self.app.response(rendering).using(mimetype=self.mimetype)

    def __repr__(self): #pragma: no cover
        attrs = ('{0}={1!r}'.format(k, v)
                 for (k, v) in vars(self).iteritems()
                 if k != 'app' and v)
        return 'GenshiRenderer({0})'.format(', '.join(attrs))


class GenshiMixin(TemplatingMixinBase):
    """Add Genshi templating to an application. Requires a
    :attr:`~ramverk.application.BaseApplication.response` implementing
    :class:`~ramverk.wrappers.ResponseUsingMixin`."""

    @cached_property
    def renderers(self):
        R = GenshiRenderer
        renderers = super(GenshiMixin, self).renderers
        renderers.update({
            '.html' : R(self, 'html', 'html5'),
            '.xhtml': R(self, 'xml',  'xhtml11', 'application/xhtml+xml'),
            '.atom' : R(self, 'xml',   None,     'application/atom+xml'),
            '.svg'  : R(self, 'xml',  'svg',     'image/svg+xml'),
            '.xml'  : R(self, 'xml',   None,     'application/xml'),
            '.txt'  : R(self, 'text',  None,     'text/plain', NewTextTemplate)
        })
        return renderers

    @cached_property
    def template_loaders(self):
        """Adds a :func:`~genshi.template.loader.package` loader for the
        :file:`{application module}/templates` directory."""
        loaders = super(GenshiMixin, self).template_loaders
        loaders.genshi = [loader.package(self.module, 'templates')]
        return loaders

    @cached_property
    def genshi_loader(self):
        """The ``template_loaders.genshi`` loaders wrapped in a
        :class:`~genshi.template.loader.TemplateLoader`."""
        return TemplateLoader(self.template_loaders.genshi,
                              auto_reload=self.settings.debug,
                              callback=self.template_loaded)

    def template_loaded(self, template):
        """Called when `template` is first loaded; override to do Babel and
        Flatland installation and such."""
