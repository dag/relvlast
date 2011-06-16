from datetime       import datetime
from persistent     import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from ramverk.utils  import EagerCachedProperties, ReprAttributes, has
from ramverk.utils  import InitFromArgs, args


class Base(EagerCachedProperties, ReprAttributes):

    pass


class Object(Base, InitFromArgs, Persistent):

    pass


class Collection(Base, OOBTree):

    pass


class List(Base, IOBTree):

    @property
    def last(self):
        if not self:
            return None
        return self[self.maxKey()]

    @property
    def id(self):
        if not self:
            return 0
        return self.maxKey()

    def save(self, object):
        self[self.id + 1] = object


@args('object')
@has(timestamp=datetime.utcnow)
class Version(Object):

    pass


class VersionedObjects(Collection):

    def save(self, name, object, *args, **kwargs):
        if name not in self:
            self[name] = List()
        version = Version(object, *args, **kwargs)
        self[name].save(version)
        return version

    def latest(self, name):
        return self[name].last.object


@args('of', 'definition', 'notes')
class Translation(Object):

    pass


@args('id', 'type', 'class_', 'affixes')
class WordProperties(Object):

    pass


@args('title', 'body')
class Page(Object):

    pass


@args('locale')
@has(words=VersionedObjects)
class Language(Object):

    pass


@has(words=VersionedObjects, pages=VersionedObjects)
class Properties(Object):

    pass


@has(translations=Collection, properties=Properties)
class Root(Object):

    pass
