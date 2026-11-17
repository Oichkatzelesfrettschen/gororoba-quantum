#!/usr/bin/env python3
"""Prepare the quadric-ideal comparison of the v2 Rees runs with the weight-slice producer, cells in parallel.

For each cell (E8-bar -> N-, E8-bar -> N+, Iso -> N-) at p = 32009, i = 10754, this script

1. regenerates the degree-2 relation lines with weight_slice_fiber_relations.py (the producer whose digest the
   weight-slice record holds) and checks their digest against the digest of the run's own REL lines and, where the
   record has the cell, against the record;
2. writes the producer relations as an ideal KA-CELL.sing in y(1..g);
3. writes the header-slice relation file as an ideal KH-CELL.sing where the cell has one, and prints the supports and
   the F_32009 rank of the union of the two relation sets;
4. cuts the run's script before its Rees stage and appends kcompare-tail.sing, which compares the script's own K with
   KA by mutual reduction, with two known-bad controls, and writes kcmp-CELL.sing.

The Singular regenerations of the three cells are independent processes and so are the rank computations of the
cells: both maps run through parallel.ordered_map (GOROROBA_WORKERS caps the workers). The checks, the printed lines and
the file writes follow in cell order, so the lines and files equal those of kcompare.py. A cell whose Singular run
fails stops the script before it prints a line. run_kcompare.sh runs the comparison scripts.
Usage: kcompare_v2.py prepare
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[2]
RUNS = EVIDENCE / "working" / "runs" / "e8-rees-fibers-v2-p32009"
PRODUCER_DIR = EVIDENCE.parent / "a5-kernel-attachments"
RECORD = PRODUCER_DIR / "weight-slice-fiber-relations-result.json"
HEADERS = {
    "e8-nm": EVIDENCE / "working" / "distribute" / "out" / "a5-e8-d2" / "e8nm_p1" / "d2" / "relations-upto-d2.rel",
    "e8-np": EVIDENCE / "working" / "runs" / "e8_a2" / "e8_k2.rel",
}
PRIME, ROOT = 32009, 10754
# cell name, run script stem, orbit, producer source, generator count, relation count
CELLS = [
    ("e8-nm", "e8-nm-p.v2-u-full", "N-", "e8", 21, 148),
    ("e8-np", "e8-np-p.v2-u-full", "N+", "e8", 21, 148),
    ("iso-nm", "iso-nm-p.v2-u-full", "N-", "iso", 17, 68),
]
CUT = 'setring r2; "SOURCE sha256'

sys.path.insert(0, str(PRODUCER_DIR))
import weight_slice_fiber_relations as producer  # noqa: E402

import parallel  # noqa: E402  (on sys.path once the producer is imported)

Rows = list[dict[tuple[int, int], int]]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def monomial(first: int, second: int) -> str:
    return f"y({first})*y({second})"


def relation_polynomial(line: str) -> tuple[str, dict[tuple[int, int], int]]:
    row: dict[tuple[int, int], int] = {}
    for key, coefficient in producer.parse_relation(line):
        pair = (min(key), max(key))
        row[pair] = (row.get(pair, 0) + int(coefficient)) % PRIME
    row = {pair: value for pair, value in row.items() if value}
    text = "+".join(f"{value}*{monomial(*pair)}" for pair, value in sorted(row.items()))
    return text, row


def header_rows(path: Path) -> Rows:
    """The header relation file as rows over F_p: terms c*y(a)*y(b) or c*y(a)^2 split on the plus signs."""
    rows = []
    for entry in path.read_text(encoding="utf-8").strip().rstrip(",").split(",\n"):
        row: dict[tuple[int, int], int] = {}
        for term in entry.strip().split("+"):
            coefficient, _, rest = term.partition("*")
            if "^2" in rest:
                first = second = int(rest.split("(")[1].split(")")[0])
            else:
                first, second = (int(part.split(")")[0]) for part in rest.split("y(")[1:])
            pair = (min(first, second), max(first, second))
            row[pair] = (row.get(pair, 0) + int(coefficient)) % PRIME
        rows.append({pair: value for pair, value in row.items() if value})
    return rows


def rank(rows: Rows) -> int:
    pivots: dict[tuple[int, int], dict[tuple[int, int], int]] = {}
    for original in rows:
        row = dict(original)
        while row:
            lead = min(row)
            if lead not in pivots:
                inverse = pow(row[lead], -1, PRIME)
                pivots[lead] = {key: value * inverse % PRIME for key, value in row.items()}
                break
            factor = row[lead]
            for key, value in pivots[lead].items():
                row[key] = (row.get(key, 0) - factor * value) % PRIME
                if row[key] == 0:
                    del row[key]
    return len(pivots)


def support(rows: Rows) -> int:
    return len({pair for row in rows for pair in row})


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL {message}")


def analyze_cell(task: tuple[list[str], Path | None]) -> dict[str, Any]:
    """The polynomials and ranks of one cell's relation lines and, where it has one, of its header relation file."""
    lines, header_path = task
    polynomials, rows = [], []
    for line in lines:
        text, row = relation_polynomial(line)
        polynomials.append(text)
        rows.append(row)
    analysis: dict[str, Any] = {"polynomials": polynomials, "rank": rank(rows), "support": support(rows)}
    if header_path is not None:
        header = header_rows(header_path)
        analysis |= {
            "header_count": len(header),
            "header_rank": rank(header),
            "header_support": support(header),
            "union_rank": rank(rows + header),
        }
    return analysis


def prepare() -> None:
    checker = load("check_rees_fibers", RUNS / "check_rees_fibers.py")
    record_text = RECORD.read_text(encoding="utf-8")
    orbits = list(dict.fromkeys(orbit for _, _, orbit, _, _, _ in CELLS))
    pieces = dict(zip(orbits, parallel.ordered_map(producer.orbit_task, orbits, min_items=1), strict=True))
    items = [
        producer.RunItem("cell", orbit, source, PRIME, producer.fiber_script(pieces[orbit], source, PRIME, ROOT))
        for _, _, orbit, source, _, _ in CELLS
    ]
    runs = parallel.ordered_map(producer.run_item, items, min_items=1)
    tasks = [(run["relations"], HEADERS.get(cell[0])) for cell, run in zip(CELLS, runs, strict=True)]
    analyses = parallel.ordered_map(analyze_cell, tasks, min_items=1)
    for (cell, stem, _orbit, _source, generators, count), run, analysis in zip(CELLS, runs, analyses, strict=True):
        script_text = (RUNS / f"{stem}.sing").read_text(encoding="utf-8")
        log_text = (RUNS / f"{stem}.log").read_text(encoding="utf-8")
        summary = run["summary"]
        digest = summary["relations_sha256"]
        run_digest = checker.relations_digest(log_text)
        require(summary["relation_count"] == count, f"{cell}: producer relation count {summary['relation_count']}")
        require(summary["generator_count"] == generators, f"{cell}: producer generator count")
        require(digest == run_digest, f"{cell}: producer digest {digest} differs from the run's {run_digest}")
        in_record = digest in record_text
        print(
            f"TIE {cell} producer_relations_sha256 {digest} run_relations_sha256 {run_digest} "
            f"in_record {int(in_record)}"
        )
        require(
            len(analysis["polynomials"]) == count and analysis["rank"] == count,
            f"{cell}: producer relations are not {count} independent",
        )
        (HERE / f"KA-{cell}.sing").write_text(
            "ideal KA=\n" + ",\n".join(analysis["polynomials"]) + ";\n", encoding="utf-8"
        )
        tail = (HERE / "kcompare-tail.sing").read_text(encoding="utf-8")
        span = ""
        if cell in HEADERS:
            require(
                analysis["header_count"] == count and analysis["header_rank"] == count,
                f"{cell}: header file is not {count} independent",
            )
            text = HEADERS[cell].read_text(encoding="utf-8").strip().rstrip(",")
            (HERE / f"KH-{cell}.sing").write_text("ideal KH=\n" + text + ";\n", encoding="utf-8")
            sha = hashlib.sha256(HEADERS[cell].read_bytes()).hexdigest()
            print(
                f"SPAN {cell} header_file_sha256 {sha} weight_support {analysis['support']} "
                f"header_support {analysis['header_support']} union_rank {analysis['union_rank']}"
            )
            span = tail.split("//SPAN\n", 1)[1]
        cut = script_text.index(CUT)
        prefix = script_text[:cut]
        body = tail.split("//SPAN\n", 1)[0].replace("@CELL@", cell)
        out = prefix + body + (span.replace("@CELL@", cell) if span else "") + f'"KCMP DONE cell {cell}"; quit;\n'
        (HERE / f"kcmp-{cell}.sing").write_text(out, encoding="utf-8")
        print(f"WROTE kcmp-{cell}.sing source {stem}.sing prefix_bytes {cut}")
    print("PREPARE DONE")


def main(argv: list[str]) -> int:
    if argv[1:] != ["prepare"]:
        print(__doc__)
        return 2
    prepare()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
