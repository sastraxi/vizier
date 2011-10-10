from distutils.core import setup

setup(
    name='vizier',
    version='1.2dev',
    packages=['vizier', 'vizier.handlers', 'vizier.book'],
    requires=['cairo',],
    license='GNU LGPL 2.1',
    url='https://github.com/sastraxi/vizier',
    long_description=open('README.rst').read(),
)
