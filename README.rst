
CDL Convert
===========

|PyPI Version|\ |Build Status|\ |Coverage Status|\ |Code Health|

Converts between common `ASC CDL`_ formats. The `American Society of
Cinematographers`_ Color Decision List (ASC CDL, or CDL for short) is a
schema to simplify the process of interchanging color data between
various programs and facilities.

The ASC has defined schemas for including the 10 basic numbers in 5
different formats:

-  Avid Log Exchange (ALE)
-  Film Log EDL Exchange (FLEx)
-  CMX EDL
-  XML Color Correction (cc)
-  XML Color Correction Collection (ccc)

Unofficial Formats:

-  OCIOCDLTransform, a `Foundry Nuke`_ node
-  Space separated CDL, a Rhythm & Hues internal cdl format

It is the purpose of CDL Convert to convert ASC CDL information between
these basic formats to further facilitate the ease of exchange of color
data within the Film and TV industries.

**CDL Convert is not associated with the American Society of
Cinematographers**

Conversions
-----------

Currently we support converting from:

-  ALE
-  CC
-  FLEx
-  CDL

To:

-  CC
-  Space Separated CDL

With support for both from and to expanding in the future.

Installation
------------

Installing is as simple as using pip:

::

    $ pip install cdl_convert
If you don't want to bother with a pip style install, you can alternatively
grab ``cdl_convert/cdl_convert.py``, As this file is the script and all the
functions and classes needed.

Usage
-----

If you just want to convert to a ``.cc`` XML file, the only required argument
is an input file, like so:
::

    $ cdl_convert ./di_v001.flex
You can override the default ``.cc`` output, or provide multiple outputs with
the ``-o`` flag.
::

    $ cdl_convert ./di_v001.flex -o cc,cdl
Full help is available with ``--help``

Code
----

CDL Convert is written for Python 2.6 through 3.4.
Code is written for strict PEP 8 compliance, with all code being checked on
push through `landscape.io`_. Docstrings follow Google code standards.

Development uses Git Flow model.

License
-------

Basic MIT License. If you use or modify the project I would love to hear
from you. For more information on the license, please see the LICENSE
file that accompanies the project.

.. _ASC CDL: http://en.wikipedia.org/wiki/ASC_CDL
.. _American Society of Cinematographers: http://www.theasc.com/
.. _Foundry Nuke: http://www.thefoundry.co.uk/nuke/
.. _landscape.io: https://landscape.io/

.. |PyPI Version| image:: https://badge.fury.io/py/cdl_convert.svg
   :target: http://badge.fury.io/py/cdl_convert
.. |Build Status| image:: https://travis-ci.org/shidarin/cdl_convert.svg?branch=master
   :target: https://travis-ci.org/shidarin/cdl_convert
.. |Coverage Status| image:: https://coveralls.io/repos/shidarin/cdl_convert/badge.png?branch=master
   :target: https://coveralls.io/r/shidarin/cdl_convert?branch=master
.. |Code Health| image:: https://landscape.io/github/shidarin/cdl_convert/master/landscape.png
   :target: https://landscape.io/github/shidarin/cdl_convert/master