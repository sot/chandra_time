# from distutils.core import setup, Extension
from setuptools import setup, Extension

import os
from Cython.Build import cythonize
from Cython.Build.Dependencies import create_extension_list

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

ext_modules = create_extension_list(["Chandra/*.pyx"])

for module in ext_modules:
    module.extra_compile_args = compile_args

setup(name='Chandra.Time',
      author='Tom Aldcroft',
      description='Convert between various time formats relevant to Chandra',
      author_email='taldcroft@cfa.harvard.edu',
      py_modules=['Chandra.axTime3', 'Chandra.Time'],
      version='3.17.1',
      zip_safe=False,
      test_suite="Chandra.test_Time",
      namespace_packages=['Chandra'],
      packages=['Chandra'],
      package_dir={'Chandra' : 'Chandra'},
      ext_modules=cythonize(ext_modules),
      )
