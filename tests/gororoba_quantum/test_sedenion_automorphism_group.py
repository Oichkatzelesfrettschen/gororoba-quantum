"""Exact computation of the automorphism groups of the cd_core octonions and sedenions.

An automorphism g of a finite-dimensional real algebra A conjugates its derivation algebra Der(A) onto itself.
For the octonions and the sedenions Der(A) is g2 (14-dimensional, computed here over Q), every automorphism of
g2 is inner (its Dynkin diagram has no symmetry), and the inner ones are Ad(h) for h in the connected group
exp(Der(A)) of automorphisms. So g = h c with c an automorphism commuting with Der(A), and Aut(A) is that
connected group times the automorphisms inside the commutant of Der(A). The commutant is computed over Q and
its automorphisms are the real roots of a lex Groebner basis: one for the octonions (Aut(O) = G2) and six for
the sedenions, exactly the S3 that epsilon and psi of Gresnigt (arXiv 2609.10569, Eqs. 60-62) generate, so
Aut(S) = G2 x S3 (docs/evidence/sedenion-automorphisms/README.md).

The same computation on Gresnigt's Table 5 as printed is the mutation control, and the table Rocq evaluates
from the integer pair tower of proofs/CdImaginarySumConference.v binds cd_core's product to the proof's.
"""

import json
import re
from pathlib import Path

import pytest
from sympy import QQ, Matrix, Rational, eye, groebner, solve, sqrt, symbols, zeros
from sympy.polys.matrices import DomainMatrix

import cd_core
import parallel

# One worker builds the census fixture for every test of the module.
pytestmark = pytest.mark.xdist_group("sedenion-automorphism-census")
EVIDENCE = Path(__file__).resolve().parents[2] / "docs/evidence/sedenion-automorphisms"
Table = tuple[tuple[tuple[int, int], ...], ...]


def cd_table(n: int) -> Table:
    """table[p][q] = (sign, index) with e_p e_q = sign e_index under cd_core."""
    return tuple(tuple((cd_core.cd_sign(n, p, q), p ^ q) for q in range(n)) for p in range(n))


def printed_gresnigt_table() -> Table:
    """cd_core's sedenion table with the 11 cells that Table 5 of arXiv 2609.10569v1 prints with the other sign."""
    cells = json.loads((EVIDENCE / "gresnigt_table5_printed.json").read_text(encoding="utf-8"))["cells"]
    flipped = {(cell["row"], cell["column"]) for cell in cells}
    return tuple(
        tuple((-s if (p, q) in flipped else s, k) for q, (s, k) in enumerate(row)) for p, row in enumerate(cd_table(16))
    )


def nullspace(rows: list[list[int]], width: int) -> list[list[Rational]]:
    matrix = DomainMatrix([[QQ(x) for x in row] for row in rows], (len(rows), width), QQ)
    return [[Rational(int(x.numerator), int(x.denominator)) for x in v] for v in matrix.nullspace().to_list()]


def derivations(table: Table) -> list[Matrix]:
    """A basis of the D with D(e_p e_q) = D(e_p) e_q + e_p D(e_q); D[r, c] is the e_r coefficient of D(e_c)."""
    n = len(table)
    rows = []
    for p in range(n):
        for q in range(n):
            s, k = table[p][q]
            for r in range(n):
                row = [0] * (n * n)
                row[r * n + k] += s
                row[(r ^ q) * n + p] -= table[r ^ q][q][0]
                row[(r ^ p) * n + q] -= table[p][r ^ p][0]
                rows.append(row)
    return [Matrix(n, n, v) for v in nullspace(rows, n * n)]


def commutant(basis: list[Matrix], n: int) -> list[Matrix]:
    """A basis of the matrices that commute with every matrix of basis."""
    rows = []
    for d in basis:
        for i in range(n):
            for j in range(n):
                row = [0] * (n * n)
                for k in range(n):
                    row[i * n + k] += int(d[k, j])
                    row[k * n + j] -= int(d[i, k])
                rows.append(row)
    return [Matrix(n, n, v) for v in nullspace(rows, n * n)]


def multiply(table: Table, u: list, v: list) -> list:
    out = [0] * len(table)
    for a, x in enumerate(u):
        if x != 0:
            for b, y in enumerate(v):
                if y != 0:
                    s, k = table[a][b]
                    out[k] += s * x * y
    return out


def is_automorphism(table: Table, g: Matrix) -> bool:
    n = len(table)
    columns = [list(g[:, p]) for p in range(n)]
    for p in range(n):
        for q in range(n):
            s, k = table[p][q]
            product = multiply(table, columns[p], columns[q])
            if any((s * x - y).expand() != 0 for x, y in zip(columns[k], product, strict=True)):
                return False
    return True


def automorphisms_in(table: Table, basis: list[Matrix]) -> list[Matrix]:
    """Every invertible g in span(basis) with g(xy) = g(x) g(y), from the real roots of a lex Groebner basis."""
    n = len(table)
    xs = symbols(f"x0:{len(basis)}")
    g = zeros(n, n)
    for x, b in zip(xs, basis, strict=True):
        g += x * b
    columns = [list(g[:, p]) for p in range(n)]
    equations = set()
    for p in range(n):
        for q in range(n):
            s, k = table[p][q]
            for x, y in zip(columns[k], multiply(table, columns[p], columns[q]), strict=True):
                if (e := (s * x - y).expand()) != 0:
                    equations.add(e)
    roots = solve(list(groebner(sorted(equations, key=str), *xs, order="lex")), xs, dict=True)
    if any(not value.is_real for root in roots for value in root.values()):
        raise AssertionError(f"a complex root {roots} needs a real-form argument")
    found = [g.subs(root) for root in roots]
    return [m for m in found if m.det() != 0]


def census(table: Table) -> dict:
    n = len(table)
    der = derivations(table)
    centralizer = commutant(der, n)
    return {"derivations": der, "commutant": centralizer, "automorphisms": automorphisms_in(table, centralizer)}


def run_census(name: str) -> dict:
    """The full census of the octonions or sedenions, or the derivations alone of Table 5 as printed, whose
    commutant of 32 dimensions puts the Groebner solve out of reach."""
    if name == "printed":
        return {"derivations": derivations(printed_gresnigt_table())}
    return census(cd_table({"octonion": 8, "sedenion": 16}[name]))


def octonion_diagonal(d: Matrix) -> Matrix:
    """The sedenion map A + B s_8 -> d(A) + d(B) s_8 of an octonion matrix d."""
    out = zeros(16, 16)
    out[:8, :8] = d
    out[8:, 8:] = d
    return out


def epsilon() -> Matrix:
    return Matrix.diag(*([1] * 8 + [-1] * 8))


def psi() -> Matrix:
    """Gresnigt Eq. 61: psi(A + B s_8) = (A + 3A* + sqrt 3 (B - B*))/4 + (B + 3B* - sqrt 3 (A - A*))/4 s_8."""
    out = eye(16)
    for i in range(1, 8):
        out[i, i] = out[i + 8, i + 8] = Rational(-1, 2)
        out[i + 8, i] = -sqrt(3) / 2
        out[i, i + 8] = sqrt(3) / 2
    return out


def key(m: Matrix) -> tuple:
    return tuple(x.simplify() for x in m)


def rocq_tower_signs() -> dict[tuple[int, int], tuple[int, int]]:
    """(sign, index) of e_a e_b from tower_table.txt, the Rocq vm_compute output of TowerTable.v."""
    text = (EVIDENCE / "tower_table.txt").read_text(encoding="utf-8")
    values = [int(x) for x in re.findall(r"-?\d+", text.split(":", 1)[0])]
    if len(values) != 16**3:
        raise AssertionError(f"tower_table.txt holds {len(values)} coordinates, expected 4096")
    out = {}
    for a in range(16):
        for b in range(16):
            vector = values[(a * 16 + b) * 16 : (a * 16 + b + 1) * 16]
            support = [i for i, x in enumerate(vector) if x != 0]
            if len(support) != 1 or abs(vector[support[0]]) != 1:
                raise AssertionError(f"e_{a} e_{b} is not a signed basis element in the Rocq tower: {vector}")
            out[a, b] = (vector[support[0]], support[0])
    return out


@pytest.fixture(scope="module")
def results() -> dict[str, dict]:
    names = ["octonion", "sedenion", "printed"]
    return dict(zip(names, parallel.ordered_map(run_census, names, min_items=1), strict=True))


def test_octonion_automorphisms_are_the_derivation_group_alone(results: dict[str, dict]) -> None:
    result = results["octonion"]
    if len(result["derivations"]) != 14 or len(result["commutant"]) != 2:
        raise AssertionError(f"Der(O) {len(result['derivations'])}, commutant {len(result['commutant'])}; want 14, 2")
    if [key(m) for m in result["automorphisms"]] != [key(eye(8))]:
        raise AssertionError(f"the commutant of Der(O) holds automorphisms {result['automorphisms']}")


def test_sedenion_automorphisms_are_g2_times_s3(results: dict[str, dict]) -> None:
    result = results["sedenion"]
    der = result["derivations"]
    if len(der) != 14 or len(result["commutant"]) != 8:
        raise AssertionError(f"Der(S) {len(der)}, commutant {len(result['commutant'])}; want 14, 8")
    diagonal = [octonion_diagonal(d) for d in results["octonion"]["derivations"]]
    if Matrix.hstack(*(m.reshape(256, 1) for m in der + diagonal)).rank() != 14:
        raise AssertionError("Der(S) is not the diagonal image of Der(O)")
    e, p = epsilon(), psi()
    s3 = {key(m) for m in (eye(16), p, p * p, e, e * p, e * p * p)}
    found = {key(m) for m in result["automorphisms"]}
    if len(found) != 6 or found != s3:
        raise AssertionError(f"the commutant automorphisms are not the S3 of epsilon and psi: {len(found)} found")
    if p**3 != eye(16) or e * e != eye(16) or (e * p - p * p * e).applyfunc(lambda x: x.simplify()) != zeros(16, 16):
        raise AssertionError("epsilon and psi break psi^3 = epsilon^2 = 1 or epsilon psi = psi^2 epsilon")
    for m in result["automorphisms"]:
        if m != eye(16) and m[:8, 8:] == zeros(8, 8) and m[8:, :8] == zeros(8, 8) and m[:8, :8] == m[8:, 8:]:
            raise AssertionError(f"a nontrivial S3 element lies in the diagonal G2: {m}")


def test_printed_gresnigt_table_loses_psi(results: dict[str, dict]) -> None:
    printed = printed_gresnigt_table()
    # epsilon scales e_p by a character of p, an automorphism of every table e_p e_q = +-e_(p XOR q).
    if not is_automorphism(printed, epsilon()) or is_automorphism(printed, psi()):
        raise AssertionError("Table 5 as printed keeps psi or loses epsilon")
    if (count := len(results["printed"]["derivations"])) != 4:
        raise AssertionError(f"Table 5 as printed has {count} derivations, expected 4 against cd_core's 14")


def test_rocq_tower_table_is_cd_core() -> None:
    rocq = rocq_tower_signs()
    differing = [(a, b) for a in range(16) for b in range(16) if rocq[a, b] != cd_table(16)[a][b]]
    if differing:
        raise AssertionError(f"the Rocq tower and cd_core differ at {differing}")


def test_gresnigt_erratum_cells() -> None:
    record = json.loads((EVIDENCE / "gresnigt_table5_printed.json").read_text(encoding="utf-8"))
    rocq = rocq_tower_signs()
    for cell in record["cells"]:
        i, j = cell["row"], cell["column"]
        sign, index = (-1, cell["printed"][1:]) if cell["printed"].startswith("-") else (1, cell["printed"])
        partner = -1 if cell["printed_exchanged"].startswith("-") else 1
        if int(index[1:]) != i ^ j or sign != partner or rocq[i, j] != (-sign, i ^ j):
            raise AssertionError(f"cell s_{i} s_{j}: printed {cell['printed']}, Rocq tower {rocq[i, j]}")
    if len(record["cells"]) != 11:
        raise AssertionError(f"the record lists {len(record['cells'])} cells, not 11")
