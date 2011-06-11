from werkzeug.routing import Rule
from werkzeug.utils   import cached_property
from ramverk.routing  import URLMapMixin


def compiled(route_values, compilers):
    filename = route_values['name']
    compiler_name = filename[filename.index('.'):]
    compiler = compilers[compiler_name]
    return compiler(filename)


class CompilerMixinBase(URLMapMixin):
    """Base class for compiler mixins."""

    def setup_mixins(self):
        self.route(Rule('/compiled/<path:name>', endpoint='compiled'))
        self.endpoints['compiled'] = compiled
        super(CompilerMixinBase, self).setup_mixins()

    @cached_property
    def compilers(self):
        """Mapping of output file extensions to compilers."""
        return {}
