"""Ascella two-photon 8-mode octonion associator-character campaign.

This module implements the two-photon 8-mode associator-character interferometer on
Quandela Ascella (qpu:ascella / sim:ascella). It tests the non-associativity of the
octonions through quantum optical two-photon interference across the Fano plane PG(2, 2).

First-principles mathematics:
1. For any pair of distinct imaginary octonions e_a, e_b (1 <= a < b <= 7):
   The column signs s(x) defined by (e_a e_b) e_x = s(x) e_a (e_b e_x) for x in {0..7}
   form a nontrivial character of F_2^3:
     s(x) = (-1)^{omega(a,b) . x}
   whose kernel is exactly the quaternion subalgebra {0, a, b, a ^ b} (for all 21 pairs).
2. The frequency vector omega(a, b) in {1..7} identifies the non-zero target mode where the
   character causes constructive interference.
3. The interferometer is formed by sandwiching the diagonal phase matrix D = diag(s(0)..s(7))
   between two 8-mode Walsh-Hadamard transform layers W_8 = H_2^{ox 3}:
     U(a, b) = W_8 D(a, b) W_8
   By Pontryagin duality / Fourier inversion on F_2^3, U(a, b) is an exact group translation
   matrix tau_omega: tau_omega |x> = |x ^ omega>.
4. When two indistinguishable photons enter connected source modes (0, 2):
   - Under tau_omega, photon 1 (mode 0) maps to 0 ^ omega = omega.
   - Photon 2 (mode 2) maps to 2 ^ omega.
   - The two photons exit deterministically on the pair P_focal = {min(omega, 2 ^ omega), max(omega, 2 ^ omega)}.
5. Quotient coset partitioning of F_2^3 / {0, 2}:
   The subgroup K_0 = {0, 2} partitions the 8 modes into 4 cosets of size 2:
   - K_0 = {0, 2}: Stabilizer line (omega = 2, Line 2 of Fano plane, 3 pairs).
     tau_2 stabilizes K_0: {0, 2} ^ 2 = {2, 0} = K_0. Photons remain in (0, 2).
   - K_1 = {1, 3}: Displacing lines 1 & 3 (omega in {1, 3}, 6 pairs). Photons exit in (1, 3).
   - K_2 = {4, 6}: Displacing lines 4 & 6 (omega in {4, 6}, 6 pairs). Photons exit in (4, 6).
   - K_3 = {5, 7}: Displacing lines 5 & 7 (omega in {5, 7}, 6 pairs). Photons exit in (5, 7).
6. Non-bunching theorem:
   Because 0 != 2, omega != 2 ^ omega for all omega in F_2^3. The two output modes are strictly
   distinct across all 21 pairs! Ideal bunching probability is strictly zero, completely
   bypassing threshold-detector saturation defects.
7. Contrasts:
   - For displacing pairs (omega != 2): D = (N(P_focal) - N(P_control)) / (N(P_focal) + N(P_control))
     gives D_oct = +1.0 and D_ctrl = -1.0, yielding differential character contrast
     Delta_char = D_oct - D_ctrl = +2.000000.
   - For stabilizer pairs (omega == 2): P(0, 2) = 1.0 under both arms, certifying K_0 as the
     invariant stabilizer subspace.

Usage:
  "$PYTHON" scripts/ascella_two_photon_character.py --check
  "$PYTHON" scripts/ascella_two_photon_character.py --build [--job job-00] [--all-pairs]
  "$PYTHON" scripts/ascella_two_photon_character.py --dry-run [--job job-00] [--all-pairs]
  "$PYTHON" scripts/ascella_two_photon_character.py --analyze RUN_DIR
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

from cd_core import cd_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

MODES = 12
LOGICAL = 8
SENTINELS = list(range(LOGICAL, MODES))
CASE_DIR = ROOT / "results/quandela/cases/ascella_two_photon_character/job-00"

INPUT_STATE = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
MIN_DETECTED_PHOTONS = 2
CONTROL_PAIR = (0, 2)

DEFAULT_SAMPLES_PER_ITERATION = 4096
DEFAULT_SHOTS_FACTOR = 64
MIN_FOCAL_SAMPLES_PER_SETTING = 50
# The preregistered ceiling on the fraction of two-click events in the sentinel modes.
SENTINEL_LEAKAGE_MAX = 0.05
MAX_DURATION = 300
TOLERANCE = 1e-12
BODY_TOLERANCE = 1e-9

PRIMARY_PAIRS = ((1, 2), (1, 4), (2, 4), (3, 5))
ALL_PAIRS: tuple[tuple[int, int], ...] = tuple((a, b) for a in range(1, 8) for b in range(a + 1, 8))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def hadamard_8() -> np.ndarray:
    """8-mode normalized Walsh-Hadamard transform W_8 = H_2^{ox 3}."""
    h2 = np.array([[1.0, 1.0], [1.0, -1.0]]) / math.sqrt(2.0)
    return np.kron(h2, np.kron(h2, h2))


def associator_sign(a: int, b: int, x: int) -> int:
    """The sign s(x) such that (e_a e_b) e_x = s(x) e_a (e_b e_x)."""
    lhs = cd_sign(8, a, b) * cd_sign(8, a ^ b, x)
    rhs = cd_sign(8, b, x) * cd_sign(8, a, b ^ x)
    sign = lhs * rhs
    require(sign in (+1, -1), f"invalid sign {sign} for ({a}, {b}, {x})")
    return int(sign)


def character_frequency(a: int, b: int) -> int:
    """The unique non-zero frequency omega in {1..7} such that s(x) = (-1)^{omega . x}."""
    w8 = hadamard_8()
    s = np.array([associator_sign(a, b, x) for x in range(8)], dtype=float)
    u = w8 @ np.diag(s) @ w8
    out_mode = int(np.argmax(np.abs(u[:, 0])))
    require(out_mode != 0, f"pair ({a}, {b}) has trivial frequency omega=0")
    require(abs(abs(u[out_mode, 0]) - 1.0) < TOLERANCE, f"pair ({a}, {b}) transfer is not 1.0")
    return out_mode


def coset_focal_pair(omega: int) -> tuple[int, int]:
    """The two-photon exit pair {omega, 2 ^ omega} for input photons entering (0, 2)."""
    m1 = omega
    m2 = 2 ^ omega
    return (min(m1, m2), max(m1, m2))


def build_character_unitary(a: int, b: int, arm: str) -> np.ndarray:
    """Build the 8x8 orthogonal unitary for the specified arm."""
    w8 = hadamard_8()
    if arm == "octonion":
        s = np.array([associator_sign(a, b, x) for x in range(8)], dtype=float)
        return w8 @ np.diag(s) @ w8
    elif arm == "clifford_control":
        return w8 @ np.eye(8) @ w8
    elif arm == "diagonal_null":
        return np.eye(8)
    elif arm == "reversed":
        s = np.array([associator_sign(b, a, x) for x in range(8)], dtype=float)
        return w8 @ np.diag(s) @ w8
    else:
        raise ValueError(f"unknown arm {arm!r}")


def embed_12(matrix_8x8: np.ndarray) -> np.ndarray:
    u12 = np.eye(MODES, dtype=complex)
    u12[:LOGICAL, :LOGICAL] = matrix_8x8
    return u12


def build_setting_item(item: tuple[int, dict[str, Any]]) -> dict[str, Any]:
    idx, spec = item
    a, b = spec["pair"]
    arm = spec["arm"]
    omega = character_frequency(a, b)
    focal_pair = coset_focal_pair(omega)

    u8 = build_character_unitary(a, b, arm)
    u12 = embed_12(u8)

    _, params = photonic_template(u8.astype(complex))
    col = [[float(v.real), float(v.imag)] for v in u12[:, 0]]

    # Compute ideal 2-photon permanent probabilities for input on (0, 2)
    # Since u8 is a permutation matrix tau_omega:
    # Under octonion/reversed: photon 0 -> omega, photon 2 -> 2 ^ omega
    # Under clifford/null: photon 0 -> 0, photon 2 -> 2
    if arm in ("octonion", "reversed"):
        ideal_target_pair = focal_pair
        ideal_probs = {f"{focal_pair[0]}_{focal_pair[1]}": 1.0}
    else:
        ideal_target_pair = CONTROL_PAIR
        ideal_probs = {f"{CONTROL_PAIR[0]}_{CONTROL_PAIR[1]}": 1.0}

    is_stabilizer = bool(omega == 2)
    if is_stabilizer:
        ideal_d = 0.0
    else:
        ideal_d = 1.0 if ideal_target_pair == focal_pair else -1.0

    return {
        "name": f"iter{idx:02d}-{spec['name']}",
        "observation_index": idx,
        "pair": [a, b],
        "arm": arm,
        "omega_target": omega,
        "focal_pair": list(focal_pair),
        "control_pair": list(CONTROL_PAIR),
        "is_stabilizer": is_stabilizer,
        "circuit_params": params,
        "column": col,
        "operator": encoded(u12),
        "ideal": {
            "probabilities": ideal_probs,
            "d_observable": round(ideal_d, 6),
            "target_pair": list(ideal_target_pair),
        },
    }


def build_schedule_spec(all_pairs: bool = False) -> list[dict[str, Any]]:
    pairs = ALL_PAIRS if all_pairs else PRIMARY_PAIRS
    spec = []
    for a, b in pairs:
        spec.append({"pair": (a, b), "arm": "octonion", "name": f"pair_{a}_{b}-octonion"})
        spec.append({"pair": (a, b), "arm": "clifford_control", "name": f"pair_{a}_{b}-clifford_control"})
        spec.append({"pair": (a, b), "arm": "diagonal_null", "name": f"pair_{a}_{b}-diagonal_null"})
        spec.append({"pair": (a, b), "arm": "reversed", "name": f"pair_{a}_{b}-reversed"})
    return spec


def build_template_circuit() -> dict[str, Any]:
    canonical_8 = build_character_unitary(1, 2, "octonion").astype(complex)
    mesh, _ = photonic_template(canonical_8)
    return {**mesh, "modes": MODES, "input_state": INPUT_STATE}


def build_documents(
    samples_per_iteration: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
    job_name: str = "job-00",
    all_pairs: bool = False,
) -> dict[str, bytes]:
    if samples_per_iteration <= 0:
        raise ValueError(f"samples_per_iteration must be positive integer, got {samples_per_iteration}")
    if shots_factor <= 0:
        raise ValueError(f"shots_factor must be positive integer, got {shots_factor}")

    circuit = build_template_circuit()
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()

    is_all_pairs = all_pairs or (job_name in ("job-01", "atlas"))
    schedule = build_schedule_spec(all_pairs=is_all_pairs)
    settings = ordered_map(build_setting_item, list(enumerate(schedule)), min_items=1)

    shots_per_iteration = samples_per_iteration * shots_factor
    credit_ceiling = 1.0 + 1e-6 * shots_per_iteration

    sample_scale = samples_per_iteration / float(DEFAULT_SAMPLES_PER_ITERATION)
    sec_per_iter = round(2.5 * sample_scale, 2)
    est_seconds = round(30.0 + len(settings) * sec_per_iter, 1)
    duration_bounds = [
        round(est_seconds * 0.8, 1),
        round(min(float(MAX_DURATION), est_seconds * 1.3), 1),
    ]

    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": "ascella_two_photon_character",
        "job": job_name,
        "platforms": ["qpu:ascella", "sim:ascella"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": MIN_DETECTED_PHOTONS,
        "input_state": INPUT_STATE,
        "samples_per_iteration": samples_per_iteration,
        "shots_per_iteration": shots_per_iteration,
        "max_samples": samples_per_iteration * len(settings),
        "max_shots": shots_per_iteration * len(settings),
        "max_duration": MAX_DURATION,
        "credit_ceiling": round(credit_ceiling, 6),
        "timing_model": {
            "overhead_seconds": 30.0,
            "seconds_per_iteration": sec_per_iter,
            "estimated_duration_seconds": est_seconds,
            "duration_bounds_seconds": duration_bounds,
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
        "sentinel_modes": SENTINELS,
        "connected_input_modes": [0, 2],
        "eligibility": "exactly two detected clicks across modes 0..7; sentinel events click in modes 8..11",
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "two_photon_character_contrast": "Delta_char = D_oct - D_ctrl for displacing pairs (omega != 2)",
            "stabilizer_coset_invariance": "P(0, 2) = 1.0 for Line 2 pairs (omega == 2)",
            "ideal_contrast": 2.0,
            "non_bunching_theorem": "P(2_m) = 0 for all modes m (bunching identically zero)",
            "sentinel_leakage_endpoint": (
                f"fraction of two-click counts in sentinel modes 8..11 < {SENTINEL_LEAKAGE_MAX}"
            ),
        },
    }

    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def _verify_two_photon_flint(pair: tuple[int, int]) -> bool:
    """Exact rational two-photon transfer for one octonion basis pair."""
    import flint

    a, b = pair
    w8 = flint.fmpz_mat(8, 8, [(-1) ** (bin(i & j).count("1")) for i in range(8) for j in range(8)])
    om = character_frequency(a, b)
    d_mat = flint.fmpz_mat(8, 8, [associator_sign(a, b, i) if i == j else 0 for i in range(8) for j in range(8)])
    prod = w8 * d_mat * w8
    if int(prod[om, 0]) != 8 or int(prod[2 ^ om, 2]) != 8:
        raise ValueError(f"Flint two-photon transfer failed for ({a},{b})")
    return True


def check() -> int:
    """Verify two-photon coset theorem, non-bunching theorem, template binding, and SLOS."""
    from itertools import combinations

    # 1. Mathematical theorem verification across all 21 pairs
    for a, b in combinations(range(1, 8), 2):
        s = [associator_sign(a, b, x) for x in range(8)]
        kernel = set(x for x in range(8) if s[x] == 1)
        expected_kernel = {0, a, b, a ^ b}
        require(kernel == expected_kernel, f"pair ({a}, {b}) kernel {kernel} != {expected_kernel}")
        omega = character_frequency(a, b)
        require(omega != 0, f"pair ({a}, {b}) omega is zero")
        focal = coset_focal_pair(omega)
        require(focal[0] != focal[1], f"pair ({a}, {b}) would bunch into mode {focal[0]}")

    # 2. Template experiment binding for job-00 (16 settings) and job-01 (84 settings)
    docs_16 = build_documents(job_name="job-00", all_pairs=False)
    manifest_16 = json.loads(docs_16["cases.json"].decode())
    circuit_16 = json.loads(docs_16["circuit.json"].decode())
    exp_16, settings_16 = template_experiment(manifest_16, circuit_16)
    require(
        exp_16 is not None and len(settings_16) == 16,
        f"template experiment bound {len(settings_16)} settings, expected 16",
    )

    docs_84 = build_documents(job_name="job-01", all_pairs=True)
    manifest_84 = json.loads(docs_84["cases.json"].decode())
    circuit_84 = json.loads(docs_84["circuit.json"].decode())
    exp_84, settings_84 = template_experiment(manifest_84, circuit_84)
    require(
        exp_84 is not None and len(settings_84) == 84,
        f"atlas template experiment bound {len(settings_84)} settings, expected 84",
    )

    # 3. SLOS verification on two-photon propagation
    import perceval as pcvl

    u8 = build_character_unitary(1, 2, "octonion")
    u12 = embed_12(u8)
    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(u12)))
    backend.set_input_state(pcvl.BasicState(INPUT_STATE))
    dist = backend.prob_distribution()

    # Pair (1, 2) has omega = 4. 4 ^ 2 = 6. Focal pair is (4, 6).
    focal_state = [0] * MODES
    focal_state[4] = 1
    focal_state[6] = 1
    control_state = [0] * MODES
    control_state[0] = 1
    control_state[2] = 1

    p_focal = dist.get(pcvl.BasicState(focal_state), 0.0)
    p_ctrl = dist.get(pcvl.BasicState(control_state), 0.0)
    require(abs(p_focal - 1.0) < BODY_TOLERANCE, f"SLOS P(4, 6) {p_focal} != 1.0")
    require(abs(p_ctrl) < BODY_TOLERANCE, f"SLOS P(0, 2) {p_ctrl} != 0.0")

    # 4. Exact rational arithmetic verification via python-flint pooled through parallel.py
    try:
        import flint  # noqa: F401

        pairs = list(combinations(range(1, 8), 2))
        list(ordered_map(_verify_two_photon_flint, pairs))
        flint_verified = True
    except ImportError:
        flint_verified = False

    print("ascella_two_photon_character: check passed!")
    print("21-pair octonion two-photon coset theorem verified across F_2^3 / {0, 2}")
    print("Non-bunching theorem verified: P(2_m) = 0 for all modes (zero threshold-detector blindness)")
    if flint_verified:
        print("Flint exact rational arithmetic verified: W_8 D(a,b) W_8 = 8 tau_omega (0 drift)")
    print("16 settings (job-00) and 84 settings (job-01 atlas) bound to 8-mode Clements mesh")
    print(f"SLOS two-photon transfer confirmed: P(4, 6) = {p_focal:.6f}, P(0, 2) = {p_ctrl:.6f}")
    print(f"credit ceiling confirmed at {manifest_84['credit_ceiling']:.6f} credits (job-01)")
    return 0


def build_case(
    samples: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
    job_name: str = "job-00",
    case_dir: Path | None = None,
    all_pairs: bool = False,
) -> int:
    is_all_pairs = all_pairs or (job_name in ("job-01", "atlas"))
    target_dir = case_dir or (ROOT / f"results/quandela/cases/ascella_two_photon_character/{job_name}")
    target_dir.mkdir(parents=True, exist_ok=True)
    docs = build_documents(
        samples_per_iteration=samples,
        shots_factor=shots_factor,
        job_name=job_name,
        all_pairs=is_all_pairs,
    )
    for name, data in docs.items():
        (target_dir / name).write_bytes(data)
    manifest = json.loads(docs["cases.json"].decode())
    print(
        f"Wrote {len(docs)} files to {target_dir} (job={job_name}, settings={len(manifest['settings'])}, "
        f"samples={manifest['samples_per_iteration']}, shots={manifest['shots_per_iteration']}, "
        f"credits={manifest['credit_ceiling']})"
    )
    return 0


def dry_run(
    samples: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
    job_name: str = "job-00",
    case_dir: Path | None = None,
    all_pairs: bool = False,
) -> int:
    """Execute local simulation across all iterations to verify end-to-end pipeline and contrast."""
    is_all_pairs = all_pairs or (job_name in ("job-01", "atlas"))
    target_dir = case_dir or (ROOT / f"results/quandela/cases/ascella_two_photon_character/{job_name}")
    docs = build_documents(
        samples_per_iteration=samples,
        shots_factor=shots_factor,
        job_name=job_name,
        all_pairs=is_all_pairs,
    )
    manifest = json.loads(docs["cases.json"].decode())
    settings = manifest["settings"]

    simulated_iterations = []
    print(f"Running local simulation of {len(settings)} two-photon settings at {samples} samples/iteration...")
    for idx, s in enumerate(settings):
        target_pair = tuple(s["ideal"]["target_pair"])

        # Optical visibility on two photons on Ascella (~96%)
        vis = 0.96
        counts: dict[str, int] = {}
        n_target = int(round(samples * vis))
        n_leak = samples - n_target

        state_target = [0] * MODES
        state_target[target_pair[0]] += 1
        state_target[target_pair[1]] += 1

        # Small leakage into orthogonal pair
        if target_pair == CONTROL_PAIR:
            alt_pair = (1, 3)
        else:
            alt_pair = CONTROL_PAIR
        state_leak = [0] * MODES
        state_leak[alt_pair[0]] += 1
        state_leak[alt_pair[1]] += 1

        counts[f"|{','.join(str(v) for v in state_target)}>"] = n_target
        counts[f"|{','.join(str(v) for v in state_leak)}>"] = n_leak

        simulated_iterations.append(
            {
                "setting": s["name"],
                "counts": counts,
                "elapsed_seconds": round(idx * 2.5, 2),
                "duration": 2.5,
            }
        )

    mock_run_dir = target_dir / "dry_run_simulation"
    mock_run_dir.mkdir(parents=True, exist_ok=True)
    (mock_run_dir / "cases.json").write_bytes(docs["cases.json"])
    (mock_run_dir / "results.json").write_text(json.dumps({"iterations": simulated_iterations}, indent=2))
    print(f"Local dry run complete. Output saved to {mock_run_dir}")
    print("Running analysis on simulated two-photon dry-run data...")
    report = analyze(mock_run_dir)
    print(json.dumps(report, indent=2))
    return 0


def analyze(run_dir: Path) -> dict[str, Any]:
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
        raise ValueError("missing iterations list in results.json")

    settings = manifest["settings"]
    require(len(entries) == len(settings), f"mismatch: {len(entries)} != {len(settings)}")

    samples_per_iter = int(manifest.get("samples_per_iteration", DEFAULT_SAMPLES_PER_ITERATION))
    min_focal = max(MIN_FOCAL_SAMPLES_PER_SETTING, int(0.01 * samples_per_iter))
    admission_errors: list[str] = []

    per_setting_reports = []
    pair_contrasts: dict[str, dict[str, float]] = {}

    total_focal = 0
    total_sentinel = 0

    for s, entry in zip(settings, entries, strict=True):
        name = s["name"]
        a, b = s["pair"]
        pair_key = f"pair_{a}_{b}"
        arm = s["arm"]
        omega = s["omega_target"]
        focal_pair = tuple(s["focal_pair"])
        is_stabilizer = s["is_stabilizer"]

        counts = entry.get("counts")
        if not isinstance(counts, dict) or not counts:
            admission_errors.append(f"{name}: empty or missing counts payload")
            counts = {}

        c_focal = 0
        c_control = 0
        c_sentinel = 0
        c_other = 0

        for state_str, cnt in counts.items():
            occupation = [int(v) for v in state_str.strip("|>").split(",")]
            occupied = [m for m, n in enumerate(occupation) if n > 0]
            total_photons = sum(occupation)

            if total_photons != 2:
                # Excluded by two-click post-selection
                continue

            if any(m >= LOGICAL for m in occupied):
                c_sentinel += cnt
            elif len(occupied) == 2:
                pair = (min(occupied), max(occupied))
                if pair == CONTROL_PAIR:
                    c_control += cnt
                elif pair == focal_pair:
                    c_focal += cnt
                else:
                    c_other += cnt
            elif len(occupied) == 1 and occupation[occupied[0]] == 2:
                # Mode bunching (both photons in one logical mode)
                c_other += cnt

        focal_events = c_focal + c_control + c_other
        total_focal += focal_events
        total_sentinel += c_sentinel

        if is_stabilizer:
            # Stabilizer line: focal == control == (0, 2)
            c_focal_eff = c_control
            denom = max(1, c_focal_eff + c_other)
            d_obs = c_focal_eff / denom  # persistence in (0, 2)
        else:
            denom = max(1, c_focal + c_control)
            d_obs = (c_focal - c_control) / denom

        if denom < min_focal:
            admission_errors.append(
                f"{name}: two-click counts (denom = {denom}) below statistical threshold ({min_focal})"
            )

        # 95% Wilson score interval for binomial proportion p = c_focal / denom transformed to D = 2p - 1
        z = 1.96
        p_hat = c_focal / denom if not is_stabilizer else c_focal_eff / denom
        denom_wilson = 1.0 + (z**2) / denom
        center = (p_hat + (z**2) / (2.0 * denom)) / denom_wilson
        half_width = (z / denom_wilson) * math.sqrt((p_hat * (1.0 - p_hat) / denom) + ((z**2) / (4.0 * (denom**2))))
        p_lower = max(0.0, center - half_width)
        p_upper = min(1.0, center + half_width)

        if not is_stabilizer:
            d_lower = max(-1.0, 2.0 * p_lower - 1.0)
            d_upper = min(1.0, 2.0 * p_upper - 1.0)
            se_plugin = 2.0 * math.sqrt(max(0.0, p_hat * (1.0 - p_hat)) / denom)
        else:
            d_lower = p_lower
            d_upper = p_upper
            se_plugin = math.sqrt(max(0.0, p_hat * (1.0 - p_hat)) / denom)

        record = {
            "name": name,
            "pair": [a, b],
            "arm": arm,
            "omega": omega,
            "focal_pair": list(focal_pair),
            "is_stabilizer": is_stabilizer,
            "c_focal": c_focal,
            "c_control": c_control,
            "c_other": c_other,
            "d_observable": round(d_obs, 6),
            "std_error": round(se_plugin, 6),
            "ci95": [round(d_lower, 6), round(d_upper, 6)],
        }

        try:
            import scipy.stats as stats

            successes = c_focal if not is_stabilizer else c_focal_eff
            cp_low = stats.beta.ppf(0.025, successes, denom - successes + 1) if successes > 0 else 0.0
            cp_high = stats.beta.ppf(0.975, successes + 1, denom - successes) if successes < denom else 1.0
            if not is_stabilizer:
                d_cp_low = max(-1.0, 2.0 * cp_low - 1.0)
                d_cp_high = min(1.0, 2.0 * cp_high - 1.0)
            else:
                d_cp_low = cp_low
                d_cp_high = cp_high
            record["clopper_pearson_ci95"] = [round(float(d_cp_low), 6), round(float(d_cp_high), 6)]
        except ImportError:
            pass

        per_setting_reports.append(record)

        if pair_key not in pair_contrasts:
            pair_contrasts[pair_key] = {}
        pair_contrasts[pair_key][arm] = d_obs

    total_events = total_focal + total_sentinel
    observed_sentinel_rate = total_sentinel / total_events if total_events > 0 else 0.0
    if total_events > 0 and observed_sentinel_rate >= SENTINEL_LEAKAGE_MAX:
        admission_errors.append(
            f"sentinel leakage {observed_sentinel_rate:.6f} reaches the preregistered limit {SENTINEL_LEAKAGE_MAX}"
        )

    if admission_errors:
        return {
            "status": "REFUSED",
            "verdicts": {
                "execution_status": "REFUSED",
                "admission_errors": admission_errors,
                "character_signal_detected": False,
                "mean_displacing_contrast": None,
                "mean_stabilizer_persistence": None,
                "sentinel_leakage_rate": round(observed_sentinel_rate, 6) if total_events > 0 else None,
            },
            "contrasts_by_pair": {},
            "iterations": per_setting_reports,
        }

    contrasts_summary = {}
    displacing_contrasts = []
    stabilizer_persistences = []

    for pair_key, arm_map in pair_contrasts.items():
        parts = pair_key.split("_")
        pa, pb = int(parts[1]), int(parts[2])
        om = character_frequency(pa, pb)
        d_oct = arm_map.get("octonion", 0.0)
        d_ctrl = arm_map.get("clifford_control", 0.0)

        if om == 2:
            # Stabilizer line
            stabilizer_persistences.append(d_oct)
            contrasts_summary[pair_key] = {
                "type": "stabilizer",
                "omega": om,
                "p_control_octonion": round(d_oct, 6),
                "p_control_clifford": round(d_ctrl, 6),
                "stabilizer_admitted": bool(d_oct > 0.80),
            }
        else:
            delta = d_oct - d_ctrl
            displacing_contrasts.append(delta)
            contrasts_summary[pair_key] = {
                "type": "displacing",
                "omega": om,
                "d_octonion": round(d_oct, 6),
                "d_clifford_control": round(d_ctrl, 6),
                "delta_character": round(delta, 6),
            }

    mean_delta = float(np.mean(displacing_contrasts)) if displacing_contrasts else 0.0
    mean_stabilizer = float(np.mean(stabilizer_persistences)) if stabilizer_persistences else 0.0

    return {
        "status": "ADMITTED",
        "verdicts": {
            "execution_status": "ADMITTED",
            "character_signal_detected": bool(mean_delta > 1.5),
            "mean_displacing_contrast": round(mean_delta, 6),
            "mean_stabilizer_persistence": round(mean_stabilizer, 6),
            "sentinel_leakage_rate": round(observed_sentinel_rate, 6),
        },
        "contrasts_by_pair": contrasts_summary,
        "iterations": per_setting_reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify identities, circuits, and simulation")
    parser.add_argument("--build", action="store_true", help="build and write case files to results/")
    parser.add_argument("--dry-run", action="store_true", help="execute local simulation and test analysis")
    parser.add_argument("--job", default="job-00", help="job identifier (e.g. job-00)")
    parser.add_argument("--all-pairs", action="store_true", help="build or run all 21 octonion pairs (84 iterations)")
    parser.add_argument("--case-dir", type=Path, default=None, help="case directory override")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES_PER_ITERATION, help="samples per iteration")
    parser.add_argument("--shots-factor", type=int, default=DEFAULT_SHOTS_FACTOR, help="shots multiplier")
    parser.add_argument("--analyze", type=Path, help="analyze collected run directory")
    args = parser.parse_args()

    job_name = args.job
    if args.all_pairs and job_name == "job-00":
        job_name = "job-01"

    if args.check:
        sys.exit(check())
    elif args.build:
        sys.exit(
            build_case(
                samples=args.samples,
                shots_factor=args.shots_factor,
                job_name=job_name,
                case_dir=args.case_dir,
                all_pairs=args.all_pairs,
            )
        )
    elif args.dry_run:
        sys.exit(
            dry_run(
                samples=args.samples,
                shots_factor=args.shots_factor,
                job_name=job_name,
                case_dir=args.case_dir,
                all_pairs=args.all_pairs,
            )
        )
    elif args.analyze:
        print(json.dumps(analyze(args.analyze), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
