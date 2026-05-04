<p align="center">
  <img src="https://fschwar4.github.io/pycohortflow/_static/logo_wide.svg" alt="pycohortflow logo" width="100%" />
</p>

# pycohortflow

[![CI](https://github.com/fschwar4/pycohortflow/actions/workflows/ci.yml/badge.svg)](https://github.com/fschwar4/pycohortflow/actions/workflows/ci.yml)
[![Documentation](https://github.com/fschwar4/pycohortflow/actions/workflows/docs.yml/badge.svg)](https://github.com/fschwar4/pycohortflow/actions/workflows/docs.yml)
[![PyPI version](https://img.shields.io/pypi/v/pycohortflow.svg)](https://pypi.org/project/pycohortflow/)
[![Python versions](https://img.shields.io/pypi/pyversions/pycohortflow.svg)](https://pypi.org/project/pycohortflow/)
[![License](https://img.shields.io/pypi/l/pycohortflow.svg)](https://pypi.org/project/pycohortflow/)




Lightweight cohort flow diagrams built on Matplotlib.

Turn a plain Python list of cohort steps into a publication-ready vertical flow chart with a single function call. Colours, fonts, spacing, and box geometry are fully customisable via TOML configuration files.

## About

`pycohortflow` is a Python library for programmatically generating cohort flow diagrams — vertical flowcharts that document participant progression through clinical studies, randomised controlled trials and systematic reviews, with explicit exclusion counts and reasons at each step.

The library targets the **reproducibility** and **reporting-standard** requirements of medical research. Cohort flow diagrams in this form are required by **CONSORT** (Consolidated Standards of Reporting Trials) for randomised trials and **PRISMA 2020** (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) for systematic reviews and meta-analyses. `pycohortflow` produces the structural elements those standards expect — a vertical main column with side panels for exclusions, automatic participant-count tracking and customisable per-step labels — without prescribing a single fixed template.

Diagrams are defined as data: a Python list of cohort steps drives the layout, exclusion counts are computed automatically with non-decreasing-N validation, and visual style is controlled by version-controllable TOML files held separately from the data. The same input renders the same diagram across machines and over time, eliminating the manual vector-editor adjustments that typically break reproducibility between manuscript revisions. Output formats include PNG, SVG, PDF and EPS, ready for journal submission.

## No Python installed?

**Use the [Interactive Generator](https://fschwar4.github.io/pycohortflow/generator.html) to build diagrams directly in your browser and export them as SVG, PNG or PDF.**

## Installation

```bash
pip install pycohortflow
```

## Quick Start

```python
from pycohortflow import plot_cfd
import matplotlib.pyplot as plt

data = [
    {"heading": "Registered Patients", "N": 350,
     "description": "Total patients registered in database"},
    {"heading": "Screening", "N": 150,
     "exclusion_description": "Did not meet inclusion criteria"},
    {"heading": "Eligible", "N": 120,
     "exclusion_description": "Declined / Lost to follow-up"},
    {"heading": "Final Analysis", "N": 115,
     "exclusion_description": "Data incomplete"},
]

fig, ax = plot_cfd(
    data,
    figure_title="Clinical Cohort Flow Diagram",
)
plt.show()
```

## Built-in Styles

Three styles ship with the package:

<p align="center">
  <img src="https://fschwar4.github.io/pycohortflow/_static/clinical_flow_chart_white.png" alt="White style preview" width="31%" />
  <img src="https://fschwar4.github.io/pycohortflow/_static/clinical_flow_chart_colorful.png" alt="Colorful style preview" width="31%" />
  <img src="https://fschwar4.github.io/pycohortflow/_static/clinical_flow_chart_minimal_white.png" alt="Minimal style preview" width="31%" />
</p>

```python
# Clean white boxes (default)
fig, ax = plot_cfd(data, style="white")

# Pastel gradient backgrounds
fig, ax = plot_cfd(data, style="colorful")

# Notebook-style: white boxes, normal-weight headings, italic side
# text instead of an exclusion box
fig, ax = plot_cfd(data, style="minimal")

# Transparent figure background (for slides / posters)
fig, ax = plot_cfd(data, transparent=True)
```

## Customisation

Create a TOML file with only the values you want to override:

```toml
[figure]
dpi = 300

[colors]
main_start = "#cce5ff"
main_end   = "#d4edda"
```

Then pass it when plotting:

```python
fig, ax = plot_cfd(data, style_config_path="my_style.toml")
```

See the [full documentation](https://fschwar4.github.io/pycohortflow/) for all available options.

## Saving Figures

```python
fig, ax = plot_cfd(
    data,
    save_dir="output",
    img_name="flow_chart",
    save_format=["png", "svg", "pdf"],
)
```

## Requirements

- Python >= 3.9
- Matplotlib >= 3.5

## License

EUPL-1.2 (European Union Public Licence v1.2) — see [LICENSE](LICENSE) for the full text.

---

## Roadmap

The list below is auto-generated from [docs/roadmap.rst](docs/roadmap.rst);
edit that file (and run `python scripts/sync_roadmap.py`) to update it.

<!-- ROADMAP-START -->
- [x] Add: Small Diagram version (delivered as the `minimal` style in v0.1.3)
- [x] Add: Verbose option for communication of saving options (delivered as `verbose=False` in v0.1.3)
- [ ] Add: Python-based PRISMA2020 style generation, if necessary
- [ ] Add: Diagrams for multiple Arms (e.g. something like CONSORT style)
- [ ] Add: Full test coverage — assert per-node `color` and `exclusion_color` overrides actually change rendered `facecolor`; assert `[exclusion] mode` can be overridden via a custom TOML file; cover the `verbose=True` print path; consider an image-comparison regression test
- [ ] Consider: switch the `verbose=True` print path to standard Python `logging` so callers can control level, destination and handlers without per-call flags
<!-- ROADMAP-END -->
