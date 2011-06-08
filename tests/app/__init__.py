from persistent        import Persistent
from logbook           import TestHandler
from ramverk.fullstack import Application
from ramverk.utils     import request_property


class Root(Persistent):

    greeting = 'Welcome'


class TestApp(Application):

    def update_template_context(self, context):
        context.setdefault('injected', 42)
        return super(TestApp, self).update_template_context(context)

    @request_property
    def db(self):
        if 'testapp' not in self.root_object:
            self.root_object['testapp'] = Root()
        return self.root_object['testapp']

    def setup(self):
        self.log_handler = TestHandler()
        self.scan('tests.app.frontend')
        self.scan('tests.app.module', '/module', 'module:')
