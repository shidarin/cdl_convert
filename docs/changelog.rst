#########
Changelog
#########

Version 0.9.2
=============

- Fixed a bug where ALE's with blank lines would not convert correctly.
- Fixed a bug that was preventing ``cdl_convert`` from being correctly installed in Python 2.6
- Fixed continuous integration testing.
- No longer officially supporting Python 3.2, as I've had to remove it from our CI builds. It should still work just fine though, but we won't be running CI against it.

Version 0.9
===========

- Added ability to parse CMX EDLs
- Fixed a script bug where a collection format containing color decisions will not have those color decisions exported as individual color corrections.
- Fixed a bug where we weren't reading line endings correctly in certain situations.
- Added a cdl_convert.py stub file to the package root level, which will allow running of the cdl_convert script without installation. Due to relative imports in the python code, it was no longer possible to call cdl_convert/cdl_convert.py directly.
- The script, when run directly from cdl_convert.py, will now write errors to stderror correctly, and exit with a status of 1.


Version 0.8
===========

- Added `--single` flag. When provided with an output collection format, each color correction in the input will be exported to it's own collection.
- Giving a ColorCorrection a non-duplicate ID now works unless the ``--halt`` flag is given. This means that incoming collections that contain duplicate IDs will not fail out.

Version 0.7.1
=============

- Fixed bug where ALE's without 'Scan Filename' fields could not parse correctly.

Version 0.7
===========

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

- Project is now structured according to Python packaging guidelines with ``setup.py`` etc.
- Some :class:`AscCdl` attributes have been moved into dictionaries (Note that this was later reversed in release 0.6)
- Refactors some parse functions to be less complex
- Makes ``write_cdl`` much simpler and more pythonic.

Version 0.4.2
=============

- Hotfix to fix ``from __future__`` imports

Version 0.4.1
=============

- :pep:`8` conversion
- landscape.io support
- Uses ``from __future__`` for print

Version 0.4
===========

- Python 3 compatible
- More unit testing bug fixes and enhancements.
- Adds better type and exception handling for :class:`AscCdl` setters.
- Now sanitizes id fields of any characters they shouldn't contain.
- Test suite runs on windows now
- Adds Travis-ci for continuous integration testing
- ``parse_cc`` now uses ``ElementTree`` for XML parsing
