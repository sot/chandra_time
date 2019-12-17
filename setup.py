# Licensed under a 3-clause BSD style license - see LICENSE.rst
from setuptools import setup, Extension

import os
from Cython.Build import cythonize

if (os.name == "nt"):
    compile_args = ['/EHs', '/D_CRT_SECURE_NO_DEPRECATE']
else:
    compile_args = ['-Wno-switch-enum', '-Wno-switch', '-Wno-switch-default',
                    '-Wno-deprecated', '-Wno-parentheses', '-stdlib=libc++']

extensions = [Extension("*", ["Chandra/Time/_axTime3.pyx"],
                        extra_compile_args=compile_args)]

try:
    from testr.setup_helper import cmdclass
except ImportError:
    cmdclass = {}

setup(name='Chandra.Time',
      author='Tom Aldcroft',
      description='Convert between various time formats relevant to Chandra',
      author_email='taldcroft@cfa.harvard.edu',
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      zip_safe=False,
      packages=['Chandra', 'Chandra.Time', 'Chandra.Time.tests'],
      ext_modules=cythonize(extensions),
      tests_require=['pytest'],
      cmdclass=cmdclass,
      )
