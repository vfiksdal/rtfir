all: test-local

setuptools:
	# Create python setup environment
	@echo "include src/rtfir.hpp" > MANIFEST.in
	@echo "from setuptools import setup, Extension" > setup.py
	@echo "from distutils.command.build import build" >> setup.py
	@echo "from shutil import copyfile" >> setup.py
	@echo "" >> setup.py
	@echo "class CustomBuild(build):" >> setup.py
	@echo "    def run(self):" >> setup.py
	@echo "        self.run_command('build_ext')" >> setup.py
	@echo "        copyfile('src/rtfir.py','rtfir.py')" >> setup.py
	@echo "        build.run(self)" >> setup.py
	@echo "" >> setup.py
	@echo "setup(" >> setup.py
	@echo "    name='rtfir'," >> setup.py
	@echo "    version='1.1.2'," >> setup.py
	@echo "    ext_modules=[Extension('_rtfir',['src/rtfir.cpp','src/rtfir.i'],extra_compile_args=['-O2'],swig_opts=['-c++'])]," >> setup.py
	@echo "    py_modules=['rtfir']," >> setup.py
	@echo "    author='Vegard Fiksdal'," >> setup.py
	@echo "    author_email='vegard@fiksdal.cc'," >> setup.py
	@echo "    description='Realtime FIR filteters'," >> setup.py
	@echo "    url='https://github.com/vfiksdal/rtfir'," >> setup.py
	@echo "    cmdclass={'build': CustomBuild}" >> setup.py
	@echo ")" >> setup.py

install: setuptools
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
	rm -rf *.so *.o *.png rtfir.py setup.py

