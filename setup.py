#!/usr/bin/env python
#
# distutils script to build and install rtfir
# $ python3 setup.py build
# $ python3 setup.py install
#

from distutils.core import setup, Extension

setup(name='rtfir',
      version='1.1.0',
      description='Realtime FIR filters',
      long_description='Realtime FIR filters',
      license='GPLv3',
      author='Vegard Fiksdal',
      author_email='vegard@fiksdal.cc',
      url='https://github.com/vfiksdal/rtfir',
      ext_modules=[Extension('_rtfir',['rtfir.i','rtfir.cpp'],extra_compile_args=['-O2'],swig_opts=['-c++'])],
      py_modules=['rtfir']
)
