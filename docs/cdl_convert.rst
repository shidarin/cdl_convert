#############
API Reference
#############

.. note::
    All code for the following lives under cdl_convert.cdl_convert, and is
    imported into the local space of cdl_convert.

Classes
=======

The class structure of ``cdl_convert`` mirrors the element structure of the
defined XML schema for ``ccc``, ``cdl`` and ``cc`` files as defined by the
ASC. The XML schema's represent the most complicated and structured variant of
the format, and therefore it behooves the project to mimic their structure.

However, where similar elements exist as entirely separate entities in the XML
schema, they might have been combined here.

ColorCollectionBase
-------------------

:class:`ColorDecisionList` and :class:`ColorCollection` use this class as a
a base class, since they both are collections of other more specific classes.

.. autoclass:: cdl_convert.ColorCollectionBase

ColorCorrection
---------------

The :class:`ColorCorrection` class is the backbone of cdl_convert, as it
represents the basic level of the color decision list concept- the color
decision list itself. All the parse functions exist to extract the CDL metadata
and populate this class, and all the write functions exist to write files out
from this class.

Parser --> :class:`ColorCorrection` --> Writer

:class:`ColorCorrection` can of course be instantiated and used without a parse
function, see :doc:`usage` for a walkthrough.

.. warning::
    When an instance of :class:`ColorCorrection` is first created, the ``id``
    provided is checked against a class level dictionary variable named
    ``members`` to ensure that no two :class:`ColorCorrection` share the same
    ``id`` , as this is required by the specification.

.. warning::
    ``cdl_file`` is likely to not be a required attribute in the future.

.. autoclass:: cdl_convert.ColorCorrection

ColorNodeBase
-------------

The base node for the SAT and SOP values is a little different than the base
nodes for the ColorCorrect classes, as SAT and SOP nodes cannot contain any
fields except ``description``. Like the other nodes however, they can contain
an infinite amount of descriptions.

This class only exists to be subclassed by :class:`SatNode` and :class:`SopNode`
and thus should never be used directly.

.. warning::
    Node that setting the ``desc`` attribute directly using a traditional method
    of ``cnb.desc = 'Bob walked into the room'`` will result it that string
    being appended into the list returned when calling ``desc``.

.. autoclass:: cdl_convert.ColorNodeBase

SatNode
-------

.. note::
    This class is meant only to be created by a container CDL format, and thus has
    the required arg of ``parent`` when instantiating it.

.. autoclass:: cdl_convert.SatNode

SopNode
-------

.. note::
    This class is meant only to be created by a container CDL format, and thus has
    the required arg of ``parent`` when instantiating it.

.. warning::
    Setting any of the sop node values with a single value as in
    ``offset = 5.4`` will cause that value to be copied over all 3 colors,
    resulting in ``[5.4, 5.4, 5.4]``.

.. autoclass:: cdl_convert.SopNode

Parse Functions
===============

These functions create and return one of more :class:`ColorCorrection`, always
returning their results in the form of a list, even if the file type can only
produce a single cdl.

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

Each of these functions takes an :class:`ColorCorrection` as an arg, then places
as many attributes of the :class:`ColorCorrection` that the format supports
into a properly   formatted string or XML Tree, then writes that file.

Write cc
--------

.. autofunction:: cdl_convert.write_cc

Write cdl
---------

.. autofunction:: cdl_convert.write_cdl
