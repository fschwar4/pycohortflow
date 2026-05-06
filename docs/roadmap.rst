Roadmap
=======

Planned and in-flight features.  This page is the **single source of
truth**: the matching section in ``README.md`` is generated from this
file by ``scripts/sync_roadmap.py`` (a pre-commit hook keeps the two in
sync).  Use ``✅`` for completed items and ``⬜`` for outstanding ones.

- ✅ Add: Small Diagram version (delivered as the ``minimal`` style in v0.1.3)
- ✅ Add: Verbose option for communication of saving options (delivered as ``verbose=False`` in v0.1.3)
- ✅ Add: Export Python data + resolved style as a paste-ready ``.cohort.json`` + ``.style.toml`` pair for the Interactive Generator (delivered as ``export()`` and ``plot_and_export()`` in v0.1.4)
- ⬜ Add: "Load Bundle" button in the Interactive Generator that reads a single combined JSON file (data + style + meta) and auto-populates all inputs, removing the two-textarea paste step
- ⬜ Add: Python-based PRISMA2020 style generation, if necessary
- ⬜ Add: Diagrams for multiple Arms (e.g. something like CONSORT style)
- ⬜ Add: Multi-source / multi-center patient recruitment — support several parallel input streams (e.g. one box per recruiting site or registry) that merge into a single downstream cohort flow, including aggregated participant counts and per-source labelling
- ⬜ Add: Full test coverage — assert per-node ``color`` and ``exclusion_color`` overrides actually change rendered ``facecolor``; assert ``[exclusion] mode`` can be overridden via a custom TOML file; cover the ``verbose=True`` print path; consider an image-comparison regression test
- ⬜ Consider: switch the ``verbose=True`` print path to standard Python ``logging`` so callers can control level, destination and handlers without per-call flags
