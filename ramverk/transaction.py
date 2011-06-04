from __future__  import absolute_import
from transaction import manager


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
