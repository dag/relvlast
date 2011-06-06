from paver.easy     import options, Bunch, task, cmdopts
from paver.tasks    import help
from paver.doctools import doc_clean, html


options(
    serve=
        Bunch(hostname='localhost',
              port=8008,
              no_reloader=False,
              no_debugger=False,
              no_evalex=False,
              production=False),
    sphinx=
        Bunch(builddir='../build'))


@task
@cmdopts([('port=', 'p', 'override default ({port})'.format(**options.serve)),
          ('no-reloader', 'R', 'disable the reloader'),
          ('no-debugger', 'D', 'disable the debugger'),
          ('no-evalex', 'E', 'disable exception evaluation'),
          ('production', 'P', 'set debug to false')])
def serve():
    """Run the development server."""
    opts = options.serve

    from werkzeug.serving import run_simple
    from relvlast         import Relvlast

    app = Relvlast(debug=not opts.production)
    run_simple(opts.hostname, int(opts.port), app,
               use_reloader = not opts.no_reloader,
               use_debugger = not opts.no_debugger,
               use_evalex   = not opts.no_evalex)


@task
def shell():
    """Enter a bpython shell configured for relvlast."""

    from bpython          import embed
    from werkzeug.test    import create_environ
    from relvlast         import Relvlast

    app = Relvlast()
    app.bind_to_environ(create_environ())

    embed(dict(app=app))
