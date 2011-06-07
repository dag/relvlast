from werkzeug.routing import Rule
from ramverk.routing  import router, endpoint


@router
def urls():
    yield Rule('/', endpoint='index')


@endpoint
def index(response):
    return response('module index')
