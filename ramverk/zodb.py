from __future__     import absolute_import
from ZODB.DB        import DB
from transaction    import manager
from werkzeug.utils import cached_property


class ZODBEnvironmentMixin(object):
    """Environment mixin connecting the configured ZODB
    :attr:`~ZODBMixin.settings.storage` on-demand."""

    transaction_manager = manager

    _zodb_connected = False

    @cached_property
    def _zodb_connection(self):
        if __debug__:
            self.application.log.debug('connecting ZODB')
        self._zodb_connected = True
        return self.application._zodb_connection_pool.open(
            transaction_manager=self.transaction_manager)

    def __exit__(self, *exc_info):
        if self._zodb_connected:
            if __debug__:
                self.application.log.debug('disconnecting ZODB')
            self._zodb_connection.close()
        return super(ZODBEnvironmentMixin, self).__exit__(*exc_info)

    @property
    def persistent(self):
        """The root :class:`~persistent.mapping.PersistentMapping` of the
        storage."""
        return self._zodb_connection.root()


class ZODBMixin(object):
    """Application mixin adding a ZODB connection pool for use with
    :class:`ZODBEnvironmentMixin`."""

    @cached_property
    def _zodb_connection_pool(self):
        return DB(self.settings.storage())
