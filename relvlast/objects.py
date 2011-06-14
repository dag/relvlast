from pkg_resources  import resource_string
from werkzeug.utils import cached_property
from persistent     import Persistent
from BTrees.OOBTree import OOBTree
from relvlast       import schemata


class Root(Persistent):

    @cached_property
    def start(self):
        return Page("la lojban bangu fi lo si'o zifre",
                    resource_string('relvlast', 'lojban.creole'))

    @cached_property
    def words(self):
        return OOBTree()


class Page(Persistent):

    schema = schemata.Page

    def __init__(self, title, body):
        self.title, self.body = title, body


class Word(Persistent):

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
