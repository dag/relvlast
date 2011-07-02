from __future__          import absolute_import
from attest              import Tests, assert_hook, raises
from fudge               import Fake
from werkzeug.test       import create_environ
from werkzeug.wrappers   import BaseResponse
from ramverk.application import BaseApplication
from ramverk.environment import BaseEnvironment
from ramverk.local       import UnboundContextError, get_current, current
from ramverk.rendering   import JSONMixin
from ramverk.transaction import TransactionMixin
from ramverk.utils       import super as _super
from ramverk.utils       import Bunch
from ramverk.utils       import EagerCachedProperties, ReprAttributes, has
from ramverk.utils       import InitFromArgs, args
from ramverk.wrappers    import DeferredResponseInitMixin
from tests               import mocking


unit = Tests()
mock = Tests(contexts=[mocking])


@unit.test
def unbound_contexts():
    with raises(UnboundContextError):
        get_current()
    with raises(UnboundContextError):
        current.application


@unit.test
def newstyle_super():

    class Base(object):
        def meth(self):
            return 'base'

    class FirstMixin(object):
        def meth(self):
            return _super().meth()

    class SecondMixin(object):
        def meth(self):
            return 'second mixin'

    class Multi(FirstMixin, SecondMixin, Base):
        pass

    assert Multi().meth() == 'second mixin'


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


@mock.test
def successful_transaction():

    class Env(TransactionMixin, BaseEnvironment):
        transaction_manager =\
            (Fake('TransactionManager')
            .remember_order()
            .expects('begin')
            .expects('isDoomed')
            .returns(False)
            .expects('commit'))

    with Env(BaseApplication(), create_environ()):
        pass


@mock.test
def failed_transaction():

    class Env(TransactionMixin, BaseEnvironment):
        transaction_manager =\
            (Fake('TransactionManager')
            .remember_order()
            .expects('begin')
            .expects('abort'))

    with raises(RuntimeError):
        with Env(BaseApplication(), create_environ()):
            raise RuntimeError


@mock.test
def doomed_transaction():

    class Env(TransactionMixin, BaseEnvironment):
        transaction_manager =\
            (Fake('TransactionManager')
            .remember_order()
            .expects('begin')
            .expects('isDoomed')
            .returns(True)
            .expects('abort'))

    with Env(BaseApplication(), create_environ()):
        pass


@unit.test
def deferred_response_init():

    class Response(DeferredResponseInitMixin, BaseResponse):
        pass

    response = Response('hello').using(status=404)
    assert response.data == 'hello' and response.status_code == 404

    response = Response(headers={'location': 'other-place'})
    response = response.using(headers={'Server': 'some-server'})
    assert response.headers['Location'] == 'other-place'
    assert response.headers['Server'] == 'some-server'

    assert Response().direct_passthrough == False
    assert Response().using().direct_passthrough == False
    response = Response().using(direct_passthrough=True)
    assert response.direct_passthrough == True

    assert Response('hello').using('hi').data == 'hi'
    assert Response('hello').using(['hi']).data == 'hi'

    response = Response(status=300).using(status='404 NOT FOUND')
    assert response.status_code == 404


@unit.test
def has_properties():

    @has(listing=list, mapping=dict)
    class DataModel(object):
        pass

    one, two = DataModel(), DataModel()
    assert isinstance(one.listing, list)
    assert isinstance(one.mapping, dict)
    assert not one.listing and not one.mapping
    assert one.listing is one.listing
    assert one.mapping is one.mapping
    assert one.listing is not two.listing
    assert one.mapping is not two.mapping


@unit.test
def eager_cached_properties():

    @has(listing=list)
    class LazyModel(object):
        pass

    @has(listing=list)
    class EagerModel(EagerCachedProperties):
        pass

    eager = EagerModel()
    lazy = LazyModel()

    assert 'listing' in vars(eager)
    assert 'listing' not in vars(lazy)


@unit.test
def attribute_repr():

    assert repr(ReprAttributes()) == '<ReprAttributes>'

    class Object(ReprAttributes):

        initial = 42

        class not_classes(object):
            pass

        def not_methods(self):
            pass

    instance = Object()
    instance.extra = 144

    assert repr(instance) in ('<Object initial=42, extra=144>',
                              '<Object extra=144, initial=42>')


@unit.test
def init_from_args():

    @args('x', 'y')
    class Point(InitFromArgs):
        pass

    assert vars(Point()) == dict(x=None, y=None)
    assert vars(Point(2)) == dict(x=2, y=None)
    assert vars(Point(2, 3)) == dict(x=2, y=3)
    assert vars(Point(2, y=3)) == dict(x=2, y=3)
    assert vars(Point(x=2, y=3)) == dict(x=2, y=3)
    assert vars(Point(y=3, x=2)) == dict(x=2, y=3)
    assert vars(Point(y=3)) == dict(x=None, y=3)

    @args('x', 'y')
    class CustomInit(InitFromArgs):

        def __create__(self):
            self.z = 3

    assert vars(CustomInit(1, 2)) == dict(x=1, y=2, z=3)
