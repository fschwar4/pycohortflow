"""Sync the roadmap from ``docs/roadmap.rst`` into ``README.md``.

The RST file is the single source of truth.  Bullet items use Unicode
emoji to encode checkbox state:

* ``- ✅ ...`` → completed item   (rendered as ``- [x] ...`` in MD)
* ``- ⬜ ...`` → outstanding item (rendered as ``- [ ] ...`` in MD)

Inline ``\\`\\`code\\`\\``` (RST double-backtick) becomes ``\\`code\\``` in
Markdown.

Usage::

    python scripts/sync_roadmap.py            # rewrite README.md in place
    python scripts/sync_roadmap.py --check    # exit non-zero if README is stale

The ``--check`` mode is intended for CI / pre-commit verification.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RST_PATH = ROOT / "docs" / "roadmap.rst"
README_PATH = ROOT / "README.md"

START_MARKER = "<!-- ROADMAP-START -->"
END_MARKER = "<!-- ROADMAP-END -->"


def extract_bullets(rst_text: str) -> list[str]:
    """Return roadmap bullet lines from the RST source, in document order.

    Only top-level ``- `` bullets are captured; nested or indented
    lines are ignored.
    """
    return [
        line for line in rst_text.splitlines() if line.startswith("- ")
    ]


def rst_bullet_to_md(line: str) -> str:
    """Convert a single RST bullet line to GitHub-flavoured Markdown."""
    # Emoji checkbox → [x] / [ ]
    line = line.replace("- ✅ ", "- [x] ", 1).replace("- ⬜ ", "- [ ] ", 1)
    # RST double-backtick inline code → MD single-backtick
    line = re.sub(r"``([^`]+)``", r"`\1`", line)
    return line


def render_markdown_block(rst_text: str) -> str:
    """Build the Markdown roadmap block (without the marker comments)."""
    md_lines = [rst_bullet_to_md(line) for line in extract_bullets(rst_text)]
    return "\n".join(md_lines) + "\n"


def replace_block(readme_text: str, new_block: str) -> str:
    """Inject ``new_block`` between the README's roadmap marker comments."""
    pattern = re.compile(
        re.escape(START_MARKER) + r"\n.*?\n" + re.escape(END_MARKER),
        re.DOTALL,
    )
    if not pattern.search(readme_text):
        raise SystemExit(
            f"README.md is missing the roadmap markers "
            f"({START_MARKER!r} / {END_MARKER!r}). "
            "Add them around the roadmap section before running this script."
        )
    replacement = f"{START_MARKER}\n{new_block}{END_MARKER}"
    return pattern.sub(replacement, readme_text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if README.md is out of sync (do not modify it).",
    )
    args = parser.parse_args()

    rst_text = RST_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")

    new_block = render_markdown_block(rst_text)
    expected = replace_block(readme_text, new_block)

    if expected == readme_text:
        print(f"Roadmap is in sync ({len(extract_bullets(rst_text))} items).")
        return 0

    if args.check:
        print(
            "README.md is out of sync with docs/roadmap.rst.\n"
            "Run: python scripts/sync_roadmap.py",
            file=sys.stderr,
        )
        return 1

    README_PATH.write_text(expected, encoding="utf-8")
    print(f"Synced {len(extract_bullets(rst_text))} roadmap items to README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
