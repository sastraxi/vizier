from distutils.core import setup
import vizier

setup(
    author='Cameron Gorrie',
    author_email='sastraxi@gmail.com',
    name='vizier',
    version=vizier.__version__,
    packages=['vizier'],
    requires=['cairo',],
    license='GNU LGPL 2.1',
    url='https://github.com/sastraxi/vizier',
    long_description=open('README.rst').read(),
)
