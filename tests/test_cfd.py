"""Tests for pycohortflow.cfd — the main plotting function."""

import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")  # non-interactive backend for CI

from pycohortflow import plot_cohort_flow_diagram

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
    """Core happy-path tests for plot_cohort_flow_diagram."""

    def test_returns_figure_and_axes(self, sample_data):
        """Verify the function returns a (Figure, Axes) tuple."""
        fig, ax = plot_cohort_flow_diagram(sample_data)
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plt.close(fig)

    def test_single_node(self, single_node):
        """Verify rendering succeeds with a single-node cohort."""
        fig, ax = plot_cohort_flow_diagram(single_node)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_figure_title(self, sample_data):
        """Verify the figure_title parameter is applied to the axes."""
        fig, ax = plot_cohort_flow_diagram(sample_data, figure_title="My Title")
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
        ret_fig, ret_ax = plot_cohort_flow_diagram(sample_data, ax=host_ax)
        assert ret_ax is host_ax
        assert ret_fig is fig
        plt.close(fig)

    def test_returns_parent_figure(self, sample_data):
        """Verify the returned figure is the parent of the provided axes."""
        fig, axes = plt.subplots(1, 2)
        ret_fig, ret_ax = plot_cohort_flow_diagram(sample_data, ax=axes[0])
        assert ret_fig is fig
        assert ret_ax is axes[0]
        plt.close(fig)

    def test_title_on_provided_axes(self, sample_data):
        """Verify figure_title is applied as axes title on provided axes."""
        fig, host_ax = plt.subplots()
        plot_cohort_flow_diagram(sample_data, ax=host_ax, figure_title="Custom")
        assert host_ax.get_title() == "Custom"
        plt.close(fig)

    def test_no_ax_creates_new_figure(self, sample_data):
        """Verify omitting ax creates a fresh figure."""
        fig, ax = plot_cohort_flow_diagram(sample_data)
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plt.close(fig)


# ---------------------------------------------------------------------------
# Style selection
# ---------------------------------------------------------------------------


class TestStyles:
    """Tests for built-in style selection."""

    def test_white_style(self, sample_data):
        """Verify the 'white' style renders without error."""
        fig, _ = plot_cohort_flow_diagram(sample_data, style="white")
        plt.close(fig)

    def test_colorful_style(self, sample_data):
        """Verify the 'colorful' style renders without error."""
        fig, _ = plot_cohort_flow_diagram(sample_data, style="colorful")
        plt.close(fig)

    def test_unknown_style_raises(self, sample_data):
        """Verify an unknown style name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown built-in style"):
            plot_cohort_flow_diagram(sample_data, style="neon")


# ---------------------------------------------------------------------------
# Transparent background
# ---------------------------------------------------------------------------


class TestTransparent:
    """Tests for the transparent background option."""

    def test_transparent_flag(self, sample_data):
        """Verify transparent=True sets figure and axes alpha to 0."""
        fig, ax = plot_cohort_flow_diagram(sample_data, transparent=True)
        assert fig.patch.get_alpha() == 0.0
        assert ax.patch.get_alpha() == 0.0
        plt.close(fig)

    def test_opaque_by_default(self, sample_data):
        """Verify the background is opaque when transparent is not set."""
        fig, ax = plot_cohort_flow_diagram(sample_data)
        # Default alpha is 1.0 (or None which means opaque)
        alpha = fig.patch.get_alpha()
        assert alpha is None or alpha == 1.0
        plt.close(fig)


# ---------------------------------------------------------------------------
# Saving
# ---------------------------------------------------------------------------


class TestSaving:
    """Tests for saving figures to disk."""

    def test_save_png(self, sample_data, tmp_path):
        """Verify a single PNG file is written to the target directory."""
        plot_cohort_flow_diagram(
            sample_data,
            save_dir=str(tmp_path),
            img_name="test_chart",
            save_format="png",
        )
        assert (tmp_path / "test_chart.png").exists()

    def test_save_multiple_formats(self, sample_data, tmp_path):
        """Verify multiple formats are written when a list is passed."""
        plot_cohort_flow_diagram(
            sample_data,
            save_dir=str(tmp_path),
            img_name="multi",
            save_format=["png", "svg"],
        )
        assert (tmp_path / "multi.png").exists()
        assert (tmp_path / "multi.svg").exists()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestValidation:
    """Tests for input validation guards."""

    def test_empty_data_raises(self):
        """Verify an empty data list raises ValueError."""
        with pytest.raises(ValueError, match="at least one"):
            plot_cohort_flow_diagram([])

    def test_increasing_n_raises(self):
        """Verify non-decreasing N across steps raises ValueError."""
        data = [
            {"heading": "A", "N": 50},
            {"heading": "B", "N": 100},  # more than previous → error
        ]
        with pytest.raises(ValueError, match="more patients"):
            plot_cohort_flow_diagram(data)
