all: python

python:
	swig -python -c++ rtfir.i
	g++ -fPIC -c rtfir.cpp rtfir_wrap.cxx -Wno-psabi $(shell python3-config --includes)
	g++ -shared rtfir.o rtfir_wrap.o -o _rtfir.so

test: python
	g++ test.cpp -o test

clean:
	rm -f *.so *.o *.png rtfir_wrap.cxx rtfir.py
