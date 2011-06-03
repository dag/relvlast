from ZODB.FileStorage    import FileStorage
from werkzeug.routing    import Map, Rule
from werkzeug.utils      import cached_property

from ramverk.application import Application
from ramverk.genshi      import GenshiMixin
from ramverk.utils       import request_property
from ramverk.zodb        import TransactionMixin, ZODBMixin

from relvlast            import objects, endpoints


class Relvlast(TransactionMixin, ZODBMixin, GenshiMixin, Application):

    def storage(self):
        return FileStorage('relvlast.db')

    @request_property
    def db(self):
        if 'relvlast' not in self.root_object:
            self.root_object['relvlast'] = objects.Root()
        return self.root_object['relvlast']

    @cached_property
    def url_map(self):
        return Map([Rule('/', endpoint='index')])

    @cached_property
    def endpoints(self):
        return dict(index=endpoints.index)
