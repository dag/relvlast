from ramverk.routing import router


@router
def urls(rule):
    yield rule('/', endpoint='index')
