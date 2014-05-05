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

AscColorSpaceBase
-----------------

Classes that deal with input and viewer colorspace can subclass from this class
to get the ``input_desc`` and ``viewing_desc`` attributes.

.. note::
    This class is a stub for now. In the future it will have colorspace related
    functionality.

.. autoclass:: cdl_convert.AscColorSpaceBase

AscDescBase
-----------

Classes that are allowed to have a description field subclass from this from
this class to get the ``desc`` attribute. The ``desc`` attribute can be set
with a single string, which will append to the list of strings already present
in ``desc``. If set to a list or tuple, ``desc`` will become a list of those
values. If set to ``None``, ``desc`` will become an empty list.

.. autoclass:: cdl_convert.AscDescBase

AscXMLBase
----------

.. autoclass:: cdl_convert.AscXMLBase

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

    If the ``id`` given is a blank string and ``HALT_ON_ERROR`` is set to
    ``False``, ``id`` will be set to the total number of :class:`ColorCorrection`
    in the file, including the one currently being created. This behavior is not
    accepted when changing the ``id`` after creation.

.. warning::
    ``cdl_file`` is likely to not be a required attribute in the future.

.. autoclass:: cdl_convert.ColorCorrection

ColorDecision
-------------

.. note:: This class is a stub and has no functionality yet.

.. autoclass:: cdl_convert.ColorDecision

ColorNodeBase
-------------

This class only exists to be subclassed by :class:`SatNode` and :class:`SopNode`
and should not be used directly.

.. autoclass:: cdl_convert.ColorNodeBase

MediaRef
--------

Media Ref's are normally found only inside of :class:`ColorDecision`, which
itself is found only inside of the :class:`ColorDecisionList` collection. This
isn't a restriction that ``cdl_convert`` explicitly enforces, but the parse
and write functions will only be creating and writing found :class:`MediaRef`
objects following the rules.

Where possible when writing filetypes that don't support :class:`MediaRef`,
the information kept in :class:`MediaRef` will be converted into description
field metadata and preserved in that way.

:class:`MediaRef` is meant to provide a convenient interface for managing
and interpreting data stored in CDLs. You can change a broken absolute link
directory to a relative link without touching the filename, or retrieve a full
list of image sequences contained within a referenced directory.

.. autoclass:: cdl_convert.MediaRef


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
into a properly formatted string or XML Tree, then writes that file.

Write cc
--------

.. autofunction:: cdl_convert.write_cc

Write cdl
---------

.. autofunction:: cdl_convert.write_cdl
