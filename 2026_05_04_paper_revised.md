---
title: "pycohortflow: Lightweight, customisable cohort flow diagrams in Python and JavaScript"
tags:
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
authors:
  - name: Friedrich Schwarz
    orcid: 0009-0001-1167-8365
    affiliation: 1
affiliations:
  - name: "[Affiliation placeholder — institution, city, country]"
    index: 1
date: 4 May 2026
bibliography: paper.bib
---

# Summary

`pycohortflow` is a small Python package that turns a declarative list of
cohort steps — participant counts, optional headings and exclusion labels —
into a publication-ready vertical flow diagram with a single function call.
The Python implementation is a thin wrapper around Matplotlib [@Hunter2007]
and pulls in no other runtime dependency. A faithful JavaScript port ships
with the documentation and powers an interactive, in-browser diagram
generator that has zero runtime dependencies and renders SVG natively in
the browser. Both back-ends share the same TOML-based configuration schema,
so a diagram designed in the browser can be reproduced from a Python script
(and vice versa) by reusing the same style file.

The package separates the *content layer* (cohort description) from the
*styling layer* (TOML configuration), so analysis pipelines and visual
design can evolve independently. Three built-in styles (`white`,
`colorful`, `minimal`) cover common needs of small observational studies
and case series; every visual parameter can be overridden through TOML
files or per-call keyword arguments. The package targets small,
single-column vertical attrition diagrams — typical of single-centre
observational studies, case series, and individual arms of larger trials —
where the analytical complexity of multi-arm CONSORT or two-column PRISMA
diagrams is not warranted, but where reproducible, code-generated figures
still substantially reduce manual transcription errors.

# Statement of need

Standard reporting guidelines now exist for almost every major study
design in the biomedical sciences, and most of them prescribe a
participant flow diagram as a mandatory or strongly recommended figure:
CONSORT 2025 for randomised trials [@Hopewell2025; @Hopewell2025EE], with
extensions such as CONSORT-PRO for patient-reported outcomes
[@Calvert2013]; PRISMA 2020 for systematic reviews and meta-analyses
[@Page2021]; STROBE for observational studies in epidemiology
[@vonElm2007]; and TRIPOD+AI for clinical prediction-model studies
[@Collins2024]. A general overview of the role of these guidelines and
their flow diagrams in medical manuscript writing is given by
@Ferreira2021.

Flow diagrams provide the fastest way for readers, peer reviewers, and
editors to assess the two main threats to the internal validity of
clinical and observational research: selection bias and attrition bias.
Despite this near-universal recommendation, compliance with the
flow-diagram component remains poor in practice. Audits across
pharmacology and infectious-disease trials [@Godwin2019; @Pharma2019], and
in early-phase dose-finding oncology trials [@DoseFinding2024], report
that a substantial fraction of published RCTs either omit the flow
diagram entirely or fail to report key items such as reasons for
exclusion at allocation or for loss to follow-up.

A frequently cited driver of these errors is the manual creation of the
figure, typically in a slide editor or vector-graphics program: numbers
are copied from analysis output by hand, boxes are added and removed in
response to revision rounds, and any change to the underlying cohort
definition has to be back-propagated into the figure. This separates the
figure from the analysis code that generated the underlying counts —
breaking reproducibility — and increases the risk of arithmetic
inconsistencies and transcription errors between analysis, text, tables,
and figures.

Generating the diagram programmatically from the same data structure that
drives the statistical analysis closes this loop and removes a class of
preventable errors. `pycohortflow` addresses this narrow but recurring
workflow problem for Python users who need single-column vertical
attrition diagrams. Its intended audience includes clinical researchers,
physicians, epidemiologists, statisticians, and manuscript authors who
already use Python for data processing or figure generation, as well as
their non-coding clinical collaborators, who can use the in-browser
generator to design and export the figure without a Python toolchain.
Python is now the most widely used language for general data science and
biomedical machine learning [@StackOverflow2025], while R retains a
strong base in clinical-trial biostatistics. For Python-first analysis
pipelines, however, no comparably lightweight cohort flow-diagram tool
currently exists, which forces small clinical and translational projects
either to fall back to manual graphics editors or to pull in an entire R
toolchain to render a figure of fewer than ten boxes. `pycohortflow`
integrates natively with the common Python ecosystem (Jupyter notebooks,
Matplotlib subplot composition, standard image-format export) so that
this gap can be closed inside the existing analysis script.

# State of the field

The space of code-driven flow-diagram tools is dominated by R packages,
each making different trade-offs. `consort` [@Wang2023] and `ggconsort`
[@Gerke2021] target CONSORT RCT diagrams; `flowchart` [@Satorra2025]
constructs diagrams directly from a `data.frame` using a tidyverse pipe;
`PRISMA2020` [@Haddaway2022] specialises in PRISMA two-column diagrams
and exposes an interactive Shiny app. In Python, `equiflow`
[@Estiri2024] is the closest existing package, but its purpose is to
surface compositional shifts across exclusion steps for equity audits in
clinical machine-learning research, not to render small,
publication-ready figures from already-computed counts. Beyond these
domain-specific tools, researchers commonly fall back to general-purpose
diagram engines such as Graphviz or `DiagrammeR` [@IannoneDiagrammeR] or
to slide editors such as PowerPoint, draw.io, or Inkscape, all of which
require non-trivial layout work and are difficult to reproduce across
revisions.

`pycohortflow` is complementary to these projects. Its distinguishing
focus is a Python-native, Matplotlib-based implementation for
single-column cohort pipelines with a small dependency footprint and
publication-oriented style configuration. Compared with R tools such as
`consort` and `flowchart`, it integrates naturally into Python analysis
notebooks, scripts, and multi-panel Matplotlib figures. It also provides
a JavaScript interactive generator as a no-code option; the same TOML
configuration produces visually equivalent figures in both runtimes
(matching node geometry, colour palette, and exclusion-text rendering),
allowing clinical co-authors without a Python environment to participate
directly in the figure design. The package is deliberately scoped to
small, single-column vertical diagrams; it does not compete with the
multi-arm CONSORT support of `consort` or the two-column source-tracking
of `PRISMA2020`. This narrow scope keeps the API and the visual defaults
sane for the most common case in small clinical and translational
studies.

# Software design

The public Python API consists of a single high-level function,
`plot_cfd`, that accepts the cohort as an ordered list of dictionaries
with an `N` field (participant count) plus optional `heading`,
`description`, and `exclusion_description` strings, and returns the
resulting Matplotlib `Figure` and `Axes`. Per-node colour and
heading-weight overrides are supported; transition exclusions are
computed automatically from successive `N` values. Inputs are validated
up-front: the function rejects empty cohorts, non-numeric or negative
`N`, and any node whose `N` exceeds the preceding node — all of which
would otherwise produce a silently nonsensical figure.

Styling is layered in three steps: a built-in TOML style file (`white`,
`colorful`, or `minimal`) is loaded first; an optional user-supplied
TOML file is merged on top; finally, selected keyword arguments (`dpi`,
`figsize`, `main_palette`, `exclusion_palette`) override individual
values. This keeps the common case ("just plot it") a one-liner while
allowing fine-grained control without subclassing or monkey-patching.
The JavaScript implementation under `docs/_static/js/` mirrors the same
schema, so a configuration developed against the in-browser generator is
directly reusable from Python.

Figures can be exported in any Matplotlib-supported format (PNG, SVG,
PDF, EPS, …) via the `save_dir`, `img_name`, and `save_format`
parameters, or returned as live `Figure`/`Axes` objects for further
composition — for example, embedding the diagram in a multi-panel
publication figure via `plot_cfd(data, ax=axes[0])`. A `transparent=True`
flag is provided for slides and posters.

The package is tested with a unit-test suite (47 unit tests in v0.1.3)
and an end-to-end notebook test executed via `nbmake`, which re-renders
the example cohort with all three styles on every CI run. Documentation
is auto-deployed to GitHub Pages via GitHub Actions from the same
repository. The package targets Python 3.9–3.13 and Matplotlib >= 3.5.

# Research impact statement

The immediate impact of `pycohortflow` is infrastructural: it turns a
common reporting figure into a reproducible software artefact. This is
directly relevant to fields where participant flow and attrition are
emphasised by reporting guidelines [@Hopewell2025; @Page2021;
@vonElm2007]. By making the figure data-driven, the package aligns
manuscript figures with analysis code and reduces opportunities for
manual transcription or arithmetic errors. The browser-based generator
additionally lowers the entry barrier for clinical collaborators without
a Python toolchain, which makes the package useful as a teaching example
for reproducible figure generation in small clinical research projects.

The package was used to produce the cohort flow diagrams in three
manuscripts currently under peer review or in preparation
[Manuscripts A–C — citations pending]; this list will be updated once
the manuscripts are publicly available. Releases are archived on Zenodo
with a concept DOI for citation and version-specific DOIs for each
tagged release; the project additionally ships a `CITATION.cff` file so
that GitHub's "Cite this repository" action returns a structured
citation.

# AI usage disclosure

Generative AI tools were used during development of this software and
during preparation of this manuscript. All AI-assisted outputs were
reviewed, edited, and validated by the human author, who made all core
design and content decisions.

- *Software development*: Claude Opus 4.6 and Claude Opus 4.7.
- *Documentation*: Claude Opus 4.6 and Claude Opus 4.7.
- *Paper authoring*: Claude Opus 4.7 and ChatGPT (GPT-5 family — verify
  exact model string before submission).
- *Human oversight*: The author made all architectural and design
  decisions for the software, determined the scientific content and
  framing of the paper, and reviewed and validated all AI-assisted
  outputs before inclusion. No AI-generated code or text was included
  without human verification and editing.

# Acknowledgements

The author thanks [collaborators / clinical co-authors / institute] for
feedback on early versions of the package and the flow-diagram styles,
and the maintainers of Matplotlib and the wider Python and JavaScript
open-source ecosystems for the underlying tooling.

# Availability

- *Source code*: <https://github.com/fschwar4/pycohortflow>
- *Documentation*: <https://fschwar4.github.io/pycohortflow/>
- *Interactive Generator*: <https://fschwar4.github.io/pycohortflow/generator.html>
- *Python package*: <https://pypi.org/project/pycohortflow/>
- *Archived release (Zenodo concept DOI)*: [10.5281/zenodo.XXXXXXX — to be
  minted with v0.1.3]
- *License*: BSD 3-Clause (planned for v0.1.3; v0.1.0–v0.1.2 were
  released under AGPL-3.0-only)

# References

<!--
JOSS / OSF builds render this section automatically from paper.bib.
The bibliography file (paper.bib) is included alongside this paper.md.
-->

---

<!--

EDITOR NOTES — REMOVE BEFORE SUBMISSION
=======================================

A. ITEMS TO RESOLVE BEFORE SUBMISSION
-------------------------------------

1. Affiliation placeholder on line 17 — fill in institution, city,
   country.

2. License: this draft assumes the planned switch to BSD-3-Clause has
   been performed before v0.1.3 is tagged and the Zenodo DOI is minted.
   At the time of writing the actual LICENSE file in the repository is
   AGPL-3.0-only. Update LICENSE, pyproject.toml ("license =") and
   CHANGELOG.md before tagging v0.1.3.

3. Zenodo concept DOI in the Availability section is a placeholder
   ("10.5281/zenodo.XXXXXXX"). Replace with the real concept DOI after
   the first Zenodo archiving of v0.1.3.

4. Manuscripts A–C in the Research-impact section are placeholders.
   Replace with concrete citations or, if not yet citable, leave the
   sentence and update post-acceptance via a corrigendum/erratum if
   permitted by the venue.

5. Verify all bibliography entries — see paper.bib editor notes below.

B. paper.bib — keys used in this paper
--------------------------------------

The following BibTeX keys are referenced in the text and must be present
in paper.bib:

  @Hunter2007            J. D. Hunter, Matplotlib, CSE 2007.
                         doi:10.1109/MCSE.2007.55  (verified)
  @Hopewell2025          CONSORT 2025 statement, Hopewell et al.,
                         BMJ 2025.  PMID: 40228833  (DOI to verify)
  @Hopewell2025EE        CONSORT 2025 explanation & elaboration,
                         BMJ 2025.  PMID: 40228832  (DOI to verify)
  @Calvert2013           CONSORT-PRO extension, Calvert et al.,
                         JAMA 2013.  doi:10.1001/jama.2013.879
                         (verify exact DOI before submission)
  @Page2021              PRISMA 2020 statement, Page et al.,
                         BMJ 2021;372:n71.  doi:10.1136/bmj.n71
                         (verified)
  @vonElm2007            STROBE statement, von Elm et al.,
                         The Lancet 2007;370:1453-7.
                         doi:10.1016/S0140-6736(07)61602-X  (verified)
  @Collins2024           TRIPOD+AI, Collins et al., BMJ 2024.
                         PMID: 38636956  (DOI to verify)
  @Ferreira2021          Ferreira & Patiño, J Bras Pneumol 2021;47(2):
                         e20210057.  doi:10.36416/1806-3756/e20210057
                         (verified)
  @Godwin2019            Compliance to CONSORT, infectious-disease
                         RCTs, Godwin et al., 2019. Chapman University
                         Digital Commons, pharmacy_articles/149.
                         (author list to verify)
  @Pharma2019            Evaluation of CONSORT flow-diagram reporting
                         in a national and international pharmacology
                         journal — corresponds to PMC article
                         PMC6801991.  *Look up actual authors and
                         journal at https://pmc.ncbi.nlm.nih.gov/articles/PMC6801991/
                         and replace placeholder author list before
                         submission.*
  @DoseFinding2024       Reporting quality of CONSORT flow diagrams in
                         published early-phase dose-finding clinical
                         trial reports.  ScienceDirect article
                         S1551714423002008 — look up full citation
                         before submission.
  @Wang2023              `consort` R package, Wang AD, CRAN 2023.
                         (cite latest CRAN version)
  @Gerke2021             `ggconsort`, Gerke T., GitHub 2021.
                         https://github.com/tgerke/ggconsort
  @Satorra2025           `flowchart` R package, Satorra et al.,
                         Journal of Open Research Software, 2025.
                         doi:10.5334/jors.649  (verified)
  @Haddaway2022          PRISMA2020 R package, Haddaway et al.,
                         Campbell Systematic Reviews 2022;18(2):e1230.
                         doi:10.1002/cl2.1230  (verified)
  @Estiri2024            Equiflow, PLOS Digital Health 2024.
                         doi:10.1371/journal.pdig.0001342
                         (verify full author order before submission)
  @IannoneDiagrammeR     `DiagrammeR` R package, Iannone R., CRAN.
                         (cite latest CRAN version + URL)
  @StackOverflow2025     Stack Overflow Developer Survey 2025
                         (technology section).
                         https://survey.stackoverflow.co/2025/technology

C. ITEMS DELIBERATELY REMOVED FROM THE PREVIOUS DRAFT
-----------------------------------------------------

- "Single-arm" study-design wording, replaced everywhere with
  "single-column vertical attrition diagrams" — "single-arm" has a
  specific clinical-trial meaning (no comparator) that is too narrow
  for what the package actually supports.
- Bullet "export automatically generated info layers to json to
  finetune layout interactively" was dropped from Software design
  because no such JSON export exists in v0.1.3 source. Re-add only if
  the feature lands in a future release.
- Mixed bibliography keys (@Schulz2010Consort, @Vandenbroucke2007Strobe,
  @Page2021Prisma) were unified to (@Hopewell2025 / @Page2021 /
  @vonElm2007) so each reporting standard is cited under exactly one
  bibkey.

D. SUBMISSION-VENUE CAVEATS
---------------------------

- JOSS now requires at least six months of public development history
  before submission. The first public release of pycohortflow was
  v0.1.0 on 2026-02-13, so the earliest valid JOSS submission window
  is approximately 2026-08-13. OSF Preprints is suitable as an
  immediate venue and does not block a later JOSS submission.
- arXiv has no clean software-paper niche; OSF Preprints is the better
  immediate destination for a biomedical software paper of this kind.

-->
