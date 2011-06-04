from ZODB.DemoStorage    import DemoStorage

from ramverk.application import Application
from ramverk.genshi      import GenshiMixin
from ramverk.utils       import request_property
from ramverk.zodb        import TransactionMixin, ZODBMixin

from tests.app           import objects, endpoints


class TestApp(TransactionMixin, ZODBMixin, GenshiMixin, Application):

    def storage(self):
        return DemoStorage()

    @request_property
    def db(self):
        if 'testapp' not in self.root_object:
            self.root_object['testapp'] = objects.Root()
        return self.root_object['testapp']

    def setup(self):
        self.route('/', endpoints.index, methods=('GET', 'POST'))
