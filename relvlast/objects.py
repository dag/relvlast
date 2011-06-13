from pkg_resources  import resource_string
from persistent     import Persistent
from BTrees.OOBTree import OOBTree
from flatland       import Form, String, List


class Root(Persistent):

    def __init__(self):
        self.start = Page("la lojban bangu fi lo si'o zifre",
                          resource_string('relvlast', 'lojban.creole'))

        self.words = OOBTree()


class Page(Persistent):

    class schema(Form):

        title = String
        body  = String

    def __init__(self, title, body):
        self.title, self.body = title, body


class Word(Persistent):

    class schema(Form):

        id = String
        type = String
        class_ = String
        affixes = List.of(String).using(optional=True)
        definition = String
        notes = String

    id = None
    type = None
    class_ = None
    affixes = ()
    definition = None
    notes = None

    def __init__(self, **attrs):
        for name, value in attrs.iteritems():
            setattr(self, name, value)
