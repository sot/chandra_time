from setuptools import setup, Extension

import os
from Cython.Build import cythonize

if (os.name == "nt"):
    compile_args = ['/EHs', '/D_CRT_SECURE_NO_DEPRECATE']
else:
    compile_args = ['-Wno-switch-enum', '-Wno-switch', '-Wno-switch-default',
                    '-Wno-deprecated', '-Wno-parentheses']

extensions = [Extension("*", ["Chandra/_axTime3.pyx"],
                        extra_compile_args=compile_args)]

setup(name='Chandra.Time',
      author='Tom Aldcroft',
      description='Convert between various time formats relevant to Chandra',
      author_email='taldcroft@cfa.harvard.edu',
      py_modules=['Chandra.axTime3', 'Chandra.Time'],
      version='3.20.0',
      zip_safe=False,
      test_suite="Chandra.test_Time",
      packages=['Chandra'],
      package_dir={'Chandra': 'Chandra'},
      ext_modules=cythonize(extensions),
      )
