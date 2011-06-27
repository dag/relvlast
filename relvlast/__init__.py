from __future__          import absolute_import
from pkg_resources       import resource_filename

from relvlast.babel      import patch
patch()

from babel               import Locale
from babel.support       import Translations
from creoleparser        import Parser, creole11_base
from flatland.out.genshi import setup as setup_flatland
from genshi.filters      import Translator
from werkzeug.local      import LocalProxy
from werkzeug.routing    import Rule
from werkzeug.utils      import cached_property
from ramverk             import fullstack
from ramverk.utils       import Alias
from relvlast.objects    import Root


class Environment(fullstack.Environment):

    @cached_property
    def locale(self):
        return Locale(self.segments.get('locale', 'jbo'))

    @cached_property
    def db(self):
        return self.persistent.setdefault('root', Root())

    @cached_property
    def translations(self):
        return self.db.translations[self.locale.language]

    @cached_property
    def message_catalog(self):
        dirname = resource_filename(self.application.module, 'translations')
        return Translations.load(dirname, [self.locale])

    @cached_property
    def creole_parser(self):
        return Parser(creole11_base(
            wiki_links_base_url=self.path(':index')))


class TemplateContext(fullstack.TemplateContext):

    creole = Alias('environment.creole_parser.generate')

    locale = Alias('environment.locale')

    _ = Alias('environment.message_catalog.gettext')

    def locale_name(self, locale):
        return self.locale.languages.get(locale, Locale(locale).display_name)


class Relvlast(fullstack.Application):

    environment = Environment

    template_context = TemplateContext

    def configure(self):
        self.url_map.add(Rule('/', redirect_to='jbo'))
        self.scan('relvlast.frontend', submount='/<locale>')
        self.scan('relvlast.dictionary', submount='/<locale>/vlaste')

    def configure_genshi_template(self, template):
        setup_flatland(template)
        catalog = LocalProxy(lambda: self.local.message_catalog)
        Translator(catalog).setup(template)

    def update_endpoint_values(self, endpoint, values):
        if self.url_map.is_endpoint_expecting(endpoint, 'locale'):
            values.setdefault('locale', self.local.locale.language)
