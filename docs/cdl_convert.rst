#############
API Reference
#############

.. note::
    All code for the following lives under cdl_convert.cdl_convert, and is
    imported into the local space of cdl_convert.

Base Class
==========

The :class:`AscCdl` class is the backbone of cdl_convert. All the parse
functions exist to extract the CDL metadata and populate this class, and all
the write functions exist to write files out from this class.

Parser --> :class:`AscCdl` --> Writer

:class:`AscCdl` can of course be instantiated and used without a parse function,
see :doc:`usage` for a walkthrough.

AscCdl
------

.. autoclass:: cdl_convert.AscCdl

Parse Functions
===============

These functions create and return one of more :class:`AscCdl`, always returning
their results in the form of a list, even if the file type can only produce
a single cdl.

Parse ale
---------

.. autofunction:: cdl_convert.parse_ale

Parse cc
---------

.. autofunction:: cdl_convert.parse_cc

Parse cdl
---------

.. autofunction:: cdl_convert.parse_cdl

Parse flex
----------

.. autofunction:: cdl_convert.parse_flex

Write Functions
===============

Each of these functions takes an :class:`AscCdl` as an arg, then places as many
attributes of the :class:`AscCdl` that the format supports into a properly
formatted string or XML Tree, then writes that file.

Write cc
--------

.. autofunction:: cdl_convert.write_cc

Write cdl
---------

.. autofunction:: cdl_convert.write_cdl

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
