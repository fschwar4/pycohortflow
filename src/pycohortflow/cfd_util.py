"""Utility helpers for the pycohortflow package.

This module provides colour handling, text wrapping, figure saving, and
TOML-based style configuration loading used internally by
:func:`pycohortflow.plot_cohort_flow_diagram`.
"""

import textwrap
from importlib import resources
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python < 3.11

import matplotlib.colors as mcolors

__all__ = [
    "save_figure",
    "wrap_lines",
    "get_matplotlib_named_colors",
    "named_color",
    "gradient_palette",
    "resolve_color",
    "load_style_config",
]

# Mapping of built-in style short-names to TOML file names inside the
# ``styles/`` sub-package shipped with pycohortflow.
_BUILTIN_STYLES = {
    "white": "default_style_white.toml",
    "colorful": "default_style_colorful.toml",
}


# ---------------------------------------------------------------------------
# Figure I/O
# ---------------------------------------------------------------------------


def save_figure(fig, save_dir, img_name, save_format):
    """Save a Matplotlib figure to disk in one or more formats.

    The function creates *save_dir* if it does not already exist and writes
    the figure for every format listed in *save_format*.

    Args:
        fig (matplotlib.figure.Figure): The figure object to save.
        save_dir (str | os.PathLike | None): Directory to write into.
            Defaults to the current working directory when ``None``.
        img_name (str): Base file name **without** extension.
        save_format (str | list[str]): One format string (e.g. ``"png"``)
            or a list of format strings (e.g. ``["png", "svg", "pdf"]``).

    Returns:
        None

    Example:
        >>> save_figure(fig, "output", "my_chart", ["png", "svg"])
        Saved: output/my_chart.png
        Saved: output/my_chart.svg

    """
    if not img_name:
        return

    output_dir = Path(save_dir) if save_dir is not None else Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(save_format, str):
        save_format = [save_format]

    for fmt in save_format:
        clean_fmt = fmt.lstrip(".")
        full_path = output_dir / f"{img_name}.{clean_fmt}"
        fig.savefig(full_path, bbox_inches="tight", dpi=300)
        print(f"Saved: {full_path}")


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def wrap_lines(text, width):
    """Wrap a string into a list of lines that fit within *width* characters.

    Uses :func:`textwrap.wrap` with ``break_long_words=False`` so that words
    are never split mid-word.

    Args:
        text (str): The input string to wrap.
        width (int): Maximum number of characters per line.

    Returns:
        list[str]: Wrapped lines.  Returns an empty list for blank input
        and a single-element list when the text cannot be broken.

    Example:
        >>> wrap_lines("A rather long description text", width=15)
        ['A rather long', 'description', 'text']

    """
    if not text:
        return []
    wrapped = textwrap.wrap(text, width=width, break_long_words=False)
    return wrapped or [text]


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------


def get_matplotlib_named_colors():
    """Return a sorted list of all Matplotlib named colour strings.

    Useful for discovering valid colour names that can be used in the
    ``color`` or ``exclusion_color`` fields of cohort data dictionaries.

    Returns:
        list[str]: Sorted colour names recognised by Matplotlib.

    Example:
        >>> "steelblue" in get_matplotlib_named_colors()
        True

    """
    return sorted(mcolors.get_named_colors_mapping().keys())


def named_color(name):
    """Resolve a Matplotlib colour name or specification to a hex string.

    Args:
        name (str): Any valid Matplotlib colour specification — e.g.
            ``"steelblue"``, ``"C0"``, ``"#aabbcc"``, or ``"tab:blue"``.

    Returns:
        str: A lowercase ``#RRGGBB`` hex string.

    Raises:
        ValueError: If *name* is not a recognised colour specification.

    Example:
        >>> named_color("white")
        '#ffffff'

    """
    return mcolors.to_hex(name, keep_alpha=False)


def _hex_to_rgb(hex_color):
    """Convert a ``#RRGGBB`` (or ``#RRGGBBAA``) hex string to an RGB tuple.

    Args:
        hex_color (str): Hex colour string.  An optional leading ``#`` and
            alpha channel are stripped automatically.

    Returns:
        tuple[int, int, int]: ``(r, g, b)`` with each component in 0–255.

    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 8:  # #RRGGBBAA → strip alpha
        hex_color = hex_color[:6]
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    """Convert an ``(r, g, b)`` tuple (0–255 per channel) to ``#RRGGBB``.

    Args:
        rgb (tuple[int, int, int]): Red, green, blue channel values.

    Returns:
        str: Lowercase hex colour string.

    """
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _interpolate_color(start_hex, end_hex, t):
    """Linearly interpolate between two hex colours.

    Args:
        start_hex (str): Start colour in ``#RRGGBB`` format.
        end_hex (str): End colour in ``#RRGGBB`` format.
        t (float): Interpolation factor in ``[0, 1]``.  ``0`` returns
            *start_hex*, ``1`` returns *end_hex*.

    Returns:
        str: Interpolated colour as a ``#RRGGBB`` hex string.

    """
    sr, sg, sb = _hex_to_rgb(start_hex)
    er, eg, eb = _hex_to_rgb(end_hex)
    rgb = (
        int(round(sr + (er - sr) * t)),
        int(round(sg + (eg - sg) * t)),
        int(round(sb + (eb - sb) * t)),
    )
    return _rgb_to_hex(rgb)


def gradient_palette(start_hex, end_hex, n):
    """Generate *n* hex colours that blend linearly from *start* to *end*.

    Args:
        start_hex (str): Starting colour (any Matplotlib colour spec).
        end_hex (str): Ending colour (any Matplotlib colour spec).
        n (int): Number of colours to generate.

    Returns:
        list[str]: List of ``#RRGGBB`` hex colour strings.

    Example:
        >>> gradient_palette("#000000", "#ffffff", 3)
        ['#000000', '#808080', '#ffffff']

    """
    if n <= 1:
        return [start_hex]
    s_hex = mcolors.to_hex(start_hex, keep_alpha=False)
    e_hex = mcolors.to_hex(end_hex, keep_alpha=False)
    return [_interpolate_color(s_hex, e_hex, i / (n - 1)) for i in range(n)]


def resolve_color(color_value, default_value, allow_named_colors=True):
    """Resolve and normalise a colour value to a ``#RRGGBB`` hex string.

    The function first falls back to *default_value* when *color_value* is
    ``None``, then validates the result against Matplotlib's colour parser.

    Args:
        color_value (str | None): User-supplied colour.  ``None`` means
            "use the default".
        default_value (str): Fallback colour when *color_value* is ``None``.
        allow_named_colors (bool): If ``False``, only hex strings
            (starting with ``#``) are accepted; named colours such as
            ``"steelblue"`` raise :class:`ValueError`.

    Returns:
        str: Normalised ``#RRGGBB`` hex colour string.

    Raises:
        ValueError: If the resolved colour is invalid or if named colours
            are disallowed and a non-hex value is provided.

    Example:
        >>> resolve_color(None, "#aabbcc")
        '#aabbcc'
        >>> resolve_color("red", "#000000")
        '#ff0000'

    """
    value = default_value if color_value is None else color_value

    if isinstance(value, str) and not allow_named_colors and not value.startswith("#"):
        raise ValueError(
            f"Unsupported color '{value}' when allow_named_colors=False. "
            "Use hex colors like '#88ccff'."
        )
    try:
        return mcolors.to_hex(value, keep_alpha=False)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported color '{value}'. Use hex or Matplotlib named colors. "
            "See get_matplotlib_named_colors()."
        ) from exc


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _recursive_update(default, override):
    """Recursively merge *override* into *default* (in-place).

    Nested dictionaries are merged key-by-key; all other value types in
    *override* simply replace those in *default*.

    Args:
        default (dict): Base configuration dictionary (modified in-place).
        override (dict): Dictionary whose values take precedence.

    Returns:
        dict: The mutated *default* dictionary.

    """
    for key, value in override.items():
        if isinstance(value, dict) and key in default:
            default[key] = _recursive_update(default[key], value)
        else:
            default[key] = value
    return default


def load_style_config(style="white", custom_config_path=None):
    """Load the TOML style configuration for the flow diagram.

    The function reads one of the **bundled** style files shipped with the
    package and optionally deep-merges a user-provided TOML file on top.
    This lets users override only the keys they care about while inheriting
    sensible defaults for everything else.

    Args:
        style (str): Name of the built-in style to use as the base.
            Currently available: ``"white"`` (no background colours,
            default) and ``"colorful"`` (pastel gradient backgrounds).
        custom_config_path (str | os.PathLike | None): Path to a custom
            TOML file.  When ``None`` (the default), only the built-in
            style is used.

    Returns:
        dict: Nested configuration dictionary with sections such as
        ``"figure"``, ``"layout"``, ``"box_geometry"``, ``"text"``,
        ``"lines"``, and ``"colors"``.

    Raises:
        ValueError: If *style* is not one of the recognised built-in style
            names.

    Example:
        >>> cfg = load_style_config()
        >>> cfg["figure"]["dpi"]
        200
        >>> cfg = load_style_config("colorful", "my_overrides.toml")

    """
    # 1. Resolve built-in style
    if style not in _BUILTIN_STYLES:
        raise ValueError(
            f"Unknown built-in style '{style}'. Available styles: {sorted(_BUILTIN_STYLES)}"
        )

    toml_filename = _BUILTIN_STYLES[style]

    try:
        style_file = resources.files("pycohortflow").joinpath("styles").joinpath(toml_filename)
        config = tomllib.loads(style_file.read_text(encoding="utf-8"))
    except Exception:
        # Minimal hard-coded fallback (white style)
        config = {
            "figure": {
                "dpi": 200,
                "figsize_width": 12,
                "figsize_height": 8,
                "title_fontsize": 16,
                "title_fontweight": "bold",
                "title_pad": 20,
            },
            "layout": {
                "main_title_width": 26,
                "main_text_width": 34,
                "exclusion_text_width": 30,
                "main_box_width": 2.8,
                "exclusion_box_width": 2.6,
                "base_gap": 0.8,
                "side_gap": 1.2,
                "top_margin": 0.8,
                "bottom_margin": 0.8,
                "x_padding": 0.6,
            },
            "box_geometry": {
                "padding": 0.52,
                "title_line_height": 0.42,
                "body_line_height": 0.33,
                "title_body_gap": 0.16,
                "text_top_padding": 0.24,
                "min_main_height": 1.6,
                "min_exclusion_height": 1.2,
                "clearance": 0.2,
                "corner_radius": 0.05,
                "pad_factor": 0.03,
            },
            "text": {
                "fontsize_title": 12,
                "fontsize_main": 10,
                "fontsize_exclusion": 9,
            },
            "lines": {
                "box_linewidth": 1,
                "connector_linewidth": 1,
                "arrow_mutation_scale": 20,
                "junction_radius": 0.004,
            },
            "colors": {
                "allow_named_colors": True,
                "main_start": "#ffffff",
                "main_end": "#ffffff",
                "exclusion_start": "#ffffff",
                "exclusion_end": "#ffffff",
            },
        }

    # 2. Merge user overrides
    if custom_config_path:
        custom_path = Path(custom_config_path)
        if custom_path.exists():
            with open(custom_path, "rb") as f:
                user_config = tomllib.load(f)
            config = _recursive_update(config, user_config)
        else:
            print(f"Warning: Custom config path '{custom_config_path}' does not exist. Ignoring.")

    return config
