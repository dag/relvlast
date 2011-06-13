from werkzeug.exceptions import NotFound
from werkzeug.routing    import Rule
from ramverk.routing     import router, endpoint
from relvlast.objects    import Word


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


@endpoint
def word(render, db, route_values, request, redirect):
    id = route_values['word']
    try:
        word = db.words[id]
    except KeyError:
        raise NotFound

    if request.method == 'GET':
        form = Word.schema(vars(word))
        return render('dictionary/word.html', word=word, form=form)

    elif request.method == 'POST':
        word = Word(id=id, affixes=word.affixes, **request.form.to_dict())
        db.words[id] = word
        return redirect('dictionary:word', word=id)
