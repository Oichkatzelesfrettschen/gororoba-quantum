"""Replay bounded exact regressions for the uniform ordinary-doubling theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

SOURCE_FILES = (
    "docs/evidence/four_support_doubling/replay.py",
    "gororoba_quantum/four_support_doubling.py",
    "gororoba_quantum/four_support_geometry.py",
    "gororoba_quantum/four_support_rank.py",
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/rank_charts.py",
)
PROOF_NOTES = (
    "docs/notes/four_support_doubling.md",
    "docs/notes/four_support_incidence_geometry.md",
    "docs/notes/four_support_rank_loci.md",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_digests(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in (*SOURCE_FILES, *PROOF_NOTES)}


def audit(root: Path) -> dict[str, Any]:
    before = source_digests(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    from four_support_doubling import audit_four_support_doubling

    result = audit_four_support_doubling()
    for source in SOURCE_FILES[1:]:
        loaded = Path(str(sys.modules[Path(source).stem].__file__)).resolve()
        _require(loaded == (root / source).resolve(), "loaded module differs from the declared checkout")
    _require(source_digests(root) == before, "source or proof-note bytes change during the replay")
    return {"python_version": platform.python_version(), "certificate": result}


def adopt_recorded_interpreter(record: dict[str, Any], retained: dict[str, Any]) -> None:
    """Carry the retained interpreter release into a replay under the same Python major.minor.

    The patch release names the interpreter that wrote result.json and is
    provenance; every certificate field still compares byte for byte, and a
    replay under another major.minor keeps its own version and differs.
    """
    for holder, key, kept in (
        (record, "python_version", retained),
        (record.get("versions"), "python", retained.get("versions")),
    ):
        if isinstance(holder, dict) and isinstance(kept, dict) and key in holder and isinstance(kept.get(key), str):
            if kept[key].split(".")[:2] == str(holder[key]).split(".")[:2]:
                holder[key] = kept[key]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare recomputed JSON with result.json")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    record = audit(bundle.parents[2])
    if arguments.check:
        adopt_recorded_interpreter(record, json.loads((bundle / "result.json").read_bytes()))
    result = json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        _require(
            result.encode() == (bundle / "result.json").read_bytes(), "doubling replay differs from retained bytes"
        )
        print(
            "Four-support ordinary-doubling operators, frames, inverse maps, resource bounds and negative controls pass"
        )
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
