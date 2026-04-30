Development
===========

This page covers setting up a local development environment, running the
test suite, linting, and deploying new versions.

Local Development Setup
-----------------------

1. **Clone the repository:**

   .. code-block:: bash

      git clone https://github.com/fschwar4/pycohortflow.git
      cd pycohortflow

2. **Create and activate a virtual environment** (recommended):

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate   # Linux / macOS
      .venv\Scripts\activate      # Windows

3. **Install the package in editable mode with all development extras:**

   .. code-block:: bash

      pip install -e ".[dev,docs]"

   This installs the package itself (so ``import pycohortflow`` works),
   plus Ruff, pytest, build, twine, Sphinx and the documentation theme.

Project Layout
--------------

.. code-block:: text

   pycohortflow/
   ├── src/pycohortflow/          # package source
   │   ├── __init__.py            # public API & metadata
   │   ├── cfd.py                 # main plotting function
   │   ├── cfd_util.py            # colour, text & config helpers
   │   └── styles/                # built-in TOML style files
   │       ├── __init__.py
   │       ├── default_style_white.toml
   │       └── default_style_colorful.toml
   ├── tests/                     # pytest test suite
   │   ├── test_cfd.py
   │   └── test_cfd_util.py
   ├── docs/                      # Sphinx documentation
   ├── .github/workflows/         # CI/CD pipelines
   ├── pyproject.toml             # project metadata & build config
   ├── CHANGELOG.md               # release history (Keep a Changelog)
   └── MANIFEST.in                # sdist inclusion rules

Running the Tests
-----------------

Run the full suite with verbose output:

.. code-block:: bash

   pytest -v

All tests use the ``Agg`` Matplotlib backend so they work without a
display (headless CI environments).

You can run a specific test file or class:

.. code-block:: bash

   pytest tests/test_cfd.py -v
   pytest tests/test_cfd_util.py::TestColourHelpers -v

Linting and Formatting
----------------------

The project uses `Ruff <https://docs.astral.sh/ruff/>`_ for both linting
and formatting.  The configuration lives in ``pyproject.toml``:

.. code-block:: bash

   # Check for lint errors
   ruff check src/ tests/

   # Check formatting
   ruff format --check src/ tests/

   # Auto-fix lint issues
   ruff check --fix src/ tests/

   # Auto-format code
   ruff format src/ tests/

CI will reject pull requests that fail either check (see below).

Continuous Integration
----------------------

Two GitHub Actions workflows run automatically:

**CI** (``ci.yml``) — triggered on every push and pull request to ``main``:

- **Lint job** — runs ``ruff check`` and ``ruff format --check`` on Python 3.12.
- **Test job** — runs ``pytest -v`` across a matrix of Python 3.9, 3.10,
  3.11, 3.12 and 3.13.

**Deploy Documentation** (``docs.yml``) — triggered on push to ``main``
(or manually via ``workflow_dispatch``):

- Builds the Sphinx HTML documentation.
- Deploys it to GitHub Pages.

Building the Documentation Locally
-----------------------------------

.. code-block:: bash

   sphinx-build -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in a browser to preview.

Alternatively, serve the built docs over a local HTTP server so that
relative links, JavaScript modules and the Interactive Generator behave
as they would in production:

.. code-block:: bash

   python -m http.server --directory docs/_build/html

Then open http://localhost:8000 in a browser. Use ``Ctrl+C`` to stop
the server.

Publishing to PyPI
------------------

1. **Bump the version** in ``pyproject.toml``:

   .. code-block:: toml

      version = "0.2.0"

2. **Build source and wheel distributions:**

   .. code-block:: bash

      python -m build

3. **Check the package** (optional but recommended):

   .. code-block:: bash

      twine check dist/*

4. **Upload to Test PyPI** first:

   .. code-block:: bash

      twine upload --repository testpypi dist/*

5. **Upload to PyPI:**

   .. code-block:: bash

      twine upload dist/*

   You will need a PyPI API token configured in your ``~/.pypirc`` or
   passed via ``--username __token__ --password <token>``.

Git Tags
--------

Every release must have a corresponding annotated git tag matching the
version in ``pyproject.toml``.  Tag names use the ``v`` prefix
(e.g. ``v0.2.0``).

1. **Create an annotated tag:**

   .. code-block:: bash

      git tag -a v0.2.0 -m "Release 0.2.0"

   Use the same message format consistently.  For a longer annotation,
   summarise the highlights from the changelog.

2. **Push the tag to GitHub:**

   .. code-block:: bash

      git push origin v0.2.0

   Or push all local tags at once:

   .. code-block:: bash

      git push origin --tags

GitHub Releases
---------------

After pushing a tag, create a GitHub Release so that the version is
visible on the repository's *Releases* page and users receive
notifications.

1. **Via the GitHub CLI** (``gh``):

   .. code-block:: bash

      gh release create v0.2.0 \
        --title "v0.2.0" \
        --notes-file CHANGELOG.md

   The ``--notes-file`` flag uploads the full changelog as the release
   body.  To include only the notes for the current version, extract the
   relevant section first or pass ``--notes "…"`` directly.

2. **Via the GitHub web UI:**

   Go to *Releases → Draft a new release*, choose the tag you just
   pushed, paste the changelog entry for this version into the
   description, and click *Publish release*.

.. tip::

   Keep the ``CHANGELOG.md`` file up to date **before** tagging.  The
   release workflow is: update changelog → bump version in
   ``pyproject.toml`` → commit → tag → push → publish to PyPI →
   create GitHub release.

Changelog
---------

The project maintains a ``CHANGELOG.md`` in the repository root,
following the `Keep a Changelog <https://keepachangelog.com/>`_ format.
Each release section uses these categories:

- **Added** — new features.
- **Changed** — changes to existing functionality.
- **Deprecated** — features that will be removed in a future release.
- **Removed** — features that have been removed.
- **Fixed** — bug fixes.
- **Security** — vulnerability fixes.

An ``[Unreleased]`` section at the top collects changes that have not
yet been tagged.  When cutting a release, rename ``[Unreleased]`` to the
new version and date, add a fresh empty ``[Unreleased]`` heading, and
update the comparison links at the bottom of the file.

Test Suite Reference
--------------------

This section documents every test class, what it verifies, and why the
test exists.

``test_cfd.py`` — Plotting Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**TestBasicPlotting** — Core happy-path tests that ensure the main
plotting function produces valid output.

- ``test_returns_figure_and_axes`` — Verifies that
  ``plot_cohort_flow_diagram()`` returns a ``(Figure, Axes)`` tuple.
  This is the most fundamental contract of the function.
- ``test_single_node`` — Ensures the function works with a minimal
  single-step cohort (no exclusions).  Edge case: the arrow and
  exclusion-box logic must gracefully handle having nothing to draw.
- ``test_figure_title`` — Confirms the ``figure_title`` parameter is
  propagated to the Matplotlib axes title.

**TestExternalAxes** — Drawing into a caller-provided axes.

- ``test_uses_provided_axes`` — Passes an existing axes via ``ax``
  and checks the returned axes is the same object.  Ensures no new
  figure is created.
- ``test_returns_parent_figure`` — Creates a two-subplot figure, passes
  one subplot, and verifies the returned figure is the original parent.
- ``test_title_on_provided_axes`` — Confirms ``figure_title`` is applied
  as the axes title when an external axes is used.
- ``test_no_ax_creates_new_figure`` — Omitting ``ax`` must still
  create a fresh figure (backwards compatibility).

**TestStyles** — Built-in style selection.

- ``test_white_style`` — Confirms ``style="white"`` loads and renders
  without error.
- ``test_colorful_style`` — Confirms ``style="colorful"`` loads and
  renders without error.
- ``test_unknown_style_raises`` — Verifies that passing an unrecognised
  style name raises a ``ValueError`` with a helpful message, rather than
  silently falling back.

**TestTransparent** — Transparent figure background.

- ``test_transparent_flag`` — Checks that ``transparent=True`` sets
  both the figure and axes background alpha to ``0.0``.  This is
  essential for users who embed diagrams in presentations or posters.
- ``test_opaque_by_default`` — Asserts that the default behaviour leaves
  the background opaque (alpha ``1.0`` or ``None``), so the chart is
  visible on a white canvas.

**TestSaving** — File export.

- ``test_save_png`` — Writes a single PNG file to ``tmp_path`` and
  verifies the file exists on disk.
- ``test_save_multiple_formats`` — Passes ``save_format=["png", "svg"]``
  and checks both files are created.  This covers the list-of-formats
  code path.

**TestValidation** — Input validation guards.

- ``test_empty_data_raises`` — Passing an empty list must raise a
  ``ValueError``.  Without this guard the function would produce an
  empty figure with no user feedback.
- ``test_increasing_n_raises`` — Cohort counts must be non-increasing
  across steps.  A later step with *more* participants than the previous
  one is a data error and should be caught early.

``test_cfd_util.py`` — Utility Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**TestWrapLines** — Text wrapping helper used to fit text inside boxes.

- ``test_empty_string`` — An empty input should produce an empty list,
  not crash.
- ``test_short_string`` — A string shorter than the wrap width should
  return as a single-element list (no wrapping).
- ``test_wraps_correctly`` — A longer string is broken into multiple
  lines, each respecting the width limit.

**TestColourHelpers** — Low-level colour conversion functions.

- ``test_hex_to_rgb`` — Verifies conversion from hex strings to
  ``(R, G, B)`` tuples for primary colours.
- ``test_hex_to_rgb_strips_alpha`` — Ensures an 8-digit hex string
  (with alpha channel) is handled correctly by stripping the alpha.
- ``test_rgb_to_hex`` — Inverse conversion: RGB tuple to lowercase hex
  string.
- ``test_roundtrip`` — A hex → RGB → hex roundtrip must return the
  original value, proving both conversions are consistent.
- ``test_interpolate_endpoints`` — ``_interpolate_color`` at ``t=0.0``
  and ``t=1.0`` must return the start and end colours exactly.
- ``test_interpolate_midpoint`` — At ``t=0.5`` between black and white,
  the result must be ``#808080`` (50 % grey), verifying linear
  interpolation.
- ``test_named_color`` — ``named_color("red")`` must resolve to
  ``#ff0000`` via Matplotlib's colour registry.
- ``test_named_colors_list`` — ``get_matplotlib_named_colors()`` returns
  a non-empty list containing standard colour names like ``"red"``.

**TestGradientPalette** — Gradient generation for box backgrounds.

- ``test_single_colour`` — Requesting a palette of length 1 returns just
  the start colour.
- ``test_correct_length`` — The returned list has exactly the requested
  number of entries.
- ``test_endpoints`` — The first and last elements of the palette must
  match the requested start and end colours.

**TestResolveColor** — Colour resolution with fallback and validation.

- ``test_none_uses_default`` — Passing ``None`` falls back to the
  provided default colour.
- ``test_explicit_value`` — A named colour like ``"red"`` is resolved to
  its hex equivalent.
- ``test_named_color_disallowed`` — When ``allow_named_colors=False``,
  passing a colour name raises ``ValueError``.  This tests the
  configuration guard that prevents accidental use of named colours when
  the style forbids them.
- ``test_invalid_color`` — A completely invalid colour string raises
  ``ValueError`` to surface typos early.

**TestRecursiveUpdate** — Deep dictionary merge used for TOML config
layering.

- ``test_flat_merge`` — Top-level keys are merged correctly (override +
  addition).
- ``test_nested_merge`` — Nested dicts are merged recursively; existing
  sibling keys are preserved when only one sub-key is overridden.

**TestLoadStyleConfig** — TOML-based style configuration loader.

- ``test_white_style`` — Loading ``"white"`` sets all box colours to
  ``#ffffff``.
- ``test_colorful_style`` — Loading ``"colorful"`` yields non-white
  colours.
- ``test_unknown_style_raises`` — An unrecognised style name raises
  ``ValueError``.
- ``test_all_sections_present`` — The loaded config dict contains every
  expected section (``figure``, ``layout``, ``box_geometry``, ``text``,
  ``lines``, ``colors``).  This guards against accidental deletion of
  required keys in the TOML files.
