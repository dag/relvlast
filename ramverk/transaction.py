from __future__     import absolute_import
from transaction    import TransactionManager
from werkzeug.utils import cached_property


class TransactionMixin(object):
    """Environment mixin binding the request to a transaction."""

    @cached_property
    def transaction_manager(self):
        """The transaction manager to use for this request."""
        return TransactionManager()

    def __enter__(self):
        self.transaction_manager.begin()
        return super(TransactionMixin, self).__enter__()

    def __exit__(self, *exc_info):
        manager = self.transaction_manager
        if exc_info == (None, None, None) and not manager.isDoomed():
            manager.commit()
        else:
            manager.abort()
        return super(TransactionMixin, self).__exit__(*exc_info)
