---
title: "pycohortflow: Lightweight, customisable cohort flow diagrams in Python and JavaScript"
subtitle: "Version 0.1.4"

date: "today"
date-format: "DD.MM.YYYY"

author:
  - name: Friedrich Schwarz
    orcid: 0009-0001-1167-8365
    corresponding: true
    email: friedrich.schwarz@uni-goettingen.de
    affiliations:
      - id: aff1
        name: "University of Göttingen"
        department: "Göttingen Campus Institute for Dynamics of Biological Networks (CIDBN)"
        city: "Göttingen"
        country: "Germany"
      - id: aff2
        name: "Max Planck Institute for Dynamics and Self-Organization"
        city: "Göttingen"
        country: "Germany"

keywords:
  - Python
  - JavaScript
  - Matplotlib
  - cohort flow diagram
  - clinical research
  - epidemiology
  - reporting guidelines
  - CONSORT
  - STROBE
  - PRISMA
  - TRIPOD

abstract: |
  Flow diagrams are widely recommended to support transparent reporting of participant or record flow. However, they are frequently omitted, incompletely reported, or generated manually in ways that separate the figure from the analysis code and increase the risk of transcription errors, arithmetic inconsistencies, and outdated counts. `pycohortflow` addresses this narrow but common problem by generating cohort flow diagrams from structured input within Python analysis workflows, making figures easier to reproduce, review, and update. A companion browser-based JavaScript generator allows collaborators to inspect, adjust, or export diagrams directly in the browser, without local software setup. This makes the same structured diagram model usable in both scripted analyses and collaborative manuscript preparation, bridging reproducibility and interdisciplinary accessibility.


bibliography: paper.bib
csl: nature.csl                            
link-citations: true
citations-hover: true

format:
  arxiv-pdf:
    keep-tex: true
    linenumbers: false
    doublespacing: false
    runninghead: "pycohortflow technical description"
    include-in-header:
      text: |
        \usepackage{eso-pic}
        \usepackage{graphicx}
        \AtBeginDocument{%
          \rhead{\scshape \runninghead\ -\ v0.1.4}
          \AddToShipoutPictureBG*{%
            \AtPageUpperLeft{%
              \put(75,-70){\includegraphics[width=8cm]{../docs/_static/logo_wide.png}}%
            }%
          }%
        }
  arxiv-html: default

execute:
  echo: false
  warning: false
---

# Summary

`pycohortflow` is a lightweight Python package for generating publication-ready cohort flow diagrams from a declarative description of cohort selection and analysis steps. These diagrams are commonly used in clinical, epidemiological, and translational research to show how an initial population or record set changes during screening, eligibility assessment, exclusion, follow-up, and final analysis.

The package provides two complementary routes to the same figure type: a Python interface intended for reproducible analysis workflows and a browser-based interactive JavaScript implementation as a no-code option. The Python package supports both explicit and programmatic (stepwise, during an analysis run) construction of the diagram. By coupling the figure to the analysis code that produced the counts, the package reduces a recurring source of manual transcription and arithmetic errors.
The browser-based JavaScript implementation is intended for collaborators who do not use Python. It allows users to enter or edit the same diagram information interactively and export figures without a local software installation. Both back-ends share the same content and configuration schemas, so a diagram designed in the browser can be reproduced from a Python script and vice versa. This is possible due to a strict separation of the *content layer* (cohort flow description) from the *style layer* (TOML configuration). 

The current release is scoped to single-column, monotonically decreasing cohort pipelines, which are common in single-centre observational studies, case series, and small clinical studies.

# Statement of need
Flow diagrams provide a compact visual summary for readers, peer reviewers, and editors to assess the two main threats to the internal validity of clinical and observational research: selection bias and attrition bias. Reporting guidelines for several biomedical study designs emphasise transparent reporting of participant or record flow. CONSORT 2025 includes a flow diagram for randomised controlled trials (RCTs) [@Hopewell2025; @Hopewell2025EE], PRISMA 2020 provides flow diagrams for systematic reviews
and meta-analyses [@Page2021], and STROBE recommends reporting numbers at each stage and considering a flow diagram for observational studies [@vonElm2007]. Prediction-model reporting guidance such as TRIPOD+AI also reflects the broader need to make data sources, participant selection, and analytic populations transparent [@Collins2024]. An overview of these guidelines and their flow diagrams is given by @Ferreira2021.

Despite this near-universal recommendation, compliance with the flow-diagram reporting remains poor in practice. An audit of randomised trial reports found that only 56% of 469 primary reports included a CONSORT flow diagram [@Hopewell2011]. Additional audits across pharmacology, infectious-disease, and early-phase oncology trials report that a substantial fraction of published RCTs either omit the flow diagram entirely or fail to report key items such as reasons for exclusion at allocation or for loss to follow-up [@Shaikh2019; @Godwin2015; @Alger2023].

In practice, such diagrams are often drawn manually in slide editors or vector-graphics software. Manual drawing is flexible, but it separates the figure from the analysis that produced the counts and is often time-consuming. Furthermore, this can easily introduce transcription errors, arithmetic inconsistencies, and outdated figures when cohort definitions or analysis code changes. These risks are especially relevant in small single-centre or clinician-led projects, where authors may not have access to dedicated statistical or design support and where reporting tasks are often completed under substantial time constraints.

`pycohortflow` addresses this narrow but frequent problem in two ways. In Python-based projects, the cohort flow diagram can become data-driven: the same scripts or notebooks that compute cohort counts can construct the diagram input, making the figure easier to reproduce, review, and update. Generating the diagram programmatically from the same data structure that drives the statistical analysis closes this loop and removes a class of preventable errors. While R retains a strong base in clinical-trial biostatistics, Python is widely used in data science, AI, and biomedical machine-learning workflows [@StackOverflow2025]. However, few Python tools focus on small, publication-oriented cohort attrition diagrams generated from already-computed counts. This leaves many small clinical and translational projects either drawing such figures manually or using tools outside their main analysis environment.

`pycohortflow` integrates natively with the common Python ecosystem (Jupyter notebooks, Matplotlib subplot composition, standard image-format export) so that this gap can be closed inside the existing analysis script.

At the same time, the JavaScript generator provides a no-installation route for physicians, clinical collaborators, and manuscript authors who need to inspect, adjust, or export the figure without writing code. The package can therefore bridge reproducible computational workflows and interdisciplinary manuscript preparation.

As large language models (LLMs) are increasingly used by clinicians and researchers to design analytic workflows and prepare manuscript figures, small, single-purpose repositories gain value as well-tested building blocks that an LLM can incorporate into more complex pipelines, rather than regenerating bespoke plotting code for every study. The package's clear input schema, internal sanity checks, automatic exclusion arithmetic, and externalised TOML styling are designed to provide an unambiguous API.
 
# State of the field
The space of code-driven flow-diagram tools is dominated by R packages, each making different trade-offs. `consort` [@Wang2023] and `ggconsort` [@Gerke2021] target CONSORT RCT diagrams; `flowchart` [@Satorra2026] constructs diagrams directly from a `data.frame` using a tidyverse pipe; `PRISMA2020` [@Haddaway2022] specialises in PRISMA two-column diagrams and exposes an interactive Shiny app. 

In Python, `equiflow` is the closest existing package, but its emphasis is different: it is designed to generate equity-focused cohort selection flow diagrams and to quantify compositional shifts across exclusion steps [@Ellen2026]. This is useful for auditing selection bias in machine-learning and clinical datasets, but it is not primarily a minimal publication-figure tool that renders single-column cohort attrition diagrams from already-computed counts.

Beyond these domain-specific tools, researchers commonly fall back to general-purpose diagram engines such as Graphviz or `DiagrammeR` [@IannoneDiagrammeR] or to slide editors such as PowerPoint, draw.io, or Inkscape, all of which require non-trivial layout work and are difficult to reproduce across revisions.

`pycohortflow` is therefore complementary to existing tools. It integrates natively in the Python ecosystem, e.g., Jupyter notebooks or multi-panel Matplotlib figures. With the additional JavaScript interactive generator as a no-code option, it further facilitates cooperation between clinicians and data scientists. Compared with general diagram engines, it encodes cohort-flow assumptions directly: ordered steps, monotonically non-increasing counts, automatic exclusion arithmetic, and consistent placement of exclusion annotations. Compared with manual drawing, it makes the diagram input inspectable, version-controllable, and reproducible. The package does not aim to replace tools for multi-arm CONSORT diagrams, PRISMA source tracking, or general graph layout.

# Software design
`pycohortflow` is a small two-runtime (Python, JavaScript) utility built around a single declarative input (an ordered list of cohort steps) and a strict separation between the *content layer* (which steps, with what counts and labels) and the *style layer* (TOML files that control colours, spacing, typography, and box geometry). The same input format and the same TOML schema drive both runtimes, so a diagram designed in either can be reproduced exactly in the other.

The Python package exposes a single high-level function, `plot_cfd()`, which takes the cohort list, computes exclusion counts at each transition, validates that participant totals are monotonically non-increasing, and renders the diagram onto a Matplotlib `Axes`. 
Because it draws onto a Matplotlib Axes object, the diagram can be embedded directly into multi-panel publication figures via `plot_cfd(data, ax=axes[i])` and saved in any Matplotlib-supported format (PNG, SVG, PDF, EPS, …). A complementary `export()` helper and the convenience wrapper `plot_and_export()` emit a paste-ready `cohort.json` and `style.toml` pair, so a figure produced inside an analysis pipeline can be reproduced, tweaked, or re-rendered in the browser without re-running Python.

A JavaScript port of the layout algorithm ships embedded in the Sphinx documentation as an in-browser interactive generator, allowing collaborators without a Python environment to assemble, edit, and export diagrams. Rendering uses native SVG; PNG and PDF export are implemented client-side (PDF via the jsPDF library), so no server component, no account, and no local installation are required.

Styling is externalised. Three built-in TOML styles (`white`, `colorful`, `minimal`) cover common publication needs. User TOML files can override individual parameters on top of a base style, and per-node fields allow exceptional overrides for individual boxes (for example, a non-default colour for the last node). The same layered configuration is consumed by both the Python and the JavaScript implementations, so the visual result is determined by the style file rather than by the runtime.

The package is implemented in pure Python with `matplotlib` and `tomli-w` as runtime dependencies (plus `tomli` on Python < 3.11; on 3.11+ the standard-library `tomllib` is used). The package is tested via a unit-test suite and an end-to-end notebook test executed via `nbmake`, which re-renders the example cohort with all built-in styles on every CI run. Documentation is auto-deployed to GitHub Pages via GitHub Actions from the same repository. The package is distributed through PyPI under the [EUPL-1.2 licence](https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12). Releases are archived on Zenodo with a concept DOI for citation and version-specific DOIs for each tagged release; the project additionally ships a `CITATION.cff` file so that GitHub's "Cite this repository" action returns a structured citation. The accompanying preprint is published on [OSF MetaArXiv](https://doi.org/10.31222/osf.io/ncya2).

::: {#fig-styles layout-ncol=3}
![`white`](../docs/_static/clinical_flow_chart_white.png){#fig-white}

![`colorful`](../docs/_static/clinical_flow_chart_colorful.png){#fig-colorful}

![`minimal`](../docs/_static/clinical_flow_chart_minimal_white.png){#fig-minimal}

The three built-in TOML styles applied to the same example cohort. Style files are externalised, so the identical input renders consistently in Python and in the in-browser JavaScript generator.
:::

# Research impact statement
`pycohortflow` turns cohort flow diagrams from manually edited figures into reproducible outputs of an analysis workflow. This is relevant to research fields in which participant flow, attrition, eligibility, and analytic-sample definition are central to interpretation. By making the figure data-driven, the package helps align manuscript figures with analysis code and reduces opportunities for manual transcription or arithmetic errors.
The browser-based generator additionally lowers the entry barrier for clinical collaborators without a Python toolchain or coding background, which makes the package especially useful for reproducible figure generation in interdisciplinary projects where not every contributor uses the same computational tools.

The project is at an early stage and should be interpreted accordingly. It is not a general flowchart editor, a graph-layout engine, or a full implementation of all CONSORT and PRISMA diagram variants. Nevertheless, the project is publicly available (under EUPL-1.2), documented, installable from PyPI, and accompanied by an interactive browser generator. So far, the software has been used by the author to produce cohort flow diagrams for manuscripts currently under review or in preparation. The public list of downstream uses will be updated when those manuscripts become available.

# Acknowledgements

The author thanks the developers and maintainers of the open-source software on which `pycohortflow` depends — in particular Matplotlib [@Hunter2007] for the Python rendering back-end, the `tomli` / `tomli-w` projects for TOML parsing and serialisation, jsPDF [@jsPDF] for client-side PDF export in the browser-based interactive generator, and the wider Python and JavaScript open-source ecosystems. The author also thanks clinical and scientific collaborators whose manuscript workflows motivated the package design.

# AI usage disclosure

Generative AI tools were used during the development of this software and the preparation of
this manuscript. All AI-assisted outputs were reviewed, edited, and validated by the human
author, who made all core design decisions.

*Software Development*: Opus 4.6 and Opus 4.7 for code suggestions and code review assistance.  
*Documentation*: Opus 4.6 and Opus 4.7 for initial drafts and layout formatting.  
*Paper Authoring*: Opus 4.7 and ChatGPT 5.5 for spelling, grammar and overall reading flow improvements.  
*Human Oversight*: The author made all architectural and design decisions for the software,
determined the scientific content and framing of the paper, and reviewed and validated all
AI-assisted outputs before inclusion. No AI-generated code or text was included without human
verification and editing.

# Availability
The source code is publicly available on GitHub: <https://github.com/fschwar4/pycohortflow>.  
Documentation is available at <https://fschwar4.github.io/pycohortflow/>.  
The interactive browser generator is available at <https://fschwar4.github.io/pycohortflow/generator.html>.  
The Python package is distributed through PyPI: <https://pypi.org/project/pycohortflow/>.  
Zenodo Concept DOI: <https://doi.org/10.5281/zenodo.20052730>.  
OSF persistent DOI: <https://doi.org/10.31222/osf.io/ncya2>.

# References

::: {#refs}
:::