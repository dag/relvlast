from attest        import Tests, assert_hook
from werkzeug.test import create_environ
from tests         import testapp, testenv


app = Tests(contexts=[testapp])
env = Tests(contexts=[testenv])


@app.test
def configurators(app):
    assert app.some_attribute == 'set by configurator'
    assert app.another_attribute == 666


@app.test
def transactions(app):

    with app.contextbound(create_environ()):
        app.local.persistent[1] = 42
    with app.contextbound(create_environ()):
        assert app.local.persistent[1] == 42

    with app.contextbound(create_environ()):
        app.local.persistent[2] = 43
        app.local.transaction_manager.doom()
        assert 2 in app.local.persistent
    with app.contextbound(create_environ()):
        assert 2 not in app.local.persistent

    with app.contextbound(create_environ()):
        app.local.persistent[3] = 44
        app.local.transaction_manager.abort()
        assert 3 not in app.local.persistent
    with app.contextbound(create_environ()):
        assert 3 not in app.local.persistent


@env.test
def url_building(app):
    path, url = app.local.path, app.local.url
    assert path(':index') == '/'
    assert path('.module:index') == '/module/'
    assert path('tests.app.module:index') == '/module/'
    assert url('.module:index') == 'http://localhost/module/'
    assert url('tests.app.module:index') == 'http://localhost/module/'
    assert url('tests.app.subdomain:en_index') == 'http://en.localhost/'
