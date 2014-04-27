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
- **Python Versions:** 2.6-3.4

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

Unofficial Formats:

-  OCIOCDLTransform, a `Foundry Nuke`_ node
-  Space separated CDL, a Rhythm & Hues internal cdl format

It is the purpose of ``cdl_convert`` to convert ASC CDL information between
these basic formats to further facilitate the ease of exchange of color
data within the Film and TV industries.

**cdl_convert is not associated with the American Society of
Cinematographers**

.. warning::
    ``cdl_convert`` is still in active development and the API is changing
    rapidly. Not all features work correctly in every instance. The best thing
    you can do to help this is to :doc:`contribute </contributing>` and get
    through this period the quickest.

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   usage
   installation
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
