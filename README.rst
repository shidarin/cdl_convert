
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
- **Python Versions:** 2.7-3.5, PyPy & PyPy3

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

``cdl_convert`` supports parsing ALE, FLEx, CC, CCC, CDL CMX EDL and RCDL.
We can write out CC, CCC, CDL and RCDL.

The only requirement of ``cdl_convert`` is Pixar's `OpenTimelineIO`_ project
for reading EDLs. This dependency was added because OTIO does a much better
job of parsing EDLs than we do, so a much larger range of compatibility was
added.

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

*New in version 0.9.2:*

- Fixed a bug where ALE's with blank lines would not convert correctly.
- Fixed a bug that was preventing ``cdl_convert`` from being correctly installed in Python 2.6
- Fixed continuous integration testing.
- No longer officially supporting Python 3.2, as I've had to remove it from our CI builds. It should still work just fine though, but we won't be running CI against it.

*New in version 0.9:*

- Added ability to parse CMX EDLs
- Fixed a script bug where a collection format containing color decisions will not have those color decisions exported as individual color corrections.
- Fixed a bug where we weren't reading line endings correctly in certain situations.
- Added a cdl_convert.py stub file to the package root level, which will allow running of the cdl_convert script without installation. Due to relative imports in the python code, it was no longer possible to call cdl_convert/cdl_convert.py directly.
- The script, when run directly from cdl_convert.py, will now write errors to stderror correctly, and exit with a status of 1.

*New in version 0.8:*

- Added ``--single`` flag. When provided with an output collection format, each color correction in the input will be exported to it's own collection.
- Giving a ColorCorrection a non-duplicate ID now works unless the ``--halt`` flag is given. This means that incoming collections that contain duplicate IDs will not fail out.

*New in version 0.7.1:*

- Fixed bug where ALE's without 'Scan Filename' fields could not parse correctly.

*New in version 0.7:*

The biggest change in 0.7 is the addition of collection format support.
``.ccc``, Color Correction Collections, can now be parsed and written. ``.cdl``,
Color Decision Lists, can now be parsed and written. ``.ale``
and ``.flex`` files now return a collection.

- New script flags:
    - Adds ``--check`` flag to script, which checks all parsed `ColorCorrects` for sane values, and prints warnings to shell
    - Adds ``-d``, ``--destination`` flag to the script, which allows user to specify the output directory converted files will be written to.
    - Adds ``--no-ouput`` flag to the script, which goes through the entire conversion process but doesn't actually write anything to disk. Useful for troubleshooting, especially when combined with ``--check``
    - Adds ``--halt`` flag to the script, which halts on errors that can be resolved safely (such as negative slope or power values)
- Renames `ColorCollectionBase` to `ColorCollection` , since it will be used directly by both ``ccc`` and ``cdl``.
- Adds ``parse_ccc`` which returns a `ColorCollection` .
- Adds ``write_ccc`` which writes a `ColorCollection` as a ``ccc`` file.
- Adds ``parse_cdl`` which returns a `ColorCollection` .
- Adds ``write_cdl`` which returns a `ColorCollection` as a ``cdl`` file.
- `ColorCollection` is now a fully functional container class, with many attributes and methods.
- Added `ColorDecision` , which stores either a `ColorCorrection` or `ColorCorrectionRef` , and an optional `MediaRef`
- Added `ColorCorrectionRef` , which stores a reference to a `ColorCorrection`
- Added ``parent`` attribute to `ColorCorrection` .
- Calling ``sop_node`` or ``sat_node`` on a `ColorCorrection` before attempting to set a SOP or Sat power now works.
- `ColorCorrection` ``cdl_file`` init argument renamed to ``input_file``, which is now optional and able to be set after init.
- ``parse_cc`` and ``parse_rnh_cdl`` now only yield a single `ColorCorrection` , not a single member list.
- Added dev-requirements.txt (contains ``mock``)
- All ``determine_dest`` methods now take a second ``directory`` argument, which determines the output directory.
- Adds ``sanity_check`` function which prints values which might be unusual to stdout.
- ``parse_cdl`` and ``write_cdl`` renamed to ``parse_rnh_cdl`` and ``write_rnh_cdl`` respectively.
- ``member_reset`` methods:
    - `ColorCorrection` now has a ``reset_members`` method, which resets the class level member's dictionary.
    - `MediaRef` also has a ``reset_members`` method, as does `ColorCollection`
    - ``reset_all`` function calls all of the above ``reset_members`` methods at once.
- Renamed ``cdl_file`` argument:
    - ``parse_cc`` ``cdl_file`` arg renamed to ``input_file`` and now accepts a either a raw string or an ``ElementTree`` ``Element`` as ``input_file``.
    - ``parse_rnh_cdl`` ``cdl_file`` arg renamed to ``input_file``.
    - ``parse_ale`` ``edl_file`` arg renamed to ``input_file``.
    - ``parse_flex`` ``edl_file`` arg renamed to ``input_file``.
- Python Structure Refactoring
    - Moved ``HALT_ON_ERROR`` into the ``config`` module, which should now be referenced and set by importing the entire ``config`` module, and referencing or setting ``config.HALT_ON_ERROR``
    - Script functionality remains in ``cdl_convert.cdl_convert``, but everything else has been moved out.
    - `AscColorSpaceBase` , `AscDescBase` , `AscXMLBase` and `ColorNodeBase` now live under ``cdl_convert.base``
    - `ColorCollection` now lives in ``cdl_convert.collection``
    - `ColorCorrection` , `SatNode` and `SopNode` now live under ``cdl_convert.correction``
    - `ColorDecision` , `ColorCorrectionRef` and `MediaRef` now live under ``cdl_convert.decision``
    - All parse functions now live under ``cdl_convert.parse``
    - All write functions now live under ``cdl_convert.write``
    - ``sanity_check`` now live under ``cdl_convert.utils``
    - ``reset_all`` now lives under the main module

Installation
------------

Installing is as simple as using pip:::

    $ pip install cdl_convert --process-dependency-links

If you don't want to bother with a pip style install, you can alternatively
grab the entire `cdl_convert`_ directory, then set up a shortcut to call
``cdl_convert/cdl_convert.py``.

Note you will need to install `OpenTimelineIO`_ to parse EDLs.

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
    pep 8 **compliant**, with docstrings following `google code`_ docstring
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
    | Copyright (c) 2015 Sean Wallitsch
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
.. _OpenTimelineIO: https://github.com/PixarAnimationStudios/OpenTimelineIO

.. |PyPI Version| image:: https://badge.fury.io/py/cdl_convert.png
   :target: http://badge.fury.io/py/cdl_convert
.. |Build Status| image:: https://travis-ci.org/shidarin/cdl_convert.svg?branch=master
   :target: https://travis-ci.org/shidarin/cdl_convert
.. |Coverage Status| image:: https://coveralls.io/repos/shidarin/cdl_convert/badge.png?branch=master
   :target: https://coveralls.io/r/shidarin/cdl_convert?branch=master
.. |Code Health| image:: https://landscape.io/github/shidarin/cdl_convert/master/landscape.png
   :target: https://landscape.io/github/shidarin/cdl_convert/master
