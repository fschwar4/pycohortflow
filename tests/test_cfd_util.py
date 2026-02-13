"""Tests for pycohortflow.cfd_util — utility functions."""

import pytest

from pycohortflow.cfd_util import (
    _hex_to_rgb,
    _interpolate_color,
    _recursive_update,
    _rgb_to_hex,
    get_matplotlib_named_colors,
    gradient_palette,
    load_style_config,
    named_color,
    resolve_color,
    wrap_lines,
)

# ---------------------------------------------------------------------------
# wrap_lines
# ---------------------------------------------------------------------------


class TestWrapLines:
    """Tests for the text wrapping helper."""

    def test_empty_string(self):
        """Verify an empty string returns an empty list."""
        assert wrap_lines("", 20) == []

    def test_short_string(self):
        """Verify a string within width returns a single-element list."""
        assert wrap_lines("hello", 20) == ["hello"]

    def test_wraps_correctly(self):
        """Verify a long string is wrapped into lines within width."""
        result = wrap_lines("one two three four", width=10)
        assert len(result) >= 2
        assert all(len(line) <= 10 for line in result)


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------


class TestColourHelpers:
    """Tests for low-level colour conversion functions."""

    def test_hex_to_rgb(self):
        """Verify hex-to-RGB conversion for primary colours."""
        assert _hex_to_rgb("#ff0000") == (255, 0, 0)
        assert _hex_to_rgb("#00ff00") == (0, 255, 0)

    def test_hex_to_rgb_strips_alpha(self):
        """Verify 8-digit hex strings are truncated to RGB."""
        assert _hex_to_rgb("#ff000080") == (255, 0, 0)

    def test_rgb_to_hex(self):
        """Verify RGB-to-hex conversion produces a lowercase string."""
        assert _rgb_to_hex((255, 0, 0)) == "#ff0000"

    def test_roundtrip(self):
        """Verify hex-RGB-hex roundtrip preserves the original value."""
        original = "#1a2b3c"
        assert _rgb_to_hex(_hex_to_rgb(original)) == original

    def test_interpolate_endpoints(self):
        """Verify interpolation at t=0 and t=1 returns the endpoints."""
        assert _interpolate_color("#000000", "#ffffff", 0.0) == "#000000"
        assert _interpolate_color("#000000", "#ffffff", 1.0) == "#ffffff"

    def test_interpolate_midpoint(self):
        """Verify midpoint interpolation between black and white."""
        mid = _interpolate_color("#000000", "#ffffff", 0.5)
        assert mid == "#808080"

    def test_named_color(self):
        """Verify named_color resolves 'red' to its hex value."""
        assert named_color("red") == "#ff0000"

    def test_named_colors_list(self):
        """Verify get_matplotlib_named_colors returns a list with 'red'."""
        colors = get_matplotlib_named_colors()
        assert isinstance(colors, list)
        assert "red" in colors


# ---------------------------------------------------------------------------
# gradient_palette
# ---------------------------------------------------------------------------


class TestGradientPalette:
    """Tests for gradient palette generation."""

    def test_single_colour(self):
        """Verify a palette of length 1 returns only the start colour."""
        result = gradient_palette("#ff0000", "#0000ff", 1)
        assert result == ["#ff0000"]

    def test_correct_length(self):
        """Verify the palette has the requested number of entries."""
        result = gradient_palette("#000000", "#ffffff", 5)
        assert len(result) == 5

    def test_endpoints(self):
        """Verify first and last entries match start and end colours."""
        result = gradient_palette("#000000", "#ffffff", 3)
        assert result[0] == "#000000"
        assert result[-1] == "#ffffff"


# ---------------------------------------------------------------------------
# resolve_color
# ---------------------------------------------------------------------------


class TestResolveColor:
    """Tests for colour resolution with fallback and validation."""

    def test_none_uses_default(self):
        """Verify None falls back to the provided default colour."""
        assert resolve_color(None, "#aabbcc") == "#aabbcc"

    def test_explicit_value(self):
        """Verify a named colour is resolved to its hex equivalent."""
        assert resolve_color("red", "#000000") == "#ff0000"

    def test_named_color_disallowed(self):
        """Verify named colours raise ValueError when disallowed."""
        with pytest.raises(ValueError, match="allow_named_colors"):
            resolve_color("red", "#000000", allow_named_colors=False)

    def test_invalid_color(self):
        """Verify an invalid colour string raises ValueError."""
        with pytest.raises(ValueError):
            resolve_color("not_a_color_at_all", "#000000")


# ---------------------------------------------------------------------------
# _recursive_update
# ---------------------------------------------------------------------------


class TestRecursiveUpdate:
    """Tests for deep dictionary merge used in config layering."""

    def test_flat_merge(self):
        """Verify top-level keys are merged with override and addition."""
        base = {"a": 1, "b": 2}
        result = _recursive_update(base, {"b": 99, "c": 3})
        assert result == {"a": 1, "b": 99, "c": 3}

    def test_nested_merge(self):
        """Verify nested dicts are merged recursively."""
        base = {"x": {"y": 1, "z": 2}}
        result = _recursive_update(base, {"x": {"z": 99}})
        assert result == {"x": {"y": 1, "z": 99}}


# ---------------------------------------------------------------------------
# load_style_config
# ---------------------------------------------------------------------------


class TestLoadStyleConfig:
    """Tests for the TOML-based style configuration loader."""

    def test_white_style(self):
        """Verify the 'white' style sets main_start to white."""
        cfg = load_style_config("white")
        assert cfg["colors"]["main_start"] == "#ffffff"

    def test_colorful_style(self):
        """Verify the 'colorful' style uses non-white colours."""
        cfg = load_style_config("colorful")
        assert cfg["colors"]["main_start"] != "#ffffff"

    def test_unknown_style_raises(self):
        """Verify an unknown style name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown built-in style"):
            load_style_config("galaxy")

    def test_all_sections_present(self):
        """Verify all required config sections are present."""
        cfg = load_style_config()
        for section in ("figure", "layout", "box_geometry", "text", "lines", "colors"):
            assert section in cfg, f"Missing section: {section}"
