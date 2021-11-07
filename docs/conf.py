import datetime
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from vesta import __version__ as version


# Project

project = "Vesta"
copyright = f"{datetime.date.today().year} Jon Parise"
author = "Jon Parise"
release = version

# General

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# HTML

html_theme = "sphinx_rtd_theme"
html_title = f"Vesta Documentation ({version})"
html_static_path = ["_static"]
html_copy_source = False
html_show_sourcelink = False
html_show_sphinx = False
