from __future__     import absolute_import
from paver.easy     import options, Bunch, task, cmdopts
from werkzeug.utils import import_string


options.ramverk = Bunch()
options.shell   = Bunch(namespace=None, fake_request=None)
options.serve   = Bunch(hostname='localhost',
                        port=8008,
                        no_reloader=False,
                        no_debugger=False,
                        no_evalex=False,
                        debug=True)


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

    appfactory = import_string(options.ramverk.app)

    opts = options.serve
    app = appfactory(debug=opts.debug)
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
    appfactory = import_string(options.ramverk.app)
    app = appfactory(debug=True)
    environ = create_environ(options.shell.fake_request)

    locals = dict(app=app)
    namespace = options.shell.namespace or app.module
    locals.update(vars(import_string(namespace)))

    with app.environment(app, environ):
        try:
            from bpython import embed
            embed(locals)
        except ImportError:
            from code import interact
            interact(local=locals)
