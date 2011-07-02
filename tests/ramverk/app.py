from datetime      import datetime
from attest        import Tests, assert_hook, raises
from werkzeug.test import create_environ
from ramverk.local import get_current, current
from tests         import testapp, testenv


app = Tests(contexts=[testapp])
env = Tests(contexts=[testenv])


@env.test
def stack(app):
    assert get_current() is app.local
    assert current.application is app
    first_env = get_current()
    with app.contextbound(create_environ()) as second_env:
        assert get_current() is not first_env
        assert get_current() is second_env
    assert get_current() is first_env


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


@env.test
def json_renderer(app, env):

    now = datetime.now()
    response = env.render('json', time=now)
    assert response.data == '{"time": "%s"}' % now.isoformat()

    with raises(TypeError):
        env.render('json', response=response)
