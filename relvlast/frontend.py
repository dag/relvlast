from werkzeug.routing import Rule
from werkzeug.testapp import test_app
from creoleparser     import text2html
from ramverk.routing  import router, endpoint
from relvlast.objects import Page


@router
def urls():
    yield Rule('/wsgi/',
               endpoint='wsgi_info')
    yield Rule('/',
               endpoint='index',
               methods=('GET', 'POST'))


@endpoint
def wsgi_info():
    return test_app


@endpoint
def index(request, render, db, redirect):
    if request.method == 'GET':
        page = db.start
        title = page.title
        body = text2html.generate(page.body)
        form = Page.schema(vars(page))
        return render('index.html', form=form, title=title, body=body)

    elif request.method == 'POST':
        form = Page.schema(request.form)
        if form.validate():
            page = Page(**form.value)
            db.start = page
        return redirect('index')
