#####
Usage
#####

Most likely you'll use ``cdl_convert`` as a script, instead of a python package
itself. Indeed, even the name is formatted more like a script (with an
underscore) than the more common all lowercase of python modules.

Script Usage
============

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
    $ cdl_convert ./ca102_x34.cdl -i cdl

.. note::
    You should not normally need to do this, but it is possible especially since
    there are multiple formats sharing the same file extension. In this case,
    ``.cdl`` could have indicated either a space separated cdl, or an XML
    cdl. ``cdl_convert`` does it's best to try and guess which one the file is,
    but if you're running into trouble, it might help to indicate to
    ``cdl_convert`` what the input file type is.

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
    usage: cdl_convert.py [-h] [-i INPUT] [-o OUTPUT] [--halt] [--no-output]
                          [--check]
                          input_file

    positional arguments:
      input_file            the file to be converted

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            specify the filetype to convert from. Use when
                            CDLConvert cannot determine the filetype
                            automatically. Supported input formats are: ['cc',
                            'cdl', 'ale', 'flex']
      -o OUTPUT, --output OUTPUT
                            specify the filetype to convert to, comma separated
                            lists are accepted. Defaults to a .cc XML. Supported
                            output formats are: ['cc', 'cdl']
      --halt                turns off exception handling default behavior. Turn
                            this on if you want the conversion process to fail and
                            not continue,rather than relying on default behavior
                            for bad values. Examples are clipping negative values
                            to 0.0 for Slope, Power and Saturation, and
                            automatically generating a new id for a ColorCorrect
                            if no or a bad id is given.
      --no-output           parses all incoming files but no files will be
                            written. Use this in conjunction with '--halt' and '--
                            check to try and track down any oddities observed in
                            the CDLs.
      --check               checks all ColorCorrects that were parsed for odd
                            values. Odd values are any values over 3 or under 0.1
                            for Slope, Power and Saturation. For offset, any value
                            over 1 and under -1 is flagged. Note that depending on
                            the look, these still might be correct values.

Python Usage
============

Once installed with pip, importing ``cdl_convert`` works like importing any
other python module.

    >>> import cdl_convert as cdl


Creating an :class:`ColorCorrection`
------------------------------------

Once imported, you have two choices. You can either instantiate a new, blank
cdl directly, or you can parse a file on disk.

Direct Creation
^^^^^^^^^^^^^^^

If you want to create a new instance of :class:`ColorCorrection`, you have to
provide an ``id``, for the unique cdl identifier and a source filename to
``cdl_file``.

    >>> cc = cdl.ColorCorrection(id='cc1', cdl_file='./myfirstcdl.cc')

.. warning::
    When an instance of :class:`ColorCorrection` is first created, the ``id``
    provided is checked against a class level dictionary variable named
    ``members`` to ensure that no two :class:`ColorCorrection` share the same
    ``id`` , as this is required by the specification.

.. warning::
    It's not possible to change the ``file_in`` attribute once it has been set.

.. warning::
    ``cdl_file`` is likely to not be a required attribute in the future.

An :class:`ColorCorrection` is created with the 10 required values (RGB values
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
can be an infinitely long list of shot descriptions, gripes, notes and
ramblings).

Parsing a CDL file
^^^^^^^^^^^^^^^^^^

Instead of creating a blank CDL object, you can parse a file from disk, and it
will return a list of :class:`ColorCorrection` found in the file. For some
formats like ``cc``, this list will be one member long. For others like
``flex`` or ``ale``, this list could contain hundreds of cdls.

    >>> cdl.parse_cc('./myfirstcdl.cc')
    [<cdl_convert.ColorCorrection object at 0x1004a5590>]
    >>> cdl.parse_ale('/myfirstedl.ale')
    [
        <cdl_convert.ColorCorrection object at 0x100633b90>,
        <cdl_convert.ColorCorrection object at 0x100633c50>,
        <cdl_convert.ColorCorrection object at 0x100633cd0>,
        <cdl_convert.ColorCorrection object at 0x100633b50>,
        <cdl_convert.ColorCorrection object at 0x100633d90>,
        <cdl_convert.ColorCorrection object at 0x100633b10>,
        <cdl_convert.ColorCorrection object at 0x100633ad0>,
    ]

Once you have an :class:`ColorCorrection` from a parser, you'll find that
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
    '/Users/sean/cdls/xf/015.cc'

.. note::
    When parsing, the ``id`` attribute is set in a variety of ways depending
    on how much information is available. Some formats, like ``cc``, have an
    explicitly tagged ``id`` field that is always used. Other formats, like
    ``flex``, have no such field and the parser tries to grab any scene/take
    metadata it can find to construct one. The last fallback is always the
    filename. For formats that can export multiple :class:`ColorCorrection` ,
    the ``id`` has a created instance number after it.

Working with :class:`ColorCorrection`
-------------------------------------

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

    >>> cc = cdl.ColorCorrection(id='cc1', cdl_file='./myfirstcdl.cc')
    >>> cc2 = cdl.ColorCorrection(id='cc2', cdl_file='./mysecondcdl.cc')
    >>> cc.id
    Out[6]: 'cc1'
    >>> cc2.id
    Out[7]: 'cc2'
    >>> cc2.id = 'cc1'
    Traceback (most recent call last):
      File "<ipython-input-8-b2b5487dbc63>", line 1, in <module>
        cc2.id = 'cc1'
      File "cdl_convert/cdl_convert.py", line 362, in id
        self._set_id(value)
      File "cdl_convert/cdl_convert.py", line 430, in _set_id
        cc_id=cc_id
    ValueError: Error setting the id to "cc1". This id is already a registered id.

At the current time, filepaths cannot be changed after
:class:`ColorCorrection` instantiation. ``file_out`` is determined by using
the class method ``determine_dest``, which takes the ``file_in`` directory,
the ``id`` and figures out the output path.

    >>> cc.file_in
    '/Users/sean/cdls/xf/015.cc'
    >>> cc.file_out
    >>> cc.determine_dest('cdl')
    >>> cc.id
    '015_xf_seqGrade_v01'
    >>> cc.file_out
    '/Users/sean/cdls/xf/015_xf_seqGrade_v01.cdl'

Writing CDLs
------------

When you're done tinkering with the :class:`ColorCorrection` instance, you
might want to write it out to a file. Currently the output file is written the
same directory as the input file. We need to give :class:`ColorCorrection` the
file extension we plan to write to, then call a ``write`` function with our
:class:`ColorCorrection` instance, which will actually convert the values on
the :class:`ColorCorrection` into the format desired, then write that format
to disk.

    >>> cc.determine_dest('cdl')
    >>> cc.file_out
    '/Users/sean/cdls/xf/015_xf_seqGrade_v01.cdl'
    >>> cdl.write_rnh_cdl(cc)

.. warning::
    It is highly likely that in the future, these will be methods on the
    :class:`ColorCorrection` class itself, and that instead of writing the
    file directly, they will instead return a string formatted for writing.
