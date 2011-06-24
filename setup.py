from setuptools import setup, find_packages


setup(
    name='Ramverk',
    packages=find_packages(exclude=('deployments', 'tests')),
    entry_points = {
        'pygments.lexers': [
            'compactxml = ramverk.pygments:CompactXmlLexer',
            'compactxml+genshi = ramverk.pygments:CompactXmlGenshiLexer',
        ],
    },
)
