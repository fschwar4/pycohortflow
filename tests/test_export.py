"""Tests for ``pycohortflow.export`` and the ``plot_and_export`` wrapper."""

import json

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")  # non-interactive backend for CI

from pycohortflow import export, plot_and_export
from pycohortflow.cfd_util import load_style_config


@pytest.fixture
def sample_data():
    """Three-step cohort with exclusion descriptions."""
    return [
        {"heading": "Registered", "N": 100},
        {"heading": "Screened", "N": 80, "exclusion_description": "Not eligible"},
        {"heading": "Analysed", "N": 60, "exclusion_description": "Withdrew"},
    ]


# ---------------------------------------------------------------------------
# Strings-only mode
# ---------------------------------------------------------------------------


class TestExportStrings:
    """In-memory exports (no out_dir / basename)."""

    def test_returns_expected_keys(self, sample_data):
        """Verify the result dict has the documented shape."""
        result = export(sample_data, style="white")
        assert set(result) == {"cohort_json", "style_toml", "json_path", "toml_path"}
        assert isinstance(result["cohort_json"], str)
        assert isinstance(result["style_toml"], str)
        assert result["json_path"] is None
        assert result["toml_path"] is None

    def test_json_envelope_shape(self, sample_data):
        """Verify the JSON wraps data in the documented `_meta` + `data` envelope."""
        result = export(sample_data, style="white", figure_title="My Study")
        parsed = json.loads(result["cohort_json"])
        assert isinstance(parsed, dict)
        assert "_meta" in parsed
        assert "data" in parsed
        assert isinstance(parsed["data"], list)
        assert len(parsed["data"]) == len(sample_data)
        meta = parsed["_meta"]
        assert meta["figure_title"] == "My Study"
        assert meta["transparent"] is False
        assert "pycohortflow_version" in meta
        assert "exported_at" in meta

    def test_data_roundtrip(self, sample_data):
        """Original data fields are preserved after JSON roundtrip."""
        result = export(sample_data, style="white")
        parsed = json.loads(result["cohort_json"])
        for orig, baked in zip(sample_data, parsed["data"]):
            for key, value in orig.items():
                assert baked[key] == value

    def test_toml_includes_all_sections(self, sample_data):
        """The exported TOML resolves to a valid pycohortflow style config."""
        result = export(sample_data, style="colorful")
        cfg = tomllib.loads(result["style_toml"])
        for section in ("figure", "layout", "box_geometry", "text", "lines", "colors", "exclusion"):
            assert section in cfg, f"Missing section: {section}"

    def test_dpi_kwarg_in_toml(self, sample_data):
        """`dpi` kwarg is baked into the TOML's [figure] section."""
        result = export(sample_data, style="white", dpi=72)
        cfg = tomllib.loads(result["style_toml"])
        assert cfg["figure"]["dpi"] == 72

    def test_figsize_kwarg_in_toml(self, sample_data):
        """`figsize` kwarg is split into [figure] width and height."""
        result = export(sample_data, style="white", figsize=(20, 15))
        cfg = tomllib.loads(result["style_toml"])
        assert cfg["figure"]["figsize_width"] == 20.0
        assert cfg["figure"]["figsize_height"] == 15.0

    def test_transparent_true_round_trip(self, sample_data):
        """`transparent=True` is captured in `_meta.transparent`."""
        result = export(sample_data, style="white", transparent=True)
        parsed = json.loads(result["cohort_json"])
        assert parsed["_meta"]["transparent"] is True

    def test_invalid_style_raises_value_error(self, sample_data):
        """Unknown built-in style raises ValueError listing the valid styles.

        The error message must enumerate the available styles so that
        users hitting the ValueError can self-diagnose without having
        to dig into the source.  ``_BUILTIN_STYLES`` in cfd_util is the
        canonical list — keep this test aligned with it.
        """
        with pytest.raises(ValueError) as exc:
            export(sample_data, style="bogus")
        msg = str(exc.value)
        assert "bogus" in msg
        for built_in in ("white", "colorful", "minimal"):
            assert built_in in msg, f"Error message missing built-in style {built_in!r}: {msg}"

    def test_style_config_path_round_trip(self, sample_data, tmp_path):
        """A custom TOML override file is merged into the exported style."""
        # Custom file overrides dpi and a colour; style="white" base
        # provides every other key.
        custom = tmp_path / "custom.toml"
        custom.write_text(
            '[figure]\ndpi = 333\n\n[colors]\nmain_start = "#aabbcc"\n',
            encoding="utf-8",
        )
        result = export(sample_data, style="white", style_config_path=str(custom))
        cfg = tomllib.loads(result["style_toml"])
        # Override applied …
        assert cfg["figure"]["dpi"] == 333
        assert cfg["colors"]["main_start"] == "#aabbcc"
        # … other keys still come from the base "white" style.
        assert cfg["figure"]["figsize_width"] == 12
        assert cfg["colors"]["main_end"] == "#ffffff"


# ---------------------------------------------------------------------------
# Palette baking (D3)
# ---------------------------------------------------------------------------


class TestExportPaletteBaking:
    """`main_palette` / `exclusion_palette` kwargs become per-node colours."""

    def test_main_palette_baked_per_node(self, sample_data):
        """A main_palette kwarg becomes per-node `color` in the JSON."""
        palette = ["#ff0000", "#00ff00", "#0000ff"]
        result = export(sample_data, style="white", main_palette=palette)
        parsed = json.loads(result["cohort_json"])
        for node, expected in zip(parsed["data"], palette):
            assert node["color"] == expected

    def test_per_node_color_wins_over_palette(self):
        """Existing per-node `color` is preserved (matches plot_cfd behaviour)."""
        data = [
            {"heading": "A", "N": 100, "color": "#abcdef"},
            {"heading": "B", "N": 50},
        ]
        palette = ["#ff0000", "#00ff00"]
        result = export(data, style="white", main_palette=palette)
        parsed = json.loads(result["cohort_json"])
        assert parsed["data"][0]["color"] == "#abcdef"  # explicit wins
        assert parsed["data"][1]["color"] == "#00ff00"  # palette fills the gap

    def test_input_data_not_mutated(self, sample_data):
        """`export()` must not mutate the caller's data list."""
        snapshot = [dict(d) for d in sample_data]
        palette = ["#ff0000", "#00ff00", "#0000ff"]
        export(sample_data, style="white", main_palette=palette)
        assert sample_data == snapshot


# ---------------------------------------------------------------------------
# Disk mode
# ---------------------------------------------------------------------------


class TestExportToDisk:
    """`out_dir` + `basename` write the documented file pair."""

    def test_writes_two_files(self, sample_data, tmp_path):
        """Both .cohort.json and .style.toml are written with the basename stem."""
        result = export(sample_data, style="white", out_dir=tmp_path, basename="study")
        assert result["json_path"] == tmp_path / "study.cohort.json"
        assert result["toml_path"] == tmp_path / "study.style.toml"
        assert result["json_path"].exists()
        assert result["toml_path"].exists()

    def test_files_match_returned_strings(self, sample_data, tmp_path):
        """File contents equal the in-memory strings (modulo trailing newline on JSON)."""
        result = export(sample_data, style="white", out_dir=tmp_path, basename="study")
        assert result["json_path"].read_text(encoding="utf-8").rstrip("\n") == result["cohort_json"]
        assert result["toml_path"].read_text(encoding="utf-8") == result["style_toml"]

    def test_creates_missing_out_dir(self, sample_data, tmp_path):
        """`out_dir` is created if it doesn't exist."""
        target = tmp_path / "nested" / "dir"
        export(sample_data, style="white", out_dir=target, basename="study")
        assert target.is_dir()

    def test_partial_disk_args_raises(self, sample_data, tmp_path):
        """Providing only one of (out_dir, basename) is an error."""
        with pytest.raises(ValueError, match="must be provided together"):
            export(sample_data, style="white", out_dir=tmp_path)
        with pytest.raises(ValueError, match="must be provided together"):
            export(sample_data, style="white", basename="study")


# ---------------------------------------------------------------------------
# Round-trip via load_style_config
# ---------------------------------------------------------------------------


class TestExportRoundTrip:
    """Exported TOML re-loads through ``load_style_config`` to the same dict."""

    def test_toml_loads_back_to_same_config(self, sample_data, tmp_path):
        """Round-trip integration: exported TOML reproduces the input config."""
        # Reference: what plot_cfd would compute internally
        original_cfg = load_style_config(style="colorful")
        original_cfg["figure"]["dpi"] = 150
        original_cfg["figure"]["figsize_width"] = 14.0
        original_cfg["figure"]["figsize_height"] = 9.0

        # Exported equivalent
        result = export(
            sample_data,
            style="colorful",
            dpi=150,
            figsize=(14, 9),
            out_dir=tmp_path,
            basename="rt",
        )
        # Re-load via the public loader path
        reloaded = load_style_config(style="white", custom_config_path=str(result["toml_path"]))
        # The custom file fully specifies the config, so the base style
        # ("white") doesn't matter for the comparison.
        assert reloaded == original_cfg


# ---------------------------------------------------------------------------
# plot_and_export wrapper
# ---------------------------------------------------------------------------


class TestPlotAndExport:
    """The convenience wrapper drives both `plot_cfd` and `export`."""

    def test_returns_three_tuple(self, sample_data, tmp_path):
        """Returns ``(Figure, Axes, export_result_dict)``."""
        fig, ax, result = plot_and_export(
            sample_data, out_dir=tmp_path, name="study", style="white"
        )
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        assert isinstance(result, dict)
        plt.close(fig)

    def test_writes_figure_and_export_pair(self, sample_data, tmp_path):
        """Figure + .cohort.json + .style.toml all land with the same stem."""
        fig, ax, _ = plot_and_export(
            sample_data,
            out_dir=tmp_path,
            name="study",
            style="white",
            save_format="png",
        )
        assert (tmp_path / "study.png").exists()
        assert (tmp_path / "study.cohort.json").exists()
        assert (tmp_path / "study.style.toml").exists()
        plt.close(fig)

    def test_conflicting_kwargs_raise_type_error(self, sample_data, tmp_path):
        """Passing `save_dir` / `img_name` / `basename` raises TypeError.

        Silent drops surprised users when nothing landed at the path
        they expected; we now reject the conflicting names outright.
        """
        for bad_kwarg in ("save_dir", "img_name", "basename"):
            with pytest.raises(TypeError, match="plot_and_export does not accept"):
                plot_and_export(
                    sample_data,
                    out_dir=tmp_path,
                    name="study",
                    style="white",
                    **{bad_kwarg: "should-be-rejected"},
                )

    def test_partial_args_raises_value_error(self, sample_data, tmp_path):
        """Providing exactly one of (out_dir, name) is an error.

        Without this guard, `plot_cfd` would silently skip writing the
        figure (img_name=None falsy) and only `export()` would surface
        a ValueError half-way through, leaving the figure rendered in
        memory but never saved.
        """
        with pytest.raises(ValueError, match="must be provided together"):
            plot_and_export(sample_data, out_dir=tmp_path, style="white")
        with pytest.raises(ValueError, match="must be provided together"):
            plot_and_export(sample_data, name="study", style="white")

    def test_no_args_returns_in_memory_result(self, sample_data):
        """Omitting both out_dir and name keeps everything in memory."""
        fig, ax, result = plot_and_export(sample_data, style="white")
        assert result["json_path"] is None
        assert result["toml_path"] is None
        assert isinstance(result["cohort_json"], str)
        assert isinstance(result["style_toml"], str)
        plt.close(fig)
