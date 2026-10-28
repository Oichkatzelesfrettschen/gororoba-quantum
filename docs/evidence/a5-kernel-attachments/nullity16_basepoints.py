"""Path-supported germs and Schur-coordinate Nakayama counts at the nullity-16 strata."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, replace
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

import holomorphic_gauss_fibers as schur  # noqa: E402
import strata_regularity as regularity  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-nullity16-basepoints-v1"
CENSUS_RESULT = HERE / "incidence-census-result.json"
RESULT_PATH = HERE / "nullity16-basepoints-result.json"
SOURCE_PATHS = (
    HERE / "nullity16_basepoints.py",
    HERE / "holomorphic_gauss_fibers.py",
    HERE / "holomorphic_kernel_lemma.py",
    REGULARITY / "strata_regularity.py",
    EQUATIONS / "rederive_strata_equations.py",
    CENSUS_RESULT,
    ROOT / "gororoba_quantum" / "cd_core.py",
    ROOT / "gororoba_quantum" / "parallel.py",
)
INCLUDED_PASSAGES = ("12->16", "8->16")
ORBIT_KEYS = {"E8bar": "Ehat", "X+": "Xp", "X-": "Xm", "Va+": "Vap", "Va-": "Vam", "N+": "Np", "N-": "Nm"}
BOUNDARY_C_RANK = 6
BOUNDARY_C_KERNEL_DIMENSION = 9
SINGULAR_MEMORY_LIMIT = "4294967296"
SINGULAR_TIMEOUT_SECONDS = 300
MUTATION_TARGET = "Va+->N+"
MUTATION_NAME = "drop_first_source_closure_generator"

GaussianPolynomial: TypeAlias = schur.GaussianPolynomial
GaussianPolynomialMatrix: TypeAlias = schur.GaussianPolynomialMatrix


@dataclass(frozen=True)
class RowTask:
    incidence: str
    passage: str
    source_orbit: str
    boundary_orbit: str
    source_nullity: int
    point_key: str
    boundary_point: tuple[Fraction, ...]
    census_support_verified: bool
    closure_generators: tuple[str, ...]
    expected_germ: tuple[int, int, int, int]
    mutation: str = ""


@dataclass(frozen=True)
class PolynomialData:
    slice_names: tuple[str, ...]
    slice_columns: tuple[int, ...]
    coordinate_kind: str
    coordinates: tuple[GaussianPolynomial, ...]
    pivot_indices: tuple[int, ...]
    pivot_pfaffian_at_origin: schur.Gaussian
    pfaffian_adjugate_identity: bool
    schur_skew: bool
    coordinate_sha256: str
    maximum_total_degree: int
    maximum_component_terms: int


@dataclass(frozen=True)
class SingularOutcome:
    status: str
    stage: str
    results: dict[str, str]
    wall_nanoseconds: int
    peak_rss_kib: int | None
    diagnostic: str | None


@dataclass(frozen=True)
class RowOutcome:
    record: dict[str, Any]
    cost: dict[str, Any]


@dataclass(frozen=True)
class RecordBuild:
    record: dict[str, Any]
    costs: tuple[dict[str, Any], ...]


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


def _source_key(name: str) -> str:
    return ORBIT_KEYS.get(name, name)


def _boundary_key(name: str) -> str:
    return ORBIT_KEYS.get(name, name)


def _field() -> str:
    return "(0,I)"


def _parse_singular(stdout: str, return_code: int) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in stdout.splitlines():
        match = re.match(r"^RESULT (\S+) (.*)$", line.strip())
        if match is not None:
            parsed[match.group(1)] = match.group(2).strip()
    if return_code != 0 or "? " in stdout:
        parsed["singular_error"] = stdout[-6000:]
    return parsed


def _peak_rss(stderr: str) -> int | None:
    match = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", stderr)
    return int(match.group(1)) if match is not None else None


def _run_singular(script: str, stage: str) -> SingularOutcome:
    started = time.monotonic_ns()
    command = (
        "/usr/bin/time",
        "-v",
        "prlimit",
        f"--as={SINGULAR_MEMORY_LIMIT}",
        "Singular",
        "-q",
        "--no-warn",
    )
    process = subprocess.Popen(  # noqa: S603
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(script, timeout=SINGULAR_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        return SingularOutcome(
            "blocked_timeout",
            stage,
            {},
            time.monotonic_ns() - started,
            _peak_rss(stderr),
            "Singular exceeded the 300-second timeout",
        )
    elapsed = time.monotonic_ns() - started
    results = _parse_singular(stdout, process.returncode)
    if "singular_error" in results:
        diagnostic = (stderr + results["singular_error"])[-6000:]
        status = "blocked_resource" if process.returncode in (9, 137) else "blocked_error"
        return SingularOutcome(status, stage, results, elapsed, _peak_rss(stderr), diagnostic)
    return SingularOutcome("completed", stage, results, elapsed, _peak_rss(stderr), None)


def _coordinate_hash(values: tuple[GaussianPolynomial, ...]) -> str:
    payload = json.dumps([schur._gpoly_text(value) for value in values], separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _principal_four_pfaffians(context: Any, matrix: GaussianPolynomialMatrix) -> tuple[GaussianPolynomial, ...]:
    return tuple(
        schur._gpoly_pfaffian(context, schur._gpoly_extract(matrix, indices, indices))
        for indices in itertools.combinations(range(BOUNDARY_C_KERNEL_DIMENSION), 4)
    )


def _schur_coordinates(task: RowTask) -> PolynomialData:
    boundary_key = _boundary_key(task.boundary_orbit)
    slice_columns = tuple(
        regularity.transverse_columns(
            cast("list[int]", task.boundary_point),
            regularity.COLUMN_ORDER.get(boundary_key, range(schur.COMPLEX_DIMENSION)),
        )
    )
    slice_names = tuple(f"t{index + 1}" for index in range(len(slice_columns)))
    context = flint.fmpq_mpoly_ctx.get(slice_names, "degrevlex")
    variables = tuple(context.gens())
    split_coordinates = [schur._polynomial_constant(context, value) for value in task.boundary_point]
    for variable_index, coordinate_index in enumerate(slice_columns):
        split_coordinates[coordinate_index] += variables[variable_index]
    z_polynomials = tuple(
        schur._gpoly_scale_gaussian(
            context,
            (split_coordinate, schur._polynomial_zero(context)),
            schur.kernel_lemma._phase(index.bit_count()),
        )
        for index, split_coordinate in enumerate(split_coordinates, start=1)
    )
    c_polynomial = schur._polynomial_c_matrix(context, z_polynomials)

    boundary_z = schur.kernel_lemma._original_z_from_split(task.boundary_point)
    boundary_c = schur.kernel_lemma._c_matrix(boundary_z)
    _require(
        schur.kernel_lemma._rank(boundary_c) == BOUNDARY_C_RANK,
        f"{task.incidence} boundary C_z rank changed",
    )
    pivot, kernel_frame, complement = schur._principal_frame(boundary_c, BOUNDARY_C_RANK)
    transformation = schur._transformation_matrix(complement, kernel_frame)
    transformed = schur._gpoly_congruence(context, c_polynomial, transformation)
    pivot_range = range(BOUNDARY_C_RANK)
    kernel_range = range(BOUNDARY_C_RANK, schur.COMPLEX_DIMENSION)
    pivot_block = schur._gpoly_extract(transformed, pivot_range, pivot_range)
    coupling = schur._gpoly_extract(transformed, pivot_range, kernel_range)
    kernel_block = schur._gpoly_extract(transformed, kernel_range, kernel_range)
    pivot_pfaffian = schur._gpoly_pfaffian(context, pivot_block)
    pfaffian_adjugate = schur._pfaffian_adjugate(context, pivot_block)
    adjugate_identity = schur._gpoly_matrix_multiply(context, pivot_block, pfaffian_adjugate)
    expected_identity = tuple(
        tuple(
            pivot_pfaffian if row_index == column_index else schur._gpoly_zero(context)
            for column_index in range(BOUNDARY_C_RANK)
        )
        for row_index in range(BOUNDARY_C_RANK)
    )
    correction = schur._gpoly_matrix_multiply(
        context,
        schur._gpoly_matrix_multiply(context, schur._gpoly_transpose(coupling), pfaffian_adjugate),
        coupling,
    )
    numerator = tuple(
        tuple(
            schur._gpoly_add(
                schur._gpoly_multiply(pivot_pfaffian, kernel_block[row_index][column_index]),
                correction[row_index][column_index],
            )
            for column_index in range(BOUNDARY_C_KERNEL_DIMENSION)
        )
        for row_index in range(BOUNDARY_C_KERNEL_DIMENSION)
    )
    schur_skew = all(
        schur._gpoly_is_zero(schur._gpoly_add(numerator[row_index][column_index], numerator[column_index][row_index]))
        for row_index in range(BOUNDARY_C_KERNEL_DIMENSION)
        for column_index in range(BOUNDARY_C_KERNEL_DIMENSION)
    )
    if task.source_nullity == 12:
        coordinate_kind = "upper_triangle_entries_of_rank_two_form"
        coordinates = tuple(
            numerator[row_index][column_index]
            for row_index in range(BOUNDARY_C_KERNEL_DIMENSION)
            for column_index in range(row_index + 1, BOUNDARY_C_KERNEL_DIMENSION)
        )
        _require(len(coordinates) == 36, "rank-two Schur coordinate count changed")
    elif task.source_nullity == 8:
        coordinate_kind = "principal_four_pfaffians_of_rank_four_form"
        coordinates = _principal_four_pfaffians(context, numerator)
        _require(len(coordinates) == 126, "rank-four Schur coordinate count changed")
    else:
        raise RuntimeError(f"unsupported source nullity {task.source_nullity}")
    variable_count = len(slice_names)
    pfaffian_at_origin = schur._gpoly_constant_coefficient(pivot_pfaffian, variable_count)
    _require(pfaffian_at_origin != schur.kernel_lemma.ZERO, f"{task.incidence} boundary pivot Pfaffian vanished")
    return PolynomialData(
        slice_names,
        slice_columns,
        coordinate_kind,
        coordinates,
        pivot,
        pfaffian_at_origin,
        adjugate_identity == expected_identity,
        schur_skew,
        _coordinate_hash(coordinates),
        max(map(schur._gpoly_total_degree, coordinates)),
        max(map(schur._gpoly_term_count, coordinates)),
    )


def _germ_substitutions(task: RowTask, slice_columns: tuple[int, ...]) -> tuple[str, ...]:
    return tuple(
        f"({task.boundary_point[index]}+t{slice_columns.index(index) + 1})"
        if index in slice_columns
        else str(task.boundary_point[index])
        for index in range(schur.COMPLEX_DIMENSION)
    )


def _local_germ_lines(task: RowTask, data: PolynomialData) -> tuple[str, ...]:
    global_names = regularity.GLOBAL_VARS
    slice_names = data.slice_names
    return (
        'LIB "primdec.lib";',
        'LIB "sing.lib";',
        f"ring r={_field()},({','.join(global_names)}),dp;",
        "minpoly=I2+1;",
        f"ideal Closure={','.join(task.closure_generators)};",
        f"ring s={_field()},({','.join(slice_names)}),dp;",
        "minpoly=I2+1;",
        f"map sliceMap=r,{','.join(_germ_substitutions(task, data.slice_columns))};",
        "list LocalPrimes=minAssGTZ(sliceMap(Closure)); list ThroughOrigin; int componentCount=0;",
        "for(int i=1;i<=size(LocalPrimes);i++){if(size(reduce(LocalPrimes[i],std(maxideal(1))))==0){"
        "componentCount++;ThroughOrigin[componentCount]=LocalPrimes[i];}}",
        "ideal J=ThroughOrigin[1];",
        "for(int i=2;i<=componentCount;i++){J=intersect(J,ThroughOrigin[i]);}",
        "J=std(J);",
    )


def _germ_script(task: RowTask, data: PolynomialData) -> str:
    slice_names = data.slice_names
    zero = ",".join("0" for _name in slice_names)
    return "\n".join(
        (
            *_local_germ_lines(task, data),
            "int germDimension=dim(J); matrix GermJacobian=jacob(J);",
            f"map origin=s,{zero}; matrix OriginJacobian=origin(GermJacobian);",
            "int embeddingDimension=nvars(s)-rank(OriginJacobian);",
            f"ring d={_field()},({','.join(slice_names)},h),dp;",
            "minpoly=I2+1;",
            f"map normalMap=s,{','.join('h*' + name for name in slice_names)};",
            "ideal Cone=sat(normalMap(J),h); Cone=subst(Cone,h,0);",
            "setring s; ideal Tangent=std(imap(d,Cone)); int germMultiplicity=mult(Tangent);",
            '"RESULT germ_dimension",germDimension;',
            '"RESULT germ_multiplicity",germMultiplicity;',
            '"RESULT germ_embedding_dimension",embeddingDimension;',
            '"RESULT germ_component_count",componentCount;',
            "quit;",
        )
    )


def _nakayama_script(task: RowTask, data: PolynomialData) -> str:
    coordinate_text = ",".join(schur._singular_expression(value) for value in data.coordinates)
    return "\n".join(
        (
            *_local_germ_lines(task, data),
            f"ideal F={coordinate_text};",
            "ideal SJ=std(J+maxideal(1)*F);",
            "ideal NormalForms,G; intvec Selected; int selectedCount=0; poly candidate; int independent;",
            "for(int i=1;i<=size(F);i++){candidate=reduce(F[i],SJ);if(candidate!=0){independent=1;"
            "if(selectedCount>0 && reduce(candidate,std(NormalForms))==0){independent=0;}"
            "if(independent){selectedCount++;NormalForms[selectedCount]=candidate;G[selectedCount]=F[i];"
            "Selected[selectedCount]=i;}}}",
            '"RESULT nakayama_count",selectedCount;',
            'for(int i=1;i<=selectedCount;i++){"RESULT selected_"+string(i),Selected[i];}',
            "quit;",
        )
    )


def _blocked_record(
    task: RowTask,
    data: PolynomialData,
    outcome: SingularOutcome,
    germ_results: dict[str, str] | None,
) -> dict[str, Any]:
    record = {
        "incidence": task.incidence,
        "passage": task.passage,
        "source_orbit": task.source_orbit,
        "boundary_orbit": task.boundary_orbit,
        "source_nullity": task.source_nullity,
        "census_point_key": task.point_key,
        "boundary_point": list(map(str, task.boundary_point)),
        "slice_columns_zero_based": list(data.slice_columns),
        "slice_dimension": len(data.slice_columns),
        "coordinate_kind": data.coordinate_kind,
        "coordinate_count": len(data.coordinates),
        "schur_coordinate_sha256": data.coordinate_sha256,
        "status": outcome.status,
        "blocked_stage": outcome.stage,
        "blocked_diagnostic": outcome.diagnostic,
        "mutation": task.mutation,
        "pass": False,
    }
    if germ_results is not None:
        observed_germ = (
            int(germ_results["germ_dimension"]),
            int(germ_results["germ_multiplicity"]),
            int(germ_results["germ_embedding_dimension"]),
            int(germ_results["germ_component_count"]),
        )
        record.update(
            {
                "expected_germ_dimension_multiplicity_embedding_components": list(task.expected_germ),
                "observed_germ_dimension_multiplicity_embedding_components": list(observed_germ),
                "germ_matches_regularity_record": observed_germ == task.expected_germ,
            }
        )
    return record


def _completed_record(task: RowTask, data: PolynomialData, results: dict[str, str]) -> dict[str, Any]:
    selected_count = int(results["nakayama_count"])
    observed_germ = (
        int(results["germ_dimension"]),
        int(results["germ_multiplicity"]),
        int(results["germ_embedding_dimension"]),
        int(results["germ_component_count"]),
    )
    selected_indices = [int(results[f"selected_{index}"]) for index in range(1, selected_count + 1)]
    germ_matches = observed_germ == task.expected_germ
    structural_checks = (
        task.census_support_verified
        and len(data.slice_columns) == BOUNDARY_C_KERNEL_DIMENSION
        and data.pfaffian_adjugate_identity
        and data.schur_skew
        and 0 < selected_count <= len(data.coordinates)
        and len(set(selected_indices)) == selected_count
    )
    return {
        "incidence": task.incidence,
        "passage": task.passage,
        "source_orbit": task.source_orbit,
        "boundary_orbit": task.boundary_orbit,
        "source_nullity": task.source_nullity,
        "census_point_key": task.point_key,
        "census_support_verified": task.census_support_verified,
        "boundary_point": list(map(str, task.boundary_point)),
        "slice_columns_zero_based": list(data.slice_columns),
        "slice_dimension": len(data.slice_columns),
        "boundary_c_rank": BOUNDARY_C_RANK,
        "boundary_c_kernel_dimension": BOUNDARY_C_KERNEL_DIMENSION,
        "pivot_indices_zero_based": list(data.pivot_indices),
        "pivot_pfaffian_at_origin": [str(value) for value in data.pivot_pfaffian_at_origin],
        "pfaffian_adjugate_identity": data.pfaffian_adjugate_identity,
        "schur_skew": data.schur_skew,
        "coordinate_kind": data.coordinate_kind,
        "coordinate_count": len(data.coordinates),
        "schur_coordinate_sha256": data.coordinate_sha256,
        "maximum_coordinate_total_degree": data.maximum_total_degree,
        "maximum_coordinate_component_terms": data.maximum_component_terms,
        "expected_germ_dimension_multiplicity_embedding_components": list(task.expected_germ),
        "observed_germ_dimension_multiplicity_embedding_components": list(observed_germ),
        "germ_matches_regularity_record": germ_matches,
        "nakayama_count": selected_count,
        "selected_coordinate_indices_one_based": selected_indices,
        "status": "completed",
        "mutation": task.mutation,
        "pass": task.mutation == "" and structural_checks and germ_matches,
    }


def _analyze_row(task: RowTask) -> RowOutcome:
    started = time.monotonic_ns()
    schur._cap_worker_memory()
    data = _schur_coordinates(task)
    germ = _run_singular(_germ_script(task, data), "source_germ")
    nakayama: SingularOutcome | None = None
    if germ.status == "completed":
        nakayama = _run_singular(_nakayama_script(task, data), "nakayama_count")
    if germ.status != "completed":
        record = _blocked_record(task, data, germ, None)
        final_outcome = germ
    elif nakayama is None:
        raise RuntimeError("the Nakayama outcome is missing")
    elif nakayama.status != "completed":
        record = _blocked_record(task, data, nakayama, germ.results)
        final_outcome = nakayama
    else:
        record = _completed_record(task, data, germ.results | nakayama.results)
        final_outcome = nakayama
    singular_wall = germ.wall_nanoseconds + (nakayama.wall_nanoseconds if nakayama is not None else 0)
    rss_values = tuple(
        value
        for value in (germ.peak_rss_kib, nakayama.peak_rss_kib if nakayama is not None else None)
        if value is not None
    )
    cost = {
        "incidence": task.incidence,
        "mutation": task.mutation,
        "status": final_outcome.status,
        "stage": final_outcome.stage,
        "row_wall_nanoseconds": time.monotonic_ns() - started,
        "singular_wall_nanoseconds": singular_wall,
        "singular_peak_rss_kib": max(rss_values) if rss_values else None,
        "germ_wall_nanoseconds": germ.wall_nanoseconds,
        "nakayama_wall_nanoseconds": nakayama.wall_nanoseconds if nakayama is not None else None,
    }
    return RowOutcome(record, cost)


def _incidence_candidate(row: dict[str, Any]) -> dict[str, Any] | None:
    return row if str(row["passage"]) in INCLUDED_PASSAGES else None


def _point_candidate(row: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    key = str(row["key"])
    return (key, row) if key in ("N+:canonical", "N-:canonical") else None


def _closure_row(source_orbit: str) -> tuple[str, tuple[str, ...]]:
    ideals = regularity.closure_ideals()
    source_key = _source_key(source_orbit)
    return source_orbit, tuple(str(value) for value in ideals[source_key])


def _row_task(
    row: dict[str, Any],
    *,
    points: dict[str, dict[str, Any]],
    closures: dict[str, tuple[str, ...]],
) -> RowTask:
    point_key = f"{row['boundary_orbit']}:canonical"
    point = points[point_key]
    source_key = _source_key(str(row["source_orbit"]))
    boundary_key = _boundary_key(str(row["boundary_orbit"]))
    expected = regularity.EXPECTED_GERMS[(source_key, boundary_key)]
    expected_germ = (expected[0], expected[1], expected[2], expected[4])
    support_verified = (
        bool(row["pass"])
        and bool(point["pass"])
        and point_key == str(row["point_keys"][0])
        and bool(row["source_closure_membership"][0])
        and bool(row["boundary_orbit_membership"][0])
        and tuple(Fraction(value) for value in point["split_coordinates"])
        == tuple(Fraction(value) for value in regularity.REPS[boundary_key])
    )
    return RowTask(
        str(row["incidence"]),
        str(row["passage"]),
        str(row["source_orbit"]),
        str(row["boundary_orbit"]),
        int(row["source_nullity"]),
        point_key,
        tuple(Fraction(value) for value in point["split_coordinates"]),
        support_verified,
        closures[str(row["source_orbit"])],
        expected_germ,
    )


def _mutation_task(task: RowTask) -> RowTask:
    _require(task.incidence == MUTATION_TARGET, "mutation target changed")
    _require(len(task.closure_generators) > 1, "mutation target has no removable closure generator")
    return replace(task, closure_generators=task.closure_generators[1:], mutation=MUTATION_NAME)


def _row_pass(row: dict[str, Any]) -> bool:
    return bool(row["pass"])


def _completed_row(row: dict[str, Any]) -> bool:
    return row["status"] == "completed"


def _completed_row_pass(row: dict[str, Any]) -> bool:
    return row["status"] != "completed" or bool(row["pass"])


def _mutation_record(baseline: dict[str, Any], mutated: dict[str, Any]) -> dict[str, Any]:
    baseline_germ = baseline.get("observed_germ_dimension_multiplicity_embedding_components")
    mutated_germ = mutated.get("observed_germ_dimension_multiplicity_embedding_components")
    detected = (
        baseline.get("status") == "completed"
        and mutated.get("status") == "completed"
        and baseline_germ != mutated_germ
        and mutated.get("germ_matches_regularity_record") is False
    )
    return {
        "name": MUTATION_NAME,
        "target": MUTATION_TARGET,
        "input_change": "drop the first exact generator from the Va+ source-closure ideal",
        "baseline_germ_dimension_multiplicity_embedding_components": baseline_germ,
        "mutated_germ_dimension_multiplicity_embedding_components": mutated_germ,
        "detected": detected,
    }


def build_record() -> RecordBuild:
    census = _load_json(CENSUS_RESULT)
    _require(census.get("pass") is True, "committed incidence census does not pass")
    incidence_candidates = parallel.ordered_map(_incidence_candidate, census["incidences"], min_items=1)
    incidence_rows = cast(tuple[dict[str, Any], ...], tuple(filter(None, incidence_candidates)))
    _require(len(incidence_rows) == 18, "nullity-16 incidence count changed")
    point_candidates = parallel.ordered_map(_point_candidate, census["points"], min_items=1)
    points = dict(filter(None, point_candidates))
    source_orbits = tuple(sorted({str(row["source_orbit"]) for row in incidence_rows}))
    closures = dict(parallel.ordered_map(_closure_row, source_orbits, min_items=1))
    tasks = tuple(
        parallel.ordered_map(partial(_row_task, points=points, closures=closures), incidence_rows, min_items=1)
    )
    mutation_source = next(task for task in tasks if task.incidence == MUTATION_TARGET)
    mutation_task = _mutation_task(mutation_source)
    outcomes = tuple(parallel.ordered_map(_analyze_row, (*tasks, mutation_task), min_items=1))
    rows = tuple(outcome.record for outcome in outcomes[:-1])
    mutated_row = outcomes[-1].record
    mutation_baseline = next(row for row in rows if row["incidence"] == MUTATION_TARGET)
    mutation = _mutation_record(mutation_baseline, mutated_row)
    pass_flags = parallel.ordered_map(_row_pass, rows, min_items=1)
    completed_flags = parallel.ordered_map(_completed_row, rows, min_items=1)
    completed_pass_flags = parallel.ordered_map(_completed_row_pass, rows, min_items=1)
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    blocked_rows = [
        {"incidence": row["incidence"], "status": row["status"], "stage": row.get("blocked_stage")}
        for row in rows
        if row["status"] != "completed"
    ]
    record = {
        "schema": SCHEMA,
        "inputs": dict(input_rows),
        "tools": {"python_flint": flint.__version__, "singular": schur._singular_version()},
        "scope": {
            "incidence_count": len(rows),
            "passages": list(INCLUDED_PASSAGES),
            "boundary_orbits": ["N+", "N-"],
            "claim_boundary": (
                "The record certifies canonical census-supported basepoints, coordinate transverse slices, reduced "
                "source-closure germs, and local Schur-coordinate Nakayama counts for the 18 incidences into "
                "nullity 16. It does not compute their Gauss fibers or attaching maps."
            ),
        },
        "execution_contract": {
            "singular_address_space_bytes": int(SINGULAR_MEMORY_LIMIT),
            "singular_timeout_seconds": SINGULAR_TIMEOUT_SECONDS,
            "wall_clock_gate": None,
            "blocked_rows_continue": True,
        },
        "summary": {
            "incidence_count": len(rows),
            "completed_count": sum(completed_flags),
            "blocked_count": len(blocked_rows),
            "all_completed_rows_pass": all(completed_pass_flags),
        },
        "blocked_rows": blocked_rows,
        "incidences": rows,
        "mutation_control": mutation,
        "falsifier": (
            "A census-supported point leaves its stated orbit or source closure; a transverse slice has dimension "
            "other than nine; a reduced germ differs from the committed regularity invariants; the boundary C_z "
            "rank, Pfaffian-adjugate identity, Schur skewness, coordinate count, or Nakayama count fails; a row "
            "exceeds the 300-second or 4 GiB Singular limit without a blocked record; or the source-ideal mutation "
            "survives."
        ),
        "pass": all(pass_flags) and bool(mutation["detected"]),
    }
    costs = tuple(outcome.cost for outcome in outcomes)
    return RecordBuild(record, costs)


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(record["summary"]["incidence_count"] == 18, "nullity-16 incidence count changed")
    _require(
        record["summary"]["completed_count"] + record["summary"]["blocked_count"] == 18,
        "a nullity-16 row has neither a completed nor blocked outcome",
    )
    _require(bool(record["summary"]["all_completed_rows_pass"]), "a completed nullity-16 row failed")
    _require(bool(record["mutation_control"]["detected"]), "the source-ideal mutation survived")
    if record["summary"]["blocked_count"] == 0:
        _require(bool(record["pass"]), "the complete nullity-16 basepoint record failed")
    else:
        _require(not bool(record["pass"]), "an incomplete nullity-16 basepoint record passed")


def _report_costs(costs: tuple[dict[str, Any], ...]) -> None:
    for cost in costs:
        print(
            "COST"
            f" incidence={cost['incidence']}"
            f" mutation={cost['mutation'] or 'baseline'}"
            f" status={cost['status']}"
            f" stage={cost['stage']}"
            f" row_wall_ns={cost['row_wall_nanoseconds']}"
            f" singular_wall_ns={cost['singular_wall_nanoseconds']}"
            f" germ_wall_ns={cost['germ_wall_nanoseconds']}"
            f" nakayama_wall_ns={cost['nakayama_wall_nanoseconds']}"
            f" singular_peak_rss_kib={cost['singular_peak_rss_kib']}",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run baseline and mutation checks")
    arguments = parser.parse_args()
    selected_modes = sum((arguments.out is not None, arguments.check is not None, arguments.self_test))
    if selected_modes != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    build = build_record()
    _self_test(build.record)
    _report_costs(build.costs)
    rendered = _record_bytes(build.record)
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
