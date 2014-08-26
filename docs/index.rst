Saratoga Documentation
======================

.. image:: https://travis-ci.org/hawkowl/saratoga.png?branch=master
.. image:: https://coveralls.io/repos/hawkowl/saratoga/badge.png?branch=master

Saratoga is a framework for easily creating APIs.
It uses Python and Twisted, and supports both CPython 2.7 and PyPy.

Saratoga revolves around versions - it is designed so that you can write code for new versions of your API without disturbing old ones.
You simply expand the scope of the unchanged methods, and copy a reference into your new version.

You can get the MIT-licensed code on `GitHub <https://github.com/hawkowl/saratoga>`_, or download it from `PyPI <https://pypi.python.org/pypi/saratoga>`_.


Introduction
------------

A look at Saratoga, starting from the ground up.

.. toctree::
   :maxdepth: 2

   intro
   serviceclasses
   paramschecking
   authentication


Specifications
--------------

This specifies the Saratoga API definition format.

.. toctree::
   apidescription
