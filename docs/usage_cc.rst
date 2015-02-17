*********************
ColorCorrection Usage
*********************

Once installed with pip, importing ``cdl_convert`` works like importing any
other python module.

    >>> import cdl_convert as cdl

Creating :class:`ColorCorrection`
---------------------------------

Once imported, you have two choices. You can either instantiate a new, blank
cdl directly, or you can parse a file on disk.

A :class:`ColorCorrection` is created with the 10 required values (RGB values
for slope, offset and power, and a single value for saturation) set to their
defaults.

    >>> cc.slope
    (Decimal('1.0'), Decimal('1.0'), Decimal('1.0'))
    >>> cc.offset
    (Decimal('0.0'), Decimal('0.0'), Decimal('0.0'))
    >>> cc.power
    (Decimal('1.0'), Decimal('1.0'), Decimal('1.0'))
    >>> cc.sat
    Decimal('1.0')

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

    Giving duplicate ``id`` will result in a number being appended to the back,
    unless ``HALT_ON_ERROR`` is set, in which case it will fail.

    Reset the members list by calling the ``reset_members`` method of
    :class:`ColorCorrection` or reset all class member list and dictionaries
    with ``cdl_convert.reset_all``.

Parsing a single correction CDL file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of creating a blank CDL object, you can parse a ``cc`` file from disk,
and it will return a single :class:`ColorCorrection` matching the correction
found in the file. Formats that contain multiple corrections will return
a :class:`ColorCollection` , which contains child :class:`ColorCorrection` .

If you don't want to worry about matching the filetype to a parser, just use
the generic ``parse_file`` function.

    >>> cdl.parse_file('./myfirstcdl.cc')
    <cdl_convert.correction.ColorCorrection object at 0x1004a5590>
    >>> collection = cdl.parse_file('/myfirstedl.ccc')
    <cdl_convert.collection.ColorCollection object at 0x100633b40>,
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

Once you have a :class:`ColorCorrection` from a parser, you'll find that
whatever values it found on the file now exist on the instance of
:class:`ColorCorrection`.

    >>> cc = cdl.parse_cc('./xf/015.cc')
    >>> cc.slope
    (Decimal('1.02401'), Decimal('1.00804'), Decimal('0.89562'))
    >>> cc.offset
    (Decimal('-0.00864'), Decimal('-0.00261'), Decimal('0.03612'))
    >>> cc.power
    (Decimal('1.0'), Decimal('1.0'), Decimal('1.0'))
    >>> cc.sat
    Decimal('1.2')
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
any list or tuple with three values. Integers, strings and floats will be
automatically converted to Decimals, while slope and power will also truncate
at zero.

    >>> cc.slope = ('1.234', 5, 273891.37823)
    >>> cc.slope
    (Decimal('1.234'), Decimal('5.0'), Decimal('273891.37823'))
    >>> cc.offset = (-0.0013, 0.097, 0.001)
    >>> cc.offset
    (Decimal('-0.0013'), Decimal('0.097'), Decimal('0.001'))
    >>> cc.power = (-0.01, 1.0, 1.0)
    >>> cc.power
    (Decimal('0.0'), Decimal('1.0'), Decimal('1.0'))
    >>> cc.power = (1.01, 1.007)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "cdl_convert/correction.py", line 306, in power
        self.sop_node.power = power_rgb
      File "cdl_convert/correction.py", line 668, in power
        value = self._check_setter_value(value, 'power')
      File "cdl_convert/correction.py", line 767, in _check_setter_value
        value = self._check_rgb_values(value, name, negative_allow)
      File "cdl_convert/correction.py", line 709, in _check_rgb_values
        values=values
    ValueError: Error setting power with value: "(1.01, 1.007)". Power values given as a list or tuple must have 3 elements, one for each color.

It's also possible to set the SOP values with a single value, and have it
copy itself across all three colors. Setting SOP values this way mimics how
color corrections typically start out.

    >>> cc.slope = 1.2
    >>> cc.slope
    (Decimal('1.2'), Decimal('1.2'), Decimal('1.2'))


Saturation
^^^^^^^^^^

Saturation is a positive float values, and the same checks and conversions
that we do on SOP values happen for saturation as well.

    >>> cc.sat = 1.1
    >>> cc.sat
    Decimal('1.1')
    >>> cc.sat = '1.2'
    >>> cc.sat
    Decimal('1.2')
    >>> cc.sat = 1
    >>> cc.sat
    Decimal('1.0')
    >>> cc.sat = -0.1
    >>> cc.sat
    Decimal('0.0')

.. warning::
    If it's desired to have negative values raise an exception instead of
    truncating to zero, set the global config module variable ``HALT_ON_ERROR``
    to be ``True``.
    ::
        >>> cdl.config.HALT_ON_ERROR = True
        >>> cc.power = (-0.01, 1.0, 1.0)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "cdl_convert/correction.py", line 306, in power
            self.sop_node.power = power_rgb
          File "cdl_convert/correction.py", line 668, in power
            value = self._check_setter_value(value, 'power')
          File "cdl_convert/correction.py", line 767, in _check_setter_value
            value = self._check_rgb_values(value, name, negative_allow)
          File "cdl_convert/correction.py", line 720, in _check_rgb_values
            negative_allow
          File "cdl_convert/base.py", line 419, in _check_single_value
            value=value
        ValueError: Error setting power with value: "-0.01". Values must not be negative


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
      File "cdl_convert/correction.py", line 362, in id
        self._set_id(value)
      File "cdl_convert/correction.py", line 430, in _set_id
        cc_id=cc_id
    ValueError: Error setting the id to "cc1". This id is already a registered id.

A ValueError is only raised if ``HALT_ON_ERROR`` is set. If ``HALT_ON_ERROR``
is not set (default), a number will be appended to the non-duplicate ID.

So if you already have a ColorCorrection with the id of 'sh100cc', the second
ColorCorrection you set to have that id will actually set to 'sh100cc001'.

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
