from distutils.core import setup

setup(
    name='cairoplot-bsm',
    version='1.2dev',
    packages=['cairoplot',],
    requires=['cairo',],
    license='GNU LGPL 2.1',
    url='https://github.com/sastraxi/cairoplot-bsm',
    long_description=open('README.txt').read(),
)
