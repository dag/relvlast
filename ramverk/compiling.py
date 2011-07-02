from werkzeug.utils import cached_property


class EnvironmentCompilerMixin(object):
    """Environment mixin dispatching to compilers."""

    def __call__(self):
        if self.request.path.startswith('/compiled/'):
            filename = self.request.path.split('/compiled/', 1)[1]
            compiler_name = filename[filename.index('.'):]
            compiler = self.application.compilers[compiler_name]
            return compiler(filename)
        return super(EnvironmentCompilerMixin, self).__call__()


class CompilerMixinBase(object):
    """Base class for compiler mixins."""

    def __create__(self):
        super(CompilerMixinBase, self).__create__()
        if hasattr(self, 'url_map'):
            self.url_map.add(
                self.url_rule_class(
                    '/compiled/<path:name>',
                    endpoint='compiled',
                    build_only=True))

    @cached_property
    def compilers(self):
        """Mapping of output file extensions to compilers."""
        return {}
