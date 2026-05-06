"""pycohortflow — lightweight cohort flow diagrams built on Matplotlib.

This package provides a single high-level function,
:func:`plot_cfd`, that turns a plain Python list of cohort
steps into a publication-ready vertical flow diagram.  Appearance is fully
customisable via TOML configuration files.

Typical usage::

    from pycohortflow import plot_cfd

    data = [
        {"heading": "Registered", "N": 350},
        {"heading": "Screened",   "N": 150, "exclusion_description": "Not eligible"},
        {"heading": "Analysed",   "N": 120, "exclusion_description": "Lost to follow-up"},
    ]

    fig, ax = plot_cfd(data, figure_title="My Study")

To also export the data and resolved style for the Interactive Generator
in one call, use :func:`plot_and_export`.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata as _metadata
from typing import Any

from pycohortflow.cfd import plot_cfd
from pycohortflow.cfd_util import (
    _package_version,
    get_matplotlib_named_colors,
    gradient_palette,
    load_style_config,
    resolve_color,
)
from pycohortflow.export import export

# Single-source metadata from pyproject.toml via importlib.metadata.
# Version goes through the shared helper so export.py's _meta block and
# __version__ here can never drift.
__version__ = _package_version()
try:
    __author__ = _metadata("pycohortflow").get("Author", "")
except PackageNotFoundError:
    __author__ = ""


def plot_and_export(
    data: list[dict[str, Any]],
    *,
    out_dir: str | None = None,
    name: str | None = None,
    **kwargs: Any,
) -> tuple[Any, Any, dict[str, Any]]:
    """Plot a cohort flow diagram and export its inputs in one call.

    Thin convenience wrapper around :func:`plot_cfd` and :func:`export`
    that emits a figure plus the data + resolved style needed to
    reproduce it in the Interactive Generator.
    Both *out_dir* and *name* (when provided) are used for the figure
    output (``save_dir`` / ``img_name``) and for the export pair
    (``out_dir`` / ``basename``), so a typical invocation produces::

        out_dir/<name>.png            (figure)
        out_dir/<name>.cohort.json    (export — paste into "Cohort data")
        out_dir/<name>.style.toml     (export — paste into "TOML overrides")

    Args:
        data: Ordered list of cohort node dicts.
        out_dir: Directory to write the figure(s) and export pair.
            ``None`` means do not write to disk; the figure is still
            rendered in memory and the export strings are returned.
        name: Stem used for both the saved figure and the export files.
            Required when *out_dir* is set.
        **kwargs: Forwarded to :func:`plot_cfd` and :func:`export` —
            ``style``, ``style_config_path``, ``figure_title``,
            ``transparent``, ``dpi``, ``figsize``, ``save_format``,
            ``main_palette``, ``exclusion_palette``, ``ax``, ``verbose``,
            etc.  Passing any of ``save_dir``, ``img_name``, or
            ``basename`` raises :class:`TypeError` — use *out_dir* and
            *name* instead.

    Returns:
        ``(fig, ax, export_result)`` — the same ``(Figure, Axes)``
        returned by :func:`plot_cfd`, plus the dict returned by
        :func:`export`.

    Raises:
        TypeError: If any of ``save_dir`` / ``img_name`` / ``basename``
            is passed via ``**kwargs`` (use *out_dir* / *name* instead).
        ValueError: If exactly one of *out_dir* / *name* is provided
            (both or neither, never just one).

    Example:
        >>> from pycohortflow import plot_and_export
        >>> data = [{"heading": "Registered", "N": 350},
        ...         {"heading": "Final", "N": 120}]
        >>> fig, ax, exp = plot_and_export(  # doctest: +SKIP
        ...     data,
        ...     out_dir="output",
        ...     name="study",
        ...     style="colorful",
        ...     figure_title="My Study",
        ...     save_format=["png", "pdf"],
        ... )
        >>> exp["json_path"].name  # doctest: +SKIP
        'study.cohort.json'

    """
    # 1. Reject kwargs that would conflict with the wrapper's own
    #    arguments instead of silently dropping them.  Silent drops
    #    surprise users when nothing lands at the path they expect.
    conflicts = {"save_dir", "img_name", "basename"} & kwargs.keys()
    if conflicts:
        raise TypeError(
            f"plot_and_export does not accept {sorted(conflicts)!r}; "
            "use the `out_dir` and `name` arguments instead."
        )

    # 2. Reject mismatched out_dir / name.  Without this guard, a stray
    #    `out_dir="x"` (no `name`) would render the figure in memory,
    #    skip writing it (img_name is None), and only surface as a
    #    confusing ValueError from `export()` half-way through.
    if (out_dir is None) != (name is None):
        raise ValueError(
            "out_dir and name must be provided together (or both omitted "
            "to keep everything in memory)."
        )

    fig, ax = plot_cfd(data, save_dir=out_dir, img_name=name, **kwargs)
    export_result = export(data, out_dir=out_dir, basename=name, **kwargs)
    return fig, ax, export_result


__all__ = [
    "plot_cfd",
    "plot_and_export",
    "export",
    "gradient_palette",
    "get_matplotlib_named_colors",
    "load_style_config",
    "resolve_color",
]
