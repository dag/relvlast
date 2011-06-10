project = 'Ramverk'
release = '0.0.0'
copyright = 'Dag Odenhall'

master_doc = 'index'
modindex_common_prefix = ['ramverk.']

templates_path = ['_templates']
html_static_path = ['_static']

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.inheritance_diagram',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode']

autodoc_member_order = 'bysource'

inheritance_graph_attrs = {'rankdir': 'RL'}

inheritance_node_attrs = {'color': '"#465158"',
                          'fontcolor': 'white',
                          'fontsize': '12',
                          'fontname': '"Ubuntu"',
                          'style': '"rounded,filled"'}

inheritance_edge_attrs = {'color': '"#444444"'}

intersphinx_mapping = {'python':   ('http://python.readthedocs.org/en/latest/', None),
                       'werkzeug': ('http://werkzeug.readthedocs.org/en/latest/', None),
                       'genshi':   ('http://genshi.readthedocs.org/en/latest/', None),
                       'zodb':     ('http://zodb.readthedocs.org/en/latest/', None),
                       'logbook':  ('http://log-book.readthedocs.org/en/latest/', None)}
