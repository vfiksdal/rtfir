#!/usr/bin/env python3
#
# distutils script to build and install rtfir
# $ python3 setup.py build
# $ python3 setup.py install
#
from setuptools import setup,Extension

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='rtfir',
    version='1.1.1',
    ext_modules=[Extension('_rtfir',['rtfir.i','rtfir.cpp'],extra_compile_args=['-O2'],swig_opts=['-c++'])],
    headers=['rtfir.hpp'],
    scripts=['rtfir.py'],
    author='Vegard Fiksdal',
    author_email='vegard@fiksdal.cc',
    description='Realtime FIR filteters',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vfiksdal/rtfir'
)

