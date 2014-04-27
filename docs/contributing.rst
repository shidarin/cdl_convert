############
Contributing
############

.. note::
    Portions of this page have been modified from the excellent
    `OpenComparison project docs`_.

Contributing CDL and EDL Samples
================================

Please, *please*, **please** submit samples of the following formats:

- FLEx
- ALE
- CMX
- CCC
- CDL

These are complex formats, and seeing real world samples helps write tests
that ensure correct parsing of real world EDLs and CDLs. If you don't even see
a format of CDL listed that you know exists, open an issue at the github
`issues`_ page asking for parse/write support for the format, and include a
sample.

Issues & Bugs
=============

Take a look at the `issues`_ page and if you see something that you think you
can bang out, leave a comment saying you're going to take it on. While many
issues are already assigned to the principal authors, just because it's assigned
doesn't mean any work has begun.

Feel welcome to post issues, feature requests and bugs that aren't present.

Workflow
========

``cdl_convert`` is a `GitFlow`_ workflow project. If you're not familiar with
GitFlow, please take a moment to read the workflow documentation. Essentially
it means that all work beyond tiny bug fixes needs to be done on it's own
feature branch, called something like ``feature/thing_I_am_fixing``.

After you fork the repository, take a second to create a new feature branch from
the ``develop`` branch and checkout that newly created branch.

Submitting Your Fix
-------------------

Once you've pushed your feature branch to GitHub, it's time to generate a pull
request back to the central ``cdl_convert`` repository.

The pull request let's you attach a comment, and when you're addressing an issue
it's imperative to link to that issue in the initial pull request comment.
We'll shortly be notified of your request and it will be reviewed as soon as
possible.

.. warning::
    If you continue to add commits to the feature branch you submitted as
    a pull request, the pull request will be updated with those changes (as
    long as you push those changes to GitHub). This is why you should not
    submit a pull request of the ``develop`` branch.

Pull Request Tips
=================

``cdl_convert`` really needs your collaboration, but we only have so much time
to work on the project and merge your fixes and features in. There's some easy
to follow guidelines that will ensure your pull request is accepted and integrated
quickly.

Run the tests!
--------------

Before you submit a pull request, please run the entire test suite via
::
    $ python setup.py tests

If the tests are failing, it's likely that you accidentally broke something.
Note which tests are failing, and how your code might have affected them. If
your change is intentional- for example you made it so urls all read ``https://``
instead of ``http://``, adjust the test suite, get it back into a passing state,
and then submit it.

If your code fails the tests (`Travis-ci.org`_ checks all pull requests when
you create them) it will be **rejected**.

Add tests for your new code
---------------------------

If your pull request adds a feature but lacks tests then it will be **rejected**.

Tests are written using the standard unittest framework. Please keep test cases
as simple as possible while maintaining a good coverage of the code you added.

.. warning::
    Tests are currently written in the style of unittest with camelCased
    method & variable names. Please follow :pep:`8` otherwise.

Don't mix code changes with whitespace cleanup
----------------------------------------------

If you change two lines of code and correct 200 lines of whitespace issues in a
file the diff on that pull request is functionally unreadable and will be
**rejected**. Whitespace cleanups need to be in their own pull request.

Keep your pull requests limited to a single issue
--------------------------------------------------

Pull requests should be as small/atomic as possible. Large, wide-sweeping
changes in a pull request will be **rejected**, with comments to isolate the
specific code in your pull request.

Follow PEP-8 and keep your code simple!
---------------------------------------

Memorize the Zen of Python
::
    >>> python -c 'import this'

Please keep your code as clean and straightforward as possible.
When we see more than one or two functions/methods starting with
`_my_special_function` or things like `__builtins__.object = str`
we start to get worried. Rather than try and figure out your brilliant work
we'll just **reject** it and send along a request for simplification.

Furthermore, the pixel shortage is over. We want to see:

* `package` instead of `pkg`
* `grid` instead of `g`
* `my_function_that_does_things` instead of `mftdt`

If the code style doesn't follow :pep:`8` , it's going to be **rejected**.

Copyright of Submitted Contributions
====================================

When submitting, you'll be asked to waive copyright to your submitted code to
the listed authors. This is so we can keep a tight handle on the code and change
the license for future releases if needed.

.. _OpenComparison project docs: http://opencomparison.readthedocs.org/en/latest/contributing.html
.. _Travis-ci.org: http://travis-ci.org/shidarin/cdl_convert
.. _issues: http://github.com/shidarin/cdl_convert/issues
.. _GitFlow: http://nvie.com/posts/a-successful-git-branching-model/
