from setuptools import setup, find_packages

setup(name='Ramverk',
      packages=find_packages(),
      install_requires=['Werkzeug==dev', 'ZODB3', 'Genshi>=0.6'])
