from inspect             import isfunction

from logbook             import Logger

from werkzeug.exceptions import HTTPException
from werkzeug.local      import Local, release_local
from werkzeug.utils      import cached_property
from werkzeug.wrappers   import Request, Response
from werkzeug.wsgi       import responder

from ramverk.utils       import request_property


class HTMLResponse(Response):

    default_mimetype = 'text/html'


class Application(object):

    debug = False

    response = HTMLResponse

    def __init__(self, **overrides):
        for key, value in overrides.iteritems():
            setattr(self, key, value)

    @cached_property
    def local(self):
        return Local()

    @cached_property
    def log(self):
        return Logger(self.__class__.__name__)

    @request_property
    def request(self):
        return Request(self.local.environ)

    @request_property
    def url_adapter(self):
        return self.url_map.bind_to_environ(self.local.environ)

    def url(self, endpoint, **values):
        return self.url_adapter.build(endpoint, values, force_external=True)

    def path(self, endpoint, **values):
        return self.url_adapter.build(endpoint, values)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def dispatch(self, endpoint, values):
        view = self.endpoints[endpoint]
        try:
            return view(self, **values)
        except HTTPException as e:
            return e

    @responder
    def __call__(self, environ, start_response):
        release_local(self.local)
        self.local.environ = environ
        with self:
            response = self.url_adapter.dispatch(self.dispatch)
        return response
