from __future__          import absolute_import
from errno               import ENOENT
from pkg_resources       import resource_string, resource_filename
from werkzeug.exceptions import abort
from werkzeug.utils      import cached_property
from ramverk.compiling   import CompilerMixinBase

import scss


class SCSSMixin(CompilerMixinBase):
    """Add an SCSS compiler to an application."""

    @cached_property
    def compilers(self):
        compilers = super(SCSSMixin, self).compilers
        compilers['.css'] = self.__compiler
        return compilers

    @cached_property
    def __parser(self):
        parser = scss.Scss()
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
        old = scss.LOAD_PATHS
        scss.LOAD_PATHS = ','.join([resource_filename(self.module, 'compiled'),
                                    scss.LOAD_PATHS])
        try:
            css = self.__parser.compile(string)
        finally:
            scss.LOAD_PATHS = old
        return self.response(css, mimetype='text/css')
