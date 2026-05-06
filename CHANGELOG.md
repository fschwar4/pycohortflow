# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-05-05

### Added

- **`pycohortflow.export()`** — serialises a `plot_cfd` invocation into
  a paste-ready `.cohort.json` + `.style.toml` pair for the
  [Interactive Generator](https://fschwar4.github.io/pycohortflow/generator.html).
  Arguments mirror `plot_cfd`; the resolved style (including `dpi` /
  `figsize` overrides) is written as TOML, the data is wrapped in a
  JSON envelope with a `_meta` block so `figure_title` and `transparent`
  round-trip too. `main_palette` / `exclusion_palette` kwargs bake
  into per-node `"color"` / `"exclusion_color"` entries; existing
  per-node overrides win, matching `plot_cfd`.
- **`pycohortflow.plot_and_export()`** — convenience wrapper producing
  `<name>.png`, `<name>.cohort.json` and `<name>.style.toml`
  side-by-side under `out_dir` from one call. Returns
  `(fig, ax, export_result)`. Conflicting kwargs
  (`save_dir` / `img_name` / `basename`) raise `TypeError`; partial
  `out_dir` / `name` raises `ValueError` instead of half-completing.
- **Interactive Generator: envelope-form JSON support.** The data
  textarea accepts both the bare list (legacy) and the new envelope
  form. Pasting — or programmatically loading — an exported
  `.cohort.json` auto-populates the *Figure title* and *Transparent
  background* inputs from `_meta`; manual edits to those inputs are
  preserved on subsequent input events.
- **Pre-commit hooks**: `nbstripout` (notebook outputs / execution
  counts) and `ruff-pre-commit` (pinned to CI's Ruff version, runs
  `ruff check` + `ruff format --check`).
- New runtime dependency: `tomli-w >= 1.0` (TOML serialisation).
- Documentation, README, and `examples/example_cfd.ipynb` cover the
  export workflow end-to-end; test suite extended with in-memory and
  on-disk modes, palette baking, and full TOML round-trip.
- **Citation infrastructure**: `CITATION.cff` (GitHub "Cite this
  repository"), `.zenodo.json` (Zenodo release metadata), README
  badges (OSF preprint, Zenodo concept DOI) and "Citing pycohortflow"
  sections in `docs/index.rst` and `docs/generator.rst`, plus Quarto
  preprint sources under `paper/` (with `paper/LICENCE.md` declaring
  CC BY 4.0 for the paper, separate from EUPL-1.2 for the code) for
  the OSF preprint server. Build instructions in
  `docs/development.rst` ("Building the Preprint PDF"); preprint
  build artefacts are gitignored.

### Changed

- **`pycohortflow.cfd_util.apply_kwarg_overrides` is now public** —
  the single source of truth for "which `plot_cfd` kwargs map onto
  TOML config keys" (currently `dpi`, `figsize`). Both `plot_cfd` and
  `export()` route through it, so any kwarg recognised here is
  guaranteed to round-trip through the export.

### Fixed

- **Interactive Generator (JS): validation parity with Python.** The
  browser-side `parseCohortInput()` now matches `cfd.py`'s guards —
  a negative `N`, or a step with more patients than the previous, is
  rejected with a clear error banner instead of silently rendering
  the implied negative exclusion swallowed.
- **README license badge** showed stale AGPL-3 (the dynamic
  `shields.io/pypi/l/...` badge couldn't read the SPDX-style license
  metadata introduced in 0.1.3). Replaced with a static
  `EUPL-1.2` badge linked to `LICENSE`.

## [0.1.3] - 2026-04-30

### Changed (breaking)

- **Project licence: AGPL-3.0-only → EUPL-1.2** (European Union Public
  Licence v1.2; still strong-copyleft, OSI-approved). Downstream
  redistributors should review the new terms.
- **Renamed `plot_cohort_flow_diagram` → `plot_cfd`** (same signature
  and behaviour, only the name). JS counterpart renamed in lock-step
  (`plotCohortFlowDiagram` → `plotCfd`):

  ```python
  # before
  from pycohortflow import plot_cohort_flow_diagram

  # after
  from pycohortflow import plot_cfd
  ```

- **`save_figure` no longer emits a `UserWarning` per file written.**
  New opt-in `verbose: bool = False` parameter on `save_figure` and
  `plot_cfd` prints `Saved: <path>` to stdout instead. Default is
  silent.

### Added

- **New built-in `"minimal"` style** — white boxes, normal-weight
  headings, italic side text instead of an exclusion box. Pair with
  per-node `"color"` and `"heading_fontweight": "bold"` overrides to
  highlight start and end nodes.
- **New TOML keys** enabling the minimal style and per-style theming:
  `[text] heading_fontweight` (`"bold"` default; `"normal"` for
  minimal) and `[exclusion] mode` (`"box"` default; `"text"` for
  minimal).
- **New per-node dict key `"heading_fontweight"`** for selectively
  overriding individual box headings (e.g. re-bolding the first and
  last nodes when the style default is `"normal"`).
- **Interactive Generator: live auto-update** — the preview now
  re-renders on input changes (text inputs debounced ~300 ms;
  selects/checkboxes fire immediately). The "Generate" button is
  retained for explicit refreshes.
- **Interactive Generator: minimal-style support** — registered in
  `loadStyleConfigSync`, exposed as a "Minimal" option in the style
  dropdown, and rendered via a text-mode exclusion branch in
  `cohortflow.js`.
- **Roadmap page** (`docs/roadmap.rst`) as the single source of
  truth for project planning. The README section is auto-generated by
  `scripts/sync_roadmap.py` (Unicode `✅`/`⬜` → MD `[x]`/`[ ]`); a
  pre-commit hook plus `tests/test_roadmap_sync.py` keep the two in
  sync.
- `examples/example_cfd.ipynb` extended to demonstrate all three
  styles, saving into a `tempfile.mkdtemp()` directory that is removed
  at the end of the run.
- Developer documentation: `python -m http.server` instruction after
  `sphinx-build`; new "Quickstart" section heading on the landing
  page; `customise.rst` and `getting_started.rst` updated for the
  minimal style and the new TOML keys.
- **End-to-end notebook test via `nbmake`** for
  `examples/example_cfd.ipynb`. New dev deps: `nbmake>=1.5`,
  `ipykernel>=6.0`. `--nbmake` is opt-in (not in `addopts`), so plain
  `pytest` works in any environment without the notebook stack.
- Assertion-based tests covering the minimal style, the
  `heading_fontweight` resolution path, and the new `[exclusion]` /
  `[text]` config keys in `TestLoadStyleConfig`.

### Changed

- **Default `colorful` style: red exclusion gradient direction**
  flipped from bright→dark to dark→bright (`exclusion_start =
  "#f8cccc"`, `exclusion_end = "#fee8e8"`). Mirrored in Python and
  JS.
- **Landing page**: the "Interactive Generator" card is promoted
  above the Quickstart code block (full-width, centred); the
  "Documentation" and "Python API" cards now sit below.

### Removed

- **19 redundant unit tests** subsumed by the notebook coverage or
  testing matplotlib internals (smoke style-renders, weak palette
  overrides, matplotlib-wrapper colour helpers, redundant edge
  cases). Total test count: 66 unit → 47 unit + 1 sync + 1 notebook
  = **49**; ~0.6 s without `--nbmake`, ~3 s with.

### Fixed

- **Minimal style: exclusion text position** — italic side text now
  anchored next to the vertical arrow (`center_x + clearance`), not
  past the right edge of the main box. Mirrored in `cfd.py` and
  `cohortflow.js`.
- **Minimal style: figure width and title alignment** — the canvas no
  longer reserves space for a non-existent exclusion box; the title
  is re-anchored above the main column via `ax.title.set_x(...)`.
  Mirrored in JS (`rightX` shrinks; SVG title `x` set to
  `tx(centerX)` in text mode).
- **Interactive Generator (JS): vertical spacing in minimal style** —
  the gap between boxes was sized for an absent exclusion box. Now
  computed from the actual rendered text height when
  `exclusion.mode === "text"`.

## [0.1.2] - 2026-02-24

### Added

- Interactive browser-based diagram generator embedded in the Sphinx
  documentation — no Python installation required.
- SVG, PNG and PDF export from the web generator (jsPDF for PDF).
- `title_pad` now controls both the Python (Matplotlib points) and
  JavaScript (converted via `/ 72` to layout units) title spacing.
- Generator page linked from landing page, Getting Started, Customise
  and Documentation hub.
- Package description updated to mention the web-based generator.

### Changed

- License field in `pyproject.toml` corrected to AGPL-3.0-only SPDX
  identifier.
- Landing page card grid now includes an "Interactive Generator" card.
- Toctree reorganised: "API Reference" renamed to "Python API"; new
  "Tools" section for the generator.

### Fixed

- CI badge and documentation badge URLs in README.
- Typo fixes in documentation.

## [0.1.1] - 2026-02-13

### Added

- Wide logo SVG used in documentation navbar and README.

### Changed

- README updated with logo and style preview images.
- Logo arrow styling improved.

### Fixed

- PyPI display issues (long description rendering).

## [0.1.0] - 2026-02-13

### Added

- Initial release.
- `plot_cohort_flow_diagram()` function for generating vertical cohort
  flow charts from a Python list.
- Two built-in TOML styles: `white` and `colorful`.
- Custom TOML configuration support with three-layer merging
  (built-in → custom file → keyword arguments).
- Transparent background option.
- Multi-format export (PNG, SVG, PDF, EPS, etc.) via Matplotlib.
- Drawing into an existing Matplotlib axes.
- Input validation (empty data, non-decreasing N).
- Full Sphinx documentation with pydata-sphinx-theme.
- CI pipeline (lint + test matrix across Python 3.9–3.13).
- Documentation auto-deploy to GitHub Pages.

[Unreleased]: https://github.com/fschwar4/pycohortflow/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/fschwar4/pycohortflow/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/fschwar4/pycohortflow/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/fschwar4/pycohortflow/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/fschwar4/pycohortflow/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/fschwar4/pycohortflow/releases/tag/v0.1.0
