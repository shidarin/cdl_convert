"""
cdl_convert documentation build configuration.
Modernized with MyST support for Markdown documentation.
"""

import sys
from pathlib import Path

# Add project to path for autodoc
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import cdl_convert as cdl

# -- Project information -----------------------------------------------------

project = "cdl_convert"
copyright = cdl.__copyright__
author = "Sean Wallitsch"
version = cdl.__version__
release = cdl.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",  # Auto-generate docs from docstrings
    "sphinx.ext.napoleon",  # Support for Google/NumPy style docstrings
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Link to other project docs
    "myst_parser",  # Markdown support via MyST
]

# MyST configuration
myst_enable_extensions = [
    "colon_fence",  # ::: fences for directives
    "deflist",  # Definition lists
    "fieldlist",  # Field lists
    "substitution",  # Variable substitutions
    "tasklist",  # Task lists with checkboxes
]

# Support both .rst and .md files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document
master_doc = "index"

# Patterns to exclude
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Pygments syntax highlighting style
pygments_style = "sphinx"

# -- Autodoc configuration ---------------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "groupwise",
    "special-members": "__init__",
    "inherited-members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "exclude-members": "__weakref__",
}

from sphinx.ext import autodoc

# # Original order
# autodoc.Documenter.member_order = 0
# autodoc.ExceptionDocumenter.member_order = 10
# autodoc.ClassDocumenter.member_order = 20
# autodoc.FunctionDocumenter.member_order = 30
# autodoc.DataDocumenter.member_order = 40
# autodoc.MethodDocumenter.member_order = 50
# autodoc.AttributeDocumenter.member_order = 60
# autodoc.PropertyDocumenter.member_order = 60

# Overridden
autodoc.Documenter.member_order = 0
autodoc.DataDocumenter.member_order = 10
autodoc.FunctionDocumenter.member_order = 40
autodoc.ClassDocumenter.member_order = 30
autodoc.AttributeDocumenter.member_order = 20
autodoc.PropertyDocumenter.member_order = 20
autodoc.MethodDocumenter.member_order = 50
autodoc.ExceptionDocumenter.member_order = 60

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "opentimelineio": (
        "https://opentimelineio.readthedocs.io/en/latest/",
        None,
    ),
}

# -- HTML output options -----------------------------------------------------

# Use the modern Furo theme (clean, fast, mobile-friendly)
html_theme = "furo"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2962ff",
        "color-brand-content": "#2962ff",
    },
}

html_title = f"{project} {version}"
# html_static_path = ['_static']  # Uncomment and create directory if custom CSS/JS needed

# Add last updated timestamp
html_last_updated_fmt = "%b %d, %Y"

# -- LaTeX output options ----------------------------------------------------

latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
}

latex_documents = [
    (
        master_doc,
        "cdl_convert.tex",
        "cdl\\_convert Documentation",
        "Sean Wallitsch",
        "manual",
    ),
]

# -- Manual page output options ----------------------------------------------

man_pages = [
    (master_doc, "cdl_convert", "cdl_convert Documentation", [author], 1)
]

# -- Texinfo output options --------------------------------------------------

texinfo_documents = [
    (
        master_doc,
        "cdl_convert",
        "cdl_convert Documentation",
        author,
        "cdl_convert",
        "Convert between ASC CDL formats.",
        "Miscellaneous",
    ),
]
