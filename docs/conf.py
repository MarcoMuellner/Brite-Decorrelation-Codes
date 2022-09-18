"""Sphinx configuration."""
project = "Py-Brite-Decorrelation Codes"
author = "Marco Müllner"
copyright = "2022, Marco Müllner"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
