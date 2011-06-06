from persistent        import Persistent
from logbook           import TestHandler

from ramverk.fullstack import Application
from ramverk.utils     import request_property


class Root(Persistent):

    greeting = 'Welcome'


def index(log, request, render, db, redirect):
    log.info('in index view')

    if request.method == 'GET':
        return render('index.html', greeting=db.greeting)

    if request.method == 'POST':
        db.greeting = request.form.get('greeting')
        return redirect('index')


class TestApp(Application):

    @request_property
    def db(self):
        if 'testapp' not in self.root_object:
            self.root_object['testapp'] = Root()
        return self.root_object['testapp']

    def setup(self):
        self.route('/', index, methods=('GET', 'POST'))
        self.log_handler = TestHandler()
