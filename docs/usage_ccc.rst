*****************
Color Collections
*****************

Once installed with pip, importing ``cdl_convert`` works like importing any
other python module.

    >>> import cdl_convert as cdl

Creating :class:`ColorCollection`
---------------------------------

The :class:`ColorCollection` class represents both the
``ColorCorrectionCollection`` and ``ColorDecisionList`` containers of the ASC
CDL spec.

The distinctions between the two are fairly trivial:

``ColorCorrectionCollection`` contain one or more ``ColorCorrections``
(which directly correspond to :class:`ColorCorrection` ), as well as the normal
``Description``, ``InputDescription`` and ``ViewingDescription`` fields.

``ColorDecisionList`` contain ``ColorDecision`` (directly corresponding to
:class:`ColorDecision` ) instead of ``ColorCorrection`` . Those
``ColorDecision`` in turn contain the same ``ColorCorrection`` elements
that ``ColorCorrectionCollection`` directly contains. Alongside the
``ColorCorrection`` are optional ``MediaRef`` elements (again directly
corresponding to :class:`MediaRef` ), which simply contain a path to reference
media for the ``ColorCorrection`` alongside.

.. note::
    One final difference is that instead of a ``ColorCorrection``
    element, a ``ColorDecision`` could instead contain a ``ColorCorrectionRef``,
    which is simply an ``id`` reference to another ``ColorCorrection.

:class:`ColorCollection` has a ``type`` attribute that determines what
the :class:`ColorCollection` currently describes when you call its XML
attributes. Setting this to ``'ccc'`` will cause a
``ColorCorrectionCorrection`` to be returned when the ``xml`` attribute is
retrieved. Setting it to ``'cdl'`` causes a ``ColorDecisionList`` to appear
instead.

.. note::
    No matter what combination of ``ColorDecision`` or ``ColorCorrection`` a
    single :class:`ColorCollection` has, any members of the 'opposite' class
    will be displayed correctly when you switch the ``type``.

    If you have 3 :class:`ColorDecision` (each with their own
    :class:`ColorCorrection` ) under the ``color_decisions`` attribute, and 4
    :class:`ColorCorrection` under the ``color_corrections`` attribute,
    the XML will export 7 ``ColorCorrection`` elements when ``type`` is set to
    ``'ccc'``, and 7 ``ColorDecision`` elements when ``type`` is set to
    ``'cdl'``.

    The converted elements are created 'on the fly' and are not saved, simply
    exported that way.

Unlike a :class:`ColorCorrection` , :class:`ColorCollection` does not have any
default values. The description attributes it inherits from
:class:`AscColorSpaceBase` and :class:`AscDescBase` default to none.

Those inherited attributes are ``input_desc`` (to describe the colorspace
entering the correction, ``viewing_desc`` (to describe the colorspace
conversions that must occur for viewing, and what type of monitor was used),
and ``desc`` (which can be an infinitely long list of shot descriptions)

.. note::
    When a child :class:`ColorCorrection` **does not** have an ``input_desc``
    or a ``viewing_desc`` of it's own and that child is exported alone to a
    ``.cc`` file, the descriptions from it's parent are used.

    When a child :class:`ColorCorrection` **has** an ``input_desc`` or a
    ``viewing_desc``, that attribute is considered to have overruled the parent
    attribute.

    In both cases, ``desc``s from the parent are prepended to the child node's
    ``desc``.

    When elements (such as ``desc``) are placed into the child
    :class:`ColorCorrection`, their text data is prepended with
    ``From Parent Collection:`` to easily distinguish between inherited fields
    and native.

.. warning::
    The above note describes behavior not yet implemeneted and should be
    ignored. The author of the above note has been sacked.

Direct Creation
^^^^^^^^^^^^^^^

Creating a new :class:`ColorCollection` is easy, and requires no arguments.

    >>> ccc = cdl.ColorCollection()

Alternatively, you can pass in an ``input_file``:

    >>> ccc = cdl.ColorCollection(input_file='CoolMovieSequence.ccc')
    >>> ccc.file_in
    '/proj/UltimateMovie/share/color/CoolMovieSequence.ccc'

Parsing a CDL Collection file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When the collection you want to manipulate already exists, you'll want to parse
the file on disk. EDL files, ``.ccc`` and ``.cdl`` files all return a single
:class:`ColorCollection` object, which contains all the child color corrections.

    >>> collection = cdl.parse_ccc('/myfirstedl.ccc')
    <cdl_convert.ColorCollection object at 0x100633b40>,
    >>> collection.color_corrections
    [
        <cdl_convert.correction.ColorCorrection object at 0x100633b90>,
        <cdl_convert.correction.ColorCorrection object at 0x100633c50>,
        <cdl_convert.correction.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.correction.ColorCorrection object at 0x100633b50>,
        <cdl_convert.correction.ColorCorrection object at 0x100633d90>,
        <cdl_convert.correction.ColorCorrection object at 0x100633b10>,
        <cdl_convert.correction.ColorCorrection object at 0x100633ad0>,
    ]

When parsing to a :class:`ColorCollection` from disk, the type of file you
parse determines what ``type`` is set to. Parsing an EDL or a ``.cdl`` file
creates a :class:`ColorCollection` with a type of ``'cdl'`` (since EDLs
contain many media references and may even include ``ColorCorrectionRef``
elements), while parsing a ``.ccc`` file or multiple ``.cc`` files will create
an instance with a type of ``'ccc'``.

.. note::
    At the current time, parsing EDLs results on a ``ccc`` collection, not a
    ``cdl`` as stated above.

Using :class:`ColorCollection`
------------------------------

Adding children to :class:`ColorCollection`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Already created :class:`ColorCorrection` or :class:`ColorDecision` can be
added to the correct child list by calling the ``append_child`` method.

    >>> ccc.color_corrections
    []
    >>> ccc.append_child(cc)
    >>> ccc.color_corrections
    [
        <cdl_convert.correction.ColorCorrection object at 0x1004a5590>
    ]
    >>> ccc.append_child(cd)
    >>> ccc.color_decisions
    [
        <cdl_convert.decision.ColorDecision object at 0x1004a5510>
    ]

``append_child`` automatically detects which type of child you are attempting to
append, and places it in the correct list. You can use ``append_children`` to
append a list of children at once- the list can even contain mixed classes.

    >>> list_of_colors
    [
        <cdl_convert.correction.ColorCorrection object at 0x100633b90>,
        <cdl_convert.decision.ColorDecision object at 0x100633b10>,
        <cdl_convert.correction.ColorCorrection object at 0x100633c50>,
        <cdl_convert.correction.ColorCorrection object at 0x100633b50>,
        <cdl_convert.decision.ColorDecision object at 0x100633d90>,
        <cdl_convert.correction.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.decision.ColorDecision object at 0x100633ad0>,
    ]
    >>> ccc.append_children(list_of_colors)
    >>> ccc.color_corrections
    [
        <cdl_convert.correction.ColorCorrection object at 0x100633b90>,
        <cdl_convert.correction.ColorCorrection object at 0x100633c50>,
        <cdl_convert.correction.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.correction.ColorCorrection object at 0x100633b50>,
    ]
    >>> ccc.color_decisions
    [
        <cdl_convert.decision.ColorDecision object at 0x100633d90>,
        <cdl_convert.decision.ColorDecision object at 0x100633b10>,
        <cdl_convert.decision.ColorDecision object at 0x100633ad0>,
    ]

    ``append_child`` and ``append_children`` will fail if you attempt to append
    a child which has a matching ``id`` to an already present child. The only
    exception is a :class:`ColorCorrectionRef` , which of course should
    have the same ``id`` as a full :class:`ColorCorrection` .

.. warning::
    Both ``appand_child`` and ``append_children`` will change the ``parent``
    attribute of :class:`ColorCorrection` and :class:`ColorDecision` to point
    to the :class:`ColorCollection` they are appending to. Since we don't
    enforce a 1 parent to each child relationship, it's very easy to
    accidentally lose track of original parentage.

    While the child's ``parent`` attribute might point to another
    :class:`ColorCollection`, the children of a collection will never
    be removed from the ``color_corrections``, ``color_decisions`` and
    ``all_children`` lists.

    You can immediately reset the ``parent`` attribute to point to a specific
    instance of :class:`ColorCollection` by calling the ``set_parentage``
    method.

Merging multiple :class:`ColorCollection`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have multiple :class:`ColorCollection` and wish to end up with a single
collection, you'll need to merge them together. Assuming you have two
:class:`ColorCollection` with the names ``ccc`` and ``dl`` with the following
information:

    >>> ccc.input_desc
    'LogC to sRGB'
    >>> ccc.viewing_desc
    'DaVinci Resolve on Eizo'
    >>> ccc.desc
    [
        'When Babies Attack Test DI',
        'Do not use for final',
        'Color by Zap Brannigan',
    ]
    >>> ccc.type
    'ccc'
    >>> ccc.all_children
    [
        <cdl_convert.correction.ColorCorrection object at 0x100633b90>,
        <cdl_convert.correction.ColorCorrection object at 0x100633c50>,
        <cdl_convert.correction.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.correction.ColorCorrection object at 0x100633b50>,
    ]
    >>> dl.input_desc
    'Cineon Log'
    >>> dl.viewing_desc
    'Panasonic Plasma rec709'
    >>> dl.desc
    [
        'Animals shot with a fisheye lens',
        'cute fluffy animals',
        'watch for blown out highlights',
        'Color by Zap Brannigan',
    ]
    >>> dl.type
    'cdl'
    >>> dl.all_children
    [
        <cdl_convert.decision.ColorDecision object at 0x100633d90>,
        <cdl_convert.decision.ColorDecision object at 0x100633b10>,
        <cdl_convert.decision.ColorDecision object at 0x100633ad0>,
    ]

You merge by choosing a 'parent' collection, and calling the
``merge_collections`` method on it.

    >>> merged = ccc.merge_collections([dl])
    >>> merged.all_children
    [
        <cdl_convert.correction.ColorCorrection object at 0x100633b90>,
        <cdl_convert.correction.ColorCorrection object at 0x100633c50>,
        <cdl_convert.correction.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.correction.ColorCorrection object at 0x100633b50>,
        <cdl_convert.decision.ColorDecision object at 0x100633d90>,
        <cdl_convert.decision.ColorDecision object at 0x100633b10>,
        <cdl_convert.decision.ColorDecision object at 0x100633ad0>,
    ]

.. note::
    When merging multiple :class:`ColorCollection` , any duplicate children
    objects (if you had the same :class:`ColorCorrection` object assigned as a
    child to multiple :class:`ColorCollection` ) are removed, so the list only
    contains unique members.

The parent determines which Input and Viewing Description
overrides all of the other merged collections. ``type`` is also set to match
the ``type`` of the parent. Since ``ccc`` was our parent:

    >>> merged.input_desc
    'LogC to sRGB'
    >>> merged.viewing_desc
    'DaVinci Resolve on Eizo'
    >>> merged.type
    'ccc'

If we had used ``dl`` as the merged parent:

    >>> merged = dl.merge_collections([ccc])
    >>> merged.input_desc
    'Cineon Log'
    >>> merged.viewing_desc
    'Panasonic Plasma rec709'
    >>> merged.type
    'cdl'

Unlike the Input and Viewing Descriptions, the normal Description attributes
are all merged together.

    >>> merged.desc
    [
        'When Babies Attack Test DI',
        'Do not use for final',
        'Color by Zap Brannigan',
        'Animals shot with a fisheye lens',
        'cute fluffy animals',
        'watch for blown out highlights',
        'Color by Zap Brannigan',
    ]

.. note::
    Unlike the lists of children, duplicates are not removed from the list of
    descriptions.
