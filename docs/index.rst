.. cdl_convert documentation master file, created by
   sphinx-quickstart on Fri Apr 25 20:41:02 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cdl_convert
###########

Project Info
============

|PyPI Version|\ |Build Status|\ |Coverage Status|\ |Code Health|

- **Name:** cdl_convert
- **Version:** |release|
- **Author/Maintainer:** Sean Wallitsch
- **Email:** shidarin@alphamatte.com
- **License:** MIT
- **Status:** Development
- **Docs:** http://cdl-convert.readthedocs.org/
- **GitHub:** https://github.com/shidarin/cdl_convert
- **PyPI:** https://pypi.python.org/pypi/cdl_convert
- **Python Versions:** 2.7-3.4, PyPy

Introduction
============

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

The only requirement of ``cdl_convert`` is Pixar's `OpenTimelineIO`_ project
for reading EDLs. This dependency was added because OTIO does a much better
job of parsing EDLs than we do, so a much larger range of compatibility was
added.

**cdl_convert is not associated with the American Society of
Cinematographers**

Changelog
=========

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

- Added `--single` flag. When provided with an output collection format, each color correction in the input will be exported to it's own collection.
- Giving a :class:`ColorCorrection` a non-duplicate ID now works unless the ``--halt`` flag is given. This means that incoming collections that contain duplicate IDs will not fail out.

*New in version 0.7.1:*

- Fixed bug where ALE's without 'Scan Filename' fields could not parse correctly.

*New in version 0.7:*

The biggest change in 0.7 is the addition of collection format support.
``.ccc``, Color Correction Collections, can now be parsed and written. ``.cdl``,
Color Decision Lists, can now be parsed and written. ``.ale``
and ``.flex`` files now return a collection.

- New script flags:
    - Adds ``--check`` flag to script, which checks all parsed :class:`ColorCorrects` for sane values, and prints warnings to shell
    - Adds ``-d``, ``--destination`` flag to the script, which allows user to specify the output directory converted files will be written to.
    - Adds ``--no-ouput`` flag to the script, which goes through the entire conversion process but doesn't actually write anything to disk. Useful for troubleshooting, especially when combined with ``--check``
    - Adds ``--halt`` flag to the script, which halts on errors that can be resolved safely (such as negative slope or power values)
- Renames :class:`ColorCollectionBase` to :class:`ColorCollection` , since it will be used directly by both ``ccc`` and ``cdl``.
- Adds ``parse_ccc`` which returns a :class:`ColorCollection` .
- Adds ``write_ccc`` which writes a :class:`ColorCollection` as a ``ccc`` file.
- Adds ``parse_cdl`` which returns a :class:`ColorCollection` .
- Adds ``write_cdl`` which returns a :class:`ColorCollection` as a ``cdl`` file.
- :class:`ColorCollection` is now a fully functional container class, with many attributes and methods.
- Added :class:`ColorDecision` , which stores either a :class:`ColorCorrection` or :class:`ColorCorrectionRef` , and an optional :class:`MediaRef`
- Added :class:`ColorCorrectionRef` , which stores a reference to a :class:`ColorCorrection`
- Added ``parent`` attribute to :class:`ColorCorrection` .
- Calling ``sop_node`` or ``sat_node`` on a :class:`ColorCorrection` before attempting to set a SOP or Sat power now works.
- :class:`ColorCorrection` ``cdl_file`` init argument renamed to ``input_file``, which is now optional and able to be set after init.
- ``parse_cc`` and ``parse_rnh_cdl`` now only yield a single :class:`ColorCorrection` , not a single member list.
- Added dev-requirements.txt (contains ``mock``)
- All ``determine_dest`` methods now take a second ``directory`` argument, which determines the output directory.
- Adds ``sanity_check`` function which prints values which might be unusual to stdout.
- ``parse_cdl`` and ``write_cdl`` renamed to ``parse_rnh_cdl`` and ``write_rnh_cdl`` respectively.
- ``member_reset`` methods:
    - :class:`ColorCorrection` now has a ``reset_members`` method, which resets the class level member's dictionary.
    - :class:`MediaRef` also has a ``reset_members`` method, as does :class:`ColorCollection`
    - ``reset_all`` function calls all of the above ``reset_members`` methods at once.
- Renamed ``cdl_file`` argument:
    - ``parse_cc`` ``cdl_file`` arg renamed to ``input_file`` and now accepts a either a raw string or an ``ElementTree`` ``Element`` as ``input_file``.
    - ``parse_rnh_cdl`` ``cdl_file`` arg renamed to ``input_file``.
    - ``parse_ale`` ``edl_file`` arg renamed to ``input_file``.
    - ``parse_flex`` ``edl_file`` arg renamed to ``input_file``.
- Python Structure Refactoring
    - Moved ``HALT_ON_ERROR`` into the ``config`` module, which should now be referenced and set by importing the entire ``config`` module, and referencing or setting ``config.HALT_ON_ERROR``
    - Script functionality remains in ``cdl_convert.cdl_convert``, but everything else has been moved out.
    - :class:`AscColorSpaceBase` , :class:`AscDescBase` , :class:`AscXMLBase` and :class:`ColorNodeBase` now live under ``cdl_convert.base``
    - :class:`ColorCollection` now lives in ``cdl_convert.collection``
    - :class:`ColorCorrection` , :class:`SatNode` and :class:`SopNode` now live under ``cdl_convert.correction``
    - :class:`ColorDecision` , :class:`ColorCorrectionRef` and :class:`MediaRef` now live under ``cdl_convert.decision``
    - All parse functions now live under ``cdl_convert.parse``
    - All write functions now live under ``cdl_convert.write``
    - ``sanity_check`` now live under ``cdl_convert.utils``
    - ``reset_all`` now lives under the main module

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   usage
   usage_cc
   usage_ccc
   installation
   changelog
   support
   faq
   contributing
   license
   cdl_convert

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _ASC CDL: http://en.wikipedia.org/wiki/ASC_CDL
.. _American Society of Cinematographers: http://www.theasc.com/
.. _Foundry Nuke: http://www.thefoundry.co.uk/nuke/
.. _OpenTimelineIO: https://github.com/PixarAnimationStudios/OpenTimelineIO

.. |PyPI Version| image:: https://badge.fury.io/py/cdl_convert.png
   :target: http://badge.fury.io/py/cdl_convert
.. |Build Status| image:: https://travis-ci.org/shidarin/cdl_convert.svg?branch=master
   :target: https://travis-ci.org/shidarin/cdl_convert
.. |Coverage Status| image:: https://coveralls.io/repos/shidarin/cdl_convert/badge.png?branch=master
   :target: https://coveralls.io/r/shidarin/cdl_convert?branch=master
.. |Code Health| image:: https://landscape.io/github/shidarin/cdl_convert/master/landscape.png
   :target: https://landscape.io/github/shidarin/cdl_convert/master
