"""Rerun the independent kernel-bundle verifiers and fail unless every statement is confirmed.

The verifiers of `docs/evidence/a5-kernel-bundles/` and of this directory exit zero whatever their verdicts, and their
records carry wall-clock timings, so a byte replay cannot gate them. This runner executes both into a temporary
directory, reads each statement verdict, and exits nonzero on any verdict that does not begin with "confirmed".

Usage:
    GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 "$PYTHON" -B -W error \\
        docs/evidence/a5-kernel-bundles-nullity8/rerun_independent_verifications.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VERIFIERS = (
    ROOT / "docs" / "evidence" / "a5-kernel-bundles" / "verify_kernel_bundles_independent.py",
    HERE / "verify_nullity8_independent.py",
)


def verdicts(record: dict[str, object]) -> dict[str, str]:
    """Statement verdicts of a verifier record, keyed by statement name."""
    found: dict[str, str] = {}
    for key, value in record.items():
        if key.startswith("statement_") and isinstance(value, dict) and "verdict" in value:
            found[key] = str(value["verdict"])
    return found


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as scratch:
        for script in VERIFIERS:
            out = Path(scratch) / f"{script.stem}.json"
            run = subprocess.run(
                [sys.executable, "-B", "-W", "error", str(script), "--out", str(out)],
                capture_output=True,
                text=True,
                check=False,
            )
            if run.returncode != 0:
                failures.append(f"{script.name}: exit {run.returncode}: {run.stderr.strip()[-400:]}")
                continue
            found = verdicts(json.loads(out.read_text()))
            bad = [
                f"{script.name}: {name} is {v!r}" for name, v in sorted(found.items()) if not v.startswith("confirmed")
            ]
            if not found:
                bad.append(f"{script.name}: no statement verdicts")
            failures.extend(bad)
            print(f"{script.name}: {len(found) - len(bad)} of {len(found)} statements confirmed")
    for line in failures:
        print(line, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
