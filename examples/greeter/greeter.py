from persistent      import Persistent
from ramverk         import fullstack
from ramverk.routing import get, post
from werkzeug.utils  import cached_property


class Root(Persistent):

    greeting = 'Hello'


class Environment(fullstack.Environment):

    @cached_property
    def db(self):
        return self.persistent.setdefault('greeter', Root())


@get('/')
def greet_visitor(render, db):
    return render('index.html', greeting=db.greeting)


@post('/')
def set_greeting(db, request, redirect):
    db.greeting = request.form['greeting']
    return redirect(':greet_visitor')


class Greeter(fullstack.Application):

    environment = Environment

    def configure(self):
        self.scan()
