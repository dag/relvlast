from __future__     import absolute_import
from transaction    import TransactionManager
from werkzeug.utils import cached_property


class TransactionalMixinBase(object):
    """Base class for transactional environment mixins."""

    @cached_property
    def transaction_manager(self):
        """The transaction manager to use for this request."""
        return TransactionManager()

    @property
    def transaction(self):
        """The current transaction."""
        return self.transaction_manager.get()


class TransactionMixin(TransactionalMixinBase):
    """Environment mixin binding the request to a transaction."""

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


from ramverk.inventory import members
__all__ = members[__name__]
