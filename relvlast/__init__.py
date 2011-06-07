from persistent          import Persistent
from BTrees.OOBTree      import OOBTree
from flatland            import Form, String
from flatland.out.genshi import setup as setup_flatland
from werkzeug.routing    import Rule
from werkzeug.testapp    import test_app
from ramverk.fullstack   import Application
from ramverk.utils       import request_property
from ramverk.routing     import router, endpoint


class Root(Persistent):

    def __init__(self):
        self.definitions = OOBTree()


class Definition(Persistent):

    class schema(Form):
        word = String
        definition = String

    def __init__(self, word, definition):
        self.word = word
        self.definition = definition


class Relvlast(Application):

    @request_property
    def db(self):
        if 'relvlast' not in self.root_object:
            self.root_object['relvlast'] = Root()
        return self.root_object['relvlast']

    def setup(self):
        self.scan()

    def template_loaded(self, template):
        setup_flatland(template)


@router
def urls():
    yield Rule('/__info__',
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
