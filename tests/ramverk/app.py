from attest import Tests, assert_hook, raises
from fudge  import patch
from tests  import testapp


app = Tests(contexts=[testapp])


@app.test
def transactions(app):
    manager = app.transaction_manager

    with app:
        app.persistent[1] = 42
    with app:
        assert app.persistent[1] == 42

    with app:
        app.persistent[2] = 43
        manager.doom()
        assert 2 in app.persistent
    with app:
        assert 2 not in app.persistent

    with app:
        app.persistent[3] = 44
        manager.abort()
        assert 3 not in app.persistent
    with app:
        assert 3 not in app.persistent

    with patch('transaction.manager.begin') as begin:
        begin.expects_call()
        app.__enter__()

    with patch('transaction.manager.commit') as commit:
        commit.expects_call()
        app.__exit__(None, None, None)

    with patch('transaction.manager.abort') as abort:
        abort.expects_call()
        with raises(AssertionError):
            with app:
                assert False


@app.test
def url_building(app):
    assert app.path('module:index') == '/module/'
    assert app.url('module:index') == 'http://localhost/module/'
    assert app.url('en_index') == 'http://en.localhost/'
