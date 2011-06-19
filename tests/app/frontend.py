from werkzeug.routing import Rule
from ramverk.routing  import router, endpoint, get


@router
def urls():
    yield Rule('/', endpoint='index', methods=('GET', 'POST'))


@endpoint
def index(log, request, render, db, redirect):
    log.info('in index view')

    if request.method == 'GET':
        if 'json' in request.args:
            return render('json', greeting=db.greeting)
        return render('index.html', greeting=db.greeting)

    if request.method == 'POST':
        db.greeting = request.form.get('greeting')
        return redirect(':index')


@get('/page/<page>/')
def page(response, segments):
    return response(segments.page)


@get('/relative-endpoint/')
def relative_endpoint(response, path):
    return response(path(':page', page='fubar'))
