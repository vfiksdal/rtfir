# Generate version data for python module to track versions
VERSION=1.1.2
REVISION=0x$(shell git rev-parse --short HEAD || echo 0)
ABOUT_VERSION=RTFIR $(VERSION)
ABOUT_DATE=Compiled on $(shell date)
#ABOUT_ME=Vegard Fiksdal(C)2021
ifneq ($(REVISION),0)
    ABOUT_VERSION=RTFIR $(VERSION) [$(REVISION)]
endif
ABOUT=-DABOUT="\"$(ABOUT_VERSION)\n$(ABOUT_DATE)\n$(ABOUT_ME)\""

all: python

setuptools: python
	# Create python setup environment
	@echo "include src/rtfir.hpp" > MANIFEST.in
	@echo "from setuptools import setup,Extension" > setup.py
	@echo "" >> setup.py
	@echo "with open('README.md', 'r') as fh:" >> setup.py
	@echo "    long_description = fh.read()" >> setup.py
	@echo "" >> setup.py
	@echo "setup(" >> setup.py
	@echo "    name='rtfir'," >> setup.py
	@echo "    version='$(VERSION)'," >> setup.py
	@echo "    ext_modules=[Extension('_rtfir',['src/rtfir.i','src/rtfir.cpp'],extra_compile_args=['-O2','$(ABOUT)'],swig_opts=['-c++'])]," >> setup.py
	@echo "    packages=['rtfir']," >> setup.py
	@echo "    author='Vegard Fiksdal'," >> setup.py
	@echo "    author_email='vegard@fiksdal.cc'," >> setup.py
	@echo "    description='Realtime FIR filteters'," >> setup.py
	@echo "    long_description=long_description," >> setup.py
	@echo "    long_description_content_type='text/markdown'," >> setup.py
	@echo "    url='https://github.com/vfiksdal/rtfir'" >> setup.py
	@echo ")" >> setup.py
	
	# Stage package
	rm -rf rtfir
	mkdir -p rtfir
	echo "__version__ = \"$(VERSION)\"" > rtfir/__init__.py
	cp src/rtfir.py rtfir/

install: setuptools
	# Installing python package
	python3 setup.py build
	python3 setup.py install

python:
	# Build python module
	swig $(ABOUT) -python -c++ src/rtfir.i
	g++ -O2 -fPIC $(ABOUT) -c src/rtfir.cpp src/rtfir_wrap.cxx -Wno-psabi $(shell python3-config --includes)
	g++ -shared rtfir.o rtfir_wrap.o -o _rtfir.so
	cp src/rtfir.py .

test-system:
	# Build test programs
	g++ -O2 test/cpptest.cpp src/rtfir.cpp -lm -o test/cpptest -Wno-psabi
	gcc -O2 test/ctest.c src/rtfir.c -lm -o test/ctest
	rm -rf test/rtfir.py test/_rtfir.so

test-local: test-system python
	# Copy local files to test folder
	cp _rtfir.so rtfir.py test/

test: test-local

clean:
	rm -rf test/*.png test/ctest test/cpptest test/test.csv test/__pycache__
	rm -rf src/*.so src/*.o src/rtfir_wrap.* src/rtfir.py src/__pycache__
	rm -rf rtfir/ build dist rtfir.egg-info MANIFEST.in __pycache__
	rm -rf *.so *.o *.png rtfir.py setup.py

