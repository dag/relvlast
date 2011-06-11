from flatland.out.genshi import setup as setup_flatland
from ramverk.fullstack   import Application
from ramverk.utils       import request_property
from relvlast.objects    import Root


class Relvlast(Application):

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
