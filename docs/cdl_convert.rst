#############
API Reference
#############

.. note::
    All code for the following lives under cdl_convert.cdl_convert, and is
    imported into the local space of cdl_convert.

Classes
=======

The class structure of ``cdl_convert`` mirrors the element structure of the
 XML schema for ``ccc``, ``cdl`` and ``cc`` files as defined by the
ASC. The XML schema's represent the most complicated and structured variant of
the format, and therefore it behooves the project to mimic their structure.

However, where similar elements exist as entirely separate entities in the XML
schema, they might have been combined here.

AscColorSpaceBase
-----------------

Classes that deal with input and viewer colorspace can subclass from this class
to get the ``input_desc`` and ``viewing_desc`` attributes.

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

ColorCollection
---------------

This class functions as both a ColorDecisionList and a
ColorCorrectionCollection. It's children can be either ColorDecisions,
ColorCorrections, or a combination of the two. Despite being able to
have either type of child, the :class:`ColorCollection` still needs to know
which type of collection you want it to represent.

Setting the ``type`` of the :class:`ColorCollection` to either ``ccc`` or
``cdl`` causes children of the opposite type to be converted into the
appropriate type when exporting the class.

.. note::
    ``parse_ale`` and ``parse_flex`` both return as a ``ccc`` at this time,
    contrary to the documentation below.

    In addition, the inclusion of parent metadata into orphaned children is
    also a work in progress.

If ``parse_ale`` is used to parse an ``ale`` edl file, the ``ale`` will be
read into a :class:`ColorCollection` set to ``cdl`` and the children the
``ale`` creates will actually be :class:`ColorDecision` , as that allows
for the easy inclusion of :class:`MediaRef` objects. If you then use
``write_ccc`` to write a ``ccc`` file, all the children :class:`ColorDecision`
will create XML elements for their :class:`ColorCorrection` children,
adding in any :class:`MediaRef` that were found as ``Description`` elements.
Finally the :class:`ColorCollection` ``type`` is set to ``ccc`` and the
``xml_root`` field is called, which knows to return a ``ccc`` style XML
element to ``write_ccc``.

.. autoclass:: cdl_convert.ColorCollection

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

    Reset the members dictionary by either calling the ``reset_members`` method
    on :class:`ColorCorrection` or by reseting all cdl_convert member
    lists and dictionaries with the ``reset_all`` function.

    If the ``id`` given is a blank string and ``HALT_ON_ERROR`` is set to
    ``False``, ``id`` will be set to the total number of :class:`ColorCorrection`
    in the file, including the one currently being created. This behavior is not
    accepted when changing the ``id`` after creation.

.. warning::
    ``cdl_file`` is likely to not be a required attribute in the future.

.. autoclass:: cdl_convert.ColorCorrection

ColorCorrectionReference
------------------------

.. autoclass:: cdl_convert.ColorCorrectionReference

ColorDecision
-------------

ColorDecision's are normally found only within :class:`ColorCorrection` but
this limitation of the ASC CDL schema is not enforced by cdl_convert.

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

.. note::
    The above metadata preservation is not yet implemented.

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

General Functions
=================

Reset All
---------

Resets all the class level lists and dictionaries of cdl_convert. Calling this
is the same as calling each individual ``reset_members`` method.

.. autofunction:: cdl_convert.reset_all

Sanity Check
------------

.. autofunction:: cdl_convert.sanity_check

Parse Functions
===============

These functions create and return one of more :class:`ColorCorrection`, always
returning their results in the form of a list, even if the file type can only
produce a single cdl.

Parse ale
---------

.. autofunction:: cdl_convert.parse_ale

Parse cc
--------

.. autofunction:: cdl_convert.parse_cc

Parse ccc
---------

.. autofunction:: cdl_convert.parse_ccc

Parse cdl
---------

.. autofunction:: cdl_convert.parse_cdl

Parse Rhythm & Hues cdl
-----------------------

Rhythm & Hues' implementation of the cdl format is based on a very early spec,
and as such lacks the all metadata. It's extremely unlikely that you'll run
into this format in the wild.

.. autofunction:: cdl_convert.parse_rnh_cdl

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

Write ccc
---------

.. autofunction:: cdl_convert.write_ccc

Write cdl
---------

.. autofunction:: cdl_convert.write_cdl

Write Rhythm & Hues cdl
-----------------------

This writes a very sparse cdl format that is based on a very early spec of the
cdl implementation. It lacks all metadata. Unless you work at Rhythm & Hues,
you probably don't want to write a cdl that uses this format.

.. autofunction:: cdl_convert.write_rnh_cdl
