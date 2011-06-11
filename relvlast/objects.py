from pkg_resources  import resource_string
from persistent     import Persistent
from BTrees.OOBTree import OOBTree
from flatland       import Form, String


class Root(Persistent):

    def __init__(self):
        self.start = Page("la lojban bangu filo si'o zifre",
                          resource_string('relvlast', 'lojban.creole'))


class Page(Persistent):

    class schema(Form):

        title = String
        body  = String

    def __init__(self, title, body):
        self.title, self.body = title, body
