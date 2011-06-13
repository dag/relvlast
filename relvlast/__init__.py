from flatland.out.genshi import setup as setup_flatland
from creoleparser        import Parser, creole11_base
from werkzeug.utils      import cached_property
from ramverk.fullstack   import Application
from ramverk.utils       import request_property
from relvlast.objects    import Root


class Relvlast(Application):

    @cached_property
    def creole_parser(self):
        return Parser(creole11_base(
            wiki_links_base_url=self.path('dictionary:index')))

    def update_template_context(self, context):
        context = super(Relvlast, self).update_template_context(context)
        context.setdefault('creole', self.creole_parser.generate)
        return context

    @request_property
    def db(self):
        if 'relvlast' not in self.root_object:
            self.root_object['relvlast'] = Root()
        return self.root_object['relvlast']

    def setup(self):
        self.scan('relvlast.frontend')
        self.scan('relvlast.dictionary', '/vlaste', 'dictionary:')

    def template_loaded(self, template):
        setup_flatland(template)
