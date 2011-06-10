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
