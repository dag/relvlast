from inspect        import isclass
from werkzeug.utils import import_string
from paver.easy     import options, Bunch, task, sh, pushd, path, info
from paver.tasks    import help
from paver.doctools import doc_clean, html
from ramverk.paver  import serve, shell


options.ramverk = Bunch(app='relvlast:Relvlast')
options.sphinx  = Bunch(builddir='../build')


@task
def cover():
    """Measure test coverage."""
    sh('coverage run -m attest')
    sh('coverage report')
    sh('coverage html')


@task
def import_words():
    """Import data exported to XML from jbovlaste."""
    import re
    from lxml import objectify
    from BTrees.OOBTree import OOBTree
    from relvlast import Relvlast
    from relvlast.objects import Word

    app = import_string(options.ramverk.app)
    if isclass(app):
        app = app()

    def creolify(text):
        return re.sub(r'\$(.+?)_(.+?)\$', r'##\1,,\2,,##', str(text))

    def linkify(text):
        return re.sub(r'\{(.+?)\}', r'[[\1]]', str(text))

    tree = objectify.parse('exports/jbo.xml')
    root = tree.getroot()

    with app:
        app.db.words = OOBTree()
        for valsi in root.direction.valsi:
            id = valsi.attrib['word']
            type = valsi.attrib['type']
            class_ = str(getattr(valsi, 'selmaho', ''))
            affixes = tuple(str(affix)
                            for affix in getattr(valsi, 'rafsi', []))
            defn = creolify(valsi.definition)
            notes = linkify(creolify(getattr(valsi, 'notes', '')))
            app.db.words[id] = Word(id=id,
                                    type=type,
                                    class_=class_,
                                    affixes=affixes,
                                    definition=defn,
                                    notes=notes)


@task
def deploy():
    """Deploy to ep.io."""
    with pushd('relvlast/compiled'):
        sh('pyscss -o main.css main.scss')
    sh('epio upload')


@task
def localedata():
    """Install custom locale data for Babel."""
    import yaml, babel, copy, cPickle as pickle
    for source in path('localedata').files('*.yml'):
        data = copy.deepcopy(babel.localedata.load('en'))
        babel.localedata.merge(data, yaml.load(source.bytes()))
        with pushd(babel.localedata._dirname):
            target = source.stripext().basename() + '.dat'
            with open(target, 'wb') as stream:
                info('writing ' + target)
                pickle.dump(data, stream, -1)
