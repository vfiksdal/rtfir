all: python

python:
	swig -python -c++ rtfir.i
	g++ -O2 -fPIC -c rtfir.cpp rtfir_wrap.cxx -Wno-psabi $(shell python3-config --includes)
	g++ -shared rtfir.o rtfir_wrap.o -o _rtfir.so
	strip _rtfir.so

test: python
	g++ -O2 cpptest.cpp rtfir.cpp -lm -o cpptest -Wno-psabi
	gcc -O2 ctest.c rtfir.c -lm -o ctest
	strip ctest cpptest
	./pytest.py --qa

clean:
	rm -rf *.so *.o *.png rtfir_wrap.cxx rtfir.py ctest cpptest __pycache__
