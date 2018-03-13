##########################
Frequently Asked Questions
##########################

Python 2 & 3 Support
====================

- What versions of Python does ``cdl_convert`` support?
    ``cdl_convert`` works in Python 2.7 through 3.4 and PyPy. A full test suite
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

- Why the underscore?
    ``cdl_convert`` started as a simple script to convert from one format to
    another. As such, it wasn't named with the standards that one would usually
    use for a python module. By the time the project became big enough, was on
    PyPI, etc, it was too spread out on the web, in too many places to make
    changing easy. In the end, I opted to keep it. At some point,
    ``cdl_convert`` might migrate into a larger, more generic film & tv
    python module, which will be named properly.

.. _Travis-ci.org: http://travis-ci.org/shidarin/cdl_convert
.. _coveralls.io: http://coveralls.io/r/shidarin/cdl_convert
.. _google code: http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Comments
.. _landscape.io: http://landscape.io/
.. _issues: http://github.com/shidarin/cdl_convert/issues
