from werkzeug.testapp import test_app
from ramverk.routing  import get


@get('/wsgi/')
def wsgi_info():
    return test_app


@get('/')
def index(request, translations, render):
    page = translations.pages.latest('/')
    return render('index.html', page=page)
