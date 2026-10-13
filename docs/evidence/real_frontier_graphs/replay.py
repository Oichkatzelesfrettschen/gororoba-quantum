"""Replay real graph, inverse and evaluation certificates from stable sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    root = bundle.parents[2]
    source = root / "gororoba_quantum"
    names = (
        "real_frontier_graphs",
        "real_frontier_contracts",
        "circle_kernel_attachments",
        "projective_kernel_limits",
        "kernel_limits",
        "complex_skew",
        "integral_homology",
        "rank_charts",
        "cd_core",
        "parallel",
    )
    paths = [source / f"{name}.py" for name in names] + [
        Path(__file__).resolve(),
        root / "docs/notes/real_circle_frontier_graphs.md",
        bundle / "proof_obligations.json",
    ]
    before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
    sys.path.insert(0, str(source))
    from real_frontier_contracts import audit

    result = json.dumps(audit(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    for name in names:
        if Path(str(sys.modules[name].__file__)).resolve() != (source / f"{name}.py").resolve():
            raise RuntimeError("loaded module differs from the replay checkout")
    if before != [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]:
        raise RuntimeError("source or proof input changes during replay")
    if arguments.check:
        if result.encode() != (bundle / "result.json").read_bytes():
            raise RuntimeError("real-frontier replay differs from retained evidence")
        print(
            "Real frontier graphs: real inverse, positive domains, symbolic coverage and integral evaluation maps pass"
        )
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
