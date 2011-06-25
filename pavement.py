from inspect        import isclass
from werkzeug.utils import import_string
from paver.easy     import options, Bunch, sh, pushd, path, info
from paver.easy     import task, consume_args
from paver.tasks    import help
from paver.doctools import doc_clean, html
from ramverk.paver  import serve, shell


options.ramverk = Bunch(app='relvlast:Relvlast')
options.sphinx  = Bunch(builddir='../build')
options.shell   = Bunch(namespace='relvlast.objects',
                        fake_request='/jbo/vlaste/')


@task
def cover():
    """Measure test coverage."""
    sh('coverage run -m attest tests')
    sh('coverage report')
    sh('coverage html')


@task
def import_words():
    """Import data exported to XML from jbovlaste."""
    from relvlast.importing import words_from_xml

    app = import_string(options.ramverk.app)
    if isclass(app):
        app = app()

    with app:
        for source in path('exports').files('*.xml'):
            locale = source.stripext().basename()
            info('importing ' + locale)
            words_from_xml(source, app.db, locale)


@task
def deploy():
    """Deploy to ep.io."""
    with pushd('relvlast/compiled'):
        sh('pyscss -o main.css main.scss')
    sh('epio upload')


@task
@consume_args
def epio(args):
    commands = ' '.join(args)
    sh('epio run_command paver ramverk.app=deployments.epio:app ' + commands)


@task
def localedata():
    """Install custom locale data for Babel."""
    import yaml, babel, copy, cPickle as pickle
    for source in path('relvlast/localedata').files('*.yml'):
        data = copy.deepcopy(babel.localedata.load('en'))
        babel.localedata.merge(data, yaml.load(source.bytes()))
        with pushd(babel.localedata._dirname):
            target = source.stripext().basename() + '.dat'
            with open(target, 'wb') as stream:
                info('writing ' + target)
                pickle.dump(data, stream, -1)


@task
def translations():
    sh('pybabel extract -F babel.ini -o messages.pot relvlast')
    sh('pybabel update -i messages.pot -d relvlast/translations')
    sh('pybabel compile -d relvlast/translations')
