from __future__        import absolute_import
from textwrap          import dedent

from attest            import Tests, assert_hook
from werkzeug.test     import Client
from werkzeug.wrappers import BaseResponse
from ZODB.DemoStorage  import DemoStorage

from tests.app         import TestApp


app = TestApp(storage=DemoStorage)


request = Tests()

@request.context
def test_client():
    yield Client(app, BaseResponse)


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
