Introduction: what is pss?
--------------------------

**pss** is a power-tool for searching inside source code files. **pss**
searches recursively within a directory tree, knows which extensions and
file names to search and which to ignore, automatically skips directories
you wouldn't want to search in (for example ``.svn`` or ``.git``), colors
its output in a helpful way, and does much more.

If you're familiar with the **ack** tool, then you will find **pss** very
similar (see https://github.com/eliben/pss/wiki/pss-and-ack).

Pre-requisites
--------------

**pss** needs only Python to run. It works with Python versions 2.6, 2.7 and
3.2+ on Linux and Windows. Some testing was done on Mac OS X and FreeBSD as
well.

Installing
----------

**pss** can be installed from PyPi (Python package index)::

    > pip install pss

Alternatively, you can download the source distribution either from PyPi or
from the main Github project page. When you unzip the source distribution, run::

    > python setup.py install

Running without installing
--------------------------

**pss** supports direct invocation even without installing it. This may
be useful if you're on a machine without administrator rights, or want to
experiment with a source distribution of **pss**.

Just unzip the **pss** distribution into some directory. Let's assume its full
path is ``/path/to/pss``. You can now run::

    > /path/to/python /path/to/pss

And this will invoke **pss** as expected. This command can also be tied to an
alias or placed in a shell (or batch) script for convenience.

How to use it?
--------------

**pss** is meant to be executed from the command line. Running it with no
arguments or with ``-h`` will print a detailed usage message.

For some detailed usage examples, check out the
Usage wiki page - https://github.com/eliben/pss/wiki/Usage-samples

License
-------

**pss** is open-source software. Its code is in the public domain. See the
``LICENSE`` file for more details.

CI Status
---------

**pss** has automatic testing enabled through the convenient
`Travis CI project <https://travis-ci.org>`_. Here is the latest build status:

.. image:: https://travis-ci.org/eliben/pss.png?branch=master
  :align: center
  :target: https://travis-ci.org/eliben/pss
