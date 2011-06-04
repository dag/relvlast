from ZODB.DemoStorage    import DemoStorage
from werkzeug.routing    import Map, Rule
from werkzeug.utils      import cached_property

from ramverk.application import Application
from ramverk.genshi      import GenshiMixin
from ramverk.utils       import request_property
from ramverk.zodb        import TransactionMixin, ZODBMixin

from tests.app           import objects, endpoints


class TestApp(TransactionMixin, ZODBMixin, GenshiMixin, Application):

    def setup(self):
        self.storage = DemoStorage()
        self.route('/', endpoints.index, methods=('GET', 'POST'))

    @request_property
    def db(self):
        if 'testapp' not in self.root_object:
            self.root_object['testapp'] = objects.Root()
        return self.root_object['testapp']
