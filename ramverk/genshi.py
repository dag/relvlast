from __future__        import absolute_import
from genshi.core       import Stream
from genshi.filters    import Transformer
from genshi.input      import HTML, ET
from genshi.template   import TemplateLoader, loader
from genshi.template   import MarkupTemplate, NewTextTemplate
from werkzeug.utils    import cached_property
from ramverk.rendering import TemplatingMixinBase

try:
    from compactxml import expand_to_string
except ImportError:
    pass


class CompactTemplate(MarkupTemplate):
    """A :class:`~genshi.template.markup.MarkupTemplate` parsing with
    :term:`Compact XML` using preconfigured namespace prefixes."""

    namespaces = dict(
        py='http://genshi.edgewall.org/',
        xi='http://www.w3.org/2001/XInclude')
    """Mapping of namespace prefixes to namespace URIs to be included in
    templates, by default including `py` and `xi`."""

    pretty_print = True
    """Whether the rendered markup should be pretty-printed with
    whitespace."""

    def __init__(self, source, filepath=None, filename=None, loader=None,
                 encoding=None, lookup='strict', allow_exec=True):
        if hasattr(source, 'render'):
            source = source.render()
        source = expand_to_string(source, self.namespaces,
                                  prettyPrint=self.pretty_print)
        super(CompactTemplate, self).__init__(source,
            filepath=filepath, filename=filename, loader=loader,
            encoding=encoding, lookup=lookup, allow_exec=allow_exec)


namespace_filter = (Transformer('//html')
    .attr('xmlns:py', 'http://genshi.edgewall.org/')
    .attr('xmlns:xi', 'http://www.w3.org/2001/XInclude')
    .attr('xmlns:i18n', 'http://genshi.edgewall.org/i18n')
    .attr('xmlns:form', 'http://ns.discorporate.us/flatland/genshi'))


class HTMLTemplate(MarkupTemplate):
    """A :class:`~genshi.template.markup.MarkupTemplate` parsing with
    :class:`~genshi.input.HTMLParser` and injecting the common namespace
    prefixes `py`, `xi`, `i18n` and `form` (for flatland)."""

    def __init__(self, source, filepath=None, filename=None, loader=None,
                 encoding=None, lookup='strict', allow_exec=True):
        if hasattr(source, 'read'):
            source = source.read()
        elif hasattr(source, 'render'):
            source = source.render()
        stream = HTML(source) | namespace_filter
        source = stream.render()
        super(HTMLTemplate, self).__init__(source,
            filepath=filepath, filename=filename, loader=loader,
            encoding=encoding, lookup=lookup, allow_exec=allow_exec)


class GenshiRenderer(object):
    """Genshi renderer with fixed configuration."""

    serializer = None
    """The method to use when serializing the stream."""

    doctype = None
    """Set a doctype for rendered documents."""

    mimetype = None
    """Set a mimetype on the returned response object."""

    dialect = None
    """Template class if not :class:`CompactTemplate`."""

    lazy = False
    """Serialize lazily, can misbehave with databases."""

    def __init__(self, app, serializer=None, doctype=None,
                 mimetype=None, dialect=CompactTemplate, lazy=False):
        self.app, self.serializer, self.doctype = app, serializer, doctype
        self.mimetype, self.dialect, self.lazy = mimetype, dialect, lazy

    def __call__(self, template_name, **context):
        self.app.update_template_context(context)
        template = self.app.genshi_loader.load(template_name, cls=self.dialect)
        stream = template.generate(**context)
        serialize = stream.serialize if self.lazy else stream.render
        if self.doctype is None:
            rendering = serialize(self.serializer)
        else:
            rendering = serialize(self.serializer, doctype=self.doctype)
        return self.app.response(rendering, mimetype=self.mimetype)

    def __repr__(self): #pragma: no cover
        attrs = ('{0}={1!r}'.format(k, v)
                 for (k, v) in vars(self).iteritems()
                 if k != 'app' and v)
        return 'GenshiRenderer({0})'.format(', '.join(attrs))


class GenshiMixin(TemplatingMixinBase):
    """Add Genshi templating to an application."""

    @cached_property
    def renderers(self):
        R = GenshiRenderer
        renderers = super(GenshiMixin, self).renderers
        renderers.update({
            '.html' : R(self, 'html', 'html5',   'text/html'),
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
                              callback=self.configure_genshi_template)

    def configure_genshi_template(self, template):
        """Called when `template` is first loaded; override to do Babel and
        Flatland installation and such."""
