project = 'Ramverk'
release = '0.0.0'
copyright = 'Dag Odenhall'

needs_sphinx = '1.1'
master_doc = 'index'
modindex_common_prefix = ['ramverk.']

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode']

autodoc_member_order = 'bysource'

intersphinx_mapping = {'python':   ('http://docs.python.org/', None),
                       'werkzeug': ('http://werkzeug.pocoo.org/docs/', None),
                       'logbook':  ('http://packages.python.org/Logbook/', None)}