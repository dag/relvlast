from werkzeug.routing import Rule
from ramverk.routing  import router, endpoint


@router
def urls():
    yield Rule('/', endpoint='index', methods=('GET', 'POST'))
    yield Rule('/page/<page>/', endpoint='page')


@endpoint
def index(log, request, render, db, redirect):
    log.info('in index view')

    if request.method == 'GET':
        if 'json' in request.args:
            return render('json', greeting=db.greeting)
        return render('index.html', greeting=db.greeting)

    if request.method == 'POST':
        db.greeting = request.form.get('greeting')
        return redirect('index')


@endpoint
def page(response, segments):
    return response(segments.page)
