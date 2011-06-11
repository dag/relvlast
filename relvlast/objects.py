from persistent     import Persistent
from BTrees.OOBTree import OOBTree
from flatland       import Form, String


class Root(Persistent):

    def __init__(self):
        self.definitions = OOBTree()


class Definition(Persistent):

    class schema(Form):
        word = String
        definition = String

    def __init__(self, word, definition):
        self.word = word
        self.definition = definition
