from inspect        import isclass
from werkzeug.utils import import_string
from paver.easy     import options, Bunch, task, sh
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

    tree = objectify.parse('jvs.xml')
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
