"""Tests for pycohortflow.cfd_util — utility functions."""

import pytest

from pycohortflow.cfd_util import (
    _hex_to_rgb,
    _interpolate_color,
    _recursive_update,
    _rgb_to_hex,
    gradient_palette,
    load_style_config,
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

    def test_interpolate_endpoints(self):
        """Verify interpolation at t=0 and t=1 returns the endpoints."""
        assert _interpolate_color("#000000", "#ffffff", 0.0) == "#000000"
        assert _interpolate_color("#000000", "#ffffff", 1.0) == "#ffffff"


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

    def test_zero_or_negative_returns_empty(self):
        """Verify n <= 0 returns an empty list (single guard branch)."""
        assert gradient_palette("#000000", "#ffffff", 0) == []
        assert gradient_palette("#000000", "#ffffff", -1) == []


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

    def test_does_not_mutate_original(self):
        """Verify _recursive_update does not modify the original dict."""
        base = {"a": 1, "nested": {"b": 2, "c": 3}}
        original_base = {"a": 1, "nested": {"b": 2, "c": 3}}
        _recursive_update(base, {"a": 99, "nested": {"c": 99}})
        assert base == original_base

    def test_returns_new_dict(self):
        """Verify _recursive_update returns a new dictionary object."""
        base = {"a": 1}
        result = _recursive_update(base, {"b": 2})
        assert result is not base


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

    def test_minimal_style(self):
        """Verify the 'minimal' style sets the new mode + weight defaults."""
        cfg = load_style_config("minimal")
        assert cfg["exclusion"]["mode"] == "text"
        assert cfg["text"]["heading_fontweight"] == "normal"

    def test_box_mode_default_for_white_and_colorful(self):
        """Verify white and colorful styles default to exclusion.mode='box'."""
        for style in ("white", "colorful"):
            cfg = load_style_config(style)
            assert cfg["exclusion"]["mode"] == "box"
            assert cfg["text"]["heading_fontweight"] == "bold"

    def test_unknown_style_raises(self):
        """Verify an unknown style name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown built-in style"):
            load_style_config("galaxy")

    def test_all_sections_present(self):
        """Verify all required config sections are present."""
        cfg = load_style_config()
        for section in (
            "figure",
            "layout",
            "box_geometry",
            "text",
            "lines",
            "colors",
            "exclusion",
        ):
            assert section in cfg, f"Missing section: {section}"

    def test_custom_config_override(self, tmp_path):
        """Verify a custom TOML file overrides specific values."""
        toml_file = tmp_path / "override.toml"
        toml_file.write_text("[figure]\ndpi = 42\n")

        cfg = load_style_config("white", custom_config_path=str(toml_file))
        assert cfg["figure"]["dpi"] == 42
        # Other values should remain at default
        assert cfg["figure"]["figsize_width"] == 12

    def test_missing_custom_config_warns(self):
        """Verify a missing custom config path emits a warning."""
        with pytest.warns(UserWarning, match="does not exist"):
            cfg = load_style_config("white", custom_config_path="/nonexistent.toml")
        # Should still return a valid config
        assert "figure" in cfg
