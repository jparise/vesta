import datetime
import os
import re


def get_version(filename):
    docsdir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(docsdir, filename)) as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = \"([^\"]*)\"", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Project

project = "Vesta"
copyright = f"{datetime.date.today().year} Jon Parise"
author = "Jon Parise"
version = get_version("../vesta/__init__.py")
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
