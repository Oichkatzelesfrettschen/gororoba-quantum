#!/usr/bin/env python3
"""Prepare the quadric-ideal comparison of the v2 Rees runs with the weight-slice producer.

For each cell (E8-bar -> N-, E8-bar -> N+, Iso -> N-) at p = 32009, i = 10754, this script

1. regenerates the degree-2 relation lines with weight_slice_fiber_relations.py (the producer whose digest the
   weight-slice record holds) and checks their digest against the digest of the run's own REL lines and, where the
   record has the cell, against the record;
2. writes the producer relations as an ideal KA-CELL.sing in y(1..g);
3. writes the header-slice relation file as an ideal KH-CELL.sing where the cell has one, and prints the supports and
   the F_32009 rank of the union of the two relation sets;
4. cuts the run's script before its Rees stage and appends kcompare-tail.sing, which compares the script's own K with
   KA by mutual reduction, with two known-bad controls, and writes kcmp-CELL.sing.

It runs one Singular process per cell for the producer and none for the comparison; run_kcompare.sh runs the
comparison scripts. Usage: kcompare.py prepare
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

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


def relation_polynomial(line: str, producer) -> tuple[str, dict[tuple[int, int], int]]:
    row: dict[tuple[int, int], int] = {}
    for key, coefficient in producer.parse_relation(line):
        pair = (min(key), max(key))
        row[pair] = (row.get(pair, 0) + int(coefficient)) % PRIME
    row = {pair: value for pair, value in row.items() if value}
    text = "+".join(f"{value}*{monomial(*pair)}" for pair, value in sorted(row.items()))
    return text, row


def header_rows(path: Path) -> list[dict[tuple[int, int], int]]:
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


def rank(rows: list[dict[tuple[int, int], int]]) -> int:
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


def support(rows: list[dict[tuple[int, int], int]]) -> int:
    return len({pair for row in rows for pair in row})


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL {message}")


def prepare() -> None:
    producer = load("weight_slice_fiber_relations", PRODUCER_DIR / "weight_slice_fiber_relations.py")
    checker = load("check_rees_fibers", RUNS / "check_rees_fibers.py")
    record_text = RECORD.read_text(encoding="utf-8")
    for cell, stem, orbit, source, generators, count in CELLS:
        script_text = (RUNS / f"{stem}.sing").read_text(encoding="utf-8")
        log_text = (RUNS / f"{stem}.log").read_text(encoding="utf-8")
        piece = producer.orbit_task(orbit)
        run = producer.run_singular(producer.fiber_script(piece, source, PRIME, ROOT))
        summary = producer.summarize_fiber_run(run)
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
        polynomials, rows = [], []
        for line in run["relations"]:
            text, row = relation_polynomial(line, producer)
            polynomials.append(text)
            rows.append(row)
        require(
            len(polynomials) == count and rank(rows) == count,
            f"{cell}: producer relations are not {count} independent",
        )
        (HERE / f"KA-{cell}.sing").write_text("ideal KA=\n" + ",\n".join(polynomials) + ";\n", encoding="utf-8")
        tail = (HERE / "kcompare-tail.sing").read_text(encoding="utf-8")
        span = ""
        if cell in HEADERS:
            header = header_rows(HEADERS[cell])
            require(len(header) == count and rank(header) == count, f"{cell}: header file is not {count} independent")
            text = HEADERS[cell].read_text(encoding="utf-8").strip().rstrip(",")
            (HERE / f"KH-{cell}.sing").write_text("ideal KH=\n" + text + ";\n", encoding="utf-8")
            union = rank(rows + header)
            sha = hashlib.sha256(HEADERS[cell].read_bytes()).hexdigest()
            print(
                f"SPAN {cell} header_file_sha256 {sha} weight_support {support(rows)} header_support {support(header)} "
                f"union_rank {union}"
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
