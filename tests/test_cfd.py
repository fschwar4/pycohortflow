"""Tests for pycohortflow.cfd — the main plotting function."""

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")  # non-interactive backend for CI

from pycohortflow import plot_cfd

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_data():
    """Provide minimal cohort data with three steps.

    Returns:
        list[dict]: A three-step cohort with exclusion descriptions.

    """
    return [
        {"heading": "Registered", "N": 100},
        {"heading": "Screened", "N": 80, "exclusion_description": "Not eligible"},
        {"heading": "Analysed", "N": 60, "exclusion_description": "Withdrew"},
    ]


@pytest.fixture
def single_node():
    """Provide a single-node cohort with no exclusions.

    Returns:
        list[dict]: A one-step cohort.

    """
    return [{"heading": "Total", "N": 200}]


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------


class TestBasicPlotting:
    """Core behaviour tests for plot_cfd not covered by the example notebook.

    Smoke tests of the form "function returns a Figure" are subsumed by
    `--nbmake examples/example_cfd.ipynb`; this class keeps only the
    edge cases and assertion-based tests.
    """

    def test_single_node(self, single_node):
        """Verify rendering succeeds with a single-node cohort.

        Edge case: the arrow and exclusion-box logic must gracefully
        handle having nothing to draw between boxes. Not covered by
        the example notebook (which uses a 4-step cohort).
        """
        fig, ax = plot_cfd(single_node)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_figure_title(self, sample_data):
        """Verify the figure_title parameter is applied to the axes."""
        fig, ax = plot_cfd(sample_data, figure_title="My Title")
        assert ax.get_title() == "My Title"
        plt.close(fig)


# ---------------------------------------------------------------------------
# External axes
# ---------------------------------------------------------------------------


class TestExternalAxes:
    """Tests for passing an existing axes object via the ax parameter."""

    def test_uses_provided_axes(self, sample_data):
        """Verify the diagram is drawn on the provided axes object."""
        fig, host_ax = plt.subplots()
        ret_fig, ret_ax = plot_cfd(sample_data, ax=host_ax)
        assert ret_ax is host_ax
        assert ret_fig is fig
        plt.close(fig)

    def test_returns_parent_figure(self, sample_data):
        """Verify the returned figure is the parent of the provided axes."""
        fig, axes = plt.subplots(1, 2)
        ret_fig, ret_ax = plot_cfd(sample_data, ax=axes[0])
        assert ret_fig is fig
        assert ret_ax is axes[0]
        plt.close(fig)

    def test_title_on_provided_axes(self, sample_data):
        """Verify figure_title is applied as axes title on provided axes."""
        fig, host_ax = plt.subplots()
        plot_cfd(sample_data, ax=host_ax, figure_title="Custom")
        assert host_ax.get_title() == "Custom"
        plt.close(fig)


# ---------------------------------------------------------------------------
# Style selection
# ---------------------------------------------------------------------------


class TestStyles:
    """Tests for built-in style selection.

    "Does style X render without error" is covered by the example
    notebook (which exercises all three styles). This class keeps only
    the assertion-based and error-path tests that the notebook can't
    catch.
    """

    def test_minimal_style_skips_exclusion_boxes(self, sample_data):
        """Verify 'minimal' style draws no exclusion FancyBboxPatch.

        In box mode each non-final step adds an exclusion FancyBboxPatch
        on top of the main one (so a 3-node sample has 3 main + 2
        exclusion = 5 FancyBboxPatch instances). In text mode only the
        3 main boxes should be present.
        """
        from matplotlib.patches import FancyBboxPatch

        fig_box, ax_box = plot_cfd(sample_data, style="white")
        fig_text, ax_text = plot_cfd(sample_data, style="minimal")

        n_box = sum(isinstance(p, FancyBboxPatch) for p in ax_box.patches)
        n_text = sum(isinstance(p, FancyBboxPatch) for p in ax_text.patches)
        assert n_text == len(sample_data)
        assert n_text < n_box
        plt.close(fig_box)
        plt.close(fig_text)

    def test_unknown_style_raises(self, sample_data):
        """Verify an unknown style name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown built-in style"):
            plot_cfd(sample_data, style="neon")


class TestHeadingFontweight:
    """Tests for the heading_fontweight style key and per-node override."""

    def test_default_white_is_bold(self, sample_data):
        """Verify the white style renders headings in bold by default."""
        fig, ax = plot_cfd(sample_data, style="white")
        title_text = sample_data[0]["heading"]
        weights = [t.get_fontweight() for t in ax.texts if t.get_text() == title_text]
        assert weights, "first node heading text not found on the axes"
        assert weights[0] == "bold"
        plt.close(fig)

    def test_minimal_default_is_normal(self, sample_data):
        """Verify the minimal style renders headings in normal weight."""
        fig, ax = plot_cfd(sample_data, style="minimal")
        title_text = sample_data[0]["heading"]
        weights = [t.get_fontweight() for t in ax.texts if t.get_text() == title_text]
        assert weights, "first node heading text not found on the axes"
        assert weights[0] == "normal"
        plt.close(fig)

    def test_per_node_override(self, sample_data):
        """Verify per-node heading_fontweight overrides the style default."""
        data = [dict(d) for d in sample_data]
        data[0]["heading_fontweight"] = "bold"
        data[1]["heading_fontweight"] = "normal"

        fig, ax = plot_cfd(data, style="minimal")

        first_weights = [t.get_fontweight() for t in ax.texts if t.get_text() == data[0]["heading"]]
        second_weights = [
            t.get_fontweight() for t in ax.texts if t.get_text() == data[1]["heading"]
        ]
        assert first_weights and first_weights[0] == "bold"
        assert second_weights and second_weights[0] == "normal"
        plt.close(fig)


# ---------------------------------------------------------------------------
# Transparent background
# ---------------------------------------------------------------------------


class TestTransparent:
    """Tests for the transparent background option."""

    def test_transparent_flag(self, sample_data):
        """Verify transparent=True sets figure and axes alpha to 0."""
        fig, ax = plot_cfd(sample_data, transparent=True)
        assert fig.patch.get_alpha() == 0.0
        assert ax.patch.get_alpha() == 0.0
        plt.close(fig)

    def test_opaque_by_default(self, sample_data):
        """Verify the background is opaque when transparent is not set."""
        fig, ax = plot_cfd(sample_data)
        # Default alpha is 1.0 (or None which means opaque)
        alpha = fig.patch.get_alpha()
        assert alpha is None or alpha == 1.0
        plt.close(fig)


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------


class TestSaving:
    """Tests for saving figures to disk.

    Saving a single PNG and saving multiple formats are both covered by
    the example notebook (which writes ``["png", "pdf", "svg"]`` for
    each style). Only the ``save_dir=None`` default path remains here,
    since the notebook always sets ``save_dir`` explicitly.
    """

    def test_save_to_cwd_when_no_dir(self, sample_data, tmp_path, monkeypatch):
        """Verify saving with save_dir=None writes to the current directory."""
        monkeypatch.chdir(tmp_path)
        plot_cfd(
            sample_data,
            img_name="cwd_chart",
            save_format="png",
        )
        assert (tmp_path / "cwd_chart.png").exists()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestValidation:
    """Tests for input validation guards."""

    def test_empty_data_raises(self):
        """Verify an empty data list raises ValueError."""
        with pytest.raises(ValueError, match="at least one"):
            plot_cfd([])

    def test_increasing_n_raises(self):
        """Verify non-decreasing N across steps raises ValueError."""
        data = [
            {"heading": "A", "N": 50},
            {"heading": "B", "N": 100},  # more than previous → error
        ]
        with pytest.raises(ValueError, match="more patients"):
            plot_cfd(data)

    def test_missing_n_key_raises(self):
        """Verify a node without 'N' raises ValueError with helpful message."""
        data = [{"heading": "Missing N"}]
        with pytest.raises(ValueError, match="missing the required 'N' key"):
            plot_cfd(data)

    def test_non_numeric_n_raises(self):
        """Verify a non-numeric N value raises TypeError."""
        data = [{"heading": "Bad", "N": "fifty"}]
        with pytest.raises(TypeError, match="must be a non-negative number"):
            plot_cfd(data)

    def test_boolean_n_raises(self):
        """Verify a boolean N value raises TypeError (bool is subclass of int)."""
        data = [{"heading": "Bad", "N": True}]
        with pytest.raises(TypeError, match="must be a non-negative number"):
            plot_cfd(data)

    def test_negative_n_raises(self):
        """Verify a negative N value raises ValueError."""
        data = [{"heading": "Negative", "N": -10}]
        with pytest.raises(ValueError, match="negative N value"):
            plot_cfd(data)


# ---------------------------------------------------------------------------
# Custom TOML config
# ---------------------------------------------------------------------------


class TestCustomConfig:
    """Tests for loading a custom TOML style override file."""

    def test_custom_toml_overrides(self, sample_data, tmp_path):
        """Verify a custom TOML file is applied to the diagram."""
        toml_content = "[figure]\ndpi = 72\n"
        toml_file = tmp_path / "custom.toml"
        toml_file.write_text(toml_content)

        fig, ax = plot_cfd(
            sample_data,
            style_config_path=str(toml_file),
        )
        assert fig.dpi == pytest.approx(72)
        plt.close(fig)

    def test_missing_toml_warns(self, sample_data):
        """Verify a missing TOML path emits a warning instead of crashing."""
        with pytest.warns(UserWarning, match="does not exist"):
            fig, ax = plot_cfd(
                sample_data,
                style_config_path="/nonexistent/path.toml",
            )
            plt.close(fig)
