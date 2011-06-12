from werkzeug.routing import Rule
from ramverk.routing  import router, endpoint


@router
def urls():
    yield Rule('/',
               endpoint='index')
    yield Rule('/<word>/',
               endpoint='word')


@endpoint
def index(render, db):
    return render('dictionary/index.html', words=db.words.values()[:20])
