
CDL Convert
===========

|PyPI Version|\ |Build Status|\ |Coverage Status|\ |Code Health|

- **Author/Maintainer:** Sean Wallitsch
- **Email:** shidarin@alphamatte.com
- **License:** MIT
- **Status:** Development
- **Docs:** http://cdl-convert.readthedocs.org/
- **GitHub:** https://github.com/shidarin/cdl_convert
- **PyPI:** https://pypi.python.org/pypi/cdl_convert
- **Python Versions:** 2.6-3.4, PyPy

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
-  XML Color Decision List (cdl)

Unofficial Formats:

-  OCIOCDLTransform, a `Foundry Nuke`_ node
-  Space separated CDL, a Rhythm & Hues internal cdl format

It is the purpose of ``cdl_convert`` to convert ASC CDL information between
these basic formats to further facilitate the ease of exchange of color
data within the Film and TV industries.

``cdl_convert`` supports parsing ALE, FLEx, CC, CCC, CDL and RCDL. We can write
out CC, CCC, CDL and RCDL.

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


Changelog
---------

*New in version 0.6.1:*

- Added ``AscXMLBase`` class for nodes that can be represented by XML to inherit.
- Suppressed scientific notation from being written out when writing files. Should now write out as close as Python accuracy allows, and the same number of digits.
- ``write_cc`` now writes out 100% correct XML using ElementTree.
- Added tests for ``write_cc``, which **brings our coverage to 100%**

*New in version 0.6:*

- Adds much greater ASC CDL XML compliance with the addition of many classes that represent node concepts in the CDL XML schema.
- Moves ``viewing_desc`` and ``input_desc`` attributes and methods into the base class ``AscColorSpaceBase``.
- Moved ``desc`` attribute and methods into the base class ``AscDescBase``.
- Adds ``ColorCollectionBase`` class for a basis of all collection type nodes (``ColorCorrectionCollection`` , ``ColorDecisionList`` , etc).
- Adds ``MediaRef`` class which represents the MediaRef node of a ColorDecision. This class allows convenient handling of files given as media reference.
- Adds ``HALT_ON_ERROR`` module variable which determines certain exception handling behavior. Exceptions that can normally be handled with default behavior (such as negative Slope or Power values) will be dealt with silently instead of stopping the program. Negative Slope and Power values, for example, will clip to 0.0.
- ``ColorCorrection`` (formally ``AscCdl``) class changes:
    - Renames ``AscCdl`` to ``ColorCorrection`` .
    - Adds class level member dictionary, which allows lookup of a ``ColorCorrection`` instance by the unique ID.
    - ``ColorCorrection`` objects now require a unique ID to be instantiated.
    - Removes ``metadata`` attribute of ``ColorCorrection`` .
    - Moves SOP and SAT operations out of ``ColorCorrection`` into their own classes, which are based on ``ColorNodeBase`` . The ``SatNode`` and ``SopNode`` classes are still meant to be children of ``ColorCorrection``.
    - Added ``sop_node`` and ``sat_node`` attributes to access the child ``SatNode`` and ``SopNode`` .
    - Removed ``metadata`` attribute, splitting it into the inherited attributes of ``input_desc``, ``viewing_desc`` and ``desc``.
    - ``desc`` attribute is now fully fleshed out as a list of all encountered description fields.
    - Renamed ``cc_id`` field to ``id``, shadowing the built in ``id`` within the class.
    - Slope, Offset and Power now return as a tuple instead of a list to prevent index assignment, appending and extending.
- ``parse_cc`` should now parse a much greater variety of ``.cc`` files more accurately.
    - Now supports infinite Description fields
    - Now supports Viewing and Input Description fields
    - Significantly simplifies the function.
- ``parse_flex`` has been significantly simplified.
- Test Suite broken up into sub-modules.
- Adds PyPy support.
- Adds ReadTheDocs
- Adds docs to build

Installation
------------

Installing is as simple as using pip:::

    $ pip install cdl_convert

If you don't want to bother with a pip style install, you can alternatively
grab the entire `cdl_convert`_ directory, then set up a shortcut to call
``cdl_convert/cdl_convert.py``

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
    ``cdl_convert`` works in Python 2.6 through 3.4 and PyPy. A full test suite
    runs continuous integration through `Travis-ci.org`_, coverage through
    `coveralls.io`_, and code quality checked with `landscape.io`_. **Code is**
    :pep:`8` **compliant**, with docstrings following `google code`_ docstring
    standards.

- Why don't you support format *X*?
    I either haven't had time to build a parser for the format yet, or I might
    even be unaware it exists. Perhaps you should drop by the `issues`_ page
    and create a request for the format? If creating a request for a format it
    helps immensely to have a sample of that format.

- Why the underscore?
    ``cdl_convert`` started as a simple script to convert from one format to
    another. As such, it wasn't named with the standards that one would usually
    use for a python module. By the time the project became big enough, was on
    PyPI, etc, it was too spread out on the web, in too many places to make
    changing easy. In the end, I opted to keep it. At some point,
    ``cdl_convert`` might migrate into a larger, more generic film & tv
    python module, which will be named properly.

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

    $ python setup.py test

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

    | cdl_convert
    | Copyright (c) 2014 Sean Wallitsch
    | http://github.com/shidarin/cdl_convert/

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

.. _ASC CDL: http://en.wikipedia.org/wiki/ASC_CDL
.. _American Society of Cinematographers: http://www.theasc.com/
.. _Foundry Nuke: http://www.thefoundry.co.uk/nuke/
.. _cdl_convert: http://github.com/shidarin/cdl_convert/blob/master/cdl_convert/cdl_convert.py
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
