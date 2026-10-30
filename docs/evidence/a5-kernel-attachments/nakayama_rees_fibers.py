"""Nakayama-reduced Rees fibers for six higher-order A_5 incidences."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any, TypeAlias, cast

import flint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import holomorphic_gauss_fibers as resolved  # noqa: E402
import strata_regularity as regularity  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-nakayama-rees-fibers-v1"
FIRST_ORDER_RESULT = HERE / "first-order-normal-cones-result.json"
SCHUR_WITNESS_RESULT = HERE / "schur-degeneracy-witnesses-result.json"
RESULT_PATH = HERE / "nakayama-rees-fibers-result.json"
SOURCE_PATHS = (
    HERE / "nakayama_rees_fibers.py",
    HERE / "holomorphic_gauss_fibers.py",
    HERE / "holomorphic_kernel_lemma.py",
    REGULARITY / "strata_regularity.py",
    EQUATIONS / "rederive_strata_equations.py",
    FIRST_ORDER_RESULT,
    SCHUR_WITNESS_RESULT,
    ROOT / "gororoba_quantum" / "cd_core.py",
    ROOT / "gororoba_quantum" / "parallel.py",
)
INCIDENCES = (
    "X+->VB",
    "X-->VB",
    "Iso->VB",
    "W8->VB",
    "E8bar->Va+",
    "E8bar->Va-",
)
SOURCE_KEYS = {"E8bar": "Ehat", "X+": "Xp", "X-": "Xm"}
EXPECTED_GENERATOR_COUNTS = {
    "X+->VB": 3,
    "X-->VB": 3,
    "Iso->VB": 4,
    "W8->VB": 5,
    "E8bar->Va+": 6,
    "E8bar->Va-": 6,
}
EXPECTED_FIBERS = {
    "X+->VB": (2, 1, 1),
    "X-->VB": (2, 1, 1),
    "Iso->VB": (3, 1, 1),
    "W8->VB": (4, 1, 1),
    "E8bar->Va+": (2, 2, 2),
    "E8bar->Va-": (2, 2, 2),
}
MODULAR_PRIME = 32003
SINGULAR_MEMORY_LIMIT = "4294967296"
SINGULAR_TIMEOUT_SECONDS = 300

Gaussian = resolved.Gaussian
GaussianMatrix = resolved.GaussianMatrix
GaussianVector = resolved.kernel_lemma.GaussianVector
ModGaussian: TypeAlias = tuple[int, int]


@dataclass(frozen=True)
class RowTask:
    row: dict[str, Any]
    witnesses: tuple[dict[str, Any], ...]
    closure_generators: tuple[str, ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"{path.name} does not hold a JSON object")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(path: Path) -> tuple[str, str]:
    return str(path.relative_to(ROOT)), _sha256(path)


def _field(characteristic: int) -> str:
    return f"({characteristic},I)" if characteristic else "(0,I)"


def _parse_singular(stdout: str, stderr: str, return_code: int) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in stdout.splitlines():
        match = re.match(r"^RESULT (\S+) (.*)$", line.strip())
        if match is not None:
            parsed[match.group(1)] = match.group(2).strip()
    if return_code != 0 or "error" in stderr.lower() or "? " in stdout:
        parsed["singular_error"] = (stderr + stdout)[-6000:]
    return parsed


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
        raise RuntimeError("Singular exceeded the 300-second formulation-error gate") from error
    result = _parse_singular(process.stdout, process.stderr, process.returncode)
    _require("singular_error" not in result, result.get("singular_error", "Singular failed"))
    return result


def _parse_gaussian(text: str) -> Gaussian:
    compact = text.replace(" ", "").replace("*", "").replace("(", "").replace(")", "")
    terms = re.findall(r"[+-]?[^+-]+", compact)
    real = Fraction(0)
    imaginary = Fraction(0)
    for term in terms:
        if "I" not in term:
            real += Fraction(term)
            continue
        coefficient = term.replace("I", "")
        if coefficient in ("", "+"):
            coefficient = "1"
        elif coefficient == "-":
            coefficient = "-1"
        elif coefficient.startswith("/"):
            coefficient = "1" + coefficient
        elif coefficient.startswith("-/"):
            coefficient = "-1" + coefficient[1:]
        imaginary += Fraction(coefficient)
    return real, imaginary


def _gaussian_expression(value: Gaussian) -> str:
    return f"({value[0]})+(I)*({value[1]})"


def _mod_expression(value: ModGaussian) -> str:
    return f"({value[0]})+(I)*({value[1]})"


def _gaussian_record(value: Gaussian) -> list[str]:
    return [str(value[0]), str(value[1])]


def _fraction_mod(value: Fraction) -> int:
    return (value.numerator * pow(value.denominator, -1, MODULAR_PRIME)) % MODULAR_PRIME


def _gaussian_mod(value: Gaussian) -> ModGaussian:
    return _fraction_mod(value[0]), _fraction_mod(value[1])


def _parse_mod_gaussian(text: str) -> ModGaussian:
    value = _parse_gaussian(text)
    return _gaussian_mod(value)


def _mod_add(left: ModGaussian, right: ModGaussian) -> ModGaussian:
    return (left[0] + right[0]) % MODULAR_PRIME, (left[1] + right[1]) % MODULAR_PRIME


def _mod_subtract(left: ModGaussian, right: ModGaussian) -> ModGaussian:
    return (left[0] - right[0]) % MODULAR_PRIME, (left[1] - right[1]) % MODULAR_PRIME


def _mod_multiply(left: ModGaussian, right: ModGaussian) -> ModGaussian:
    return (
        (left[0] * right[0] - left[1] * right[1]) % MODULAR_PRIME,
        (left[0] * right[1] + left[1] * right[0]) % MODULAR_PRIME,
    )


def _mod_inverse(value: ModGaussian) -> ModGaussian:
    denominator = (value[0] * value[0] + value[1] * value[1]) % MODULAR_PRIME
    _require(denominator != 0, "modular Gaussian pivot is zero")
    inverse = pow(denominator, -1, MODULAR_PRIME)
    return value[0] * inverse % MODULAR_PRIME, -value[1] * inverse % MODULAR_PRIME


def _mod_rref(
    matrix: tuple[tuple[ModGaussian, ...], ...],
) -> tuple[tuple[tuple[ModGaussian, ...], ...], tuple[int, ...]]:
    rows = [list(row) for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0]) if rows else 0
    pivot_row = 0
    pivot_columns: list[int] = []
    zero = (0, 0)
    for column in range(column_count):
        selected = next((row for row in range(pivot_row, row_count) if rows[row][column] != zero), None)
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        inverse = _mod_inverse(rows[pivot_row][column])
        rows[pivot_row] = [_mod_multiply(value, inverse) for value in rows[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or rows[row][column] == zero:
                continue
            factor = rows[row][column]
            rows[row] = [
                _mod_subtract(value, _mod_multiply(factor, pivot_value))
                for value, pivot_value in zip(rows[row], rows[pivot_row], strict=True)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return tuple(tuple(row) for row in rows), tuple(pivot_columns)


def _slice_variable_index(value: str) -> int:
    return int(value[1:])


def _solve_gaussian(columns: tuple[GaussianVector, ...], target: GaussianVector) -> GaussianVector | None:
    augmented = tuple((*row, target[row_index]) for row_index, row in enumerate(zip(*columns, strict=True)))
    reduced, pivots = resolved.kernel_lemma._rref(augmented)
    width = len(columns)
    if width in pivots or pivots[:width] != tuple(range(width)):
        return None
    return tuple(reduced[row][-1] for row in range(width))


def _solve_modular(
    columns: tuple[tuple[ModGaussian, ...], ...], target: tuple[ModGaussian, ...]
) -> tuple[ModGaussian, ...] | None:
    augmented = tuple((*row, target[row_index]) for row_index, row in enumerate(zip(*columns, strict=True)))
    reduced, pivots = _mod_rref(augmented)
    width = len(columns)
    if width in pivots or pivots[:width] != tuple(range(width)):
        return None
    return tuple(reduced[row][-1] for row in range(width))


def _univariate_multiply(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    product: dict[int, Fraction] = {}
    for left_degree, left_value in left.items():
        for right_degree, right_value in right.items():
            degree = left_degree + right_degree
            product[degree] = product.get(degree, Fraction(0)) + left_value * right_value
    return {degree: value for degree, value in product.items() if value != 0}


def _evaluate_component(
    polynomial: Any, first: tuple[Fraction, ...], second: tuple[Fraction, ...]
) -> dict[int, Fraction]:
    values: dict[int, Fraction] = {}
    for exponents, coefficient in polynomial.to_dict().items():
        term = {0: Fraction(int(coefficient.p), int(coefficient.q))}
        for variable_index, exponent in enumerate(exponents):
            factor = {1: first[variable_index], 2: second[variable_index]}
            factor = {degree: value for degree, value in factor.items() if value != 0}
            for _power in range(exponent):
                term = _univariate_multiply(term, factor)
        for degree, value in term.items():
            values[degree] = values.get(degree, Fraction(0)) + value
    return {degree: value for degree, value in values.items() if value != 0}


def _skew_matrix(coordinates: GaussianVector) -> GaussianMatrix:
    size = resolved.BOUNDARY_C_KERNEL_DIMENSION
    rows = [[resolved.kernel_lemma.ZERO for _column in range(size)] for _row in range(size)]
    coordinate_index = 0
    for row in range(size):
        for column in range(row + 1, size):
            value = coordinates[coordinate_index]
            rows[row][column] = value
            rows[column][row] = resolved.kernel_lemma._gaussian_negate(value)
            coordinate_index += 1
    return tuple(tuple(row) for row in rows)


def _arc_coordinates(data: Any, row: dict[str, Any], witness: dict[str, Any]) -> dict[str, Any]:
    first_split = tuple(Fraction(value) for value in witness["first_order_split_coefficients"])
    second_split = tuple(Fraction(value) for value in witness["second_order_split_coefficients"])
    boundary_point = tuple(Fraction(value) for value in row["boundary_point"])
    boundary_z = resolved.kernel_lemma._original_z_from_split(boundary_point)
    first_z = resolved.kernel_lemma._original_z_from_split(first_split)
    second_z = resolved.kernel_lemma._original_z_from_split(second_split)
    boundary_c = resolved.kernel_lemma._c_matrix(boundary_z)
    first_c = resolved.kernel_lemma._c_matrix(first_z)
    second_c = resolved.kernel_lemma._c_matrix(second_z)
    _pivot, c_frame, complement = resolved._principal_frame(boundary_c, resolved.BOUNDARY_C_RANK)
    transformation = resolved._transformation_matrix(complement, c_frame)
    transformed_boundary = resolved._numeric_congruence(boundary_c, transformation)
    transformed_first = resolved._numeric_congruence(first_c, transformation)
    transformed_second = resolved._numeric_congruence(second_c, transformation)
    pivot_range = range(resolved.BOUNDARY_C_RANK)
    kernel_range = range(resolved.BOUNDARY_C_RANK, resolved.COMPLEX_DIMENSION)
    pivot_block = resolved._numeric_extract(transformed_boundary, pivot_range, pivot_range)
    first_coupling = resolved._numeric_extract(transformed_first, pivot_range, kernel_range)
    first_restriction = resolved._numeric_extract(transformed_first, kernel_range, kernel_range)
    second_restriction = resolved._numeric_extract(transformed_second, kernel_range, kernel_range)
    _require(
        all(value == resolved.kernel_lemma.ZERO for matrix_row in first_restriction for value in matrix_row),
        f"{row['incidence']} {witness['approach']} has a nonzero first Schur restriction",
    )
    correction = resolved._numeric_matrix_multiply(
        resolved._numeric_matrix_multiply(
            resolved._numeric_transpose(first_coupling), resolved._numeric_inverse(pivot_block)
        ),
        first_coupling,
    )
    effective_form = tuple(
        tuple(
            resolved.kernel_lemma._gaussian_add(
                second_restriction[row_index][column_index], correction[row_index][column_index]
            )
            for column_index in range(resolved.BOUNDARY_C_KERNEL_DIMENSION)
        )
        for row_index in range(resolved.BOUNDARY_C_KERNEL_DIMENSION)
    )
    coordinates = tuple(
        resolved.kernel_lemma._gaussian_multiply(data.pivot_pfaffian_at_origin, effective_form[row_index][column_index])
        for row_index in range(resolved.BOUNDARY_C_KERNEL_DIMENSION)
        for column_index in range(row_index + 1, resolved.BOUNDARY_C_KERNEL_DIMENSION)
    )
    _require(any(value != resolved.kernel_lemma.ZERO for value in coordinates), "arc point is projectively zero")

    z_coordinates = resolved._solve_frame_coordinates(
        c_frame,
        tuple((value,) for value in boundary_z),
    )
    committed_plane_rows = tuple(
        tuple(_parse_gaussian(str(value)) for value in plane_row)
        for plane_row in witness["schur"]["limiting_plane_rref"]
    )
    lower_plane = tuple(
        tuple(committed_plane_rows[column][row + 1] for column in range(len(committed_plane_rows)))
        for row in range(resolved.COMPLEX_DIMENSION)
    )
    plane_coordinates = resolved._solve_frame_coordinates(c_frame, lower_plane)
    committed_holomorphic_columns = (
        tuple(row_values[0] for row_values in z_coordinates),
        *(tuple(row_values[column] for row_values in plane_coordinates) for column in range(4)),
    )
    schur_kernel = resolved.kernel_lemma._nullspace(_skew_matrix(coordinates))
    matches = resolved.kernel_lemma._spans_equal(schur_kernel, committed_holomorphic_columns)
    _require(matches, f"{row['incidence']} {witness['approach']} holomorphic limit plane changed")
    return {
        "approach": witness["approach"],
        "coordinate_order": 2,
        "coordinates": coordinates,
        "holomorphic_kernel_matches_committed_plane_plus_boundary_line": matches,
    }


def _germ_substitutions(row: dict[str, Any]) -> tuple[str, ...]:
    boundary = tuple(Fraction(value) for value in row["boundary_point"])
    slice_columns = tuple(int(value) for value in row["slice_columns_zero_based"])
    return tuple(
        f"({boundary[index]}+t{slice_columns.index(index) + 1})" if index in slice_columns else str(boundary[index])
        for index in range(resolved.COMPLEX_DIMENSION)
    )


def _phase_one_script(characteristic: int, task: RowTask, data: Any) -> str:
    row = task.row
    slice_names = data.slice_names
    global_names = regularity.GLOBAL_VARS
    coordinate_text = ",".join(resolved._singular_expression(value) for value in data.coordinates)
    lines = [
        'LIB "primdec.lib";',
        'LIB "presolve.lib";',
        'LIB "sing.lib";',
        f"ring r={_field(characteristic)},({','.join(global_names)}),dp;",
        "minpoly=I2+1;",
        f"ideal Closure={','.join(task.closure_generators)};",
        f"ring s={_field(characteristic)},({','.join(slice_names)}),dp;",
        "minpoly=I2+1;",
        f"map sliceMap=r,{','.join(_germ_substitutions(row))};",
        "list LocalPrimes=minAssGTZ(sliceMap(Closure)); list ThroughOrigin; int componentCount=0;",
        "for(int i=1;i<=size(LocalPrimes);i++){"
        "if(size(reduce(LocalPrimes[i],std(maxideal(1))))==0){componentCount++;ThroughOrigin[componentCount]=LocalPrimes[i];}}",
        "ideal J=ThroughOrigin[1];",
        "for(int i=2;i<=componentCount;i++){J=intersect(J,ThroughOrigin[i]);}",
        "J=std(J);",
        f"ideal F={coordinate_text};",
        "ideal maximal=maxideal(1);",
        "ideal SJ=std(J+maximal*F);",
        "ideal NormalForms,G; intvec Selected; int selectedCount=0; poly candidate; int independent;",
        "for(int i=1;i<=size(F);i++){candidate=reduce(F[i],SJ);if(candidate!=0){independent=1;"
        "if(selectedCount>0 && reduce(candidate,std(NormalForms))==0){independent=0;}"
        "if(independent){selectedCount++;NormalForms[selectedCount]=candidate;G[selectedCount]=F[i];"
        "Selected[selectedCount]=i;}}}",
        "list EP=elimpart(J); map reducedMap=s,EP[5];",
        "ideal ReducedJ=std(reducedMap(J));",
        "ideal ReducedG=simplify(reduce(reducedMap(G),ReducedJ),2);",
        "ideal Prefix=J+maximal*F; int generatorOffset=size(Prefix); ideal LiftBasis=Prefix+G;",
        "matrix LiftMatrix=lift(LiftBasis,F); matrix A[selectedCount][21];",
        "for(int i=1;i<=selectedCount;i++){for(int j=1;j<=21;j++){A[i,j]=jet(LiftMatrix[generatorOffset+i,j],0);}}",
        '"RESULT germ_dimension",dim(J);',
        '"RESULT germ_component_count",componentCount;',
        '"RESULT selected_count",selectedCount;',
        'for(int i=1;i<=selectedCount;i++){"RESULT selected_"+string(i),Selected[i];}',
        "int eliminatedCount=0;for(int i=1;i<=size(EP[2]);i++){if(EP[2][i]!=0){eliminatedCount++;"
        '"RESULT eliminated_"+string(eliminatedCount),EP[2][i];}}',
        '"RESULT eliminated_count",eliminatedCount;',
        "int remainingCount=0;for(int i=1;i<=size(EP[4]);i++){if(EP[4][i]!=0){remainingCount++;"
        '"RESULT remaining_"+string(remainingCount),EP[4][i];}}',
        '"RESULT remaining_count",remainingCount;',
        '"RESULT reduced_j_count",size(ReducedJ);',
        'for(int i=1;i<=size(ReducedJ);i++){"RESULT reduced_j_"+string(i),ReducedJ[i];}',
        '"RESULT reduced_g_count",size(ReducedG);',
        'for(int i=1;i<=size(ReducedG);i++){"RESULT reduced_g_"+string(i),ReducedG[i];}',
        '"RESULT embedding_rank",rank(A);',
        "for(int i=1;i<=selectedCount;i++){for(int j=1;j<=21;j++){"
        '"RESULT embedding_"+string(i)+"_"+string(j),A[i,j];}}',
        "quit;",
    ]
    return "\n".join(lines)


def _phase_one_summary(result: dict[str, str]) -> dict[str, Any]:
    selected_count = int(result["selected_count"])
    eliminated_count = int(result["eliminated_count"])
    reduced_j_count = int(result["reduced_j_count"])
    reduced_g_count = int(result["reduced_g_count"])
    reduced_j = [result[f"reduced_j_{index}"] for index in range(1, reduced_j_count + 1)]
    reduced_g = [result[f"reduced_g_{index}"] for index in range(1, reduced_g_count + 1)]
    reduced_variables = {
        variable for polynomial in (*reduced_j, *reduced_g) for variable in re.findall(r"\bt\d+\b", polynomial)
    }
    return {
        "germ_dimension": int(result["germ_dimension"]),
        "germ_component_count": int(result["germ_component_count"]),
        "selected_count": selected_count,
        "selected_indices_one_based": [int(result[f"selected_{index}"]) for index in range(1, selected_count + 1)],
        "eliminated_variables": [result[f"eliminated_{index}"] for index in range(1, eliminated_count + 1)],
        "remaining_variables": sorted(reduced_variables, key=_slice_variable_index),
        "reduced_j": reduced_j,
        "reduced_g": reduced_g,
        "embedding_rank": int(result["embedding_rank"]),
        "embedding_rows": [
            [result[f"embedding_{row}_{column}"] for column in range(1, 22)] for row in range(1, selected_count + 1)
        ],
    }


def _phase_two_script(
    characteristic: int,
    phase_one: dict[str, Any],
    arc_preimages: tuple[tuple[str, ...], ...],
) -> str:
    remaining = tuple(str(value) for value in phase_one["remaining_variables"])
    reduced_j = tuple(str(value) for value in phase_one["reduced_j"])
    reduced_g = tuple(str(value) for value in phase_one["reduced_g"])
    target_names = tuple(f"y{index + 1}" for index in range(len(reduced_g)))
    variables = ("a", *remaining, *target_names)
    lines = [
        'LIB "primdec.lib";',
        'LIB "elim.lib";',
        f"ring R={_field(characteristic)},({','.join(variables)}),dp;",
        "minpoly=I2+1;",
        f"ideal J={','.join(reduced_j) if reduced_j else '0'};",
        f"ideal G={','.join(reduced_g) if reduced_g else '0'};",
        "ideal Graph=J;",
    ]
    for index, target_name in enumerate(target_names, start=1):
        lines.append(f"Graph=Graph,({target_name}-a*G[{index}]);")
    lines.extend(("ideal Rees=eliminate(std(Graph),a);", "ideal Fiber=Rees;"))
    for variable in remaining:
        lines.append(f"Fiber=subst(Fiber,{variable},0);")
    lines.extend(
        (
            f"ideal Target={','.join(target_names)};",
            "Fiber=std(sat(Fiber,Target));",
            "list Components=minAssGTZ(Fiber);",
            f'"RESULT image_projective_dimension",dim(Fiber)-{len(remaining) + 2};',
            '"RESULT image_degree",mult(Fiber);',
            '"RESULT component_count",size(Components);',
            "for(int c=1;c<=size(Components);c++){ideal Component=simplify(Components[c],2);",
            f'"RESULT component_"+string(c)+"_projective_dimension",dim(Component)-{len(remaining) + 2};',
            '"RESULT component_"+string(c)+"_degree",mult(Component);',
            '"RESULT component_"+string(c)+"_generator_count",size(Component);',
            'for(int g=1;g<=size(Component);g++){"RESULT component_"+string(c)+"_generator_"+string(g),Component[g];}}',
        )
    )
    for arc_index, preimage in enumerate(arc_preimages, start=1):
        lines.append(f"ideal ArcFiber{arc_index}=Fiber;")
        for name, value in zip(target_names, preimage, strict=True):
            lines.append(f"ArcFiber{arc_index}=subst(ArcFiber{arc_index},{name},{value});")
        lines.append(f'"RESULT arc_{arc_index}_in_fiber",size(simplify(ArcFiber{arc_index},2))==0;')
        lines.append("for(int c=1;c<=size(Components);c++){ideal ArcComponent=Components[c];")
        for name, value in zip(target_names, preimage, strict=True):
            lines.append(f"ArcComponent=subst(ArcComponent,{name},{value});")
        lines.append(f'"RESULT arc_{arc_index}_component_"+string(c),size(simplify(ArcComponent,2))==0;}}')
    lines.append("quit;")
    return "\n".join(lines)


def _phase_two_summary(result: dict[str, str], arc_count: int) -> dict[str, Any]:
    component_count = int(result["component_count"])
    components: list[dict[str, Any]] = []
    for component_index in range(1, component_count + 1):
        generator_count = int(result[f"component_{component_index}_generator_count"])
        components.append(
            {
                "projective_dimension": int(result[f"component_{component_index}_projective_dimension"]),
                "degree": int(result[f"component_{component_index}_degree"]),
                "generators": [
                    result[f"component_{component_index}_generator_{generator_index}"]
                    for generator_index in range(1, generator_count + 1)
                ],
            }
        )
    arcs = [
        {
            "in_fiber": result[f"arc_{arc_index}_in_fiber"] == "1",
            "component_indices_one_based": [
                component_index
                for component_index in range(1, component_count + 1)
                if result[f"arc_{arc_index}_component_{component_index}"] == "1"
            ],
        }
        for arc_index in range(1, arc_count + 1)
    ]
    return {
        "image_projective_dimension": int(result["image_projective_dimension"]),
        "image_degree": int(result["image_degree"]),
        "component_count": component_count,
        "components": components,
        "arcs": arcs,
    }


def _rational_columns(phase_one: dict[str, Any]) -> tuple[GaussianVector, ...]:
    return tuple(
        tuple(_parse_gaussian(value) for value in row) for row in cast(list[list[str]], phase_one["embedding_rows"])
    )


def _modular_columns(phase_one: dict[str, Any]) -> tuple[tuple[ModGaussian, ...], ...]:
    return tuple(
        tuple(_parse_mod_gaussian(value) for value in row) for row in cast(list[list[str]], phase_one["embedding_rows"])
    )


def _standard_negative_control(
    rational_columns: tuple[GaussianVector, ...],
    modular_columns: tuple[tuple[ModGaussian, ...], ...],
) -> int:
    for coordinate_index in range(21):
        rational_target = tuple(
            resolved.kernel_lemma.ONE if index == coordinate_index else resolved.kernel_lemma.ZERO
            for index in range(21)
        )
        modular_target = tuple((1, 0) if index == coordinate_index else (0, 0) for index in range(21))
        if (
            _solve_gaussian(rational_columns, rational_target) is None
            and _solve_modular(modular_columns, modular_target) is None
        ):
            return coordinate_index
    raise RuntimeError("every standard projective control point lies in the embedding image")


def _fiber_tuple(summary: dict[str, Any]) -> tuple[int, int, int, tuple[tuple[int, int], ...]]:
    components = tuple(sorted((int(row["projective_dimension"]), int(row["degree"])) for row in summary["components"]))
    return (
        int(summary["image_projective_dimension"]),
        int(summary["image_degree"]),
        int(summary["component_count"]),
        components,
    )


def _drop_required_generator(
    rational_columns: tuple[GaussianVector, ...], arc_targets: tuple[GaussianVector, ...]
) -> int:
    for generator_index in range(len(rational_columns)):
        reduced_columns = tuple(column for index, column in enumerate(rational_columns) if index != generator_index)
        if any(_solve_gaussian(reduced_columns, target) is None for target in arc_targets):
            return generator_index
    raise RuntimeError("every arc survives every Nakayama-generator deletion")


def _mutated_phase_one(phase_one: dict[str, Any], dropped_index: int) -> dict[str, Any]:
    updated = dict(phase_one)
    updated["reduced_g"] = [
        value for index, value in enumerate(cast(list[str], phase_one["reduced_g"])) if index != dropped_index
    ]
    return updated


def _analyze_row(task: RowTask) -> dict[str, Any]:
    resolved._cap_worker_memory()
    row = task.row
    incidence = str(row["incidence"])
    data = resolved._schur_polynomials(resolved.IncidenceTask(row))
    arc_rows = tuple(_arc_coordinates(data, row, witness) for witness in task.witnesses)
    arc_targets = tuple(cast(GaussianVector, arc["coordinates"]) for arc in arc_rows)

    modular_phase_one = _phase_one_summary(_run_singular(_phase_one_script(MODULAR_PRIME, task, data)))
    _require(
        modular_phase_one["selected_count"] == EXPECTED_GENERATOR_COUNTS[incidence],
        f"{incidence} modular Nakayama count changed",
    )
    modular_columns = _modular_columns(modular_phase_one)
    modular_preimages = tuple(
        _solve_modular(modular_columns, tuple(map(_gaussian_mod, target))) for target in arc_targets
    )
    _require(all(value is not None for value in modular_preimages), f"{incidence} modular arc left the column span")
    modular_expressions = tuple(
        tuple(_mod_expression(value) for value in cast(tuple[ModGaussian, ...], preimage))
        for preimage in modular_preimages
    )
    modular_fiber = _phase_two_summary(
        _run_singular(_phase_two_script(MODULAR_PRIME, modular_phase_one, modular_expressions)),
        len(arc_rows),
    )

    rational_phase_one = _phase_one_summary(_run_singular(_phase_one_script(0, task, data)))
    _require(
        rational_phase_one["selected_indices_one_based"] == modular_phase_one["selected_indices_one_based"],
        f"{incidence} Nakayama selections differ by characteristic",
    )
    rational_columns = _rational_columns(rational_phase_one)
    rational_preimages = tuple(_solve_gaussian(rational_columns, target) for target in arc_targets)
    _require(all(value is not None for value in rational_preimages), f"{incidence} rational arc left the column span")
    rational_expressions = tuple(
        tuple(_gaussian_expression(value) for value in cast(GaussianVector, preimage))
        for preimage in rational_preimages
    )
    rational_fiber = _phase_two_summary(
        _run_singular(_phase_two_script(0, rational_phase_one, rational_expressions)),
        len(arc_rows),
    )

    expected = EXPECTED_FIBERS[incidence]
    characteristics_agree = _fiber_tuple(modular_fiber) == _fiber_tuple(rational_fiber)
    expected_matches = _fiber_tuple(rational_fiber)[:3] == expected
    negative_coordinate = _standard_negative_control(rational_columns, modular_columns)
    arc_checks = []
    for index, arc in enumerate(arc_rows):
        arc_checks.append(
            {
                "approach": arc["approach"],
                "coordinate_order": arc["coordinate_order"],
                "holomorphic_kernel_matches_committed_plane_plus_boundary_line": arc[
                    "holomorphic_kernel_matches_committed_plane_plus_boundary_line"
                ],
                "projective_coordinates": [
                    _gaussian_record(value) for value in cast(GaussianVector, arc["coordinates"])
                ],
                "rational_preimage": [
                    _gaussian_record(value) for value in cast(GaussianVector, rational_preimages[index])
                ],
                "modular_in_fiber": modular_fiber["arcs"][index]["in_fiber"],
                "modular_component_indices_one_based": modular_fiber["arcs"][index]["component_indices_one_based"],
                "rational_in_fiber": rational_fiber["arcs"][index]["in_fiber"],
                "rational_component_indices_one_based": rational_fiber["arcs"][index]["component_indices_one_based"],
            }
        )

    mutation = None
    if incidence == "W8->VB":
        dropped_index = _drop_required_generator(rational_columns, arc_targets)
        mutated_modular_phase_one = _mutated_phase_one(modular_phase_one, dropped_index)
        mutated_rational_phase_one = _mutated_phase_one(rational_phase_one, dropped_index)
        mutated_modular = _phase_two_summary(
            _run_singular(_phase_two_script(MODULAR_PRIME, mutated_modular_phase_one, ())),
            0,
        )
        mutated_rational = _phase_two_summary(
            _run_singular(_phase_two_script(0, mutated_rational_phase_one, ())),
            0,
        )
        reduced_columns = tuple(column for index, column in enumerate(rational_columns) if index != dropped_index)
        broken_arcs = [
            str(arc_rows[index]["approach"])
            for index, target in enumerate(arc_targets)
            if _solve_gaussian(reduced_columns, target) is None
        ]
        fiber_changed = _fiber_tuple(mutated_rational) != _fiber_tuple(rational_fiber)
        mutation = {
            "name": "drop_one_nakayama_generator_from_rees_ideal",
            "dropped_generator_index_one_based": dropped_index + 1,
            "dropped_original_coordinate_index_one_based": rational_phase_one["selected_indices_one_based"][
                dropped_index
            ],
            "broken_arc_containments": broken_arcs,
            "modular_fiber": mutated_modular,
            "rational_fiber": mutated_rational,
            "fiber_changed": fiber_changed,
            "detected": bool(broken_arcs) or fiber_changed,
        }

    arcs_pass = all(
        bool(arc["holomorphic_kernel_matches_committed_plane_plus_boundary_line"])
        and bool(arc["modular_in_fiber"])
        and bool(arc["rational_in_fiber"])
        and bool(arc["modular_component_indices_one_based"])
        and bool(arc["rational_component_indices_one_based"])
        for arc in arc_checks
    )
    passed = (
        data.schur_skew
        and data.pfaffian_adjugate_identity
        and data.restriction_matches_bordered_form
        and modular_phase_one["embedding_rank"] == EXPECTED_GENERATOR_COUNTS[incidence]
        and rational_phase_one["embedding_rank"] == EXPECTED_GENERATOR_COUNTS[incidence]
        and characteristics_agree
        and expected_matches
        and arcs_pass
        and (mutation is None or bool(mutation["detected"]))
    )
    return {
        "incidence": incidence,
        "source_orbit": row["source_orbit"],
        "boundary_orbit": row["boundary_orbit"],
        "schur_coordinate_sha256": data.coordinate_sha256,
        "nakayama_generator_count": rational_phase_one["selected_count"],
        "chosen_coordinate_indices_one_based": rational_phase_one["selected_indices_one_based"],
        "eliminated_slice_variables": rational_phase_one["eliminated_variables"],
        "remaining_slice_variables": rational_phase_one["remaining_variables"],
        "embedding_rank": rational_phase_one["embedding_rank"],
        "modular_prime": MODULAR_PRIME,
        "modular": modular_fiber,
        "rational": rational_fiber,
        "characteristic_invariants_agree": characteristics_agree,
        "expected_projective_dimension_degree_components": list(expected),
        "arc_checks": arc_checks,
        "negative_control": {
            "kind": "first standard projective basis point outside both embedding column spans",
            "coordinate_index_zero_based": negative_coordinate,
            "modular_in_column_span": False,
            "rational_in_column_span": False,
        },
        "mutation_control": mutation,
        "pass": passed,
    }


def _candidate_row(row: dict[str, Any]) -> dict[str, Any] | None:
    return row if str(row["incidence"]) in INCIDENCES else None


def _named_row(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    return str(row["incidence"]), row


def _witness_candidate(witness: dict[str, Any]) -> dict[str, Any] | None:
    return witness if str(witness["incidence"]) in INCIDENCES else None


def _witness_group(name: str, *, witnesses: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], ...]:
    return tuple(witness for witness in witnesses if str(witness["incidence"]) == name)


def _named_witness_group(name: str, *, witnesses: tuple[dict[str, Any], ...]) -> tuple[str, tuple[dict[str, Any], ...]]:
    return name, _witness_group(name, witnesses=witnesses)


def _closure_row(
    name: str,
    *,
    rows: dict[str, dict[str, Any]],
) -> tuple[str, tuple[str, ...]]:
    source_orbit = str(rows[name]["source_orbit"])
    source_key = SOURCE_KEYS.get(source_orbit, source_orbit)
    ideals = regularity.closure_ideals()
    return name, tuple(str(value) for value in ideals[source_key])


def _row_task(
    name: str,
    *,
    rows: dict[str, dict[str, Any]],
    witnesses: dict[str, tuple[dict[str, Any], ...]],
    closures: dict[str, tuple[str, ...]],
) -> RowTask:
    return RowTask(rows[name], witnesses[name], closures[name])


def _row_pass(row: dict[str, Any]) -> bool:
    return bool(row["pass"])


def _mutation_candidate(row: dict[str, Any]) -> dict[str, Any] | None:
    return row["mutation_control"] if row["incidence"] == "W8->VB" else None


def build_record() -> dict[str, Any]:
    first_order = _load_json(FIRST_ORDER_RESULT)
    witness_record = _load_json(SCHUR_WITNESS_RESULT)
    _require(first_order.get("pass") is True, "committed first-order record does not pass")
    _require(witness_record.get("pass") is True, "committed Schur-witness record does not pass")
    candidate_rows = parallel.ordered_map(_candidate_row, first_order["incidences"], min_items=1)
    selected_rows = cast(tuple[dict[str, Any], ...], tuple(filter(None, candidate_rows)))
    rows_by_name = dict(parallel.ordered_map(_named_row, selected_rows, min_items=1))
    witness_candidates = parallel.ordered_map(_witness_candidate, witness_record["witnesses"], min_items=1)
    selected_witnesses = cast(tuple[dict[str, Any], ...], tuple(filter(None, witness_candidates)))
    witness_groups = parallel.ordered_map(
        partial(_named_witness_group, witnesses=selected_witnesses), INCIDENCES, min_items=1
    )
    witnesses_by_name = dict(witness_groups)
    closures = dict(parallel.ordered_map(partial(_closure_row, rows=rows_by_name), INCIDENCES, min_items=1))
    tasks = parallel.ordered_map(
        partial(_row_task, rows=rows_by_name, witnesses=witnesses_by_name, closures=closures),
        INCIDENCES,
        min_items=1,
    )
    rows = tuple(parallel.ordered_map(_analyze_row, tasks, min_items=1))
    pass_flags = parallel.ordered_map(_row_pass, rows, min_items=1)
    mutation_candidates = parallel.ordered_map(_mutation_candidate, rows, min_items=1)
    mutations = tuple(filter(None, mutation_candidates))
    _require(len(mutations) == 1, "W8 mutation record is missing")
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    passed = all(pass_flags) and bool(mutations[0]["detected"])
    return {
        "schema": SCHEMA,
        "inputs": dict(input_rows),
        "tools": {"python_flint": flint.__version__, "singular": resolved._singular_version()},
        "scope": {
            "incidences": list(INCIDENCES),
            "excluded_blocked_incidence": {
                "incidence": "E8bar->VB",
                "ledger_reference": "docs/evidence/a5-kernel-attachments/ledger.md#ledger-rows, item 2j-c",
                "status": "blocked",
            },
            "claim_boundary": (
                "The record computes six holomorphic special fibers at the selected path-supported basepoints. "
                "It does not compute E8-bar to VB or variation along a boundary orbit."
            ),
        },
        "execution_contract": {
            "modular_prime": MODULAR_PRIME,
            "singular_address_space_bytes": int(SINGULAR_MEMORY_LIMIT),
            "singular_timeout_seconds": SINGULAR_TIMEOUT_SECONDS,
        },
        "summary": {
            "incidence_count": len(rows),
            "committed_arc_count": sum(len(row["arc_checks"]) for row in rows),
            "all_characteristic_invariants_agree": all(bool(row["characteristic_invariants_agree"]) for row in rows),
            "all_arcs_contained": all(
                bool(arc["modular_in_fiber"]) and bool(arc["rational_in_fiber"])
                for row in rows
                for arc in row["arc_checks"]
            ),
        },
        "incidences": rows,
        "mutation_control": mutations[0],
        "falsifier": (
            "A Nakayama count, chosen generator, presolved variable set, embedding rank, component invariant, "
            "committed-arc containment, or characteristic comparison changes; the projective negative control enters "
            "the column span; the generator-deletion mutation survives; or a row exceeds one second."
        ),
        "pass": passed,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "Nakayama-Rees record failed")
    _require(record["summary"]["incidence_count"] == 6, "incidence count changed")
    _require(record["summary"]["committed_arc_count"] == 12, "committed arc count changed")
    _require(bool(record["summary"]["all_characteristic_invariants_agree"]), "characteristics disagree")
    _require(bool(record["summary"]["all_arcs_contained"]), "a committed arc misses its fiber")
    _require(bool(record["mutation_control"]["detected"]), "generator-deletion mutation survived")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare deterministic JSON byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run baseline and mutation checks")
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
