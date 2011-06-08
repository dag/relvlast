from __future__        import absolute_import
from textwrap          import dedent

from attest            import Tests, assert_hook
from werkzeug.test     import Client, create_environ
from ZODB.DemoStorage  import DemoStorage
from transaction       import manager

from ramverk.utils     import Bunch

from tests.app         import TestApp


app = TestApp(storage=DemoStorage)


simple = Tests()

@simple.test
def transactions():
    with app:
        app.root_object[1] = 42
    with app:
        assert app.root_object[1] == 42

    with app:
        app.root_object[2] = 43
        manager.doom()
        assert 2 in app.root_object
    with app:
        assert 2 not in app.root_object

    with app:
        app.root_object[3] = 44
        manager.abort()
        assert 3 not in app.root_object
    with app:
        assert 3 not in app.root_object


request = Tests()

@request.context
def test_client():
    yield Client(app, app.response)

@request.test
def first_get_to_index(client):
    response = client.get('/')
    assert app.log_handler.formatted_records\
        == ['[DEBUG] TestApp: beginning transaction',
            '[DEBUG] TestApp: connecting ZODB',
             '[INFO] TestApp: in index view',
            '[DEBUG] TestApp: committing transaction',
            '[DEBUG] TestApp: disconnecting ZODB']
    assert response.status_code == 200
    assert response.data == dedent("""\
        <!DOCTYPE html>
        <html>
          <body>
            <h1>Welcome</h1>
            <form method="POST" action="/">
              <input type="text" name="greeting" placeholder="Enter a greeting">
            </form>
          </body>
        </html>""")

@request.test
def get_and_render_json(client):
    response = client.get('/?json')
    assert response.mimetype == 'application/json'
    assert response.data == '{"greeting": "Welcome"}'

@request.test
def post_to_and_get_index(client):
    response = client.post('/', data={'greeting': 'Hello'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert response.data == dedent("""\
        <!DOCTYPE html>
        <html>
          <body>
            <h1>Hello</h1>
            <form method="POST" action="/">
              <input type="text" name="greeting" placeholder="Enter a greeting">
            </form>
          </body>
        </html>""")

@request.test
def four_oh_four(client):
    response = client.get('/404')
    assert response.status_code == 404

@request.test
def module(client):
    response = client.get('/module/')
    assert response.data == 'module index'


genshi = Tests()

@genshi.context
def fake_wsgi_environ():
    app.bind_to_environ(create_environ())
    yield

@genshi.test
def render_genshi_template():
    response = app.render('index.html', greeting='Hi')
    assert response.data == dedent("""\
        <!DOCTYPE html>
        <html>
          <body>
            <h1>Hi</h1>
            <form method="POST" action="/">
              <input type="text" name="greeting" placeholder="Enter a greeting">
            </form>
          </body>
        </html>""")

@genshi.test
def injected_context():
    response = app.render('context.html')
    assert response.data == dedent("""\
        <!DOCTYPE html>
        <html>
          <body><p>The answer to the ultimate question is 42</p></body>
        </html>""")

@genshi.test
def override_context():
    response = app.render('context.html', injected='not 144')
    assert response.data == dedent("""\
        <!DOCTYPE html>
        <html>
          <body><p>The answer to the ultimate question is not 144</p></body>
        </html>""")

@genshi.test
def mutate_response():
    response = app.render('context.html').using(status=404, mimetype='text/css')
    assert response.status_code == 404
    assert response.content_type == 'text/css; charset=utf-8'


utils = Tests()

@utils.test
def bunch_attrs_and_items_are_same():

    bunch = Bunch(answer=42)
    assert bunch.answer is bunch['answer'] == 42

    del bunch.answer
    assert 'answer' not in bunch and not hasattr(bunch, 'answer')

    bunch.answer = 42
    assert bunch.answer is bunch['answer'] == 42

    del bunch['answer']
    assert 'answer' not in bunch and not hasattr(bunch, 'answer')
