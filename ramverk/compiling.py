from werkzeug.routing import Rule
from werkzeug.utils   import cached_property


class CompilerMixinBase(object):
    """Base class for compiler mixins."""

    def __create__(self):
        super(CompilerMixinBase, self).__create__()
        if hasattr(self, 'route'):
            self.route(Rule('/compiled/<path:name>',
                            endpoint='compiled',
                            build_only=True))

    @cached_property
    def compilers(self):
        """Mapping of output file extensions to compilers."""
        return {}

    def respond(self):
        if self.request.path.startswith('/compiled/'):
            filename = self.request.path.split('/compiled/', 1)[1]
            compiler_name = filename[filename.index('.'):]
            compiler = self.compilers[compiler_name]
            return compiler(filename)
        return super(CompilerMixinBase, self).respond()
