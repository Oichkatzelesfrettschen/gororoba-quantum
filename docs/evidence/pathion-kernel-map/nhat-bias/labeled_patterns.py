"""Labeled sign patterns of the 252 nullity-12 two-term operands, grouped by H-orbit.

    $PYTHON docs/evidence/pathion-kernel-map/nhat-bias/labeled_patterns.py [--out labeled-patterns.json]

For an operand (i, j, t) with pair class m = i xor j, the ideal kernel-map contrast is -1 on the misaligned pairs
{k, k xor m} (`nhat_spectral.aligned_reps`). The unlabeled signature over all tilings is one value on all 252
operands (`nhat_spectral.orbit_blindness`). This script keeps the labels: it groups the operands by the set of
minus bins, and by that set together with m, and counts which orbits of `hardware_orbits.classify` occur in each
group. A group that holds one orbit identifies it; a group that holds several is a collision.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import nhat_spectral as ns  # noqa: E402

pkm, nb = ns.pkm, ns.nb


def pattern(op: tuple[int, int, int]) -> tuple[int, int, tuple[int, ...]] | None:
    """(nullity, m, minus bins) of the operand; None unless the nullity is 12."""
    m, aligned = ns.aligned_reps(op)
    if len(aligned) != 12:
        return None
    reps = [k for k in range(pkm.DIM) if k < k ^ m and k not in aligned]
    return len(aligned), m, tuple(sorted(x for k in reps for x in (k, k ^ m)))


def build() -> dict[str, Any]:
    ops = [(i, j, t) for i in range(1, pkm.DIM) for j in range(i + 1, pkm.DIM) for t in (1, -1)]
    patterns = nb.parallel.ordered_map(pattern, ops)
    kept = [(op, p) for op, p in zip(ops, patterns, strict=True) if p is not None]
    orbits = nb.parallel.ordered_map(nb.operand_orbit, [op for op, _ in kept], min_items=2)
    out: dict[str, Any] = {"schema": "nhat-labeled-patterns-v1", "operands": len(kept), "orbits": dict(Counter(orbits))}
    for name, key in (("minus_bins", lambda p: p[2]), ("pair_class_and_minus_bins", lambda p: (p[1], p[2]))):
        groups: dict[Any, Counter[str]] = defaultdict(Counter)
        for (_, p), orbit in zip(kept, orbits, strict=True):
            groups[key(p)][orbit] += 1
        kinds = Counter("+".join(sorted(c)) for c in groups.values())
        out[name] = {"values": len(groups), "values_by_orbit_content": dict(sorted(kinds.items()))}
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "labeled-patterns.json")
    arguments = parser.parse_args()
    record = build()
    arguments.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
