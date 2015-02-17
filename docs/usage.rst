************
Script Usage
************

Most likely you'll use ``cdl_convert`` as a script, instead of a python package
itself. Indeed, even the name is formatted more like a script (with an
underscore) than the more common all lowercase of python modules.

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
    usage: cdl_convert [-h] [-i INPUT] [-o OUTPUT] [-d DESTINATION] [--halt]
                       [--no-output] [--check] [--single]
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
      --single              only write a single color decision per file when given
                            collection formats. This means that a single input CDL
                            will export multipleCDL files, one per color decision.
