from textwrap import dedent
from attest   import Tests, assert_hook
from tests    import wsgiclient


wsgi = Tests(contexts=[wsgiclient])


@wsgi.test
def first_get_to_index(client):
    response = client.get('/')
    assert client.application.log_handler.formatted_records\
        == ['[DEBUG] TestApp: connecting ZODB',
             '[INFO] TestApp: in index view',
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


@wsgi.test
def get_and_render_json(client):
    response = client.get('/?json')
    assert response.mimetype == 'application/json'
    assert response.data == '{"greeting": "Welcome"}'


@wsgi.test
def method_dispatch_class(client):
    response = client.get('/classic/')
    assert response.mimetype == 'application/json'
    assert response.data == '{"greeting": "Welcome"}'


@wsgi.test
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


@wsgi.test
def four_oh_four(client):
    response = client.get('/404')
    assert response.status_code == 404


@wsgi.test
def module(client):
    response = client.get('/module/')
    assert response.data == 'module index'


@wsgi.test
def segments(client):
    response = client.get('/page/fubar/')
    assert response.data == 'fubar'


@wsgi.test
def relative_endpoint(client):
    response = client.get('/relative-endpoint/')
    assert response.data == '/page/fubar/'


@wsgi.test
def compiled_scss(client):
    response = client.get('/compiled/style.css')
    assert response.mimetype == 'text/css'
    assert response.data == dedent("""\
        body h1 {
          font-size: larger;
        }

        """)
