from persistent        import Persistent
from logbook           import TestHandler
from ramverk.fullstack import Application
from ramverk.utils     import request_property


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
        self.scan('tests.app.frontend')
        self.scan('tests.app.module', '/module', 'module:')
