from persistent          import Persistent
from ZODB.DemoStorage    import DemoStorage

from werkzeug.utils      import redirect

from ramverk.application import Application
from ramverk.genshi      import GenshiMixin
from ramverk.utils       import request_property
from ramverk.zodb        import TransactionMixin, ZODBMixin


class Root(Persistent):

    greeting = 'Welcome'


def index(request, render, db, path):

    if request.method == 'GET':
        return render('index.html', greeting=db.greeting)

    if request.method == 'POST':
        db.greeting = request.form.get('greeting')
        return redirect(path('index'))


class TestApp(TransactionMixin, ZODBMixin, GenshiMixin, Application):

    def storage(self):
        return DemoStorage()

    @request_property
    def db(self):
        if 'testapp' not in self.root_object:
            self.root_object['testapp'] = Root()
        return self.root_object['testapp']

    def setup(self):
        self.route('/', index, methods=('GET', 'POST'))
