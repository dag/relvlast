from __future__    import absolute_import
from transaction   import TransactionManager
from ramverk.utils import request_property


class TransactionMixin(object):
    """Add managed transactions for each request to an application."""

    @request_property
    def transaction_manager(self):
        """Transaction manager to use, per default a request-bound
        :class:`~transaction.TransactionManager`."""
        # Because it is a @request_property we don't need to use
        # the thread-safe ThreadTransactionManager
        return TransactionManager()

    def __enter__(self):
        self.transaction_manager.begin()
        return super(TransactionMixin, self).__enter__()

    def __exit__(self, *exc_info):
        if exc_info == (None, None, None) and not self.transaction_manager.isDoomed():
            self.transaction_manager.commit()
        else:
            self.transaction_manager.abort()
        return super(TransactionMixin, self).__exit__(*exc_info)
