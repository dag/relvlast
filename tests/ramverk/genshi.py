from textwrap import dedent
from attest   import Tests, assert_hook
from tests    import testapp


genshi = Tests(contexts=[testapp])


@genshi.test
def render_genshi_template(app):
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
def injected_context(app):
    response = app.render('context.html')
    assert response.data == dedent("""\
        <!DOCTYPE html>
        <html>
          <body><p>The answer to the ultimate question is 42</p></body>
        </html>""")


@genshi.test
def override_context(app):
    response = app.render('context.html', injected='not 144')
    assert response.data == dedent("""\
        <!DOCTYPE html>
        <html>
          <body><p>The answer to the ultimate question is not 144</p></body>
        </html>""")


@genshi.test
def mutate_response(app):
    response = app.render('context.html').using(status=404, mimetype='text/css')
    assert response.status_code == 404
    assert response.content_type == 'text/css; charset=utf-8'
