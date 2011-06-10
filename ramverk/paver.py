from __future__     import absolute_import
from paver.easy     import options, Bunch, task, cmdopts
from werkzeug.utils import import_string


options.ramverk = Bunch()
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
    from logbook.compat import redirect_logging
    from werkzeug       import _internal

    redirect_logging()
    appfactory = import_string(options.ramverk.app)

    opts = options.serve
    app = appfactory(debug=opts.debug)

    def _log(type, message, *args, **kwargs):
        getattr(app.log, type)(message % args % kwargs)
    _internal._log = _log

    from werkzeug.serving import run_simple
    run_simple(opts.hostname, int(opts.port), app,
               use_reloader = not opts.no_reloader,
               use_debugger = not opts.no_debugger,
               use_evalex   = not opts.no_evalex)


@task
def shell():
    """Enter a bpython shell set up for the app."""

    from bpython       import embed
    from werkzeug.test import create_environ

    appfactory = import_string(options.ramverk.app)
    app = appfactory()
    app.bind_to_environ(create_environ())

    embed(dict(app=app))
