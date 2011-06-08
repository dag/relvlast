from __future__  import absolute_import
from transaction import manager


class TransactionMixin(object):
    """Add managed transactions for each request to an application."""

    def __enter__(self):
        self.log.debug('beginning transaction')
        manager.begin()
        return super(TransactionMixin, self).__enter__()

    def __exit__(self, *exc_info):
        if exc_info == (None, None, None) and not manager.isDoomed():
            self.log.debug('committing transaction')
            manager.commit()
        else:
            self.log.debug('aborting transaction')
            manager.abort()
        return super(TransactionMixin, self).__exit__(*exc_info)
