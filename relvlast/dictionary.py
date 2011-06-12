from werkzeug.routing import Rule
from ramverk.routing  import router, endpoint


@router
def urls():
    yield Rule('/',
               endpoint='index')
    yield Rule('/<word>/',
               endpoint='word')


@endpoint
def index(request, render, db):
    words = db.words.values()
    page = request.args.get('papri', 1, type=int)
    per = 50
    end = per * page
    start = end - per
    total = len(words) / per
    return render('dictionary/index.html',
                  words=words[start:end],
                  total=total)
