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

    app = Relvlast()

    tree = objectify.parse('jvs.xml')
    root = tree.getroot()

    with app:
        app.db.words = OOBTree()
        for valsi in root.direction.valsi:
            defn = str(valsi.definition)
            defn = re.sub(r'\$(.+?)_(.+?)\$', r'##\1,,\2,,##', defn)
            word = Word(valsi.attrib['word'], defn)
            app.db.words[word.id] = word
