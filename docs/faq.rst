##########################
Frequently Asked Questions
##########################

Python 2 & 3 Support
====================

- What versions of Python does ``cdl_convert`` support?
    ``cdl_convert`` works in Python 2.6 through 3.4 and PyPy. A full test suite
    runs continuous integration through `Travis-ci.org`_, coverage through
    `coveralls.io`_, and code quality checked with `landscape.io`_. **Code is**
    :pep:`8` **compliant**, with docstrings following `google code`_ docstring
    standards.

- Really? It works on both Python 2 and 3? And PyPy?
    Yes. No conversion or modification needed.

CDL Format Support
==================

- Why don't you support format *X*?
    I either haven't had time to build a parser for the format yet, or I might
    even be unaware it exists. Perhaps you should drop by the `issues`_ page
    and create a request for the format? If creating a request for a format it
    helps immensely to have a sample of that format.

Project Structure
=================

- Why are all the parsers and writers functions, instead of methods on the :class:`ColorCorrection` class? to
    This seemed the best approach for it's place in the script converter
    that forms a backbone of this project. As support for the more complicated
    formats grows, It's very like that export formats that write out a single
    file per CDL will live as methods of :class:`ColorCorrection` , and export
    formats that write out multiple CDLs will live as methods of the yet unwritten
    container class.

    It's extremely unlikely that the parser functions will ever move to be
    methods of a class (either :class:`ColorCorrection` or the container) as
    it wouldn't make logical sense to instantiate the class, call a parse
    method of that class, then create more copies of itself.

    At some point it may be desirable to create a class representing the input
    file, and at that point that class would definitely contain parse methods.

- Why the underscore?
    ``cdl_convert`` started as a simple script to convert from one format to
    another. As such, it wasn't named with the standards that one would usually
    use for a python module. By the time the project became big enough, was on
    PyPI, etc, it was too spread out, in too many places to make changing easy.
    In the end, I opted to keep it. At some point, ``cdl_convert`` might migrate
    into a larger, more generic film & tv python module, which will be named
    properly.

.. _Travis-ci.org: http://travis-ci.org/shidarin/cdl_convert
.. _coveralls.io: http://coveralls.io/r/shidarin/cdl_convert
.. _google code: http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Comments
.. _landscape.io: http://landscape.io/
.. _issues: http://github.com/shidarin/cdl_convert/issues
