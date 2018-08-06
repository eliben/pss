#-------------------------------------------------------------------------------
# pss: setup.py
#
# Setup/installation script.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os, sys
try:
    from setuptools import setup
    use_setuptools = True
except ImportError:
    from distutils.core import setup
    use_setuptools = False

if use_setuptools:
    # Setuptools provides an "entry points" facility to automatically generate
    # scripts that work in the same way as the supplied "pss" script. This
    # feature is more portable to other platforms than providing a manually
    # created script, so we use that feature if it is available.
    # By using entry points, we get a "pss" shell script on Unix, and a
    # "pss.exe" command on Windows, without any extra effort.
    extra_args = {
        'entry_points': {
            'console_scripts': 'pss = psslib.pss:main'
        },
    }
else:
    # Setuptools is not available, so fall back to custom built scripts.
    extra_args = {
        'scripts': ['scripts/pss.py', 'scripts/pss'],
    }


try:
    with open('README.rst', 'rt') as readme:
        description = '\n' + readme.read()
except IOError:
    # maybe running setup.py from some other dir
    description = ''


setup(
    # metadata
    name='pss',
    description='Tool for grepping through source code',
    long_description=description,
    license='Public domain',
    version='1.42',
    author='Eli Bendersky',
    maintainer='Eli Bendersky',
    author_email='eliben@gmail.com',
    url='https://github.com/eliben/pss',
    platforms='Cross Platform',
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',],

    packages=['psslib', 'psslib.colorama'],

    **extra_args
)
