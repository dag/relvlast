from pkg_resources  import resource_string
from persistent     import Persistent
from BTrees.OOBTree import OOBTree
from creoleparser   import text2html
from flatland       import Form, String


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

    @property
    def html(self):
        return text2html.generate(self.body)


class Word(Persistent):

    class schema(Form):

        id = String
        definition = String

    def __init__(self, id, definition):
        self.id, self.definition = id, definition

    @property
    def html(self):
        return text2html.generate(self.definition)
