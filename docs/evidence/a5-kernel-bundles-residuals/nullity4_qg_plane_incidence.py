"""Real points of V(Q) n V(G) with an exceptional kernel plane: a line in each fiber, none for P_y, P_z at s = +-1.

Setting. M(t), K(z) = ker M(z), the cone J, the planes P_x, P_y, P_z of J, the kernel plane P = K n conj(z)-perp and
dim L = 2 (dim C(P) - 2) are those of nullity4_qg_intersection.py (qg) and nullity4_qg_orbit_types.py (ot). <a, b>
is the Hermitian form sum a_i conj(b_i). S is the set of nullity-4 points of V(Q) n V(G) (rank M = 12).

1. Incidence (argument). A point z of S lies in K(z), every vector of K(z) outside J has kernel K(z) (qg item 6), and
   J is closed, so S is the disjoint union over the kernels K of the open sets K minus J of the three-dimensional
   spaces K. The planes P_j depend on K alone. For z in K minus J the kernel plane is the Hermitian complement of z
   in K, so P(z) = P_j exactly when z lies on the complex line of K Hermitian-orthogonal to P_j: the map
   k -> (<k, p_1>, <k, p_2>) from K to C^2, p_1, p_2 a basis of P_j, is complex-linear and onto, because the form
   is positive definite on K. Hence inside each fiber K minus J (real dimension 6) the points with kernel plane
   P_j form a complex line minus the points of J. A line of K that is not inside one of the three planes of J
   meets J at 0 alone, so the set is the punctured line (real dimension 2, real codimension 4 in the fiber) or it
   is empty, when the line lies in J: always at s = +-1 (A5-555 and item 3), and elsewhere over the kernels g K
   whose Hermitian form puts the line of P_y or P_z inside g P_x. With A5-557
   the set {dim L = 6} is the set P = P_x (s^2 other than 1) and the set {dim L = 4} is the set P = P_y or P_z
   away from the roots of D1 D2. The fiberwise statement does not give the dimension of these sets in S: that needs
   the dimension of the set of kernels over which the line leaves J. Item 2 gives the local answer at six points.
   hypothesis: both sets have real dimension dim S - 4 = 22; missing lemma: the map z -> K(z) has an image of real
   dimension 20 (a Pluecker differential of rank 10) over which the exceptional lines form line bundles.
2. Incidence (exact check at the six witnesses of qg, s = 2 and 0, planes x, y, z). The local parametrization
   (g, s, c) -> g (c_0 k_0(s) + c_1 k_1(s) + c_2 k_2(s)) of S has the tangent vectors D_k z (14 derivations),
   sum c_a dk_a/ds and k_0, k_1, k_2. They span 13 dimensions, lie in ker dQ n ker dDelta, and dQ, dDelta have
   rank 2 at the witness, so the span is the tangent space of V(Q) n V(Delta) there. F(z) = (<z, p_1>, <z, p_2>)
   with (p_1, p_2) = g (plane vectors of P_j at s) vanishes at the witness, and its real Jacobian (4 rows; the
   columns are the real directions D_k z, i D_k z, d/ds, i d/ds, k_a, i k_a) has rank 4; the six fiber columns
   alone have rank 4, the columns of the compact directions D_k z vanish (the form is invariant under the compact
   G_2), and the columns i D_k z alone have rank 4. The rank at a zero of F does not depend on the frame of P_j. So
   near each witness the points with kernel plane P_j form a real submanifold of codimension 4 in S.
3. The planes P_y and P_z at s = +-1 (argument). K = P_x + C q with P_x in E_eps and q in E_(-eps), q lies in
   P_y and in P_z, and E_+ and E_- are Hermitian-orthogonal and preserved by G_2(C) (ot item 1). For g in G_2(C),
   g P_y contains g q and the line g (P_y n P_x) of g P_x, so g P_y = C g q + g (P_y n P_x), an orthogonal sum. A
   vector w of g K orthogonal to g P_y is orthogonal to g q; since g K = g P_x + C g q is an orthogonal sum, w lies
   in g P_x, a plane of g J. A real point z' with K(z') = g K and kernel plane g P_y would lie on C w, so it would
   lie in J and have nullity above 3. The same holds for P_z. Hence no real point of the type s = +-1 has the
   kernel plane P_y or P_z; with A5-555 (no P_x) every real point of the type has dim C(P) = 3 and dim L = 2.
4. The planes at s = +-1 (exact checks). At the base frames and at the image under the unipotent element
   g = exp(X), X = D_a + i D_b nilpotent of order 3 (equivariant, not unitary, <g k_1, g k_2> nonzero), the
   Hermitian complement in g K of each plane g P_x, g P_y, g P_z: for P_y and P_z it lies in g P_x and has nullity 9
   (at the base frame, where k_1 and k_2 are orthogonal, it is the line P_x n P_z or P_x n P_y; at the unipotent
   frame it lies in g P_x alone); for P_x it is C g q, of nullity 7, inside g P_y and g P_z. Control: the
   complement of a plane of K outside J has nullity 3. At s = 2 the complements of P_y and P_z lie outside P_x and
   have nullity 3 (the witnesses of qg).

Evidence. Every number is exact over Q(i); no scan modulo a prime and no floating point enters the record.

--write writes nullity4-qg-plane-incidence-result.json beside this file; --check recomputes and compares.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_plane_incidence.py --check
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(HERE))

import nullity4_orbit_normal_forms as forms  # noqa: E402
import nullity4_qg_intersection as qg  # noqa: E402
import nullity4_qg_orbit_types as ot  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-nullity4-qg-plane-incidence-v1"
RECORD = HERE / "nullity4-qg-plane-incidence-result.json"
SOURCE_PATHS = (
    HERE / "nullity4_qg_plane_incidence.py",
    HERE / "nullity4_qg_intersection.py",
    HERE / "nullity4_qg_orbit_types.py",
    HERE / "nullity4_orbit_normal_forms.py",
)
FIELD = "Q(i) for every vector, rank and Jacobian"
IU = sp.I
Vector = list[Any]

WITNESS_JOBS = tuple((s, plane) for s in qg.WITNESS_S for plane in "xyz")
# F vanishes; rank M; tangent span; orbit span; rank of (dQ, dDelta); tangent in ker dQ n ker dDelta; compact columns
# vanish; rank of the real Jacobian; rank of its fiber columns; rank of its columns i D_k z.
INCIDENCE_ROW = [True, 12, 13, 11, 2, True, True, 4, 4, 4]
INCIDENCE = {f"s = {s}, {plane}": list(INCIDENCE_ROW) for s, plane in WITNESS_JOBS}

# X = D_a + sign i D_b: the indices into ot.derivation_matrices() and the sign.
UNIPOTENT = (0, 9, 1)
UNIPOTENT_FACTS = {"order": 3, "equivariant": True, "unitary": False}
ELEMENTS = ("identity", "unipotent")
# Per plane: nullity of the Hermitian complement in g K, and whether it lies in g P_x, g P_y, g P_z; then the
# nullity of the complement of the control plane outside J and whether <g k_1, g k_2> is nonzero.
# At the base frame k_1 and k_2 are orthogonal, so the complement of P_y is C k_1, which also lies in P_z; the
# unipotent frame is not orthogonal and the complement lies in g P_x alone.
_FRAMES: dict[str, dict[str, Any]] = {
    "identity": {
        "x": [7, False, True, True],
        "y": [9, True, False, True],
        "z": [9, True, True, False],
        "control": 3,
        "frame_not_orthogonal": False,
    },
    "unipotent": {
        "x": [7, False, True, True],
        "y": [9, True, False, False],
        "z": [9, True, False, False],
        "control": 3,
        "frame_not_orthogonal": True,
    },
}
COMPLEMENTS = {f"s = {s}, {element}": copy.deepcopy(_FRAMES[element]) for s in (1, -1) for element in ELEMENTS}
# At s = 2: the nullity of the complement of P_y and of P_z in K and whether it lies in P_x.
GENERIC_COMPLEMENTS = {"y": [3, False], "z": [3, False]}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _apply(matrix: sp.Matrix, vector: Sequence[Any]) -> Vector:
    return [sp.expand(entry) for entry in matrix * sp.Matrix(list(vector))]


def _times_i(vector: Sequence[Any]) -> Vector:
    return [sp.expand(IU * entry) for entry in vector]


def _at(vector: Sequence[Any], s: int) -> Vector:
    return [sp.expand(sp.sympify(entry).subs(qg.S, s)) for entry in vector]


def _derivative_at(vector: Sequence[Any], s: int) -> Vector:
    return [sp.expand(sp.diff(sp.sympify(entry), qg.S).subs(qg.S, s)) for entry in vector]


def _gradients(z: Sequence[Any]) -> tuple[Vector, Vector]:
    """dQ and dDelta at the frame vector z = (u; mu; v)."""
    u, mu, v = list(z[:7]), z[7], list(z[8:])
    uu, vv = sum(a * a for a in u), sum(a * a for a in v)
    uv = sum(a * b for a, b in zip(u, v, strict=True))
    d_q = [2 * a for a in u] + [2 * mu] + [2 * a for a in v]
    d_delta = [2 * a * vv - 2 * uv * b for a, b in zip(u, v, strict=True)]
    d_delta += [0] + [2 * b * uu - 2 * uv * a for a, b in zip(u, v, strict=True)]
    return [sp.expand(e) for e in d_q], [sp.expand(e) for e in d_delta]


def _real_rank(columns: Sequence[Sequence[Any]]) -> int:
    """The rank over Q of the real 4 x n matrix whose columns are (Re F_1, Im F_1, Re F_2, Im F_2)."""
    rows = [[part(column[index]) for column in columns] for index in (0, 1) for part in (sp.re, sp.im)]
    return int(sp.Matrix(rows).rank())


@functools.cache
def _witness_data(s: int, plane: str) -> tuple[Vector, list[Vector], list[Any], list[Vector], list[Vector], Vector]:
    """The witness z, the kernel basis, the coefficients of z, the frame of the plane, its s-derivative and dz/ds."""
    z = [sp.expand(entry) for entry in qg.witness_point(sp.Integer(s), plane)]
    kernel = [_at(k, s) for k in qg.kernel_vectors(qg.S)]
    solution = sp.Matrix(kernel).T.gauss_jordan_solve(sp.Matrix(z))[0]
    coefficients = [sp.nsimplify(entry) for entry in solution]
    _require(qg._combination(coefficients, kernel) == z, "the witness is not in K")
    symbolic = qg.plane_vectors(qg.S)[plane]
    frame = [_at(p, s) for p in symbolic]
    frame_ds = [_derivative_at(p, s) for p in symbolic]
    z_ds = qg._combination(coefficients, [_derivative_at(k, s) for k in qg.kernel_vectors(qg.S)])
    return z, kernel, coefficients, frame, frame_ds, z_ds


def derivation_columns(job: tuple[int, str, int]) -> tuple[Vector, list[Any], list[Any]]:
    """D_k z and the columns of dF along D_k z and along i D_k z at the witness of the job (s, plane, k)."""
    s, plane, index = job
    z, _, _, frame, _, _ = _witness_data(s, plane)
    matrix = ot.derivation_matrices()[index]
    moved = _apply(matrix, z)
    moved_frame = [_apply(matrix, p) for p in frame]
    pairs = list(zip(frame, moved_frame, strict=True))
    compact = [qg._hermitian(moved, p) + qg._hermitian(z, q) for p, q in pairs]
    noncompact = [qg._hermitian(_times_i(moved), p) + qg._hermitian(z, _times_i(q)) for p, q in pairs]
    return moved, compact, noncompact


def incidence_facts(job: tuple[int, str]) -> list[Any]:
    """The facts of item 2 at the witness of the plane at the rational s, in the order of INCIDENCE_ROW."""
    s, plane = job
    z, kernel, _, frame, frame_ds, z_ds = _witness_data(s, plane)
    value = [qg._hermitian(z, p) for p in frame]
    count = len(ot.derivation_matrices())
    moved = parallel.ordered_map(derivation_columns, [(s, plane, index) for index in range(count)], min_items=2)
    tangent = [row[0] for row in moved]
    compact = [row[1] for row in moved]
    noncompact = [row[2] for row in moved]
    pairs = list(zip(frame, frame_ds, strict=True))
    chart = [
        [qg._hermitian(z_ds, p) + qg._hermitian(z, dp) for p, dp in pairs],
        [qg._hermitian(_times_i(z_ds), p) + qg._hermitian(z, _times_i(dp)) for p, dp in pairs],
    ]
    fiber = [[qg._hermitian(scaled, p) for p in frame] for k in kernel for scaled in (k, _times_i(k))]
    gradients = _gradients(z)
    directions = [*tangent, z_ds, *kernel]
    inside = all(sp.expand(sum(a * b for a, b in zip(g, t, strict=True))) == 0 for g in gradients for t in directions)
    return [
        all(entry == 0 for entry in value),
        qg._rank(qg.msym(z).tolist()),
        qg._rank(directions),
        qg._rank(tangent),
        qg._rank(list(gradients)),
        inside,
        all(entry == 0 for column in compact for entry in column),
        _real_rank([*compact, *noncompact, *chart, *fiber]),
        _real_rank(fiber),
        _real_rank(noncompact),
    ]


def incidence_record() -> dict[str, list[Any]]:
    rows = parallel.ordered_map(incidence_facts, list(WITNESS_JOBS), min_items=2)
    return {f"s = {s}, {plane}": row for (s, plane), row in zip(WITNESS_JOBS, rows, strict=True)}


@functools.cache
def unipotent_element() -> tuple[sp.Matrix, int]:
    """g = exp(X) for the nilpotent X = D_a + sign i D_b of UNIPOTENT, and the order of nilpotency of X."""
    a, b, sign = UNIPOTENT
    matrices = ot.derivation_matrices()
    x = matrices[a] + sign * IU * matrices[b]
    power, order, g = x, 1, sp.eye(15) + x
    while order < 15 and any(power):
        power = (power * x).applyfunc(sp.expand)
        order += 1
        g += power / sp.factorial(order)
    _require(not any(power), "X is not nilpotent")
    return g.applyfunc(sp.expand), order


def unipotent_facts() -> dict[str, Any]:
    """The order of X, M(g t) = g M(t) g^T on the generic frame vector, and whether g^* g = 1."""
    g, order = unipotent_element()
    t = sp.Matrix(sp.symbols("t1:16"))
    moved = forms.block(list(g * t), forms.ALL, forms.ALL)
    difference = (moved - g * forms.block(list(t), forms.ALL, forms.ALL) * g.T).applyfunc(sp.expand)
    return {
        "order": order,
        "equivariant": not any(difference),
        "unitary": not any((g.H * g - sp.eye(15)).applyfunc(sp.expand)),
    }


def _element(name: str) -> sp.Matrix:
    _require(name in ELEMENTS, f"unknown element {name}")
    return sp.eye(15) if name == "identity" else unipotent_element()[0]


def _complement(kernel: Sequence[Vector], plane: Sequence[Vector]) -> Vector:
    """The vector of span(kernel) Hermitian-orthogonal to the plane, a plane of span(kernel)."""
    solution = qg._nullspace([[qg._hermitian(k, p) for k in kernel] for p in plane])
    _require(len(solution) == 1, "the Hermitian complement of the plane in K is not a line")
    return qg._combination(solution[0], kernel)


COMPLEMENT_KEYS = ("x", "y", "z", "control", "frame_not_orthogonal")


def complement_fact(job: tuple[int, str, str]) -> Any:
    """One fact of item 4 for the kernel g K(z(s)): the job is (s, element, key), key one of COMPLEMENT_KEYS."""
    s, name, key = job
    _require(key in COMPLEMENT_KEYS, f"unknown fact {key}")
    g = _element(name)
    kernel = [_apply(g, k) for k in qg.kernel_vectors(sp.Integer(s))]
    if key == "frame_not_orthogonal":
        return qg._hermitian(kernel[1], kernel[2]) != 0
    if key == "control":
        outside = [
            [a + b for a, b in zip(kernel[0], kernel[1], strict=True)],
            [a + 2 * b for a, b in zip(kernel[0], kernel[2], strict=True)],
        ]
        return 15 - qg._rank(qg.msym(_complement(kernel, outside)).tolist())
    planes = {other: [_apply(g, p) for p in plane] for other, plane in qg.plane_vectors(sp.Integer(s)).items()}
    w = _complement(kernel, planes[key])
    return [15 - qg._rank(qg.msym(w).tolist()), *[qg._rank([*planes[other], w]) == 2 for other in "xyz"]]


def complement_facts(job: tuple[int, str]) -> dict[str, Any]:
    """The facts of item 4 for the kernel g K(z(s)) and the element of the job, as at COMPLEMENTS."""
    s, name = job
    values = parallel.ordered_map(complement_fact, [(s, name, key) for key in COMPLEMENT_KEYS], min_items=2)
    return dict(zip(COMPLEMENT_KEYS, values, strict=True))


def complement_record() -> dict[str, dict[str, Any]]:
    jobs = [(s, name) for s in (1, -1) for name in ELEMENTS]
    rows = parallel.ordered_map(complement_facts, jobs, min_items=2)
    return {f"s = {s}, {name}": row for (s, name), row in zip(jobs, rows, strict=True)}


def generic_complement(plane: str) -> list[Any]:
    """At s = 2: the nullity of the Hermitian complement of the plane in K and whether it lies in P_x."""
    kernel = qg.kernel_vectors(sp.Integer(2))
    planes = qg.plane_vectors(sp.Integer(2))
    w = _complement(kernel, list(planes[plane]))
    return [15 - qg._rank(qg.msym(w).tolist()), qg._rank([*planes["x"], w]) == 2]


def generic_complements() -> dict[str, list[Any]]:
    return dict(zip("yz", parallel.ordered_map(generic_complement, ["y", "z"], min_items=2), strict=True))


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": FIELD,
        "inputs": _inputs(),
        "incidence": incidence_record(),
        "unipotent": {"element": list(UNIPOTENT), **unipotent_facts()},
        "complements": complement_record(),
        "generic_complements": generic_complements(),
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
        "incidence": copy.deepcopy(INCIDENCE),
        "unipotent": {"element": list(UNIPOTENT), **UNIPOTENT_FACTS},
        "complements": copy.deepcopy(COMPLEMENTS),
        "generic_complements": copy.deepcopy(GENERIC_COMPLEMENTS),
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    messages = {
        "inputs": "the input digests differ from the files",
        "incidence": "an incidence Jacobian at a witness has a rank other than 4, or a tangent fact differs",
        "unipotent": "the element exp(X) is not the pinned equivariant non-unitary unipotent element",
        "complements": "a Hermitian complement at s = +-1 leaves the plane x or the cone J",
        "generic_complements": "the complements of the planes y and z at s = 2 differ",
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
    print(f"pass: {len(record['incidence'])} incidence Jacobians, {len(record['complements'])} complement frames")


if __name__ == "__main__":
    main()
