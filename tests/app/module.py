from ramverk.routing import router


@router
def urls(rule):
    yield rule('/', endpoint='index')


def index(response):
    return response('module index')
