"""Images in the Pluecker space of the embedded plane of same-sign X and of the opposite-sign X fiber.

The nullity-16 Rees record (`a5-kernel-attachments/nullity16-rees-fibers-result.json`) gives, for each incidence
into N+ or N-, the 126 principal four-Pfaffians as a constant matrix applied to the Nakayama generators, over Q(i).
This script reads the 12 linear forms of A = K2 : P from `quadric-and-germ-probes.jsonl` and records two kinds of row:

- `spans`, per basepoint, over Q(i): the ranks of the embedding matrices of the same-sign and the opposite-sign X
  incidence and of the two side by side. Rank 15 + 3 = 18 means the two linear spans share no point, so no point of
  the same-sign fiber has the image of a point of the opposite-sign fiber.
- `plane`, per retained K2 cell, modulo the prime: the ranks of the image of the embedded plane, of the image of the
  opposite-sign fiber and of their sum, and, for the strata VB and V^a of the sign of the basepoint, the rank of the
  linear conditions (iota_k S_0) ^ pi(y) = 0 of composed_limit_sections.py on the same-sign generators and their
  rank together with the 12 forms, and the rank of the same conditions on the three opposite-sign generators. A
  joint rank of 12 puts every condition in the span of the 12 forms, so the embedded plane lies in that section; a
  rank of 3 on three generators leaves no point of the opposite-sign fiber in it.

A `spans` row alone cannot tell skew spans from matrices written in different frames of the 9-dimensional kernel,
since two unrelated subspaces of dimensions 15 and 3 also give rank 18. The `plane` rows separate the two images
through source-against-stratum pairs: the V^a section holds the whole embedded plane and no point of the
opposite-sign fiber. Their ranks 12 and 0, far from the generic 15 and 3, are the evidence that the source and
stratum matrices of a basepoint share one frame. Exact arithmetic throughout; no Singular run.

Usage: embedded_plane_images.py OUT.jsonl; run from any directory.
"""

from __future__ import annotations

import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ATTACH = HERE.parents[1] / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

import composed_limit_sections as cls  # noqa: E402

ROOT_OF_MINUS_ONE = {32009: 10754, 32029: 9115}
# basepoint: (same-sign incidence, opposite-sign incidence, V^a stratum of the basepoint)
BASEPOINTS = {"N-": ("X-->N-", "X+->N-", "Va-->N-"), "N+": ("X+->N+", "X-->N+", "Va+->N+")}
TERM = re.compile(r"([+-]?)y\((\d+)\)")
Gauss = tuple[Fraction, Fraction]


def record16() -> dict[str, Any]:
    data = json.loads((ATTACH / "nullity16-rees-fibers-result.json").read_text())
    return {str(r["incidence"]): r for r in data["incidences"]}


def rank_gauss(rows: list[list[Gauss]]) -> int:
    """Rank over Q(i) by exact elimination."""
    m = [row[:] for row in rows]
    zero = (Fraction(0), Fraction(0))
    rank = 0
    for col in range(len(m[0])):
        pivot = next((i for i in range(rank, len(m)) if m[i][col] != zero), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        a, b = m[rank][col]
        norm = a * a + b * b
        inv = (a / norm, -b / norm)
        m[rank] = [(x * inv[0] - y * inv[1], x * inv[1] + y * inv[0]) for x, y in m[rank]]
        for i in range(rank + 1, len(m)):
            fa, fb = m[i][col]
            if (fa, fb) != zero:
                m[i] = [
                    (x - (fa * u - fb * v), y - (fa * v + fb * u)) for (x, y), (u, v) in zip(m[i], m[rank], strict=True)
                ]
        rank += 1
    return rank


def echelon(rows: list[list[int]], p: int) -> tuple[list[list[int]], list[int]]:
    """Reduced row echelon form modulo p and its pivot columns."""
    m = [[x % p for x in row] for row in rows if any(x % p for x in row)]
    pivots: list[int] = []
    for col in range(len(rows[0]) if rows else 0):
        r = len(pivots)
        pivot = next((i for i in range(r, len(m)) if m[i][col]), None)
        if pivot is None:
            continue
        m[r], m[pivot] = m[pivot], m[r]
        inv = pow(m[r][col], -1, p)
        m[r] = [x * inv % p for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][col]:
                f = m[i][col]
                m[i] = [(x - f * y) % p for x, y in zip(m[i], m[r], strict=True)]
        pivots.append(col)
    return m[: len(pivots)], pivots


def rank_mod(rows: list[list[int]], p: int) -> int:
    return len(echelon(rows, p)[1])


def kernel_mod(rows: list[list[int]], width: int, p: int) -> list[list[int]]:
    reduced, pivots = echelon(rows, p)
    basis = []
    for free in (c for c in range(width) if c not in pivots):
        vec = [0] * width
        vec[free] = 1
        for row, col in zip(reduced, pivots, strict=True):
            vec[col] = -row[free] % p
        basis.append(vec)
    return basis


def form_row(form: str, width: int, p: int) -> list[int]:
    """The coefficient row of a linear form written as signed terms y(k)."""
    if TERM.sub("", form):
        raise ValueError(f"not a sum of signed variables: {form}")
    row = [0] * width
    for sign, index in TERM.findall(form):
        row[int(index) - 1] = (row[int(index) - 1] + (-1 if sign == "-" else 1)) % p
    return row


def flag_rows(form_entries: list[int], embedding: list[list[int]], p: int) -> list[list[int]]:
    """The coefficient rows of (iota_k S_0) ^ pi(y), the linear conditions of composed_limit_sections.flag_equations."""
    n = cls.KERNEL_DIMENSION
    form = [[0] * n for _ in range(n)]
    for value, (a, b) in zip(form_entries, cls.PAIRS, strict=True):
        form[a][b], form[b][a] = value, -value
    rows = []
    for k in range(n):
        for five in cls.FIVES:
            row = [0] * len(embedding[0])
            for position, j in enumerate(five):
                if j == k or not form[k][j]:
                    continue
                rest = tuple(index for index in five if index != j)
                sign = -form[k][j] if position % 2 else form[k][j]
                row = [(x + sign * y) % p for x, y in zip(row, embedding[cls.QUAD_INDEX[rest]], strict=True)]
            rows.append(row)
    return rows


def reduce_matrix(rows: list[list[list[str]]], p: int) -> list[list[int]]:
    return [[cls.reduce_gaussian(cell, p, ROOT_OF_MINUS_ONE[p]) for cell in row] for row in rows]


def spans(basepoint: str) -> dict[str, Any]:
    r16 = record16()
    same, opposite, _ = BASEPOINTS[basepoint]
    ms = [[(Fraction(c[0]), Fraction(c[1])) for c in row] for row in r16[same]["embedding_matrix_rows"]]
    mo = [[(Fraction(c[0]), Fraction(c[1])) for c in row] for row in r16[opposite]["embedding_matrix_rows"]]
    ranks = [rank_gauss(ms), rank_gauss(mo), rank_gauss([x + y for x, y in zip(ms, mo, strict=True)])]
    return {"check": "spans", "basepoint": basepoint, "same": same, "opposite": opposite, "ranks": ranks}


def plane(probe: dict[str, Any]) -> dict[str, Any]:
    r16 = record16()
    p = probe["prime"]
    basepoint = probe["fiber"][-2:]
    same, opposite, va = BASEPOINTS[basepoint]
    es = reduce_matrix(r16[same]["embedding_matrix_rows"], p)
    eo = reduce_matrix(r16[opposite]["embedding_matrix_rows"], p)
    forms = [form_row(f, 15, p) for f in probe["forms"]]
    image = [[sum(row[j] * v[j] for j in range(15)) % p for row in es] for v in kernel_mod(forms, 15, p)]
    fiber = [[row[j] for row in eo] for j in range(3)]
    rec: dict[str, Any] = {"check": "plane", "fiber": probe["fiber"], "prime": p, "opposite": opposite}
    rec["ranks"] = [rank_mod(image, p), rank_mod(fiber, p), rank_mod(image + fiber, p)]
    for name, stratum in (("VB", f"VB->{basepoint}"), ("Va", va)):
        s0 = [row[0] for row in reduce_matrix(r16[stratum]["embedding_matrix_rows"], p)]
        conditions = flag_rows(s0, es, p)
        rec[name] = {
            "stratum": stratum,
            "conditions": rank_mod(conditions, p),
            "with_forms": rank_mod(forms + conditions, p),
            "on_opposite": rank_mod(flag_rows(s0, eo, p), p),
        }
    return rec


def run(job: tuple[str, Any]) -> dict[str, Any]:
    kind, item = job
    return spans(item) if kind == "spans" else plane(item)


def build() -> list[dict[str, Any]]:
    for parent in HERE.parents:
        if (parent / "gororoba_quantum" / "parallel.py").is_file():
            sys.path.insert(0, str(parent / "gororoba_quantum"))
            break
    import parallel

    probes = [json.loads(ln) for ln in (HERE / "quadric-and-germ-probes.jsonl").read_text().splitlines()]
    jobs: list[tuple[str, Any]] = [("spans", basepoint) for basepoint in BASEPOINTS]
    jobs += [("plane", probe) for probe in probes if probe["check"] == "x-colon"]
    rows: list[dict[str, Any]] = parallel.ordered_map(run, jobs, min_items=1)
    return rows


EXPECTED: list[dict[str, Any]] = [
    {"check": "spans", "basepoint": "N-", "same": "X-->N-", "opposite": "X+->N-", "ranks": [15, 3, 18]},
    {"check": "spans", "basepoint": "N+", "same": "X+->N+", "opposite": "X-->N+", "ranks": [15, 3, 18]},
    *(
        {
            "check": "plane", "fiber": fiber, "prime": p, "opposite": opposite, "ranks": [3, 3, 6],
            "VB": {"stratum": f"VB->{fiber[-2:]}", "conditions": 9, "with_forms": 14, "on_opposite": 0},
            "Va": {"stratum": va, "conditions": 9, "with_forms": 12, "on_opposite": 3},
        }
        for fiber, p, opposite, va in (
            ("X- -> N-", 32009, "X+->N-", "Va-->N-"),
            ("X- -> N-", 32029, "X+->N-", "Va-->N-"),
            ("X+ -> N+", 32029, "X-->N+", "Va+->N+"),
        )
    ),
]  # fmt: skip


def check(rows: list[dict[str, Any]]) -> list[str]:
    """The departures of a record from the retained findings, row by row."""
    if len(rows) != len(EXPECTED):
        return [f"{len(rows)} rows, expected {len(EXPECTED)}"]
    return [
        f"row {i}: {got} differs from {want}"
        for i, (got, want) in enumerate(zip(rows, EXPECTED, strict=True))
        if got != want
    ]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    rows = build()
    Path(sys.argv[1]).write_text("".join(json.dumps(r) + "\n" for r in rows))
    problems = check(rows)
    for line in problems:
        print(line)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
