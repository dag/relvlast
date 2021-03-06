from werkzeug.exceptions import NotFound
from ramverk.routing     import get


@get('/')
def index(request, render, translations):
    words = translations.words.values()
    page = request.args.get('papri', 1, type=int)
    per = 50
    end = per * page
    start = end - per
    total = len(words) / per
    return render('dictionary/index.html',
                  words=words[start:end],
                  total=total)


@get('/<word>/')
def word(render, db, translations, segments, request, redirect):
    id = segments.word

    try:
        translation = translations.words.latest(id)
        word = db.properties.words.latest(id)
    except KeyError:
        raise NotFound

    if request.method == 'GET':
        return render('dictionary/word.html',
                      translation=translation,
                      word=word)
