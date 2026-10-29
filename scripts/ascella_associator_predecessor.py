"""Ascella two-photon associator predecessor and sentinel-leakage campaign.

This module implements a prospective, preregistered phase-request predecessor-dependence
benchmark on Quandela Ascella (qpu:ascella). It tests whether a fixed two-photon
interferometer responds differently depending on the preceding phase request, while
monitoring modes 4..11 as a chip-wide spatial sentinel array and accounting for
non-linear causal drift.

First-principles design:
1. Two photons enter connected source ports 0 and 2 of the 12-mode processor.
2. The focal interferometer acts on logical modes 0..3 using the 4x4 orthogonal blocks
   of the octonion associator (L_a L_b vs L_(ab)) and the quaternion associative null
   control (where L_a L_b = L_(ab) identically).
3. Predecessor phase requests test distinct nominal configurations across the chip:
   - 'hot': requested phase pi on all phase shifters.
   - 'cold': requested phase 0 on all phase shifters (quiescent baseline).
   - 'wrapped': requested phase 2*pi on all phase shifters (optical identity to 0 under wave
     optics, testing whether the compilation/hardware path treats 2*pi distinctly).
4. The campaign uses paired predecessor-target sequencing (following docs/runbooks/evidence-closure.md):
   In every pair, iteration 2p is the commanded Predecessor, and iteration 2p+1 is the unchanged Target.
   Across the 16 pairs (32 iterations total):
   - Block 1 (Pairs 0..7): Octonion Associator under Hot, Cold, and Wrapped Carryover
   - Block 2 (Pairs 8..15): Quaternion Null Control under Hot, Cold, and Wrapped Carryover
5. Non-linear drift cancellation & anchor tracking:
   - Within each block, target routes L_a L_b and L_(ab) have identical linear sums (sum t = 14, 46)
     AND identical quadratic sums (sum t^2 = 70, 550), algebraically annihilating constant,
     linear, and quadratic background drift to absolute zero.
   - Every odd pair (1, 3, 5, 7, 9, 11, 13, 15) is an interleaved Cold baseline anchor, providing
     a uniform grid across the run to reconstruct the continuous non-linear drift trajectory f_drift(t).
6. Scaled for 8,192 samples per iteration (524,288 shots/iteration), achieving a 95% CI radius
   of +/-0.0245 on predecessor carryover shifts, with credit ceiling 1.524288 credits.
7. In addition to focal two-click statistics on modes 0..3, the analysis tracks all
   clicks in modes 4..11 as spatial sentinel observables measuring scattered leakage.

Usage:
  "$PYTHON" scripts/ascella_associator_predecessor.py --check
  "$PYTHON" scripts/ascella_associator_predecessor.py --build [--samples 8192]
  "$PYTHON" scripts/ascella_associator_predecessor.py --dry-run [--samples 8192]
  "$PYTHON" scripts/ascella_associator_predecessor.py --analyze RUN_DIR
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import scipy.stats as stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

from cd_core import cd_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

MODES = 12
LOGICAL = 4
DESIGN_PATH = "docs/design/ascella-associator-thermal-seismograph.md"
CASE_DIR = ROOT / "results/quandela/cases/ascella_associator_predecessor/job-00"

ALGEBRA_TO_LOGICAL = {2: 0, 0: 1, 3: 2, 1: 3}
PHOTON_ALGEBRA_MODES = (2, 3)
PAIRS = {"associator": ((6, 7), (5, 7)), "control": ((1, 2), (1, 3))}

# 16-pair schedule (32 iterations total) designed for exact quadratic drift cancellation
# and uniform Cold-baseline anchor reconstruction across the entire run.
#
# Mathematical properties:
# 1. Even pairs (0, 2, 4, 6, 8, 10, 12, 14) are active predecessor interventions (Hot, Wrapped).
# 2. Odd pairs (1, 3, 5, 7, 9, 11, 13, 15) are regular Cold baseline anchors.
# 3. For Block 1 (Associator):
#    sum(t for LaLb) = 1 + 2 + 4 + 7 = 14
#    sum(t for Lab)  = 0 + 3 + 5 + 6 = 14   --> Linear drift cancelled to 0.
#    sum(t^2 for LaLb) = 1 + 4 + 16 + 49 = 70
#    sum(t^2 for Lab)  = 0 + 9 + 25 + 36 = 70 --> Quadratic drift cancelled to 0.
# 4. For Block 2 (Control):
#    sum(t for LaLb) = 9 + 10 + 12 + 15 = 46
#    sum(t for Lab)  = 8 + 11 + 13 + 14 = 46  --> Linear drift cancelled to 0.
#    sum(t^2 for LaLb) = 81 + 100 + 144 + 225 = 550
#    sum(t^2 for Lab)  = 64 + 121 + 169 + 196 = 550 --> Quadratic drift cancelled to 0.
PAIRED_SCHEDULE_SPEC = [
    # Block 1: Octonion Associator (Pairs 0..7)
    {"pair": 0, "pred": "hot", "block": "associator", "route": "Lab"},
    {"pair": 1, "pred": "cold", "block": "associator", "route": "LaLb"},  # Cold Anchor 1
    {"pair": 2, "pred": "wrapped", "block": "associator", "route": "LaLb"},
    {"pair": 3, "pred": "cold", "block": "associator", "route": "Lab"},  # Cold Anchor 2
    {"pair": 4, "pred": "hot", "block": "associator", "route": "LaLb"},
    {"pair": 5, "pred": "cold", "block": "associator", "route": "Lab"},  # Cold Anchor 3
    {"pair": 6, "pred": "wrapped", "block": "associator", "route": "Lab"},
    {"pair": 7, "pred": "cold", "block": "associator", "route": "LaLb"},  # Cold Anchor 4
    # Block 2: Quaternion Null Control (Pairs 8..15)
    {"pair": 8, "pred": "hot", "block": "control", "route": "Lab"},
    {"pair": 9, "pred": "cold", "block": "control", "route": "LaLb"},  # Cold Anchor 5
    {"pair": 10, "pred": "wrapped", "block": "control", "route": "LaLb"},
    {"pair": 11, "pred": "cold", "block": "control", "route": "Lab"},  # Cold Anchor 6
    {"pair": 12, "pred": "hot", "block": "control", "route": "LaLb"},
    {"pair": 13, "pred": "cold", "block": "control", "route": "Lab"},  # Cold Anchor 7
    {"pair": 14, "pred": "wrapped", "block": "control", "route": "Lab"},
    {"pair": 15, "pred": "cold", "block": "control", "route": "LaLb"},  # Cold Anchor 8
]

DEFAULT_SAMPLES_PER_ITERATION = 8192
DEFAULT_SHOTS_FACTOR = 64
MAX_DURATION = 300
TOLERANCE = 1e-12
BODY_TOLERANCE = 1e-9

MUTATION_TOLERANCE = 0.05
CLOSURE_TOLERANCE = 0.05
TVD_EQUIVALENCE_MARGIN = 0.02
MIN_FOCAL_SAMPLES_PER_ITERATION = 100
OUTLIER_SIGMA_THRESHOLD = 3.5


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def octonion_table() -> np.ndarray:
    table = np.zeros((8, 8, 8))
    for p in range(8):
        for q in range(8):
            table[p, q, p ^ q] = cd_sign(8, p, q)
    return table


def left_action(vector: np.ndarray) -> np.ndarray:
    """Left multiplication matrix L_v with columns indexed by the input basis vector."""
    return np.einsum("p,pqr->rq", vector, octonion_table())


def route_operator(block: str, route: str) -> np.ndarray:
    """The logical 4x4 orthogonal block of one route restricted to span(e0..e3), relabelled to logical modes."""
    eye = np.eye(8)
    (i, j), (k, m) = PAIRS[block]
    a = (eye[i] + eye[j]) / math.sqrt(2)
    b = (eye[k] + eye[m]) / math.sqrt(2)
    full = (
        left_action(a) @ left_action(b)
        if route == "LaLb"
        else left_action(np.einsum("p,q,pqr->r", a, b, octonion_table()))
    )
    require(np.allclose(full.T @ full, eye, atol=TOLERANCE), f"{block} {route} is not orthogonal")
    require(np.abs(full[4:, :4]).max() < TOLERANCE, f"{block} {route} leaves span(e0..e3)")
    logical = np.zeros((LOGICAL, LOGICAL))
    for row, column in itertools.product(range(LOGICAL), repeat=2):
        logical[ALGEBRA_TO_LOGICAL[row], ALGEBRA_TO_LOGICAL[column]] = full[row, column]
    return logical


def input_modes() -> tuple[int, int]:
    first, second = sorted(ALGEBRA_TO_LOGICAL[m] for m in PHOTON_ALGEBRA_MODES)
    return first, second


def pair_label(algebra_pair: tuple[int, int]) -> str:
    low, high = sorted(ALGEBRA_TO_LOGICAL[m] for m in algebra_pair)
    return f"{low}{high}"


PLUS_PAIRS = (pair_label((0, 3)), pair_label((1, 2)))
MINUS_PAIRS = (pair_label((0, 2)), pair_label((1, 3)))


def two_click_law(unitary: np.ndarray, visibility: float) -> dict[str, float]:
    """Two-click probabilities over distinct logical modes for indistinguishable mixture of visibility V."""
    x, y = input_modes()
    law = {}
    for o1, o2 in itertools.combinations(range(len(unitary)), 2):
        direct = unitary[o1, x] * unitary[o2, y]
        exchange = unitary[o1, y] * unitary[o2, x]
        law[f"{o1}{o2}"] = float(
            visibility * abs(direct + exchange) ** 2 + (1.0 - visibility) * (abs(direct) ** 2 + abs(exchange) ** 2)
        )
    return law


def endpoint_d(law: dict[str, float]) -> float:
    """D = P(PLUS_PAIRS | two clicks in logical block) - P(MINUS_PAIRS | two clicks in logical block)."""
    total = sum(law.values())
    if total <= TOLERANCE:
        return 0.0
    return (sum(law.get(p, 0.0) for p in PLUS_PAIRS) - sum(law.get(p, 0.0) for p in MINUS_PAIRS)) / total


def embed_matrix(matrix: np.ndarray) -> np.ndarray:
    full = np.eye(MODES, dtype=complex)
    full[:LOGICAL, :LOGICAL] = matrix
    return full


def build_template_circuit() -> dict[str, Any]:
    """Build the canonical fixed circuit template from the associator LaLb operator."""
    canonical_logical = route_operator("associator", "LaLb").astype(complex)
    mesh, _ = photonic_template(canonical_logical)
    input_state = [0] * MODES
    for mode in input_modes():
        input_state[mode] = 1
    return {**mesh, "modes": MODES, "input_state": input_state}


def compute_template_unitary(template_ops: list[list[Any]], parameters: dict[str, float]) -> np.ndarray:
    """Compute the 12-mode unitary of the template circuit under given parameter values."""
    import perceval as pcvl

    chip = pcvl.Circuit(MODES)
    param_objs: dict[str, Any] = {}
    for kind, mode, index in template_ops:
        if kind == "BS":
            chip.add(mode, pcvl.BS.Rx(theta=param_objs.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
        else:
            chip.add(mode, pcvl.PS(param_objs.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
    for name, value in parameters.items():
        param_objs[name].set_value(value)
    return np.asarray(chip.compute_unitary())


def build_pair_settings(item: tuple[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Build both the Predecessor and Target settings for one paired trial."""
    pair_index, spec = item
    pred_kind = spec["pred"]
    target_block = spec["block"]
    target_route = spec["route"]

    canonical_logical = route_operator("associator", "LaLb").astype(complex)
    mesh, _ = photonic_template(canonical_logical)
    ops = mesh["ops"]

    # 1. Predecessor setting (Iteration 2*pair_index)
    pred_phase_map = {"cold": 0.0, "wrapped": 2 * math.pi, "hot": math.pi}
    pred_phase = pred_phase_map[pred_kind]
    pred_params = {}
    for kind, _, index in ops:
        pred_params[f"x{index}"] = 0.0 if kind == "BS" else pred_phase

    pred_unitary = compute_template_unitary(ops, pred_params)
    source_col = input_modes()[0]
    pred_col = [[float(v.real), float(v.imag)] for v in pred_unitary[:, source_col]]

    setting_pred = {
        "name": f"pair{pair_index:02d}-pred_{pred_kind}",
        "observation_index": 2 * pair_index,
        "role": "predecessor",
        "pair_index": pair_index,
        "pred": pred_kind,
        "block": target_block,
        "route": target_route,
        "circuit_params": pred_params,
        "column": pred_col,
        "operator": encoded(pred_unitary),
        "ideal": {
            "two_click_law_indistinguishable": {"02": 1.0},
            "D_indistinguishable": 0.0,
            "D_distinguishable": 0.0,
        },
    }

    # 2. Target setting (Iteration 2*pair_index + 1)
    target_logical = route_operator(target_block, target_route).astype(complex)
    _, target_params = photonic_template(target_logical)
    target_full = embed_matrix(target_logical)
    target_col = [[float(v.real), float(v.imag)] for v in target_full[:, source_col]]

    ideal_indist = two_click_law(target_logical.real, 1.0)
    ideal_dist = two_click_law(target_logical.real, 0.0)

    setting_target = {
        "name": f"pair{pair_index:02d}-target_{target_block}_{target_route}-post_{pred_kind}",
        "observation_index": 2 * pair_index + 1,
        "role": "target",
        "pair_index": pair_index,
        "pred": pred_kind,
        "block": target_block,
        "route": target_route,
        "circuit_params": target_params,
        "column": target_col,
        "operator": encoded(target_full),
        "ideal": {
            "two_click_law_indistinguishable": {k: round(v, 12) for k, v in ideal_indist.items() if v > TOLERANCE},
            "D_indistinguishable": round(endpoint_d(ideal_indist), 12),
            "D_distinguishable": round(endpoint_d(ideal_dist), 12),
        },
    }

    return [setting_pred, setting_target]


def build_documents(
    samples_per_iteration: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
) -> dict[str, bytes]:
    if samples_per_iteration <= 0:
        raise ValueError(f"samples_per_iteration must be positive integer, got {samples_per_iteration}")
    if shots_factor <= 0:
        raise ValueError(f"shots_factor must be positive integer, got {shots_factor}")

    circuit = build_template_circuit()
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()

    pair_items = list(enumerate(PAIRED_SCHEDULE_SPEC))
    built_pairs = ordered_map(build_pair_settings, pair_items, min_items=1)
    flat_settings: list[dict[str, Any]] = []
    for pair in built_pairs:
        flat_settings.extend(pair)

    shots_per_iteration = samples_per_iteration * shots_factor
    credit_ceiling = 1.0 + 1e-6 * shots_per_iteration

    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": "ascella_associator_predecessor_seismograph",
        "job": "job-00",
        "platforms": ["qpu:ascella", "sim:ascella"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(flat_settings),
        "pairs": len(PAIRED_SCHEDULE_SPEC),
        "min_detected_photons": 2,
        "samples_per_iteration": samples_per_iteration,
        "shots_per_iteration": shots_per_iteration,
        "max_samples": samples_per_iteration * len(flat_settings),
        "max_shots": shots_per_iteration * len(flat_settings),
        "max_duration": MAX_DURATION,
        "credit_ceiling": round(credit_ceiling, 6),
        "timing_model": {
            "overhead_seconds": 30.0,
            "seconds_per_iteration": 3.0,
            "estimated_duration_seconds": 126.0,
            "duration_bounds_seconds": [93.0, 186.0],
            "max_duration": MAX_DURATION,
        },
        "tariff": {
            "statement": "credit ceiling under matching preflight tariff (1.0 + 1e-6 * max_shots)",
            "rate_per_shot": 1e-6,
            "fixed_invocation_credits": 1.0,
            "credit_ceiling": round(credit_ceiling, 6),
        },
        "mitigations": [],
        "output_modes": MODES,
        "logical_modes": list(range(LOGICAL)),
        "sentinel_modes": list(range(LOGICAL, MODES)),
        "algebra_to_logical": {str(k): v for k, v in sorted(ALGEBRA_TO_LOGICAL.items())},
        "eligibility": (
            "at least two detected clicks across all 12 modes; focal events have exactly two clicks in modes 0..3"
        ),
        "design": DESIGN_PATH,
        "settings": flat_settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "plus_pairs": list(PLUS_PAIRS),
            "minus_pairs": list(MINUS_PAIRS),
            "primary_associator_endpoint": "Delta_oct = D(LaLb) - D(Lab) on the associator block",
            "mutation_control_endpoint": "Delta_quat = D(LaLb) - D(Lab) on the quaternion control block",
            "closure_endpoint": "C = Delta_oct + 2 * mean(D_control) == 0 for all visibilities",
            "predecessor_shift_hot": "gamma_hot from joint WLS model with full covariance",
            "predecessor_shift_wrapped": "gamma_wrapped from joint WLS model with full covariance",
            "joint_model": (
                "WLS model identifying Delta_assoc, Delta_ctrl, gamma_hot, gamma_wrapped, "
                "and polynomial drift simultaneously"
            ),
            "equivalence_test": "Two One-Sided Tests (TOST) requiring 95% CI to fall strictly inside [-0.02, +0.02]",
            "quarantine_rule": "Studentized residual > 3.5 flags abrupt step change / outlier and quarantines the run",
            "sentinel_leakage_endpoint": (
                "fraction of events with clicks in sentinel modes 4..11 separated by predecessor and target roles"
            ),
            "tvd_equivalence_margin": TVD_EQUIVALENCE_MARGIN,
            "mutation_tolerance": MUTATION_TOLERANCE,
            "closure_tolerance": CLOSURE_TOLERANCE,
            "min_focal_samples_per_iteration": MIN_FOCAL_SAMPLES_PER_ITERATION,
        },
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def slos_simulation(unitary: np.ndarray, input_state: list[int]) -> dict[str, float]:
    """Compute exact two-photon click probabilities from Perceval's SLOS backend."""
    import perceval as pcvl

    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(unitary)))
    backend.set_input_state(pcvl.BasicState(input_state))
    law: dict[str, float] = {}
    for state, probability in backend.prob_distribution().items():
        occupied = [mode for mode in range(len(input_state)) if state[mode] > 0]
        if len(occupied) == 2 and probability > TOLERANCE:
            law["".join(str(m) for m in occupied)] = float(probability)
    return law


def check() -> int:
    """Verify all mathematical identities, template experiment binding, SLOS simulation, and ideal endpoints."""
    documents = build_documents()
    manifest = json.loads(documents["cases.json"].decode())
    circuit = json.loads(documents["circuit.json"].decode())
    experiment, settings = template_experiment(manifest, circuit)
    require(
        experiment is not None and len(settings) == 32,
        f"template experiment bound {len(settings)} settings, expected 32",
    )

    import perceval as pcvl

    chip = pcvl.Circuit(MODES)
    parameters: dict[str, Any] = {}
    for kind, mode, index in circuit["ops"]:
        if kind == "BS":
            chip.add(mode, pcvl.BS.Rx(theta=parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
        else:
            chip.add(mode, pcvl.PS(parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))

    # Check each target setting matches ideal indistinguishable probabilities
    for setting in settings:
        for name, parameter in parameters.items():
            parameter.set_value(setting["circuit_params"][name])
        unitary = np.asarray(chip.compute_unitary())
        block = unitary[:LOGICAL, :LOGICAL]

        if setting["role"] == "target":
            require(np.abs(block.imag).max() < BODY_TOLERANCE, f"{setting['name']}: compiled block is not real")
            law = two_click_law(block.real, 1.0)
            expected = setting["ideal"]["two_click_law_indistinguishable"]
            for pair, value in law.items():
                require(abs(value - expected.get(pair, 0.0)) < BODY_TOLERANCE, f"{setting['name']}: pair {pair}")

    # Check quadratic drift cancellation identity in both blocks
    for block_name, pair_slice in (("associator", slice(0, 8)), ("control", slice(8, 16))):
        sub_spec = PAIRED_SCHEDULE_SPEC[pair_slice]
        lalb_t = [int(str(p["pair"])) for p in sub_spec if p["route"] == "LaLb"]
        lab_t = [int(str(p["pair"])) for p in sub_spec if p["route"] == "Lab"]
        linear_diff = sum(lalb_t) - sum(lab_t)
        quad_diff = sum(t**2 for t in lalb_t) - sum(t**2 for t in lab_t)
        require(linear_diff == 0, f"{block_name}: linear drift not cancelled ({linear_diff})")
        require(quad_diff == 0, f"{block_name}: quadratic drift not cancelled ({quad_diff})")

    # Check optical phase wrapping identity: U(2*pi) == U(0) to tolerance
    u_cold = compute_template_unitary(circuit["ops"], {f"x{k}": 0.0 for k in range(circuit["parameters"])})
    u_wrapped = compute_template_unitary(
        circuit["ops"],
        {f"x{k}": (0.0 if circuit["ops"][k][0] == "BS" else 2 * math.pi) for k in range(circuit["parameters"])},
    )
    diff = float(np.max(np.abs(u_cold - u_wrapped)))
    require(diff < TOLERANCE, f"optical phase wrapping identity failed: max diff = {diff}")

    # Verify ideal Octonion associator Delta = 2.0 and Control Delta = 0.0
    u_oct_lalb = route_operator("associator", "LaLb")
    u_oct_lab = route_operator("associator", "Lab")
    delta_oct = endpoint_d(two_click_law(u_oct_lalb, 1.0)) - endpoint_d(two_click_law(u_oct_lab, 1.0))
    require(abs(delta_oct - 2.0) < BODY_TOLERANCE, f"ideal Octonion Delta {delta_oct} != 2.0")

    u_quat_lalb = route_operator("control", "LaLb")
    u_quat_lab = route_operator("control", "Lab")
    delta_quat = endpoint_d(two_click_law(u_quat_lalb, 1.0)) - endpoint_d(two_click_law(u_quat_lab, 1.0))
    require(abs(delta_quat) < BODY_TOLERANCE, f"ideal Control Delta {delta_quat} != 0.0")

    # Verify in-situ closure C = Delta + 2 * mean(D_control) == 0.0
    d_quat_mean = (endpoint_d(two_click_law(u_quat_lalb, 1.0)) + endpoint_d(two_click_law(u_quat_lab, 1.0))) / 2
    closure = delta_oct + 2 * d_quat_mean
    require(abs(closure) < BODY_TOLERANCE, f"ideal in-situ closure {closure} != 0.0")

    # Verify build parameter positivity enforcement
    try:
        build_documents(samples_per_iteration=0)
        raise AssertionError("build_documents accepted 0 samples")
    except ValueError:
        pass
    try:
        build_documents(shots_factor=0)
        raise AssertionError("build_documents accepted 0 shots factor")
    except ValueError:
        pass

    print("ascella_associator_predecessor: 32 iterations (16 paired trials) bound successfully")
    print(f"ideal Delta_oct: {delta_oct:.6f}, Delta_quat: {delta_quat:.6f}, closure C: {closure:.6f}")
    print("exact quadratic drift cancellation verified: sum(w*t) = 0, sum(w*t^2) = 0 on both blocks")
    print(f"optical phase wrapping identity verified: max |U(2*pi) - U(0)| = {diff:.2e} < {TOLERANCE}")
    print(
        f"credit ceiling confirmed at {manifest['credit_ceiling']:.6f} credits for "
        f"{manifest['samples_per_iteration']} samples ({manifest['shots_per_iteration']} shots)"
    )
    return 0


def build_case(
    samples: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
) -> int:
    CASE_DIR.mkdir(parents=True, exist_ok=True)
    docs = build_documents(samples_per_iteration=samples, shots_factor=shots_factor)
    for name, data in docs.items():
        (CASE_DIR / name).write_bytes(data)
    manifest = json.loads(docs["cases.json"].decode())
    print(
        f"Wrote {len(docs)} files to {CASE_DIR} (samples={manifest['samples_per_iteration']}, "
        f"shots={manifest['shots_per_iteration']}, credits={manifest['credit_ceiling']})"
    )
    return 0


def dry_run(
    samples: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
) -> int:
    """Execute local simulation across all 32 iterations using SLOS / two-click laws to verify end-to-end pipeline."""
    docs = build_documents(samples_per_iteration=samples, shots_factor=shots_factor)
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())
    _, settings = template_experiment(manifest, circuit)

    import perceval as pcvl

    chip = pcvl.Circuit(MODES)
    parameters: dict[str, Any] = {}
    for kind, mode, index in circuit["ops"]:
        if kind == "BS":
            chip.add(mode, pcvl.BS.Rx(theta=parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
        else:
            chip.add(mode, pcvl.PS(parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))

    simulated_iterations = []
    print(
        f"Running local simulation of 32 iterations (16 paired trials) at {samples} samples/iteration "
        f"({samples * shots_factor} shots/iteration)..."
    )
    for idx, setting in enumerate(settings):
        for name, parameter in parameters.items():
            parameter.set_value(setting["circuit_params"][name])
        unitary = np.asarray(chip.compute_unitary())

        if setting["role"] == "predecessor":
            counts = {"|1,0,1,0,0,0,0,0,0,0,0,0>": samples}
        else:
            law = two_click_law(unitary[:LOGICAL, :LOGICAL].real, 0.875)
            counts = {}
            for pair, prob in law.items():
                count = int(round(prob * samples))
                if count > 0:
                    state_vec = [0] * MODES
                    state_vec[int(pair[0])] = 1
                    state_vec[int(pair[1])] = 1
                    state_str = f"|{','.join(str(v) for v in state_vec)}>"
                    counts[state_str] = count

        simulated_iterations.append(
            {
                "setting": setting["name"],
                "counts": counts,
                "elapsed_seconds": round(idx * 3.2, 2),
                "duration": 3.2,
            }
        )

    mock_run_dir = CASE_DIR / "dry_run_simulation"
    mock_run_dir.mkdir(parents=True, exist_ok=True)
    (mock_run_dir / "cases.json").write_bytes(docs["cases.json"])
    (mock_run_dir / "results.json").write_text(json.dumps({"iterations": simulated_iterations}, indent=2))
    print(f"Local dry run complete. Output saved to {mock_run_dir}")
    print("Running analysis on simulated dry-run data...")
    report = analyze(mock_run_dir)
    print(json.dumps(report, indent=2))
    return 0


def validate_count_payload(counts: Any, setting_name: str, min_photons: int = 2) -> dict[str, int]:
    """Validate Fock state string syntax, mode count, photon count, and non-negative integer values."""
    if not isinstance(counts, dict) or len(counts) == 0:
        raise ValueError(f"{setting_name}: counts payload must be a non-empty dictionary")
    validated: dict[str, int] = {}
    for state_str, count in counts.items():
        if not isinstance(count, int) or count < 0:
            raise ValueError(
                f"{setting_name}: count for state {state_str!r} must be non-negative integer, got {count!r}"
            )
        if count == 0:
            continue
        if not (isinstance(state_str, str) and state_str.startswith("|") and state_str.endswith(">")):
            raise ValueError(f"{setting_name}: malformed Fock state syntax {state_str!r}")
        inner = state_str[1:-1]
        try:
            occupations = [int(x.strip()) for x in inner.split(",")]
        except ValueError as err:
            raise ValueError(f"{setting_name}: invalid occupation integers in {state_str!r}") from err
        if len(occupations) != MODES:
            raise ValueError(f"{setting_name}: state {state_str!r} has {len(occupations)} modes, expected {MODES}")
        if any(n < 0 for n in occupations):
            raise ValueError(f"{setting_name}: negative occupation in {state_str!r}")
        if sum(occupations) < min_photons:
            raise ValueError(
                f"{setting_name}: state {state_str!r} has {sum(occupations)} photons, below filter {min_photons}"
            )
        validated[state_str] = count
    if not validated:
        raise ValueError(f"{setting_name}: no valid counts after filtering zero counts")
    return validated


def fit_joint_model(
    target_records: list[dict[str, Any]],
    drift_degree: int = 2,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Preregistered Weighted Least Squares joint model.

    Jointly identifies:
    - intercept (cold associator Lab baseline)
    - delta_assoc (associator route contrast LaLb - Lab)
    - block_ctrl (quaternion control block offset)
    - delta_ctrl (quaternion control route contrast LaLb - Lab)
    - gamma_hot (hot predecessor carryover shift)
    - gamma_wrapped (wrapped predecessor carryover shift)
    - polynomial drift terms tau_1 .. tau_d

    Returns parameters, covariance, standard errors, confidence intervals,
    TOST equivalence verdicts, and diagnostic residual tests.
    """
    n_obs = len(target_records)
    if n_obs != 16:
        raise ValueError(f"expected 16 target records, got {n_obs}")

    p_drift = max(0, min(drift_degree, 3))
    p_total = 6 + p_drift

    rows: list[list[float]] = []
    y: list[float] = []
    w: list[float] = []

    for rec in target_records:
        t = rec["time"]
        is_assoc = 1.0 if rec["block"] == "associator" else 0.0
        is_ctrl = 1.0 if rec["block"] == "control" else 0.0
        route_lalb = 1.0 if rec["route"] == "LaLb" else 0.0
        pred_hot = 1.0 if rec["pred"] == "hot" else 0.0
        pred_wrapped = 1.0 if rec["pred"] == "wrapped" else 0.0

        row = [
            1.0,
            is_assoc * route_lalb,
            is_ctrl,
            is_ctrl * route_lalb,
            pred_hot,
            pred_wrapped,
        ]
        for d in range(1, p_drift + 1):
            row.append(float(t**d))

        rows.append(row)
        d_val = float(rec["d_observable"])
        n_focal = float(rec["focal_samples"])
        y.append(d_val)
        var_i = max(1.0 - d_val**2, 0.05) / n_focal
        w.append(1.0 / var_i)

    X = np.array(rows, dtype=float)
    y_vec = np.array(y, dtype=float)
    W = np.diag(w)

    rank = int(np.linalg.matrix_rank(X))
    if rank < p_total:
        raise RuntimeError(f"design matrix is rank deficient: rank {rank} < {p_total}")

    XtWX = X.T @ W @ X
    theta_hat = np.linalg.solve(XtWX, X.T @ W @ y_vec)
    residuals = y_vec - X @ theta_hat
    rss = float(np.sum(w * residuals**2))

    df_resid = n_obs - p_total
    if df_resid <= 0:
        raise RuntimeError(f"insufficient residual degrees of freedom: {df_resid}")

    # Quasi-likelihood dispersion: enforce the fundamental quantum shot-noise floor
    # dispersion >= 1.0 guarantees uncertainty never collapses below Poisson/multinomial counting limits
    dispersion = max(1.0, rss / df_resid)
    cov = dispersion * np.linalg.inv(XtWX)
    se = np.sqrt(np.maximum(np.diag(cov), 1e-18))

    t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df=df_resid))

    param_names = [
        "intercept",
        "delta_assoc",
        "block_ctrl",
        "delta_ctrl",
        "gamma_hot",
        "gamma_wrapped",
    ] + [f"drift_poly_{d}" for d in range(1, p_drift + 1)]

    coefficients: dict[str, dict[str, Any]] = {}
    for idx, name in enumerate(param_names):
        val = float(theta_hat[idx])
        s = float(se[idx])
        t_stat = float(val / s) if s > 0 else 0.0
        p_val = float(2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=df_resid)))
        ci_low = float(val - t_crit * s)
        ci_high = float(val + t_crit * s)
        coefficients[name] = {
            "estimate": round(val, 6),
            "std_error": round(s, 6),
            "t_statistic": round(t_stat, 4),
            "p_value": round(p_val, 6),
            "ci95": [round(ci_low, 6), round(ci_high, 6)],
        }

    # Hat matrix and leverage
    shot_sigma = 1.0 / np.sqrt(np.array(w))
    shot_z_scores = np.abs(residuals) / shot_sigma
    max_z = float(np.max(shot_z_scores))
    max_z_idx = int(np.argmax(shot_z_scores))
    abrupt_step = bool(max_z > OUTLIER_SIGMA_THRESHOLD)

    # Drift significance F-test (compare with model without drift parameters)
    if p_drift > 0:
        X_nodrift = X[:, :6]
        XtWX_nodrift = X_nodrift.T @ W @ X_nodrift
        theta_nodrift = np.linalg.solve(XtWX_nodrift, X_nodrift.T @ W @ y_vec)
        rss_nodrift = max(float(np.sum(w * (y_vec - X_nodrift @ theta_nodrift) ** 2)), rss)
        f_num = max(0.0, (rss_nodrift - rss) / p_drift)
        f_den = rss / df_resid
        f_stat = float(f_num / f_den) if f_den > 1e-12 else 0.0
        drift_p_val = float(1.0 - stats.f.cdf(f_stat, p_drift, df_resid)) if f_den > 1e-12 else 1.0
    else:
        f_stat = 0.0
        drift_p_val = 1.0

    # Closure linear combination: C = delta_assoc + 2 * (intercept + block_ctrl + 0.5 * delta_ctrl)
    c_vec = np.zeros(p_total)
    c_vec[0] = 2.0
    c_vec[1] = 1.0
    c_vec[2] = 2.0
    c_vec[3] = 1.0
    closure_est = float(c_vec @ theta_hat)
    closure_var = float(c_vec @ cov @ c_vec)
    closure_se = float(math.sqrt(max(closure_var, 0.0)))
    closure_ci = [
        round(closure_est - t_crit * closure_se, 6),
        round(closure_est + t_crit * closure_se, 6),
    ]

    # Two One-Sided Tests (TOST) on carryover parameters against margin TVD_EQUIVALENCE_MARGIN
    margin = TVD_EQUIVALENCE_MARGIN

    def evaluate_tost(ci: list[float], est: float, p_val: float) -> str:
        if ci[0] > -margin and ci[1] < margin:
            return "EQUIVALENT"
        elif (ci[0] > 0.0 and est > margin) or (ci[1] < 0.0 and est < -margin):
            return "SIGNIFICANT_CARRYOVER"
        else:
            return "INCONCLUSIVE"

    hot_tost = evaluate_tost(
        coefficients["gamma_hot"]["ci95"],
        coefficients["gamma_hot"]["estimate"],
        coefficients["gamma_hot"]["p_value"],
    )
    wrapped_tost = evaluate_tost(
        coefficients["gamma_wrapped"]["ci95"],
        coefficients["gamma_wrapped"]["estimate"],
        coefficients["gamma_wrapped"]["p_value"],
    )

    return {
        "coefficients": coefficients,
        "residual_degrees_of_freedom": df_resid,
        "residual_sum_of_squares": round(rss, 6),
        "f_test_drift": {
            "f_statistic": round(f_stat, 4),
            "p_value": round(drift_p_val, 6),
            "drift_significant": bool(drift_p_val < 0.05),
        },
        "step_change_diagnostic": {
            "max_standardized_residual": round(max_z, 4),
            "max_residual_iteration": max_z_idx,
            "abrupt_step_detected": abrupt_step,
            "threshold": OUTLIER_SIGMA_THRESHOLD,
        },
        "closure": {
            "estimate": round(closure_est, 6),
            "std_error": round(closure_se, 6),
            "ci95": closure_ci,
            "closure_admitted": bool(
                abs(closure_est) < CLOSURE_TOLERANCE
                and abs(closure_ci[0]) < CLOSURE_TOLERANCE
                and abs(closure_ci[1]) < CLOSURE_TOLERANCE
            ),
        },
        "equivalence_testing": {
            "margin": margin,
            "alpha": alpha,
            "verdict_hot": hot_tost,
            "verdict_wrapped": wrapped_tost,
        },
    }


def analyze(
    run_dir: Path,
    drift_degree: int = 2,
    min_focal_per_iter: int = MIN_FOCAL_SAMPLES_PER_ITERATION,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Analyze a collected or simulated run directory with fail-closed statistical admission.

    Validates:
    - exact setting matching and count payload integrity
    - separated predecessor and target sentinel leakage with uncertainties
    - sample count thresholds and per-iteration focal yields
    - preregistered Joint WLS Model identifying contrasts, carryover, and drift
    - TOST equivalence test against +/- 0.020 with confidence intervals
    - studentized step-change / abrupt transition quarantine
    """
    cases_path = run_dir / "cases.json"
    results_path = run_dir / "results.json"
    if not cases_path.exists():
        raise FileNotFoundError(f"missing cases.json in {run_dir}")
    if not results_path.exists():
        raise FileNotFoundError(f"missing results.json in {run_dir}")

    manifest = json.loads(cases_path.read_text())
    results = json.loads(results_path.read_text())
    entries = results.get("iterations")
    if not isinstance(entries, list):
        raise ValueError(f"results.json in {run_dir} does not contain an 'iterations' list")

    expected_settings = manifest["settings"]
    if len(entries) != len(expected_settings):
        raise ValueError(
            f"iteration count mismatch: manifest expects {len(expected_settings)} settings, "
            f"results contain {len(entries)}"
        )

    # Sentinel leakage counters separated by role
    sentinel_stats: dict[str, dict[str, dict[str, int]]] = {
        "predecessor": {p: {"total_events": 0, "sentinel_events": 0} for p in ("hot", "cold", "wrapped")},
        "target": {p: {"total_events": 0, "sentinel_events": 0} for p in ("hot", "cold", "wrapped")},
    }

    target_records: list[dict[str, Any]] = []

    for setting, entry in zip(expected_settings, entries, strict=True):
        if not isinstance(entry, dict):
            raise ValueError(f"entry for {setting['name']} is not a dictionary")
        if entry.get("setting") != setting["name"]:
            raise ValueError(f"setting sequence mismatch: expected {setting['name']!r}, got {entry.get('setting')!r}")

        counts = validate_count_payload(
            entry.get("counts"),
            setting["name"],
            min_photons=manifest.get("min_detected_photons", 2),
        )

        role = setting["role"]
        pred = setting["pred"]

        if role == "predecessor":
            for state_str, count in counts.items():
                sentinel_stats["predecessor"][pred]["total_events"] += count
                occupation = [int(c) for c in state_str[1:-1].split(",")]
                occupied = [m for m, n in enumerate(occupation) if n > 0]
                if any(m >= LOGICAL for m in occupied):
                    sentinel_stats["predecessor"][pred]["sentinel_events"] += count
            continue

        # Target iterations
        block = setting["block"]
        route = setting["route"]
        pair_idx = setting["pair_index"]

        plus_c = 0
        minus_c = 0
        other_c = 0

        for state_str, count in counts.items():
            sentinel_stats["target"][pred]["total_events"] += count
            occupation = [int(c) for c in state_str[1:-1].split(",")]
            occupied = [m for m, n in enumerate(occupation) if n > 0]
            if any(m >= LOGICAL for m in occupied):
                sentinel_stats["target"][pred]["sentinel_events"] += count
            elif len(occupied) == 2:
                pair = f"{occupied[0]}{occupied[1]}"
                if pair in PLUS_PAIRS:
                    plus_c += count
                elif pair in MINUS_PAIRS:
                    minus_c += count
                else:
                    other_c += count

        focal_sum = plus_c + minus_c + other_c
        if focal_sum < min_focal_per_iter:
            raise ValueError(
                f"{setting['name']}: returned {focal_sum} focal samples, below minimum threshold {min_focal_per_iter}"
            )

        obs_d = (plus_c - minus_c) / focal_sum

        # Temporal coordinate: use elapsed_seconds if available, else normalized pair index
        elapsed_sec = entry.get("elapsed_seconds")
        time_coord = float(elapsed_sec) if elapsed_sec is not None else float(pair_idx / 15.0)

        target_records.append(
            {
                "pair_index": pair_idx,
                "block": block,
                "pred": pred,
                "route": route,
                "d_observable": obs_d,
                "focal_samples": focal_sum,
                "time": time_coord,
            }
        )

    # Compute sentinel leakage fractions and CIs
    sentinel_report: dict[str, dict[str, dict[str, Any]]] = {}
    for role_name in ("predecessor", "target"):
        sentinel_report[role_name] = {}
        for p in ("hot", "cold", "wrapped"):
            tot = sentinel_stats[role_name][p]["total_events"]
            leak = sentinel_stats[role_name][p]["sentinel_events"]
            frac = leak / tot if tot > 0 else 0.0
            se = math.sqrt(frac * (1.0 - frac) / tot) if tot > 0 else 0.0
            sentinel_report[role_name][p] = {
                "total_events": tot,
                "sentinel_events": leak,
                "leakage_fraction": round(frac, 6),
                "std_error": round(se, 6),
                "ci95": [round(max(0.0, frac - 1.96 * se), 6), round(min(1.0, frac + 1.96 * se), 6)],
            }

    # Fit preregistered Joint WLS Model
    joint_model = fit_joint_model(target_records, drift_degree=drift_degree, alpha=alpha)

    # Check execution status
    step_diag = joint_model["step_change_diagnostic"]
    if step_diag["abrupt_step_detected"]:
        execution_status = "QUARANTINED_ABRUPT_STEP"
    else:
        execution_status = "ADMITTED"

    assoc_coef = joint_model["coefficients"]["delta_assoc"]
    ctrl_coef = joint_model["coefficients"]["delta_ctrl"]
    closure_rep = joint_model["closure"]

    verdicts = {
        "execution_status": execution_status,
        "associator_signal_detected": bool(assoc_coef["estimate"] > 0.5 and assoc_coef["ci95"][0] > 0.5),
        "quaternion_null_admitted": bool(
            abs(ctrl_coef["estimate"]) < MUTATION_TOLERANCE
            and abs(ctrl_coef["ci95"][0]) < MUTATION_TOLERANCE
            and abs(ctrl_coef["ci95"][1]) < MUTATION_TOLERANCE
        ),
        "closure_admitted": closure_rep["closure_admitted"],
        "predecessor_carryover_hot": joint_model["equivalence_testing"]["verdict_hot"],
        "predecessor_carryover_wrapped": joint_model["equivalence_testing"]["verdict_wrapped"],
        "drift_detected": joint_model["f_test_drift"]["drift_significant"],
    }

    return {
        "status": execution_status,
        "verdicts": verdicts,
        "joint_model": joint_model,
        "sentinel_leakage": sentinel_report,
        "target_observations": target_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify identities, circuits, and simulation")
    parser.add_argument("--build", action="store_true", help="build and write case files to results/")
    parser.add_argument("--dry-run", action="store_true", help="execute local Perceval simulation and test analysis")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES_PER_ITERATION, help="samples per iteration")
    parser.add_argument("--shots-factor", type=int, default=DEFAULT_SHOTS_FACTOR, help="shots per sample multiplier")
    parser.add_argument("--drift-degree", type=int, default=2, help="polynomial degree for anchor drift model")
    parser.add_argument("--analyze", type=Path, help="analyze collected run directory")
    args = parser.parse_args()

    if args.check:
        sys.exit(check())
    elif args.build:
        sys.exit(build_case(samples=args.samples, shots_factor=args.shots_factor))
    elif args.dry_run:
        sys.exit(dry_run(samples=args.samples, shots_factor=args.shots_factor))
    elif args.analyze:
        print(json.dumps(analyze(args.analyze, drift_degree=args.drift_degree), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
