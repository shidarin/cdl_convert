#########
Changelog
#########

Version 0.7
===========

- Renames :class:`ColorCollectionBase` to :class:`ColorCollection` , since it will be used directly by both ``CCC`` and ``CDL``.
- Added ``parent`` attribute to :class:`ColorCorrection` .
- Calling ``sop_node`` or ``sat_node`` on a :class:`ColorCorrection` before attempting to set a SOP or Sat power now works.
- :class:`ColorCorrection` ``cdl_file`` init argument renamed to ``input_file``, which is now optional and able to be set after init.
- :class:`ColorCorrection` ``determine_dest`` will now use current directory if no ``file_in`` specified.
- ``parse_cc`` ``cdl_file`` arg renamed to ``input_file`` and now accepts a either a raw string or an ``ElementTree`` ``Element`` as ``input_file``.
- ``parse_cdl`` ``cdl_file`` arg renamed to ``input_file``.
- ``parse_ale`` ``edl_file`` arg renamed to ``input_file``.
- ``parse_flex`` ``edl_file`` arg renamed to ``input_file``.
- ``parse_cc`` and ``parse_cdl`` now only yield a single :class:`ColorCorrection` , not a single member list.

Version 0.6.1
=============

- Added :class:`AscXMLBase` class for nodes that can be represented by XML to inherit.
- Suppressed scientific notation from being written out when writing files. Should now write out as close as Python accuracy allows, and the same number of digits.
- ``write_cc`` now writes out 100% correct XML using ElementTree.
- Added tests for ``write_cc``, which **brings our coverage to 100%**

Version 0.6
===========

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

Version 0.5
===========

* Initial Release
* Project Reorganization
* :pep:`8` compliance