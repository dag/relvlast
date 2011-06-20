from __future__     import absolute_import
from ZODB.DB        import DB
from transaction    import manager
from werkzeug.utils import cached_property
from ramverk.utils  import request_property


class ZODBMixin(object):
    """Add automatic ZODB connection management to an application."""

    transaction_manager = manager  # if TransactionMixin isn't used
    """The :obj:`transaction manager <transaction.manager>` for this
    application. You should use this rather than the the transaction
    package, for example ``self.transaction_manager.doom()``."""

    @cached_property
    def _ZODBMixin__db(self):
        """The :class:`connection pool <ZODB.DB>`."""
        return DB(self.settings['storage']())

    @request_property
    def _ZODBMixin__connection(self):
        """On-demand per-request :class:`connection
        <ZODB.Connection.Connection>`."""
        if __debug__:
            self.log.debug('connecting ZODB')
        return self.__db.open(transaction_manager=self.transaction_manager)

    @property
    def persistent(self):
        """The root object of the storage, which is a
        :class:`~persistent.mapping.PersistentMapping` and behaves like a
        :class:`dict`."""
        return self.__connection.root()

    def __exit__(self, *exc_info):
        try:
            connection = self.local._ZODBMixin__connection
        except AttributeError:
            pass
        else:
            if __debug__:
                self.log.debug('disconnecting ZODB')
            connection.close()
            del self.local._ZODBMixin__connection
        return super(ZODBMixin, self).__exit__(*exc_info)
