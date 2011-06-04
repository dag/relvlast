from ZODB.FileStorage    import FileStorage
from werkzeug.testapp    import test_app

from ramverk.application import Application
from ramverk.genshi      import GenshiMixin
from ramverk.utils       import request_property
from ramverk.zodb        import TransactionMixin, ZODBMixin

from relvlast            import objects, endpoints


class Relvlast(TransactionMixin, ZODBMixin, GenshiMixin, Application):

    @request_property
    def db(self):
        if 'relvlast' not in self.root_object:
            self.root_object['relvlast'] = objects.Root()
        return self.root_object['relvlast']

    def setup(self):
        self.storage = FileStorage('relvlast.db')
        self.route('/__info__', lambda x: test_app, endpoint='__info__')
        self.route('/', endpoints.index)
