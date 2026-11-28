"""Weight-slice unit-replacement Rees fibers of the nullity-8 sources into N- at both roots of -1 (A5-409 cells).

A5-574 completes Iso -> N- (14.4 s, 34 MB) and replays X- -> N- (7.5 s) with the unit-replacement scripts of
working/runs/e8-rees-fibers-v2-p32009 on the weight slice of A5-421, where the header-slice elimination of
nullity16_rees_fibers.py (A5-409) reached its 300 s limit on all ten incidences. This script extends that route to the
other sources into N- and to the second root of -1. Each cell script is the retained iso-nm-p.v2-u-full.sing with two
substitutions and no other change:

- the germ ideal line "ideal J=..." is replaced by the closure equations of the source pulled back to the N- weight
  slice, weight_slice_fiber_relations.source_equations(build_slice("N-"), source), the producer table those runs use;
- the root of -1 in "number i=10754" (both rings) becomes 21255 for the cells of the second root.

The N- slice matrix and every later stage (Pfaffians, Nakayama selection, relations K, unit replacement with its
certificate, pivot, satstd saturation, colon loop, fiber over the origin, L = K test) are the template's own lines.
Every Singular process runs under the A5-409 limits, a 300 s timeout and a 16 GiB address-space limit
(RLIMIT_AS, which bounds the resident set from above), one cell per pool worker. The record keeps each cell's status
(done or timeout), its CERT lines, its FIBER line and its Nakayama count; wall times are not part of the bytes.

Controls: the regenerated Iso -> N- and X- -> N- cells at root 10754 must read the retained FIBER values (68, 5, 23)
and (69, 4, 12); a cell whose J line is the Iso equations with the generator mu' dropped must change its result (the
self-test). The N+ cells need the N+ slice matrix, which the template does not carry, and stay outside this record.
No random draw enters.

Usage:
    "$PYTHON" -B -W error scripts/a5_weight_slice_unit_cells.py --self-test
    R=docs/evidence/a5-weight-slice-unit-cells/result.json
    "$PYTHON" -B -W error scripts/a5_weight_slice_unit_cells.py --out "$R"
    "$PYTHON" -B -W error scripts/a5_weight_slice_unit_cells.py --check "$R"
"""

from __future__ import annotations

import argparse
import json
import re
import resource
import subprocess
import sys
import tempfile
import time
from functools import cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-attachments"))

import weight_slice_fiber_relations as ws  # noqa: E402

import parallel  # noqa: E402

TEMPLATE = ROOT / "docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-p32009/iso-nm-p.v2-u-full.sing"
ROOTS = (10754, 21255)
SOURCES = ("iso", "xm", "xp", "w8")
TIMEOUT_SECONDS = 300
ADDRESS_SPACE_BYTES = 16 * 1024**3
RETAINED = {("iso", 10754): (68, 5, 23), ("xm", 10754): (69, 4, 12)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


@cache
def equations(source: str, drop_first: bool = False) -> str:
    gens = ws.source_equations(ws.build_slice("N-"), source)
    if drop_first:
        gens = gens[1:]
    return ",".join(gens)


def cell_script(source: str, root: int, drop_first: bool = False) -> str:
    lines = TEMPLATE.read_text(encoding="utf-8").split("\n")
    j_lines = [k for k, line in enumerate(lines) if line.startswith("ideal J=")]
    require(len(j_lines) == 1, "the template has no single J line")
    k = j_lines[0]
    rest = lines[k][lines[k].index("; J=std(J);") :]
    lines[k] = "ideal J=" + equations(source, drop_first) + rest
    text = "\n".join(lines)
    require(text.count("number i=10754") == 2, "the template root occurs other than twice")
    return text.replace("number i=10754", f"number i={root}")


def limit() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE_BYTES, ADDRESS_SPACE_BYTES))


def run_cell(job: tuple[str, int, bool]) -> dict[str, Any]:
    """One cell: Singular on the generated script under the A5-409 limits."""
    source, root, drop_first = job
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cell.sing"
        path.write_text(cell_script(source, root, drop_first), encoding="utf-8")
        start = time.perf_counter()
        try:
            out = subprocess.run(
                ["Singular", "-q", "--no-warn", "--no-rc", str(path)],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=TIMEOUT_SECONDS,
                preexec_fn=limit,
                cwd=tmp,
            )
            text, status = out.stdout, "done" if out.returncode == 0 else f"exit {out.returncode}"
        except subprocess.TimeoutExpired as exc:
            raw = exc.stdout or b""
            text = raw.decode() if isinstance(raw, bytes) else raw
            status = "timeout"
        seconds = time.perf_counter() - start
    certs = sorted({line.strip() for line in text.splitlines() if line.strip().startswith("CERT")})
    fiber = [line.strip() for line in text.splitlines() if line.strip().startswith("FIBER")]
    nak = re.search(r"NAKAYAMA generators\s+(\d+)", text)
    triple = None
    for line in fiber:
        m = re.search(r"minimal generators\s+(\d+).*?dim\s+(\d+).*?mult\s+(\d+)", line)
        if m:
            triple = [int(m.group(1)), int(m.group(2)), int(m.group(3))]
    print(f"cell {source} {root} drop={drop_first}: {status} {seconds:.1f} s", file=sys.stderr)
    return {
        "source": source,
        "root": root,
        "mutant": drop_first,
        "status": status,
        "nakayama": int(nak.group(1)) if nak else None,
        "cert": certs,
        "fiber": fiber,
        "fiber_triple": triple,
    }


def compute() -> dict[str, Any]:
    jobs = [(s, r, False) for r in ROOTS for s in SOURCES]
    rows = parallel.ordered_map(run_cell, jobs, min_items=1)
    return {"template": str(TEMPLATE.relative_to(ROOT)), "timeout_seconds": TIMEOUT_SECONDS, "cells": rows}


def validate(result: dict[str, Any]) -> None:
    by = {(c["source"], c["root"]): c for c in result["cells"]}
    for key, triple in RETAINED.items():
        c = by[key]
        require(c["status"] == "done" and c["fiber_triple"] == list(triple), f"control {key}: {c['fiber_triple']}")
    for c in result["cells"]:
        if c["status"] == "done":
            require(not any("FAIL" in x for x in c["cert"]), f"{c['source']} {c['root']}: a failed certificate")
            require(any("outside_K 0 K_outside_fiber 0" in x for x in c["fiber"]), f"{c['source']} {c['root']}: L != K")


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    base = run_cell(("iso", 10754, False))
    mut = run_cell(("iso", 10754, True))
    control(base["fiber_triple"] == [68, 5, 23], mut["fiber_triple"] == [68, 5, 23], "Iso without mu'")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 1 paired control passes")
        return 0
    result = compute()
    validate(result)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print("record differs from its recomputation", file=sys.stderr)
        return 1
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
