from __future__          import absolute_import
from ast                 import literal_eval
from paver.easy          import Bunch, options, task, cmdopts
from werkzeug.utils      import import_string
from ramverk.application import BaseApplication


options.app      = None
options.settings = Bunch(debug=True)
options.shell    = Bunch(namespace=None, fake_request='/')
options.serve    = Bunch(hostname='localhost',
                         port=8008,
                         no_reloader=False,
                         no_debugger=False,
                         no_evalex=False)


def _get_application():
    app = options.app
    if app is None:
        raise SystemExit('no app configured')
    if isinstance(app, basestring):
        try:
            app = import_string(app)
        except ImportError:
            import sys
            sys.path.insert(0, '')
            app = import_string(app)
    if not isinstance(app, BaseApplication):
        settings = {}
        for key, value in options.settings.iteritems():
            try:
                settings[key] = literal_eval(value)
            except ValueError:
                settings[key] = value
        app = app(**settings)
    return app


@task
@cmdopts([('port=', 'p', 'override default ({port})'.format(**options.serve)),
          ('no-reloader', 'R', 'disable the reloader'),
          ('no-debugger', 'D', 'disable the debugger'),
          ('no-evalex', 'E', 'disable exception evaluation')])
def serve():
    """Run a development server."""
    from logging        import getLogger, DEBUG
    from logbook.compat import redirect_logging

    redirect_logging()
    getLogger().setLevel(DEBUG)

    opts = options.serve
    app = _get_application()
    app.log_handler.push_application()

    from werkzeug.serving import run_simple
    run_simple(opts.hostname, int(opts.port), app,
               use_reloader = not opts.no_reloader,
               use_debugger = not opts.no_debugger,
               use_evalex   = not opts.no_evalex)


@task
def shell():
    """Enter a [b]python shell set up for the app."""
    from werkzeug.test import create_environ
    app = _get_application()
    environ = create_environ(options.shell.fake_request)

    locals = dict(app=app)
    namespace = options.shell.namespace or app.module
    module = import_string(namespace)
    locals.update(item for item in vars(module).iteritems()
                  if not item[0].startswith('_'))

    with app.contextbound(environ):
        try:
            from bpython import embed
            embed(locals)
        except ImportError:
            from code import interact
            interact(local=locals)


@task
def routes():
    """List the application's URL rules."""
    app = _get_application()
    for rule in app.url_map.iter_rules():
        print
        print ' ',
        if rule.methods:
            print '[' + '|'.join(rule.methods) + ']',
        print rule.rule
        print '    ->', rule.endpoint


from ramverk.inventory import members
__all__ = members[__name__]
