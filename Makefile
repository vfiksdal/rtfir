all: test-local

install:
	# Installing python package
	python3 setup.py build
	python3 setup.py install

test-system:
	# Build test programs
	g++ -O2 test/cpptest.cpp src/rtfir.cpp -lm -o test/cpptest -Wno-psabi
	gcc -O2 test/ctest.c src/rtfir.c -lm -o test/ctest
	rm -rf test/rtfir.py test/_rtfir.so

test-local: test-system
	# Build python module
	swig -python -c++ src/rtfir.i
	g++ -O2 -fPIC -c src/rtfir.cpp src/rtfir_wrap.cxx -Wno-psabi $(shell python3-config --includes)
	g++ -shared rtfir.o rtfir_wrap.o -o _rtfir.so
	cp src/rtfir.py .
	
	# Copy local files to test folder
	cp _rtfir.so rtfir.py test/

test: test-local

clean:
	rm -rf test/*.png test/ctest test/cpptest test/test.csv test/__pycache__
	rm -rf src/*.so src/*.o src/rtfir_wrap.* src/rtfir.py src/__pycache__
	rm -rf rtfir/ build dist rtfir.egg-info MANIFEST.in __pycache__
	rm -rf *.so *.o *.png rtfir.py rtfir_wrap.cxx

