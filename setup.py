# from distutils.core import setup, Extension
cvs_version= '$Id: setup.py,v 1.9 2007-07-31 01:09:08 aldcroft Exp $'; 

from subprocess import Popen, PIPE, STDOUT

compile_args = ['-O0']
gcc_opt = Popen(['gcc','-v', '--help'], stdout=PIPE, stderr=STDOUT).communicate()[0]
if gcc_opt.find('fstack-protector') != -1:
    compile_args.append('-fno-stack-protector')

# machine = Popen(['uname','--machine'], stdout=PIPE).communicate()[0]
# if machine.startswith('x86_64'):

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
                               extra_compile_args = compile_args,
                               )
                     ]
      )
