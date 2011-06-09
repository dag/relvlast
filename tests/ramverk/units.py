from __future__          import absolute_import
from attest              import Tests, assert_hook, raises
from fudge               import Fake, test
from ramverk.utils       import Bunch
from ramverk.application import BaseApplication
from ramverk.transaction import TransactionMixin


unit = Tests()


@unit.test
def bunch_attrs_and_items_are_same():

    bunch = Bunch(answer=42)
    assert bunch.answer is bunch['answer'] == 42

    del bunch.answer
    assert 'answer' not in bunch and not hasattr(bunch, 'answer')

    bunch.answer = 42
    assert bunch.answer is bunch['answer'] == 42

    del bunch['answer']
    assert 'answer' not in bunch and not hasattr(bunch, 'answer')


@unit.test
@test
def successful_transaction():

    class App(TransactionMixin, BaseApplication):
        transaction_manager =\
            (Fake('TransactionManager')
            .remember_order()
            .expects('begin')
            .expects('isDoomed')
            .returns(False)
            .expects('commit'))

    with App():
        pass


@unit.test
@test
def failed_transaction():

    class App(TransactionMixin, BaseApplication):
        transaction_manager =\
            (Fake('TransactionManager')
            .remember_order()
            .expects('begin')
            .expects('abort'))

    with raises(RuntimeError):
        with App():
            raise RuntimeError


@unit.test
@test
def doomed_transaction():

    class App(TransactionMixin, BaseApplication):
        transaction_manager =\
            (Fake('TransactionManager')
            .remember_order()
            .expects('begin')
            .expects('isDoomed')
            .returns(True)
            .expects('abort'))

    with App():
        pass
