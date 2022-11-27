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

autodoc_preserve_defaults = True
autodoc_type_aliases = {
    "Row": "vesta.chars.Row",
    "Rows": "vesta.chars.Rows",
}


# HTML

html_theme = "furo"
html_title = f"Vesta Documentation ({version})"
html_logo = "_static/logo.png"
html_static_path = ["_static"]
html_copy_source = False
html_show_sourcelink = False
html_show_sphinx = False
