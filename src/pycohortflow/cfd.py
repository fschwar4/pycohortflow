"""Main plotting function for cohort flow diagrams.

This module contains the public :func:`plot_cohort_flow_diagram` function
which renders a vertical flow chart from a simple Python list of cohort
steps.
"""

import matplotlib.patches as patches
import matplotlib.pyplot as plt

from pycohortflow.cfd_util import (
    gradient_palette,
    load_style_config,
    resolve_color,
    save_figure,
    wrap_lines,
)

__all__ = ["plot_cohort_flow_diagram"]


def plot_cohort_flow_diagram(
    data,
    ax=None,
    save_dir=None,
    img_name=None,
    save_format="png",
    figure_title=None,
    style="white",
    style_config_path=None,
    transparent=False,
    **kwargs,
):
    """Draw a vertical cohort flow diagram.

    Each element of *data* represents one step (node) in the cohort
    pipeline.  The function automatically calculates exclusion counts,
    lays out boxes and arrows, and applies a colour gradient.

    Args:
        data (list[dict]): Ordered list of cohort nodes.  Every dictionary
            **must** contain an ``"N"`` key (``int``) with the remaining
            participant count.  Optional keys:

            * ``"heading"`` (``str``) – Title shown inside the box
              (defaults to ``"Step <i>"``).
            * ``"description"`` (``str``) – Body text below the title.
            * ``"exclusion_description"`` (``str``) – Label for the
              side-exclusion box (defaults to ``"Excluded"``).
            * ``"color"`` / ``"color_name"`` (``str``) – Override colour
              for this node's main box.
            * ``"exclusion_color"`` / ``"exclusion_color_name"`` (``str``)
              – Override colour for the exclusion box.

        ax (matplotlib.axes.Axes | None): An existing Matplotlib axes
            object to draw on.  When provided the function does **not**
            create a new figure; instead it renders the diagram into the
            given axes and returns ``(ax.figure, ax)``.  This is useful
            for embedding the flow chart in a subplot layout.  When
            ``None`` (default) a new figure and axes are created
            automatically.
        save_dir (str | os.PathLike | None): Directory for saved images.
            Only used when *img_name* is also provided.
        img_name (str | None): Base file name (no extension) to save the
            figure.  When ``None`` the figure is **not** written to disk.
        save_format (str | list[str]): Image format(s).  Defaults to
            ``"png"``.  Pass a list for multiple formats, e.g.
            ``["png", "svg"]``.
        figure_title (str | None): Optional title rendered above the
            diagram.  Applied as the axes title via
            :meth:`~matplotlib.axes.Axes.set_title`.
        style (str): Name of the built-in style to use.  ``"white"``
            (default) produces boxes with no background colour;
            ``"colorful"`` applies pastel gradients.  See
            :doc:`customise` for details.
        style_config_path (str | os.PathLike | None): Path to a custom
            TOML file that selectively overrides the chosen built-in
            style.  See :doc:`customise` for details.
        transparent (bool): If ``True``, the figure and axes backgrounds
            are set to transparent.  Useful for embedding the diagram in
            slides or posters.  Defaults to ``False``.
        **kwargs: Ad-hoc overrides.  Currently recognised keys:

            * ``dpi`` (``int``) – Figure resolution (ignored when *ax*
              is provided).
            * ``figsize`` (``tuple[float, float]``) – ``(width, height)``
              in inches (ignored when *ax* is provided).
            * ``main_palette`` (``list[str]``) – Explicit list of hex
              colours for main boxes.
            * ``exclusion_palette`` (``list[str]``) – Explicit list of hex
              colours for exclusion boxes.

    Returns:
        tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]: The
        Matplotlib figure and axes objects so that callers can further
        customise the plot.  When *ax* is provided the returned figure
        is ``ax.figure``.

    Raises:
        ValueError: If *data* is empty, a node has a higher ``N`` than
            the preceding node, or *style* is not recognised.

    Example:
        >>> from pycohortflow import plot_cohort_flow_diagram
        >>> data = [
        ...     {"heading": "Registered", "N": 350},
        ...     {"heading": "Screened", "N": 150,
        ...      "exclusion_description": "Not eligible"},
        ...     {"heading": "Analysed", "N": 120,
        ...      "exclusion_description": "Lost to follow-up"},
        ... ]
        >>> fig, ax = plot_cohort_flow_diagram(data, figure_title="Study")

        Drawing into an existing axes (e.g. a subplot):

        >>> import matplotlib.pyplot as plt
        >>> fig, axes = plt.subplots(1, 2, figsize=(20, 8))
        >>> plot_cohort_flow_diagram(data, ax=axes[0], figure_title="Left")
        >>> plot_cohort_flow_diagram(data, ax=axes[1], style="colorful")

    """
    if not data:
        raise ValueError("data must contain at least one cohort node.")

    # ── 1. Load Configuration ──────────────────────────────────────────
    cfg = load_style_config(style=style, custom_config_path=style_config_path)

    if "dpi" in kwargs:
        cfg["figure"]["dpi"] = kwargs["dpi"]

    layout = cfg["layout"]
    geom = cfg["box_geometry"]
    txt = cfg["text"]
    lines = cfg["lines"]
    colors = cfg["colors"]

    # Colour palettes
    main_palette = kwargs.get("main_palette") or gradient_palette(
        colors["main_start"], colors["main_end"], len(data)
    )
    excl_palette = kwargs.get("exclusion_palette") or gradient_palette(
        colors["exclusion_start"], colors["exclusion_end"], len(data)
    )

    # ── 2. Data Processing & Sizing ────────────────────────────────────
    processed_nodes = []

    for i, node in enumerate(data):
        n_curr = node["N"]
        n_prev = data[i - 1]["N"] if i > 0 else n_curr
        n_excluded = n_prev - n_curr

        if n_excluded < 0:
            raise ValueError(f"Node {i} has more patients ({n_curr}) than previous step.")

        heading = node.get("heading", "").strip() or f"Step {i + 1}"
        desc = node.get("description", "").strip()
        excl_desc = node.get("exclusion_description", "Excluded").strip()

        # Wrap text
        title_lines = wrap_lines(heading, width=layout["main_title_width"])
        body_lines = [f"(n = {n_curr})"]
        if desc:
            body_lines.append("")
            body_lines.extend(wrap_lines(desc, width=layout["main_text_width"]))

        # Height calculation
        main_h_calc = (
            geom["padding"]
            + geom["title_line_height"] * max(1, len(title_lines))
            + geom["title_body_gap"]
            + geom["body_line_height"] * max(1, len(body_lines))
        )
        main_h = max(geom["min_main_height"], main_h_calc)

        excl_lines = wrap_lines(excl_desc, width=layout["exclusion_text_width"])
        excl_lines.append(f"(n = {n_excluded})")

        excl_h_calc = geom["padding"] + geom["body_line_height"] * max(1, len(excl_lines))
        excl_h = max(geom["min_exclusion_height"], excl_h_calc)

        # Colour resolution
        main_color_raw = node.get("color", node.get("color_name", main_palette[i]))
        excl_color_raw = node.get(
            "exclusion_color", node.get("exclusion_color_name", excl_palette[i])
        )

        processed_nodes.append(
            {
                "n": n_curr,
                "excl_n": n_excluded,
                "title_lines": title_lines,
                "body_lines": body_lines,
                "excl_lines": excl_lines,
                "color": resolve_color(
                    main_color_raw, main_palette[i], colors["allow_named_colors"]
                ),
                "excl_color": resolve_color(
                    excl_color_raw, excl_palette[i], colors["allow_named_colors"]
                ),
                "main_h": main_h,
                "excl_h": excl_h,
            }
        )

    # ── 3. Geometry Calculation ────────────────────────────────────────
    transition_gaps = []
    for i in range(1, len(processed_nodes)):
        node = processed_nodes[i]
        req_gap = node["excl_h"] + 2 * geom["clearance"] if node["excl_n"] > 0 else 0
        transition_gaps.append(max(layout["base_gap"], req_gap))

    centers_y = [layout["top_margin"] + processed_nodes[0]["main_h"] / 2]
    for i in range(1, len(processed_nodes)):
        prev = centers_y[-1]
        gap = transition_gaps[i - 1]
        curr_h = processed_nodes[i]["main_h"]
        prev_h = processed_nodes[i - 1]["main_h"]
        centers_y.append(prev + (prev_h / 2) + gap + (curr_h / 2))

    total_height = centers_y[-1] + processed_nodes[-1]["main_h"] / 2 + layout["bottom_margin"]

    # Horizontal centres
    center_x = 0.0
    excl_x = center_x + (
        layout["main_box_width"] / 2 + layout["side_gap"] + layout["exclusion_box_width"] / 2
    )

    # ── 4. Plotting ────────────────────────────────────────────────────
    if ax is None:
        # Create a new figure and axes
        figsize = kwargs.get("figsize")
        if figsize is None:
            width = (excl_x + layout["exclusion_box_width"]) * 1.5
            figsize = (
                max(cfg["figure"]["figsize_width"], width),
                max(cfg["figure"]["figsize_height"], total_height),
            )

        fig, ax = plt.subplots(figsize=figsize, dpi=cfg["figure"]["dpi"])
    else:
        # Use the provided axes; derive the figure from it
        fig = ax.figure

    # Transparent background
    if transparent:
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)

    ax.invert_yaxis()
    ax.axis("off")

    if figure_title:
        ax.set_title(
            figure_title,
            fontsize=cfg["figure"]["title_fontsize"],
            fontweight=cfg["figure"]["title_fontweight"],
            pad=cfg["figure"]["title_pad"],
        )

    for i, node in enumerate(processed_nodes):
        y_pos = centers_y[i]

        # ── Main box ──
        box = patches.FancyBboxPatch(
            (center_x - layout["main_box_width"] / 2, y_pos - node["main_h"] / 2),
            layout["main_box_width"],
            node["main_h"],
            boxstyle=(f"round,pad={geom['pad_factor']},rounding_size={geom['corner_radius']}"),
            edgecolor="black",
            facecolor=node["color"],
            linewidth=lines["box_linewidth"],
            zorder=2,
        )
        ax.add_patch(box)

        # ── Text ──
        text_y = y_pos - node["main_h"] / 2 + geom["text_top_padding"]
        ax.text(
            center_x,
            text_y,
            "\n".join(node["title_lines"]),
            ha="center",
            va="top",
            fontsize=txt["fontsize_title"],
            fontweight="bold",
            zorder=3,
        )

        body_y = (
            text_y
            + geom["title_line_height"] * max(1, len(node["title_lines"]))
            + geom["title_body_gap"]
        )
        ax.text(
            center_x,
            body_y,
            "\n".join(node["body_lines"]),
            ha="center",
            va="top",
            fontsize=txt["fontsize_main"],
            zorder=3,
        )

        # ── Arrow from previous box ──
        if i > 0:
            prev_btm = centers_y[i - 1] + processed_nodes[i - 1]["main_h"] / 2
            curr_top = y_pos - node["main_h"] / 2
            ax.annotate(
                "",
                xy=(center_x, curr_top),
                xytext=(center_x, prev_btm),
                arrowprops=dict(
                    arrowstyle="->",
                    lw=lines["connector_linewidth"],
                    color="black",
                ),
                zorder=1,
            )

            # ── Exclusion box ──
            if node["excl_n"] > 0:
                mid_y = (prev_btm + curr_top) / 2
                excl_left = excl_x - layout["exclusion_box_width"] / 2

                ebox = patches.FancyBboxPatch(
                    (excl_left, mid_y - node["excl_h"] / 2),
                    layout["exclusion_box_width"],
                    node["excl_h"],
                    boxstyle=(
                        f"round,pad={geom['pad_factor']},rounding_size={geom['corner_radius']}"
                    ),
                    edgecolor="black",
                    facecolor=node["excl_color"],
                    linewidth=lines["box_linewidth"],
                    zorder=2,
                )
                ax.add_patch(ebox)

                # Junction dot & horizontal arrow
                ax.add_patch(
                    patches.Circle(
                        (center_x, mid_y),
                        radius=lines["junction_radius"],
                        facecolor="black",
                        zorder=4,
                    )
                )
                ax.annotate(
                    "",
                    xy=(excl_x, mid_y),
                    xytext=(center_x, mid_y),
                    arrowprops=dict(
                        arrowstyle="-|>",
                        lw=lines["connector_linewidth"],
                        color="black",
                        mutation_scale=lines["arrow_mutation_scale"],
                        patchB=ebox,
                        shrinkA=0,
                        shrinkB=0,
                    ),
                    zorder=1,
                )

                ax.text(
                    excl_x,
                    mid_y,
                    "\n".join(node["excl_lines"]),
                    ha="center",
                    va="center",
                    fontsize=txt["fontsize_exclusion"],
                    style="italic",
                    zorder=3,
                )

    # ── Set axis limits ──
    left_lim = center_x - layout["main_box_width"] / 2 - layout["x_padding"]
    right_lim = excl_x + layout["exclusion_box_width"] / 2 + layout["x_padding"]
    ax.set_xlim(left_lim, right_lim)
    ax.set_ylim(total_height, 0)

    if img_name:
        save_figure(fig, save_dir, img_name, save_format)

    return fig, ax
