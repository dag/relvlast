from __future__       import absolute_import
from pkg_resources    import resource_string
from werkzeug.routing import Rule
from werkzeug.utils   import cached_property
from scss.parser      import Stylecheet as Stylesheet
from ramverk.routing  import URLMapMixin


def compile_scss(_SCSSMixin__parser, route_values, module, response):
    source = 'compiled/{}.scss'.format(route_values['path'])
    string = resource_string(module, source)
    css = _SCSSMixin__parser.parse(string)
    return response(css, mimetype='text/css')


class SCSSMixin(URLMapMixin):
    """Add an SCSS compiler to an application."""

    def setup_mixins(self):
        super(SCSSMixin, self).setup_mixins()
        self.route(Rule('/compiled/<path:path>.css', endpoint='scss'))
        self.endpoints['scss'] = compile_scss

    @cached_property
    def __parser(self):
        return Stylesheet(options=dict(compress=True))
