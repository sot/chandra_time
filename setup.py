# from distutils.core import setup, Extension
from setuptools import setup, Extension

import os
from Cython.Build import cythonize

if (os.name == "nt") :
    compile_args = ['/EHs','/D_CRT_SECURE_NO_DEPRECATE']
else:
    compile_args = ['-Wno-switch-enum', '-Wno-switch', '-Wno-switch-default',
                    '-Wno-deprecated', '-Wno-parentheses']

# (gcc_stdin, gcc_stdouterr) = os.popen4(['gcc','-v', '--help'])
# gcc_opt = gcc_stdouterr.read()
# if gcc_opt.find('fstack-protector') != -1:
#    compile_args.append('-fno-stack-protector')

# machine = Popen(['uname','--machine'], stdout=PIPE).communicate()[0]
# if machine.startswith('x86_64'):

# extensions = [Extension('Chandra._axTime3.pyx',
#                         sources=['Chandra/axTime3.cc',
#                                  'Chandra/XTime.cc']
#                         language='c++',
#                         extra_compile_args=compile_args),
#               ]

# ext_modules = cythonize('Chandra/axTime3.pyx',
#                         sources=['Chandra/axTime3.cc',
#                                  'Chandra/XTime.cc'],
#                         language='c++')

setup(ext_modules = cythonize("Chandra/_axTime3.pyx"))
# setup(ext_modules = cythonize("rect.pyx"))

if 0:
    setup(name='Chandra.Time',
      author = 'Tom Aldcroft',
      description='Convert between various time formats relevant to Chandra',
      author_email = 'taldcroft@cfa.harvard.edu',
      # py_modules = ['Chandra.axTime3', 'Chandra.Time'],
      version='1.16.1',
      zip_safe=False,
      test_suite = "Chandra.test_Time",
      namespace_packages=['Chandra'],
      packages=['Chandra'],
      package_dir={'Chandra' : 'Chandra'},
      ext_modules=ext_modules,
      )
