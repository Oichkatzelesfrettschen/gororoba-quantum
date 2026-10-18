"""Preregistered initial excitation of an n21 placement from state-prep-control raw shots.

The Sampler's implicit initialization (init_qubits) is imperfect, and the
residual excitation it leaves grows with the |1> population the previous shot
left behind and shrinks with the repetition delay. The x_history arm (init,
measure, x) reads every qubit's initial state after a shot that ended in |1>,
the largest end-of-shot excited population an n21 shot can leave; prep0
(init, measure) reads it after a history near |0>. The shots of one job's circuits
interleave, so prep0 and x_history counts come only from a job holding no
other arm: an x PUB beside prep0 would give some prep0 shots a |1> history.

Rule, for each qubit q of the placement S of an n21 record, with the
family-wise alpha split evenly over 5|S| one-sided Clopper-Pearson bounds
(five per qubit):

- U50_q, U250_q: upper bounds on the x_history excited fraction at 50 us
  and 250 us.
- L0_q: lower bound on the prep0 excited fraction at 250 us.
- e10_q lower and e01_q upper bounds: the calibration's prob_meas1_prep0 and
  prob_meas0_prep1 are k/4096 estimates, read as k excited outcomes in 4096
  calibration shots.
- b_q = min(e10_q lower, L0_q).
- eps50_q = max(0, state_prep_excitation(U50_q, b_q, e01_q upper)), and
  eps250_q the same with U250_q.

eps = (P - e10) / (1 - e01 - e10) rises in P, falls in e10 wherever
P < 1 - e01 and rises in e01 wherever P > e10, so the upper P, the lower
baseline and the upper e01 give the largest eps the data admit; an upper P
at or above 1 - e01 reverses the e10 direction and the rule refuses it.
eps50 and eps250 are the maxima over S. prep0 at 50 us, where present,
enters the report as a history-versus-delay decomposition of point estimates
and stays outside the bound family. The calibration is the n21 record's
placed_qubit_calibration, the readout channel its model applies.

Placement and eps depend on each other, so the plan iterates to a fixed
point: plan at --prep-excitation 0, read S0, compute eps(S0) at the plan's
delay; while eps(S_k) exceeds the eps_k planned with, re-plan at
eps_{k+1} = max(eps_k, eps(S_k)) and read S_{k+1}; stop at the first k with
eps(S_k) <= eps_k. eps_k never decreases and every eps(S) is a maximum of
per-qubit values over the qubits with control data, a finite set, so the
iteration stops. The report's fixed_point block carries the verdict and the
next --prep-excitation, rounded up to 1e-6.

Each run writes state-prep-excess.json beside the n21 record; --check
recomputes every retained one from the inputs it names and requires the same
bytes, and --self-test exercises the rule on synthetic runs in the raw layout
live_run --collect writes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from diagnostic_experiments import (  # noqa: E402
    N21_FAMILIES,
    STATE_PREP_FAMILY,
    STATE_PREP_HISTORY_ARM,
    state_prep_excitation,
)

SCHEMA = "state-prep-excess-v1"
OUTPUT_NAME = "state-prep-excess.json"
SHORT_DELAY = 5e-05
LONG_DELAY = 2.5e-04
DELAY_LABELS = {SHORT_DELAY: "50us", LONG_DELAY: "250us"}
# Every prob_meas1_prep0 and prob_meas0_prep1 of the Heron r2 properties is a
# multiple of 1/4096: the inferred number of calibration shots per state.
CALIBRATION_SHOTS = 4096
BOUNDS_PER_QUBIT = 5
DEFAULT_ALPHA = 0.01
# The x_history fraction at each delay and prep0 at 250 us enter the rule.
REQUIRED_CELLS = ((STATE_PREP_HISTORY_ARM, SHORT_DELAY), (STATE_PREP_HISTORY_ARM, LONG_DELAY), ("prep0", LONG_DELAY))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(payload: Any) -> bytes:
    return (json.dumps(payload, indent=1, sort_keys=True, allow_nan=False) + "\n").encode()


def cp_upper(successes: Any, trials: Any, level: float) -> np.ndarray:
    """One-sided Clopper-Pearson upper bounds: P(Binomial(n, U) <= k) = level, and U = 1 at k = n."""
    k = np.asarray(successes, dtype=float)
    n = np.asarray(trials, dtype=float)
    bound = np.ones(k.shape)
    inside = k < n
    bound[inside] = beta.ppf(1.0 - level, k[inside] + 1.0, n[inside] - k[inside])
    return bound


def cp_lower(successes: Any, trials: Any, level: float) -> np.ndarray:
    """One-sided Clopper-Pearson lower bounds: P(Binomial(n, L) >= k) = level, and L = 0 at k = 0."""
    k = np.asarray(successes, dtype=float)
    n = np.asarray(trials, dtype=float)
    bound = np.zeros(k.shape)
    inside = k > 0
    bound[inside] = beta.ppf(level, k[inside], n[inside] - k[inside] + 1.0)
    return bound


def _delay(value: Any, where: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{where}: no repetition delay")
    for delay in DELAY_LABELS:
        if math.isclose(float(value), delay, rel_tol=1e-9, abs_tol=0.0):
            return delay
    raise ValueError(f"{where}: repetition delay {value} s lies outside the rule's 50 us and 250 us")


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{path} lies outside {root}") from error


def read_control(run_dir: Path, root: Path) -> dict[str, Any]:
    """Per-qubit excited counts of one submitted state-prep-control run, read from raw/<job_id>/.

    record.json's submission names each job, its options and its PUB
    manifests; a manifest component maps a member spc_<arm>_q<qubit> on its
    one physical qubit to a one-bit register of the PUB file. Every PUB file
    must carry the sha256 index.json recorded for it.
    """
    record_bytes = (run_dir / "record.json").read_bytes()
    record = json.loads(record_bytes)
    configuration = record.get("family_configuration") or {}
    require(configuration.get("name") == STATE_PREP_FAMILY, f"{run_dir}: not a state-prep-control record")
    arms = list(configuration.get("arms") or ())
    require(bool(arms), f"{run_dir}: the record names no arms")
    jobs = (record.get("submission") or {}).get("jobs") or []
    require(bool(jobs), f"{run_dir}: the record holds no submitted job")
    policy_delay = (record.get("policy") or {}).get("rep_delay_seconds")
    counts: dict[str, dict[int, list[int]]] = {}
    raw_digests: dict[str, str] = {}
    delays = set()
    backends = set()
    for job in jobs:
        job_id = str(job["job_id"])
        options = job.get("options") or {}
        execution = options.get("execution") or {}
        delay = _delay(execution.get("rep_delay"), f"{run_dir} job {job_id}")
        if policy_delay is not None:
            require(_delay(policy_delay, f"{run_dir} policy") == delay, f"{run_dir}: job and policy delays differ")
        require(execution.get("init_qubits", True) is True, f"{run_dir} job {job_id}: init_qubits is off")
        twirling = options.get("twirling") or {}
        require(
            not twirling.get("enable_measure") and not twirling.get("enable_gates"),
            f"{run_dir} job {job_id}: twirling changes the readout channel the rule inverts",
        )
        delays.add(delay)
        backends.add(str(job["backend"]))
        job_arms = {
            str(component["member"]).removeprefix("spc_").rsplit("_q", 1)[0]
            for manifest in job["pubs"]
            for component in manifest["components"]
        }
        require(
            not job_arms & {"prep0", STATE_PREP_HISTORY_ARM} or len(job_arms) == 1,
            f"{run_dir} job {job_id}: arms {sorted(job_arms)} share one job, so their shots set each other's history",
        )
        raw = run_dir / "raw" / job_id
        require((raw / "index.json").is_file(), f"{run_dir} job {job_id}: no raw result under raw/{job_id}")
        index = json.loads((raw / "index.json").read_text())
        require(index.get("job_id") == job_id, f"{raw}: index.json names another job")
        for position, manifest in enumerate(job["pubs"]):
            name = f"pub_{position:02d}.json"
            require(name in index.get("files", {}), f"{raw}: index.json lacks {name}")
            data = (raw / name).read_bytes()
            digest = sha256_bytes(data)
            require(digest == index["files"][name], f"{raw / name}: sha256 differs from index.json")
            raw_digests[_relative(raw / name, root)] = digest
            payload = json.loads(data)
            require(
                payload.get("pub_index") == position and payload.get("pub_name") == manifest["name"],
                f"{raw / name}: holds another PUB than {manifest['name']}",
            )
            for component in manifest["components"]:
                member = str(component["member"])
                require(member.startswith("spc_") and "_q" in member, f"{member}: not a state-prep member")
                arm, qubit_text = member.removeprefix("spc_").rsplit("_q", 1)
                qubit = int(qubit_text)
                require(arm in arms, f"{run_dir}: member {member} of an unselected arm")
                require(component["physical_qubits"] == [qubit], f"{member}: placed on {component['physical_qubits']}")
                registers = component["registers_by_replica"]
                require(len(registers) == 1 and len(registers[0]) == 1, f"{member}: expects one register")
                register = payload["registers"][registers[0][0]]
                bitstrings = register["bitstrings"]
                shots = int(register["num_shots"])
                require(int(register["num_bits"]) == 1, f"{member}: register holds {register['num_bits']} bits")
                ones = bitstrings.count("1")
                require(
                    len(bitstrings) == shots and ones + bitstrings.count("0") == shots,
                    f"{member}: {len(bitstrings)} outcomes for {shots} shots",
                )
                cell = counts.setdefault(arm, {})
                require(qubit not in cell, f"{run_dir}: two registers read {member}")
                cell[qubit] = [ones, shots]
    require(len(delays) == 1 and len(backends) == 1, f"{run_dir}: jobs span delays {delays} or backends {backends}")
    return {
        "path": _relative(run_dir, root),
        "record_sha256": sha256_bytes(record_bytes),
        "raw_sha256": raw_digests,
        "backend": backends.pop(),
        "rep_delay_seconds": delays.pop(),
        "arms": arms,
        "job_ids": sorted(str(job["job_id"]) for job in jobs),
        "planning_calibrations": sorted({str(group.get("calibration")) for group in record.get("groups", [])}),
        "counts": counts,
    }


def read_placement(record_path: Path, root: Path) -> dict[str, Any]:
    """Placed qubits, their readout calibration, the plan's delay and the excitation it was planned with."""
    data = record_path.read_bytes()
    record = json.loads(data)
    family = (record.get("family_configuration") or {}).get("name")
    require(family in N21_FAMILIES, f"{record_path}: family {family} is not an n21 family")
    groups = record.get("groups") or []
    require(bool(groups), f"{record_path}: the record places no group")
    backends = {str(group["backend"]) for group in groups}
    require(len(backends) == 1, f"{record_path}: groups span backends {sorted(backends)}")
    backend = next(iter(backends))
    qubits = sorted({int(q) for group in groups for replica in group["replicas"] for q in replica["physical_qubits"]})
    calibration: dict[int, tuple[float, float]] = {}
    for group in groups:
        for key, values in (group.get("placed_qubit_calibration") or {}).items():
            pair = (float(values["prob_meas1_prep0"]), float(values["prob_meas0_prep1"]))
            require(calibration.setdefault(int(key), pair) == pair, f"{record_path}: q{key} carries two calibrations")
    missing = [q for q in qubits if q not in calibration]
    require(not missing, f"{record_path}: placed qubits {missing} lack placed_qubit_calibration")
    contract = [
        entry for entry in (record.get("execution_contract") or {}).get("backends", []) if entry["name"] == backend
    ]
    require(len(contract) == 1, f"{record_path}: the execution contract names no {backend} delay")
    planned = (record.get("policy") or {}).get("design", {}).get("prep_excitation")
    return {
        "path": _relative(record_path, root),
        "sha256": sha256_bytes(data),
        "family": family,
        "backend": backend,
        "experiment_digest": record.get("experiment_digest"),
        "noise_model_calibrations": sorted({str(group.get("noise_model_calibration")) for group in groups}),
        "qubits": qubits,
        "calibration": {q: calibration[q] for q in qubits},
        "rep_delay_seconds": _delay(contract[0]["repetition_delay_seconds"], f"{record_path} plan"),
        "planned_prep_excitation": 0.0 if planned is None else float(planned),
    }


def _calibration_count(probability: float, qubit: int, name: str) -> int:
    count = probability * CALIBRATION_SHOTS
    require(
        abs(count - round(count)) < 1e-6 and 0 <= round(count) <= CALIBRATION_SHOTS,
        f"q{qubit} {name} {probability} is not a multiple of 1/{CALIBRATION_SHOTS}",
    )
    return int(round(count))


def _round_up(value: float) -> float:
    """value rounded up to a multiple of 1e-6, never below value, so the next plan covers it."""
    rounded = math.ceil(value * 1e6) / 1e6
    while rounded < value:
        rounded += 1e-6
    return rounded


def excess(placement: dict[str, Any], controls: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    """The rule's per-qubit bounds and eps on placement S, and the fixed-point step for its plan."""
    require(0.0 < alpha < 1.0, f"alpha {alpha} lies outside (0, 1)")
    cells: dict[tuple[str, float], dict[int, list[int]]] = {}
    for control in controls:
        require(control["backend"] == placement["backend"], f"{control['path']}: runs on {control['backend']}")
        for arm, by_qubit in control["counts"].items():
            cell = cells.setdefault((arm, control["rep_delay_seconds"]), {})
            for qubit, pair in by_qubit.items():
                require(qubit not in cell, f"two control runs read {arm} on q{qubit} at {control['rep_delay_seconds']}")
                cell[qubit] = pair
    qubits = placement["qubits"]
    missing = {
        f"{arm}@{DELAY_LABELS[delay]}": [q for q in qubits if q not in cells.get((arm, delay), {})]
        for arm, delay in REQUIRED_CELLS
    }
    missing = {cell: absent for cell, absent in missing.items() if absent}
    require(not missing, f"placed qubits lack control data: {missing}")
    bound_count = BOUNDS_PER_QUBIT * len(qubits)
    level = alpha / bound_count

    def column(arm: str, delay: float) -> tuple[np.ndarray, np.ndarray]:
        pairs = np.asarray([cells[(arm, delay)][q] for q in qubits], dtype=np.int64)
        return pairs[:, 0], pairs[:, 1]

    k10 = np.asarray([_calibration_count(placement["calibration"][q][0], q, "e10") for q in qubits])
    k01 = np.asarray([_calibration_count(placement["calibration"][q][1], q, "e01") for q in qubits])
    shots = np.full(len(qubits), CALIBRATION_SHOTS)
    upper = {delay: cp_upper(*column(STATE_PREP_HISTORY_ARM, delay), level) for delay in (SHORT_DELAY, LONG_DELAY)}
    prep0_lower = cp_lower(*column("prep0", LONG_DELAY), level)
    e10_lower = cp_lower(k10, shots, level)
    e01_upper = cp_upper(k01, shots, level)
    baseline = np.minimum(e10_lower, prep0_lower)
    per_qubit: dict[str, Any] = {}
    eps: dict[float, dict[int, float]] = {SHORT_DELAY: {}, LONG_DELAY: {}}
    for index, qubit in enumerate(qubits):
        row: dict[str, Any] = {
            "calibration": {
                "prob_meas1_prep0": placement["calibration"][qubit][0],
                "prob_meas0_prep1": placement["calibration"][qubit][1],
                "excited_counts": [int(k10[index]), CALIBRATION_SHOTS],
                "relaxed_counts": [int(k01[index]), CALIBRATION_SHOTS],
            },
            "counts": {},
            "bounds": {
                "e10_lower": float(e10_lower[index]),
                "e01_upper": float(e01_upper[index]),
                "prep0_250us_lower": float(prep0_lower[index]),
                "baseline": float(baseline[index]),
            },
            "eps_unclamped": {},
            "eps": {},
        }
        fractions: dict[str, float] = {}
        for (arm, delay), cell in sorted(cells.items()):
            if qubit in cell:
                key = f"{arm}_{DELAY_LABELS[delay]}"
                row["counts"][key] = cell[qubit]
                fractions[key] = cell[qubit][0] / cell[qubit][1]
        row["fractions"] = fractions
        for delay in (SHORT_DELAY, LONG_DELAY):
            label = DELAY_LABELS[delay]
            bound = float(upper[delay][index])
            row["bounds"][f"x_history_{label}_upper"] = bound
            require(
                bound < 1.0 - float(e01_upper[index]),
                f"q{qubit}: x_history upper bound {bound} at {label} reaches 1 - e01, where eps is not monotone",
            )
            value = state_prep_excitation(bound, float(baseline[index]), float(e01_upper[index]))
            row["eps_unclamped"][label] = value
            row["eps"][label] = max(0.0, value)
            eps[delay][qubit] = max(0.0, value)
        if "prep0_50us" in fractions:
            row["decomposition"] = {
                "scope": "point estimates outside the bound family; x_history runs in a dynamic job and prep0 "
                "in a static one, so each history difference spans the job kind as well as the shot history",
                "history_at_50us": fractions["x_history_50us"] - fractions["prep0_50us"],
                "history_at_250us": fractions["x_history_250us"] - fractions["prep0_250us"],
                "delay_after_prep0": fractions["prep0_50us"] - fractions["prep0_250us"],
                "delay_after_x_history": fractions["x_history_50us"] - fractions["x_history_250us"],
            }
        per_qubit[str(qubit)] = row
    maxima = {delay: max(eps[delay].values()) for delay in eps}
    measured = maxima[placement["rep_delay_seconds"]]
    planned = placement["planned_prep_excitation"]
    converged = measured <= planned
    return {
        "schema": SCHEMA,
        "rule": {
            "alpha": alpha,
            "bounds_per_qubit": BOUNDS_PER_QUBIT,
            "bound_count": bound_count,
            "alpha_per_bound": level,
            "calibration_shots": CALIBRATION_SHOTS,
            "bounds": "one-sided Clopper-Pearson: x_history upper at 50 and 250 us, prep0 lower at 250 us, "
            "e10 lower, e01 upper",
            "eps": "max(0, (U - b) / (1 - e01_upper - b)), b = min(e10_lower, prep0_250us_lower)",
        },
        "inputs": {
            "n21_record": {key: placement[key] for key in placement if key not in ("calibration", "qubits")},
            "controls": sorted(
                ({key: value for key, value in control.items() if key != "counts"} for control in controls),
                key=lambda control: str(control["path"]),
            ),
        },
        "placement": {"qubits": qubits, "rep_delay_seconds": placement["rep_delay_seconds"]},
        "qubits": per_qubit,
        "eps50": maxima[SHORT_DELAY],
        "eps250": maxima[LONG_DELAY],
        "argmax50": [q for q in qubits if eps[SHORT_DELAY][q] == maxima[SHORT_DELAY]],
        "argmax250": [q for q in qubits if eps[LONG_DELAY][q] == maxima[LONG_DELAY]],
        "fixed_point": {
            "planned_prep_excitation": planned,
            "measured_at_plan_delay": measured,
            "verdict": "converged" if converged else "replan",
            "next_prep_excitation": planned if converged else max(planned, _round_up(measured)),
        },
    }


def evaluate(record_path: Path, control_dirs: Iterable[Path], alpha: float, root: Path) -> dict[str, Any]:
    placement = read_placement(record_path, root)
    controls = [read_control(run_dir, root) for run_dir in control_dirs]
    require(bool(controls), "the rule needs control runs")
    return excess(placement, controls, alpha)


def write(record_path: Path, control_dirs: Iterable[Path], alpha: float, root: Path) -> Path:
    payload = encode(evaluate(record_path, control_dirs, alpha, root))
    destination = record_path.parent / OUTPUT_NAME
    destination.write_bytes(payload)
    return destination


def check(root: Path) -> int:
    """Recompute every retained output under results/live from the inputs it names and compare bytes."""
    retained = sorted((root / "results" / "live").glob(f"*/{OUTPUT_NAME}"))
    for output in retained:
        payload = json.loads(output.read_bytes())
        inputs = payload["inputs"]
        recomputed = encode(
            evaluate(
                root / inputs["n21_record"]["path"],
                [root / control["path"] for control in inputs["controls"]],
                float(payload["rule"]["alpha"]),
                root,
            )
        )
        require(recomputed == output.read_bytes(), f"{output}: the replay differs from the retained bytes")
    return len(retained)


def _binomial_cdf(k: int, n: int, p: float) -> float:
    """P(Binomial(n, p) <= k) by a compensated sum of lgamma terms, independent of scipy."""
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 1.0 if k >= n else 0.0
    log_p, log_q = math.log(p), math.log1p(-p)
    base = math.lgamma(n + 1)
    return math.fsum(
        math.exp(base - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * log_p + (n - i) * log_q) for i in range(k + 1)
    )


def _bisect(function: Any, target: float) -> float:
    """The root in [0, 1] of a function decreasing in p, to 1e-15."""
    low, high = 0.0, 1.0
    for _ in range(60):
        middle = (low + high) / 2
        if function(middle) > target:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def _synthetic_run(
    root: Path,
    name: str,
    arm: str,
    delay: float,
    counts: dict[int, tuple[int, int]],
    twirl: bool = False,
    companion: str | None = None,
) -> Path:
    """A submitted run directory in live_run's raw layout: one job, one PUB, one-bit register per qubit and arm.

    companion adds a second arm's members, with the same counts, to the same PUB.
    """
    run = root / "results" / "live" / name
    raw = run / "raw" / f"job_{name}"
    raw.mkdir(parents=True)
    arms = [arm] if companion is None else [arm, companion]
    components = []
    registers: dict[str, Any] = {}
    for index, (member_arm, (qubit, (ones, shots))) in enumerate(
        (member_arm, item) for member_arm in arms for item in sorted(counts.items())
    ):
        register = f"g{index}_r0_c"
        components.append(
            {
                "group": f"state_prep_q{qubit}",
                "member": f"spc_{member_arm}_q{qubit}",
                "reference": False,
                "register_prefix": f"g{index}_",
                "physical_qubits": [qubit],
                "registers_by_replica": [[register]],
            }
        )
        registers[register] = {"num_bits": 1, "num_shots": shots, "bitstrings": ["1"] * ones + ["0"] * (shots - ones)}
    kind = "dynamic" if arm == STATE_PREP_HISTORY_ARM else "static"
    pub_name = f"fake_backend_{kind}_pub_01"
    pub = encode({"pub_index": 0, "pub_name": pub_name, "registers": registers, "metadata": {}})
    (raw / "pub_00.json").write_bytes(pub)
    (raw / "index.json").write_bytes(encode({"job_id": f"job_{name}", "files": {"pub_00.json": sha256_bytes(pub)}}))
    record = {
        "family_configuration": {
            "name": STATE_PREP_FAMILY,
            "qubits": sorted(counts),
            "arms": {member_arm: "steps" for member_arm in arms},
        },
        "policy": {"rep_delay_seconds": delay, "twirl": twirl},
        "groups": [{"backend": "fake_backend", "calibration": "2026-01-01T00:00:00Z"}],
        "submission": {
            "jobs": [
                {
                    "job_id": f"job_{name}",
                    "backend": "fake_backend",
                    "options": {
                        "execution": {"rep_delay": delay, "init_qubits": True},
                        "twirling": {"enable_measure": True if twirl else None, "enable_gates": None},
                    },
                    "pubs": [{"name": pub_name, "kind": kind, "components": components}],
                }
            ]
        },
    }
    (run / "record.json").write_bytes(encode(record))
    return run


def _synthetic_placement(root: Path, calibration: dict[int, tuple[float, float]], planned: float | None) -> Path:
    run = root / "results" / "live" / "n21-plan"
    run.mkdir(parents=True)
    record = {
        "family_configuration": {"name": "n21-feedback-encoded"},
        "experiment_digest": "0" * 64,
        "policy": {"design": {} if planned is None else {"prep_excitation": planned}, "rep_delay_seconds": SHORT_DELAY},
        "execution_contract": {"backends": [{"name": "fake_backend", "repetition_delay_seconds": SHORT_DELAY}]},
        "groups": [
            {
                "backend": "fake_backend",
                "noise_model_calibration": "2026-01-01T00:00:00Z",
                "replicas": [{"physical_qubits": sorted(calibration)}],
                "placed_qubit_calibration": {
                    str(q): {"prob_meas1_prep0": k10 / CALIBRATION_SHOTS, "prob_meas0_prep1": k01 / CALIBRATION_SHOTS}
                    for q, (k10, k01) in calibration.items()
                },
            }
        ],
    }
    path = run / "record.json"
    path.write_bytes(encode(record))
    return path


def _expect_refusal(action: Any, fragment: str) -> None:
    try:
        action()
    except ValueError as error:
        require(fragment in str(error), f"refused for another reason: {error}")
        return
    raise AssertionError(f"accepted input the rule refuses ({fragment})")


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="state-prep-excess-") as scratch:
        _self_test(Path(scratch))


def _self_test(scratch: Path) -> None:
    # Clopper-Pearson bounds against an independent binomial-tail inversion.
    cases = [(0, 50), (3, 50), (50, 50), (0, 4096), (109, 4096), (4096, 4096), (281, 32768), (1500, 16384)]
    for level in (0.01 / 35, 0.05):
        for k, n in cases:
            upper = float(cp_upper([k], [n], level)[0])
            lower = float(cp_lower([k], [n], level)[0])
            reference_upper = 1.0 if k == n else _bisect(lambda p, k=k, n=n: _binomial_cdf(k, n, p), level)
            reference_lower = 0.0 if k == 0 else _bisect(lambda p, k=k, n=n: _binomial_cdf(k - 1, n, p), 1.0 - level)
            require(abs(upper - reference_upper) <= 1e-9, f"upper bound {k}/{n}: {upper} vs {reference_upper}")
            require(abs(lower - reference_lower) <= 1e-9, f"lower bound {k}/{n}: {lower} vs {reference_lower}")
            require(lower <= k / n <= upper, f"{k}/{n}: bounds exclude the fraction")
    calibration: dict[int, tuple[float, float]] = {3: (40, 60), 4: (109, 106), 7: (20, 50)}
    base = {
        "history50": {3: (300, 32768), 4: (900, 32768), 7: (150, 32768)},
        "history250": {3: (120, 16384), 4: (400, 16384), 7: (60, 16384)},
        "prep0_250": {3: (150, 16384), 4: (430, 16384), 7: (70, 16384)},
    }

    roots = (scratch / str(index) for index in range(1000))

    def run(
        overrides: dict[str, dict[int, tuple[int, int]]] | None = None,
        cal: dict[int, tuple[float, float]] | None = None,
        planned: float | None = None,
        prep0_50: dict[int, tuple[int, int]] | None = None,
        twirl: bool = False,
        companion: str | None = None,
    ) -> tuple[Path, dict[str, Any]]:
        sets = {**base, **(overrides or {})}
        root = next(roots)
        record = _synthetic_placement(root, cal or calibration, planned)
        controls = [
            _synthetic_run(root, "h50", STATE_PREP_HISTORY_ARM, SHORT_DELAY, sets["history50"], twirl),
            _synthetic_run(root, "h250", STATE_PREP_HISTORY_ARM, LONG_DELAY, sets["history250"]),
            _synthetic_run(root, "p250", "prep0", LONG_DELAY, sets["prep0_250"], companion=companion),
        ]
        if prep0_50 is not None:
            controls.append(_synthetic_run(root, "p50", "prep0", SHORT_DELAY, prep0_50))
        return root, evaluate(record, controls, DEFAULT_ALPHA, root)

    root, result = run()
    require(result["rule"]["bound_count"] == 15, f"bound count {result['rule']['bound_count']} for 3 qubits")
    require(math.isclose(result["rule"]["alpha_per_bound"] * 15, DEFAULT_ALPHA), "the alpha split moved")
    require(result["eps50"] == max(row["eps"]["50us"] for row in result["qubits"].values()), "eps50 is not the max")
    require(result["argmax50"] == [4], f"arg-max {result['argmax50']}")
    require(result["eps50"] > result["eps250"] > 0, "the synthetic history excess vanished")
    # The CLI path writes, and the replay reproduces the bytes.
    destination = write(
        root / "results/live/n21-plan/record.json", sorted((root / "results/live").glob("[hp]*")), DEFAULT_ALPHA, root
    )
    require(destination.name == OUTPUT_NAME and check(root) == 1, "the replay found no retained output")
    raw = root / "results/live/h50/raw/job_h50/pub_00.json"
    raw.write_bytes(raw.read_bytes().replace(b'"0"', b'"1"', 1))
    _expect_refusal(lambda: check(root), "sha256 differs")
    # Monotonicity on q4, whose calibration e10 sets the baseline: eps rises with the history fraction and
    # with e01, falls with e10, and rises when a lower prep0 bound takes over the baseline.
    reference = result["qubits"]["4"]
    require(reference["bounds"]["baseline"] == reference["bounds"]["e10_lower"], "e10 does not set the baseline")
    for label, outcome, sign in (
        ("history fraction", run({"history50": {**base["history50"], 4: (950, 32768)}}), 1),
        ("e10", run(cal={**calibration, 4: (120, 106)}), -1),
        ("e01", run(cal={**calibration, 4: (109, 140)}), 1),
        ("prep0 baseline", run({"prep0_250": {**base["prep0_250"], 4: (200, 16384)}}), 1),
    ):
        shifted = outcome[1]["qubits"]["4"]
        moved = shifted["eps"]["50us"] - reference["eps"]["50us"]
        require(moved * sign > 0, f"raising the {label} moved eps by {moved}")
    require(shifted["bounds"]["baseline"] == shifted["bounds"]["prep0_250us_lower"], "prep0 left the baseline")
    # Clamping: a qubit with no history excitation reads eps 0 from a negative value.
    clamped = run({"history50": {**base["history50"], 7: (0, 32768)}})[1]["qubits"]["7"]
    require(clamped["eps"]["50us"] == 0.0 and clamped["eps_unclamped"]["50us"] < 0, "eps was not clamped at 0")
    # prep0 at 50 us is reported and leaves the rule unchanged.
    reported = run(prep0_50={3: (160, 32768), 4: (450, 32768), 7: (80, 32768)})[1]
    require(reported["eps50"] == result["eps50"] and reported["eps250"] == result["eps250"], "prep0 50 us moved eps")
    require("decomposition" in reported["qubits"]["4"] and "decomposition" not in result["qubits"]["4"], "report")
    # Fixed point: below the planned value the plan stands; above it the next plan rises, rounded up.
    step = result["fixed_point"]
    require(step["verdict"] == "replan" and step["next_prep_excitation"] >= result["eps50"], f"{step}")
    stays = run(planned=0.5)[1]["fixed_point"]
    require(stays["verdict"] == "converged" and stays["next_prep_excitation"] == 0.5, f"{stays}")
    # Refusals: a placed qubit without control data, twirled readout, prep0 sharing its job with x, a
    # saturated bound, an off-grid calibration.
    _expect_refusal(lambda: run({"history250": {3: (120, 16384), 4: (400, 16384)}}), "lack control data")
    _expect_refusal(lambda: run(twirl=True), "twirling")
    _expect_refusal(lambda: run(companion="x"), "share one job")
    _expect_refusal(lambda: run({"history50": {**base["history50"], 3: (32700, 32768)}}), "not monotone")
    _expect_refusal(lambda: run(cal={**calibration, 3: (40.5, 60)}), "multiple of 1/4096")
    print(
        "state_prep_excess: Clopper-Pearson bounds match the binomial-tail inversion to 1e-9; 5|S| bounds share "
        "alpha; eps rises with the history fraction and e01, falls with the baseline, clamps at 0; prep0 at 50 us "
        "stays outside the rule; the fixed point never lowers eps; refusals hold and the replay reproduces bytes"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n21-record", type=Path, help="record.json of the n21 plan whose placement S is bounded")
    parser.add_argument("--control", type=Path, action="append", default=[], help="collected control run directory")
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    parser.add_argument("--check", action="store_true", help="replay every retained output under results/live")
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        return 0
    if arguments.check:
        count = check(ROOT)
        print(f"state_prep_excess: {count} retained output{'s' if count != 1 else ''} replay byte for byte")
        return 0
    if arguments.n21_record is None or not arguments.control:
        parser.error("--n21-record and at least one --control are required")
    destination = write(arguments.n21_record, arguments.control, arguments.alpha, ROOT)
    result = json.loads(destination.read_bytes())
    print(f"{destination}: eps50 {result['eps50']:.6g}, eps250 {result['eps250']:.6g}, {result['fixed_point']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
