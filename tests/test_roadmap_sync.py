"""CI safety net: README.md must stay in sync with docs/roadmap.rst.

If this test fails, run::

    python scripts/sync_roadmap.py

and commit the regenerated ``README.md``.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sync_roadmap.py"


def test_roadmap_in_sync():
    """Verify README.md matches the rendered docs/roadmap.rst."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, (
        "README.md is out of sync with docs/roadmap.rst. "
        "Run `python scripts/sync_roadmap.py` to regenerate.\n"
        f"stderr: {result.stderr}"
    )
