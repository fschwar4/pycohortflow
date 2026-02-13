"""pycohortflow — lightweight cohort flow diagrams built on Matplotlib.

This package provides a single high-level function,
:func:`plot_cohort_flow_diagram`, that turns a plain Python list of cohort
steps into a publication-ready vertical flow diagram.  Appearance is fully
customisable via TOML configuration files.

Typical usage::

    from pycohortflow import plot_cohort_flow_diagram

    data = [
        {"heading": "Registered", "N": 350},
        {"heading": "Screened",   "N": 150, "exclusion_description": "Not eligible"},
        {"heading": "Analysed",   "N": 120, "exclusion_description": "Lost to follow-up"},
    ]

    fig, ax = plot_cohort_flow_diagram(data, figure_title="My Study")
"""

from importlib.metadata import metadata as _metadata

from pycohortflow.cfd import plot_cohort_flow_diagram
from pycohortflow.cfd_util import (
    get_matplotlib_named_colors,
    gradient_palette,
    load_style_config,
    resolve_color,
)

# Single-source metadata from pyproject.toml via importlib.metadata
_meta = _metadata("pycohortflow")
__version__ = _meta["Version"]
__author__ = _meta.get("Author", "")

__all__ = [
    "plot_cohort_flow_diagram",
    "gradient_palette",
    "get_matplotlib_named_colors",
    "load_style_config",
    "resolve_color",
]
