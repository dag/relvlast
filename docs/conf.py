project = 'Ramverk'
release = '0.0.0'
copyright = 'Dag Odenhall'

master_doc = 'index'
modindex_common_prefix = ['ramverk.']

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.inheritance_diagram',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode']

autodoc_member_order = 'bysource'

inheritance_node_attrs = {'color': '"#465158"',
                          'fontcolor': 'white',
                          'fontsize': '13',
                          'style': '"rounded,filled"'}

intersphinx_mapping = {'python':   ('http://python.readthedocs.org/en/latest/', None),
                       'werkzeug': ('http://werkzeug.readthedocs.org/en/latest/', None),
                       'logbook':  ('http://log-book.readthedocs.org/en/latest/', None)}
