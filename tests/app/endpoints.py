from werkzeug.utils import redirect


def index(self):

    if self.request.method == 'GET':
        return self.render('index.html', greeting=self.db.greeting)

    if self.request.method == 'POST':
        self.db.greeting = self.request.form.get('greeting')
        return redirect(self.path('index'))
