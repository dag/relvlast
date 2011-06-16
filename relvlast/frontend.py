from werkzeug.routing import Rule
from werkzeug.testapp import test_app
from ramverk.routing  import router, endpoint
from relvlast.objects import Page


@router
def urls():
    yield Rule('/wsgi/', endpoint='wsgi_info')
    yield Rule('/', endpoint='index')


@endpoint
def wsgi_info():
    return test_app


@endpoint
def index(request, translations, render):
    if request.method == 'GET':
        page = translations.pages.latest('/')
        return render('index.html', page=page)
