from ZODB.DB        import DB
from transaction    import manager
from werkzeug.utils import cached_property


class TransactionMixin(object):
    """Add managed transactions for each request to an application."""

    def __exit__(self, *exc_info):
        if exc_info == (None, None, None):
            self.log.debug('committing transaction')
            manager.commit()
        else:
            self.log.debug('aborting transaction')
            manager.abort()
        return super(TransactionMixin, self).__exit__(*exc_info)


class ZODBMixin(object):
    """Add ZODB persistence to an application."""

    #: Set to the storage for ZODB.
    storage = None

    @cached_property
    def __db(self):
        if self.storage is None:
            raise ValueError('"storage" must not be None')
        return DB(self.storage)

    @property
    def __connected(self):
        return hasattr(self.local, '_ZODBMixin__connection')

    @property
    def __connection(self):
        if not self.__connected:
            self.log.debug('connecting ZODB')
            self.local._ZODBMixin__connection = self.__db.open()
            self.log.debug('beginning transaction')
            manager.begin()
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
