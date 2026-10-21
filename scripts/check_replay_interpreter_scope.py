"""Hold every exact replay's adopt_recorded_interpreter to its patch-release scope.

Each listed replay byte-compares result.json after carrying the retained
Python patch release into its recomputed record. This check loads every copy
of the helper and requires it to adopt only a MAJOR.MINOR.PATCH release of
the same major.minor, in both record shapes, and to leave every other field,
the SymPy version included, as the replay computed it.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REPLAYS = (
    "docs/evidence/local_schur/probe.py",
    "docs/evidence/four_support_rank/replay.py",
    "docs/evidence/four_support_geometry/replay.py",
    "docs/evidence/four_support_doubling/replay.py",
    "docs/evidence/four_support_homology/replay.py",
    "docs/evidence/dimension32_skew_schur/replay.py",
    "docs/evidence/nullity_twelve_locus/replay.py",
    "docs/evidence/kernel_limits/replay.py",
    "docs/evidence/schur_acceleration/replay.py",
    "docs/evidence/principal_skew_atlas/replay.py",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load(relative: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"replay_{len(relative)}_{abs(hash(relative))}", ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{relative}: no module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def adopted(module: ModuleType, record: dict[str, Any], retained: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(record)
    module.adopt_recorded_interpreter(result, retained)
    return result


def check(relative: str) -> None:
    module = load(relative)
    flat = {"python_version": "3.14.8", "certificate": {"x": 1}}
    nested = {"versions": {"python": "3.14.8", "sympy": "1.14.1"}, "records": [1]}
    cases: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = [
        (flat, {"python_version": "3.14.7"}, {**flat, "python_version": "3.14.7"}),
        (flat, {"python_version": "3.15.0"}, flat),
        (flat, {"python_version": "3.1.48"}, flat),
        (flat, {"python_version": "3.14"}, flat),
        (flat, {"python_version": "3.14.7 text"}, flat),
        (flat, {"python_version": 3.14}, flat),
        (flat, {}, flat),
        (flat, {"python_version": "3.14.7", "certificate": {"x": 2}}, {**flat, "python_version": "3.14.7"}),
        (
            nested,
            {"versions": {"python": "3.14.7", "sympy": "1.14.0"}},
            {**nested, "versions": {"python": "3.14.7", "sympy": "1.14.1"}},
        ),
        (nested, {"versions": {"python": "3.13.9", "sympy": "1.14.1"}}, nested),
        (nested, {"versions": None}, nested),
        (nested, {"python_version": "3.14.7"}, nested),
    ]
    for record, retained, expected in cases:
        require(adopted(module, record, retained) == expected, f"{relative}: adopts {retained!r} into {record!r}")


def main() -> int:
    for relative in REPLAYS:
        check(relative)
    print(f"replay interpreter scope: {len(REPLAYS)} replays adopt only a same-major.minor patch release")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
