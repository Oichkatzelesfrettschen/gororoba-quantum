"""Replay the fixed-support geometric cellular and integral homology certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

SOURCE_FILES = (
    "docs/evidence/four_support_homology/replay.py",
    "gororoba_quantum/four_support_homology.py",
    "gororoba_quantum/four_support_doubling.py",
    "gororoba_quantum/four_support_geometry.py",
    "gororoba_quantum/four_support_rank.py",
    "gororoba_quantum/integral_homology.py",
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/parallel.py",
    "gororoba_quantum/rank_charts.py",
)
PROOF_NOTES = (
    "docs/notes/four_support_cellular_homology.md",
    "docs/notes/four_support_doubling.md",
    "docs/notes/four_support_incidence_geometry.md",
    "docs/notes/four_support_rank_loci.md",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def source_digests(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in (*SOURCE_FILES, *PROOF_NOTES)}


def validate_binding(
    actual_digests: dict[str, str], expected_digests: dict[str, str], loaded: Path, declared: Path
) -> None:
    _require(actual_digests == expected_digests, "source or proof-note bytes change during replay")
    _require(loaded.resolve() == declared.resolve(), "loaded module differs from the declared checkout")


def audit(root: Path) -> dict[str, Any]:
    before = source_digests(root)
    sys.path.insert(0, str(root / "gororoba_quantum"))
    from four_support_homology import audit_four_support_homology

    result = audit_four_support_homology()
    after = source_digests(root)
    for source in SOURCE_FILES[1:]:
        loaded = Path(str(sys.modules[Path(source).stem].__file__))
        validate_binding(after, before, loaded, root / source)
    mutated = dict(before)
    mutated[SOURCE_FILES[1]] = "0" * 64
    controls = []
    for digests, declared, label in (
        (mutated, root / SOURCE_FILES[1], "changed_source_digest"),
        (before, root / "undeclared-module.py", "changed_loaded_module_path"),
    ):
        try:
            validate_binding(digests, before, root / SOURCE_FILES[1], declared)
        except RuntimeError:
            controls.append(label)
        else:
            raise RuntimeError("source binding mutation escapes rejection")
    return {
        "python_version": platform.python_version(),
        "source_sha256": before,
        "provenance_negative_controls": controls,
        "certificate": result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare the complete recomputed result with result.json")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    result = json.dumps(audit(bundle.parents[2]), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if arguments.check:
        _require(
            result.encode() == (bundle / "result.json").read_bytes(), "homology replay differs from retained bytes"
        )
        print("Four-support CW, integral homology, uniform grading, cup products and negative controls pass")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
