from persistent        import Persistent
from logbook           import TestHandler
from genshi.filters    import Transformer
from ramverk.fullstack import Application
from ramverk.genshi    import HTMLTemplate
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
        self.renderers['.html'].dialect = HTMLTemplate
        self.scan('tests.app.frontend')
        self.scan('tests.app.module', submount='/module')
        self.scan('tests.app.subdomain', subdomain='en')

    def filter_genshi_stream(self, template, stream):
        if template.filename == 'filtering.html':
            return stream | Transformer('p/text()').replace('Filtered')
        return stream
