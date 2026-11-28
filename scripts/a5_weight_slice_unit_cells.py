"""Weight-slice unit-replacement Rees fibers of the nullity-8 sources into N+ and N- at both roots (A5-409 cells).

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
and (69, 4, 12); the Iso cell with the X- germ equations in its J line must leave (68, 5, 23) (the self-test). The
N+ cells replace the template's first 140 slice-matrix lines (C, F and T, which equal the producer's _matrix_lines for
N- line for line) by the producer's lines for N+, after a check that the remaining producer lines agree for the two
basepoints; their fibers must have the dimension and multiplicity that A5-416 imports for N+.
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
ORBITS = ("N-", "N+")
SOURCES = ("iso", "xm", "xp", "w8")
TIMEOUT_SECONDS = 300
ADDRESS_SPACE_BYTES = 16 * 1024**3
RETAINED = {("N-", "iso", 10754): (68, 5, 23), ("N-", "xm", 10754): (69, 4, 12)}
# A5-416 at N+: Iso a fourfold of degree 23, same-sign X+ a threefold of degree 12, opposite-sign X- the plane P^2
IMPORTED_N_PLUS = {"iso": (5, 23), "xp": (4, 12), "xm": (3, 1)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


MATRIX_LINES = (
    140  # template lines 3..142: the C, F and T matrices that weight_slice_fiber_relations._matrix_lines emits
)


@cache
def equations(source: str, orbit: str = "N-") -> str:
    return ",".join(ws.source_equations(ws.build_slice(orbit), source))


@cache
def matrix_block(orbit: str) -> tuple[str, ...]:
    """The first MATRIX_LINES lines of the producer's slice-matrix block for one basepoint."""
    lines = ws._matrix_lines(ws.build_slice(orbit)).split("\n")
    return tuple(lines[:MATRIX_LINES])


def cell_script(source: str, root: int, j_source: str | None = None, orbit: str = "N-") -> str:
    lines = TEMPLATE.read_text(encoding="utf-8").split("\n")
    start = lines.index("matrix C[15][15];")
    require(tuple(lines[start : start + MATRIX_LINES]) == matrix_block("N-"), "the template matrix block moved")
    rest_n = ws._matrix_lines(ws.build_slice("N-")).split("\n")[MATRIX_LINES:]
    rest_o = ws._matrix_lines(ws.build_slice(orbit)).split("\n")[MATRIX_LINES:]
    require(rest_n == rest_o, "the basepoints differ after the matrix block")
    lines[start : start + MATRIX_LINES] = list(matrix_block(orbit))
    j_lines = [k for k, line in enumerate(lines) if line.startswith("ideal J=")]
    require(len(j_lines) == 1, "the template has no single J line")
    k = j_lines[0]
    rest = lines[k][lines[k].index("; J=std(J);") :]
    lines[k] = "ideal J=" + equations(j_source or source, orbit) + rest
    text = "\n".join(lines)
    require(text.count("number i=10754") == 2, "the template root occurs other than twice")
    return text.replace("number i=10754", f"number i={root}")


def cert_line(line: str) -> str:
    """A CERT line without the trailing timer that the colon line prints after its iteration count."""
    text = line.strip()
    if text.startswith("CERT colon_equal_after_iterations"):
        return " ".join(text.split()[:3])
    return text


def limit() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE_BYTES, ADDRESS_SPACE_BYTES))


def run_cell(job: tuple[str, int, str | None, str]) -> dict[str, Any]:
    """One cell: Singular on the generated script under the A5-409 limits; a timeout keeps its status alone."""
    source, root, j_source, orbit = job
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "cell.sing"
        path.write_text(cell_script(source, root, j_source, orbit), encoding="utf-8")
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
    certs = sorted({cert_line(line) for line in text.splitlines() if line.strip().startswith("CERT")})
    fiber = [line.strip() for line in text.splitlines() if line.strip().startswith("FIBER")]
    nak = re.search(r"NAKAYAMA generators\s+(\d+)", text)
    triple = None
    for line in fiber:
        m = re.search(r"minimal generators\s+(\d+).*?dim\s+(\d+).*?mult\s+(\d+)", line)
        if m:
            triple = [int(m.group(1)), int(m.group(2)), int(m.group(3))]
    print(f"cell {source} {orbit} {root} j={j_source}: {status} {seconds:.1f} s", file=sys.stderr)
    if status == "timeout":
        return {"source": source, "orbit": orbit, "root": root, "j_source": j_source, "status": status}
    return {
        "orbit": orbit,
        "source": source,
        "root": root,
        "j_source": j_source,
        "status": status,
        "nakayama": int(nak.group(1)) if nak else None,
        "cert": certs,
        "fiber": fiber,
        "fiber_triple": triple,
    }


def compute() -> dict[str, Any]:
    jobs = [(s, r, None, o) for o in ORBITS for r in ROOTS for s in SOURCES]
    rows = parallel.ordered_map(run_cell, jobs, min_items=1)
    return {"template": str(TEMPLATE.relative_to(ROOT)), "timeout_seconds": TIMEOUT_SECONDS, "cells": rows}


def validate(result: dict[str, Any]) -> None:
    by = {(c["orbit"], c["source"], c["root"]): c for c in result["cells"]}
    for key, triple in RETAINED.items():
        c = by[key]
        require(c["status"] == "done" and c["fiber_triple"] == list(triple), f"control {key}: {c['fiber_triple']}")
    for root in ROOTS:
        for source, (dim, mult) in IMPORTED_N_PLUS.items():
            c = by[("N+", source, root)]
            require(
                c["status"] == "done" and c["fiber_triple"][1:] == [dim, mult], f"N+ {source} {root} against A5-416"
            )
    for c in result["cells"]:
        if c["status"] == "done":
            require(not any("FAIL" in x for x in c["cert"]), f"{c['source']} {c['root']}: a failed certificate")
            require(any("outside_K 0 K_outside_fiber 0" in x for x in c["fiber"]), f"{c['source']} {c['root']}: L != K")


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    base = run_cell(("iso", 10754, None, "N-"))
    mut = run_cell(("iso", 10754, "xm", "N-"))
    control(base["fiber_triple"] == [68, 5, 23], mut["fiber_triple"] == [68, 5, 23], "the X- germ in the Iso cell")


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
