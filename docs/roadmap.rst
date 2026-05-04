Roadmap
=======

Planned and in-flight features.  This page is the **single source of
truth**: the matching section in ``README.md`` is generated from this
file by ``scripts/sync_roadmap.py`` (a pre-commit hook keeps the two in
sync).  Use ``✅`` for completed items and ``⬜`` for outstanding ones.

- ✅ Add: Small Diagram version (delivered as the ``minimal`` style in v0.1.3)
- ✅ Add: Verbose option for communication of saving options (delivered as ``verbose=False`` in v0.1.3)
- ⬜ Add: Python-based PRISMA2020 style generation, if necessary
- ⬜ Add: Diagrams for multiple Arms (e.g. something like CONSORT style)
- ⬜ Add: Full test coverage — assert per-node ``color`` and ``exclusion_color`` overrides actually change rendered ``facecolor``; assert ``[exclusion] mode`` can be overridden via a custom TOML file; cover the ``verbose=True`` print path; consider an image-comparison regression test
- ⬜ Consider: switch the ``verbose=True`` print path to standard Python ``logging`` so callers can control level, destination and handlers without per-call flags
