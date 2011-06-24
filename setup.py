from setuptools import setup, find_packages


setup(
    name='Ramverk',
    packages=find_packages(exclude=('deployments', 'tests')),

    install_requires=[
        'Babel',
        'Genshi',
        'Logbook',
        'Paver',
        'PyYAML',
        'Werkzeug',
        'ZODB3',
        'compactxml',
        'creoleparser',
        'pyScss',
        'venusian',
    ],

    entry_points = {
        'pygments.lexers': [
            'compactxml = ramverk.pygments:CompactXmlLexer',
            'compactxml+genshi = ramverk.pygments:CompactXmlGenshiLexer',
        ],
    },
)
