from persistent        import Persistent
from logbook           import TestHandler
from ramverk.fullstack import Application
from ramverk.utils     import request_property


class Root(Persistent):

    greeting = 'Welcome'


class TestApp(Application):

    def update_template_context(self, context):
        super(TestApp, self).update_template_context(context)
        context.setdefault('injected', 42)

    @request_property
    def db(self):
        if 'testapp' not in self.persistent:
            self.persistent['testapp'] = Root()
        return self.persistent['testapp']

    def configure(self):
        self.log_handler = TestHandler()
        self.scan('tests.app.frontend')
        self.scan('tests.app.module', '/module')
        self.scan('tests.app.subdomain', subdomain='en')
