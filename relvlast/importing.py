import re

from lxml             import objectify
from relvlast.objects import Language, WordProperties, Translation


def creolify(text):
    return re.sub(r'\$(.+?)_(.+?)\$', r'##\1,,\2,,##', unicode(text))


def linkify(text):
    return re.sub(r'\{(.+?)\}', r'[[\1]]', unicode(text))


def words_from_xml(filename, db, locale):

    if locale not in db.translations:
        language = db.translations[locale] = Language(locale)

    tree = objectify.parse(filename)
    root = tree.getroot()
    for valsi in root.direction.valsi:
        id = valsi.attrib['word']

        if id not in db.properties.words:
            word = WordProperties(id, valsi.attrib['type'])
            if hasattr(valsi, 'selmaho'):
                word.class_ = unicode(valsi.selmaho)
            if hasattr(valsi, 'rafsi'):
                word.affixes = tuple(str(affix) for affix in valsi.rafsi)
            db.properties.words.save(id, word)

        translation = Translation(id, creolify(valsi.definition))
        if hasattr(valsi, 'notes'):
            translation.notes = linkify(creolify(valsi.notes))
        language.words.save(id, translation)
