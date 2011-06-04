from abc            import ABCMeta, abstractmethod
from ZODB.DB        import DB
from werkzeug.utils import cached_property


class ZODBMixin(object):
    """Add ZODB persistence to an application."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def storage(self):
        """Override to return the storage for ZODB."""

    @cached_property
    def __db(self):
        return DB(self.storage())

    @property
    def __connected(self):
        return hasattr(self.local, '_ZODBMixin__connection')

    @property
    def __connection(self):
        if not self.__connected:
            self.log.debug('connecting ZODB')
            self.local._ZODBMixin__connection = self.__db.open()
        return self.local._ZODBMixin__connection

    @property
    def root_object(self):
        """The root object of the :meth:`storage`, connected and
        subsequently disconnected on-demand for each request."""
        return self.__connection.root()

    def __exit__(self, *exc_info):
        if self.__connected:
            self.log.debug('disconnecting ZODB')
            self.__connection.close()
        return super(ZODBMixin, self).__exit__(*exc_info)
