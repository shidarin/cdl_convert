######################
cdl_convert Module Use
######################

AscCdl Class
============

The :class:`AscCdl` class is the backbone of cdl_convert. All the parse
functions exist to extract the CDL metadata and populate this class, and all
the write functions exist to write files out containing this data.

Parser --> :class:`AscCdl` --> Writer

.. automodule:: cdl_convert
   :members: AscCdl

Parse Functions
===============

These functions create and return one of more :class:`AscCdl`s, always returning
their results in the form of a list, even if the file type can only produce
a single cdl.

.. automodule:: cdl_convert
   :members: parse_ale, parse_cc, parse_cdl, parse_flex

Write Functions
===============

Each of these functions takes an :class:`AscCdl` as an arg, then places as many
attributes of the :class:`AscCdl` that the format supports into a properly
formatted string or XML Tree, then writes that file.

.. automodule:: cdl_convert
   :members: write_cc, write_cdl

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`