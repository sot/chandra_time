# from distutils.core import setup, Extension
cvs_version= '$Id: setup.py,v 1.7 2007-07-29 21:48:01 aldcroft Exp $'; 

from setuptools import setup, Extension
setup(name='Chandra.Time',
      author = 'Tom Aldcroft',
      description='Convert between various time formats relevant to Chandra',
      author_email = 'taldcroft@cfa.harvard.edu',
      py_modules = ['Chandra.axTime3', 'Chandra.Time'],
      version='1.5',

      test_suite = "Chandra.test_Time",

      packages=['Chandra'],
      package_dir={'Chandra' : 'Chandra'},
      ext_modules = [Extension('Chandra._axTime3',
                                ['Chandra/axTime3.cc',
                                 'Chandra/XTime.cc',
                                 'Chandra/axTime3.i',
                                 ],
                               swig_opts = ['-c++'],
                               language = 'c++',
                               )
                     ]
      )
