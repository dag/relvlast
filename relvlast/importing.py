import re
from lxml             import objectify
from BTrees.OOBTree   import OOBTree
from relvlast.objects import Word


def creolify(text):
    return re.sub(r'\$(.+?)_(.+?)\$', r'##\1,,\2,,##', unicode(text))


def linkify(text):
    return re.sub(r'\{(.+?)\}', r'[[\1]]', unicode(text))


def words_from_xml(filename):
    words = OOBTree()
    tree = objectify.parse(filename)
    root = tree.getroot()
    for valsi in root.direction.valsi:
        id = valsi.attrib['word']
        type = valsi.attrib['type']
        class_ = str(getattr(valsi, 'selmaho', ''))
        affixes = tuple(str(affix) for affix in getattr(valsi, 'rafsi', []))
        defn = creolify(valsi.definition)
        notes = linkify(creolify(getattr(valsi, 'notes', '')))
        words[id] = Word(id=id,
                         type=type,
                         class_=class_,
                         affixes=affixes,
                         definition=defn,
                         notes=notes)
    return words
