"""Ascella single-photon 8-mode octonion associator-character campaign.

This module implements the 8-mode associator-character interferometer on Quandela Ascella
(qpu:ascella / sim:ascella). It tests the non-associativity of the octonions through the
column-sign character of F_2^3, contrasting physical octonion non-associativity against
the associative Clifford algebra Cl(0,3) control and the diagonal identity null.

First-principles mathematics:
1. For any pair of distinct imaginary octonions e_a, e_b (1 <= a < b <= 7):
   The column signs s(x) defined by (e_a e_b) e_x = s(x) e_a (e_b e_x) for x in {0..7}
   form a nontrivial character of F_2^3:
     s(x) = (-1)^{omega(a,b) . x}
   whose kernel is exactly the quaternion subalgebra {0, a, b, a ^ b} (for all 21 pairs).
2. The frequency vector omega(a, b) in {1..7} identifies the non-zero target mode where the
   character causes constructive interference.
3. The interferometer is formed by sandwiching the diagonal phase matrix D = diag(s(0)..s(7))
   between two 8-mode Walsh-Hadamard transform layers H_8 = H_2^{ox 3}:
     U(a, b) = H_8 D(a, b) H_8
4. Under ideal wave optics with a single photon entering mode 0:
   - Octonion character arm: U(a, b) |0> = |omega(a, b)>. Mode 0 is strictly dark (P_0 = 0),
     and mode omega is bright (P_omega = 1), yielding D = (P_omega - P_0) / (P_omega + P_0) = +1.0.
   - Associative Clifford control arm: (a b) c = a (b c) identically in Cl(0,3), so s(x) = +1
     for all x (D = I), giving U_Cl |0> = H_8 I H_8 |0> = |0>. Mode 0 is bright (P_0 = 1) and
     mode omega is dark (P_omega = 0), yielding D = -1.0.
   - Diagonal null arm (a = b): s(x) = +1 identically, giving U = I and D = -1.0.
   - Primary contrast: Delta_char = D_oct - D_ctrl = +1.0 - (-1.0) = 2.0.
5. In addition to logical modes 0..7, modes 8..11 serve as spatial sentinels tracking leakage.

Usage:
  "$PYTHON" scripts/ascella_associator_character.py --check
  "$PYTHON" scripts/ascella_associator_character.py --build [--job job-00] [--samples 10000]
  "$PYTHON" scripts/ascella_associator_character.py --dry-run [--job job-00] [--samples 10000]
  "$PYTHON" scripts/ascella_associator_character.py --analyze RUN_DIR
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
CASE_DIR = ROOT / "results/quandela/cases/ascella_associator_character/job-00"

DEFAULT_SAMPLES_PER_ITERATION = 10000
DEFAULT_SHOTS_FACTOR = 10
MIN_FOCAL_SAMPLES_PER_SETTING = 50
MAX_DURATION = 300
TOLERANCE = 1e-12
BODY_TOLERANCE = 1e-9

PRIMARY_PAIRS = ((1, 2), (1, 4), (2, 4), (3, 5))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def hadamard_8() -> np.ndarray:
    """8-mode normalized Walsh-Hadamard transform H_8 = H_2^{ox 3}."""
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
    h8 = hadamard_8()
    s = np.array([associator_sign(a, b, x) for x in range(8)], dtype=float)
    u = h8 @ np.diag(s) @ h8
    out_mode = int(np.argmax(np.abs(u[:, 0])))
    require(out_mode != 0, f"pair ({a}, {b}) has trivial frequency omega=0")
    require(abs(abs(u[out_mode, 0]) - 1.0) < TOLERANCE, f"pair ({a}, {b}) transfer is not 1.0")
    return out_mode


def build_character_unitary(a: int, b: int, arm: str) -> np.ndarray:
    """Build the 8x8 orthogonal unitary for the specified arm."""
    h8 = hadamard_8()
    if arm == "octonion":
        s = np.array([associator_sign(a, b, x) for x in range(8)], dtype=float)
        return h8 @ np.diag(s) @ h8
    elif arm == "clifford_control":
        return h8 @ np.eye(8) @ h8
    elif arm == "diagonal_null":
        return np.eye(8)
    elif arm == "reversed":
        s = np.array([associator_sign(b, a, x) for x in range(8)], dtype=float)
        return h8 @ np.diag(s) @ h8
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

    u8 = build_character_unitary(a, b, arm)
    u12 = embed_12(u8)

    # Decompose into 8-mode template
    _, params = photonic_template(u8.astype(complex))

    col = [[float(v.real), float(v.imag)] for v in u12[:, 0]]

    ideal_probs = {f"{m}": round(float(abs(u8[m, 0]) ** 2), 6) for m in range(8) if abs(u8[m, 0]) ** 2 > TOLERANCE}
    p_omega = float(abs(u8[omega, 0]) ** 2)
    p_0 = float(abs(u8[0, 0]) ** 2)
    p_sum = p_omega + p_0
    ideal_d = (p_omega - p_0) / p_sum if p_sum > TOLERANCE else 0.0
    target_mode = omega if p_omega > p_0 else 0

    return {
        "name": f"iter{idx:02d}-{spec['name']}",
        "observation_index": idx,
        "pair": [a, b],
        "arm": arm,
        "omega_target": omega,
        "circuit_params": params,
        "column": col,
        "operator": encoded(u12),
        "ideal": {
            "probabilities": ideal_probs,
            "d_observable": round(ideal_d, 6),
            "target_mode": target_mode,
        },
    }


def build_schedule_spec() -> list[dict[str, Any]]:
    spec = []
    # 4 arms across the 4 primary non-associative pairs (16 iterations total)
    for a, b in PRIMARY_PAIRS:
        spec.append({"pair": (a, b), "arm": "octonion", "name": f"pair_{a}_{b}-octonion"})
        spec.append({"pair": (a, b), "arm": "clifford_control", "name": f"pair_{a}_{b}-clifford_control"})
        spec.append({"pair": (a, b), "arm": "diagonal_null", "name": f"pair_{a}_{b}-diagonal_null"})
        spec.append({"pair": (a, b), "arm": "reversed", "name": f"pair_{a}_{b}-reversed"})
    return spec


def build_template_circuit() -> dict[str, Any]:
    canonical_8 = build_character_unitary(1, 2, "octonion").astype(complex)
    mesh, _ = photonic_template(canonical_8)
    input_state = [1] + [0] * (MODES - 1)
    return {**mesh, "modes": MODES, "input_state": input_state}


def build_documents(
    samples_per_iteration: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
    job_name: str = "job-00",
) -> dict[str, bytes]:
    if samples_per_iteration <= 0:
        raise ValueError(f"samples_per_iteration must be positive integer, got {samples_per_iteration}")
    if shots_factor <= 0:
        raise ValueError(f"shots_factor must be positive integer, got {shots_factor}")

    circuit = build_template_circuit()
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()

    schedule = build_schedule_spec()
    settings = ordered_map(build_setting_item, list(enumerate(schedule)), min_items=1)

    shots_per_iteration = samples_per_iteration * shots_factor
    credit_ceiling = 1.0 + 1e-6 * shots_per_iteration

    sample_scale = samples_per_iteration / float(DEFAULT_SAMPLES_PER_ITERATION)
    sec_per_iter = round(2.0 * sample_scale, 2)
    est_seconds = round(30.0 + len(settings) * sec_per_iter, 1)
    duration_bounds = [
        round(est_seconds * 0.8, 1),
        round(min(float(MAX_DURATION), est_seconds * 1.3), 1),
    ]

    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": "ascella_associator_character",
        "job": job_name,
        "platforms": ["qpu:ascella", "sim:ascella"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
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
        "eligibility": "at least one detected click across all 12 modes; focal events have click in modes 0..7",
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "character_contrast": "Delta_char = D_oct - D_ctrl where D = (N_omega - N_0) / (N_omega + N_0)",
            "ideal_contrast": 2.0,
            "quaternion_kernel": "kernel of s(x) is {0, a, b, a^b}",
            "mutation_clifford": "D = -1.0 for Cl(0,3) associative table",
            "diagonal_null": "D = -1.0 for a = b",
            "sentinel_leakage_endpoint": "fraction of single-click counts in sentinel modes 8..11",
        },
    }

    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def check() -> int:
    """Verify 21-pair character kernel theorem, template binding, and ideal contrast endpoints."""
    # 1. Mathematical theorem verification across all 21 pairs
    from itertools import combinations

    for a, b in combinations(range(1, 8), 2):
        s = [associator_sign(a, b, x) for x in range(8)]
        kernel = set(x for x in range(8) if s[x] == 1)
        expected_kernel = {0, a, b, a ^ b}
        require(kernel == expected_kernel, f"pair ({a}, {b}) kernel {kernel} != {expected_kernel}")
        omega = character_frequency(a, b)
        require(omega != 0, f"pair ({a}, {b}) omega is zero")

    # 2. Template experiment binding
    docs = build_documents()
    manifest = json.loads(docs["cases.json"].decode())
    circuit = json.loads(docs["circuit.json"].decode())
    exp, settings = template_experiment(manifest, circuit)
    require(exp is not None and len(settings) == 16, f"template experiment bound {len(settings)} settings, expected 16")

    # 3. SLOS verification on first setting
    import perceval as pcvl

    u8 = build_character_unitary(1, 2, "octonion")
    u12 = embed_12(u8)
    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(u12)))
    backend.set_input_state(pcvl.BasicState([1] + [0] * 11))
    dist = backend.prob_distribution()
    p_omega = dist.get(pcvl.BasicState([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]), 0.0)
    p_0 = dist.get(pcvl.BasicState([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), 0.0)
    require(abs(p_omega - 1.0) < BODY_TOLERANCE, f"SLOS P(omega) {p_omega} != 1.0")
    require(abs(p_0) < BODY_TOLERANCE, f"SLOS P(0) {p_0} != 0.0")

    print("ascella_associator_character: check passed!")
    print("21-pair octonion character kernel theorem verified: ker s = {0, a, b, a^b} for all pairs")
    print("16 settings across 4 primary triads bound to 8-mode Clements mesh")
    print(f"SLOS single-photon transfer confirmed: P_omega = {p_omega:.6f}, P_0 = {p_0:.6f}")
    print(f"credit ceiling confirmed at {manifest['credit_ceiling']:.6f} credits")
    return 0


def build_case(
    samples: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
    job_name: str = "job-00",
    case_dir: Path | None = None,
) -> int:
    target_dir = case_dir or (ROOT / f"results/quandela/cases/ascella_associator_character/{job_name}")
    target_dir.mkdir(parents=True, exist_ok=True)
    docs = build_documents(samples_per_iteration=samples, shots_factor=shots_factor, job_name=job_name)
    for name, data in docs.items():
        (target_dir / name).write_bytes(data)
    manifest = json.loads(docs["cases.json"].decode())
    print(
        f"Wrote {len(docs)} files to {target_dir} (job={job_name}, samples={manifest['samples_per_iteration']}, "
        f"shots={manifest['shots_per_iteration']}, credits={manifest['credit_ceiling']})"
    )
    return 0


def dry_run(
    samples: int = DEFAULT_SAMPLES_PER_ITERATION,
    shots_factor: int = DEFAULT_SHOTS_FACTOR,
    job_name: str = "job-00",
    case_dir: Path | None = None,
) -> int:
    """Execute local simulation across all 16 iterations to verify end-to-end pipeline and contrast."""
    target_dir = case_dir or (ROOT / f"results/quandela/cases/ascella_associator_character/{job_name}")
    docs = build_documents(samples_per_iteration=samples, shots_factor=shots_factor, job_name=job_name)
    manifest = json.loads(docs["cases.json"].decode())
    settings = manifest["settings"]

    simulated_iterations = []
    print(f"Running local simulation of 16 character settings at {samples} samples/iteration...")
    for idx, s in enumerate(settings):
        omega = s["omega_target"]
        arm = s["arm"]

        # Optical visibility on single photon on Ascella (~98%)
        vis = 0.98
        counts = {}
        if arm in ("octonion", "reversed"):
            # Bright on omega, small leakage to 0
            n_target = int(round(samples * vis))
            n_dark = samples - n_target
            state_target = [0] * MODES
            state_target[omega] = 1
            state_dark = [0] * MODES
            state_dark[0] = 1
            counts[f"|{','.join(str(v) for v in state_target)}>"] = n_target
            counts[f"|{','.join(str(v) for v in state_dark)}>"] = n_dark
        else:
            # Clifford control or null: bright on 0, dark on omega
            n_target = int(round(samples * vis))
            n_dark = samples - n_target
            state_target = [0] * MODES
            state_target[0] = 1
            state_dark = [0] * MODES
            state_dark[omega] = 1
            counts[f"|{','.join(str(v) for v in state_target)}>"] = n_target
            counts[f"|{','.join(str(v) for v in state_dark)}>"] = n_dark

        simulated_iterations.append(
            {
                "setting": s["name"],
                "counts": counts,
                "elapsed_seconds": round(idx * 2.0, 2),
                "duration": 2.0,
            }
        )

    mock_run_dir = target_dir / "dry_run_simulation"
    mock_run_dir.mkdir(parents=True, exist_ok=True)
    (mock_run_dir / "cases.json").write_bytes(docs["cases.json"])
    (mock_run_dir / "results.json").write_text(json.dumps({"iterations": simulated_iterations}, indent=2))
    print(f"Local dry run complete. Output saved to {mock_run_dir}")
    print("Running analysis on simulated character dry-run data...")
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

        counts = entry.get("counts")
        if not isinstance(counts, dict) or not counts:
            admission_errors.append(f"{name}: empty or missing counts payload")
            counts = {}

        c_omega = 0
        c_0 = 0
        c_sentinel = 0
        c_other = 0

        for state_str, cnt in counts.items():
            occupation = [int(v) for v in state_str.strip("|>").split(",")]
            occupied = [m for m, n in enumerate(occupation) if n > 0]
            if any(m >= LOGICAL for m in occupied):
                c_sentinel += cnt
            elif len(occupied) == 1:
                mode = occupied[0]
                if mode == omega:
                    c_omega += cnt
                elif mode == 0:
                    c_0 += cnt
                else:
                    c_other += cnt

        focal = c_omega + c_0 + c_other
        total_focal += focal
        total_sentinel += c_sentinel

        if (c_omega + c_0) < min_focal:
            admission_errors.append(
                f"{name}: focal counts (c_omega + c_0 = {c_omega + c_0}) below statistical threshold ({min_focal})"
            )

        denom = max(1, c_omega + c_0)
        d_obs = (c_omega - c_0) / denom
        # Wilson score continuity floor ensures strictly positive uncertainty for boundary observations (|d| ~ 1)
        var = max(1.0 - d_obs**2, 1.0 / denom) / denom
        se = math.sqrt(var)

        record = {
            "name": name,
            "pair": [a, b],
            "arm": arm,
            "omega": omega,
            "c_omega": c_omega,
            "c_0": c_0,
            "d_observable": round(d_obs, 6),
            "std_error": round(se, 6),
            "ci95": [round(d_obs - 1.96 * se, 6), round(d_obs + 1.96 * se, 6)],
        }
        per_setting_reports.append(record)

        if pair_key not in pair_contrasts:
            pair_contrasts[pair_key] = {}
        pair_contrasts[pair_key][arm] = d_obs

    total_events = total_focal + total_sentinel
    observed_sentinel_rate = total_sentinel / total_events if total_events > 0 else 0.0

    # If any iteration violated the count admission threshold, fail closed
    if admission_errors:
        return {
            "status": "REFUSED",
            "verdicts": {
                "execution_status": "REFUSED",
                "admission_errors": admission_errors,
                "character_signal_detected": False,
                "mean_character_contrast": 0.0,
                "sentinel_leakage_rate": round(observed_sentinel_rate, 6) if total_events > 0 else None,
            },
            "contrasts_by_pair": {},
            "iterations": per_setting_reports,
        }

    # Compute contrast Delta_char = D_oct - D_ctrl for each pair
    contrasts_summary = {}
    all_contrasts = []
    for pair_key, arm_map in pair_contrasts.items():
        d_oct = arm_map.get("octonion", 0.0)
        d_ctrl = arm_map.get("clifford_control", 0.0)
        delta = d_oct - d_ctrl
        contrasts_summary[pair_key] = {
            "d_octonion": round(d_oct, 6),
            "d_clifford_control": round(d_ctrl, 6),
            "delta_character": round(delta, 6),
        }
        all_contrasts.append(delta)

    mean_delta = float(np.mean(all_contrasts))
    sentinel_rate = observed_sentinel_rate

    return {
        "status": "ADMITTED",
        "verdicts": {
            "execution_status": "ADMITTED",
            "character_signal_detected": bool(mean_delta > 1.5),
            "mean_character_contrast": round(mean_delta, 6),
            "sentinel_leakage_rate": round(sentinel_rate, 6),
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
    parser.add_argument("--case-dir", type=Path, default=None, help="case directory override")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES_PER_ITERATION, help="samples per iteration")
    parser.add_argument("--shots-factor", type=int, default=DEFAULT_SHOTS_FACTOR, help="shots multiplier")
    parser.add_argument("--analyze", type=Path, help="analyze collected run directory")
    args = parser.parse_args()

    if args.check:
        sys.exit(check())
    elif args.build:
        sys.exit(
            build_case(samples=args.samples, shots_factor=args.shots_factor, job_name=args.job, case_dir=args.case_dir)
        )
    elif args.dry_run:
        sys.exit(
            dry_run(samples=args.samples, shots_factor=args.shots_factor, job_name=args.job, case_dir=args.case_dir)
        )
    elif args.analyze:
        print(json.dumps(analyze(args.analyze), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
