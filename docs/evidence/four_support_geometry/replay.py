"""Replay restricted smooth-stratum and global incidence evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

SOURCE_FILES = (
    "docs/evidence/four_support_geometry/replay.py",
    "gororoba_quantum/four_support_geometry.py",
    "gororoba_quantum/four_support_rank.py",
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/rank_charts.py",
)
PROOF_NOTE = "docs/notes/four_support_incidence_geometry.md"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_digests(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in (*SOURCE_FILES, PROOF_NOTE)}


def audit(root: Path) -> dict[str, Any]:
    before = source_digests(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    from four_support_geometry import audit_four_support_geometry

    result = audit_four_support_geometry()
    for source in SOURCE_FILES[1:]:
        loaded = Path(str(sys.modules[Path(source).stem].__file__)).resolve()
        _require(loaded == (root / source).resolve(), "loaded module differs from the declared checkout")
    _require(source_digests(root) == before, "source or proof-note bytes change during the replay")
    return {"python_version": platform.python_version(), "certificate": result}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare recomputed JSON with retained result.json")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    result = json.dumps(audit(bundle.parents[2]), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        _require(
            result.encode() == (bundle / "result.json").read_bytes(), "geometry replay differs from retained bytes"
        )
        print("Four-support strata, closure incidences, frame homeomorphism identities, and negative controls pass")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
