"""Replay the fixed-support real-rank identities against their retained bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any

SOURCE_FILES = (
    "docs/evidence/four_support_rank/replay.py",
    "gororoba_quantum/four_support_rank.py",
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/rank_charts.py",
    "gororoba_quantum/rank_polynomials.py",
    "gororoba_quantum/rank_attachments.py",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_digests(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def audit(root: Path) -> dict[str, Any]:
    before = source_digests(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    from four_support_rank import audit_four_support_rank

    result = audit_four_support_rank()
    for source in SOURCE_FILES[1:]:
        name = Path(source).stem
        loaded = Path(str(sys.modules[name].__file__)).resolve()
        _require(loaded == (root / source).resolve(), "imported source differs from the declared checkout")
    _require(source_digests(root) == before, "source bytes change during the replay")
    return {"python_version": platform.python_version(), "certificate": result}


def adopt_recorded_interpreter(record: dict[str, Any], retained: dict[str, Any]) -> None:
    """Carry the retained interpreter release into a replay under the same Python major.minor.

    The patch release names the interpreter that wrote result.json; every
    other field compares byte for byte, and a replay under another
    major.minor, or against a retained value that is not a MAJOR.MINOR.PATCH
    release, keeps its own version and differs.
    """
    for holder, key, kept in (
        (record, "python_version", retained),
        (record.get("versions"), "python", retained.get("versions")),
    ):
        if isinstance(holder, dict) and isinstance(kept, dict) and key in holder and isinstance(kept.get(key), str):
            if (
                re.fullmatch(r"\d+\.\d+\.\d+", kept[key])
                and kept[key].split(".")[:2] == str(holder[key]).split(".")[:2]
            ):
                holder[key] = kept[key]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare recomputed bytes with result.json")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    record = audit(bundle.parents[2])
    if arguments.check:
        adopt_recorded_interpreter(record, json.loads((bundle / "result.json").read_bytes()))
    result = json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        _require(result.encode() == (bundle / "result.json").read_bytes(), "replay differs from retained result bytes")
        print("Four-support real-rank identities, rational frames, source stability and negative controls pass")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
