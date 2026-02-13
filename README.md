<p align="center">
  <img src="docs/_static/logo_wide.svg" alt="pycohortflow logo" width="100%" />
</p>

# pycohortflow

Lightweight cohort flow diagrams built on Matplotlib.

Turn a plain Python list of cohort steps into a publication-ready vertical flow chart with a single function call. Colours, fonts, spacing, and box geometry are fully customisable via TOML configuration files.

## Installation

```bash
pip install pycohortflow
```

## Quick Start

```python
from pycohortflow import plot_cohort_flow_diagram
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

fig, ax = plot_cohort_flow_diagram(
    data,
    figure_title="Clinical Cohort Flow Diagram",
)
plt.show()
```

## Built-in Styles

Two styles ship with the package:

<p align="center">
  <img src="docs/_static/clinical_flow_chart_white.png" alt="White style preview" width="45%" />
  <img src="docs/_static/clinical_flow_chart_colorful.png" alt="Colorful style preview" width="45%" />
</p>

```python
# Clean white boxes (default)
fig, ax = plot_cohort_flow_diagram(data, style="white")

# Pastel gradient backgrounds
fig, ax = plot_cohort_flow_diagram(data, style="colorful")

# Transparent figure background (for slides / posters)
fig, ax = plot_cohort_flow_diagram(data, transparent=True)
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
fig, ax = plot_cohort_flow_diagram(data, style_config_path="my_style.toml")
```

See the [full documentation](https://yourusername.github.io/pycohortflow/) for all available options.

## Saving Figures

```python
fig, ax = plot_cohort_flow_diagram(
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

AGPL-3.0 license

---

## Roadmap

- [ ] python based PRISMA2020 style generation, if necessary
