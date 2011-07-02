from apipkg            import initpkg
from ramverk.inventory import members


api = {}
for module, names in members.iteritems():
    for name in names:
        assert name not in api
        api[name] = ':'.join([module, name])


initpkg(__name__, api)
