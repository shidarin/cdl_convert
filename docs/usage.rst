#####
Usage
#####

Most likely you'll use ``cdl_convert`` as a script, instead of a python package
itself. Indeed, even the name is formatted more like a script (with an
underscore) than the more common all lowercase of python modules.

************
Script Usage
************

If you just want to convert to a ``.cc`` XML file, the only required argument
is an input file, like so:
::
    $ cdl_convert ./di_v001.flex

You can override the default ``.cc`` output, or provide multiple outputs with
the ``-o`` flag.
::
    $ cdl_convert ./di_v001.flex -o cc,cdl

Sometimes it might be necessary to disable cdl_convert's auto-detection of the
input file format. This can be done with the ``-i`` flag.
::
    $ cdl_convert ./ca102_x34.cdl -i rcdl

.. note::
    You should not normally need to do this, but it is possible especially since
    there are multiple formats sharing the same file extension. In this case,
    ``.cdl`` could have indicated either a space separated cdl (an ``rcdl``),
    or an XML cdl. ``cdl_convert`` does it's best to try and guess which one
    the file is, but if you're running into trouble, it might help to indicate
    to ``cdl_convert`` what the input file type is.

By default, converted files will be written to the './converted' directory, but
a custom destination directory can easily be specified with the ``-d`` flag.
::
    $ cdl_convert ./hk416_210.ccc -d /hello_kitty/luts/cdls/

.. warning::
    It's possible to pass a '.' to the ``-d`` flag, causing converted files to
    be written to the same directory as the directory you're calling cdl_convert
    from, and often that ends up being the same directory as the file you're
    converting from. If one isn't careful, there's a possibility you could
    overwrite the original files.

When converting large batches of color corrections, it can be helpful to know
if there's anything odd about any of them. Using the ``--check`` flag will
cause any potentially invalid numbers to be flagged and printed to the shell.

For Slope, Power and Saturation, any values below ``0.1`` or above ``3.0`` will
flag. For Offset, any values below ``-1.0`` or above ``1.0`` will flag.
::
    $ cdl_convert ./di_v001.flex
    The ColorCorrection "a347.x700" was given a Slope value of "0.978", which
    might be incorrect.
    The ColorCorrection "a400.x050" was given a Saturation value of "3.1",
    which might be incorrect.

This is especially useful when combined with the ``--no-output`` flag, which
will enable a dry run mode and allow you to spot odd values before running.

Full help is available using the standard ``--help`` command:
::
    $ cdl_convert --help
    usage: cdl_convert.py [-h] [-i INPUT] [-o OUTPUT] [-d DESTINATION] [--halt]
                          [--no-output] [--check]
                          input_file

    positional arguments:
      input_file            the file to be converted

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            specify the filetype to convert from. Use when
                            CDLConvert cannot determine the filetype
                            automatically. Supported input formats are: ['flex',
                            'cc', 'ale', 'cdl', 'rcdl', 'ccc']
      -o OUTPUT, --output OUTPUT
                            specify the filetype to convert to, comma separated
                            lists are accepted. Defaults to a .cc XML. Supported
                            output formats are: ['cc', 'cdl', 'ccc', 'rcdl']
      -d DESTINATION, --destination DESTINATION
                            specify an output directory to save converted files
                            to. If not provided will default to ./converted/
      --halt                turns off exception handling default behavior. Turn
                            this on if you want the conversion process to fail and
                            not continue,rather than relying on default behavior
                            for bad values. Examples are clipping negative values
                            to 0.0 for Slope, Power and Saturation, and
                            automatically generating a new id for a ColorCorrect
                            if no or a bad id is given.
      --no-output           parses all incoming files but no files will be
                            written. Use this in conjunction with '--halt' and '--
                            check' to try and track down any oddities observed in
                            the CDLs.
      --check               checks all ColorCorrects that were parsed for odd
                            values. Odd values are any values over 3 or under 0.1
                            for Slope, Power and Saturation. For offset, any value
                            over 1 and under -1 is flagged. Note that depending on
                            the look, these still might be correct values.

************
Python Usage
************

Once installed with pip, importing ``cdl_convert`` works like importing any
other python module.

    >>> import cdl_convert as cdl

Color Corrections
=================

Creating :class:`ColorCorrection`
---------------------------------

Once imported, you have two choices. You can either instantiate a new, blank
cdl directly, or you can parse a file on disk.

A :class:`ColorCorrection` is created with the 10 required values (RGB values
for slope, offset and power, and a single float for saturation) set to their
defaults.

    >>> cc.slope
    (1.0, 1.0, 1.0)
    >>> cc.offset
    (0.0, 0.0, 0.0)
    >>> cc.power
    (1.0, 1.0, 1.0)
    >>> cc.sat
    1.0

.. note::
    ``slope``, ``offset``, ``power`` and ``sat`` are convenience properties that
    actually reference two child objects of :class:`ColorCorrection` , a
    :class:`SopNode` and a :class:`SatNode` . Calling them via ``cc.power``
    is the same as calling ``cc.sop_node.power``.

The :class:`ColorCorrection` class inherits from both the
:class:`AscColorSpaceBase` class, and the :class:`AscDescBase` class, giving it
the additional attributes of ``input_desc`` (to describe the colorspace entering
the correction, ``viewing_desc`` (to describe the colorspace conversions that
must occur for viewing, and what type of monitor was used), and ``desc`` (which
can be an infinitely long list of shot descriptions)

Direct Creation
^^^^^^^^^^^^^^^

If you want to create a new instance of :class:`ColorCorrection`, you have to
provide an ``id``, for the unique cdl identifier and an optional source
filename to ``input_file``.

    >>> cc = cdl.ColorCorrection(id='cc1', input_file='./myfirstcdl.cc')

.. warning::
    When an instance of :class:`ColorCorrection` is first created, the ``id``
    provided is checked against a class level dictionary variable named
    ``members`` to ensure that no two :class:`ColorCorrection` share the same
    ``id`` , as this is required by the specification.

    Reset the members list by calling the ``reset_members`` method of
    :class:`ColorCorrection` or reset all class member list and dictionaries
    with ``reset_all``.

Parsing a single correction CDL file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of creating a blank CDL object, you can parse a ``cc`` file from disk,
and it will return a single :class:`ColorCorrection` matching the correction
found in the file. Formats that contain multiple corrections will return
a :class:`ColorCollection` , which contains child :class:`ColorCorrection` .

If you don't want to worry about matching the filetype to a parser, just use
the generic ``parse_file`` function.

    >>> cdl.parse_file('./myfirstcdl.cc')
    <cdl_convert.ColorCorrection object at 0x1004a5590>
    >>> collection = cdl.parse_file('/myfirstedl.ccc')
    <cdl_convert.ColorCollection object at 0x100633b40>,
    >>> collection.color_corrections
    [
        <cdl_convert.ColorCorrection object at 0x100633b90>,
        <cdl_convert.ColorCorrection object at 0x100633c50>,
        <cdl_convert.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.ColorCorrection object at 0x100633b50>,
        <cdl_convert.ColorCorrection object at 0x100633d90>,
        <cdl_convert.ColorCorrection object at 0x100633b10>,
        <cdl_convert.ColorCorrection object at 0x100633ad0>,
    ]

Once you have a :class:`ColorCorrection` from a parser, you'll find that
whatever values it found on the file now exist on the instance of
:class:`ColorCorrection`.

    >>> cc = cdl.parse_cc('./xf/015.cc')[0]
    >>> cc.slope
    (1.02401, 1.00804, 0.89562)
    >>> cc.offset
    (-0.00864, -0.00261, 0.03612)
    >>> cc.power
    (1.0, 1.0, 1.0)
    >>> cc.sat
    1.2
    >>> cc.id
    '015_xf_seqGrade_v01'
    >>> cc.file_in
    '/Users/niven/cdls/xf/015.cc'

.. note::
    When parsing, the ``id`` attribute is set in a variety of ways depending
    on how much information is available. Some formats, like ``cc``, have an
    explicitly tagged ``id`` field that is always used. Other formats, like
    ``flex``, have no such field and the parser tries to grab any scene/take
    metadata it can find to construct one. The last fallback is always the
    filename. For formats that can contain multiple :class:`ColorCorrection` ,
    the ``id`` has a created instance number after it.

Using :class:`ColorCorrection`
------------------------------

Slope, Offset and Power
^^^^^^^^^^^^^^^^^^^^^^^

Setting the CDL slope, offset and power (SOP) values is as easy as passing them
any list or tuple with three values. Integers and strings will be automatically
converted to floats, while slope and power will also truncate at zero.

    >>> cc.slope = ('1.234', 5, 273891.37823)
    >>> cc.slope
    (1.234, 5.0, 273891.37823)
    >>> cc.offset = (-0.0013, 0.097, 0.001)
    >>> cc.offset
    (-0.0013, 0.097, 0.001)
    >>> cc.power = (-0.01, 1.0, 1.0)
    >>> cc.power
    (0.0, 1.0, 1.0)
    >>> cc.power = (1.01, 1.007)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "cdl_convert/cdl_convert.py", line 336, in power
        raise ValueError("Power must be set with all three RGB values")
    ValueError: Power must be set with all three RGB values

It's also possible to set the SOP values with a single value, and have it
copy itself across all three colors. Setting SOP values this way mimics how
color corrections typically start out.

    >>> cc.slope = 1.2
    >>> cc.slope
    (1.2, 1.2, 1.2)

Saturation
^^^^^^^^^^

Saturation is a positive float values, and the same checks and conversions
that we do on SOP values happen for saturation as well.

    >>> cc.sat = 1.1
    >>> cc.sat
    1.1
    >>> cc.sat = '1.2'
    >>> cc.sat
    1.2
    >>> cc.sat = 1
    >>> cc.sat
    1.0
    >>> cc.sat = -0.1
    >>> cc.sat
    0.0

.. warning::
    If it's desired to have negative values raise an exception instead of
    truncating to zero, set the global module variable ``HALT_ON_ERROR`` to be
    ``True``.
    ::
        >>> cdl.HALT_ON_ERROR = True
        >>> cc.power = (-0.01, 1.0, 1.0)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "cdl_convert/cdl_convert.py", line 352, in power
            raise ValueError("Power values must not be negative")
        ValueError: Power values must not be negative


Description
^^^^^^^^^^^

Certain formats of the cdl will contain multiple description entries. Each
description entry is added to the ``desc`` attribute, which returns a list of
the entries.

    >>> cc.desc
    ['John enters the room', '5.6 ISO 800', 'bad take']

You can append to list by setting the description field like normal.

    >>> cc.desc = 'final cc'
    >>> cc.desc
    ['John enters the room', '5.6 ISO 800', 'bad take', 'final cc]

Setting the value to a new list or tuple will replace the list.

    >>> cc.desc
    ['John enters the room', '5.6 ISO 800', 'bad take', 'final cc]
    >>> cc.desc = ['first comment', 'second comment']
    >>> cc.desc
    ['first comment', 'second comment']

Id and Files
^^^^^^^^^^^^

When creating a :class:`ColorCorrection`, the ``id`` field is checked against a
global list of :class:`ColorCorrection` ids, and creation fails if the ``id``
is not unique.

You can change the id after creation, but it will perform the same check.

    >>> cc = cdl.ColorCorrection(id='cc1', input_file='./myfirstcdl.cc')
    >>> cc2 = cdl.ColorCorrection(id='cc2', input_file='./mysecondcdl.cc')
    >>> cc.id
    'cc1'
    >>> cc2.id
    'cc2'
    >>> cc2.id = 'cc1'
    Traceback (most recent call last):
      File "<ipython-input-8-b2b5487dbc63>", line 1, in <module>
        cc2.id = 'cc1'
      File "cdl_convert/cdl_convert.py", line 362, in id
        self._set_id(value)
      File "cdl_convert/cdl_convert.py", line 430, in _set_id
        cc_id=cc_id
    ValueError: Error setting the id to "cc1". This id is already a registered id.

At the current time, ``file_out`` cannot be set directly. ``file_out`` is
determined by using the class method ``determine_dest``, which takes a
provided directory, the ``id`` and figures out the output path.

    >>> cc.file_in
    '/Users/sean/cdls/xf/015.cc'
    >>> cc.file_out
    >>> cc.determine_dest('cdl', '/Users/potter/cdls/converted/')
    >>> cc.id
    '015_xf_seqGrade_v01'
    >>> cc.file_out
    '/Users/potter/cdls/converted/015_xf_seqGrade_v01.cdl'

Writing :class:`ColorCorrection`
--------------------------------

When you're done tinkering with the :class:`ColorCorrection` instance, you
might want to write it out to a file. We need to give :class:`ColorCorrection` the
file extension we plan to write to, then call a ``write`` function with our
:class:`ColorCorrection` instance, which will actually convert the values on
the :class:`ColorCorrection` into the format desired, then write that format
to disk.

    >>> cc.determine_dest('cdl', '/Users/potter/cdls/converted/')
    >>> cc.file_out
    '/Users/potter/cdls/converted/015_xf_seqGrade_v01.cdl'
    >>> cdl.write_cdl(cc)

.. warning::
    It is highly likely that in the future, these will be methods on the
    :class:`ColorCorrection` class itself, and that instead of writing the
    file directly, they will instead return a string formatted for writing.

Color Collections
=================

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
        <cdl_convert.ColorCorrection object at 0x100633b90>,
        <cdl_convert.ColorCorrection object at 0x100633c50>,
        <cdl_convert.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.ColorCorrection object at 0x100633b50>,
        <cdl_convert.ColorCorrection object at 0x100633d90>,
        <cdl_convert.ColorCorrection object at 0x100633b10>,
        <cdl_convert.ColorCorrection object at 0x100633ad0>,
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
        <cdl_convert.ColorCorrection object at 0x1004a5590>
    ]
    >>> ccc.append_child(cd)
    >>> ccc.color_decisions
    [
        <cdl_convert.ColorDecision object at 0x1004a5510>
    ]

``append_child`` automatically detects which type of child you are attempting to
append, and places it in the correct list. You can use ``append_children`` to
append a list of children at once- the list can even contain mixed classes.

    >>> list_of_colors
    [
        <cdl_convert.ColorCorrection object at 0x100633b90>,
        <cdl_convert.ColorDecision object at 0x100633b10>,
        <cdl_convert.ColorCorrection object at 0x100633c50>,
        <cdl_convert.ColorCorrection object at 0x100633b50>,
        <cdl_convert.ColorDecision object at 0x100633d90>,
        <cdl_convert.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.ColorDecision object at 0x100633ad0>,
    ]
    >>> ccc.append_children(list_of_colors)
    >>> ccc.color_corrections
    [
        <cdl_convert.ColorCorrection object at 0x100633b90>,
        <cdl_convert.ColorCorrection object at 0x100633c50>,
        <cdl_convert.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.ColorCorrection object at 0x100633b50>,
    ]
    >>> ccc.color_decisions
    [
        <cdl_convert.ColorDecision object at 0x100633d90>,
        <cdl_convert.ColorDecision object at 0x100633b10>,
        <cdl_convert.ColorDecision object at 0x100633ad0>,
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
        <cdl_convert.ColorCorrection object at 0x100633b90>,
        <cdl_convert.ColorCorrection object at 0x100633c50>,
        <cdl_convert.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.ColorCorrection object at 0x100633b50>,
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
        <cdl_convert.ColorDecision object at 0x100633d90>,
        <cdl_convert.ColorDecision object at 0x100633b10>,
        <cdl_convert.ColorDecision object at 0x100633ad0>,
    ]

You merge by choosing a 'parent' collection, and calling the
``merge_collections`` method on it.

    >>> merged = ccc.merge_collections([dl])
    >>> merged.all_children
    [
        <cdl_convert.ColorCorrection object at 0x100633b90>,
        <cdl_convert.ColorCorrection object at 0x100633c50>,
        <cdl_convert.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.ColorCorrection object at 0x100633b50>,
        <cdl_convert.ColorDecision object at 0x100633d90>,
        <cdl_convert.ColorDecision object at 0x100633b10>,
        <cdl_convert.ColorDecision object at 0x100633ad0>,
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
