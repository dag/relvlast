from __future__          import absolute_import
from errno               import ENOENT
from pkg_resources       import resource_string
from werkzeug.exceptions import abort
from werkzeug.utils      import cached_property
from scss                import Scss
from ramverk.compiling   import CompilerMixinBase


class SCSSMixin(CompilerMixinBase):
    """Add an SCSS compiler to an application."""

    @cached_property
    def compilers(self):
        compilers = super(SCSSMixin, self).compilers
        compilers['.css'] = self.__compiler
        return compilers

    @cached_property
    def __parser(self):
        parser = Scss()
        parser.scss_opts.update(compress=False)
        return parser

    def __compiler(self, filename):
        source = 'compiled/{0}.scss'.format(filename[:-4])
        try:
            string = resource_string(self.module, source)
        except IOError as e:
            if e.errno == ENOENT:
                abort(404)
            raise
        css = self.__parser.compile(string)
        return self.response(css, mimetype='text/css')
