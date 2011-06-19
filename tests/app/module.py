from werkzeug.routing import Rule
from ramverk.routing  import router


@router
def urls():
    yield Rule('/', endpoint='index')


def index(response):
    return response('module index')
