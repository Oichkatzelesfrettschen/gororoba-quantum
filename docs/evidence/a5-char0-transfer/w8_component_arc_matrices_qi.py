"""The rank matrices of the two W8 arc families over Q(i), entry by entry as Gaussian rationals.

`w8_component_arcs_qi.py` reports, for each arc family at each basepoint, the rank of [dF | F] at two rational
parameter points, where F is the vector of the 24 limit coordinates and dF holds its partial derivatives by the
five arc parameters. This producer runs the same Singular script and prints the matrices themselves: 24 rows, the
five partial derivatives and then F as columns, every entry split into its real and imaginary part in Q. The
checker reads the record without Singular: it recomputes each rank by exact elimination over Q(i) and compares
order, rank and the count of nonzero limit coordinates with the record of `w8_component_arcs_qi.py`.

Rank 6 of [dF | F] at a point says that the cone over the limits has dimension 6 there: the five parameter
directions and the radial direction F are independent (ledger A5-431).

Run from the repository root: "$PYTHON" docs/evidence/a5-char0-transfer/w8_component_arc_matrices_qi.py [--check]
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import arcs_qi  # noqa: E402
import reduction_check as rc  # noqa: E402
import w8_component_arcs_qi as arcs  # noqa: E402

import parallel  # noqa: E402

RECORD = HERE / "w8-component-arc-matrices-qi.json"
SCHEMA = "gororoba.a5.w8-component-arc-matrices-qi/1"
INPUTS = ("w8_component_arc_matrices_qi.py", *arcs.INPUTS)
LEDGER_ROW = "A5-431"
ROWS = arcs.GENERATORS
PARAMETERS = 5
COLUMNS = PARAMETERS + 1
# The cases of the arc record that carry a claim; the two controls leave V(J) and have no limit matrix.
CASES = tuple(case for case in arcs.CASES if not case[3])
# Column 1 of jacob(Fl) is the derivative by x, zero because x is set to 1 in Fl; columns 2 to 6 are the
# parameters and column 7 is F. The split of an entry into real and imaginary part reads it in Q[I].
DUMP = (
    "matrix M1=p1(Mj); matrix M2=p2(Mj); int ri; int xc=0;"
    " for (ri=1;ri<=nrows(M1);ri++) { if (M1[ri,1]!=0 or M2[ri,1]!=0) { xc=xc+1; } }"
    ' "RESULT x_column_nonzero",xc; "RESULT shape",nrows(M1),ncols(M1);'
    " ring RT=0,(I),dp; matrix N1=imap(S,M1); matrix N2=imap(S,M2);"
    " proc parts(matrix N, int which) { int ri; int ci; matrix cq; number im;"
    " for (ri=1;ri<=nrows(N);ri++) { for (ci=2;ci<=ncols(N);ci++) { cq=coeffs(N[ri,ci],I); im=0;"
    " if (nrows(cq)>1) { im=leadcoef(cq[2,1]); }"
    ' "RESULT e_"+string(which)+"_"+string(ri)+"_"+string(ci-1),leadcoef(cq[1,1]),im; } } }'
    " parts(N1,1); parts(N2,2);"
)

Gaussian = tuple[Fraction, Fraction]
ZERO: Gaussian = (Fraction(0), Fraction(0))


def _times(left: Gaussian, right: Gaussian) -> Gaussian:
    return (left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0])


def _over(left: Gaussian, right: Gaussian) -> Gaussian:
    norm = right[0] * right[0] + right[1] * right[1]
    return _times(left, (right[0] / norm, -right[1] / norm))


def gaussian_rank(matrix: list[list[Gaussian]]) -> int:
    """The rank over Q(i) by exact elimination."""
    rows = [list(row) for row in matrix]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((index for index in range(rank, len(rows)) if rows[index][column] != ZERO), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(rank + 1, len(rows)):
            factor = _over(rows[index][column], rows[rank][column])
            if factor != ZERO:
                rows[index] = [
                    (entry[0] - product[0], entry[1] - product[1])
                    for entry, product in zip(rows[index], (_times(factor, lead) for lead in rows[rank]), strict=True)
                ]
        rank += 1
    return rank


def entries_of(matrix: dict[str, Any]) -> list[list[Gaussian]]:
    return [[(Fraction(entry["re"]), Fraction(entry["im"])) for entry in row] for row in matrix["entries"]]


def singular_script(slug: str, family: str, sign: int, variables: list[str]) -> str:
    script = arcs.singular_script(slug, family, sign, variables)
    if not script.endswith("quit;\n"):
        raise RuntimeError("the arc script does not end in quit")
    return script[: -len("quit;\n")] + DUMP + "\nquit;\n"


def certify(case: tuple[str, str, int, bool]) -> list[dict[str, Any]]:
    slug, family, sign, _ = case
    names = arcs._arc(slug, family, sign, arcs.SLICE_VARIABLES)[0]
    outcome = rc.rees._run_singular(
        singular_script(slug, family, sign, arcs.SLICE_VARIABLES),
        f"w8_component_arc_matrices_{family}",
        8 * rc.TIMEOUT_SECONDS,
    )
    if outcome.status != "completed":
        raise RuntimeError(f"{slug} {family}: {outcome.status} {outcome.diagnostic}")
    results = outcome.results
    if results["shape"].split() != [str(ROWS), str(COLUMNS + 1)] or results["x_column_nonzero"] != "0":
        raise RuntimeError(f"{slug} {family}: shape {results['shape']}, x column {results['x_column_nonzero']}")
    matrices = []
    for which, point in enumerate(arcs_qi.POINTS, 1):
        entries = []
        for row in range(1, ROWS + 1):
            cells = (results[f"e_{which}_{row}_{column}"].split() for column in range(1, COLUMNS + 1))
            entries.append([{"re": str(Fraction(real)), "im": str(Fraction(imaginary))} for real, imaginary in cells])
        matrices.append(
            {
                "id": f"{slug}-{family}-point{which}",
                "ledger_row": LEDGER_ROW,
                "slug": slug,
                "family": family,
                "point": dict(zip(names, point[: len(names)], strict=True)),
                "order_of_G": int(results["nu"]),
                "rows": ROWS,
                "columns": COLUMNS,
                "claimed_rank": int(results[f"rank_{which}"]),
                "columns_meaning": [*(f"dF/d{name}" for name in names), "F"],
                "entries": entries,
            }
        )
    return matrices


def problems(record: dict[str, Any]) -> list[str]:
    """Every way the record fails the claim; an empty list is a pass."""
    found: list[str] = []
    if record.get("schema") != SCHEMA:
        found.append("schema differs")
    if record.get("field") != "Q(i)":
        found.append("the field differs from Q(i)")
    matrices = record.get("matrices", [])
    expected = [f"{slug}-{family}-point{which}" for slug, family, _, _ in CASES for which in (1, 2)]
    if [matrix.get("id") for matrix in matrices] != expected:
        found.append("the matrices are not the eight cases in order")
        return found
    for matrix in matrices:
        label = matrix["id"]
        _, rank, _ = arcs.EXPECTED[matrix["family"]]
        names = arcs._arc(matrix["slug"], matrix["family"], arcs_qi.CASES[matrix["slug"]][2], arcs.SLICE_VARIABLES)[0]
        point = arcs_qi.POINTS[int(label[-1]) - 1]
        if matrix.get("point") != dict(zip(names, point[: len(names)], strict=True)):
            found.append(f"{label}: the parameter point differs")
        if matrix.get("columns_meaning") != [*(f"dF/d{name}" for name in names), "F"]:
            found.append(f"{label}: the column meaning differs")
        if matrix.get("ledger_row") != LEDGER_ROW:
            found.append(f"{label}: the ledger row differs from {LEDGER_ROW}")
        shape = [len(row) for row in matrix.get("entries", [])]
        if (matrix.get("rows"), matrix.get("columns")) != (ROWS, COLUMNS) or shape != [COLUMNS] * ROWS:
            found.append(f"{label}: the shape differs from {ROWS} by {COLUMNS}")
            continue
        computed = gaussian_rank(entries_of(matrix))
        if matrix.get("claimed_rank") != rank:
            found.append(f"{label}: the claimed rank differs from {rank}")
        if computed != matrix.get("claimed_rank"):
            found.append(f"{label}: the rank of the entries is {computed}, the claim is {matrix.get('claimed_rank')}")
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def arc_record_problems(record: dict[str, Any]) -> list[str]:
    """The matrices against the record of `w8_component_arcs_qi.py`: order, rank, nonzero limit coordinates."""
    found: list[str] = []
    rows = {
        (row["slug"], row["family"]): row
        for row in json.loads(arcs.RECORD.read_text(encoding="utf-8"))["rows"]
        if not row["control"]
    }
    for matrix in record.get("matrices", []):
        label = matrix["id"]
        row = rows.get((matrix["slug"], matrix["family"]))
        if row is None:
            found.append(f"{label}: the arc record holds no such row")
            continue
        which = int(label[-1]) - 1
        if matrix["claimed_rank"] != row["ranks"][which]:
            found.append(f"{label}: the rank differs from the arc record")
        if matrix["order_of_G"] != row["order_of_G"]:
            found.append(f"{label}: the order of G differs from the arc record")
        nonzero = sum(row_entries[-1] != ZERO for row_entries in entries_of(matrix))
        if nonzero != row["limit_nonzero"]:
            found.append(f"{label}: {nonzero} nonzero limit coordinates, the arc record holds {row['limit_nonzero']}")
    return found


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    groups = parallel.ordered_map(certify, list(CASES), min_items=2)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {name: _digest(HERE / name) for name in INPUTS},
        "arc_record_sha256": _digest(arcs.RECORD),
        "matrices": [matrix for group in groups for matrix in group],
        "pass": True,
    }
    record["pass"] = problems(record) == []
    return record


def main() -> None:
    if "--check" in sys.argv[1:]:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        found = problems(record) + arc_record_problems(record)
        for name in INPUTS:
            if record["inputs"].get(name) != _digest(HERE / name):
                found.append(f"input digest of {name} differs")
        if record.get("arc_record_sha256") != _digest(arcs.RECORD):
            found.append("digest of the arc record differs")
        if found:
            raise SystemExit("\n".join(found))
        print("w8-component-arc-matrices-qi.json: pass")
        return
    record = build()
    found = problems(record) + arc_record_problems(record)
    RECORD.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
