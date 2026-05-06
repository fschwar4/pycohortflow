"""Export cohort data and resolved style for the Interactive Generator.

The generator (``docs/generator.rst``) accepts two inputs: a JSON list
of cohort steps and an optional TOML overrides block.  This module
serialises a :func:`pycohortflow.plot_cfd` invocation into exactly that
pair of artefacts, so a Python-rendered figure can be reproduced in the
browser without re-running Python.

Two files are produced:

* ``<basename>.cohort.json`` — paste into the generator's
  *Cohort data (JSON)* textarea.
* ``<basename>.style.toml`` — paste into the *TOML overrides* textarea.

The JSON wraps the data list in an envelope with a ``_meta`` block so
``figure_title`` and ``transparent`` round-trip too::

    {
      "_meta": {
        "pycohortflow_version": "0.1.4",
        "exported_at": "2026-05-04T...",
        "figure_title": "My Study",
        "transparent": false
      },
      "data": [ {"heading": "...", "N": 350}, ... ]
    }

The Interactive Generator's JS reads ``_meta.figure_title`` and
``_meta.transparent`` on paste and auto-populates the matching inputs.
For backwards compatibility the JS also accepts a bare list (legacy
form) without an envelope.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import tomli_w

from pycohortflow.cfd_util import (
    _package_version,
    apply_kwarg_overrides,
    load_style_config,
)

__all__ = ["export"]


def _resolve_full_config(
    style: str,
    style_config_path: str | Path | None,
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    """Build the resolved config that ``plot_cfd`` would render with.

    Delegates to :func:`pycohortflow.cfd_util.apply_kwarg_overrides`,
    which is the single source of truth for kwargs that map onto TOML
    config keys.  Kwargs without a TOML equivalent (``main_palette``,
    ``exclusion_palette``, ``transparent``, ``figure_title``) are
    handled elsewhere — they are NOT written into the TOML.
    """
    cfg = load_style_config(style=style, custom_config_path=style_config_path)
    apply_kwarg_overrides(cfg, kwargs)
    return cfg


def _bake_palette_into_data(
    data: list[dict[str, Any]],
    kwargs: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return a deep copy of *data* with palette kwargs baked in.

    ``main_palette``/``exclusion_palette`` kwargs to ``plot_cfd`` have
    no TOML equivalent (the TOML schema only carries gradient
    start/end colours).  To keep the JS-side rendering identical, we
    inject the matplotlib-resolved colour as a per-node ``"color"`` /
    ``"exclusion_color"`` entry in the exported JSON.

    Existing per-node overrides take precedence over the palette,
    matching :func:`plot_cfd`'s own colour-resolution semantics (the
    ``node.get("color", main_palette[i])`` fallback chain).  The
    original input list is never mutated; nested mutable values inside
    each node are deep-copied so callers can mutate the result without
    affecting their input.
    """
    main_palette = kwargs.get("main_palette")
    excl_palette = kwargs.get("exclusion_palette")

    baked: list[dict[str, Any]] = []
    for i, node in enumerate(data):
        new_node = copy.deepcopy(node)
        if main_palette and "color" not in new_node and i < len(main_palette):
            new_node["color"] = main_palette[i]
        if excl_palette and "exclusion_color" not in new_node and i < len(excl_palette):
            new_node["exclusion_color"] = excl_palette[i]
        baked.append(new_node)
    return baked


class _DataJSONEncoder(json.JSONEncoder):
    """Tolerant JSON encoder for cohort data.

    Falls back to ``.item()`` for numpy/pandas scalars and ``str()``
    for :class:`pathlib.Path` (since users sometimes pass paths in
    description fields).
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Path):
            return str(obj)
        # numpy / pandas scalars: int64, float64, bool_, etc. all expose .item()
        item = getattr(obj, "item", None)
        if callable(item):
            try:
                return item()
            except (TypeError, ValueError):
                pass
        return super().default(obj)


def export(
    data: list[dict[str, Any]],
    *,
    style: str = "white",
    style_config_path: str | Path | None = None,
    figure_title: str | None = None,
    transparent: bool = False,
    out_dir: str | Path | None = None,
    basename: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Export cohort *data* and the resolved style for the Interactive Generator.

    The arguments mirror :func:`plot_cfd`: pass the same combination
    you used when plotting and the export captures exactly that
    rendering.

    Args:
        data: Ordered list of cohort node dicts (same shape as
            :func:`plot_cfd` accepts).  The list is not mutated.
        style: Name of the built-in style used as the base.  One of
            ``"white"``, ``"colorful"``, ``"minimal"``.
        style_config_path: Optional path to a custom TOML style file
            that overrides the built-in style.
        figure_title: Optional figure title.  When non-``None`` it is
            written to the JSON ``_meta.figure_title`` field; the JS
            generator auto-populates the title input on paste.
        transparent: Background-transparency flag.  Always written to
            ``_meta.transparent``; the JS generator auto-populates the
            transparent checkbox on paste.
        out_dir: Directory to write the two files into.  Created if
            missing.  When ``None``, no files are written and only the
            in-memory strings are returned.
        basename: File-name stem for the export pair.  Paired with
            *out_dir*.  Required to write to disk.
        **kwargs: Same ad-hoc overrides accepted by :func:`plot_cfd`.
            ``dpi`` and ``figsize`` are baked into the TOML's
            ``[figure]`` section; ``main_palette`` /
            ``exclusion_palette`` are baked into per-node ``"color"`` /
            ``"exclusion_color"`` entries in the data JSON.

    Returns:
        A dict with these keys:

        * ``"cohort_json"`` (``str``) — the JSON contents to paste into
          the *Cohort data (JSON)* textarea.
        * ``"style_toml"`` (``str``) — the TOML contents to paste into
          the *TOML overrides* textarea.
        * ``"json_path"`` (:class:`pathlib.Path` | ``None``) — the
          file path written, or ``None`` when no files were requested.
        * ``"toml_path"`` (:class:`pathlib.Path` | ``None``) — same.

    Raises:
        ValueError: If *style* is not a recognised built-in style, or
            if exactly one of *out_dir* / *basename* is provided
            (both or neither, never just one).

    Example:
        Export and round-trip in Python::

            >>> from pycohortflow import export
            >>> data = [{"heading": "Registered", "N": 350}, {"heading": "Final", "N": 100}]
            >>> result = export(data, style="colorful", figure_title="My Study")
            >>> "_meta" in result["cohort_json"]
            True
            >>> "[figure]" in result["style_toml"]
            True

        Write the pair to disk alongside the figure::

            >>> from pycohortflow import plot_cfd, export
            >>> fig, ax = plot_cfd(data, style="colorful", save_dir="out", img_name="study")
            >>> export(data, style="colorful", out_dir="out", basename="study")  # doctest: +SKIP

    """
    if (out_dir is None) != (basename is None):
        raise ValueError(
            "out_dir and basename must be provided together (or both omitted "
            "to return strings only)."
        )

    # 1. Resolve the full TOML config (this also validates `style`).
    cfg = _resolve_full_config(style, style_config_path, kwargs)
    style_toml = tomli_w.dumps(cfg)

    # 2. Bake palette kwargs into per-node colours.
    baked_data = _bake_palette_into_data(data, kwargs)

    # 3. Wrap the data in the envelope with metadata.
    envelope = {
        "_meta": {
            "pycohortflow_version": _package_version(),
            "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "figure_title": figure_title,
            "transparent": bool(transparent),
        },
        "data": baked_data,
    }
    cohort_json = json.dumps(envelope, indent=2, ensure_ascii=False, cls=_DataJSONEncoder)

    result: dict[str, Any] = {
        "cohort_json": cohort_json,
        "style_toml": style_toml,
        "json_path": None,
        "toml_path": None,
    }

    if out_dir is not None and basename is not None:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        json_path = out / f"{basename}.cohort.json"
        toml_path = out / f"{basename}.style.toml"
        json_path.write_text(cohort_json + "\n", encoding="utf-8")
        toml_path.write_text(style_toml, encoding="utf-8")
        result["json_path"] = json_path
        result["toml_path"] = toml_path

    return result
