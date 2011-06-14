from pkg_resources  import resource_string
from persistent     import Persistent
from BTrees.OOBTree import OOBTree
from relvlast       import schemata


class Root(Persistent):

    def __init__(self):
        self.start = Page("la lojban bangu fi lo si'o zifre",
                          resource_string('relvlast', 'lojban.creole'))

        self.words = OOBTree()


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
