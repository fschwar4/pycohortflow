# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/fschwar4/pycohortflow/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/fschwar4/pycohortflow/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/fschwar4/pycohortflow/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/fschwar4/pycohortflow/releases/tag/v0.1.0
