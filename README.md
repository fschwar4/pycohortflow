<p align="center">
  <img src="https://fschwar4.github.io/pycohortflow/_static/logo_wide.svg" alt="pycohortflow logo" width="100%" />
</p>

# pycohortflow

[![CI](https://github.com/fschwar4/pycohortflow/actions/workflows/ci.yml/badge.svg)](https://github.com/fschwar4/pycohortflow/actions/workflows/ci.yml)
[![Documentation](https://github.com/fschwar4/pycohortflow/actions/workflows/docs.yml/badge.svg)](https://github.com/fschwar4/pycohortflow/actions/workflows/docs.yml)
[![PyPI version](https://img.shields.io/pypi/v/pycohortflow.svg)](https://pypi.org/project/pycohortflow/)
[![License](https://img.shields.io/badge/license-EUPL--1.2-blue.svg)](LICENSE)
[![Preprint (OSF)](https://img.shields.io/badge/preprint-OSF-orange.svg)](https://osf.io/ncya2)
[![Zenodo concept DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20052730.svg)](https://doi.org/10.5281/zenodo.20052730)




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

## Sharing a figure with a non-Python user

Use `plot_and_export` to render the figure **and** write a paste-ready
`.cohort.json` + `.style.toml` pair that reproduces the same diagram in
the [Interactive Generator](https://fschwar4.github.io/pycohortflow/generator.html):

```python
from pycohortflow import plot_and_export

fig, ax, exp = plot_and_export(
    data,
    out_dir="export",
    name="study",
    style="colorful",
    figure_title="My Study",
    save_format=["png", "pdf"],
)
# export/study.png             (figure)
# export/study.cohort.json     → paste into "Cohort data (JSON)"
# export/study.style.toml      → paste into "TOML overrides"
```

Full details in
[the docs](https://fschwar4.github.io/pycohortflow/customise.html#exporting-for-the-interactive-generator).

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
- [x] Add: Export Python data + resolved style as a paste-ready `.cohort.json` + `.style.toml` pair for the Interactive Generator (delivered as `export()` and `plot_and_export()` in v0.1.4)
- [ ] Add: "Load Bundle" button in the Interactive Generator that reads a single combined JSON file (data + style + meta) and auto-populates all inputs, removing the two-textarea paste step
- [ ] Add: Python-based PRISMA2020 style generation, if necessary
- [ ] Add: Diagrams for multiple Arms (e.g. something like CONSORT style)
- [ ] Add: Multi-source / multi-center patient recruitment — support several parallel input streams (e.g. one box per recruiting site or registry) that merge into a single downstream cohort flow, including aggregated participant counts and per-source labelling
- [ ] Add: Full test coverage — assert per-node `color` and `exclusion_color` overrides actually change rendered `facecolor`; assert `[exclusion] mode` can be overridden via a custom TOML file; cover the `verbose=True` print path; consider an image-comparison regression test
- [ ] Consider: switch the `verbose=True` print path to standard Python `logging` so callers can control level, destination and handlers without per-call flags
<!-- ROADMAP-END -->


## Citing pycohortflow

If you use `pycohortflow` in your research, please cite **both** the
descriptive paper *and* the specific software version you used. The
Zenodo link is the **concept DOI**, which always resolves to the latest
archived version; from there, pick the version DOI matching the release
you actually used so readers can reproduce your analysis.

- **Paper** (methodology and design):
  Schwarz, F. (2026). *pycohortflow: Lightweight, customisable
  cohort flow diagrams in Python and JavaScript.* MetaArXiv.
  https://doi.org/10.31222/osf.io/ncya2

- **Software version** (for reproducibility):
  Schwarz, Friedrich. *Pycohortflow.* Zenodo, 2026.
  https://doi.org/10.5281/zenodo.20052730

A `CITATION.cff` file is included in the repository; GitHub's "Cite this
repository" button and Zotero's importer will produce these citations
automatically.
