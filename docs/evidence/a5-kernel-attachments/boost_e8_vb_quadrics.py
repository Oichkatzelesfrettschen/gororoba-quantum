"""The quadric scheme of the fiber cone of E8bar->VB at basepoints moved along the boost, modulo 32029.

G_2(C) x C^* transports the fiber of holomorphic kernel limits along six of the seven directions of the VB orbit;
the seventh is the boost u -> c u + s v, v -> s u + c v with c^2 - s^2 = 1, which has no lift to the kernel
(`kernel_equivariance.py`). `boost_fiber_variation.py` samples the boost for the four incidences whose fiber is a
whole projective space and leaves E8bar->VB out, because its Rees elimination does not finish. This producer samples
E8bar->VB through the relations of low degree of its fiber cone instead.

At each basepoint (the retained one and three rational boosts of it) the script moves the boundary point, keeps the
retained slice columns, emits the presolved slice ideal J and the Nakayama generators G by the phase-one script of
the nullity-16 Rees record (`fiber_inputs._nakayama_inputs` with the moved row), and computes the degree-2 relations
{q : q(G) in J + m I^2} by the Singular stage of `../a5-char0-transfer/quadric_lift.py`, modulo 32029 with i sent
to 9115. From the quadrics it reads the Hilbert numerator, dimension, multiplicity, saturation, radicality and
minimal primes of the quadric ideal (Singular) and the dimension of its linear symmetry algebra (the modular
stabilizer of the quadric census). At the retained basepoint the echelon form of the relations must equal the
retained K2 of the exceptional-fiber record. At one boosted basepoint the script also counts the degree-3 relations:
220 minus that count is h_3 of the fiber cone there, to compare with the Hilbert function of the quadric ring.

The four quadric ideals are then compared directly. Each echelon basis yields three scalars a, b, d and from them
an invertible matrix M (`adapted_frame`); `normal_form` substitutes y = M w and row-reduces. The four normal forms
are one ideal, so M_k M_0^{-1} is a linear change of the 10 generators that carries the quadric ideal at basepoint
k onto the one at the retained basepoint: the four quadric schemes are projectively equivalent over F_32029. As a
control, the frame of the retained basepoint applied at a moved basepoint gives another ideal.

The equivalence concerns the quadric schemes at four sampled points in one characteristic. The fiber cone above
degree 2 is compared at one moved point and in degree 3 alone, and no limiting plane is compared.

`--write` writes boost-e8-vb-quadrics-result.json beside this file, `--check` recomputes and compares. Both need
Singular 4.4 on PATH; the degree-3 count takes about 18 minutes in one process.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/boost_e8_vb_quadrics.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRANSFER = HERE.parent / "a5-char0-transfer"
CENSUS = HERE.parent / "a5-exceptional-fibers" / "quadric-census"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(TRANSFER))
sys.path.insert(0, str(CENSUS.parent))
sys.path.insert(0, str(CENSUS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import boost_fiber_variation as boosts_record  # noqa: E402
import fiber_inputs  # noqa: E402
import quadric_lift  # noqa: E402
import reduction_check  # noqa: E402
import symmetry_algebra  # noqa: E402

import parallel  # noqa: E402

nakayama = fiber_inputs.nakayama
rees = reduction_check.rees

SCHEMA = "a5-kernel-attachments-boost-e8-vb-quadrics-v1"
RECORD = HERE / "boost-e8-vb-quadrics-result.json"
INCIDENCE = "E8bar->VB"
PRIME, ROOT_OF_MINUS_ONE = 32029, 9115
FIELD = f"GF({PRIME}), i = {ROOT_OF_MINUS_ONE}"
RETAINED_K2 = "a5-p2-small/vb_p2/d2"
BOOSTS = boosts_record.BOOSTS
DEGREE_THREE_BOOST = BOOSTS[1]
SINGULAR_TIMEOUT_SECONDS = 3600
SOURCE_PATHS = (
    HERE / "boost_e8_vb_quadrics.py",
    HERE / "boost_fiber_variation.py",
    HERE / "fiber_inputs.py",
    HERE / "nullity16_rees_fibers.py",
    HERE / "first-order-normal-cones-result.json",
    TRANSFER / "quadric_lift.py",
    CENSUS / "symmetry_algebra.py",
)
# What the retained basepoint gives; every sampled basepoint must give the same.
GENERATORS = 10
FIRST_NUMERATOR = [1, 0, -21, 70, -105, 84, -35, 6]
EXPECTED: dict[str, Any] = {
    "generators": GENERATORS,
    "relations": 21,
    "affine_dimension": 4,
    "multiplicity": 7,
    "first_numerator": FIRST_NUMERATOR,
    "saturated": True,
    "radical": True,
    "minimal_primes": [[4, 3], [4, 4]],
    "symmetry_algebra_dimension": 15,
}
PRODUCTS = {2: math.comb(GENERATORS + 1, 2), 3: math.comb(GENERATORS + 2, 3)}
DEGREE_THREE_RELATIONS = 140
SLICE_DIMENSION, COMPLEX_DIMENSION = 8, 15
# Membership of a VB point in the twelve closure ideals, and the digest of the retained K2 relation file.
CLOSURE_MEMBERSHIP = "111111110000"
RETAINED_K2_SHA256 = "e65cbd06cbcef44195409f776541d28e0f7a39f50347eea54b21a15f7c5a95ac"
# The three scalars of the adapted frame, as (monomial that names the row, monomial whose coefficient is read).
FRAME_SCALARS = {"a": ((7, 10), (1, 7)), "b": ((7, 9), (5, 7)), "d": ((6, 7), (1, 7))}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def moved_inputs(boost: tuple[Fraction, Fraction]) -> tuple[Any, Any, tuple[int, ...], dict[str, Any]]:
    """The row task, Schur data, candidate indices and transversality data of E8bar->VB at a moved basepoint."""
    first_order = nakayama._load_json(nakayama.FIRST_ORDER_RESULT)
    retained = next(row for row in first_order["incidences"] if row["incidence"] == INCIDENCE)
    row = boosts_record.moved_row(retained, boost)
    ideals = nakayama.regularity.closure_ideals()
    source = str(row["source_orbit"])
    closure = tuple(str(value) for value in ideals[nakayama.SOURCE_KEYS.get(source, source)])
    schur = nakayama.resolved._schur_polynomials(nakayama.resolved.IncidenceTask(row))
    shim = {
        "incidence": row["incidence"],
        "passage": "8->12",
        "source_orbit": source,
        "boundary_orbit": row["boundary_orbit"],
        "source_nullity": 8,
        "census_point_key": f"{row['boundary_orbit']}:canonical",
        "boundary_point": [str(value) for value in row["boundary_point"]],
        "expected_germ_dimension_multiplicity_embedding_components": [0, 0, 0, 0],
    }
    data = SimpleNamespace(
        slice_names=tuple(schur.slice_names),
        slice_columns=tuple(int(value) for value in row["slice_columns_zero_based"]),
        coordinates=tuple(schur.coordinates),
    )
    candidates = tuple(range(1, len(data.coordinates) + 1))
    return rees.RowTask(shim, closure), data, candidates, boosts_record.transversality(row)


def relation_script(boost: tuple[Fraction, Fraction], degree: int) -> str:
    """The Singular script for the relations of the given degree at the moved basepoint, modulo PRIME."""
    task, data, candidates, _ = moved_inputs(boost)
    body = rees._phase_one_script(ROOT_OF_MINUS_ONE, task, data, candidates, prime=PRIME, embedding=False)
    stage = "\n".join(quadric_lift.QUADRICS).replace("@SLICE@", ",".join(data.slice_names))
    for old, new in (("ring Y=0,", f"ring Y={PRIME},"), ("kbase(std(ideal(0)),2)", f"kbase(std(ideal(0)),{degree})")):
        _require(stage.count(old) == 1, f"the relation stage holds {stage.count(old)} copies of {old}")
        stage = stage.replace(old, new)
    return body.replace("\nquit;", "") + "\n" + stage + "\nquit;\n"


def hilbert_data(quadrics: list[dict[tuple[int, int], int]], generators: int) -> dict[str, Any]:
    """Hilbert numerator, dimension, multiplicity, saturation, radicality and minimal primes of the quadric ideal."""
    polynomials = ",".join(
        "+".join(f"{value}*y({a + 1})*y({b + 1})" for (a, b), value in quadric.items()) for quadric in quadrics
    )
    script = "\n".join(
        (
            'LIB "primdec.lib";',
            f"ring r={PRIME},(y(1..{generators})),dp; option(redSB);",
            f"ideal K={polynomials}; ideal S=std(K);",
            'print("RESULT dimension "+string(dim(S)));',
            'print("RESULT multiplicity "+string(mult(S)));',
            'print("RESULT numerator "+string(hilb(S,1)));',
            'print("RESULT saturated "+string(size(reduce(quotient(S,maxideal(1)),S))==0));',
            'print("RESULT radical "+string(size(reduce(radical(K),S))==0));',
            "list L=minAssGTZ(K); int k; ideal c;",
            'for(k=1;k<=size(L);k++){ c=std(L[k]); print("RESULT prime "+string(dim(c))+","+string(mult(c))); }',
            'print("RESULT done 1");',
            "quit;",
        )
    )
    with tempfile.TemporaryDirectory(prefix="boost-e8-vb-") as directory:
        path = Path(directory) / "hilbert.sing"
        path.write_text(script + "\n", encoding="utf-8")
        process = subprocess.run(
            ["Singular", "-q", "--no-warn", "--no-rc", str(path)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
            timeout=SINGULAR_TIMEOUT_SECONDS,
        )
    values: dict[str, list[str]] = {}
    for line in process.stdout.splitlines():
        if line.startswith("RESULT "):
            key, _, value = line.removeprefix("RESULT ").partition(" ")
            values.setdefault(key, []).append(value)
    _require(process.returncode == 0 and values.get("done") == ["1"], f"Singular failed: {process.stdout[-800:]}")
    numerator = [int(token) for token in values["numerator"][0].split(",")]
    return {
        "affine_dimension": int(values["dimension"][0]),
        "multiplicity": int(values["multiplicity"][0]),
        # The last entry of hilb(I, 1) is bookkeeping of Singular's Hilbert-driven standard basis.
        "first_numerator": numerator[:-1],
        "saturated": values["saturated"][0] == "1",
        "radical": values["radical"][0] == "1",
        "minimal_primes": sorted([int(token) for token in text.split(",")] for text in values.get("prime", [])),
    }


def adapted_frame(quadrics: list[dict[tuple[int, int], int]]) -> tuple[dict[str, int], list[list[int]]]:
    """The scalars a, b, d of one echelon basis and the matrix M of the substitution y = M w they define.

    The linear spans of the two components are cut out by y7, y3, y4 + y6 and by y10 + a y1, y9 + b y5, y8 + b y2,
    y6 - y4 + d y1. M takes those seven forms to w1, w2, w3 and w4 - (d/2) w7, w5, w6, w7 and y1, y2, y5 to
    w8, w9, w10. Nothing here is assumed: `normal_form` decides whether the frame works.
    """
    scalars = {}
    for name, (pivot, monomial) in FRAME_SCALARS.items():
        rows = [quadric for quadric in quadrics if (pivot[0] - 1, pivot[1] - 1) in quadric]
        _require(len(rows) == 1, f"{len(rows)} echelon rows hold y{pivot[0]} y{pivot[1]}")
        scalars[name] = rows[0].get((monomial[0] - 1, monomial[1] - 1), 0)
    a, b, d = scalars["a"], scalars["b"], scalars["d"]
    half = (PRIME + 1) // 2
    forms: dict[int, dict[int, int]] = {
        1: {8: 1},
        2: {9: 1},
        3: {2: 1},
        4: {3: half, 7: -half, 8: half * d},
        5: {10: 1},
        6: {3: half, 7: half, 8: -half * d},
        7: {1: 1},
        8: {6: 1, 9: -b},
        9: {5: 1, 10: -b},
        10: {4: 1, 7: -half * d, 8: -a},
    }
    matrix = [[forms[k + 1].get(j + 1, 0) % PRIME for j in range(GENERATORS)] for k in range(GENERATORS)]
    _require(len(quadric_lift._rref_fp(matrix, PRIME)) == GENERATORS, "the adapted frame is singular")
    return scalars, matrix


def normal_form(quadrics: list[dict[tuple[int, int], int]], matrix: list[list[int]]) -> list[list[int]]:
    """The reduced echelon basis of the quadrics after the substitution y = M w, on the monomials w_i w_j, i <= j."""
    columns = {
        pair: index for index, pair in enumerate((i, j) for i in range(GENERATORS) for j in range(i, GENERATORS))
    }
    rows = []
    for quadric in quadrics:
        row = [0] * len(columns)
        for (first, second), value in quadric.items():
            for i, left in enumerate(matrix[first]):
                if not left:
                    continue
                for j, right in enumerate(matrix[second]):
                    if right:
                        column = columns[(min(i, j), max(i, j))]
                        row[column] = (row[column] + value * left * right) % PRIME
        rows.append(row)
    return [list(row) for row in quadric_lift._rref_fp(rows, PRIME)]


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value).encode("utf-8")).hexdigest()


def degree_two_row(boost: tuple[Fraction, Fraction]) -> dict[str, Any]:
    """Geometry, relation counts, echelon digest, Hilbert data and symmetry algebra dimension at one basepoint."""
    task, data, _, geometry = moved_inputs(boost)
    outcome = rees._run_singular(relation_script(boost, 2), "boost_e8_vb_d2", SINGULAR_TIMEOUT_SECONDS)
    _require(outcome.status == "completed", f"{boost}: {outcome.status} {outcome.diagnostic}")
    results = outcome.results
    count = int(results["targets"])
    targets = [quadric_lift._monomial(results[f"target_{k}"]) for k in range(1, count + 1)]
    generators = max(index for target in targets for index in target)
    relations = [
        [int(value) % PRIME for value in results[f"rel_{k}"].split(";")]
        for k in range(1, int(results["relations"]) + 1)
    ]
    echelon = quadric_lift._rref_fp(relations, PRIME)
    quadrics = [
        {(target[0] - 1, target[1] - 1): value for target, value in zip(targets, row, strict=True) if value}
        for row in echelon
    ]
    row: dict[str, Any] = {
        "boost": [str(value) for value in boost],
        "transversality": geometry,
        # The moved boundary point, the Schur coordinates and the slice columns the relation stage reads.
        "moved_input_sha256": _digest(
            [task.row["boundary_point"], [str(value) for value in data.coordinates], list(data.slice_columns)]
        ),
        "_quadrics": [[[a, b, value] for (a, b), value in quadric.items()] for quadric in quadrics],
        "generators": generators,
        "products": count,
        "relations": len(echelon),
        "echelon_sha256": _digest(echelon),
        "symmetry_algebra_dimension": len(symmetry_algebra.stabilizer(quadrics, generators, PRIME)),
    }
    row |= hilbert_data(quadrics, generators)
    if boost == BOOSTS[0]:
        columns = {monomial: index for index, monomial in enumerate(targets)}
        path = quadric_lift.FIBERS / RETAINED_K2 / "relations-upto-d2.rel"
        retained = quadric_lift._rref_fp(quadric_lift._modular_rows(path, columns, PRIME), PRIME)
        row["retained_k2_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        row["equals_retained_k2"] = retained == echelon
    return row


def degree_three_row(boost: tuple[Fraction, Fraction]) -> dict[str, Any]:
    """The count of degree-3 relations at one basepoint and the Hilbert value it leaves."""
    stage_end = '"RESULT targets",c;"RESULT relations",size(S);'
    script = relation_script(boost, 3)
    start = script.index('"RESULT targets"')
    script = script[:start] + stage_end + "\nquit;\n"
    outcome = rees._run_singular(script, "boost_e8_vb_d3", SINGULAR_TIMEOUT_SECONDS)
    _require(outcome.status == "completed", f"{boost} degree 3: {outcome.status} {outcome.diagnostic}")
    products, relations = int(outcome.results["targets"]), int(outcome.results["relations"])
    return {
        "boost": [str(value) for value in boost],
        "products": products,
        "relations": relations,
        "h_3": products - relations,
    }


def job(item: tuple[int, tuple[Fraction, Fraction]]) -> dict[str, Any]:
    degree, boost = item
    return degree_two_row(boost) if degree == 2 else degree_three_row(boost)


def normalize(item: tuple[list[dict[tuple[int, int], int]], list[list[int]]]) -> dict[str, Any]:
    """The frame scalars of one quadric ideal and its normal forms in its own frame and in the retained frame."""
    quadrics, retained_frame = item
    scalars, matrix = adapted_frame(quadrics)
    return {
        "adapted_frame_scalars": scalars,
        "normal_form_sha256": _digest(normal_form(quadrics, matrix)),
        "normal_form_in_retained_frame_sha256": _digest(normal_form(quadrics, retained_frame)),
    }


def quadric_ring_hilbert(numerator: list[int], generators: int, degree: int) -> int:
    """The Hilbert function in the given degree of a quotient of k[y_1..y_n] with that first numerator."""
    return sum(
        coefficient * math.comb(generators - 1 + degree - shift, generators - 1)
        for shift, coefficient in enumerate(numerator)
        if degree >= shift
    )


def compute() -> dict[str, Any]:
    items = [(2, boost) for boost in BOOSTS] + [(3, DEGREE_THREE_BOOST)]
    rows = parallel.ordered_map(job, items, min_items=1)
    ideals = [
        [{(a, b): value for a, b, value in quadric} for quadric in row.pop("_quadrics")] for row in rows[: len(BOOSTS)]
    ]
    retained_frame = adapted_frame(ideals[0])[1]
    normalized = parallel.ordered_map(normalize, [(quadrics, retained_frame) for quadrics in ideals], min_items=1)
    for row, fields in zip(rows[: len(BOOSTS)], normalized, strict=True):
        row.update(fields)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "incidence": INCIDENCE,
        "field": FIELD,
        "inputs": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS},
        "basepoints": rows[: len(BOOSTS)],
        "degree_three": rows[len(BOOSTS)] | {"quadric_ring_h_3": quadric_ring_hilbert(FIRST_NUMERATOR, GENERATORS, 3)},
    }
    record["pass"] = verdict(record) == []
    return record


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes."""
    problems = []
    header = (record.get("schema"), record.get("incidence"), record.get("field"))
    if header != (SCHEMA, INCIDENCE, FIELD):
        problems.append(f"the record is headed {header}")
    rows = record["basepoints"]
    if [row["boost"] for row in rows] != [[str(value) for value in boost] for boost in BOOSTS]:
        problems.append("the basepoints differ from the four boosts")
    for row in rows:
        name = "boost " + ", ".join(row["boost"])
        geometry = row["transversality"]
        if (
            geometry["orbit_dimension"] != COMPLEX_DIMENSION - SLICE_DIMENSION
            or geometry["slice_dimension"] != SLICE_DIMENSION
            or geometry["rank_of_orbit_tangent_with_slice"] != COMPLEX_DIMENSION
            or geometry["closure_membership"] != CLOSURE_MEMBERSHIP
        ):
            problems.append(f"{name}: the point leaves the VB orbit or the slice is not complementary")
        if row.get("products") != PRODUCTS[2]:
            problems.append(f"{name}: {row.get('products')} degree-2 products")
        for key, value in EXPECTED.items():
            if row.get(key) != value:
                problems.append(f"{name}: {key} is {row.get(key)}, expected {value}")
    if rows and (rows[0].get("equals_retained_k2"), rows[0].get("retained_k2_sha256")) != (True, RETAINED_K2_SHA256):
        problems.append("the retained basepoint does not reproduce the retained K2")
    if len({row["moved_input_sha256"] for row in rows}) != len(rows):
        problems.append("two basepoints hand the relation stage the same input")
    if len({row["normal_form_sha256"] for row in rows}) != 1:
        problems.append("the adapted frames do not carry the four quadric ideals onto one ideal")
    for row in rows[1:]:
        # Control: the frame of the retained point is the wrong frame at a moved point.
        if rows and row["normal_form_in_retained_frame_sha256"] == rows[0]["normal_form_sha256"]:
            problems.append("the retained frame carries a moved ideal onto the common one: the control is void")
    if rows and rows[0]["normal_form_in_retained_frame_sha256"] != rows[0]["normal_form_sha256"]:
        problems.append("the retained frame gives two normal forms at the retained point")
    third = record["degree_three"]
    expected_h_3 = quadric_ring_hilbert(FIRST_NUMERATOR, GENERATORS, 3)
    if third["boost"] != [str(value) for value in DEGREE_THREE_BOOST]:
        problems.append("the degree-3 count is not at the boosted basepoint")
    if (third["products"], third["relations"]) != (PRODUCTS[3], DEGREE_THREE_RELATIONS):
        problems.append(f"degree 3 has {third['products']} products and {third['relations']} relations")
    if not third["h_3"] == third["products"] - third["relations"] == third["quadric_ring_h_3"] == expected_h_3:
        problems.append("h_3 at the boosted basepoint differs from the quadric ring")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    elif json.loads(RECORD.read_text(encoding="utf-8")) != record:
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    print([(row["boost"], row["relations"], row["symmetry_algebra_dimension"]) for row in record["basepoints"]])
    print(record["degree_three"])


if __name__ == "__main__":
    main()
