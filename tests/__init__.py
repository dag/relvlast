from contextlib       import contextmanager
from werkzeug.test    import Client, create_environ
from ZODB.DemoStorage import DemoStorage
from fudge            import registry
from tests.app        import TestApp


@contextmanager
def testapp():
    yield TestApp(storage=DemoStorage, secret_key='testing')


@contextmanager
def testenv():
    with testapp() as app:
        with app.contextbound(create_environ()) as env:
            yield app, env


@contextmanager
def wsgiclient():
    with testapp() as app:
        yield Client(app, app.response)


@contextmanager
def mocking():
    registry.clear_all()
    yield
    registry.verify()
