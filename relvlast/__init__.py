from __future__          import absolute_import

from relvlast.babel      import patch
patch()

from pkg_resources       import resource_filename
from flatland.out.genshi import setup as setup_flatland
from genshi.filters      import Translator
from creoleparser        import Parser, creole11_base
from werkzeug.local      import LocalProxy
from werkzeug.routing    import Rule
from babel               import Locale
from babel.support       import Translations
from ramverk.fullstack   import Application
from ramverk.utils       import request_property
from relvlast.objects    import Root


class Relvlast(Application):

    def setup(self):
        self.route(Rule('/', redirect_to='jbo'))
        self.scan('relvlast.frontend', '/<locale>')
        self.scan('relvlast.dictionary', '/<locale>/vlaste', 'dictionary:')

    @request_property
    def locale(self):
        return Locale(self.route_values.get('locale', 'jbo'))

    @request_property
    def db(self):
        return self.root_object.setdefault('root', Root())

    @property
    def translations(self):
        return self.db.translations[self.locale.language]

    def update_template_context(self, context):
        super(Relvlast, self).update_template_context(context)
        context.setdefault('creole', self.creole_parser.generate)
        context.setdefault('locale', self.locale)
        context.setdefault('cross_locale_path', self.cross_locale_path)
        context.setdefault('locale_name', self.locale_name)
        context.setdefault('_', self.message_catalog.gettext)

    def template_loaded(self, template):
        setup_flatland(template)
        Translator(LocalProxy(lambda: self.message_catalog)).setup(template)

    @request_property
    def message_catalog(self):
        dirname = resource_filename(self.module, 'translations')
        return Translations.load(dirname, [self.locale])

    @request_property
    def creole_parser(self):
        return Parser(creole11_base(
            wiki_links_base_url=self.path('dictionary:index')))

    def path(self, endpoint, **values):
        values.setdefault('locale', self.locale.language)
        return super(Relvlast, self).path(endpoint, **values)

    def cross_locale_path(self, locale):
        return self.path(self.local.endpoint,
                         **dict(self.route_values, locale=locale))

    def locale_name(self, locale):
        return self.locale.languages.get(locale, Locale(locale).display_name)
