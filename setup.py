from setuptools import setup, Extension
from distutils.command.build import build
from shutil import copyfile
from os.path import exists

# Need custom build sequence to accomodate swig
class CustomBuild(build):
    def run(self):
        self.run_command('build_ext')
        copyfile('src/rtfir.py','rtfir.py')
        build.run(self)


# Assert manifest
if not exists('MANIFEST.in'):
    fd=open('MANIFEST.in','w')
    fd.write('include src/rtfir.hpp')
    fd.close()

# Try to compile binary extensions
try:
    setup(
        name='rtfir',
        version='1.1.3',
        ext_modules=[Extension('_rtfir',['src/rtfir.cpp','src/rtfir.i'],extra_compile_args=['-O2'],swig_opts=['-c++'])],
        py_modules=['rtfir'],
        author='Vegard Fiksdal',
        author_email='vegard@fiksdal.cc',
        description='Realtime FIR filteters',
        url='https://github.com/vfiksdal/rtfir',
        cmdclass={'build': CustomBuild}
    )

# Handle compilation failure
except SystemExit as e:
    # Inform user of fallback option
    print(str(e))
    print('')
    print('='*74)
    print('Compilation of binary extensions failed, please read the')
    print('error-information above and fix the problem. Alternatively you can')
    print('choose to install the pure-python fallback, but this will incur')
    print('a *massive* performance hit and will not be suitable for embedded')
    print('systems, big filters or large datasets.')
    print('='*74)

    # Get user confirmation
    print('\nDo you wish to install the pure python fallback (yes/no)?')
    process=False
    while not process:
        yes = {'yes','y', 'ye', ''}
        no = {'no','n'}
        choice = input().lower()
        if choice in yes:
            process=True
        elif choice in no:
            break
        else:
            print('Please respond with "yes" or "no"')

    # Process if user wants to
    if process:
        copyfile('src/rtfir_fallback.py','rtfir.py')
        setup(
            name='rtfir',
            version='1.1.3',
            py_modules=['rtfir'],
            author='Vegard Fiksdal',
            author_email='vegard@fiksdal.cc',
            description='Realtime FIR filteters',
            url='https://github.com/vfiksdal/rtfir'
        )
    else:
        exit(1)

