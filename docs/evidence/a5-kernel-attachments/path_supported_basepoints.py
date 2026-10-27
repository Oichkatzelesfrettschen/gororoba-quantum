"""Exact path-supported basepoints for the A_5 nullity-8 to nullity-12 incidences."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from functools import partial
from pathlib import Path
from typing import Any, TypeAlias, cast

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NULLITY_EIGHT = HERE.parent / "a5-kernel-bundles-nullity8"
REGULARITY = HERE.parent / "a5-strata-regularity"
EQUATIONS = HERE.parent / "a5-rank-strata-equations"
sys.path.insert(0, str(NULLITY_EIGHT))
sys.path.insert(0, str(REGULARITY))
sys.path.insert(0, str(EQUATIONS))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import boundary_specializations as boundary  # noqa: E402
import strata_regularity as regularity  # noqa: E402
import verify_regularity_independent as independent  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-path-supported-basepoints-v1"
SPLIT_DIMENSION = 15
SINGULAR_MEMORY_LIMIT = "8589934592"
SINGULAR_TIMEOUT_SECONDS = 900
ORBIT_KEYS = {"E8bar": "Ehat", "X+": "Xp", "X-": "Xm", "Va+": "Vap", "Va-": "Vam"}
SOURCE_PATHS = (
    HERE / "path_supported_basepoints.py",
    ROOT / "docs" / "design" / "a5-kernel-attachments-program.md",
    NULLITY_EIGHT / "boundary_specializations.py",
    NULLITY_EIGHT / "boundary-specializations-result.json",
    REGULARITY / "strata_regularity.py",
    REGULARITY / "verify_regularity_independent.py",
    REGULARITY / "result.json",
    EQUATIONS / "rederive_strata_equations.py",
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


def incidences() -> tuple[Incidence, ...]:
    boundary_orbits = tuple(sorted(set(itertools.chain.from_iterable(boundary.INCIDENCES.values()))))
    candidates = tuple(itertools.product(tuple(boundary.INCIDENCES), boundary_orbits))
    selected = parallel.ordered_map(_incidence_candidate, candidates, min_items=1)
    return tuple(sorted(filter(None, selected), key=lambda incidence: cast(Incidence, incidence).name))


def _path_candidate(path: boundary.PathSpec, incidence_name: str) -> boundary.PathSpec | None:
    return path if path.incidence == incidence_name else None


def selected_path_group(incidence: Incidence) -> tuple[RationalVector, tuple[boundary.PathSpec, ...]]:
    candidates = parallel.ordered_map(
        partial(_path_candidate, incidence_name=incidence.name), boundary._path_specs(), min_items=1
    )
    paths = tuple(filter(None, candidates))
    _require(bool(paths), f"{incidence.name} has no retained exact path")
    grouped: dict[RationalVector, list[boundary.PathSpec]] = defaultdict(list)
    for path in paths:
        grouped[path.coefficients[0]].append(path)
    ranked = sorted(
        grouped.items(),
        key=lambda item: (-len(item[1]), tuple(str(value) for value in item[0])),
    )
    point, selected = ranked[0]
    return point, tuple(sorted(selected, key=lambda path: path.approach))


def _parse_singular(stdout: str, stderr: str, return_code: int) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in stdout.splitlines():
        match = re.match(r"^RESULT (\S+) (.*)$", line.strip())
        if match:
            parsed[match.group(1)] = match.group(2).strip()
    if return_code != 0 or "error" in stderr.lower() or "? " in stdout:
        parsed["singular_error"] = (stderr + stdout)[-4000:]
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
        raise RuntimeError("Singular exceeded the 15-minute sub-step limit") from error
    return _parse_singular(process.stdout, process.stderr, process.returncode)


def _germ_script(incidence: Incidence, point: Sequence[Fraction], slice_columns: Sequence[int]) -> str:
    ideals = regularity.closure_ideals()
    slice_names = tuple(f"t{index + 1}" for index in range(len(slice_columns)))
    substitutions = tuple(
        f"({point[coordinate]}+{slice_names[slice_columns.index(coordinate)]})"
        if coordinate in slice_columns
        else str(point[coordinate])
        for coordinate in range(SPLIT_DIMENSION)
    )
    zero_substitution = ",".join("0" for _name in slice_names)
    return "\n".join(
        [
            regularity.head(),
            f"ideal G = {regularity.gens_text(ideals[incidence.source_key])};",
            f"ring r1 = 0, ({','.join(slice_names)}), dp;",
            f"map phi = r, {','.join(substitutions)};",
            "list L = minAssGTZ(phi(G)); list C; int nc = 0;",
            "for (int i = 1; i <= size(L); i++) { if (size(reduce(L[i], std(maxideal(1)))) == 0) { "
            "nc++; C[nc] = L[i]; } }",
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
            "quit;",
        ]
    )


def _result_generators(result: dict[str, str]) -> tuple[str, ...]:
    count = int(result["tangent_generator_count"])
    return tuple(result[f"tangent_generator_{index}"] for index in range(1, count + 1))


def _sympy_polynomial(text: str, symbols: Sequence[sp.Symbol]) -> sp.Expr:
    local_symbols = {str(symbol): symbol for symbol in symbols}
    return sp.expand(sp.sympify(text.replace("^", "**"), locals=local_symbols))


def _normal_basis(point: Sequence[Fraction], slice_columns: Sequence[int]) -> tuple[sp.Matrix, int]:
    tangent_matrix = sp.Matrix(regularity.h_generators(point)).T
    tangent_columns = tangent_matrix.columnspace()
    slice_basis = tuple(sp.eye(SPLIT_DIMENSION)[:, coordinate] for coordinate in slice_columns)
    full_basis = sp.Matrix.hstack(*tangent_columns, *slice_basis)
    _require(full_basis.shape == (SPLIT_DIMENSION, SPLIT_DIMENSION), "normal decomposition is not square")
    _require(full_basis.rank() == SPLIT_DIMENSION, "orbit tangents and slice columns do not span")
    return full_basis, len(tangent_columns)


def _path_projection(
    path: boundary.PathSpec,
    point: RationalVector,
    slice_columns: Sequence[int],
    slice_symbols: Sequence[sp.Symbol],
    tangent_generators: Sequence[sp.Expr],
) -> dict[str, Any]:
    full_basis, tangent_dimension = _normal_basis(point, slice_columns)
    decomposed = full_basis.inv() * sp.Matrix(path.coefficients[1])
    normal_coordinates = tuple(sp.expand(value) for value in decomposed[tangent_dimension:, 0])
    substitutions = dict(zip(slice_symbols, normal_coordinates, strict=True))
    tangent_values = tuple(sp.expand(generator.subs(substitutions)) for generator in tangent_generators)
    direction_in_tangent_cone = all(value == 0 for value in tangent_values)
    curve = boundary._curve_certificate(path)
    return {
        "approach": path.approach,
        "normal_coordinates": list(map(str, normal_coordinates)),
        "tangent_generator_values": list(map(str, tangent_values)),
        "direction_in_tangent_cone": direction_in_tangent_cone,
        "curve_containment_verified": curve["closure_containment_proved"],
        "curve_certificate_pass": curve["pass"],
        "pass": direction_in_tangent_cone and bool(curve["pass"]),
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


def _analyze_incidence(incidence: Incidence) -> dict[str, Any]:
    point, paths = selected_path_group(incidence)
    point_pattern = independent.pattern(point)
    expected_pattern = independent.pattern(independent.REPS[incidence.boundary_orbit])
    point_nullity = independent.nullity_ly(point)
    expected_nullity = independent.NULLITY[incidence.boundary_orbit]
    orbit_dimension = independent.orbit_dim(point)
    expected_orbit_dimension = independent.DIMS[incidence.boundary_orbit]
    slice_columns = tuple(
        regularity.transverse_columns(
            point, regularity.COLUMN_ORDER.get(incidence.boundary_key, range(SPLIT_DIMENSION))
        )
    )
    slice_symbols = tuple(sp.symbols(f"t1:{len(slice_columns) + 1}"))
    singular_result = _run_singular(_germ_script(incidence, point, slice_columns))
    _require(
        "singular_error" not in singular_result,
        f"Singular failed on {incidence.name}: {singular_result.get('singular_error')}",
    )
    tangent_generator_text = _result_generators(singular_result)
    tangent_generators = tuple(_sympy_polynomial(text, slice_symbols) for text in tangent_generator_text)
    path_rows = parallel.ordered_map(
        partial(
            _path_projection,
            point=point,
            slice_columns=slice_columns,
            slice_symbols=slice_symbols,
            tangent_generators=tangent_generators,
        ),
        paths,
        min_items=1,
    )
    expected_germ = regularity.EXPECTED_GERMS[(incidence.source_key, incidence.boundary_key)]
    observed_germ = (
        int(singular_result["germ_dimension"]),
        int(singular_result["tangent_multiplicity"]),
        int(singular_result["germ_embedding_dimension"]),
        int(singular_result["germ_component_count"]),
    )
    expected_projection = (expected_germ[0], expected_germ[1], expected_germ[2], expected_germ[4])
    mutation_control = None
    if incidence.name == "W8->B9":
        comparison_tasks = (paths[0], _mutated_path(paths[0]))
        comparison_rows = parallel.ordered_map(
            partial(
                _path_projection,
                point=point,
                slice_columns=slice_columns,
                slice_symbols=slice_symbols,
                tangent_generators=tangent_generators,
            ),
            comparison_tasks,
            min_items=1,
        )
        baseline, mutated = comparison_rows
        mutation_control = {
            "name": "add_middle_coordinate_to_W8_path",
            "input_change": "add the split middle-coordinate basis vector to the exact first-order path coefficient",
            "baseline": baseline,
            "mutated": mutated,
            "detected": bool(baseline["pass"])
            and not bool(mutated["pass"])
            and bool(baseline["direction_in_tangent_cone"])
            and not bool(mutated["direction_in_tangent_cone"]),
        }
    passed = (
        point_pattern == expected_pattern
        and point_nullity == expected_nullity
        and orbit_dimension == expected_orbit_dimension
        and len(slice_columns) + orbit_dimension == SPLIT_DIMENSION
        and observed_germ == expected_projection
        and int(singular_result["tangent_dimension"]) == expected_germ[0]
        and all(bool(row["pass"]) for row in path_rows)
        and (mutation_control is None or bool(mutation_control["detected"]))
    )
    return {
        "incidence": incidence.name,
        "source_orbit": incidence.source_orbit,
        "boundary_orbit": incidence.boundary_orbit,
        "selected_point": list(map(str, point)),
        "path_count_at_selected_point": len(paths),
        "path_approaches": [path.approach for path in paths],
        "membership_pattern": point_pattern,
        "expected_membership_pattern": expected_pattern,
        "real_left_nullity": point_nullity,
        "expected_real_left_nullity": expected_nullity,
        "orbit_dimension": orbit_dimension,
        "expected_orbit_dimension": expected_orbit_dimension,
        "slice_columns_zero_based": list(slice_columns),
        "slice_dimension": len(slice_columns),
        "slice_complements_orbit": len(slice_columns) + orbit_dimension == SPLIT_DIMENSION,
        "germ": {
            "observed_dimension_multiplicity_embedding_components": list(observed_germ),
            "expected_dimension_multiplicity_embedding_components": list(expected_projection),
            "matches_regularity_record": observed_germ == expected_projection,
            "tangent_generators": list(tangent_generator_text),
        },
        "paths": path_rows,
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
    rows = parallel.ordered_map(_analyze_incidence, incidences(), min_items=1)
    input_rows = parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)
    mutation_controls = tuple(row["mutation_control"] for row in rows if row["mutation_control"] is not None)
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
                "The record reconciles exact path-supported boundary points and their transverse germs. It does not "
                "transport kernels between boundary points or determine a Gauss-graph fiber."
            ),
        },
        "summary": {
            "incidence_count": len(rows),
            "selected_basepoint_count": len(set(tuple(row["selected_point"]) for row in rows)),
            "retained_path_count": sum(int(row["path_count_at_selected_point"]) for row in rows),
        },
        "incidences": rows,
        "mutation_controls": list(mutation_controls),
        "falsifier": (
            "An incidence lacks a path-supported point; a selected point has the wrong orbit pattern or nullity; a "
            "slice fails to complement the orbit tangent space; a germ invariant differs from the orbit-constant "
            "regularity value; an admitted path misses the transverse tangent cone; or the geometric-input mutation "
            "survives."
        ),
        "pass": passed,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the path-supported basepoint record failed")
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
