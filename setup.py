from setuptools import setup
import codecs
import os
import re

# Instructions for setting up a dist of cdl_convert
#
# Recommended to create a new clone of a fresh master before doing this,
# and trashing the repo afterwards.
#
# 1. Run tests
#       python setup.py test
# 2. Build Sphinx Documentation
#       python setup.py build_sphinx
# 3. Copy the html docs the docs_html folder
#       cp -R docs/_build/html/ ./docs_html/
# 3. Build normal dist and wheel dist
#       python setup.py sdist
#       python setup.py bdist_wheel
# 4. Check the built dists to make sure they are correct
# 5. Upload
#       python setup.py sdist bdist_wheel upload

here = os.path.abspath(os.path.dirname(__file__))
main_file = os.path.join(here, 'cdl_convert', '__init__.py')

# Read the version number from a source file.
# Why read it, and not import?
# see https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion
def find_metadata(filepath):
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(filepath, 'r', 'latin1') as f:
        metadata_file = f.read()

    metadata = {}

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              metadata_file, re.M)
    author_match = re.search(r"^__author__ = ['\"]([^'\"]*)['\"]",
                             metadata_file, re.M)
    copyright_match = re.search(r"^__copyright__ = ['\"]([^'\"]*)['\"]",
                                metadata_file, re.M)
    credits_match = re.search(r"^__credits__ = ['\"]([^'\"]*)['\"]",
                              metadata_file, re.M)
    license_match = re.search(r"^__license__ = ['\"]([^'\"]*)['\"]",
                              metadata_file, re.M)
    maint_match = re.search(r"^__maintainer__ = ['\"]([^'\"]*)['\"]",
                            metadata_file, re.M)
    email_match = re.search(r"^__email__ = ['\"]([^'\"]*)['\"]",
                            metadata_file, re.M)
    status_match = re.search(r"^__status__ = ['\"]([^'\"]*)['\"]",
                             metadata_file, re.M)

    if version_match:
        metadata['version'] = version_match.group(1)
    else:
        # We only absolutely need the version, everything else can
        # have sane defaults
        raise RuntimeError("Unable to find version string.")

    if author_match:
        metadata['author'] = author_match.group(1)
    if copyright_match:
        metadata['copyright'] = copyright_match.group(1)
    if credits_match:
        metadata['credits'] = credits_match.group(1)
    if license_match:
        metadata['license'] = license_match.group(1)
    if maint_match:
        metadata['maintainer'] = maint_match.group(1)
    if email_match:
        metadata['email'] = email_match.group(1)
    if status_match:
        metadata['status'] = status_match.group(1)

    return metadata

metadata = find_metadata(main_file)

# Get the long description from the relevant file
with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="cdl_convert",
    version=metadata['version'],
    description="Converts between common ASC Color Decision List (CDL) formats",
    long_description=long_description,

    # The project URL.
    url='http://github.com/shidarin/cdl_convert',

    # Author details
    author=metadata['author'],
    author_email=metadata['email'],
    maintainer=metadata['maintainer'],

    # Choose your license
    license=metadata['license'],

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',

        # OS
        'Operating System :: OS Independent',

        # Language
        'Natural Language :: English',
    ],

    # What does your project relate to?
    keywords='film tv color conversion converter cdl editing',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages.
    packages=['cdl_convert'],

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed.
    install_requires=['argparse'],

    # Testing
    test_suite='nose.collector',
    tests_require=['nose'],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={},
    include_package_data=True,

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # Targeted OS
    platforms='any',

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'cdl_convert=cdl_convert.cdl_convert:main',
        ],
    },
)
