"""Nakayama-reduced Rees fibers for the 18 incidences into nullity 16."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any, cast

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import nakayama_rees_fibers as rees  # noqa: E402
import nullity16_basepoints as basepoints  # noqa: E402
import strata_regularity as regularity  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-nullity16-rees-fibers-v1"
BASEPOINT_RESULT = HERE / "nullity16-basepoints-result.json"
RESULT_PATH = HERE / "nullity16-rees-fibers-result.json"
SOURCE_PATHS = (
    HERE / "nullity16_rees_fibers.py",
    HERE / "nullity16_basepoints.py",
    BASEPOINT_RESULT,
    HERE / "nakayama_rees_fibers.py",
    HERE / "holomorphic_gauss_fibers.py",
    HERE / "holomorphic_kernel_lemma.py",
    REGULARITY / "strata_regularity.py",
    EQUATIONS / "rederive_strata_equations.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
    ROOT / "gororoba_quantum" / "parallel.py",
)
# Singular's eliminate takes its Hilbert-driven path only over a prime field; over (p,I) with a minpoly it runs
# plain sugar std. 32009 = 1 mod 4, so F_32009 contains i, and the two square roots of -1 are the images of i at
# the two primes of Z[i] over 32009.
MODULAR_PRIME = 32009
MODULAR_I_ROOTS = (10754, 32009 - 10754)
SINGULAR_MEMORY_LIMIT = "17179869184"
SINGULAR_TIMEOUT_SECONDS = 300
MUTATION_TARGET = "B9->N+"
# The ten nullity-8 incidences complete the Nakayama count and embedding; their modular Rees fiber may exhaust the
# Singular timeout, which the self-test admits at that stage only.
PERMITTED_BLOCKED = {
    **{
        f"{source}->{target}": "modular_rees_fiber"
        for source in ("E8bar", "Iso", "W8", "X+", "X-")
        for target in ("N+", "N-")
    },
}
MUTATION_NAME = "drop_first_nakayama_generator_from_rees_ideal"

Gaussian = rees.Gaussian
GaussianVector = rees.GaussianVector
ModVector = tuple[int, ...]


@dataclass(frozen=True)
class RowTask:
    row: dict[str, Any]
    closure_generators: tuple[str, ...]


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
    costs: tuple[SingularOutcome, ...]


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


def _ring_lines(name: str, root: int | None, variables: Sequence[str], prime: int = MODULAR_PRIME) -> tuple[str, str]:
    """Declare a ring over Q(i) when root is None, else over F_prime with I bound to that square root of -1."""
    if root is None:
        return f"ring {name}=(0,I),({','.join(variables)}),dp;", "minpoly=I2+1;"
    return f"ring {name}={prime},({','.join(variables)}),dp;", f"number I={root};"


def _peak_rss(stderr: str) -> int | None:
    match = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", stderr)
    return int(match.group(1)) if match is not None else None


def _parse_singular(stdout: str, stderr: str, return_code: int) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in stdout.splitlines():
        match = re.match(r"^RESULT (\S+) (.*)$", line.strip())
        if match is not None:
            parsed[match.group(1)] = match.group(2).strip()
    error_lines = tuple(
        line.strip() for stream in (stdout, stderr) for line in stream.splitlines() if line.strip().startswith("?")
    )
    if error_lines:
        parsed["singular_error"] = "\n".join(error_lines)
    elif return_code != 0:
        parsed["singular_error"] = f"Singular exited with status {return_code}"
    return parsed


def _kill_session(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def _exit_on_term(signum: int, _frame: object) -> None:
    raise SystemExit(128 + signum)


def _run_singular(script: str, stage: str, timeout_seconds: int = SINGULAR_TIMEOUT_SECONDS) -> SingularOutcome:
    started = time.monotonic_ns()
    if signal.getsignal(signal.SIGTERM) is signal.SIG_DFL:
        signal.signal(signal.SIGTERM, _exit_on_term)
    command = (
        "/usr/bin/time",
        "-v",
        "systemd-run",
        "--user",
        "--scope",
        "--quiet",
        "-p",
        f"MemoryMax={SINGULAR_MEMORY_LIMIT}",
        "-p",
        "MemorySwapMax=0",
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
        stdout, stderr = process.communicate(script, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        _kill_session(process)
        stdout, stderr = process.communicate()
        return SingularOutcome(
            "blocked_timeout",
            stage,
            {},
            time.monotonic_ns() - started,
            _peak_rss(stderr),
            f"Singular exceeded the {timeout_seconds}-second timeout",
        )
    except BaseException:
        # start_new_session detaches Singular from the caller's signals, so an unwinding caller kills and reaps it.
        _kill_session(process)
        process.wait()
        raise
    elapsed = time.monotonic_ns() - started
    results = _parse_singular(stdout, stderr, process.returncode)
    if "singular_error" in results:
        status = "blocked_resource" if process.returncode in (9, 137) else "blocked_error"
        return SingularOutcome(status, stage, results, elapsed, _peak_rss(stderr), results["singular_error"])
    return SingularOutcome("completed", stage, results, elapsed, _peak_rss(stderr), None)


def _base_task(task: RowTask) -> basepoints.RowTask:
    row = task.row
    expected = tuple(int(value) for value in row["expected_germ_dimension_multiplicity_embedding_components"])
    return basepoints.RowTask(
        str(row["incidence"]),
        str(row["passage"]),
        str(row["source_orbit"]),
        str(row["boundary_orbit"]),
        int(row["source_nullity"]),
        str(row["census_point_key"]),
        tuple(Fraction(value) for value in row["boundary_point"]),
        True,
        task.closure_generators,
        cast(tuple[int, int, int, int], expected),
    )


def _local_germ_lines(
    root: int | None, task: RowTask, data: basepoints.PolynomialData, prime: int = MODULAR_PRIME
) -> tuple[str, ...]:
    row_task = _base_task(task)
    slice_names = data.slice_names
    global_names = regularity.GLOBAL_VARS
    return (
        'LIB "primdec.lib";',
        'LIB "sing.lib";',
        *_ring_lines("r", root, global_names, prime),
        f"ideal Closure={','.join(task.closure_generators)};",
        *_ring_lines("s", root, slice_names, prime),
        f"map sliceMap=r,{','.join(basepoints._germ_substitutions(row_task, data.slice_columns))};",
        "list LocalPrimes=minAssGTZ(sliceMap(Closure)); list ThroughOrigin; int componentCount=0;",
        "for(int i=1;i<=size(LocalPrimes);i++){if(size(reduce(LocalPrimes[i],std(maxideal(1))))==0){"
        "componentCount++;ThroughOrigin[componentCount]=LocalPrimes[i];}}",
        "ideal J=ThroughOrigin[1];",
        "for(int i=2;i<=componentCount;i++){J=intersect(J,ThroughOrigin[i]);}",
        "J=std(J);",
    )


def _coordinate_text(data: basepoints.PolynomialData, indices: tuple[int, ...] | None = None) -> str:
    values = data.coordinates if indices is None else tuple(data.coordinates[index - 1] for index in indices)
    return ",".join(basepoints.schur._singular_expression(value) for value in values)


def _survivor_script(task: RowTask, data: basepoints.PolynomialData) -> str:
    variable_product = "*".join(data.slice_names)
    return "\n".join(
        (
            *_local_germ_lines(None, task, data),
            'LIB "matrix.lib";',
            f"ideal FullF={_coordinate_text(data)};",
            "ideal NormalForms=reduce(FullF,J);",
            f"matrix Coefficients=coef(NormalForms,{variable_product});",
            "int rowCount=nrows(Coefficients)-1; int columnCount=ncols(Coefficients);",
            "matrix CoefficientMatrix[rowCount][columnCount]; int rowIndex; int columnIndex; int swapIndex;",
            "for(rowIndex=1;rowIndex<=rowCount;rowIndex++){for(columnIndex=1;columnIndex<=columnCount;columnIndex++){"
            "CoefficientMatrix[rowIndex,columnIndex]=Coefficients[rowIndex+1,columnIndex];}}",
            "intvec RowLabels;for(rowIndex=1;rowIndex<=rowCount;rowIndex++){RowLabels[rowIndex]=rowIndex;}",
            "int pivotRow=1;int pivotCandidate;int originalLabel;poly swapEntry;number pivotValue;number factor;"
            "intvec Selected;",
            "for(columnIndex=1;columnIndex<=columnCount && pivotRow<=rowCount;columnIndex++){pivotCandidate=0;"
            "for(rowIndex=pivotRow;rowIndex<=rowCount;rowIndex++){"
            "if(CoefficientMatrix[rowIndex,columnIndex]!=0 && pivotCandidate==0){pivotCandidate=rowIndex;}}"
            "if(pivotCandidate>0){if(pivotCandidate!=pivotRow){for(swapIndex=1;swapIndex<=columnCount;swapIndex++){"
            "swapEntry=CoefficientMatrix[pivotRow,swapIndex];"
            "CoefficientMatrix[pivotRow,swapIndex]=CoefficientMatrix[pivotCandidate,swapIndex];"
            "CoefficientMatrix[pivotCandidate,swapIndex]=swapEntry;}"
            "originalLabel=RowLabels[pivotRow];RowLabels[pivotRow]=RowLabels[pivotCandidate];"
            "RowLabels[pivotCandidate]=originalLabel;}pivotValue=leadcoef(CoefficientMatrix[pivotRow,columnIndex]);"
            "for(swapIndex=1;swapIndex<=columnCount;swapIndex++){"
            "CoefficientMatrix[pivotRow,swapIndex]=CoefficientMatrix[pivotRow,swapIndex]/pivotValue;}"
            "for(rowIndex=1;rowIndex<=rowCount;rowIndex++){"
            "if(rowIndex!=pivotRow && CoefficientMatrix[rowIndex,columnIndex]!=0){"
            "factor=leadcoef(CoefficientMatrix[rowIndex,columnIndex]);"
            "for(swapIndex=1;swapIndex<=columnCount;swapIndex++){CoefficientMatrix[rowIndex,swapIndex]="
            "CoefficientMatrix[rowIndex,swapIndex]-factor*CoefficientMatrix[pivotRow,swapIndex];}}}"
            "Selected[pivotRow]=RowLabels[pivotRow];pivotRow++;}}",
            '"RESULT normal_form_count",ncols(NormalForms);',
            '"RESULT coefficient_monomial_count",columnCount;',
            '"RESULT survivor_count",pivotRow-1;',
            'for(rowIndex=1;rowIndex<pivotRow;rowIndex++){"RESULT survivor_"+string(rowIndex),Selected[rowIndex];}',
            "quit;",
        )
    )


def _survivor_summary(result: dict[str, str]) -> dict[str, Any]:
    count = int(result["survivor_count"])
    return {
        "normal_form_count": int(result["normal_form_count"]),
        "coefficient_monomial_count": int(result["coefficient_monomial_count"]),
        "survivor_count": count,
        "survivor_indices_one_based": [int(result[f"survivor_{index}"]) for index in range(1, count + 1)],
    }


def _phase_one_script(
    root: int | None,
    task: RowTask,
    data: basepoints.PolynomialData,
    candidate_indices: tuple[int, ...],
    *,
    prime: int = MODULAR_PRIME,
    embedding: bool = True,
) -> str:
    # I/(mI+J) is annihilated by m, and reduction modulo the standard basis of J+mF is linear with kernel J+mF, so a
    # candidate joins the Nakayama generators exactly when its normal-form coefficient row raises the prefix rank.
    # With embedding False the script stops after the presolved ideals, which is all the Rees-fiber input needs.
    candidate_text = _coordinate_text(data, candidate_indices)
    variable_product = "*".join(data.slice_names)
    candidate_mapping = ",".join(map(str, candidate_indices))
    coordinate_count = len(data.coordinates)
    reduction = (
        "ideal ReducedFullF=reduce(reducedMap(FullF),ReducedJ);",
        "ideal ReducedMaximal=simplify(reduce(reducedMap(maximal),ReducedJ),2);",
    )
    lift = (
        "ideal Prefix=ReducedJ+ReducedMaximal*ReducedFullF;int generatorOffset=size(Prefix);",
        "ideal LiftBasis=Prefix+ReducedG;",
        f"matrix LiftMatrix=lift(LiftBasis,ReducedFullF);matrix A[selectedCount][{coordinate_count}];",
        f"for(int i=1;i<=selectedCount;i++){{for(int j=1;j<={coordinate_count};j++){{"
        "A[i,j]=jet(LiftMatrix[generatorOffset+i,j],0);}}",
    )
    embedding_report = (
        '"RESULT embedding_rank",rank(A);',
        f"for(int i=1;i<=selectedCount;i++){{for(int j=1;j<={coordinate_count};j++){{"
        'string("RESULT embedding_"+string(i)+"_"+string(j)+" "+string(A[i,j]));}}',
    )
    return "\n".join(
        (
            *_local_germ_lines(root, task, data, prime),
            'LIB "presolve.lib";',
            'LIB "matrix.lib";',
            f"ideal FullF={_coordinate_text(data)};",
            f"ideal F={candidate_text};",
            f"intvec CandidateOriginal={candidate_mapping};",
            "ideal maximal=maxideal(1);ideal SJ=std(J+maximal*F);ideal CandidateForms=reduce(F,SJ);",
            f"matrix CandidateCoefficients=coef(CandidateForms,{variable_product});",
            'if(nrows(CandidateCoefficients)!=ncols(F)+1){ERROR("coefficient rows do not match the candidates");}',
            "intvec CoefficientColumns=1..ncols(CandidateCoefficients);",
            "ideal NormalForms,G;intvec Selected;int selectedCount=0;int prefixRank;",
            "for(int i=1;i<=ncols(F);i++){intvec PrefixRows=2..i+1;"
            "prefixRank=rank(submat(CandidateCoefficients,PrefixRows,CoefficientColumns));kill PrefixRows;"
            "if(prefixRank>selectedCount){selectedCount++;NormalForms[selectedCount]=CandidateForms[i];"
            "G[selectedCount]=F[i];Selected[selectedCount]=CandidateOriginal[i];}}",
            "list EP=elimpart(J);map reducedMap=s,EP[5];",
            "ideal ReducedJ=std(reducedMap(J));",
            *(reduction if embedding else reduction[1:]),
            "ideal ReducedG=simplify(reduce(reducedMap(G),ReducedJ),2);",
            *(lift if embedding else ()),
            '"RESULT germ_dimension",dim(J);',
            '"RESULT germ_component_count",componentCount;',
            '"RESULT candidate_count",ncols(F);',
            '"RESULT selected_count",selectedCount;',
            'for(int i=1;i<=selectedCount;i++){"RESULT selected_"+string(i),Selected[i];}',
            "int eliminatedCount=0;for(int i=1;i<=size(EP[2]);i++){if(EP[2][i]!=0){eliminatedCount++;"
            '"RESULT eliminated_"+string(eliminatedCount),EP[2][i];}}',
            '"RESULT eliminated_count",eliminatedCount;',
            '"RESULT reduced_j_count",size(ReducedJ);',
            'for(int i=1;i<=size(ReducedJ);i++){"RESULT reduced_j_"+string(i),ReducedJ[i];}',
            '"RESULT reduced_g_count",size(ReducedG);',
            'for(int i=1;i<=size(ReducedG);i++){"RESULT reduced_g_"+string(i),ReducedG[i];}',
            *(embedding_report if embedding else ()),
            "quit;",
        )
    )


def _phase_one_summary(result: dict[str, str], coordinate_count: int) -> dict[str, Any]:
    candidate_count = int(result["candidate_count"])
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
        "candidate_count": candidate_count,
        "selected_count": selected_count,
        "selected_indices_one_based": [int(result[f"selected_{index}"]) for index in range(1, selected_count + 1)],
        "eliminated_variables": [result[f"eliminated_{index}"] for index in range(1, eliminated_count + 1)],
        "remaining_variables": sorted(reduced_variables, key=rees._slice_variable_index),
        "reduced_j": reduced_j,
        "reduced_g": reduced_g,
        "embedding_rank": int(result["embedding_rank"]),
        "embedding_rows": [
            [result[f"embedding_{row}_{column}"] for column in range(1, coordinate_count + 1)]
            for row in range(1, selected_count + 1)
        ],
    }


def _rational_vectors(phase_one: dict[str, Any]) -> tuple[GaussianVector, ...]:
    return tuple(
        tuple(rees._parse_gaussian(value) for value in row)
        for row in cast(list[list[str]], phase_one["embedding_rows"])
    )


def _fraction_mod(value: Fraction) -> int:
    _require(value.denominator % MODULAR_PRIME != 0, f"{value} has no residue modulo {MODULAR_PRIME}")
    return value.numerator * pow(value.denominator, -1, MODULAR_PRIME) % MODULAR_PRIME


def _gaussian_mod(value: Gaussian, root: int) -> int:
    return (_fraction_mod(value[0]) + root * _fraction_mod(value[1])) % MODULAR_PRIME


def _parse_mod(text: str) -> int:
    """Read a prime-field coefficient as Singular prints it, an integer in the symmetric residue range."""
    _require(re.fullmatch(r"-?\d+", text.strip()) is not None, f"modular coefficient {text!r} is not a residue")
    return int(text) % MODULAR_PRIME


def _modular_vectors(phase_one: dict[str, Any]) -> tuple[ModVector, ...]:
    return tuple(
        tuple(_parse_mod(value) for value in row) for row in cast(list[list[str]], phase_one["embedding_rows"])
    )


def _mod_rref(matrix: tuple[ModVector, ...]) -> tuple[tuple[ModVector, ...], tuple[int, ...]]:
    rows = [list(row) for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0]) if rows else 0
    pivot_row = 0
    pivot_columns: list[int] = []
    for column in range(column_count):
        selected = next((row for row in range(pivot_row, row_count) if rows[row][column]), None)
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, MODULAR_PRIME)
        rows[pivot_row] = [value * inverse % MODULAR_PRIME for value in rows[pivot_row]]
        for row in range(row_count):
            factor = rows[row][column]
            if row == pivot_row or not factor:
                continue
            rows[row] = [
                (value - factor * pivot_value) % MODULAR_PRIME
                for value, pivot_value in zip(rows[row], rows[pivot_row], strict=True)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    return tuple(tuple(row) for row in rows), tuple(pivot_columns)


def _solve_modular(columns: tuple[ModVector, ...], target: ModVector) -> ModVector | None:
    augmented = tuple((*row, target[row_index]) for row_index, row in enumerate(zip(*columns, strict=True)))
    reduced, pivots = _mod_rref(augmented)
    width = len(columns)
    if width in pivots or pivots[:width] != tuple(range(width)):
        return None
    return tuple(reduced[row][-1] for row in range(width))


def _embedding_rank(vectors: tuple[GaussianVector, ...]) -> int:
    if not vectors:
        return 0
    matrix = tuple(tuple(vector[column] for vector in vectors) for column in range(len(vectors[0])))
    _reduced, pivots = basepoints.schur.kernel_lemma._rref(matrix)
    return len(pivots)


def _standard_negative_control(
    rational_vectors: tuple[GaussianVector, ...],
    modular_vectors_by_root: tuple[tuple[ModVector, ...], ...],
) -> int:
    coordinate_count = len(rational_vectors[0])
    for coordinate_index in range(coordinate_count):
        rational_target = tuple(
            basepoints.schur.kernel_lemma.ONE if index == coordinate_index else basepoints.schur.kernel_lemma.ZERO
            for index in range(coordinate_count)
        )
        modular_target = tuple(int(index == coordinate_index) for index in range(coordinate_count))
        if rees._solve_gaussian(rational_vectors, rational_target) is None and all(
            _solve_modular(modular_vectors, modular_target) is None for modular_vectors in modular_vectors_by_root
        ):
            return coordinate_index
    raise RuntimeError("every standard projective basis point lies in the embedding image")


def _embedding_record(vectors: tuple[GaussianVector, ...]) -> list[list[list[str]]]:
    coordinate_count = len(vectors[0])
    return [
        [rees._gaussian_record(vectors[column][row]) for column in range(len(vectors))]
        for row in range(coordinate_count)
    ]


def _projective_point(vector: GaussianVector) -> list[list[str]]:
    pivot = next(value for value in vector if value != basepoints.schur.kernel_lemma.ZERO)
    inverse = basepoints.schur.kernel_lemma._gaussian_inverse(pivot)
    return [rees._gaussian_record(basepoints.schur.kernel_lemma._gaussian_multiply(value, inverse)) for value in vector]


def _modular_embedding_agrees(
    rational_vectors: tuple[GaussianVector, ...], modular_vectors: tuple[ModVector, ...], root: int
) -> bool:
    return all(
        _gaussian_mod(rational_value, root) == modular_value
        for rational_vector, modular_vector in zip(rational_vectors, modular_vectors, strict=True)
        for rational_value, modular_value in zip(rational_vector, modular_vector, strict=True)
    )


def _phase_two_script(root: int | None, phase_one: dict[str, Any]) -> str:
    """Write the Rees special-fiber script of nakayama_rees_fibers without arc tests, over the field root selects."""
    remaining = tuple(str(value) for value in phase_one["remaining_variables"])
    reduced_j = tuple(str(value) for value in phase_one["reduced_j"])
    reduced_g = tuple(str(value) for value in phase_one["reduced_g"])
    target_names = tuple(f"y{index + 1}" for index in range(len(reduced_g)))
    lines = [
        'LIB "primdec.lib";',
        'LIB "elim.lib";',
        *_ring_lines("R", root, ("a", *remaining, *target_names)),
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
            "quit;",
        )
    )
    return "\n".join(lines)


def _blocked_record(
    task: RowTask,
    data: basepoints.PolynomialData,
    outcome: SingularOutcome,
    partial: dict[str, Any],
) -> dict[str, Any]:
    return {
        "incidence": task.row["incidence"],
        "source_orbit": task.row["source_orbit"],
        "boundary_orbit": task.row["boundary_orbit"],
        "coordinate_count": len(data.coordinates),
        "coordinate_kind": data.coordinate_kind,
        "schur_coordinate_sha256": data.coordinate_sha256,
        **partial,
        "status": outcome.status,
        "blocked_stage": outcome.stage,
        "blocked_diagnostic": outcome.diagnostic,
        "pass": False,
    }


def _analyze_row(task: RowTask) -> RowOutcome:
    # Singular inherits RLIMIT_AS from this process, so the row analysis leaves it unset and the MemoryMax scope of
    # _run_singular bounds each call.
    row = task.row
    incidence = str(row["incidence"])
    data = basepoints._schur_coordinates(_base_task(task))
    _require(data.coordinate_sha256 == row["schur_coordinate_sha256"], f"{incidence} Schur coordinates changed")
    costs: list[SingularOutcome] = []
    partial: dict[str, Any] = {}

    if row["status"] == "completed":
        candidate_indices = tuple(int(value) for value in row["selected_coordinate_indices_one_based"])
        survivor = {
            "applied": False,
            "authority": "nullity16-basepoints-result.json selected_coordinate_indices_one_based",
            "candidate_count": len(candidate_indices),
            "candidate_indices_one_based": list(candidate_indices),
        }
    else:
        survivor_outcome = _run_singular(_survivor_script(task, data), "normal_form_survivor_selection")
        costs.append(survivor_outcome)
        if survivor_outcome.status != "completed":
            return RowOutcome(_blocked_record(task, data, survivor_outcome, partial), tuple(costs))
        survivor_summary = _survivor_summary(survivor_outcome.results)
        candidate_indices = tuple(int(value) for value in survivor_summary["survivor_indices_one_based"])
        _require(bool(candidate_indices), f"{incidence} survivor selection is empty")
        _require(
            survivor_summary["normal_form_count"] == len(data.coordinates),
            f"{incidence} normal-form coordinate count changed",
        )
        survivor = {"applied": True, **survivor_summary, "candidate_indices_one_based": list(candidate_indices)}
    partial["normal_form_survivor_selection"] = survivor

    modular_phases: list[dict[str, Any]] = []
    for root in MODULAR_I_ROOTS:
        modular_phase_outcome = _run_singular(
            _phase_one_script(root, task, data, candidate_indices), "modular_nakayama_and_embedding"
        )
        costs.append(modular_phase_outcome)
        if modular_phase_outcome.status != "completed":
            partial["blocked_modular_i_root"] = root
            return RowOutcome(_blocked_record(task, data, modular_phase_outcome, partial), tuple(costs))
        modular_phases.append(_phase_one_summary(modular_phase_outcome.results, len(data.coordinates)))
    partial["modular_nakayama_counts"] = [phase["selected_count"] for phase in modular_phases]

    rational_phase_outcome = _run_singular(
        _phase_one_script(None, task, data, candidate_indices), "rational_nakayama_and_embedding"
    )
    costs.append(rational_phase_outcome)
    if rational_phase_outcome.status != "completed":
        return RowOutcome(_blocked_record(task, data, rational_phase_outcome, partial), tuple(costs))
    rational_phase = _phase_one_summary(rational_phase_outcome.results, len(data.coordinates))
    partial["rational_nakayama_count"] = rational_phase["selected_count"]

    rational_vectors = _rational_vectors(rational_phase)
    modular_vectors_by_root = tuple(_modular_vectors(phase) for phase in modular_phases)
    selected_agree = all(
        rational_phase["selected_indices_one_based"] == phase["selected_indices_one_based"] for phase in modular_phases
    )
    counts_agree = all(rational_phase["selected_count"] == phase["selected_count"] for phase in modular_phases)
    embeddings_agree = all(
        _modular_embedding_agrees(rational_vectors, modular_vectors, root)
        for modular_vectors, root in zip(modular_vectors_by_root, MODULAR_I_ROOTS, strict=True)
    )
    negative_coordinate = _standard_negative_control(rational_vectors, modular_vectors_by_root)
    embedding_rank = _embedding_rank(rational_vectors)
    one_point = _projective_point(rational_vectors[0]) if len(rational_vectors) == 1 else None

    mutation = None
    partial.update(
        {
            "nakayama_generator_count": rational_phase["selected_count"],
            "chosen_coordinate_indices_one_based": rational_phase["selected_indices_one_based"],
            "eliminated_slice_variables": rational_phase["eliminated_variables"],
            "remaining_slice_variables": rational_phase["remaining_variables"],
            "embedding_shape_rows_columns": [len(data.coordinates), rational_phase["selected_count"]],
            "embedding_rank": embedding_rank,
            "embedding_matrix_rows": _embedding_record(rational_vectors),
            "embedded_point": one_point,
            "nakayama_counts_agree": counts_agree,
            "chosen_coordinates_agree": selected_agree,
            "embedding_reduces_modularly": embeddings_agree,
            "negative_control": {
                "kind": "first standard projective basis point outside the rational and every modular embedding span",
                "coordinate_index_zero_based": negative_coordinate,
                "modular_in_column_span": False,
                "rational_in_column_span": False,
            },
            "mutation_control": mutation,
        }
    )

    modular_fibers: list[dict[str, Any]] = []
    for root, modular_phase in zip(MODULAR_I_ROOTS, modular_phases, strict=True):
        modular_fiber_outcome = _run_singular(_phase_two_script(root, modular_phase), "modular_rees_fiber")
        costs.append(modular_fiber_outcome)
        if modular_fiber_outcome.status != "completed":
            partial["blocked_modular_i_root"] = root
            return RowOutcome(_blocked_record(task, data, modular_fiber_outcome, partial), tuple(costs))
        modular_fibers.append({"i_root": root, **rees._phase_two_summary(modular_fiber_outcome.results, 0)})

    rational_fiber_outcome = _run_singular(_phase_two_script(None, rational_phase), "rational_rees_fiber")
    costs.append(rational_fiber_outcome)
    if rational_fiber_outcome.status != "completed":
        return RowOutcome(_blocked_record(task, data, rational_fiber_outcome, partial), tuple(costs))
    rational_fiber = rees._phase_two_summary(rational_fiber_outcome.results, 0)

    characteristic_fibers_agree = all(
        rees._fiber_tuple(rational_fiber) == rees._fiber_tuple(modular_fiber) for modular_fiber in modular_fibers
    )

    if incidence == MUTATION_TARGET:
        _require(rational_phase["selected_count"] >= 2, "the mutation target needs at least two Rees generators")
        mutated_phase = rees._mutated_phase_one(rational_phase, 0)
        mutated_outcome = _run_singular(_phase_two_script(None, mutated_phase), "mutated_rational_rees_fiber")
        costs.append(mutated_outcome)
        if mutated_outcome.status != "completed":
            return RowOutcome(_blocked_record(task, data, mutated_outcome, partial), tuple(costs))
        mutated_fiber = rees._phase_two_summary(mutated_outcome.results, 0)
        fiber_changed = rees._fiber_tuple(mutated_fiber) != rees._fiber_tuple(rational_fiber)
        mutation = {
            "name": MUTATION_NAME,
            "target": MUTATION_TARGET,
            "dropped_generator_index_one_based": 1,
            "dropped_original_coordinate_index_one_based": rational_phase["selected_indices_one_based"][0],
            "baseline_fiber": rees._fiber_tuple(rational_fiber),
            "mutated_fiber": rees._fiber_tuple(mutated_fiber),
            "fiber_changed": fiber_changed,
            "detected": fiber_changed,
        }
        partial["mutation_control"] = mutation

    expected_count_matches = row.get("nakayama_count") in (None, rational_phase["selected_count"])
    germ_matches = rational_phase["germ_dimension"] == int(
        row["observed_germ_dimension_multiplicity_embedding_components"][0]
    ) and rational_phase["germ_component_count"] == int(
        row["observed_germ_dimension_multiplicity_embedding_components"][3]
    )
    passed = (
        counts_agree
        and selected_agree
        and embeddings_agree
        and characteristic_fibers_agree
        and expected_count_matches
        and germ_matches
        and all(phase["embedding_rank"] == phase["selected_count"] for phase in modular_phases)
        and rational_phase["embedding_rank"] == rational_phase["selected_count"]
        and embedding_rank == rational_phase["selected_count"]
        and (mutation is None or bool(mutation["detected"]))
    )
    return RowOutcome(
        {
            "incidence": incidence,
            "source_orbit": row["source_orbit"],
            "boundary_orbit": row["boundary_orbit"],
            "coordinate_count": len(data.coordinates),
            "coordinate_kind": data.coordinate_kind,
            "schur_coordinate_sha256": data.coordinate_sha256,
            "normal_form_survivor_selection": survivor,
            "nakayama_generator_count": rational_phase["selected_count"],
            "chosen_coordinate_indices_one_based": rational_phase["selected_indices_one_based"],
            "eliminated_slice_variables": rational_phase["eliminated_variables"],
            "remaining_slice_variables": rational_phase["remaining_variables"],
            "embedding_shape_rows_columns": [len(data.coordinates), rational_phase["selected_count"]],
            "embedding_rank": embedding_rank,
            "embedding_matrix_rows": _embedding_record(rational_vectors),
            "embedded_point": one_point,
            "modular_prime": MODULAR_PRIME,
            "modular_i_roots": list(MODULAR_I_ROOTS),
            "modular": modular_fibers,
            "rational": rational_fiber,
            "nakayama_counts_agree": counts_agree,
            "chosen_coordinates_agree": selected_agree,
            "embedding_reduces_modularly": embeddings_agree,
            "characteristic_invariants_agree": characteristic_fibers_agree,
            "committed_nakayama_count_matches": expected_count_matches,
            "germ_dimension_and_components_match": germ_matches,
            "negative_control": {
                "kind": "first standard projective basis point outside the rational and every modular embedding span",
                "coordinate_index_zero_based": negative_coordinate,
                "modular_in_column_span": False,
                "rational_in_column_span": False,
            },
            "mutation_control": mutation,
            "status": "completed",
            "pass": passed,
        },
        tuple(costs),
    )


def _source_key(name: str) -> str:
    return basepoints.ORBIT_KEYS.get(name, name)


def _closure_row(source_orbit: str) -> tuple[str, tuple[str, ...]]:
    ideals = regularity.closure_ideals()
    return source_orbit, tuple(str(value) for value in ideals[_source_key(source_orbit)])


def _task_row(row: dict[str, Any], *, closures: dict[str, tuple[str, ...]]) -> RowTask:
    source_orbit = str(row["source_orbit"])
    return RowTask(row, closures[source_orbit])


def _row_pass(row: dict[str, Any]) -> bool:
    return bool(row["pass"])


def _completed_row(row: dict[str, Any]) -> bool:
    return row["status"] == "completed"


def _completed_row_pass(row: dict[str, Any]) -> bool:
    return row["status"] != "completed" or bool(row["pass"])


def _mutation_candidate(row: dict[str, Any]) -> dict[str, Any] | None:
    return cast(dict[str, Any] | None, row.get("mutation_control"))


def admitted_row_workers(budget_gib: int, items: int) -> int:
    """Each row analysis holds one Singular scope of SINGULAR_MEMORY_LIMIT bytes, so a budget of B GiB admits
    floor(B / 16) concurrent rows; the CPU allocation and the row count cap it further, and at least one runs."""
    per_row_gib = int(SINGULAR_MEMORY_LIMIT) // 2**30
    return max(1, min(budget_gib // per_row_gib, items, parallel.workers()))


def _analyze_rows(tasks: tuple[RowTask, ...]) -> tuple[RowOutcome, ...]:
    """Row analyses in order, pooled in chunks of the admitted width. GOROROBA_SINGULAR_BUDGET_GIB sets the
    memory budget (default 16 GiB, one row at a time); a row's 300 s timeout makes its outcome depend on the
    host, so a replay of the retained record keeps the retained host's width."""
    budget = int(os.environ.get("GOROROBA_SINGULAR_BUDGET_GIB", "16"))
    width = admitted_row_workers(budget, len(tasks))
    outcomes: list[RowOutcome] = []
    for start in range(0, len(tasks), width):
        outcomes.extend(parallel.ordered_map(_analyze_row, tasks[start : start + width], min_items=2))
    return tuple(outcomes)


def build_record() -> tuple[dict[str, Any], tuple[RowOutcome, ...]]:
    _require(
        all(root * root % MODULAR_PRIME == MODULAR_PRIME - 1 for root in MODULAR_I_ROOTS),
        f"a listed root is not a square root of -1 modulo {MODULAR_PRIME}",
    )
    basepoint_record = _load_json(BASEPOINT_RESULT)
    _require(basepoint_record["summary"]["incidence_count"] == 18, "nullity-16 incidence count changed")
    _require(
        bool(basepoint_record["summary"]["all_completed_rows_pass"]),
        "a completed nullity-16 basepoint row does not pass",
    )
    singular_version = basepoints.schur._singular_version()
    source_orbits = tuple(sorted({str(row["source_orbit"]) for row in basepoint_record["incidences"]}))
    closures = dict(parallel.ordered_map(_closure_row, source_orbits, min_items=1))
    tasks = parallel.ordered_map(partial(_task_row, closures=closures), basepoint_record["incidences"], min_items=1)
    outcomes = _analyze_rows(tuple(tasks))
    rows = tuple(outcome.record for outcome in outcomes)
    pass_flags = parallel.ordered_map(_row_pass, rows, min_items=1)
    completed_flags = parallel.ordered_map(_completed_row, rows, min_items=1)
    completed_pass_flags = parallel.ordered_map(_completed_row_pass, rows, min_items=1)
    mutation_candidates = parallel.ordered_map(_mutation_candidate, rows, min_items=1)
    mutations = tuple(filter(None, mutation_candidates))
    _require(len(mutations) <= 1, "multiple generator-deletion mutation records exist")
    blocked_rows = [
        {"incidence": row["incidence"], "status": row["status"], "stage": row.get("blocked_stage")}
        for row in rows
        if row["status"] != "completed"
    ]
    mutation_target_row = next(row for row in rows if row["incidence"] == MUTATION_TARGET)
    mutation = (
        mutations[0]
        if mutations
        else {
            "name": MUTATION_NAME,
            "target": MUTATION_TARGET,
            "status": "blocked",
            "blocked_stage": mutation_target_row.get("blocked_stage"),
            "reason": "the target row blocked before its full embedding was available",
            "detected": False,
        }
    )
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    record = {
        "schema": SCHEMA,
        "inputs": dict(input_rows),
        "tools": {"python_flint": basepoints.flint.__version__, "singular": singular_version},
        "scope": {
            "incidence_count": len(rows),
            "boundary_orbits": ["N+", "N-"],
            "claim_boundary": (
                "The record computes complex-algebraic Nakayama-reduced Rees special fibers at the canonical "
                "census-supported N+ and N- basepoints. It does not compute variation along either boundary orbit, "
                "two-sided real fibers, or attaching maps."
            ),
        },
        "execution_contract": {
            "modular_prime": MODULAR_PRIME,
            "modular_i_roots": list(MODULAR_I_ROOTS),
            "singular_cgroup_memory_max_bytes": int(SINGULAR_MEMORY_LIMIT),
            "row_analysis_workers": 1,
            "singular_timeout_seconds": SINGULAR_TIMEOUT_SECONDS,
            "wall_clock_gate": None,
            "blocked_rows_continue": True,
        },
        "summary": {
            "incidence_count": len(rows),
            "completed_count": sum(completed_flags),
            "blocked_count": len(blocked_rows),
            "all_completed_rows_pass": all(completed_pass_flags),
            "all_completed_characteristic_invariants_agree": all(
                row["status"] != "completed" or bool(row["characteristic_invariants_agree"]) for row in rows
            ),
        },
        "blocked_rows": blocked_rows,
        "incidences": rows,
        "mutation_control": mutation,
        "falsifier": (
            "A normal-form survivor rank, Nakayama count, chosen generator, presolved variable set, full embedding "
            "rank, special-fiber component invariant, or characteristic comparison changes; a standard projective "
            "basis point enters both embedding spans; a row exceeds a Singular resource limit without a stage-specific "
            "blocked record; or the generator-deletion mutation survives."
        ),
        "pass": not blocked_rows and all(pass_flags) and bool(mutation["detected"]),
    }
    return record, outcomes


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    rows = {row["incidence"]: row for row in record["incidences"]}
    _require(len(rows) == 18, "nullity-16 incidence count changed")
    for name, row in rows.items():
        if name in PERMITTED_BLOCKED:
            if row["status"] != "completed":
                _require(row["status"] == "blocked_timeout", f"{name} blocked for a reason other than the timeout")
                _require(row.get("blocked_stage") == PERMITTED_BLOCKED[name], f"{name} blocked at an unexpected stage")
            else:
                _require(bool(row["pass"]), f"{name} completed but failed")
        else:
            _require(row["status"] == "completed", f"{name} did not complete")
            _require(bool(row["pass"]), f"{name} failed")
    _require(record["summary"]["completed_count"] >= 8, "fewer than the eight fast rows completed")
    _require(bool(record["mutation_control"]["detected"]), "the generator-deletion mutation survived")
    _require(
        bool(record["pass"]) == (record["summary"]["blocked_count"] == 0),
        "the record pass flag disagrees with its blocked rows",
    )


def _report_costs(outcomes: tuple[RowOutcome, ...]) -> None:
    for outcome in outcomes:
        for cost in outcome.costs:
            print(
                "COST"
                f" incidence={outcome.record['incidence']}"
                f" status={cost.status}"
                f" stage={cost.stage}"
                f" wall_ns={cost.wall_nanoseconds}"
                f" peak_rss_kib={cost.peak_rss_kib}",
                file=sys.stderr,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare deterministic JSON byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run baseline and mutation checks")
    arguments = parser.parse_args()
    selected_modes = sum((arguments.out is not None, arguments.check is not None, arguments.self_test))
    if selected_modes != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record, outcomes = build_record()
    _self_test(record)
    _report_costs(outcomes)
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
