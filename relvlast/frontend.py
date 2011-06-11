from werkzeug.routing import Rule
from werkzeug.testapp import test_app
from ramverk.routing  import router, endpoint
from relvlast.objects import Definition


@router
def urls():
    yield Rule('/wsgi/',
               endpoint='wsgi_info')
    yield Rule('/',
               endpoint='index')
    yield Rule('/definitions/',
               endpoint='definitions',
               methods=('GET', 'POST'))


@endpoint
def wsgi_info():
    return test_app


@endpoint
def index(render):
    return render('index.html')


@endpoint
def definitions(request, render, db, redirect):
    form = Definition.schema(request.form)

    if request.method == 'GET':
        return render('definitions.html',
                      definitions=db.definitions,
                      form=form)

    elif request.method == 'POST':
        if form.validate():
            definition = Definition(**request.form)
            db.definitions[definition.word] = definition
        return redirect('definitions')
