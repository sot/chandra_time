# Licensed under a 3-clause BSD style license - see LICENSE.rst
import platform
import sys

from setuptools import Extension, setup
from ska_helpers.setup_helper import duplicate_package_info
from testr.setup_helper import cmdclass

os_name = platform.system()
if os_name == "Windows":
    compile_args = ["/EHs", "/D_CRT_SECURE_NO_DEPRECATE"]
else:
    compile_args = [
        "-Wno-switch-enum",
        "-Wno-switch",
        "-Wno-switch-default",
        "-Wno-deprecated",
        "-Wno-parentheses",
    ]
if os_name == "Darwin":
    compile_args += ["-stdlib=libc++"]

extensions = [
    Extension(
        "chandra_time._axTime3",
        ["chandra_time/_axTime3.pyx"],
        extra_compile_args=compile_args,
    )
]

name = "chandra_time"
namespace = "Chandra.Time"

packages = ["chandra_time", "chandra_time.tests"]
package_dir = {name: name}

duplicate_package_info(packages, name, namespace)
duplicate_package_info(package_dir, name, namespace)

# Special case here to allow `python setup.py --version` to run without
# requiring cython and numpy to be installed.
if "--version" in sys.argv[1:]:
    ext_modules = None
else:
    from Cython.Build import cythonize
    ext_modules = cythonize(extensions, language_level="3")

setup(
    name=name,
    author="Tom Aldcroft",
    description="Convert between various time formats relevant to Chandra",
    author_email="taldcroft@cfa.harvard.edu",
    use_scm_version=True,
    setup_requires=["setuptools_scm", "setuptools_scm_git_archive"],
    zip_safe=False,
    packages=packages,
    package_dir=package_dir,
    ext_modules=ext_modules,
    tests_require=["pytest"],
    cmdclass=cmdclass,
)
