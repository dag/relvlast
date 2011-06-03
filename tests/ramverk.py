from __future__        import absolute_import
from textwrap          import dedent

from attest            import Tests, assert_hook
from werkzeug.test     import Client
from werkzeug.wrappers import BaseResponse

from tests.app         import TestApp


request = Tests()

@request.context
def test_client():
    app = TestApp()
    client = Client(app, BaseResponse)
    yield client


@request.test
def first_get_to_index(client):
    response = client.get('/')
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
