from persistent        import Persistent
from werkzeug.utils    import cached_property
from logbook           import TestHandler
from genshi.filters    import Transformer
from ramverk.fullstack import Environment, Application
from ramverk.genshi    import HTMLTemplate


class Root(Persistent):

    greeting = 'Welcome'


class TestEnvironment(Environment):

    @cached_property
    def db(self):
        return self.persistent.setdefault('root', Root())


class TestApp(Application):

    environment = TestEnvironment

    def update_template_context(self, context):
        super(TestApp, self).update_template_context(context)
        context.setdefault('injected', 42)

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
