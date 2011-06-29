from werkzeug.routing import Rule
from ramverk.routing  import MethodDispatch, router, route, get


@router
def urls():
    yield Rule('/', endpoint='index', methods=('GET', 'POST'))


def index(application, request, render, db, redirect):
    application.log.info('in index view')

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


@route('/classic/')
class Classic(MethodDispatch):

    renderer = 'json'

    def configure(self):
        self.greeting = self.environment.db.greeting

    def get(self, render):
        return render(self.renderer, greeting=self.greeting)


@route('/session/')
class Session(MethodDispatch):

    def post(self, session, request, redirect):
        session['user'] = request.form['user']
        return redirect(':Session')

    def get(self, response, session):
        return response(session['user'])
