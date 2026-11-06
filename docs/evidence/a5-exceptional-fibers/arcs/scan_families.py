"""Deterministic scan of monomial arc families through the origin of the slice; one record per family.

usage: scan_families.py TARGET KIND WORKDIR OUT.jsonl     (KIND in: k-rs, k-pq, near)
Each family runs gen_family.py at jet orders 3 to 7 until the order nu of G(x(s)) appears. The Singular scripts and
logs of the families land in WORKDIR/fam; the per-family records go to OUT.jsonl. The families are independent, so
parallel.ordered_map spreads them over the worker pool (GOROROBA_WORKERS caps it).
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import gen_family as g
from arc_targets import ROOT, TARGETS

NS = [3, 4, 5, 6, 7]
BC = [(1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (3, 1), (2, 3), (3, 2), (3, 3)]

Job = tuple[str, str, str, int, int, int, int, tuple[Any, ...], str]


def one(job: Job) -> dict[str, object]:
    """Run one family at increasing jet order; the record carries the counts of the first order that finds nu."""
    target_name, workdir, tag, a, b, c, d, etype, coords = job
    target = TARGETS[target_name]
    out = ""
    for n in NS:
        fam = g.Family(f"{tag}_n{n}", a, b, c, d, n, etype, coords)
        out = g.run(target, fam, Path(workdir))
        row = g.parse(out)
        if row is not None:
            row.update(tag=tag, a=a, b=b, c=c, d=d, etype=list(etype), coords=coords, n=n)
            return row
    return {
        "tag": tag,
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        "etype": list(etype),
        "coords": coords,
        "status": f"no order found up to n={NS[-1]}",
    }


def jobs(target_name: str, workdir: str, kind: str) -> list[Job]:
    js: list[Job] = []
    if kind in ("k-rs", "k-pq"):
        coords = kind[2:]
        for a in (1, 2, 3):
            for b, c in BC:
                for d in (1, 2, 3, 4):
                    for k in range(-a, a + 1):
                        if k != 0 and abs(k) == a:
                            continue
                        tag = f"{kind}_a{a}_b{b}_c{c}_d{d}_k{k}"
                        js.append((target_name, workdir, tag, a, b, c, d, ("k", k), coords))
    else:
        for e0 in (-1, 1):
            for j in (1, 2, 3):
                for a in (1, 2, 3):
                    for b, c in BC:
                        for d in (1, 2, 3, 4):
                            tag = f"near_e{e0}_j{j}_a{a}_b{b}_c{c}_d{d}"
                            js.append((target_name, workdir, tag, a, b, c, d, ("near", e0, j), "pq"))
    return js


def scan(target_name: str, workdir: Path, kind: str) -> list[dict[str, object]]:
    """The records of every family of the scan, in job order."""
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    import parallel

    rows: Sequence[dict[str, object]] = parallel.ordered_map(one, jobs(target_name, str(workdir), kind), min_items=1)
    return list(rows)


def main(argv: list[str]) -> int:
    rows = scan(argv[1], Path(argv[3]), argv[2])
    Path(argv[4]).write_text("".join(json.dumps(r) + "\n" for r in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
