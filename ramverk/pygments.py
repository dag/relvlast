from __future__      import absolute_import
from pygments.lexer  import RegexLexer, DelegatingLexer, bygroups
from pygments.lexers import GenshiTextLexer
from pygments.token  import *


class CompactXmlLexer(RegexLexer):

    name = 'Compact XML'
    aliases = ['compactxml']
    filenames = []

    tokens = {
        'root': [
            (r'^\s+', Whitespace),
            (r'(["\'])(.+)', bygroups(Operator, Other)),
            (r'(\?)(\S+)(.+)',
                bygroups(Operator, Keyword.Declaration, Comment.Preproc)),
            (r'(<)(\S+)', bygroups(Operator, Name.Tag)),
            (r'(@)([^=]+)', bygroups(Operator, Name.Attribute)),
            (r'(=)(.+)', bygroups(Operator, Other)),
        ]
    }


class CompactXmlGenshiLexer(DelegatingLexer):

    name = 'Compact XML+Genshi'
    aliases = ['compactxml+genshi']

    def __init__(self, **options):
        super(CompactXmlGenshiLexer, self).__init__(
            GenshiTextLexer, CompactXmlLexer, **options)
