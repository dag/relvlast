from ZODB.DemoStorage    import DemoStorage
from werkzeug.routing    import Map, Rule
from werkzeug.utils      import cached_property

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

    @cached_property
    def url_map(self):
        return Map([Rule('/', endpoint='index',
                              methods=('GET', 'POST'))])

    @cached_property
    def endpoints(self):
        return dict(index=endpoints.index)
