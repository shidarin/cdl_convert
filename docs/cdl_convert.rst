#############
API Reference
#############

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

.. autoclass:: cdl_convert.base.AscColorSpaceBase

AscDescBase
-----------

Classes that are allowed to have a description field subclass from this from
this class to get the ``desc`` attribute. The ``desc`` attribute can be set
with a single string, which will append to the list of strings already present
in ``desc``. If set to a list or tuple, ``desc`` will become a list of those
values. If set to ``None``, ``desc`` will become an empty list.

.. autoclass:: cdl_convert.base.AscDescBase

AscXMLBase
----------

.. autoclass:: cdl_convert.base.AscXMLBase

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

.. autoclass:: cdl_convert.collection.ColorCollection

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

    If the ``id`` does match an already created ``id`` and ``HALT_ON_ERROR`` is
    not set, the ``id`` assignment will go forward, appending the duplicate
    number to the back of the ``id``. So the 2nd instance of 'sh100cc' will
    become 'sh100cc001'.

    Reset the members dictionary by either calling the ``reset_members`` method
    on :class:`ColorCorrection` or by reseting all cdl_convert member
    lists and dictionaries with the ``reset_all`` function.

    If the ``id`` given is a blank string and ``HALT_ON_ERROR`` is set to
    ``False``, ``id`` will be set to the total number of :class:`ColorCorrection`
    in the file, including the one currently being created. This behavior is not
    accepted when changing the ``id`` after creation.

.. warning::
    ``cdl_file`` is likely to not be a required attribute in the future.

.. autoclass:: cdl_convert.correction.ColorCorrection

ColorCorrectionRef
------------------

.. autoclass:: cdl_convert.decision.ColorCorrectionRef

ColorDecision
-------------

ColorDecision's are normally found only within :class:`ColorCorrection` but
this limitation of the ASC CDL schema is not enforced by cdl_convert.

.. autoclass:: cdl_convert.decision.ColorDecision

ColorNodeBase
-------------

This class only exists to be subclassed by :class:`SatNode` and :class:`SopNode`
and should not be used directly.

.. autoclass:: cdl_convert.base.ColorNodeBase

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

.. autoclass:: cdl_convert.decision.MediaRef


SatNode
-------

.. note::
    This class is meant only to be created by a :class:`ColorCorrection` ,
    and thus has the required arg of ``parent`` when instantiating it.

.. autoclass:: cdl_convert.correction.SatNode

SopNode
-------

.. note::
    This class is meant only to be created by a :class:`ColorCorrection` ,
    and thus has the required arg of ``parent`` when instantiating it.

.. warning::
    Setting any of the sop node values with a single value as in
    ``offset = 5.4`` will cause that value to be copied over all 3 colors,
    resulting in ``[5.4, 5.4, 5.4]``.

.. autoclass:: cdl_convert.correction.SopNode

General Functions
=================

Reset All
---------

Resets all the class level lists and dictionaries of cdl_convert. Calling this
is the same as calling each individual ``reset_members`` method.

.. autofunction:: cdl_convert.reset_all

Sanity Check
------------

.. autofunction:: cdl_convert.utils.sanity_check


To Decimal
----------

This is the function we use to convert ints, floats and strings to Decimal
objects. We do NOT attempt to use maximum accuracy on floats passed in,
as that results in extremely long values more often than not. Better to just
truncate the float with a string conversion, than attempt to perfectly
represent with a Decimal.

.. autofunction:: cdl_convert.utils.to_decimal

Parse Functions
===============

These functions can either return a :class:`ColorCorrection` , or a
:class:`ColorCollection` , depending on if they are from a container format.

.. note::
    Use the ``parse_file`` function to parse any input file correctly, without
    worrying about matching the file extension by hand.

Parse ale
---------

.. autofunction:: cdl_convert.parse.parse_ale

Parse cc
--------

.. autofunction:: cdl_convert.parse.parse_cc

Parse ccc
---------

.. autofunction:: cdl_convert.parse.parse_ccc

Parse cdl
---------

.. autofunction:: cdl_convert.parse.parse_cdl

Parse cmx
---------

.. autofunction:: cdl_convert.parse.parse_cmx

Parse file
----------

Passes on the file to the correct parser.

.. autofunction:: cdl_convert.parse.parse_file

Parse flex
----------

.. autofunction:: cdl_convert.parse.parse_flex

Parse Rhythm & Hues cdl
-----------------------

Rhythm & Hues' implementation of the cdl format is based on a very early spec,
and as such lacks the all metadata. It's extremely unlikely that you'll run
into this format in the wild.

.. autofunction:: cdl_convert.parse.parse_rnh_cdl

Write Functions
===============

Each of these functions takes an :class:`ColorCorrection` as an arg, then places
as many attributes of the :class:`ColorCorrection` that the format supports
into a properly formatted string or XML Tree, then writes that file.

Write cc
--------

.. autofunction:: cdl_convert.write.write_cc

Write ccc
---------

.. autofunction:: cdl_convert.write.write_ccc

Write cdl
---------

.. autofunction:: cdl_convert.write.write_cdl

Write Rhythm & Hues cdl
-----------------------

This writes a very sparse cdl format that is based on a very early spec of the
cdl implementation. It lacks all metadata. Unless you work at Rhythm & Hues,
you probably don't want to write a cdl that uses this format.

.. autofunction:: cdl_convert.write.write_rnh_cdl
