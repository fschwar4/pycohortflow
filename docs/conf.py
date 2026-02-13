"""Sphinx configuration for pycohortflow documentation."""

import os
import sys
from importlib.metadata import metadata

# Make the package importable for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# -- Single-source metadata from pyproject.toml ------------------------------
_meta = metadata("pycohortflow")
project = _meta["Name"]
author = _meta.get("Author", "fschwar4")
release = _meta["Version"]
copyright = f"2026, {author}"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",        # Google-style docstrings
    "sphinx.ext.viewcode",        # [source] links
    "sphinx.ext.intersphinx",     # Cross-reference external docs
    "sphinx_autodoc_typehints",   # Render type hints nicely
    "sphinx_copybutton",          # Copy button on code blocks
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Napoleon settings (Google Style)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# Autodoc settings
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Intersphinx mappings
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}

# -- Options for HTML output (PyData Sphinx Theme) ---------------------------
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "_static/logo_wide.svg"
html_favicon = "_static/favicon.png"

html_theme_options = {
    "navigation_depth": 4,
    "show_nav_level": 2,
    "show_toc_level": 3,
    "collapse_navigation": False,
    "navbar_align": "left",
    "navbar_start": ["navbar-logo"],
    "secondary_sidebar_items": ["page-toc"],
    "show_version_warning_banner": False,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/fschwar4/pycohortflow",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/pycohortflow/",
            "icon": "fa-solid fa-box",
        },
    ],
}

# The wide logo already contains the project name, so suppress the
# separate text title to avoid duplication.
html_short_title = project
version = ""  # hide version in sidebar header
