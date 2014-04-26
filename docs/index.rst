.. cdl_convert documentation master file, created by
   sphinx-quickstart on Fri Apr 25 20:41:02 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cdl_convert's documentation
###########################

Contents:

.. toctree::
   :maxdepth: 2

   cdl_convert

Read Me Contents
================

|PyPI Version|\ |Build Status|\ |Coverage Status|\ |Code Health|

Introduction
------------

``cdl_convert`` converts between common `ASC CDL`_ formats. The `American Society of
Cinematographers`_ Color Decision List (ASC CDL, or CDL for short) is a
schema to simplify the process of interchanging color data between
various programs and facilities.

The ASC has defined schemas for including the 10 basic numbers in 5
different formats:

-  Avid Log Exchange (ALE)
-  Film Log EDL Exchange (FLEx)
-  CMX EDL
-  XML Color Correction (cc)
-  XML Color Correction Collection (ccc)

Unofficial Formats:

-  OCIOCDLTransform, a `Foundry Nuke`_ node
-  Space separated CDL, a Rhythm & Hues internal cdl format

It is the purpose of ``cdl_convert`` to convert ASC CDL information between
these basic formats to further facilitate the ease of exchange of color
data within the Film and TV industries.

**cdl_convert is not associated with the American Society of
Cinematographers**

Usage
-----

Most likely you'll use ``cdl_convert`` as a script, instead of a python package
itself (indeed, even the name is formatted more like a script (with an
underscore) than the more common all lowercase of python modules.

For usage as a python module, see the module documentation.

Script Usage
^^^^^^^^^^^^

If you just want to convert to a ``.cc`` XML file, the only required argument
is an input file, like so:::

    $ cdl_convert ./di_v001.flex

You can override the default ``.cc`` output, or provide multiple outputs with
the ``-o`` flag.::

    $ cdl_convert ./di_v001.flex -o cc,cdl

Sometimes it might be nessicary to disable cdl_convert's auto-detection of the
input file format. This can be done with the ``-i`` flag.::

    $ cdl_convert ./ca102_x34.cdl -i cdl -o cc

In this case, ``.cdl`` could have indicated either a space separated cdl, or an XML
cdl. ``cdl_convert`` does it's best to try and guess which one the file is, but
if you're running into trouble, it might help to indicate to ``cdl_convert``
what the input file type is.

Installation
------------

Installing is as simple as using pip:::

    $ pip install cdl_convert

If you don't want to bother with a pip style install, you can alternatively
grab `cdl_convert/cdl_convert.py`_, As this file is the script and all the
functions and classes needed.

GitHub, Bug Reporting and Support
---------------------------------

At ``cdl_convert``'s `GitHub`_ page you can browse the code and the history of
the project.

Builds can be downloaded from the GitHub page or the `PyPI`_ repository entry.

The `issues`_ page on GitHub is the best place to report bugs or request support,
and while ``cdl_convert`` is distributed with no warranty of any kind, issues
will be read and helped if able.

Frequently Asked Questions
--------------------------

- What versions of Python does ``cdl_convert`` support?
    ``cdl_convert`` works in Python 2.6 through 3.4, with a full test suite
    running continuous integration through `Travis-ci.org`_, coverage through
    `coveralls.io`_, and code quality checked with `landscape.io`_. **Code is**
    `PEP-8`_ **compliant**, with docstrings following `google code`_ docstring
    standards.

- Why don't you support format *X*?
    I either haven't had time to build a parser for the format yet, or I might
    even be unaware it exists. Perhaps you should drop by the `issues`_ page
    and create a request for the format? If creating a request for a format it
    helps immensely to have a sample of that format.

- Why are all the parsers and writers functions, instead of methods on the :class:`AscCdl` class?
    This seemed the current best approach for it's place in the script converter
    that forms a backbone of this project right now. It's very possible that in
    the future, :class:`AscCdl` will contain methods for converting its values to a
    string object ready for writing. It's unlikely that :class:`AscCdl` will contain
    methods for parsing, as different cdl formats can contain multiple cdls.

Contributing
------------

Samples
^^^^^^^

Please, *please*, **please** submit samples of the following formats:

- FLEx
- ALE
- CMX
- CCC

These are complex formats, and seeing real world samples helps write tests
that ensure correct parsing of real world EDLs and CDLs. If you don't even see
a format of CDL listed that you know exists, open an issue at the github
`issues`_ page asking for parse/write support for the format, and include a
sample.

Squashing Bugs
^^^^^^^^^^^^^^

Take a look at the `issues`_ page and if you see something that you think you
can bang out, leave a comment saying you're going to take it on. While many
issues are already assigned to the principal authors, just because it's assigned
doesn't mean any work has begun.

Submitting Code
^^^^^^^^^^^^^^^

Before generating a pull request, make sure to run the test suite:::

    $ python setup.py tests

If the tests fail, note which tests are failing, how they would have been
affected by your code. Always assume you broke something rather than that the
tests are 'wrong.' If you know you didn't break something, and the tests are
simply reporting out of date results based on your changes, *change the tests.*

If your code fails the tests (`Travis-ci.org`_ checks all pull requests when
you create them) it will be **rejected**. If the code style doesn't follow
PEP-8, it's not going to be a high priority for integration.

When submitting, you'll be asked to waive copyright to your submitted code to
the listed authors. This is so we can keep a tight handle on the code and change
the license for future releases if needed.

License
-------

    The MIT License (MIT)

    Copyright (c) 2014 Sean Wallitsch

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _ASC CDL: http://en.wikipedia.org/wiki/ASC_CDL
.. _American Society of Cinematographers: http://www.theasc.com/
.. _Foundry Nuke: http://www.thefoundry.co.uk/nuke/
.. _cdl_convert/cdl_convert.py: http://github.com/shidarin/cdl_convert/blob/master/cdl_convert/cdl_convert.py
.. _GitHub: http://github.com/shidarin/cdl_convert
.. _PyPI: http://pypi.python.org/pypi/cdl_convert
.. _issues: http://github.com/shidarin/cdl_convert/issues
.. _Travis-ci.org: http://travis-ci.org/shidarin/cdl_convert
.. _coveralls.io: http://coveralls.io/r/shidarin/cdl_convert
.. _PEP-8: http://legacy.python.org/dev/peps/pep-0008/
.. _google code: http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Comments
.. _landscape.io: http://landscape.io/

.. |PyPI Version| image:: https://badge.fury.io/py/cdl_convert.png
   :target: http://badge.fury.io/py/cdl_convert
.. |Build Status| image:: https://travis-ci.org/shidarin/cdl_convert.svg?branch=master
   :target: https://travis-ci.org/shidarin/cdl_convert
.. |Coverage Status| image:: https://coveralls.io/repos/shidarin/cdl_convert/badge.png?branch=master
   :target: https://coveralls.io/r/shidarin/cdl_convert?branch=master
.. |Code Health| image:: https://landscape.io/github/shidarin/cdl_convert/master/landscape.png
   :target: https://landscape.io/github/shidarin/cdl_convert/master