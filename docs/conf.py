project = 'Ramverk'
release = '0.0.0'
copyright = 'Dag Odenhall'

master_doc = 'index'
modindex_common_prefix = ['ramverk.']

templates_path = ['_templates']
html_static_path = ['_static']

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.graphviz',
              'sphinx.ext.inheritance_diagram',
              'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode']

autodoc_member_order = 'bysource'

graphviz_dot_args = ['-Gsize=8.0,12.0',
                     '-Ncolor=#465158',
                     '-Nfontcolor=white',
                     '-Nfontsize=12',
                     '-Nfontname=Ubuntu',
                     '-Nstyle=rounded,filled,setlinewidth(0.5)',
                     '-Nshape=box',
                     '-Nheight=0.25',
                     '-Earrowsize=0.5',
                     '-Estyle=setlinewidth(0.5)',
                     '-Ecolor=#444444']

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
