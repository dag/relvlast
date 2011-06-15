from __future__    import absolute_import
from pkg_resources import resource_exists, resource_stream
from babel         import localedata
import yaml


_exists = localedata.exists
_load = localedata.load


def exists(name):
    return _exists(name) or\
           resource_exists('relvlast', 'localedata/{0}.yml'.format(name))


def load(name, merge_inherited=True):
    try:
        return _load(name, merge_inherited)
    except IOError:
        return yaml.load(resource_stream('relvlast',
            'localedata/{0}.yml'.format(name)))


def patch():
    localedata.exists = exists
    localedata.load = load
