"""Exact first-order normal-cone images for the A_5 nullity-8 to nullity-12 incidences."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any, TypeAlias, cast

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL_BUNDLES = HERE.parent / "a5-kernel-bundles"
NULLITY_EIGHT = HERE.parent / "a5-kernel-bundles-nullity8"
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(KERNEL_BUNDLES))
sys.path.insert(0, str(NULLITY_EIGHT))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import boundary_specializations as boundary  # noqa: E402
import kernel_frames  # noqa: E402
import path_supported_basepoints as basepoints  # noqa: E402
import strata_regularity as regularity  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

SCHEMA = "a5-kernel-attachments-first-order-normal-cones-v1"
MATRIX_DIMENSION = 16
BOUNDARY_MATRIX_RANK = 10
BOUNDARY_KERNEL_DIMENSION = 6
LIMITING_KERNEL_DIMENSION = 4
SINGULAR_MEMORY_LIMIT = "8589934592"
SINGULAR_TIMEOUT_SECONDS = 900
ORBIT_KEYS = {"E8bar": "Ehat", "X+": "Xp", "X-": "Xm", "Va+": "Vap", "Va-": "Vam"}
SOURCE_PATHS = (
    HERE / "first_order_normal_cones.py",
    HERE / "path_supported_basepoints.py",
    HERE / "path-supported-basepoints-result.json",
    ROOT / "docs" / "design" / "a5-kernel-attachments-program.md",
    NULLITY_EIGHT / "boundary_specializations.py",
    NULLITY_EIGHT / "boundary-specializations-result.json",
    KERNEL_BUNDLES / "kernel_frames.py",
    REGULARITY / "strata_regularity.py",
    REGULARITY / "result.json",
    EQUATIONS / "rederive_strata_equations.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
)

RationalVector: TypeAlias = tuple[Fraction, ...]


@dataclass(frozen=True)
class Incidence:
    source_orbit: str
    boundary_orbit: str

    @property
    def name(self) -> str:
        return f"{self.source_orbit}->{self.boundary_orbit}"

    @property
    def source_key(self) -> str:
        return ORBIT_KEYS.get(self.source_orbit, self.source_orbit)

    @property
    def boundary_key(self) -> str:
        return ORBIT_KEYS.get(self.boundary_orbit, self.boundary_orbit)


@dataclass(frozen=True)
class AnalysisContext:
    incidence: Incidence
    boundary_point: RationalVector
    slice_columns: tuple[int, ...]
    slice_symbols: tuple[sp.Symbol, ...]
    boundary_frame: sp.Matrix
    effective_form: sp.Matrix
    tangent_generators: tuple[sp.Expr, ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(path: Path) -> tuple[str, str]:
    return str(path.relative_to(ROOT)), _sha256(path)


def _incidence_candidate(task: tuple[str, str]) -> Incidence | None:
    source_orbit, boundary_orbit = task
    if boundary_orbit not in boundary.INCIDENCES[source_orbit]:
        return None
    return Incidence(source_orbit, boundary_orbit)


def _incidences() -> tuple[Incidence, ...]:
    boundary_orbits = tuple(sorted(set(itertools.chain.from_iterable(boundary.INCIDENCES.values()))))
    candidates = tuple(itertools.product(tuple(boundary.INCIDENCES), boundary_orbits))
    selected = parallel.ordered_map(_incidence_candidate, candidates, min_items=1)
    return tuple(sorted(filter(None, selected), key=lambda incidence: cast(Incidence, incidence).name))


def _holomorphic_matrix(split_direction: Sequence[Fraction | sp.Expr]) -> sp.Matrix:
    original_direction = kernel_frames._original_z_from_split(cast("Sequence[int]", split_direction))
    matrix = sp.zeros(MATRIX_DIMENSION)
    for row in range(1, MATRIX_DIMENSION):
        for column in range(1, MATRIX_DIMENSION):
            product = row ^ column
            if product:
                matrix[row, column] = cd_sign(MATRIX_DIMENSION, product, column) * original_direction[product - 1]
    _require(matrix.T == -matrix, "the holomorphic derivative matrix is not skew")
    return matrix


def _standard_direction(coordinate: int) -> RationalVector:
    return tuple(Fraction(index == coordinate) for index in range(MATRIX_DIMENSION - 1))


def _effective_form(
    boundary_frame: sp.Matrix, slice_columns: Sequence[int], slice_symbols: Sequence[sp.Symbol]
) -> sp.Matrix:
    form = sp.zeros(BOUNDARY_KERNEL_DIMENSION)
    for symbol, coordinate in zip(slice_symbols, slice_columns, strict=True):
        direction = _standard_direction(coordinate)
        form += symbol * (boundary_frame.T * _holomorphic_matrix(direction) * boundary_frame)
    return form.applyfunc(sp.expand)


def _upper_triangle(form: sp.Matrix) -> sp.Matrix:
    return sp.Matrix([sp.expand(form[row, column]) for row in range(form.rows) for column in range(row + 1, form.cols)])


def _independent_form_coordinates(
    effective_form: sp.Matrix, slice_symbols: Sequence[sp.Symbol]
) -> tuple[tuple[int, ...], tuple[sp.Expr, ...], sp.Matrix]:
    upper_triangle = _upper_triangle(effective_form)
    coefficient_matrix = upper_triangle.jacobian(slice_symbols)
    independent_indices = tuple(int(index) for index in coefficient_matrix.T.rref()[1])
    coordinate_forms = tuple(sp.expand(upper_triangle[index]) for index in independent_indices)
    return independent_indices, coordinate_forms, coefficient_matrix


def _singular_expression(expression: sp.Expr) -> str:
    expanded = sp.expand(expression)
    symbols = tuple(sorted(expanded.free_symbols, key=str))
    if not symbols:
        return str(expanded)
    polynomial = sp.Poly(expanded, *symbols)
    terms = []
    for exponents, coefficient in polynomial.terms():
        factors = [
            str(symbol) if exponent == 1 else f"{symbol}^{exponent}"
            for symbol, exponent in zip(symbols, exponents, strict=True)
            if exponent
        ]
        monomial = "*".join(factors)
        terms.append(f"({coefficient})" + (f"*{monomial}" if monomial else ""))
    return "+".join(terms) if terms else "0"


def _parse_singular(stdout: str, stderr: str, return_code: int) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in stdout.splitlines():
        match = re.match(r"^RESULT (\S+) (.*)$", line.strip())
        if match:
            parsed[match.group(1)] = match.group(2).strip()
    if return_code != 0 or "error" in stderr.lower() or "? " in stdout:
        parsed["singular_error"] = (stderr + stdout)[-4000:]
    return parsed


def _result_generators(result: dict[str, str], prefix: str) -> tuple[str, ...]:
    generator_count = int(result[f"{prefix}_generator_count"])
    return tuple(result[f"{prefix}_generator_{index}"] for index in range(1, generator_count + 1))


def _pfaffian_four_minors(form: sp.Matrix) -> tuple[sp.Expr, ...]:
    minors = []
    for first, second, third, fourth in itertools.combinations(range(form.rows), 4):
        minors.append(
            sp.expand(
                form[first, second] * form[third, fourth]
                - form[first, third] * form[second, fourth]
                + form[first, fourth] * form[second, third]
            )
        )
    return tuple(minors)


def _singular_script(
    incidence: Incidence,
    boundary_point: Sequence[Fraction],
    slice_columns: Sequence[int],
    slice_symbols: Sequence[sp.Symbol],
    coordinate_forms: Sequence[sp.Expr],
    pfaffian_minors: Sequence[sp.Expr],
) -> str:
    ideals = regularity.closure_ideals()
    slice_names = tuple(str(symbol) for symbol in slice_symbols)
    substitutions = tuple(
        f"({boundary_point[coordinate]}+{slice_names[slice_columns.index(coordinate)]})"
        if coordinate in slice_columns
        else str(boundary_point[coordinate])
        for coordinate in range(MATRIX_DIMENSION - 1)
    )
    zero_substitution = ",".join("0" for _symbol in slice_symbols)
    image_names = tuple(f"y{index + 1}" for index in range(len(coordinate_forms)))
    graph_generators = tuple(
        f"{name}-({_singular_expression(form)})" for name, form in zip(image_names, coordinate_forms, strict=True)
    )
    pfaffian_generators = tuple(_singular_expression(minor) for minor in pfaffian_minors)
    lines = [
        regularity.head(),
        f"ideal G = {regularity.gens_text(ideals[incidence.source_key])};",
        f"ring r1 = 0, ({','.join(slice_names)}), dp;",
        f"map phi = r, {','.join(substitutions)};",
        "list L = minAssGTZ(phi(G)); list C; int nc = 0;",
        "for (int i = 1; i <= size(L); i++) { if (size(reduce(L[i], std(maxideal(1)))) == 0) { nc++; C[nc] = L[i]; } }",
        "ideal J = C[1]; for (int i = 2; i <= nc; i++) { J = intersect(J, C[i]); }",
        f"map z0 = r1, {zero_substitution};",
        "matrix MJ = jacob(J); matrix M0 = z0(MJ);",
        '"RESULT germ_dimension", dim(std(J));',
        '"RESULT germ_embedding_dimension", nvars(r1)-rank(M0);',
        '"RESULT germ_component_count", nc;',
        f"ring r2 = 0, ({','.join((*slice_names, 'h'))}), dp;",
        f"map psi = r1, {','.join('h*' + name for name in slice_names)};",
        "setring r1; ideal X = J;",
        "setring r2; ideal Y = sat(psi(X), h); Y = subst(Y, h, 0);",
        "setring r1; ideal T = std(imap(r2, Y));",
        '"RESULT tangent_dimension", dim(T);',
        '"RESULT tangent_multiplicity", mult(T);',
        '"RESULT tangent_generator_count", size(T);',
        'for (int i = 1; i <= size(T); i++) { "RESULT tangent_generator_"+string(i), T[i]; }',
        "list TP = minAssGTZ(T);",
        '"RESULT tangent_component_count", size(TP);',
        f"ring r3 = (0,I), ({','.join((*slice_names, *image_names))}), dp;",
        "minpoly = I2+1;",
        f"map tau = r1, {','.join(slice_names)};",
        "ideal Tc = tau(T);",
        f"ideal Graph = Tc, {','.join(graph_generators)};",
        f"ideal Image = std(eliminate(std(Graph), {'*'.join(slice_names)}));",
        f'"RESULT image_dimension", dim(Image)-{len(slice_names)};',
        '"RESULT image_degree", mult(Image);',
        '"RESULT image_generator_count", size(Image);',
        'for (int i = 1; i <= size(Image); i++) { "RESULT image_generator_"+string(i), Image[i]; }',
        "list IP = minAssGTZ(Image);",
        '"RESULT image_component_count", size(IP);',
        f"ideal Degenerate = std(Graph + ideal({','.join(image_names)}));",
        '"RESULT degeneracy_dimension", dim(Degenerate);',
        '"RESULT degeneracy_degree", mult(Degenerate);',
        "list DP = minAssGTZ(Degenerate);",
        '"RESULT degeneracy_component_count", size(DP);',
        f"ideal Pfaffians = {','.join(pfaffian_generators)};",
        '"RESULT rank_four_pfaffians_vanish", size(reduce(Pfaffians, std(Tc))) == 0;',
        "quit;",
    ]
    return "\n".join(lines)


def _run_singular(script: str) -> dict[str, str]:
    try:
        process = subprocess.run(
            ["prlimit", f"--as={SINGULAR_MEMORY_LIMIT}", "Singular", "-q", "--no-warn"],
            input=script,
            capture_output=True,
            text=True,
            check=False,
            timeout=SINGULAR_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Singular exceeded the 15-minute sub-step limit") from error
    return _parse_singular(process.stdout, process.stderr, process.returncode)


def _sympy_polynomial(text: str, symbols: Sequence[sp.Symbol]) -> sp.Expr:
    local_symbols = {str(symbol): symbol for symbol in symbols}
    return sp.expand(sp.sympify(text.replace("^", "**"), locals=local_symbols))


def _normal_basis(boundary_point: Sequence[Fraction], slice_columns: Sequence[int]) -> tuple[sp.Matrix, int]:
    tangent_matrix = sp.Matrix(regularity.h_generators(boundary_point)).T
    tangent_columns = tangent_matrix.columnspace()
    slice_basis = tuple(sp.eye(MATRIX_DIMENSION - 1)[:, coordinate] for coordinate in slice_columns)
    full_basis = sp.Matrix.hstack(*tangent_columns, *slice_basis)
    _require(full_basis.shape == (MATRIX_DIMENSION - 1, MATRIX_DIMENSION - 1), "normal decomposition is not square")
    _require(full_basis.rank() == MATRIX_DIMENSION - 1, "orbit tangents and slice columns do not span")
    return full_basis, len(tangent_columns)


def _path_comparison(path: boundary.PathSpec, context: AnalysisContext) -> dict[str, Any]:
    full_basis, tangent_dimension = _normal_basis(context.boundary_point, context.slice_columns)
    direction = sp.Matrix(path.coefficients[1])
    decomposed = full_basis.inv() * direction
    normal_coordinates = tuple(sp.expand(value) for value in decomposed[tangent_dimension:, 0])
    substitutions = dict(zip(context.slice_symbols, normal_coordinates, strict=True))
    tangent_values = tuple(sp.expand(generator.subs(substitutions)) for generator in context.tangent_generators)
    direction_in_tangent_cone = all(value == 0 for value in tangent_values)
    normal_effective_form = context.effective_form.subs(substitutions).applyfunc(sp.expand)
    direct_effective_form = sp.simplify(
        context.boundary_frame.T * boundary._matrix_for_split(path.coefficients[1]) * context.boundary_frame
    )
    tangent_restriction_zero = normal_effective_form == direct_effective_form
    effective_rank = int(normal_effective_form.rank())
    curve = boundary._curve_certificate(path)
    kernel_record, retained_plane, _quotient, _boundary_frame = boundary._kernel_limit(path)
    first_order_plane_matches = None
    if effective_rank == 2:
        nullspace = normal_effective_form.nullspace()
        first_order_coordinates = sp.Matrix.hstack(*nullspace)
        first_order_plane = context.boundary_frame * first_order_coordinates
        first_order_plane_matches = (
            sp.Matrix.hstack(first_order_plane, retained_plane).rank() == LIMITING_KERNEL_DIMENSION
        )
    passed = (
        bool(curve["pass"])
        and direction_in_tangent_cone
        and tangent_restriction_zero
        and effective_rank in (0, 2)
        and (first_order_plane_matches is not False)
        and bool(kernel_record["pass"])
    )
    return {
        "approach": path.approach,
        "normal_coordinates": list(map(str, normal_coordinates)),
        "tangent_generator_values": list(map(str, tangent_values)),
        "direction_in_tangent_cone": direction_in_tangent_cone,
        "curve_containment_verified": curve["closure_containment_proved"],
        "curve_certificate_pass": curve["pass"],
        "tangent_component_restricts_to_zero": tangent_restriction_zero,
        "first_order_effective_rank": effective_rank,
        "higher_order_required": effective_rank == 0,
        "retained_leading_order": kernel_record["effective_leading_order"],
        "first_order_plane_matches_retained_limit": first_order_plane_matches,
        "pass": passed,
    }


def _mutated_path(path: boundary.PathSpec) -> boundary.PathSpec:
    first_order = list(path.coefficients[1])
    first_order[7] += 1
    return boundary.PathSpec(
        path.high_orbit,
        path.boundary_orbit,
        f"{path.approach}-middle-coordinate-mutation",
        (path.coefficients[0], tuple(first_order), path.coefficients[2]),
    )


def _mutation_control(paths: Sequence[boundary.PathSpec], context: AnalysisContext) -> dict[str, Any] | None:
    if context.incidence.name != "W8->B9":
        return None
    baseline_path = paths[0]
    comparison_tasks = (baseline_path, _mutated_path(baseline_path))
    comparisons = parallel.ordered_map(partial(_path_comparison, context=context), comparison_tasks, min_items=1)
    baseline, mutated = comparisons
    detected = (
        bool(baseline["pass"])
        and not bool(mutated["pass"])
        and bool(baseline["direction_in_tangent_cone"])
        and not bool(mutated["direction_in_tangent_cone"])
        and bool(baseline["curve_containment_verified"])
        and not bool(mutated["curve_containment_verified"])
    )
    return {
        "name": "add_middle_coordinate_to_W8_path",
        "target": context.incidence.name,
        "input_change": "add the split middle-coordinate basis vector to the exact first-order path coefficient",
        "baseline": baseline,
        "mutated": mutated,
        "detected": detected,
    }


def _analyze_incidence(incidence: Incidence) -> dict[str, Any]:
    boundary_point, canonical_paths = basepoints.selected_path_group(
        basepoints.Incidence(incidence.source_orbit, incidence.boundary_orbit)
    )
    slice_columns = tuple(
        regularity.transverse_columns(
            boundary_point, regularity.COLUMN_ORDER.get(incidence.boundary_key, range(MATRIX_DIMENSION - 1))
        )
    )
    slice_symbols = tuple(sp.symbols(f"t1:{len(slice_columns) + 1}"))
    boundary_matrix = boundary._matrix_for_split(boundary_point)
    pivot = kernel_frames._find_principal_pivot(boundary_matrix, BOUNDARY_MATRIX_RANK)
    boundary_frame, _determinant, _pfaffian = kernel_frames._principal_frame(boundary_matrix, pivot)
    effective_form = _effective_form(boundary_frame, slice_columns, slice_symbols)
    independent_indices, coordinate_forms, coefficient_matrix = _independent_form_coordinates(
        effective_form, slice_symbols
    )
    singular_result = _run_singular(
        _singular_script(
            incidence,
            boundary_point,
            slice_columns,
            slice_symbols,
            coordinate_forms,
            _pfaffian_four_minors(effective_form),
        )
    )
    _require(
        "singular_error" not in singular_result,
        f"Singular failed on {incidence.name}: {singular_result.get('singular_error')}",
    )
    tangent_generator_text = _result_generators(singular_result, "tangent")
    tangent_generators = tuple(_sympy_polynomial(text, slice_symbols) for text in tangent_generator_text)
    image_generators = _result_generators(singular_result, "image")
    expected_germ = regularity.EXPECTED_GERMS[(incidence.source_key, incidence.boundary_key)]
    observed_germ = (
        int(singular_result["germ_dimension"]),
        int(singular_result["tangent_multiplicity"]),
        int(singular_result["germ_embedding_dimension"]),
        int(singular_result["germ_component_count"]),
    )
    expected_germ_projection = (expected_germ[0], expected_germ[1], expected_germ[2], expected_germ[4])
    context = AnalysisContext(
        incidence,
        boundary_point,
        slice_columns,
        slice_symbols,
        boundary_frame,
        effective_form,
        tangent_generators,
    )
    _require(bool(canonical_paths), f"{incidence.name} has no retained path at the selected boundary point")
    path_rows = parallel.ordered_map(partial(_path_comparison, context=context), canonical_paths, min_items=1)
    mutation_control = _mutation_control(canonical_paths, context)
    image_dimension = int(singular_result["image_dimension"])
    degeneracy_dimension = int(singular_result["degeneracy_dimension"])
    tangent_dimension = int(singular_result["tangent_dimension"])
    identically_zero_on_tangent_cone = image_dimension == 0 and degeneracy_dimension == tangent_dimension
    image_consistent = image_dimension > 0 or (
        identically_zero_on_tangent_cone and all(int(row["first_order_effective_rank"]) == 0 for row in path_rows)
    )
    passed = (
        observed_germ == expected_germ_projection
        and tangent_dimension == expected_germ[0]
        and singular_result["rank_four_pfaffians_vanish"] == "1"
        and image_consistent
        and all(bool(row["pass"]) for row in path_rows)
        and (mutation_control is None or bool(mutation_control["detected"]))
    )
    return {
        "incidence": incidence.name,
        "source_orbit": incidence.source_orbit,
        "boundary_orbit": incidence.boundary_orbit,
        "boundary_point": list(map(str, boundary_point)),
        "slice_columns_zero_based": list(slice_columns),
        "slice_dimension": len(slice_columns),
        "germ": {
            "observed_dimension_multiplicity_embedding_components": list(observed_germ),
            "expected_dimension_multiplicity_embedding_components": list(expected_germ_projection),
            "matches_regularity_record": observed_germ == expected_germ_projection,
        },
        "tangent_cone": {
            "dimension": tangent_dimension,
            "multiplicity": int(singular_result["tangent_multiplicity"]),
            "component_count": int(singular_result["tangent_component_count"]),
            "generators": list(tangent_generator_text),
        },
        "effective_form": {
            "ambient_linear_rank": int(coefficient_matrix.rank()),
            "independent_upper_triangle_indices": list(independent_indices),
            "coordinate_forms": list(map(str, coordinate_forms)),
            "rank_four_pfaffians_vanish_on_tangent_cone": singular_result["rank_four_pfaffians_vanish"] == "1",
        },
        "first_order_image": {
            "affine_dimension": image_dimension,
            "projective_dimension": image_dimension - 1,
            "degree": int(singular_result["image_degree"]),
            "component_count": int(singular_result["image_component_count"]),
            "generators_in_independent_form_coordinates": list(image_generators),
            "identically_zero_on_tangent_cone": identically_zero_on_tangent_cone,
            "outcome_consistent_with_retained_paths": image_consistent,
        },
        "degeneracy_locus": {
            "affine_dimension": degeneracy_dimension,
            "projective_dimension": degeneracy_dimension - 1 if degeneracy_dimension > 0 else -1,
            "degree": int(singular_result["degeneracy_degree"]),
            "component_count": int(singular_result["degeneracy_component_count"]),
            "one_blowup_resolves_first_order_map": degeneracy_dimension == 0,
        },
        "canonical_paths": path_rows,
        "mutation_control": mutation_control,
        "pass": passed,
    }


def _singular_version() -> str:
    process = subprocess.run(
        ["prlimit", f"--as={SINGULAR_MEMORY_LIMIT}", "Singular", "--version"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    _require(process.returncode == 0, "Singular --version failed")
    return process.stdout.splitlines()[0]


def build_record() -> dict[str, Any]:
    incidences = _incidences()
    rows = parallel.ordered_map(_analyze_incidence, incidences, min_items=1)
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    mutation_controls = tuple(row["mutation_control"] for row in rows if row["mutation_control"] is not None)
    one_blowup_count = sum(bool(row["degeneracy_locus"]["one_blowup_resolves_first_order_map"]) for row in rows)
    zero_image_count = sum(bool(row["first_order_image"]["identically_zero_on_tangent_cone"]) for row in rows)
    exceptional_count = len(rows) - one_blowup_count
    passed = (
        all(bool(row["pass"]) for row in rows)
        and bool(mutation_controls)
        and all(bool(control["detected"]) for control in mutation_controls)
    )
    return {
        "schema": SCHEMA,
        "inputs": dict(input_rows),
        "tools": {"singular": _singular_version(), "sympy": sp.__version__},
        "scope": {
            "passage": "nullity 8 to nullity 12",
            "claim_boundary": (
                "The record computes the complex-algebraic projective image of the first-order tangent cone and "
                "locates directions where that map vanishes. It is an exact upper bound on first-order limits, not "
                "a two-sided real semialgebraic certificate for the full Gauss-graph fiber."
            ),
        },
        "summary": {
            "incidence_count": len(rows),
            "one_blowup_resolves_count": one_blowup_count,
            "higher_order_required_count": exceptional_count,
            "identically_zero_first_order_count": zero_image_count,
        },
        "incidences": rows,
        "mutation_controls": list(mutation_controls),
        "falsifier": (
            "A transverse slice fails to complement the boundary orbit; a germ invariant disagrees with the "
            "regularity record; a retained exact path misses the tangent cone or effective-form image; a "
            "nondegenerate direction has rank other than two; a first-order plane differs from its retained exact "
            "limit; a rank-four Pfaffian survives; or the geometric-input mutation survives."
        ),
        "pass": passed,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the first-order normal-cone record failed")
    _require(all(bool(row["pass"]) for row in record["incidences"]), "an incidence row failed")
    _require(all(bool(row["detected"]) for row in record["mutation_controls"]), "a mutation survived")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    selected_modes = sum((arguments.out is not None, arguments.check is not None, arguments.self_test))
    if selected_modes != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        retained = arguments.check.read_bytes()
        _require(
            retained == rendered,
            f"record mismatch: retained={hashlib.sha256(retained).hexdigest()} "
            f"fresh={hashlib.sha256(rendered).hexdigest()}",
        )


if __name__ == "__main__":
    main()
