from contextlib       import contextmanager
from werkzeug.test    import Client, create_environ
from ZODB.DemoStorage import DemoStorage
from fudge            import registry
from tests.app        import TestApp


@contextmanager
def testapp():
    app = TestApp(storage=DemoStorage)
    with app.request_context(create_environ()):
        app.match_request_to_endpoint()
        yield app


@contextmanager
def wsgiclient():
    with testapp() as app:
        yield Client(app, app.response)


@contextmanager
def mocking():
    registry.clear_all()
    yield
    registry.verify()
