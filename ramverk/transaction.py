from __future__  import absolute_import
from transaction import manager


class TransactionMixin(object):
    """Add managed transactions for each request to an application."""

    def __enter__(self):
        if __debug__:
            self.log.debug('beginning transaction')
        manager.begin()
        return super(TransactionMixin, self).__enter__()

    def __exit__(self, *exc_info):
        if exc_info == (None, None, None) and not manager.isDoomed():
            if __debug__:
                self.log.debug('committing transaction')
            manager.commit()
        else:
            if __debug__:
                self.log.debug('aborting transaction')
            manager.abort()
        return super(TransactionMixin, self).__exit__(*exc_info)
