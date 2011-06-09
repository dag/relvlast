from attest      import Tests, assert_hook
from transaction import manager
from tests       import testapp


app = Tests(contexts=[testapp])


@app.test
def transactions(app):
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
