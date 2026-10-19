"""Offline, source-bound Tuna-17 conditional-Ramsey proposal; never submits jobs.

The four conditional rates identify the repository's static diagonal pair
model H/hbar = (omega_A Z_A + omega_B Z_B + J Z_A Z_B)/2 without a CZ gate.
Eight induced matchings isolate active pairs from other active nearest
neighbors. Both probe directions, neighbor preparations, quadratures and
six physical delays give 384 Ramsey circuits. Four pair-state assignment
calibrations per matching bring the proposal to 416 circuits, in 139 batches
of at most three. This is a proposed acquisition, not a hardware result.

Each circuit initializes all 17 qubits. Neighbor preparation has two 20 ns
pulses in both conditions, separated from probe preparation by a full-register
barrier. Explicit waits and barriers match every other qubit's duration.
The documented primitive durations are planning inputs, not a retrieved
compiler schedule. No pulse control, automatic execution or QX submission
is provided by this module.

Usage: python scripts/qi_zz_map.py (--write DIR | --check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import ast
import cmath
import hashlib
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_platform import HARDWARE_BATCH_CIRCUITS, HARDWARE_PAUSE_SECONDS  # noqa: E402

from parallel import ordered_map  # noqa: E402

CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
OPERATIONS = ROOT / "docs/notes/quantum_inspire/site/kbase_tuna-operational-specifics.md"
MODEL_SOURCE = ROOT / "gororoba_quantum/conditional_ramsey.py"
MODEL_NOTE = ROOT / "docs/notes/conditional_ramsey_hamiltonian.md"
PLATFORM_SOURCE = ROOT / "scripts/qi_platform.py"
DEFAULT_OUT = ROOT / "results/quantum_inspire/cases/zz_map_tuna_17"
PLAN_SCHEMA = "qi-zz-map-plan-v1"
CASE_SCHEMA = "qi-zz-map-cases-v1"
WAIT_CYCLE_NS = 20
BASELINE_DT_NS = 4
DELAY_CYCLES = (0, 25, 100, 400, 1000, 2000)
# Deliberately nonmonotonic in acquisition order; analysis sorts physical time.
DELAY_ORDER = (0, 400, 25, 2000, 100, 1000)
PAIR_STATES = ((0, 0), (0, 1), (1, 0), (1, 1))
DIRECTIONS = ("a_probe", "b_probe")
QUADRATURES = ("x", "y")


def digest(data: str | bytes) -> str:
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def json_text(data: Any) -> str:
    return json.dumps(data, indent=1, sort_keys=True, allow_nan=False) + "\n"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def source_inputs(catalogue_path: Path) -> tuple[dict[str, Any], dict[str, str]]:
    catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    backend = next(b for b in catalogue["backend_types"] if b["identifier"] == "tuna_17")
    require(backend["nqubits"] == 17, "Tuna-17 register changed: review the proposal")
    needed = {"init", "measure", "wait", "barrier", "X90", "mX90", "Y90", "mY90"}
    require(needed <= set(backend["gateset"]), "catalogue lacks a required native instruction")
    require(backend["max_jobs_per_batch_job"] == 5, "batch ceiling changed: review the proposal")
    require(HARDWARE_BATCH_CIRCUITS == 3, "hardware submission policy changed: review the proposal")
    operations = OPERATIONS.read_text(encoding="utf-8")
    require(
        "20 ns" in operations and "60 ns" in operations and "ALAP" in operations,
        "Tuna primitive timing source changed: review explicit durations",
    )
    require("dt = 4 ns" in MODEL_NOTE.read_text(encoding="utf-8"), "baseline dt source changed")
    tree = ast.parse(MODEL_SOURCE.read_text(encoding="utf-8"))
    baseline_delays = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "DELAYS_DT" for target in node.targets)
    )
    require(
        tuple(t * BASELINE_DT_NS for t in baseline_delays) == tuple(t * WAIT_CYCLE_NS for t in DELAY_CYCLES),
        "physical delay ladder differs from the retained conditional-Ramsey design",
    )
    sources = {
        "catalogue_sha256": digest(catalogue_path.read_bytes()),
        "tuna_operations_sha256": digest(OPERATIONS.read_bytes()),
        "conditional_ramsey_source_sha256": digest(MODEL_SOURCE.read_bytes()),
        "conditional_ramsey_note_sha256": digest(MODEL_NOTE.read_bytes()),
        "qi_platform_source_sha256": digest(PLATFORM_SOURCE.read_bytes()),
        "proposal_builder_sha256": digest(Path(__file__).read_bytes()),
    }
    return backend, sources


def undirected_edges(backend: dict[str, Any]) -> list[tuple[int, int]]:
    edges = sorted({tuple(sorted(edge)) for edge in backend["topology"]})
    require(
        len(edges) == 24 and all(len(edge) == 2 and edge[0] != edge[1] for edge in edges),
        "Tuna-17 topology changed: expected 24 simple undirected edges",
    )
    require(all(0 <= q < backend["nqubits"] for edge in edges for q in edge), "invalid edge endpoint")
    return edges


def induced_matchings(edges: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """Exact deterministic coloring of the squared line graph, using DSATUR.

    Sharing a qubit or having any direct connection between the endpoints of
    two active pairs creates a conflict. The backtracking choices depend on
    earlier choices; this is one search, not an independent-item CPU loop.
    """
    connections = {frozenset(edge) for edge in edges}
    conflicts = [
        [
            j
            for j, other in enumerate(edges)
            if i != j and any(a == b or frozenset((a, b)) in connections for a in edge for b in other)
        ]
        for i, edge in enumerate(edges)
    ]

    def color_with(count: int) -> list[int] | None:
        colors = [-1] * len(edges)

        def search(depth: int) -> bool:
            if depth == len(edges):
                return True
            vertex = max(
                (i for i, color in enumerate(colors) if color < 0),
                key=lambda i: (len({colors[j] for j in conflicts[i] if colors[j] >= 0}), len(conflicts[i]), -i),
            )
            unavailable = {colors[j] for j in conflicts[vertex]}
            for color in range(min(count, max(colors) + 2)):
                if color not in unavailable:
                    colors[vertex] = color
                    if search(depth + 1):
                        return True
                    colors[vertex] = -1
            return False

        return colors if search(0) else None

    for count in range(1, len(edges) + 1):
        colors = color_with(count)
        if colors is not None:
            return [[edge for edge, color in zip(edges, colors, strict=True) if color == c] for c in range(count)]
    raise ValueError("unreachable: distinct colors always color a finite graph")


def row_specs(packings: list[list[tuple[int, int]]]) -> list[dict[str, Any]]:
    """Freeze all choices before parallel rendering; preserve acquisition order."""
    rows: list[dict[str, Any]] = []
    for pack_index, pairs in enumerate(packings):
        packing_id = f"pack-{pack_index:02d}"
        for state in PAIR_STATES:
            rows.append(
                {
                    "file": f"{packing_id}-readout-{state[0]}{state[1]}.cq",
                    "kind": "readout",
                    "packing_id": packing_id,
                    "prepared_pair": list(state),
                    "pairs": [{"edge": list(edge), "prepared": list(state)} for edge in pairs],
                }
            )
        for delay_index, delay in enumerate(DELAY_ORDER):
            directions = DIRECTIONS if delay_index % 2 == 0 else tuple(reversed(DIRECTIONS))
            quadratures = QUADRATURES if delay_index % 2 == 0 else tuple(reversed(QUADRATURES))
            conditions = (0, 1) if delay_index % 2 == 0 else (1, 0)
            for direction, quadrature, condition in itertools.product(directions, quadratures, conditions):
                probe_index = 0 if direction == "a_probe" else 1
                rows.append(
                    {
                        "file": f"{packing_id}-{direction}-n{condition}-{quadrature}-t{delay:04d}.cq",
                        "kind": "conditional_ramsey",
                        "packing_id": packing_id,
                        "direction": direction,
                        "neighbor_state": condition,
                        "quadrature": quadrature,
                        "delay_cycles": delay,
                        "delay_seconds": delay * WAIT_CYCLE_NS * 1e-9,
                        "ideal_probe_p1_at_zero_detuning": 0.0 if quadrature == "x" else 0.5,
                        "pairs": [
                            {
                                "edge": list(edge),
                                "probe": edge[probe_index],
                                "neighbor": edge[1 - probe_index],
                                "neighbor_state": condition,
                            }
                            for edge in pairs
                        ],
                    }
                )
    return rows


def stage(lines: list[str], nqubits: int, gates: dict[int, str]) -> None:
    """One 20 ns instruction per qubit and a full-register barrier."""
    lines.extend(f"{gates.get(qubit, 'wait(1)')} q[{qubit}]" for qubit in range(nqubits))
    lines.append("barrier q")


def render_circuit(item: tuple[int, dict[str, Any]]) -> tuple[dict[str, Any], str]:
    nqubits, spec = item
    row = dict(spec)
    lines = [
        "version 3.0",
        "",
        f"qubit[{nqubits}] q",
        f"bit[{nqubits}] b",
        "",
        "// Proposed conditional-Ramsey acquisition: no coupler controls or CZ.",
        f"// {row['file']}",
        "init q",
        "barrier q",
    ]
    if row["kind"] == "readout":
        states = {q: state for pair in row["pairs"] for q, state in zip(pair["edge"], pair["prepared"], strict=True)}
    else:
        states = {pair["neighbor"]: pair["neighbor_state"] for pair in row["pairs"]}
    # X90;mX90 prepares 0 and X90;X90 prepares 1, with the same pulse count.
    stage(lines, nqubits, {q: "X90" for q in states})
    stage(lines, nqubits, {q: "X90" if state else "mX90" for q, state in states.items()})
    probes = {pair["probe"] for pair in row["pairs"]} if row["kind"] == "conditional_ramsey" else set()
    stage(lines, nqubits, {q: "Y90" for q in probes})
    delay = row.get("delay_cycles", 0)
    if delay:
        lines.append(f"wait({delay}) q")
    lines.append("barrier q")
    readout = "mY90" if row.get("quadrature", "x") == "x" else "X90"
    stage(lines, nqubits, {q: readout for q in probes})
    lines.extend(["b = measure q", ""])
    code = "\n".join(lines)
    row["sha256"] = digest(code)
    row["cz_count"] = 0
    row["documented_fixed_primitive_ns_excluding_init_measure"] = 80
    row["all_qubits_initialized"] = True
    row["bit_order"] = "qubit_0_rightmost"
    return row, code


def build(catalogue_path: Path = CATALOGUE, shots: int | None = None) -> dict[str, str]:
    backend, sources = source_inputs(catalogue_path)
    shots = backend["default_number_of_shots"] if shots is None else shots
    require(isinstance(shots, int) and 0 < shots <= backend["max_number_of_shots"], "invalid proposed shot count")
    edges = undirected_edges(backend)
    packings = induced_matchings(edges)
    require(len(packings) == 8, "induced packing changed: review budget and analysis")
    specs = row_specs(packings)
    rendered = ordered_map(render_circuit, [(backend["nqubits"], row) for row in specs])
    files: dict[str, str] = {}
    all_rows: list[dict[str, Any]] = []
    batches: list[dict[str, Any]] = []
    limit = min(backend["max_jobs_per_batch_job"], HARDWARE_BATCH_CIRCUITS)
    for start in range(0, len(rendered), limit):
        directory = f"batch-{start // limit:03d}"
        batch_rows = []
        for row, code in rendered[start : start + limit]:
            files[f"{directory}/{row['file']}"] = code
            batch_rows.append(row)
            all_rows.append({**row, "batch_directory": directory})
        cases = {
            "schema": CASE_SCHEMA,
            "status": "proposed_not_submitted",
            "backend": backend["identifier"],
            "backend_type_id": backend["id"],
            "nqubits": backend["nqubits"],
            "shots": shots,
            "plan_schema": PLAN_SCHEMA,
            "source_digests": sources,
            "batch_index": start // limit,
            "circuits": batch_rows,
        }
        case_text = json_text(cases)
        files[f"{directory}/cases.json"] = case_text
        batches.append({"directory": directory, "circuits": len(batch_rows), "cases_sha256": digest(case_text)})
    ramsey_count = sum(row["kind"] == "conditional_ramsey" for row in all_rows)
    edge_observations = sum(len(row["pairs"]) * shots for row in all_rows if row["kind"] == "conditional_ramsey")
    programmed_ns = sum(80 + row.get("delay_cycles", 0) * WAIT_CYCLE_NS for row in all_rows)
    primitive_scenarios = {
        f"initialization_{init_us}_us": (programmed_ns + len(all_rows) * (init_us * 1000 + 800)) * shots * 1e-9
        for init_us in (200, 500)
    }
    plan = {
        "schema": PLAN_SCHEMA,
        "status": "proposed_not_submitted",
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": backend["nqubits"],
        "shots": shots,
        "source_digests": sources,
        "edges": [list(edge) for edge in edges],
        "packings": [
            {"packing_id": f"pack-{i:02d}", "edges": [list(edge) for edge in packing]}
            for i, packing in enumerate(packings)
        ],
        "delay_cycles": list(DELAY_CYCLES),
        "wait_cycle_ns": WAIT_CYCLE_NS,
        "acquisition_delay_order_cycles": list(DELAY_ORDER),
        "model": {
            "hamiltonian": "H/hbar=(omega_A*Z_A+omega_B*Z_B+J*Z_A*Z_B)/2",
            "z_zero_eigenvalue": 1,
            "rate_order": ["a_given_b0", "a_given_b1", "b_given_a0", "b_given_a1"],
            "design_rows": [[1, 0, 1], [1, 0, -1], [0, 1, 1], [0, 1, -1]],
            "omega_a": "(nu_a0+nu_a1)/2",
            "omega_b": "(nu_b0+nu_b1)/2",
            "j_a_rad_per_second": "(nu_a0-nu_a1)/2",
            "j_b_rad_per_second": "(nu_b0-nu_b1)/2",
            "directional_residual_rad_per_second": "(nu_a0-nu_a1)-(nu_b0-nu_b1)",
            "zz_conditional_shift_1_minus_0_hz": "(nu_a1-nu_a0)/(2*pi)=-J/pi",
            "zz_j_hz": "J/(2*pi)",
            "matched_idle_detuning_difference_hz": "(omega_A-omega_B)/(2*pi)",
            "first_interval_alias_bound_hz": 1 / (2 * DELAY_CYCLES[1] * WAIT_CYCLE_NS * 1e-9),
        },
        "measurement": {
            "probe_preparation": "Y90",
            "x_readout": "mY90",
            "y_readout": "X90",
            "expectation": "1-2*P1",
            "phase": "atan2(Y,X)",
            "neighbor_prep_0": ["X90", "mX90"],
            "neighbor_prep_1": ["X90", "X90"],
            "matched_neighbor_prep_ns": 40,
            "pair_assignment_calibrations": [list(state) for state in PAIR_STATES],
            "assignment_convention": "A[observed_index,prepared_index]; index=2*bit_a+bit_b for canonical edge a<b",
            "bit_order": "qubit_0_rightmost",
            "neighbor_outcome": "retain all joint outcomes; report unconditional and conditioned estimates",
        },
        "analysis_policy": {
            "assignment_condition_number_max": 100.0,
            "retained_fraction_lower_sigma": 3.0,
            "retained_fraction_lower_bound_min": 0.10,
            "radial_amplitude_min": 0.05,
            "radial_signal_to_noise_min": 5.0,
            "unwrap_innovation_sigma": 3.0,
            "unwrap_rule": "the 3-sigma phase-innovation interval stays strictly inside the chosen +/-pi branch",
            "frequency_assumption": (
                "every conditional rate lies strictly inside +/-1 MHz; global aliases are unidentifiable"
            ),
            "corrected_probabilities": (
                "never clip; flag any out-of-range point; >3-sigma nonphysicality blocks inference"
            ),
            "primary_delay_requirement": "all six delays; no automatic shorter-prefix fit",
            "regression": "ordinary least squares with free intercept and propagated joint-calibration covariance",
            "linearity_and_reciprocity_flag_p": 0.01,
            "discovery_multiple_testing": "Holm familywise alpha=0.05 over all 24 edges; invalid edges receive p=1",
            "cross_edge_covariance": "not used for per-edge inference or Holm; no independent-edge assumption",
            "calibration_assumption": (
                "pair assignment channel stable within a packing; finite state-preparation error remains"
            ),
        },
        "cost": {
            "ramsey_jobs": ramsey_count,
            "readout_jobs": len(all_rows) - ramsey_count,
            "total_jobs": len(all_rows),
            "batches": len(batches),
            "max_jobs_per_batch": limit,
            "catalogue_max_jobs_per_batch": backend["max_jobs_per_batch_job"],
            "hardware_policy_max_jobs_per_batch": HARDWARE_BATCH_CIRCUITS,
            "hardware_policy_pause_seconds": HARDWARE_PAUSE_SECONDS,
            "minimum_interbatch_pause_seconds": max(0, len(batches) - 1) * HARDWARE_PAUSE_SECONDS,
            "pause_scope": (
                "account-wide hardware spacing only; excludes the initial wait, execution, collection, "
                "queueing, calibration and other sessions' jobs"
            ),
            "shots_per_job": shots,
            "total_job_shots": len(all_rows) * shots,
            "ramsey_edge_observations": edge_observations,
            "cz_gates": 0,
            "per_job_service_execution_limit_seconds": backend["job_execution_time_limit"],
            "qpu_seconds": None,
            "monetary_charge": None,
            "documented_primitive_scenarios_seconds": primitive_scenarios,
            "primitive_scenario_scope": "arithmetic only; excludes all unspecified repetition, job and queue overhead",
            "timing_status": "documented primitives only; no retrieved compiled schedule or runtime quote",
        },
        "interpretation": {
            "primary": "effective conditional idle ZZ and matched-idle detuning differences on 24 edges",
            "acquisition_disposition": (
                "complete offline design reference; revise the delay and calibration plan before acquisition "
                "because the current interbatch pauses and retained short-coherence/drift observations "
                "do not support executing the unchanged 139-batch series"
            ),
            "scope": "no direct active-pair cross-edge in each packing; nonedge interactions remain possible",
            "does_not_identify": [
                "coupler flux setting",
                "coupler-only cause",
                "CZ gate fidelity",
                "cause of zero-divisor contrast loss",
                "cause of Q1/Q2 driven crosstalk",
            ],
            "nonedge_q1_q2": "not acquired here; a separate diagnostic, outside the default cost",
            "uncertainty": "preserve same-shot pair covariance and propagate all four assignment columns",
            "phase_fit": "report low-contrast, alias, nonlinearity and direction-agreement failures explicitly",
            "preparation": "a free intercept absorbs static prep phases; drive transients may still bias a slope",
        },
        "circuits": all_rows,
        "batches": batches,
    }
    validate_plan(plan, files)
    files["plan.json"] = json_text(plan)
    return files


def validate_plan(plan: dict[str, Any], files: dict[str, str]) -> None:
    edges = {tuple(edge) for edge in plan["edges"]}
    packed = [tuple(edge) for packing in plan["packings"] for edge in packing["edges"]]
    require(set(packed) == edges and len(packed) == len(edges), "edge coverage is not exactly once")
    for packing in plan["packings"]:
        for left, right in itertools.combinations(packing["edges"], 2):
            require(not set(left) & set(right), "packing has overlapping pairs")
            require(
                not any(tuple(sorted((a, b))) in edges for a in left for b in right),
                "packing contains a cross-edge between active pairs",
            )
    counts: Counter[tuple[Any, ...]] = Counter()
    readout_counts: Counter[tuple[Any, ...]] = Counter()
    for row in plan["circuits"]:
        path = f"{row['batch_directory']}/{row['file']}"
        require(digest(files[path]) == row["sha256"], "circuit hash mismatch")
        require(files[path].count("init q\n") == 1 and "CZ " not in files[path], "invalid Ramsey preparation")
        if row["kind"] == "conditional_ramsey":
            for pair in row["pairs"]:
                require({pair["probe"], pair["neighbor"]} == set(pair["edge"]), "incorrect pair roles")
                counts[
                    (
                        tuple(pair["edge"]),
                        row["direction"],
                        row["neighbor_state"],
                        row["quadrature"],
                        row["delay_cycles"],
                    )
                ] += 1
        elif row["kind"] == "readout":
            readout_counts[(row["packing_id"], tuple(row["prepared_pair"]))] += 1
        else:
            raise ValueError("unexpected circuit kind")
    expected = set(itertools.product(sorted(edges), DIRECTIONS, (0, 1), QUADRATURES, DELAY_CYCLES))
    require(set(counts) == expected and all(count == 1 for count in counts.values()), "conditional grid incomplete")
    expected_calibrations = set(itertools.product((p["packing_id"] for p in plan["packings"]), PAIR_STATES))
    require(
        set(readout_counts) == expected_calibrations and all(count == 1 for count in readout_counts.values()),
        "pair-state assignment calibration grid incomplete",
    )
    for batch in plan["batches"]:
        require(0 < batch["circuits"] <= plan["cost"]["max_jobs_per_batch"], "batch limit exceeded")
        require(digest(files[f"{batch['directory']}/cases.json"]) == batch["cases_sha256"], "case hash mismatch")
    require(plan["cost"]["ramsey_jobs"] == 384 and plan["cost"]["readout_jobs"] == 32, "cost changed")
    require(plan["cost"]["max_jobs_per_batch"] == HARDWARE_BATCH_CIRCUITS, "hardware batch policy differs")
    require(plan["cost"]["total_jobs"] == 416 and plan["cost"]["batches"] == 139, "packing cost changed")
    require(
        plan["cost"]["minimum_interbatch_pause_seconds"] == 138 * HARDWARE_PAUSE_SECONDS,
        "account-wide interbatch pause budget changed",
    )


def write(directory: Path, catalogue: Path, shots: int | None) -> None:
    require(not list(directory.glob("**/submission.json")), "refusing to overwrite a submitted proposal")
    files = build(catalogue, shots)
    for relative, content in files.items():
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(
        f"Tuna ZZ proposal: 416 circuits, 139 batches, {json.loads(files['plan.json'])['shots']} shots/job "
        f"-> {directory}"
    )


def check(directory: Path, catalogue: Path, shots: int | None) -> None:
    files = build(catalogue, shots)
    existing = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
    require(existing == set(files), f"proposal file set differs from regeneration: {sorted(existing ^ set(files))}")
    for relative, content in files.items():
        require((directory / relative).read_text(encoding="utf-8") == content, f"{relative}: differs from regeneration")
    print(f"Tuna ZZ proposal: {len(files)} source-bound files match; 24 edges, 384 Ramsey + 32 readout jobs")


def self_test(catalogue: Path = CATALOGUE) -> None:
    files = build(catalogue)
    plan = json.loads(files["plan.json"])
    require(plan["cost"]["total_job_shots"] == 416 * plan["shots"], "shot budget differs")
    require(
        [batch["circuits"] for batch in plan["batches"]] == [HARDWARE_BATCH_CIRCUITS] * 138 + [2],
        "three-circuit batch partition differs",
    )
    require(math.isclose(plan["model"]["first_interval_alias_bound_hz"], 1e6), "delay ladder alias bound changed")
    # Small matrix identities certify the emitted native rotation signs;
    # these are algebraic checks, not a backend simulation or timing claim.
    errors = ordered_map(
        rotation_law_error, list(itertools.product((-2.3, -math.pi / 2, -0.2, 0.0, 0.7, math.pi / 2, 2.8), QUADRATURES))
    )
    require(max(errors) < 1e-14, "emitted analysis pulse does not read the specified quadrature")
    for state in (0, 1):
        prepared = rotate(rotate((1.0 + 0j, 0j), "x", math.pi / 2), "x", math.pi / 2 if state else -math.pi / 2)
        require(abs(abs(prepared[1]) ** 2 - state) < 1e-14, "matched two-pulse neighbor preparation failed")
    omega_a, omega_b, j = 2 * math.pi * 30e3, -2 * math.pi * 12e3, 2 * math.pi * 8e3
    rates = [omega_a + j, omega_a - j, omega_b + j, omega_b - j]
    require(math.isclose((rates[0] - rates[1]) / 2, j), "A-direction J sign")
    require(math.isclose((rates[2] - rates[3]) / 2, j), "B-direction J sign")
    require(
        math.isclose((rates[0] + rates[1] - rates[2] - rates[3]) / 2, omega_a - omega_b), "matched-idle detuning sign"
    )
    changed = dict(files)
    sample = plan["circuits"][4]
    path = f"{sample['batch_directory']}/{sample['file']}"
    changed[path] = changed[path].replace("mY90", "Y90", 1)
    try:
        validate_plan(plan, changed)
    except ValueError:
        pass
    else:
        raise ValueError("circuit corruption escaped manifest validation")
    print(
        "Tuna ZZ: complete induced packing, condition grid, timing ladder, rate conventions and hash mutation checked"
    )


def rotate(state: tuple[complex, complex], axis: str, angle: float) -> tuple[complex, complex]:
    """Two-by-two Pauli rotation identity used only by the circuit contract."""
    a, b = state
    c, s = math.cos(angle / 2), math.sin(angle / 2)
    if axis == "x":
        return c * a - 1j * s * b, -1j * s * a + c * b
    if axis == "y":
        return c * a - s * b, s * a + c * b
    if axis == "z":
        return cmath.exp(-1j * angle / 2) * a, cmath.exp(1j * angle / 2) * b
    raise ValueError(axis)


def rotation_law_error(item: tuple[float, str]) -> float:
    phase, quadrature = item
    prepared = rotate((1.0 + 0j, 0j), "y", math.pi / 2)
    evolved = rotate(prepared, "z", phase)
    analyzed = rotate(evolved, "y", -math.pi / 2) if quadrature == "x" else rotate(evolved, "x", math.pi / 2)
    expected = (1 - (math.cos(phase) if quadrature == "x" else math.sin(phase))) / 2
    return abs(abs(analyzed[1]) ** 2 - expected)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--catalogue", type=Path, default=CATALOGUE)
    parser.add_argument("--shots", type=int, default=None, help="proposed shots; defaults to the retained catalogue")
    args = parser.parse_args()
    if args.write:
        write(args.write, args.catalogue, args.shots)
    elif args.check:
        check(args.check, args.catalogue, args.shots)
    else:
        self_test(args.catalogue)


if __name__ == "__main__":
    main()
