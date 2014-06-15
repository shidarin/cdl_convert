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
- **Python Versions:** 2.6-3.4, PyPy

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
-  XML Color Decision List (cdl)
-  XML Color Correction Collection (ccc)

Unofficial Formats:

-  OCIOCDLTransform, a `Foundry Nuke`_ node
-  Space separated CDL, a Rhythm & Hues internal cdl format

It is the purpose of ``cdl_convert`` to convert ASC CDL information between
these basic formats to further facilitate the ease of exchange of color
data within the Film and TV industries.

**cdl_convert is not associated with the American Society of
Cinematographers**

Changelog
=========

*New in version 0.6.1:*

- Added :class:`AscXMLBase` class for nodes that can be represented by XML to inherit.
- Suppressed scientific notation from being written out when writing files. Should now write out as close as Python accuracy allows, and the same number of digits.
- ``write_cc`` now writes out 100% correct XML using ElementTree.
- Added tests for ``write_cc``, which **brings our coverage to 100%**

*New in version 0.6:*

- Adds much greater ASC CDL XML compliance with the addition of many classes that represent node concepts in the CDL XML schema.
- Moves ``viewing_desc`` and ``input_desc`` attributes and methods into the base class :class:`AscColorSpaceBase` .
- Moved ``desc`` attribute and methods into the base class :class:`AscDescBase` .
- Adds :class:`ColorCollectionBase` class for a basis of all collection type nodes (:class:`ColorCorrectionCollection` , :class:`ColorDecisionList` , etc).
- Adds :class:`MediaRef` class which represents the MediaRef node of a ColorDecision. This class allows convenient handling of files given as media reference.
- Adds ``HALT_ON_ERROR`` module variable which determines certain exception handling behavior. Exceptions that can normally be handled with default behavior (such as negative Slope or Power values) will be dealt with silently instead of stopping the program. Negative Slope and Power values, for example, will clip to 0.0.
- :class:`ColorCorrection` (formally :class:`AscCdl`) class changes:
    - Renames :class:`AscCdl` to :class:`ColorCorrection` .
    - Adds class level member dictionary, which allows lookup of a :class:`ColorCorrection` instance by the unique ID.
    - :class:`ColorCorrection` objects now require a unique ID to be instantiated.
    - Removes ``metadata`` attribute of :class:`ColorCorrection` .
    - Moves SOP and SAT operations out of :class:`ColorCorrection` into their own classes, which are based on :class:`ColorNodeBase` . The :class:`SatNode` and :class:`SopNode` classes are still meant to be children of :class:`ColorCorrection`.
    - Added ``sop_node`` and ``sat_node`` attributes to access the child :class:`SatNode` and :class:`SopNode` .
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

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   usage
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

.. |PyPI Version| image:: https://badge.fury.io/py/cdl_convert.png
   :target: http://badge.fury.io/py/cdl_convert
.. |Build Status| image:: https://travis-ci.org/shidarin/cdl_convert.svg?branch=master
   :target: https://travis-ci.org/shidarin/cdl_convert
.. |Coverage Status| image:: https://coveralls.io/repos/shidarin/cdl_convert/badge.png?branch=master
   :target: https://coveralls.io/r/shidarin/cdl_convert?branch=master
.. |Code Health| image:: https://landscape.io/github/shidarin/cdl_convert/master/landscape.png
   :target: https://landscape.io/github/shidarin/cdl_convert/master
