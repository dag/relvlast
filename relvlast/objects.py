from pkg_resources  import resource_string
from werkzeug.utils import cached_property
from persistent     import Persistent
from BTrees.OOBTree import OOBTree
from ramverk.utils  import ForcePropertiesCalled, AttributeRepr, has
from relvlast       import schemata


class Object(ForcePropertiesCalled, AttributeRepr, Persistent):
    pass


@has(words=OOBTree)
class Root(Object):

    @cached_property
    def start(self):
        return Page("la lojban bangu fi lo si'o zifre",
                    resource_string('relvlast', 'lojban.creole'))


class Page(Object):

    schema = schemata.Page

    def __init__(self, title, body):
        self.title, self.body = title, body


class Word(Object):

    schema = schemata.Word

    id = None
    type = None
    class_ = None
    affixes = ()
    definition = None
    notes = None

    def __init__(self, **attrs):
        for name, value in attrs.iteritems():
            setattr(self, name, value)
