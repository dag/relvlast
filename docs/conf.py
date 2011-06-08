project = 'Ramverk'
release = '0.0.0'
copyright = 'Dag Odenhall'

master_doc = 'index'
modindex_common_prefix = ['ramverk.']

html_style = 'rtd.css'
html_static_path = ['_static']

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.inheritance_diagram',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode']

autodoc_member_order = 'bysource'

inheritance_node_attrs = {'color': '"#465158"',
                          'fontcolor': 'white',
                          'fontsize': '13',
                          'style': '"rounded,filled"'}

intersphinx_mapping = {'python':   ('http://docs.python.org/', None),
                       'werkzeug': ('http://werkzeug.pocoo.org/docs/', None),
                       'logbook':  ('http://packages.python.org/Logbook/', None)}
