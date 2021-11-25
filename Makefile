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
	g++ -O2 cpptest.cpp rtfir.cpp -lm -o cpptest -Wno-psabi
	gcc -O2 ctest.c rtfir.c -lm -o ctest
	strip ctest cpptest
	./pytest.py --qa

clean:
	rm -rf *.so *.o *.png rtfir_wrap.* rtfir.py ctest cpptest 
	rm -rf __pycache__ build dist rtfir.egg-info MANIFEST.in
