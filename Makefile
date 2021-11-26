all: python

python:
	swig -python -c++ rtfir.i
	g++ -O2 -fPIC -c rtfir.cpp rtfir_wrap.cxx -Wno-psabi $(shell python3-config --includes)
	g++ -shared rtfir.o rtfir_wrap.o -o _rtfir.so
	strip _rtfir.so

install: clean
	echo "include rtfir.hpp" > MANIFEST.in
	./setup.py build
	./setup.py install

test: python
	g++ -O2 test/cpptest.cpp rtfir.cpp -lm -o test/cpptest -Wno-psabi
	gcc -O2 test/ctest.c rtfir.c -lm -o test/ctest
	strip test/ctest test/cpptest

clean:
	rm -rf __pycache__ build dist rtfir.egg-info MANIFEST.in
	rm -rf test/*.png test/ctest test/cpptest test/test.csv
	rm -rf *.so *.o rtfir_wrap.* rtfir.py
