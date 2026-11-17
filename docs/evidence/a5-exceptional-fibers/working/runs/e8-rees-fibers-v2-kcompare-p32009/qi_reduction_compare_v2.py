#!/usr/bin/env python3
"""Compare the Q(i) weight-slice relations of A5-474 with the modular relations of the v2 Rees runs, cells in parallel.

For each cell (E8-bar -> N-, E8-bar -> N+, Iso -> N-) this script regenerates, with weight_slice_fiber_relations.py,
the degree-2 relation lines over Q(i) and the lines modulo p = 32009 (root of -1 = 10754), and decides
1. that the Q(i) lines hash to the relation digest of the weight-slice record cell and of the A5-474 membership record,
   and that the modular lines hash to the digest of the run's own REL lines;
2. that the Q(i) lines, reduced with i sent to 10754, span the same subspace of F_32009 as the modular lines
   (compare_reduction of the producer: both ranks and the joint rank agree);
3. that each of two known-bad controls reads unequal before the verdict counts: the Q(i) lines without their first line,
   and the modular lines without their first line.
All relations are forms of degree 2 in y(1..g), so the ideal that a set generates is determined by its span: equal
spans are equal ideals.

The six Singular regenerations (a Q(i) and a modular run per cell) are independent processes and so are the nine
reductions (three per cell): both maps run through parallel.ordered_map (GOROROBA_WORKERS caps the workers). The checks
and the printed lines follow in cell order, so the QIRED lines equal those of qi_reduction_compare.py. Usage:
qi_reduction_compare_v2.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[2]
RUNS = EVIDENCE / "working" / "runs" / "e8-rees-fibers-v2-p32009"
PRODUCER_DIR = EVIDENCE.parent / "a5-kernel-attachments"
RECORD = PRODUCER_DIR / "weight-slice-fiber-relations-result.json"
MEMBERSHIP = PRODUCER_DIR / "weight-slice-relation-membership-result.json"
PRIME, ROOT = 32009, 10754
# cell name, run stem, orbit, producer source, generator count, relation count
CELLS = [
    ("e8-nm", "e8-nm-p.v2-u-full", "N-", "e8", 21, 148),
    ("e8-np", "e8-np-p.v2-u-full", "N+", "e8", 21, 148),
    ("iso-nm", "iso-nm-p.v2-u-full", "N-", "iso", 17, 68),
]
ORBITS = ("N-", "N+")

sys.path.insert(0, str(PRODUCER_DIR))
import weight_slice_fiber_relations as producer  # noqa: E402

import parallel  # noqa: E402  (on sys.path once the producer is imported)


def load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL {message}")


def record_digests() -> tuple[dict[tuple[str, str], str], dict[tuple[str, str], str]]:
    """The Q(i) relation digests of the weight-slice record and of the A5-474 membership record, by (orbit, source)."""
    weight = {
        (cell["orbit"], cell["source"]): cell["relations_sha256"]
        for cell in json.loads(RECORD.read_text(encoding="utf-8"))["cells"]
        if cell["characteristic"] == 0
    }
    member = {
        (cell["orbit"], cell["source"]): cell["relations_sha256"]
        for cell in json.loads(MEMBERSHIP.read_text(encoding="utf-8"))["cells"]
    }
    return weight, member


def reduce_item(item: tuple[list[str], list[str]]) -> dict[str, Any]:
    gaussian_lines, modular_lines = item
    row: dict[str, Any] = producer.compare_reduction(gaussian_lines, modular_lines, PRIME, ROOT)
    return row


def main() -> int:
    checker = load("check_rees_fibers", RUNS / "check_rees_fibers.py")
    weight, member = record_digests()
    pieces = dict(zip(ORBITS, parallel.ordered_map(producer.orbit_task, ORBITS, min_items=1), strict=True))
    items = []
    for _, _, orbit, source, _, _ in CELLS:
        items.append(producer.RunItem("qi", orbit, source, 0, producer.fiber_script(pieces[orbit], source, 0, 0)))
        items.append(
            producer.RunItem("modular", orbit, source, PRIME, producer.fiber_script(pieces[orbit], source, PRIME, ROOT))
        )
    runs = parallel.ordered_map(producer.run_item, items, min_items=1)
    pairs = []
    for position in range(len(CELLS)):
        qi_lines, lines = runs[2 * position]["relations"], runs[2 * position + 1]["relations"]
        pairs += [(qi_lines, lines), (qi_lines[1:], lines), (qi_lines, lines[1:])]
    reductions = parallel.ordered_map(reduce_item, pairs, min_items=1)
    for position, (cell, stem, orbit, source, generators, count) in enumerate(CELLS):
        key = (orbit, source)
        qi = runs[2 * position]["summary"]
        qi_lines = runs[2 * position]["relations"]
        modular_summary = runs[2 * position + 1]["summary"]
        run_digest = checker.relations_digest((RUNS / f"{stem}.log").read_text(encoding="utf-8"))
        require(qi["relation_count"] == count and len(qi_lines) == count, f"{cell}: Q(i) relation count")
        require(qi["generator_count"] == generators, f"{cell}: Q(i) generator count")
        require(modular_summary["relation_count"] == count, f"{cell}: modular relation count")
        require(modular_summary["relations_sha256"] == run_digest, f"{cell}: modular digest differs from the run")
        in_weight = int(qi["relations_sha256"] == weight.get(key))
        in_member = int(qi["relations_sha256"] == member.get(key))
        print(
            f"QIRED {cell} qi_relations_sha256 {qi['relations_sha256']} in_weight_slice_record {in_weight} "
            f"in_a5_474_record {in_member} modular_relations_sha256 {modular_summary['relations_sha256']} "
            f"run_relations_sha256 {run_digest}"
        )
        require(in_weight == 1 and in_member == 1, f"{cell}: Q(i) digest is not that of the records")
        full, drop_qi, drop_modular = reductions[3 * position : 3 * position + 3]
        for label, row in (("full", full), ("control_drop_qi", drop_qi), ("control_drop_modular", drop_modular)):
            print(
                f"QIRED {cell} {label} qi {row['reduced_relations']} modular {row['modular_relations']} "
                f"reduced_rank {row['reduced_rank']} modular_rank {row['modular_rank']} "
                f"joint_rank {row['joint_rank']} spaces_equal {int(row['spaces_equal'])}"
            )
        ok = (
            full["spaces_equal"]
            and full["joint_rank"] == count
            and not drop_qi["spaces_equal"]
            and not drop_modular["spaces_equal"]
        )
        print(
            f"QIRED RESULT cell {cell} spaces_equal {int(full['spaces_equal'])} "
            f"control_drop_qi_unequal {int(not drop_qi['spaces_equal'])} "
            f"control_drop_modular_unequal {int(not drop_modular['spaces_equal'])} pass {int(ok)}"
        )
        require(ok, f"{cell}: verdict or control")
    print("QIRED ALL DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
