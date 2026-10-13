"""Replay complex skew rank and kernel certificates with source stability checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import sympy as sp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    root = bundle.parents[2]
    source = root / "gororoba_quantum"
    names = (
        "complex_skew",
        "complex_skew_contracts",
        "rank_charts",
        "rank_polynomials",
        "nullity_twelve_locus",
        "skew_schur_charts",
        "cd_core",
        "parallel",
    )
    paths = [source / f"{name}.py" for name in names] + [
        Path(__file__).resolve(),
        root / "docs/notes/complex_skew_rank_geometry.md",
        bundle / "proof_obligations.json",
    ]
    before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
    sys.path.insert(0, str(source))
    from complex_skew_contracts import audit

    result = json.dumps(audit(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    for name in names:
        if Path(str(sys.modules[name].__file__)).resolve() != (source / f"{name}.py").resolve():
            raise RuntimeError("loaded module differs from the replay checkout")
    if before != [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]:
        raise RuntimeError("source or proof inputs change during replay")
    if arguments.check:
        if result.encode() != (bundle / "result.json").read_bytes():
            raise RuntimeError("complex skew replay differs from retained result")
        print(f"Complex skew certificates pass; Python {platform.python_version()}, SymPy {sp.__version__}")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
