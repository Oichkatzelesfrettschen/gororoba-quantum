"""The base-point stabilizer in g_2 + scaling acts on the fiber-cone generators: its image in the symmetry algebra.

At the basepoint z_0 of N+ or N- the stabilizer p of z_0 in g_2(C) + C (the scaling) preserves the germ of every
source closure and the ideal I of the 4-Pfaffians of the Schur form, so it acts on I / m I, the span of the
generators y of the fiber cone, by matrices that preserve every relation. `symmetry_algebra_qi.py` computes the
algebra g of all matrices that preserve the quadrics; this script computes the map rho: p -> g and compares its
image with the Levi factor and the radical of g.

Mechanism. The encoding z -> C(z) is linear, so along the vector field z -> X z the matrix moves by C(X z), and
the Schur form W = det(B) D + X^T adj(B) X moves by the product rule, with d det(B) = tr(adj(B) dB) and
d adj(B) = (tr(adj(B) dB) adj(B) - adj(B) dB adj(B)) / det(B). A generator G_a = pf4(W) then moves to a polynomial
dG_a on the slice. The field X z leaves the slice, and the correction that returns it is a combination, with
coefficients in the maximal ideal m, of the fields of g_2 and the scaling, each of which maps I into I; they span
the tangent space of the boundary orbit at z_0, since the boost generator of the stabilizer torus fixes z_0. The
class of dG_a modulo m I is therefore the class of the action on the slice germ. The script reduces dG_a and
the generators modulo J + m (all Pfaffians)
and a truncation above the largest weight, exactly as the producer of the generators does, and solves
dG_a = sum_b rho(X)_ab G_b on the normal forms over Q(i).

Checks per cell. Every rho(X) must exist and must lie in g (`symmetry_algebra_qi.stabilizes` on the regenerated
quadrics). The brackets must match with one sign for the whole algebra. The image of the grading element
2 t_1 - t_2 of the slice torus must be the diagonal matrix of the generator weights up to a multiple of the Euler
field: this ties the map to the grading that the producer measures independently. One control must fail to give a
matrix: the diagonal matrix 1, 2, ..., 15, a direction outside g_2, the scaling and the boost. Two further rows are
observations: a
derivation of g_2 that moves z_0, under which the Pfaffian ideal is still invariant while the relations are not,
and the boost generator of the stabilizer torus, which lies outside g_2 + scaling and has no lift to the kernel.

`--write` writes stabilizer-action-qi-result.json beside this file, `--check` recomputes and compares. Both need
Singular 4.4 on PATH.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/stabilizer_action_qi.py --check
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import itertools
import json
import re
import sys
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import symmetry_algebra_qi as qi  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402
from symmetry_algebra_qi import CMat, Gauss  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-stabilizer-action-qi-v1"
RECORD = HERE / "stabilizer-action-qi-result.json"
SOURCE_PATHS = (HERE / "stabilizer_action_qi.py", HERE / "symmetry_algebra_qi.py")
SLICE_SYMBOLS = sp.symbols(f"s1:{ws.NORMAL_DIMENSION + 1}")
# The dimension of the stabilizer of the N+ or N- basepoint in g_2(C) plus scaling: a maximal parabolic of g_2.
STABILIZER_DIMENSION = 9
# A direction outside g_2, the scaling and the boost: the diagonal matrix 1, 2, ..., 15 in the original coordinates.
CONTROL_DIAGONAL = sp.diag(*range(1, ws.COMPLEX_DIMENSION + 1))
# The largest drop or rise of the grading weight under an element of the stabilizer, with a margin of one.
WEIGHT_MARGIN = 4
# The weight truncation bounds every slice coordinate of positive weight; a coordinate of weight zero is cut at this
# power, which makes the quotient Artinian and local, so the local units in that coordinate become invertible.
ZERO_WEIGHT_ORDER = 6
PFAFFIAN_INDEX = list(itertools.combinations(range(1, ws.KERNEL_DIMENSION + 1), 4))

ACTION_STAGE = """
proc pf4d(matrix A,matrix D,int a,int b,int c,int d){
  return(D[a,b]*A[c,d]+A[a,b]*D[c,d]-D[a,c]*A[b,d]-A[a,c]*D[b,d]+D[a,d]*A[b,c]+A[a,d]*D[b,c]); }
ideal ms=s1,s2,s3,s4,s5,s6,s7,s8,s9;
ideal TRA=trunc(dmax+$margin); ideal TTA=std(J+TRA+ms*PF+ideal($zero_weight_powers));
ideal GS=$generators;
ideal NG=reduce(GS,TTA);
short=0;
for(a=1;a<=ncols(GS);a++){ print("RESULT ng_"+string(a)+" "+string(NG[a])); }
matrix Td; matrix Bd; matrix Xd; matrix Dd; poly tB; matrix aBd; matrix W1; ideal GD; ideal ND;
"""

ELEMENT_STAGE = """
$derivative_lines
Td=transpose(F)*Cd*F;
Bd=submat(Td,ra,ra); Xd=submat(Td,ra,rb); Dd=submat(Td,rb,rb);
tB=trace(aB*Bd);
aBd=(tB*aB-aB*Bd*aB)/dB;
W1=tB*Dm+dB*Dd+transpose(Xd)*aB*X+transpose(X)*aBd*X+transpose(X)*aB*Xd;
GD=$derivatives;
GD=reduce(GD,J);
ND=reduce(GD,TTA);
for(a=1;a<=ncols(GD);a++){ print("RESULT nd_${label}_"+string(a)+" "+string(ND[a])); }
kill Cd;
"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


# ---------------------------------------------------------------------------------------------------------------------
# The stabilizer of the basepoint


def ambient_generators() -> list[sp.Matrix]:
    """The fourteen derivations of g_2 in the original coordinates, then the scaling."""
    phase = ws._phase_matrix()
    derivations = [phase * ws._derivation_matrix(k) * phase.inv() for k in range(len(ws.independent.DERS))]
    return [*derivations, sp.eye(ws.COMPLEX_DIMENSION)]


def _coordinates(frame: sp.Matrix, vector: sp.Matrix) -> sp.Matrix:
    """The coordinates of a vector of the column space of `frame`."""
    solution = (frame.H * frame).inv() * frame.H * vector
    _require((frame * solution - vector).applyfunc(sp.simplify).is_zero_matrix is True, "a vector leaves the span")
    return solution.applyfunc(sp.nsimplify)


@dataclasses.dataclass(frozen=True)
class Stabilizer:
    """A basis of the stabilizer of z_0 that diagonalizes ad of the two torus generators, with its bracket table."""

    orbit: str
    weights: tuple[tuple[int, int], ...]
    grading: tuple[int, ...]
    matrices: tuple[sp.Matrix, ...]
    # constants[i][j][k]: the coefficient of basis element k in [basis_i, basis_j]
    constants: tuple[tuple[tuple[Any, ...], ...], ...]
    grading_element: tuple[Any, ...]
    moving: sp.Matrix
    boost: sp.Matrix


def build_stabilizer(piece: ws.OrbitSlice) -> Stabilizer:
    generators = ambient_generators()
    moved = sp.Matrix.hstack(*[matrix * piece.z0 for matrix in generators])
    null = moved.nullspace()
    raw = [
        sum((vector[k] * generators[k] for k in range(len(generators))), sp.zeros(15, 15)).applyfunc(sp.nsimplify)
        for vector in null
    ]
    frame = sp.Matrix.hstack(*[matrix.reshape(225, 1) for matrix in raw])
    torus = ws.torus_generators(1 if piece.orbit == "N+" else -1)

    def ad(element: sp.Matrix) -> sp.Matrix:
        columns = [_coordinates(frame, (element * matrix - matrix * element).reshape(225, 1)) for matrix in raw]
        return sp.Matrix.hstack(*columns)

    joint = ws.joint_basis([ad(torus[0]), ad(torus[1])], sp.eye(len(raw)))
    joint.sort(key=lambda item: (item[0], [str(value) for value in item[1]]))
    matrices = [
        sum((vector[k] * raw[k] for k in range(len(raw))), sp.zeros(15, 15)).applyfunc(sp.nsimplify)
        for _, vector in joint
    ]
    adapted = sp.Matrix.hstack(*[matrix.reshape(225, 1) for matrix in matrices])
    constants = tuple(
        tuple(tuple(_coordinates(adapted, (left * right - right * left).reshape(225, 1))) for right in matrices)
        for left in matrices
    )
    weights = tuple((int(item[0][0]), int(item[0][1])) for item in joint)
    moving = next(matrix for matrix in generators if not (matrix * piece.z0).is_zero_matrix)
    return Stabilizer(
        orbit=piece.orbit,
        weights=weights,
        grading=tuple(2 * first - second for first, second in weights),
        matrices=tuple(matrices),
        constants=constants,
        grading_element=tuple(_coordinates(adapted, (2 * torus[0] - torus[1]).reshape(225, 1))),
        moving=moving,
        boost=torus[2],
    )


# ---------------------------------------------------------------------------------------------------------------------
# The Singular run of one cell


def derivative_lines(piece: ws.OrbitSlice, element: sp.Matrix) -> str:
    """Singular statements for Cd = C(X z(s)), the derivative of C along the field of `element` on the slice."""
    moved = dataclasses.replace(
        piece,
        z0=(element * piece.z0).applyfunc(sp.nsimplify),
        normal=tuple((weights, (element * vector).applyfunc(sp.nsimplify)) for weights, vector in piece.normal),
    )
    text = ws._matrix_lines(moved)
    head = text[: text.index("matrix F[")]
    _require(head.startswith("matrix C["), "unexpected layout of the matrix statements")
    return re.sub(r"\bC\[", "Cd[", head)


def cell_script(
    piece: ws.OrbitSlice, slice_piece: ws.SlicePiece, source: str, selected: list[int], elements: dict[str, sp.Matrix]
) -> str:
    """The script that prints the normal forms of the generators and of their derivatives along each element."""
    grading = slice_piece.grading
    ordering = ",".join(str(max(weight, 1)) for weight in grading)
    variables = ",".join(f"s{position}" for position in range(1, ws.NORMAL_DIMENSION + 1))

    def entries(name: str) -> str:
        return ",".join(f"{name}({','.join(str(k) for k in PFAFFIAN_INDEX[index - 1])})" for index in selected)

    parts = [
        'LIB "matrix.lib"; LIB "linalg.lib"; LIB "primdec.lib";',
        ws._ring(0, 0, variables, f"wp({ordering})"),
        "option(redSB);",
        slice_piece.matrix_lines,
        f"intvec tw={','.join(str(weight) for weight in grading)};",
        "int k;",
        ws.PROCEDURES,
        f"ideal J={','.join(slice_piece.equations[source])}; J=std(J);",
        ws.COMPONENT_STEP,
        ws.PFAFFIAN_STAGE,
        ACTION_STAGE.replace("$margin", str(WEIGHT_MARGIN))
        .replace("$generators", ",".join(f"PF[{index}]" for index in selected))
        .replace(
            "$zero_weight_powers",
            ",".join(f"s{k + 1}^{ZERO_WEIGHT_ORDER}" for k, weight in enumerate(grading) if weight == 0),
        ),
    ]
    for label, element in elements.items():
        derivatives = entries("pf4d").replace("pf4d(", "pf4d(W,W1,")
        parts.append(
            ELEMENT_STAGE.replace("$derivative_lines", derivative_lines(piece, element))
            .replace("$derivatives", derivatives)
            .replace("${label}", label)
        )
    parts += ['print("RESULT done 1");', "quit;"]
    return "\n".join(parts) + "\n"


def parse_polynomial(text: str) -> dict[tuple[int, ...], Gauss]:
    """A Singular polynomial in s1..s9 over Q(i), printed with short=0, as monomial -> coefficient."""
    expression = sp.sympify(
        text.replace("^", "**"), locals={symbol.name: symbol for symbol in SLICE_SYMBOLS} | {"i": sp.I}
    )
    poly = sp.Poly(sp.expand(expression), *SLICE_SYMBOLS, domain=sp.QQ_I)
    table = {}
    for monomial, value in poly.as_dict().items():
        real, imaginary = sp.sympify(value).as_real_imag()
        table[tuple(int(e) for e in monomial)] = Gauss(
            qi.fmpq(int(real.p), int(real.q)), qi.fmpq(int(imaginary.p), int(imaginary.q))
        )
    return table


def action_matrix(
    generators: list[dict[tuple[int, ...], Gauss]], derivatives: list[dict[tuple[int, ...], Gauss]]
) -> CMat | None:
    """The matrix A with derivative_a = sum_b A_ab generator_b on the normal forms, or None when one has no solution."""
    count = len(generators)
    keys = sorted({key for table in generators + derivatives for key in table})
    equations = [[table.get(key, qi.ZERO) for table in generators] for key in keys]
    rows = []
    for derivative in derivatives:
        solution = qi.solve(equations, [derivative.get(key, qi.ZERO) for key in keys], count)
        if solution is None:
            return None
        rows.append(solution)
    return CMat.from_rows(rows, count)


def run_cell(job: tuple[str, str, list[int], dict[str, str], str]) -> dict[str, Any]:
    """Run one cell script and return the normal forms: generators, then the derivatives per element label."""
    orbit, source, _selected, _elements, script = job
    values = ws.run_singular(script)["values"]
    count = len(_selected)
    generators = [values[f"ng_{a}"][0] for a in range(1, count + 1)]
    derivatives = {label: [values[f"nd_{label}_{a}"][0] for a in range(1, count + 1)] for label in _elements}
    return {
        "orbit": orbit,
        "source": source,
        "generators": generators,
        "derivatives": derivatives,
        "selected": list(_selected),
    }


# ---------------------------------------------------------------------------------------------------------------------
# Comparison with the symmetry algebra


def analyze(job: tuple[dict[str, Any], dict[str, Any], tuple[str, str, int, list[int], list[str]]]) -> dict[str, Any]:
    """One cell: the matrices rho(X), their membership in g, the bracket sign, the grading and the Levi comparison."""
    run, stabilizer, cell = job
    orbit, source, n, grading, lines = cell
    label = ws.incidence_name(orbit, source)
    generators = [parse_polynomial(text) for text in run["generators"]]
    images: dict[str, CMat | None] = {
        name: action_matrix(generators, [parse_polynomial(text) for text in texts])
        for name, texts in run["derivatives"].items()
    }
    names = [f"x{k}" for k in range(len(stabilizer["weights"]))]
    row: dict[str, Any] = {
        "incidence": label,
        "orbit": orbit,
        "source": source,
        "generators": n,
        "relations_sha256": hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode("utf-8")).hexdigest(),
        "generator_normal_forms_rank": qi.rank(
            [[table.get(key, qi.ZERO) for key in sorted({k for t in generators for k in t})] for table in generators],
            len({k for t in generators for k in t}),
        ),
        "stabilizer_dimension": len(names),
        "selected_pfaffians_one_based": list(run["selected"]),
        "elements_with_a_matrix": sum(images[name] is not None for name in names),
        "control_diagonal_has_a_matrix": images["diagonal"] is not None,
        "moving_derivation_has_a_matrix": images["moving"] is not None,
        "boost_has_a_matrix": images["boost"] is not None,
    }
    if row["elements_with_a_matrix"] != len(names):
        return row
    matrices = [image for name in names if (image := images[name]) is not None]
    quadrics = qi.read_quadrics(lines)
    echelon, pivots = qi.quadric_basis(quadrics, n)
    sparse = [{k: entry for k, entry in enumerate(entries) if entry} for entries in echelon]
    row["elements_in_symmetry_algebra"] = sum(qi.stabilizes(matrix, sparse, echelon, pivots, n) for matrix in matrices)
    for name in ("boost", "moving"):
        image = images[name]
        if image is not None:
            row[f"{name}_in_symmetry_algebra"] = qi.stabilizes(image, sparse, echelon, pivots, n)
    constants = stabilizer["constants"]
    signs = set()
    for i, j in itertools.combinations(range(len(names)), 2):
        expected = [Gauss(qi.fmpq(*value[0]), qi.fmpq(*value[1])) for value in constants[i][j]]
        target = qi.combine(expected, matrices) if any(expected) else None
        commutator = matrices[i] @ matrices[j] - matrices[j] @ matrices[i]
        if target is None:
            signs.add("zero" if commutator.is_zero() else "mismatch")
        elif (commutator - target).is_zero():
            signs.add("plus")
        elif (commutator + target).is_zero():
            signs.add("minus")
        else:
            signs.add("mismatch")
    row["bracket_signs"] = sorted(signs)
    coefficients = [Gauss(qi.fmpq(*value[0]), qi.fmpq(*value[1])) for value in stabilizer["grading_element"]]
    graded = qi.combine(coefficients, matrices).rows()
    offsets = {
        (str((graded[k][k] - Gauss(grading[k], 0)).re), str((graded[k][k] - Gauss(grading[k], 0)).im)) for k in range(n)
    }
    negated = {
        (str((graded[k][k] + Gauss(grading[k], 0)).re), str((graded[k][k] + Gauss(grading[k], 0)).im)) for k in range(n)
    }
    diagonal = all(not graded[a][b] for a in range(n) for b in range(n) if a != b)
    row["grading_image_is_diagonal"] = diagonal
    row["grading_image_minus_weights"] = sorted(offsets) if len(offsets) == 1 else None
    row["grading_image_plus_weights"] = sorted(negated) if len(negated) == 1 else None
    # The image inside g: coordinates on the echelon basis of g, then ranks against the radical.
    algebra, _ = qi.stabilizer(quadrics, n)
    basis, ad = qi.adjoint(algebra, label)
    structure = qi.Structure(ad)
    flat, basis_pivots = qi.rref([qi.flatten(matrix) for matrix in basis], n * n)
    coordinates = [[qi.flatten(matrix)[pivot] for pivot in basis_pivots] for matrix in matrices]
    radical = qi.killing_radical(structure)
    levi = [coordinates[k] for k in range(len(names)) if stabilizer["grading"][k] == 0]
    unipotent = [coordinates[k] for k in range(len(names)) if stabilizer["grading"][k] != 0]
    row |= {
        "symmetry_algebra_dimension": structure.dim,
        "radical_dimension": len(radical),
        "image_dimension": qi.rank(coordinates, structure.dim),
        "image_plus_radical_dimension": qi.rank(coordinates + radical, structure.dim),
        "grading_zero_part_dimension": len(levi),
        "grading_zero_image_dimension": qi.rank(levi, structure.dim),
        "grading_zero_image_modulo_radical": qi.rank(levi + radical, structure.dim) - len(radical),
        "grading_nonzero_part_dimension": len(unipotent),
        "grading_nonzero_image_dimension": qi.rank(unipotent, structure.dim),
        "grading_nonzero_image_in_radical": qi.rank(unipotent + radical, structure.dim) == len(radical),
    }
    boost = images["boost"]
    if boost is not None and row.get("boost_in_symmetry_algebra"):
        extended = [*coordinates, [qi.flatten(boost)[pivot] for pivot in basis_pivots]]
        row["image_with_boost_dimension"] = qi.rank(extended, structure.dim)
    return row


def _pair(value: Any) -> tuple[tuple[int, int], tuple[int, int]]:
    real, imaginary = sp.sympify(value).as_real_imag()
    return (int(real.p), int(real.q)), (int(imaginary.p), int(imaginary.q))


def stabilizer_payload(stabilizer: Stabilizer) -> dict[str, Any]:
    """The picklable integers of a stabilizer that `analyze` needs."""
    return {
        "weights": [list(weights) for weights in stabilizer.weights],
        "grading": list(stabilizer.grading),
        "constants": [[[_pair(value) for value in row] for row in block] for block in stabilizer.constants],
        "grading_element": [_pair(value) for value in stabilizer.grading_element],
    }


def orbit_setup(orbit: str) -> tuple[ws.OrbitSlice, ws.SlicePiece, Stabilizer]:
    """The slice, its Singular statements and the stabilizer of one basepoint; the two orbits are independent."""
    piece = ws.build_slice(orbit)
    return piece, ws.orbit_task(orbit), build_stabilizer(piece)


def compute(cells: tuple[tuple[str, str], ...] = qi.CELLS) -> dict[str, Any]:
    banner, version = ws.singular_version()
    retained = {
        (cell["orbit"], cell["source"]): cell
        for cell in json.loads(qi.RELATIONS_RECORD.read_text(encoding="utf-8"))["cells"]
        if cell["characteristic"] == 0
    }
    setups = parallel.ordered_map(orbit_setup, ws.ORBITS, min_items=1)
    pieces = {orbit: setup[0] for orbit, setup in zip(ws.ORBITS, setups, strict=True)}
    slice_pieces = {orbit: setup[1] for orbit, setup in zip(ws.ORBITS, setups, strict=True)}
    stabilizers = {orbit: setup[2] for orbit, setup in zip(ws.ORBITS, setups, strict=True)}
    relations = {(job[0], job[1]): job for job in qi.regenerate_relations()}
    jobs = []
    for orbit, source in cells:
        stabilizer = stabilizers[orbit]
        selected = [int(index) for index in retained[(orbit, source)]["selected_pfaffians_one_based"]]
        elements = {f"x{k}": matrix for k, matrix in enumerate(stabilizer.matrices)}
        elements |= {"moving": stabilizer.moving, "boost": stabilizer.boost, "diagonal": CONTROL_DIAGONAL}
        script = cell_script(pieces[orbit], slice_pieces[orbit], source, selected, elements)
        jobs.append((orbit, source, selected, dict.fromkeys(elements, ""), script))
    runs = parallel.ordered_map(run_cell, jobs, min_items=1)
    work = [
        (run, stabilizer_payload(stabilizers[orbit]), relations[(orbit, source)])
        for run, (orbit, source) in zip(runs, cells, strict=True)
    ]
    rows = parallel.ordered_map(analyze, work, min_items=1)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "field": "Q(i)",
        "inputs": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS},
        "tools": {"singular": banner, "singular_version": version},
        "stabilizers": [
            {
                "orbit": orbit,
                "dimension": len(stabilizers[orbit].weights),
                "torus_weights": [list(w) for w in stabilizers[orbit].weights],
                "grading_weights": list(stabilizers[orbit].grading),
            }
            for orbit in ws.ORBITS
        ],
        "rows": rows,
    }
    record["pass"] = verdict(record) == []
    return record


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes."""
    problems = []
    for row in record["rows"]:
        name = row["incidence"]
        if row["generator_normal_forms_rank"] != row["generators"]:
            problems.append(f"{name}: the normal forms of the generators are dependent")
        if row["stabilizer_dimension"] != STABILIZER_DIMENSION:
            problems.append(f"{name}: the stabilizer has dimension {row['stabilizer_dimension']}")
        if row["elements_with_a_matrix"] != row["stabilizer_dimension"]:
            problems.append(f"{name}: a stabilizer element has no matrix on the generators")
            continue
        if row["elements_in_symmetry_algebra"] != row["stabilizer_dimension"]:
            problems.append(f"{name}: an image leaves the symmetry algebra")
        if row["bracket_signs"] not in (["plus"], ["plus", "zero"], ["minus"], ["minus", "zero"]):
            problems.append(f"{name}: the brackets do not match with one sign ({row['bracket_signs']})")
        if not row["grading_image_is_diagonal"] or (
            row["grading_image_minus_weights"] is None and row["grading_image_plus_weights"] is None
        ):
            problems.append(
                f"{name}: the image of the grading element is not the weight derivation up to the Euler field"
            )
        if row["control_diagonal_has_a_matrix"]:
            problems.append(f"{name}: the diagonal control has a matrix")
        if row["moving_derivation_has_a_matrix"] and row.get("moving_in_symmetry_algebra"):
            problems.append(f"{name}: a derivation that moves the basepoint preserves the quadrics")
        if row["image_dimension"] != row["stabilizer_dimension"]:
            problems.append(f"{name}: the map from the stabilizer is not injective")
        if row["image_plus_radical_dimension"] != row["symmetry_algebra_dimension"]:
            problems.append(f"{name}: the image and the radical do not span the symmetry algebra")
        if row["grading_zero_image_modulo_radical"] != 3 or not row["grading_nonzero_image_in_radical"]:
            problems.append(f"{name}: the weight-zero part does not map onto the Levi factor")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument(
        "--cell", action="append", help="ORBIT|SOURCE; repeat to restrict the run (no record is written)"
    )
    args = parser.parse_args()
    if args.cell:
        cells = tuple((text.split("|")[0], text.split("|")[1]) for text in args.cell)
        print(json.dumps(compute(cells), indent=1, sort_keys=True))
        return
    record = compute()
    if args.write:
        RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    elif qi.comparable(json.loads(RECORD.read_text(encoding="utf-8"))) != qi.comparable(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    for row in record["rows"]:
        print(row["incidence"], row["image_dimension"], row["grading_zero_image_modulo_radical"], row["bracket_signs"])


if __name__ == "__main__":
    main()
