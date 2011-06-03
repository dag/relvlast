from __future__      import absolute_import
from genshi.template import TemplateLoader, loader, Context
from werkzeug.utils  import cached_property


class GenshiMixin(object):

    serializer = 'html'

    doctype = 'html5'

    @cached_property
    def __loader(self):
        return TemplateLoader([loader.package(self.__module__, 'templates')],
                              auto_reload=self.debug,
                              callback=self.template_loaded)

    def template_loaded(self, template):
        pass

    def context(self, overrides):
        context = Context(request=self.request,
                          url=self.url,
                          path=self.path)
        context['self'] = self
        context.update(overrides)
        return context

    def render(self, template_name, **context):
        template = self.__loader.load(template_name)
        stream = template.generate(self.context(context))
        rendering = stream.serialize(self.serializer, doctype=self.doctype)
        return self.response(rendering)
