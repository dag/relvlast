from persistent          import Persistent
from ZODB.FileStorage    import FileStorage
from werkzeug.testapp    import test_app

from ramverk.application import Application
from ramverk.genshi      import GenshiMixin
from ramverk.utils       import request_property
from ramverk.zodb        import TransactionMixin, ZODBMixin


class Root(Persistent):
    pass


def index(render):
    return render('index.html')


class Relvlast(TransactionMixin, ZODBMixin, GenshiMixin, Application):

    def storage(self):
        return FileStorage('relvlast.db')

    @request_property
    def db(self):
        if 'relvlast' not in self.root_object:
            self.root_object['relvlast'] = Root()
        return self.root_object['relvlast']

    def setup(self):
        self.route('/__info__', lambda x: test_app, endpoint='__info__')
        self.route('/', index)
