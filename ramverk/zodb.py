from ZODB.DB        import DB
from werkzeug.utils import cached_property


class ZODBMixin(object):
    """Add ZODB persistence to an application."""

    # In case we're not using TransactionMixin;
    # None gets us the default thread-bound manager.
    transaction_manager = None

    @cached_property
    def __db(self):
        """The connection pool."""
        return DB(self.settings['storage']())

    @property
    def __connected(self):
        """Whether ZODB has connected yet during the current request."""
        return hasattr(self.local, '_ZODBMixin__connection')

    @property
    def __connection(self):
        """On-demand per-request connection."""
        if not self.__connected:
            if __debug__:
                self.log.debug('connecting ZODB')
            self.local._ZODBMixin__connection = self.__db.open(
                    transaction_manager=self.transaction_manager)
        return self.local._ZODBMixin__connection

    @property
    def root_object(self):
        """The root object of the storage, connected and subsequently
        disconnected on-demand for each request."""
        return self.__connection.root()

    def __exit__(self, *exc_info):
        if self.__connected:
            if __debug__:
                self.log.debug('disconnecting ZODB')
            self.__connection.close()
            del self.local._ZODBMixin__connection
        return super(ZODBMixin, self).__exit__(*exc_info)
