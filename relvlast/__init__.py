from persistent        import Persistent
from werkzeug.testapp  import test_app

from ramverk.fullstack import Application
from ramverk.utils     import request_property


class Root(Persistent):
    pass


def index(render):
    return render('index.html')


class Relvlast(Application):

    @request_property
    def db(self):
        if 'relvlast' not in self.root_object:
            self.root_object['relvlast'] = Root()
        return self.root_object['relvlast']

    def setup(self):
        self.route('/__info__', lambda x: test_app, endpoint='__info__')
        self.route('/', index)
