#####
Usage
#####

Most likely you'll use ``cdl_convert`` as a script, instead of a python package
itself (indeed, even the name is formatted more like a script (with an
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

Sometimes it might be nessicary to disable cdl_convert's auto-detection of the
input file format. This can be done with the ``-i`` flag.
::
    $ cdl_convert ./ca102_x34.cdl -i cdl

In this case, ``.cdl`` could have indicated either a space separated cdl, or an XML
cdl. ``cdl_convert`` does it's best to try and guess which one the file is, but
if you're running into trouble, it might help to indicate to ``cdl_convert``
what the input file type is.

Full help is available using the standard ``--help`` command:
::
    $ cdl_convert --help
    usage: cdl_convert [-h] [-i INPUT] [-o OUTPUT] input_file

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

Python Usage
============

Once installed with pip, importing ``cdl_convert`` works like importing any
other python module.

    >>> import cdl_convert as cdl


Creating an :class:`AscCdl`
---------------------------

Once imported, you have two choices. You can either instantiate a new, blank
cdl directly, or you can parse a file on disk.

Direct Creation
^^^^^^^^^^^^^^^

If you want to create a new instance of :class:`AscCdl`, you have to provide a
``cc_id``, for the unique cdl identifier and you have to provide a source
filename (``cdl_file``).

    >>> cc = cdl.AscCdl(cc_id='cc1', cdl_file='./myfirstcdl.cc')

.. warning::
    Currently ``cc_id`` does no checking to ensure that it's id is unique among
    all the :class:`AscCdl` that currently exist. At some point this will likely
    be added.

.. warning::
    ``cdl_file`` is likely to not be a required attribute in the future.

An :class:`AscCdl` is created with the 10 required values (RGB values for slope,
offset and power, and a single float for saturation) set to their defaults.

    >>> cc.slope
    [1.0, 1.0, 1.0]
    >>> cc.offset
    [0.0, 0.0, 0.0]
    >>> cc.power
    [1.0, 1.0, 1.0]
    >>> cc.sat
    1.0

Other, optional parameters are set to None, and accessible as a dictionary under
the metadata attribute.

    >>> cc.metadata
    {
        'viewing_desc': None,
        'cc_ref': None,
        'media_ref': None,
        'input_desc': None,
        'desc': None
    }

Parsing a CDL file
^^^^^^^^^^^^^^^^^^

Instead of creating a blank CDL object, you can parse a file from disk, and it
will return a list of :class:`AscCdl`s found in the file. For some formats like
``cc``, this list will be one member long. For others like ``flex`` or ``ale``,
this list could contain hundreds of cdls.

    >>> cdl.parse_cc('./myfirstcdl.cc')
    [<cdl_convert.AscCdl object at 0x1004a5590>]
    >>> cdl.parse_ale('/myfirstedl.ale')
    [
        <cdl_convert.AscCdl object at 0x100633b90>,
        <cdl_convert.AscCdl object at 0x100633c50>,
        <cdl_convert.AscCdl object at 0x100633cd0>,
        <cdl_convert.AscCdl object at 0x100633b50>,
        <cdl_convert.AscCdl object at 0x100633d90>,
        <cdl_convert.AscCdl object at 0x100633b10>,
        <cdl_convert.AscCdl object at 0x100633ad0>,
    ]

Once you have an :class:`AscCdl` from a parser, you'll find that whatever values
it found on the file now exist on the instance of :class:`AscCdl`.

    >>> cc = cdl.parse_cc('./xf/015.cc')[0]
    >>> cc.slope
    [1.02401, 1.00804, 0.89562]
    >>> cc.offset
    [-0.00864, -0.00261, 0.03612]
    >>> cc.power
    [1.0, 1.0, 1.0]
    >>> cc.sat
    1.2
    >>> cc.cc_id
    '015_xf_seqGrade_v01'
    >>> cc.file_in
    '/Users/sean/cdls/xf/015.cc'

.. note::
    When parsing, the ``cc_id`` attribute is set in a variety of ways depending
    on how much information is available. Some formats, like ``cc``, have an
    explicitly tagged ``id`` field that is always used. Other formats, like
    ``flex``, have no such field and the parser tries to grab any scene/take
    metadata it can find to construct one. The last fallback is always the
    filename. For formats that can export multiple :class:`AscCdl`s, the ``cc_id``
    has a created instance number after it.

Working with :class:`AscCdl`
----------------------------

Slope, Offset and Power
^^^^^^^^^^^^^^^^^^^^^^^

Setting the CDL slope, offset and power (SOP) values is as easy as passing them
any list or tuple with three values. Integers and strings will be automatically
converted to floats, while slope and power will also be checked to make sure the
number is positive.

    >>> cc.slope = ('1.234', 5, 273891.37823)
    >>> cc.slope
    [1.234, 5.0, 273891.37823]
    >>> cc.offset = [-0.0013, 0.097, 0.001]
    >>> cc.offset
    [-0.0013, 0.097, 0.001]
    >>> cc.power = [-0.01, 1.0, 1.0]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "cdl_convert/cdl_convert.py", line 352, in power
        raise ValueError("Power values must not be negative")
    ValueError: Power values must not be negative
    >>> cc.power = [1.01, 1.007]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "cdl_convert/cdl_convert.py", line 336, in power
        raise ValueError("Power must be set with all three RGB values")
    ValueError: Power must be set with all three RGB values

.. warning::
    It is possible to set a color value on the SOP directly by index, but this
    skips all checks and conversions.

    >>> cc.slope[1] = 283.0
    >>> cc.slope
    [1.234, 283.0, 273891.37823]
    >>> cc.slope[1] = 'egg'
    >>> cc.slope[1]
    'egg'
    >>> cc.slope
    [1.234, 'egg', 273891.37823]
    >>> cc.slope[1] = '2.5'
    >>> cc.slope
    [1.234, '2.5', 273891.37823]
    >>> cc.slope[1] = -1.0
    >>> cc.slope
    [1.234, -1.0, 273891.37823]

As you can see, we were successful in setting the slope values we wanted, but none
of the values we set were checked to see if they were valid. This resulted in us
setting the green value of the slope to a non-numeric string, a numeric string,
and a negative value.

Saturation
^^^^^^^^^^

Saturation is a single positive float values, and the same checks and conversions
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
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "cdl_convert/cdl_convert.py", line 403, in sat
        raise ValueError("Saturation must be a positive value")
    ValueError: Saturation must be a positive value

Metadata
^^^^^^^^

The metadata dictionary is set like any other dictionary.

    >>> cc.metadata['desc'] = "Zach's mp7 explodes in his hard, sending metal shards everywhere"
    >>> cc.metadata['desc']
    "Zach's mp7 explodes in his hard, sending metal shards everywhere"

Id and Files
^^^^^^^^^^^^

At the current time, id and filepaths cannot be changed after :class:`AscCdl`
instantiation. ``file_out`` is determined by using the class method ``determine_dest``,
which takes the ``file_in`` directory, the cc_id and figures out the output path.

    >>> cc.file_in
    '/Users/sean/cdls/xf/015.cc'
    >>> cc.file_out
    >>> cc.determine_dest('cdl')
    >>> cc.cc_id
    '015_xf_seqGrade_v01'
    >>> cc.file_out
    '/Users/sean/cdls/xf/015_xf_seqGrade_v01.cdl'

Writing CDLs
------------

When you're done tinkering with the :class:`AscCdl` instance, you might want to
write it out to a file. Currently the output file is written the same directory
as the input file. We need to give :class:`AscCdl` the file extension we plan
to write to, then call a ``write`` function with our :class:`AscCdl` instance,
which will actually convert the values on the :class:`AscCdl` into the format
desired, then write that format to disk.

    >>> cc.determine_dest('cdl')
    >>> cc.file_out
    '/Users/sean/cdls/xf/015_xf_seqGrade_v01.cdl'
    >>> cdl.write_cdl(cc)

.. warning::
    It is highly likely that in the future, these will be methods on the
    :class:`AscCdl` class itself, and that instead of writing the file directly,
    they will instead return a string formatted for writing.
