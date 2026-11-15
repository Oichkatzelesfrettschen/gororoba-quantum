"""The SL_2-module structure of the common kernel C(l_z) and the rank of M on the polar line of a nullity-4 point.

M(t) is the 15 x 15 skew matrix of the imaginary part of t k in the 16-dimensional Cayley-Dickson algebra, and
z = (e_1; mu; v_1 e_1 + rho e_2) is the normal form of the rank-12 points of V(G) minus V(Q), with the relation
mu^2 + v_1^2 + (rho - sigma)^2 = 0, sigma = +-1, and rho nonzero (Q(z) = 2 sigma rho; see
`nullity4_orbit_normal_forms.py`). FIXED = (1, 2, 3, 8, 9, 10, 11) are the coordinates of the imaginary part
of the octonion subalgebra O', COMPLEMENT = (4, 5, 6, 7, 12, 13, 14, 15) the other eight, and l_z is the kernel of the
COMPLEMENT block of M(z). C(l_z) is the common kernel of M(p) over p in l_z. The reduction of an arbitrary point of
the stratum to the normal form is the prose argument of the module above; this producer replays nothing of it.

The mechanism, with x = (s, v_1, mu), s = rho - sigma, and the cone s^2 + v_1^2 + mu^2 = 0 that the relation defines:

1. The three derivations D_1, D_2, D_3 of the octonions that annihilate e_1 and e_2 act on (u, v) diagonally. They are
   skew, vanish on FIXED and satisfy M(D t) = D M(t) + M(t) D^T. On COMPLEMENT they satisfy D_i^2 = -1 and D_1 D_2 =
   D_3 cyclically, so COMPLEMENT is a module of the quaternion algebra over C, which is the matrix algebra of order two:
   four copies of its two-dimensional module, the standard representation of SL_2.
2. For p in COMPLEMENT the FIXED and COMPLEMENT diagonal blocks of M(p) vanish, so M(p)(a, b) = (B(p) b, -B(p)^T a)
   with B(p) the 7 x 8 block from COMPLEMENT to FIXED. Hence rank M(p) = 2 rank B(p) and the kernel of M(p) is
   ker B(p) in COMPLEMENT plus ker B(p)^T in FIXED. The equivariance of item 1 gives B(D_k p) = -B(p) D_k.
3. z lies in FIXED, so D_k commutes with the COMPLEMENT block of M(z) and l_z is stable under the D_k. A submodule of
   dimension two of four standard modules is standard, so l_z is irreducible and each q in l_z is A p for an element
   A of the algebra spanned by 1, D_1, D_2, D_3, for every nonzero p in l_z. By item 2, B(A p) is B(p) times a
   matrix, so the image of B(q) lies in the image of B(p), and the two images agree for nonzero p and q. Therefore
   rank B is constant on l_z minus 0, the FIXED part of C(l_z) is the orthogonal complement of that image, of
   dimension 7 - r, and the COMPLEMENT part is the common kernel of B(p), B(p) D_1, B(p) D_2 and B(p) D_3.
4. The Pfaffian adjoint Omega of the COMPLEMENT block of M(z) has the column -2 rho p_sigma(x) with p_1(x) = (s, 0,
   mu, v_1, v_1, -mu, 0, -s) and p_{-1}(x) = (s, 0, mu, v_1, -v_1, mu, 0, s), and M_C(z) p_sigma(x) = 0 modulo the
   relation. The vector p_sigma(x) vanishes only at x = 0, the rank-10 point (v_1, mu, rho) = (0, 0, sigma); anywhere
   else Omega is nonzero, so the COMPLEMENT block has rank 6, rank M(z) = 12 and p_sigma(x) is a nonzero vector of l_z.
   The matrix B(p_sigma(x)) is linear in x.

The certificates are polynomial identities in the ring of x modulo the cone, and unit ideals (Groebner bases that
equal (1)) with the slack variable w for the saturation by the excluded locus:

- the 5 x 5 minors of B vanish modulo the cone, so r is at most 4 at every point;
- off mu = 0, the 4 x 4 minors with the cone and 1 - w mu equal (1): r = 4; and the 8 x 8 minors of the 14 x 8 stack
  of B and B D_1 do too: the COMPLEMENT part of C(l_z) is 0, so dim C(l_z) = 3, all in FIXED;
- on mu = 0 the 4 x 4 minors vanish modulo the cone and mu, and the 3 x 3 minors with the cone, mu and 1 - w s, or
  1 - w v_1 (the excluded locus x = 0 is s = v_1 = 0), equal (1): r = 3;
- on mu = 0 the cone is the pair of lines s = +-i v_1, where B is v_1 times a constant matrix over Q(i), and so are
  the vectors p, D_k p of l_z. The rank of the stack of B, B D_1, B D_2, B D_3, the dimension of the common kernel of
  M(q), q in {p, D_k p}, its FIXED part and its stability under the D_k are exact linear algebra over Q(i).

Calibration: the same ideals with 5 x 5 minors off mu = 0, with 4 x 4 minors on mu = 0, and with the 3 x 3 minors
unsaturated are proper ideals, and a flipped sign in the vector p_sigma or in D_1 breaks an identity (the tests).

The retained record of `nullity4_orbit_normal_forms.py` (modulo 32029: 60 + 60 normal-form points and 52
fixtures) is read, not recomputed, and compared with the ranks and dimensions derived here.

`--write` writes nullity4-polar-line-module-result.json beside this file; `--check` recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_polar_line_module.py --check
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.polys.matrices import DomainMatrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import nullity4_orbit_normal_forms as forms  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-polar-line-module-v1"
RECORD = HERE / "nullity4-polar-line-module-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_polar_line_module.py",
    HERE / "nullity4_orbit_normal_forms.py",
    forms.RECORD,
    HERE / "nullity4_gauss_image.py",
)
FIELD = "Q for the identities and unit ideals; Q(i) for the constant matrices on mu = 0; retained tallies modulo 32029"
FIXED = forms.FIXED
COMPLEMENT = forms.COMPLEMENT
SIGMAS = (1, -1)
IDENTITIES = (
    "derivations_are_equivariant",
    "complement_is_four_copies_of_the_standard_module",
    "complement_vectors_swap_fixed_and_complement",
    "polar_line_is_a_submodule",
    "complement_blocks_intertwine",
    "omega_column_is_the_polar_vector",
    "polar_vector_is_in_the_kernel",
)
# Entries (row, column, value) of the 7 x 7 matrices of the derivations of the octonions that annihilate e_1 and e_2.
DERIVATION_ENTRIES = (
    ((3, 6, -1), (4, 5, -1), (5, 4, 1), (6, 3, 1)),
    ((3, 5, 1), (4, 6, -1), (5, 3, -1), (6, 4, 1)),
    ((3, 4, -1), (4, 3, 1), (5, 6, -1), (6, 5, 1)),
)
S_VAR = sp.Symbol("s")
SLACK = sp.Symbol("w")
V1, MU, RHO = forms.V1, forms.MU, forms.RHO
CONE = S_VAR**2 + V1**2 + MU**2
VECTORS = {
    1: [S_VAR, 0, MU, V1, V1, -MU, 0, -S_VAR],
    -1: [S_VAR, 0, MU, V1, -V1, MU, 0, S_VAR],
}
# The record of one sigma: the count of nonzero 5 x 5 minors, of nonzero 4 x 4 minors on mu = 0, the unit ideals of
# 4 x 4 minors and of the stack off mu = 0, the two unit ideals of 3 x 3 minors on mu = 0, the three calibration
# ideals, and per line s = +-i v_1 on mu = 0 (rank B, rank of the stack of B D_k, dim C(l_z), its FIXED part, its
# stability under the D_k, ranks of M(p) at two vectors of l_z).
CERTIFICATE: dict[str, Any] = {
    "rank_5_minors_nonzero": 0,
    "rank_4_minors_nonzero_on_mu_zero": 0,
    "rank_4_unit_off_mu_zero": True,
    "stack_unit_off_mu_zero": True,
    "rank_3_unit_on_mu_zero": [True, True],
    "calibration_units": [False, False, False],
    "mu_zero_lines": [[3, 6, 6, 4, True, [6, 6]], [3, 6, 6, 4, True, [6, 6]]],
}
CLAIMS = {
    "mu nonzero": {
        "rank_of_B": 4,
        "rank_of_M_on_polar_line": 8,
        "nullity_of_M_on_polar_line": 7,
        "dim_C": 3,
        "dim_C_in_O_prime": 3,
        "dim_C_in_complement": 0,
    },
    "mu zero": {
        "rank_of_B": 3,
        "rank_of_M_on_polar_line": 6,
        "nullity_of_M_on_polar_line": 9,
        "dim_C": 6,
        "dim_C_in_O_prime": 4,
        "dim_C_in_complement": 2,
    },
}
# Normal-form samples and fixtures of the retained record that agree with the derived ranks and dimensions.
RETAINED = {"samples": 120, "fixtures": 52}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _zero(expressions: Any, relation: Any, variable: Any) -> bool:
    return all(sp.rem(sp.expand(expression), relation, variable) == 0 for expression in expressions)


def derivations() -> list[sp.Matrix]:
    """D_1, D_2, D_3 as 15 x 15 matrices acting diagonally on (u, v)."""
    matrices = []
    for entries in DERIVATION_ENTRIES:
        matrix = sp.zeros(15, 15)
        for row, column, value in entries:
            matrix[row, column] = matrix[8 + row, 8 + column] = value
        matrices.append(matrix)
    return matrices


def _restrict(matrix: sp.Matrix) -> sp.Matrix:
    index = [unit - 1 for unit in COMPLEMENT]
    return matrix.extract(index, index)


def _complement_vector(entries: Sequence[Any]) -> list[Any]:
    vector: list[Any] = [sp.Integer(0)] * 15
    for unit, entry in zip(COMPLEMENT, entries, strict=True):
        vector[unit - 1] = entry
    return vector


def _b(entries: Sequence[Any]) -> sp.Matrix:
    """B(p): the 7 x 8 block of M(p) from COMPLEMENT to FIXED for p given by its eight COMPLEMENT entries."""
    return forms.block(_complement_vector(entries), FIXED, COMPLEMENT)


def _all_zero(matrix: sp.Matrix) -> bool:
    return all(sp.expand(entry) == 0 for entry in matrix)


def derivations_are_equivariant() -> bool:
    t = sp.Matrix(sp.symbols("t1:16"))
    for matrix in derivations():
        moved = forms.block(list(matrix * t), forms.ALL, forms.ALL)
        if not _all_zero(
            moved
            - matrix * forms.block(list(t), forms.ALL, forms.ALL)
            - forms.block(list(t), forms.ALL, forms.ALL) * matrix.T
        ):
            return False
        if not _all_zero(matrix + matrix.T) or any(matrix[:, unit - 1] != sp.zeros(15, 1) for unit in FIXED):
            return False
    return True


def complement_is_four_copies_of_the_standard_module() -> bool:
    d1, d2, d3 = (_restrict(matrix) for matrix in derivations())
    identity = sp.eye(8)
    return (
        all(matrix * matrix == -identity for matrix in (d1, d2, d3))
        and d1 * d2 == d3
        and d2 * d3 == d1
        and d3 * d1 == d2
    )


def complement_vectors_swap_fixed_and_complement() -> bool:
    vector = _complement_vector(sp.symbols("p1:9"))
    return _all_zero(forms.block(vector, FIXED, FIXED)) and _all_zero(forms.block(vector, COMPLEMENT, COMPLEMENT))


def polar_line_is_a_submodule() -> bool:
    _, vector = forms._general_fixed()
    block = forms.block(vector, COMPLEMENT, COMPLEMENT)
    return all(_all_zero(_restrict(matrix) * block - block * _restrict(matrix)) for matrix in derivations())


def complement_blocks_intertwine() -> bool:
    entries = sp.Matrix(sp.symbols("p1:9"))
    for matrix in derivations():
        restricted = _restrict(matrix)
        if not _all_zero(_b(list(restricted * entries)) + _b(list(entries)) * restricted):
            return False
    return True


def _at_rho(vector: Sequence[Any], sigma: int) -> list[Any]:
    return [sp.expand(entry.subs(S_VAR, RHO - sigma)) if isinstance(entry, sp.Basic) else entry for entry in vector]


def _normal_form_block() -> sp.Matrix:
    return forms.block(forms.frame([1, 0, 0], MU, [V1, RHO, 0]), COMPLEMENT, COMPLEMENT)


def omega_column_is_the_polar_vector() -> bool:
    adjoint = forms.pfaffian_adjoint(_normal_form_block())
    for sigma in SIGMAS:
        relation = forms._quartic_relation(sigma)
        vector = _at_rho(VECTORS[sigma], sigma)
        if not _zero([adjoint[row, 1] + 2 * RHO * vector[row] for row in range(8)], relation, MU):
            return False
    return True


def polar_vector_is_in_the_kernel() -> bool:
    block = _normal_form_block()
    return all(
        _zero(list(block * sp.Matrix(_at_rho(VECTORS[sigma], sigma))), forms._quartic_relation(sigma), MU)
        for sigma in SIGMAS
    )


CHECKS = {
    "derivations_are_equivariant": derivations_are_equivariant,
    "complement_is_four_copies_of_the_standard_module": complement_is_four_copies_of_the_standard_module,
    "complement_vectors_swap_fixed_and_complement": complement_vectors_swap_fixed_and_complement,
    "polar_line_is_a_submodule": polar_line_is_a_submodule,
    "complement_blocks_intertwine": complement_blocks_intertwine,
    "omega_column_is_the_polar_vector": omega_column_is_the_polar_vector,
    "polar_vector_is_in_the_kernel": polar_vector_is_in_the_kernel,
}


def identity(name: str) -> bool:
    return CHECKS[name]()


def minors(matrix: sp.Matrix, size: int) -> list[Any]:
    """The distinct nonzero size x size minors of a matrix over Q[s, v_1, mu], reduced modulo the cone in mu."""
    domain = sp.ZZ[S_VAR, V1, MU]
    ring = DomainMatrix.from_Matrix(matrix).convert_to(domain)
    found = set()
    for rows in itertools.combinations(range(matrix.rows), size):
        for columns in itertools.combinations(range(matrix.cols), size):
            determinant = ring.extract(list(rows), list(columns)).det()
            reduced = sp.expand(sp.rem(sp.expand(domain.to_sympy(determinant)), CONE, MU))
            if reduced != 0:
                found.add(reduced)
    return sorted(found, key=str)


def _is_unit(generators: Sequence[Any], variables: Sequence[Any]) -> bool:
    return list(sp.groebner(list(generators), *variables, order="grevlex").exprs) == [1]


def _ranks_over_gaussian(matrix: sp.Matrix) -> int:
    return int(DomainMatrix.from_Matrix(matrix.applyfunc(sp.expand)).convert_to(sp.QQ_I).rank())


def mu_zero_line(job: tuple[int, int]) -> list[Any]:
    """On the line s = sign i v_1 of mu = 0 at v_1 = 1: rank B, rank of the stack of B D_k, C(l_z) and its stability."""
    sigma, sign = job
    values = {S_VAR: sign * sp.I, V1: 1, MU: 0}
    entries = [sp.expand(entry.subs(values)) if isinstance(entry, sp.Basic) else entry for entry in VECTORS[sigma]]
    _require(sp.expand(CONE.subs(values)) == 0, "the line leaves the cone")
    matrices = derivations()
    restricted = [_restrict(matrix) for matrix in matrices]
    base = sp.Matrix(entries)
    b = _b(entries)
    stack = b.col_join(b * restricted[0]).col_join(b * restricted[1]).col_join(b * restricted[2])
    vectors = [list(base)] + [list(matrix * base) for matrix in restricted]
    rows = sp.Matrix(
        [row for vector in vectors for row in forms.block(_complement_vector(vector), forms.ALL, forms.ALL).tolist()]
    )
    domain = sp.QQ_I
    ring = DomainMatrix.from_Matrix(rows.applyfunc(sp.expand)).convert_to(domain)
    kernel = ring.nullspace()
    dimension = kernel.shape[0]
    fixed_columns = [unit - 1 for unit in FIXED]
    fixed = len(fixed_columns) - _ranks_over_gaussian(rows.extract(list(range(rows.rows)), fixed_columns))
    stable = True
    for matrix in matrices:
        moved = ring * DomainMatrix.from_Matrix(matrix * sp.Matrix(kernel.to_Matrix().T)).convert_to(domain)
        stable = stable and moved.is_zero_matrix
    generic = sp.Matrix([base[index] + (restricted[1] * base)[index] for index in range(8)])
    ranks = [
        _ranks_over_gaussian(forms.block(_complement_vector(list(vector)), forms.ALL, forms.ALL))
        for vector in (base, generic)
    ]
    return [_ranks_over_gaussian(b), _ranks_over_gaussian(stack), dimension, fixed, bool(stable), ranks]


def certificate(sigma: int) -> dict[str, Any]:
    """The minor identities and unit ideals of one sign sigma."""
    b = _b(VECTORS[sigma])
    restricted = _restrict(derivations()[0])
    five = minors(b, 5)
    four = minors(b, 4)
    three = minors(b, 3)
    stack = minors(b.col_join(b * restricted), 8)
    four_on_zero = [sp.expand(sp.rem(sp.expand(m.subs(MU, 0)), S_VAR**2 + V1**2, V1)) for m in four]
    three_on_zero = [sp.expand(m.subs(MU, 0)) for m in three]
    line = S_VAR**2 + V1**2
    units = [
        _is_unit([*four_on_zero, line, 1 - SLACK * S_VAR], (SLACK, V1, S_VAR)),
        _is_unit([*five, CONE, 1 - SLACK * MU], (SLACK, MU, V1, S_VAR)),
        _is_unit([*three_on_zero, line], (V1, S_VAR)),
    ]
    return {
        "rank_5_minors_nonzero": len(five),
        "rank_4_minors_nonzero_on_mu_zero": sum(1 for m in four_on_zero if m != 0),
        "rank_4_unit_off_mu_zero": _is_unit([*four, CONE, 1 - SLACK * MU], (SLACK, MU, V1, S_VAR)),
        "stack_unit_off_mu_zero": _is_unit([*stack, CONE, 1 - SLACK * MU], (SLACK, MU, V1, S_VAR)),
        "rank_3_unit_on_mu_zero": [
            _is_unit([*three_on_zero, line, 1 - SLACK * variable], (SLACK, V1, S_VAR)) for variable in (S_VAR, V1)
        ],
        "calibration_units": units,
        "mu_zero_lines": [mu_zero_line((sigma, sign)) for sign in (1, -1)],
    }


def retained_agreement() -> dict[str, int]:
    """The normal-form samples and fixtures of the retained record whose rank, dimension and FIXED part match."""
    retained = json.loads(forms.RECORD.read_text(encoding="utf-8"))
    derived = {False: (8, 3, 3), True: (6, 6, 4)}
    samples = 0
    for rows in retained["samples"].values():
        for row in rows:
            samples += row[-1] * ((row[1], row[2], row[3]) == derived[bool(row[0])])
    fixtures = 0
    for row in retained["fixtures"]:
        fixtures += row[-1] * ((row[1], row[2]) == derived[bool(row[0])][:2])
    return {"samples": samples, "fixtures": fixtures}


def derived_claims(certificates: dict[str, dict[str, Any]]) -> dict[str, dict[str, int | None]]:
    """The ranks and dimensions that the certificates of both signs give; None where a certificate fails.

    With r = rank B on l_z minus 0: rank M = 2 r, nullity of M = 15 - 2 r, dim C(l_z) = (7 - r) + 2 (4 - r) with 7 - r
    in FIXED, the kernel of M(p) pairing FIXED and COMPLEMENT as in item 2. Off mu = 0 the stack unit ideal gives the
    COMPLEMENT part 0, and on mu = 0 the constant matrices give it.
    """
    values = list(certificates.values())
    upper = all(c["rank_5_minors_nonzero"] == 0 for c in values)
    off_zero = upper and all(c["rank_4_unit_off_mu_zero"] and c["stack_unit_off_mu_zero"] for c in values)
    on_zero = all(c["rank_4_minors_nonzero_on_mu_zero"] == 0 and all(c["rank_3_unit_on_mu_zero"]) for c in values)
    lines = [line for c in values for line in c["mu_zero_lines"]]
    claims: dict[str, dict[str, int | None]] = {}
    for label, rank, certified in (("mu nonzero", 4, off_zero), ("mu zero", 3, on_zero)):
        known = rank if certified else None
        claims[label] = {
            "rank_of_B": known,
            "rank_of_M_on_polar_line": None if known is None else 2 * known,
            "nullity_of_M_on_polar_line": None if known is None else 15 - 2 * known,
            "dim_C": None,
            "dim_C_in_O_prime": None if known is None else 7 - known,
            "dim_C_in_complement": None,
        }
    if off_zero:
        claims["mu nonzero"]["dim_C_in_complement"] = 0
        claims["mu nonzero"]["dim_C"] = 3
    if on_zero and len({(line[2], line[3]) for line in lines}) == 1:
        total, fixed = lines[0][2], lines[0][3]
        claims["mu zero"]["dim_C"] = total
        claims["mu zero"]["dim_C_in_complement"] = total - fixed
    return claims


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    names = list(IDENTITIES)
    identities = dict(zip(names, parallel.ordered_map(identity, names, min_items=2), strict=True))
    certificates = parallel.ordered_map(certificate, list(SIGMAS), min_items=2)
    by_sign = {"sigma = 1": certificates[0], "sigma = -1": certificates[1]}
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": identities,
        "certificates": by_sign,
        "claims": derived_claims(by_sign),
        "retained_agreement": retained_agreement(),
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    return {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "identities": dict.fromkeys(IDENTITIES, True),
        "certificates": {
            "sigma = 1": copy.deepcopy(CERTIFICATE),
            "sigma = -1": copy.deepcopy(CERTIFICATE),
        },
        "claims": copy.deepcopy(CLAIMS),
        "retained_agreement": dict(RETAINED),
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "identities": "an exact identity fails",
        "certificates": "a minor identity or unit ideal of the polar line fails, or a calibration ideal is a unit",
        "claims": "the ranks and dimensions on the polar line differ from the claims",
        "retained_agreement": "the retained modular samples or fixtures disagree with the derived ranks",
    }
    for group, message in messages.items():
        if json.dumps(record.get(group), sort_keys=True) != json.dumps(expected[group], sort_keys=True):
            problems.append(message)
    if record.get("pass") is not True:
        problems.append("the record states that it fails")
    if not problems and _serialized(record) != _serialized(expected):
        problems.append("the record differs from the record the constants determine")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    """The retained text of a record. The replay compares text, so true and 1, which compare equal, differ."""
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def main() -> None:
    """Write the record with --write, or recompute and compare its text with --check."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(_serialized(record), encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != _serialized(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    retained = sum(record["retained_agreement"].values())
    print(f"pass: {len(record['identities'])} identities, 2 signs, {retained} retained points")


if __name__ == "__main__":
    main()
