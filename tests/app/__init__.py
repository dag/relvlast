from persistent        import Persistent
from logbook           import TestHandler
from werkzeug.routing  import Rule

from ramverk.fullstack import Application
from ramverk.utils     import request_property
from ramverk.routing   import endpoint


class Root(Persistent):

    greeting = 'Welcome'


class TestApp(Application):

    def create_template_context(self, overrides):
        context = super(TestApp, self).create_template_context(overrides)
        context.setdefault('injected', 42)
        return context

    @request_property
    def db(self):
        if 'testapp' not in self.root_object:
            self.root_object['testapp'] = Root()
        return self.root_object['testapp']

    def setup(self):
        self.log_handler = TestHandler()
        self.route(Rule('/', endpoint='index', methods=('GET', 'POST')))
        self.scan_for_endpoints()


@endpoint
def index(log, request, render, db, redirect):
    log.info('in index view')

    if request.method == 'GET':
        return render('index.html', greeting=db.greeting)

    if request.method == 'POST':
        db.greeting = request.form.get('greeting')
        return redirect('index')
