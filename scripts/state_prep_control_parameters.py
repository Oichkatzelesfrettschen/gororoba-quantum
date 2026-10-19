"""Every parameter the retained state-prep-control runs carry, classed by the evidence each value rests on.

A state-prep-control job runs one PUB whose members each hold one physical
qubit: prep0 runs (init, measure) and x_history runs (init, measure, x), with
the Sampler's implicit initialization (init_qubits) ahead of every shot and
the repetition delay (rep_delay) between shots. The raw archive live_run
--collect writes holds each member's one-bit register in shot order
(raw/<job>/pub_NN.json), the job's execution chunks and options
(result_metadata.json), the service's job metrics (job_metrics.json) and
the compiled schedule (metadata.compilation.scheduler_timing, rows
``block,<op>,<channel>,<start dt>,<duration dt>,<kind>``). The extraction
classes every value:

- exact: computed from the retained raw, collect, record and
  state-prep-readout bytes alone.
- sidecar: needs execution-properties.json, the read-only
  properties(datetime=PUB execution start) that --fetch-properties retains
  beside the run under the calibration stamp collect.json recorded.
- exploratory: rests on an assumption stated beside the value.

Sections. A: execution timing per job and the per-qubit INIT, operation and
FINI schedule. B: per-qubit excited fraction with its Clopper-Pearson
interval and the readout-corrected fraction (f - e10) / (1 - e01 - e10) at
the execution calibration. C: x_history minus prep0 per qubit, a difference
between separately executed jobs at one delay and execution calibration
(Newcombe hybrid score interval). D (exploratory): trend across 16
contiguous shot-array blocks. E: simultaneous excitation against the
Poisson-binomial law of the marginals and coupled-pair correlation. F
(exploratory): lag-1 shot memory. G: rank correlations with the sidecar's
calibration and the Boltzmann-equivalent population temperature
(exploratory). H (exploratory): the same qubits across delays.

inference_families declares every test family and its member count from run
structure alone; each p-value appears raw and Bonferroni-adjusted over its
own family, and no section thresholds an adjusted value.

Each run's extraction is independent and runs through parallel.ordered_map.
--out writes one JSON (sorted keys, floats at 12 significant digits) with
the sha256 of every consumed file; --check verifies those digests and
recomputes the JSON from them; --self-test exercises every section on
synthetic runs in the layouts live_run --collect, state_prep_excess
--fetch-readout and --fetch-properties write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
import tempfile
from collections.abc import Iterable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import beta, binomtest, chi2, norm, spearmanr
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402

SCHEMA = "state-prep-control-parameters-v1"
OUTPUT = Path("results/live/state-prep-control-parameters.json")
TARGETS = Path("docs/evidence/heron_platform/targets.json")
READOUT_NAME = "state-prep-readout.json"
READOUT_SCHEMA = "state-prep-readout-v1"
PROPERTIES_NAME = "execution-properties.json"
PROPERTIES_SCHEMA = "state-prep-execution-properties-v1"
RESULT_METADATA = "result_metadata.json"
# diagnostic_experiments.STATE_PREP_FAMILY and STATE_PREP_HISTORY_ARM; --self-test binds them.
FAMILY = "state-prep-control"
HISTORY_ARM = "x_history"
PREP0_ARM = "prep0"
BLOCKS = 16
CONFIDENCE = 0.95
FAMILY_ALPHA = 0.05
TAIL_COUNTS = (2, 3, 4, 5, 6)
# 2 sf(37) is about 1.1e-299; 2 sf(38) underflows a double to 0.
NEWCOMBE_Z_CAP = 37.0
TOP = 10
SIGNIFICANT_DIGITS = 12
# Floats compare within this relative tolerance on replay; scipy's special
# functions differ in their last bits between builds of one version.
REPLAY_REL_TOL = 1e-9
# Exact SI values (2019 redefinition).
PLANCK = 6.62607015e-34
BOLTZMANN = 1.380649e-23
PROPERTY_FIELDS = (
    "frequency_hz",
    "anharmonicity_hz",
    "T1_seconds",
    "T2_seconds",
    "readout_error",
    "prob_meas1_prep0",
    "prob_meas0_prep1",
    "readout_length_seconds",
)
SPEARMAN_FIELDS = ("frequency_hz", "T1_seconds", "T2_seconds", "readout_error", "prob_meas1_prep0")
ERROR_CODE = re.compile(r"Error code (\d+)")
CLASSES = {
    "exact": "computed from the retained raw, collect, record and state-prep-readout bytes",
    "sidecar": f"needs {PROPERTIES_NAME}, the read-only properties at the PUB execution start under the "
    "calibration stamp collect.json recorded",
    "exploratory": "rests on the assumption stated beside the value",
}
LAG_ASSUMPTION = (
    "AGENTS.md Execution order: adjacent entries of a shot array are not guaranteed to be adjacent physical "
    "executions, so a null here does not exclude memory and a nonzero value is evidence for both adjacency and "
    "memory; the two conditional fractions are compared as independent binomials"
)
DRIFT_ASSUMPTION = (
    "AGENTS.md Execution order: shot-array positions are not guaranteed to be physical execution order, and one "
    "executor chunk span timestamps no individual shot, so blocks are contiguous array positions and the slope is "
    "per block index; a trend is evidence for both order preservation and drift"
)
TEMPERATURE_ASSUMPTION = (
    "the composite FINI -> delay -> INIT -> measurement channel leaves a two-level Boltzmann population at the "
    "qubit frequency; the value is the temperature of that population, not a device temperature"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> Any:
    """JSON-ready copy: floats at SIGNIFICANT_DIGITS, non-finite floats as null, numpy scalars as Python."""
    if isinstance(value, bool | np.bool_):
        return bool(value)
    if isinstance(value, int | np.integer):
        return int(value)
    if isinstance(value, float | np.floating):
        number = float(value)
        return float(f"{number:.{SIGNIFICANT_DIGITS}g}") if math.isfinite(number) else None
    if isinstance(value, dict):
        return {str(key): canonical(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [canonical(item) for item in value]
    return value


def encode(payload: Any) -> bytes:
    return (json.dumps(canonical(payload), indent=1, sort_keys=True, allow_nan=False) + "\n").encode()


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{path} lies outside {root}") from error


def _instant(stamp: Any, where: str) -> datetime:
    require(isinstance(stamp, str), f"{where}: no timestamp")
    text = stamp[:-1] + "+00:00" if stamp.endswith("Z") else stamp
    moment = datetime.fromisoformat(text)
    require(moment.tzinfo is not None, f"{where}: timestamp {stamp} carries no UTC offset")
    return moment


def _seconds_between(start: Any, stop: Any, where: str) -> float:
    return (_instant(stop, where) - _instant(start, where)).total_seconds()


def _member_qubit(member: str) -> tuple[str, int]:
    require(member.startswith("spc_") and "_q" in member, f"{member}: not a state-prep member")
    arm, qubit_text = member.removeprefix("spc_").rsplit("_q", 1)
    return arm, int(qubit_text)


def _delay_label(delay: float) -> str:
    return f"{round(delay * 1e6):d}us"


class Reader:
    """Reads files under root and records each one's checkout-relative path and sha256."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.inputs: dict[str, str] = {}

    def read(self, path: Path, expected: str | None = None) -> bytes:
        require(path.is_file(), f"{path}: raw file missing")
        data = path.read_bytes()
        digest = sha256_bytes(data)
        if expected is not None:
            require(digest == expected, f"{path}: sha256 differs from the digest its index records")
        self.inputs[_relative(path, self.root)] = digest
        return data

    def json(self, path: Path, expected: str | None = None) -> Any:
        return json.loads(self.read(path, expected))


# Interval estimators.


def clopper_pearson(ones: np.ndarray, shots: np.ndarray, confidence: float = CONFIDENCE) -> tuple[Any, Any]:
    """Two-sided Clopper-Pearson interval: equal tails of (1 - confidence) / 2; 0 at k = 0 and 1 at k = n."""
    k = np.asarray(ones, dtype=float)
    n = np.asarray(shots, dtype=float)
    tail = (1.0 - confidence) / 2.0
    lower = np.zeros(k.shape)
    upper = np.ones(k.shape)
    inside = k > 0
    lower[inside] = beta.ppf(tail, k[inside], n[inside] - k[inside] + 1.0)
    inside = k < n
    upper[inside] = beta.ppf(1.0 - tail, k[inside] + 1.0, n[inside] - k[inside])
    return lower, upper


def wilson(ones: np.ndarray, shots: np.ndarray, z: float) -> tuple[np.ndarray, np.ndarray]:
    k = np.asarray(ones, dtype=float)
    n = np.asarray(shots, dtype=float)
    p = k / n
    denominator = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denominator
    half = z * np.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denominator
    return center - half, center + half


def newcombe(
    ones_a: np.ndarray, shots_a: np.ndarray, ones_b: np.ndarray, shots_b: np.ndarray, z: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """p_a - p_b with Newcombe's hybrid score interval (1998, method 10) from the two Wilson intervals."""
    p_a = np.asarray(ones_a, dtype=float) / np.asarray(shots_a, dtype=float)
    p_b = np.asarray(ones_b, dtype=float) / np.asarray(shots_b, dtype=float)
    low_a, high_a = wilson(ones_a, shots_a, z)
    low_b, high_b = wilson(ones_b, shots_b, z)
    difference = p_a - p_b
    lower = difference - np.sqrt((p_a - low_a) ** 2 + (high_b - p_b) ** 2)
    upper = difference + np.sqrt((high_a - p_a) ** 2 + (p_b - low_b) ** 2)
    return difference, lower, upper


def two_sided_z(alpha: float) -> float:
    return float(norm.isf(alpha / 2.0))


def newcombe_p(ones_a: np.ndarray, shots_a: np.ndarray, ones_b: np.ndarray, shots_b: np.ndarray) -> np.ndarray:
    """Two-sided p-value that inverts the Newcombe interval: 2 sf(z*) at the z* whose interval touches zero.

    The interval widens monotonically in z, so bisection over z in
    [0, NEWCOMBE_Z_CAP] finds z*; a difference of exactly zero reads p = 1,
    and an interval that still excludes zero at the cap reads the floor
    2 sf(NEWCOMBE_Z_CAP), about 1.1e-299, the smallest p a double resolves
    there.
    """
    difference, _, _ = newcombe(ones_a, shots_a, ones_b, shots_b, 1.0)
    difference = np.atleast_1d(difference)
    low = np.zeros(difference.shape)
    high = np.full(difference.shape, NEWCOMBE_Z_CAP)
    for _ in range(80):
        middle = (low + high) / 2.0
        _, lower, upper = newcombe(ones_a, shots_a, ones_b, shots_b, middle)
        excludes = np.where(difference > 0.0, np.atleast_1d(lower) > 0.0, np.atleast_1d(upper) < 0.0)
        low = np.where(excludes, middle, low)
        high = np.where(excludes, high, middle)
    p = 2.0 * norm.sf((low + high) / 2.0)
    return np.where(difference == 0.0, 1.0, p)


def bonferroni(p: Any, members: int) -> Any:
    """Bonferroni-adjusted p-values, min(1, m p), over a declared family of m members."""
    return np.minimum(1.0, np.asarray(p, dtype=float) * members)


def family(name: str, members: int, correction: str, scope: str) -> dict[str, Any]:
    return {"name": name, "members": members, "correction": correction, "scope": scope}


def poisson_binomial(probabilities: Sequence[float]) -> np.ndarray:
    """The law of a sum of independent Bernoulli(p_i), by exact convolution in input order."""
    pmf = np.ones(1)
    for p in probabilities:
        step = np.zeros(pmf.size + 1)
        step[:-1] += pmf * (1.0 - p)
        step[1:] += pmf * p
        pmf = step
    return pmf


def _median(values: Sequence[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _quartiles(values: Sequence[float]) -> list[float] | None:
    if len(values) < 2:
        return None
    ordered = np.sort(np.asarray(values, dtype=float))
    return [float(np.percentile(ordered, 25.0)), float(np.percentile(ordered, 75.0))]


# Scheduler table.


def _op_type(op: str) -> str:
    return re.sub(r"(_\d+)+$", "", op)


def schedule(timing: str, qubits: Iterable[int]) -> dict[str, Any]:
    """Per-qubit INIT, operation and FINI spans in dt, and the distinct INIT and FINI pulse patterns.

    Rows on channel ``Qubit q`` belong to q; capture rows on readout
    channels belong to q by a single-qubit op name such as INIT_q or
    measure_q. An operation span reads [start, duration, row count]. A pattern
    lists each row of the op as [kind, offset from the op start, duration].
    """
    rows = []
    for line in timing.splitlines():
        parts = line.split(",")
        require(len(parts) == 6, f"scheduler timing row {line!r} holds {len(parts)} fields")
        rows.append((parts[0], parts[1], parts[2], int(parts[3]), int(parts[4]), parts[5]))
    by_op: dict[str, list[tuple[str, str, str, int, int, str]]] = {}
    for row in rows:
        by_op.setdefault(row[1], []).append(row)
    per_qubit: dict[str, Any] = {}
    patterns: dict[str, dict[tuple[Any, ...], list[int]]] = {"INIT": {}, "FINI": {}}
    for qubit in sorted(qubits):
        entry: dict[str, Any] = {}
        for role in ("INIT", "FINI"):
            members = by_op.get(f"{role}_{qubit}", [])
            require(bool(members), f"scheduler timing holds no {role}_{qubit}")
            start = min(row[3] for row in members)
            stop = max(row[3] + row[4] for row in members)
            entry[role] = [start, stop - start]
            pattern = tuple(
                sorted((row[5], row[3] - start, row[4]) for row in members if row[5] in ("play", "capture"))
            )
            patterns[role].setdefault(pattern, []).append(qubit)
        operations: dict[str, list[int]] = {}
        single = re.compile(rf"[a-z0-9]+_{qubit}")
        for row in rows:
            owned = row[2] == f"Qubit {qubit}" or (row[5] == "capture" and single.fullmatch(row[1]) is not None)
            if not owned or row[1] == "barrier" or row[1].split("_")[0] in ("INIT", "FINI"):
                continue
            kind = _op_type(row[1])
            start, stop = row[3], row[3] + row[4]
            if kind in operations:
                span = operations[kind]
                first, last = span[0], span[0] + span[1]
                operations[kind] = [min(first, start), max(last, stop) - min(first, start), span[2] + 1]
            else:
                operations[kind] = [start, stop - start, 1]
        entry["operations"] = operations
        per_qubit[str(qubit)] = entry
    summary = {}
    for role, found in patterns.items():
        distinct = [
            {
                "rows": [list(row) for row in pattern],
                "plays_dt": [row[2] for row in pattern if row[0] == "play"],
                "captures_dt": [row[2] for row in pattern if row[0] == "capture"],
                "span_dt": max((row[1] + row[2] for row in pattern), default=0),
                "qubit_count": len(members),
            }
            for pattern, members in sorted(found.items(), key=lambda item: (-len(item[1]), item[0]))
        ]
        summary[role] = {"distinct_patterns": distinct, "uniform": len(distinct) == 1}
    return {"qubits": per_qubit, "patterns": summary}


# Per-run extraction.


def _executions(collect: list[Any], where: str) -> dict[str, dict[str, Any]]:
    executed: dict[str, dict[str, Any]] = {}
    for entry in collect[1:]:
        for member, execution in (entry.get("executed") or {}).items():
            require(executed.setdefault(member, execution) == execution, f"{where}: {member} executed twice")
    return executed


def _planner(record: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    """The selected candidate's cost model for this job, matched by backend and PUB names."""
    optimization = record.get("optimization") or {}
    candidates = optimization.get("candidates") or []
    selected = optimization.get("selected")
    require(selected is not None, "the record names no selected optimization candidate")
    selected_candidates = [cand for cand in candidates if cand.get("name") == selected]
    require(
        len(selected_candidates) == 1,
        f"the record holds {len(selected_candidates)} candidates named {selected!r}; expected exactly one",
    )
    candidate = selected_candidates[0]
    names = [str(pub["name"]) for pub in job["pubs"]]
    matched = [
        planned
        for planned in candidate.get("jobs") or []
        if [str(pub["name"]) for pub in planned["pubs"]] == names
        and str(planned["name"]).startswith(f"{job['backend']}/")
    ]
    require(len(matched) == 1, f"job {job.get('job_id')}: {len(matched)} planner jobs carry PUBs {names}")
    planned = matched[0]
    contract = [
        cost
        for cost in (record.get("execution_contract") or {}).get("selected_job_costs") or []
        if cost.get("name") == planned["name"]
    ]
    shots = sum(int(pub["shots"]) for pub in planned["pubs"])
    execution = math.fsum(float(pub["estimated_execution_seconds"]) for pub in planned["pubs"])
    return {
        "candidate": candidate["name"],
        "candidate_is_selected": candidate["name"] == optimization.get("selected"),
        "execution_contract_agrees": len(contract) == 1 and contract[0] == planned,
        "pubs": [
            {
                key: pub[key]
                for key in (
                    "name",
                    "shots",
                    "scheduled_seconds",
                    "repetition_delay_seconds",
                    "classical_latency_seconds",
                    "estimated_execution_seconds",
                )
            }
            for pub in planned["pubs"]
        ],
        "overhead_seconds": planned["overhead_seconds"],
        "estimated_charge_seconds": planned["estimated_charge_seconds"],
        "max_execution_seconds": planned.get("max_execution_seconds"),
        "estimated_execution_seconds": execution,
        "per_shot_seconds": execution / shots,
    }


def _completed_job(
    reader: Reader,
    run_dir: Path,
    record: dict[str, Any],
    job: dict[str, Any],
    collected: dict[str, Any],
    dt: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Timing block of one completed job and its parsed PUB payloads."""
    job_id = str(job["job_id"])
    raw = run_dir / "raw" / job_id
    index = reader.json(raw / "index.json")
    require(index.get("job_id") == job_id, f"{raw}: index.json names another job")
    files = index.get("files") or {}
    ledger = collected.get("raw")
    if ledger is not None:
        require(
            ledger.get("directory") == f"raw/{job_id}" and ledger.get("files") == files,
            f"{raw}: index.json differs from the raw ledger collect.json records",
        )
    pubs = []
    for position, manifest in enumerate(job["pubs"]):
        name = f"pub_{position:02d}.json"
        require(name in files, f"{raw}: index.json lacks {name}")
        payload = reader.json(raw / name, files[name])
        require(
            payload.get("pub_index") == position and payload.get("pub_name") == manifest["name"],
            f"{raw / name}: holds another PUB than {manifest['name']}",
        )
        pubs.append(payload)
    require(RESULT_METADATA in files, f"{raw}: index.json lacks {RESULT_METADATA}")
    metadata = reader.json(raw / RESULT_METADATA, files[RESULT_METADATA])
    metrics_names = list(index.get("metrics") or [])
    latest = index.get("metrics_latest")
    require(latest in metrics_names, f"{raw}: index.json names no latest job metrics")
    metrics = reader.json(raw / str(latest), index["metrics_sha256"][metrics_names.index(latest)])
    options = metadata["options"]
    execution = options["execution"]
    delay = float(execution["rep_delay"])
    submitted = (job.get("options") or {}).get("execution") or {}
    require(math.isclose(float(submitted["rep_delay"]), delay, rel_tol=1e-12, abs_tol=0.0), f"{job_id}: delays")
    policy_delay = (record.get("policy") or {}).get("rep_delay_seconds")
    if policy_delay is not None:
        require(math.isclose(float(policy_delay), delay, rel_tol=1e-12, abs_tol=0.0), f"{job_id}: policy delay")
    default_shots = int(options["default_shots"])
    pub_rows = []
    for payload in pubs:
        counts = {int(register["num_shots"]) for register in payload["registers"].values()}
        require(counts == {default_shots}, f"{job_id} {payload['pub_name']}: shots {sorted(counts)} != {default_shots}")
        for name, register in payload["registers"].items():
            require(
                len(register["bitstrings"]) == default_shots,
                f"{job_id} {payload['pub_name']} {name}: {len(register['bitstrings'])} outcomes for "
                f"{default_shots} shots",
            )
        timing = payload["metadata"]["compilation"]["scheduler_timing"]
        duration = int(timing["circuit_duration"])
        qubits = sorted({int(op.split("_", 1)[1]) for op in re.findall(r"INIT_\d+", timing["timing"])})
        pub_rows.append(
            {
                "name": payload["pub_name"],
                "shots": default_shots,
                "circuit_duration_dt": duration,
                "circuit_duration_seconds": duration * dt,
                "shot_period_seconds": delay + duration * dt,
                "schedule": schedule(timing["timing"], qubits),
            }
        )
    chunks = (metadata.get("executor") or {}).get("chunk_timing") or []
    require(bool(chunks), f"{raw / RESULT_METADATA}: no executor chunk_timing")
    chunk_rows = [
        {
            "start": chunk["start"],
            "stop": chunk["stop"],
            "span_seconds": _seconds_between(chunk["start"], chunk["stop"], job_id),
            "pubs": sorted({int(part["idx_item"]) for part in chunk["parts"]}),
        }
        for chunk in chunks
    ]
    stamps = metrics["timestamps"]
    usage = metrics["usage"]
    circuit_seconds = int(metrics["circuits_execution_time_ns"]) * 1e-9
    total_shots = default_shots * len(pubs)
    measured = circuit_seconds / total_shots
    predicted = math.fsum(row["shots"] * row["shot_period_seconds"] for row in pub_rows) / total_shots
    planner = _planner(record, job)
    final = usage.get("status") == "complete"
    twirling = options.get("twirling") or {}
    identity = (record.get("backends") or {}).get(str(job["backend"])) or {}
    timing_block = {
        "class": "exact",
        "job_id": job_id,
        "outcome": collected["usage"]["job_status"],
        "backend": job["backend"],
        "backend_version": identity.get("backend_version"),
        "processor_type": identity.get("processor_type"),
        "created": stamps["created"],
        "running": stamps["running"],
        "finished": stamps["finished"],
        "queue_seconds": _seconds_between(stamps["created"], stamps["running"], job_id),
        "running_seconds": _seconds_between(stamps["running"], stamps["finished"], job_id),
        "chunks": chunk_rows,
        "chunk_count": len(chunk_rows),
        "shots": default_shots,
        "pub_count": len(pubs),
        "rep_delay_seconds": delay,
        "init_qubits": execution.get("init_qubits"),
        "meas_type": execution.get("meas_type"),
        "max_execution_time": options.get("max_execution_time"),
        "twirling": {"enable_gates": twirling.get("enable_gates"), "enable_measure": twirling.get("enable_measure")},
        "dynamical_decoupling": (options.get("dynamical_decoupling") or {}).get("enable"),
        "pubs": pub_rows,
        "circuits_execution_time_seconds": circuit_seconds,
        "measured_per_shot_seconds": measured,
        "predicted_per_shot_seconds": predicted,
        "per_shot_residual_seconds": measured - predicted,
        "lock_overhead_seconds": math.fsum(row["span_seconds"] for row in chunk_rows) - circuit_seconds,
        "billed_seconds": usage.get("qpu_charge_time_seconds") if final else None,
        "billed_resource_units": usage.get("value") if final else None,
        "usage_status": usage.get("status"),
        "provisional_usage": None
        if final
        else {"qpu_charge_time_seconds": usage.get("qpu_charge_time_seconds"), "resource_units": usage.get("value")},
        "planner": planner,
        "planner_per_shot_undercount_seconds": measured - planner["per_shot_seconds"],
    }
    return timing_block, pubs


def _failed_job(record: dict[str, Any], job: dict[str, Any], collected: dict[str, Any]) -> dict[str, Any]:
    usage = collected.get("usage") or {}
    text = collected.get("result_unavailable")
    code = ERROR_CODE.search(text) if isinstance(text, str) else None
    options = job.get("options") or {}
    raw_usage = usage.get("raw_usage_metadata") or {}
    return {
        "class": "exact",
        "job_id": str(job["job_id"]),
        "backend": job["backend"],
        "kind": collected.get("kind"),
        "outcome": usage.get("job_status"),
        "usage_status": usage.get("usage_status"),
        "submitted_pub_shots": usage.get("submitted_pub_shots"),
        "rep_delay_seconds": (options.get("execution") or {}).get("rep_delay"),
        "max_execution_time": options.get("max_execution_time"),
        "billed_seconds": None,
        "provisional_usage": {
            "scope": "collect.json's raw_usage_metadata at collection, provisional until the service finalizes it",
            "qpu_charge_time_seconds": raw_usage.get("qpu_charge_time_seconds"),
            "resource_units": raw_usage.get("value"),
            "usage_status": raw_usage.get("status"),
        },
        "result_unavailable": text,
        "error_class": text.split(":", 1)[0] if isinstance(text, str) else None,
        "error_code": int(code.group(1)) if code else None,
        "planner": _planner(record, job),
    }


def _bits(payload: dict[str, Any], manifest: dict[str, Any], arm: str) -> tuple[list[int], np.ndarray]:
    """Member qubits in ascending order and their shot-ordered bits, one row per qubit."""
    rows: dict[int, np.ndarray] = {}
    for component in manifest["components"]:
        member = str(component["member"])
        member_arm, qubit = _member_qubit(member)
        require(member_arm == arm, f"{member}: arm {member_arm} in a {arm} run")
        require(component["physical_qubits"] == [qubit], f"{member}: placed on {component['physical_qubits']}")
        registers = component["registers_by_replica"]
        require(len(registers) == 1 and len(registers[0]) == 1, f"{member}: expects one register")
        register = payload["registers"][registers[0][0]]
        require(int(register["num_bits"]) == 1, f"{member}: register holds {register['num_bits']} bits")
        text = "".join(register["bitstrings"])
        require(len(text) == int(register["num_shots"]), f"{member}: outcomes and shots differ")
        values = np.frombuffer(text.encode(), dtype=np.uint8) - ord("0")
        require(bool(np.all(values <= 1)), f"{member}: outcome other than 0 or 1")
        require(qubit not in rows, f"{member}: qubit read twice")
        rows[qubit] = values
    qubits = sorted(rows)
    return qubits, np.stack([rows[q] for q in qubits])


def _excitation(qubits: list[int], ones: np.ndarray, shots: int, readout: dict[str, Any]) -> dict[str, Any]:
    lower, upper = clopper_pearson(ones, np.full(ones.shape, shots))
    per_qubit = {}
    corrected_values = []
    fractions = []
    excess = []
    for index, qubit in enumerate(qubits):
        values = readout[str(qubit)]
        e10, e01 = float(values["prob_meas1_prep0"]), float(values["prob_meas0_prep1"])
        fraction = int(ones[index]) / shots
        corrected = (fraction - e10) / (1.0 - e01 - e10)
        excess.append(fraction - e10)
        per_qubit[str(qubit)] = {
            "excited": int(ones[index]),
            "shots": shots,
            "fraction": fraction,
            "clopper_pearson_95": [float(lower[index]), float(upper[index])],
            "prob_meas1_prep0": e10,
            "prob_meas0_prep1": e01,
            "readout_corrected": corrected,
            "readout_corrected_clamped": min(1.0, max(0.0, corrected)),
            "fraction_minus_prob_meas1_prep0": fraction - e10,
        }
        corrected_values.append(corrected)
        fractions.append(fraction)
    return {
        "class": "exact",
        "qubits": per_qubit,
        "summary": {
            "qubit_count": len(qubits),
            "median_fraction": _median(fractions),
            "mean_fraction": math.fsum(fractions) / len(fractions),
            "median_readout_corrected": _median(corrected_values),
            "median_fraction_minus_prob_meas1_prep0": _median(excess),
            "quartiles_fraction": _quartiles(fractions),
            "quartiles_readout_corrected": _quartiles(corrected_values),
            "negative_readout_corrected": sum(1 for value in corrected_values if value < 0.0),
        },
    }


def _ols(x: Sequence[float], y: Sequence[float]) -> dict[str, Any]:
    """Least-squares slope with its standard error, by compensated sums."""
    count = len(x)
    x_mean = math.fsum(x) / count
    y_mean = math.fsum(y) / count
    sxx = math.fsum((a - x_mean) ** 2 for a in x)
    sxy = math.fsum((a - x_mean) * (b - y_mean) for a, b in zip(x, y, strict=True))
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    residual = math.fsum((b - intercept - slope * a) ** 2 for a, b in zip(x, y, strict=True)) / (count - 2)
    error = math.sqrt(residual / sxx)
    statistic = slope / error if error > 0.0 else None
    return {
        "slope_per_block": slope,
        "slope_standard_error": error,
        "t_statistic": statistic,
        "two_sided_p": None if statistic is None else float(2.0 * student_t.sf(abs(statistic), count - 2)),
        "mean_fraction": y_mean,
        "relative_change_over_blocks": slope * (max(x) - min(x)) / y_mean if y_mean > 0.0 else None,
    }


def _drift(qubits: list[int], bits: np.ndarray) -> dict[str, Any]:
    shots = bits.shape[1]
    sizes = [len(part) for part in np.array_split(np.arange(shots), BLOCKS)]
    starts = np.cumsum([0, *sizes[:-1]])
    counts = np.add.reduceat(bits.astype(np.int64), starts, axis=1)
    size_array = np.asarray(sizes, dtype=float)
    block_fraction = [
        float(total) / (len(qubits) * size) for total, size in zip(counts.sum(axis=0), sizes, strict=True)
    ]
    ones = counts.sum(axis=1)
    p = ones / shots
    alive = (ones > 0) & (ones < shots)
    statistic = np.zeros(len(qubits))
    expected = size_array[None, :] * p[alive, None]
    statistic[alive] = (((counts[alive] - expected) ** 2) / (expected * (1.0 - p[alive, None]))).sum(axis=1)
    p_values = np.ones(len(qubits))
    p_values[alive] = chi2.sf(statistic[alive], BLOCKS - 1)
    # Family D_chi_square/<run>: one homogeneity test per member qubit.
    adjusted = bonferroni(p_values, len(qubits))
    ranked = sorted(range(len(qubits)), key=lambda i: (float(adjusted[i]), qubits[i]))
    return {
        "class": "exploratory",
        "assumption": DRIFT_ASSUMPTION,
        "blocks": BLOCKS,
        "block_shots": sizes,
        "block_fraction": block_fraction,
        "chi_square_df": BLOCKS - 1,
        "chi_square": {
            str(q): {"statistic": float(statistic[i]), "p": float(p_values[i]), "bonferroni_p": float(adjusted[i])}
            for i, q in enumerate(qubits)
        },
        "degenerate_qubits": [qubits[i] for i in range(len(qubits)) if not alive[i]],
        "smallest_bonferroni_p": [{"qubit": qubits[i], "bonferroni_p": float(adjusted[i])} for i in ranked[:TOP]],
        "slope": _ols([float(index) for index in range(BLOCKS)], block_fraction),
    }


def _correlation(qubits: list[int], bits: np.ndarray, couplings: list[list[int]]) -> dict[str, Any]:
    shots = bits.shape[1]
    totals = bits.sum(axis=0, dtype=np.int64)
    ones = bits.sum(axis=1, dtype=np.int64)
    p = [int(k) / shots for k in ones]
    pmf = poisson_binomial(p)
    histogram = np.bincount(totals, minlength=1)
    sum_k = int(totals.sum())
    sum_k2 = int((totals * totals).sum())
    observed_variance = (sum_k2 - sum_k * sum_k / shots) / shots
    independent_variance = math.fsum(value * (1.0 - value) for value in p)
    tails = {}
    for k in TAIL_COUNTS:
        observed = int(histogram[k:].sum()) / shots
        expected = math.fsum(float(v) for v in pmf[k:])
        tails[str(k)] = {
            "observed": observed,
            "expected": expected,
            "ratio": observed / expected if expected > 0.0 else None,
        }
    order = np.lexsort((np.arange(shots), -totals))[:TOP]
    events = [
        {
            "shot": int(s),
            "excited": int(totals[s]),
            "qubits": [qubits[i] for i in np.flatnonzero(bits[:, s])],
        }
        for s in order
    ]
    position = {q: i for i, q in enumerate(qubits)}
    pairs = sorted({(min(a, b), max(a, b)) for a, b in couplings if a in position and b in position and a != b})
    rows = []
    skipped = 0
    for a, b in pairs:
        pa, pb = p[position[a]], p[position[b]]
        if not (0.0 < pa < 1.0 and 0.0 < pb < 1.0):
            skipped += 1
            continue
        both = int(np.count_nonzero(bits[position[a]] & bits[position[b]]))
        covariance = both / shots - pa * pb
        phi = covariance / math.sqrt(pa * (1.0 - pa) * pb * (1.0 - pb))
        z = phi * math.sqrt(shots)
        rows.append({"pair": [a, b], "both": both, "covariance": covariance, "phi": phi, "z": z})
    # Family E_pairs/<run>: one independence test per coupled pair whose marginals both vary.
    p_values = 2.0 * norm.sf(np.abs(np.asarray([row["z"] for row in rows], dtype=float)))
    for row, p_value, adjusted in zip(rows, p_values, bonferroni(p_values, len(rows)), strict=True):
        row["p"] = float(p_value)
        row["bonferroni_p"] = float(adjusted)
    ranked = sorted(rows, key=lambda row: (-abs(row["z"]), row["pair"]))
    return {
        "class": "exact",
        "shots": shots,
        "histogram_observed": [int(v) for v in histogram],
        "histogram_expected": [float(v) * shots for v in pmf[: len(histogram)]],
        "expected_mass_beyond_histogram": math.fsum(float(v) for v in pmf[len(histogram) :]),
        "observed_variance": observed_variance,
        "independent_variance": independent_variance,
        "variance_ratio": observed_variance / independent_variance if independent_variance > 0.0 else None,
        "tail_at_least": tails,
        "top_events": events,
        "coupled_pairs": {
            "count": len(rows),
            "skipped_constant": skipped,
            "mean_phi": math.fsum(row["phi"] for row in rows) / len(rows) if rows else None,
            "median_phi": _median([row["phi"] for row in rows]),
            "positive_phi": sum(1 for row in rows if row["phi"] > 0.0),
            "top": ranked[:TOP],
        },
    }


def _lag(qubits: list[int], bits: np.ndarray) -> dict[str, Any]:
    previous = bits[:, :-1].astype(np.int64)
    current = bits[:, 1:].astype(np.int64)
    after_one = previous.sum(axis=1)
    after_zero = previous.shape[1] - after_one
    one_one = (previous & current).sum(axis=1)
    zero_one = current.sum(axis=1) - one_one
    defined = after_one > 0
    z95 = two_sided_z(1.0 - CONFIDENCE)
    usable = [i for i in range(len(qubits)) if defined[i]]
    # Family F_lag1/<run>: one test per qubit with at least one shot after an excited shot.
    a, n_a, b, n_b = (np.asarray([column[i] for i in usable]) for column in (one_one, after_one, zero_one, after_zero))
    if usable:
        difference_all, lower_all, upper_all = newcombe(a, n_a, b, n_b, z95)
        p_all = newcombe_p(a, n_a, b, n_b)
    else:
        difference_all = lower_all = upper_all = p_all = np.zeros(0)
    adjusted_all = bonferroni(p_all, len(usable))
    per_qubit: dict[str, Any] = {}
    differences = []
    for qubit in qubits:
        per_qubit[str(qubit)] = {"undefined": "no shot follows an excited shot"}
    for position, index in enumerate(usable):
        difference = float(difference_all[position])
        differences.append(difference)
        per_qubit[str(qubits[index])] = {
            "after_excited": [int(one_one[index]), int(after_one[index])],
            "after_ground": [int(zero_one[index]), int(after_zero[index])],
            "difference": difference,
            "newcombe_95": [float(lower_all[position]), float(upper_all[position])],
            "p": float(p_all[position]),
            "bonferroni_p": float(adjusted_all[position]),
        }
    ranked = sorted(range(len(usable)), key=lambda i: (float(adjusted_all[i]), qubits[usable[i]]))
    pooled_one = int(one_one.sum()) / int(after_one.sum()) if int(after_one.sum()) else None
    pooled_zero = int(zero_one.sum()) / int(after_zero.sum())
    return {
        "class": "exploratory",
        "assumption": LAG_ASSUMPTION,
        "qubits": per_qubit,
        "defined_qubits": len(differences),
        "median_difference": _median(differences),
        "pooled_difference": None if pooled_one is None else pooled_one - pooled_zero,
        "positive_differences": sum(1 for value in differences if value > 0.0),
        "smallest_bonferroni_p": [
            {"qubit": qubits[usable[i]], "bonferroni_p": float(adjusted_all[i])} for i in ranked[:TOP]
        ],
    }


def _window(manifest: dict[str, Any], executed: dict[str, dict[str, Any]], where: str) -> dict[str, Any]:
    windows = set()
    for component in manifest["components"]:
        execution = executed.get(str(component["member"]))
        if execution is None:
            raise ValueError(f"{where}: collect.json records no execution of {component['member']}")
        require(execution.get("pub") == manifest["name"], f"{where}: {component['member']} ran in another PUB")
        require(execution.get("start") is not None, f"{where}: no execution window for {component['member']}")
        windows.add(
            (
                execution["start"],
                execution["stop"],
                execution["calibration"],
                bool(execution.get("calibration_changed_during_shots")),
            )
        )
    require(len(windows) == 1, f"{where}: members record different execution windows")
    start, stop, calibration, changed = windows.pop()
    return {"start": start, "stop": stop, "calibration": calibration, "changed": changed}


def _sidecar(
    reader: Reader,
    path: Path,
    schema: str,
    record_bytes: bytes,
    collect_bytes: bytes,
    job_id: str,
    window: dict[str, Any],
    pub: str,
) -> dict[str, Any]:
    """The per-qubit values a sidecar fetched at the PUB's execution start under collect's calibration."""
    payload = reader.json(path)
    require(payload.get("schema") == schema, f"{path}: schema {payload.get('schema')}")
    require(
        payload.get("record_sha256") == sha256_bytes(record_bytes)
        and payload.get("collect_sha256") == sha256_bytes(collect_bytes),
        f"{path}: fetched for other record or collect bytes",
    )
    found = [
        entry
        for entry in payload["windows"]
        if str(entry["job_id"]) == job_id and str(entry["pub"]) == pub and entry["edge"] == "start"
    ]
    require(len(found) == 1, f"{path}: no single start window for {job_id} {pub}")
    entry = found[0]
    require(entry.get("at") == window["start"], f"{path}: {pub} fetched at another instant")
    require(
        _instant(entry.get("calibration"), str(path)) == _instant(window["calibration"], str(path)),
        f"{path}: calibration {entry.get('calibration')} differs from collect's {window['calibration']}",
    )
    return {"calibration": entry["calibration"], "qubits": entry["qubits"]}


def _properties_block(
    arm: str, qubits: list[int], excitation: dict[str, Any], properties: dict[str, Any]
) -> dict[str, Any]:
    rows = properties["qubits"]
    missing = {field: [q for q in qubits if (rows.get(str(q)) or {}).get(field) is None] for field in PROPERTY_FIELDS}
    block: dict[str, Any] = {
        "class": "sidecar",
        "available": True,
        "calibration": properties["calibration"],
        "missing": {field: absent for field, absent in missing.items() if absent},
        "readout_agrees_with_state_prep_readout": sum(
            1
            for q in qubits
            if rows[str(q)].get("prob_meas1_prep0") == excitation["qubits"][str(q)]["prob_meas1_prep0"]
            and rows[str(q)].get("prob_meas0_prep1") == excitation["qubits"][str(q)]["prob_meas0_prep1"]
        ),
        "qubits": {str(q): {field: rows[str(q)].get(field) for field in PROPERTY_FIELDS} for q in qubits},
    }
    fraction = {q: excitation["qubits"][str(q)]["fraction"] for q in qubits}
    correlations: dict[str, dict[str, Any]] = {}
    for field in SPEARMAN_FIELDS:
        usable = [q for q in qubits if rows[str(q)].get(field) is not None]
        x = [fraction[q] for q in usable]
        y = [float(rows[str(q)][field]) for q in usable]
        if len(usable) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
            correlations[field] = {"n": len(usable), "rho": None, "p": None}
            continue
        result = spearmanr(x, y)
        correlations[field] = {"n": len(usable), "rho": float(result.statistic), "p": float(result.pvalue)}
    # Family G_spearman/<run>: one rank correlation per calibration field.
    for entry in correlations.values():
        entry["bonferroni_p"] = None if entry["p"] is None else float(bonferroni(entry["p"], len(SPEARMAN_FIELDS)))
    block["spearman_fraction"] = {"arm": arm, "fields": correlations}
    if arm == PREP0_ARM:
        temperatures = {}
        excluded: dict[str, list[int]] = {"corrected_not_in_open_0_0.5": [], "no_frequency": []}
        for q in qubits:
            corrected = excitation["qubits"][str(q)]["readout_corrected"]
            frequency = rows[str(q)].get("frequency_hz")
            if frequency is None:
                excluded["no_frequency"].append(q)
            elif not 0.0 < corrected < 0.5:
                excluded["corrected_not_in_open_0_0.5"].append(q)
            else:
                temperatures[q] = PLANCK * float(frequency) / (BOLTZMANN * math.log((1.0 - corrected) / corrected))
        values = [temperatures[q] for q in sorted(temperatures)]
        block["population_temperature"] = {
            "class": "exploratory",
            "quantity": "Boltzmann-equivalent population temperature",
            "assumption": TEMPERATURE_ASSUMPTION,
            "formula": "T = h f / (k_B ln((1 - p) / p)), p the unclamped readout-corrected prep0 fraction",
            "kelvin": {str(q): temperatures[q] for q in sorted(temperatures)},
            "count": len(values),
            "excluded": excluded,
            "excluded_count": sum(len(v) for v in excluded.values()),
            "median_kelvin": _median(values),
            "interquartile_kelvin": _quartiles(values),
        }
        if len(excluded["no_frequency"]) == len(qubits):
            block["population_temperature"]["unavailable"] = (
                "the properties carry no qubit frequency for any member; docs/evidence/heron_platform/"
                "backend_configuration.json counts zero non-null Target qubit frequencies on this backend"
            )
    return block


def _run_families(name: str, qubits: list[int], bits: np.ndarray, couplings: list[list[int]]) -> list[dict[str, Any]]:
    """The test families of one control run, sized from its members and marginals before any test runs."""
    shots = bits.shape[1]
    ones = bits.sum(axis=1, dtype=np.int64)
    varying = {q for q, k in zip(qubits, ones, strict=True) if 0 < int(k) < shots}
    present = set(qubits)
    pairs = {(min(a, b), max(a, b)) for a, b in couplings if a in present and b in present and a != b}
    lag_defined = int(np.count_nonzero(bits[:, :-1].sum(axis=1, dtype=np.int64) > 0))
    bonf = "Bonferroni: adjusted p = min(1, members x p)"
    return [
        family(f"D_chi_square/{name}", len(qubits), bonf, "block homogeneity of each member qubit's excitation"),
        family(
            f"E_pairs/{name}",
            sum(1 for a, b in pairs if a in varying and b in varying),
            bonf,
            "independence of each coupled member pair whose marginals both vary",
        ),
        family(f"F_lag1/{name}", lag_defined, bonf, "lag-1 conditional difference of each qubit with an excited shot"),
        family(f"G_spearman/{name}", len(SPEARMAN_FIELDS), bonf, "rank correlation of the fraction with each field"),
    ]


class RunExtractor:
    """One run directory's sections A, B, D, E, F and G; picklable for parallel.ordered_map."""

    def __init__(self, root: str, dt: dict[str, float], couplings: dict[str, list[list[int]]]) -> None:
        self.root = root
        self.dt = dt
        self.couplings = couplings

    def __call__(self, run: str) -> dict[str, Any]:
        root = Path(self.root)
        run_dir = root / run
        reader = Reader(root)
        record_bytes = reader.read(run_dir / "record.json")
        record = json.loads(record_bytes)
        collect_bytes = reader.read(run_dir / "collect.json")
        collect = json.loads(collect_bytes)
        require(isinstance(collect, list) and bool(collect), f"{run_dir}/collect.json: not a collection")
        collected_jobs = collect[0].get("jobs") or {}
        jobs = (record.get("submission") or {}).get("jobs") or []
        require(bool(jobs), f"{run_dir}: the record holds no submitted job")
        family = (record.get("family_configuration") or {}).get("name")
        result: dict[str, Any] = {"path": run, "family": family, "timing": [], "failed": []}
        completed: list[tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]] = []
        for job in jobs:
            job_id = str(job["job_id"])
            collected = collected_jobs.get(job_id)
            if collected is None:
                raise ValueError(f"{run_dir}: collect.json holds no job {job_id}")
            status = (collected.get("usage") or {}).get("job_status")
            if status == "DONE":
                dt = self.dt.get(str(job["backend"]))
                if dt is None:
                    raise ValueError(f"{TARGETS}: no dt for {job['backend']}")
                timing, pubs = _completed_job(reader, run_dir, record, job, collected, dt)
                result["timing"].append(timing)
                completed.append((job, timing, pubs))
            else:
                require(
                    isinstance(collected.get("result_unavailable"), str),
                    f"{run_dir} job {job_id}: status {status} without a recorded result_unavailable outcome",
                )
                result["failed"].append(_failed_job(record, job, collected))
        if family != FAMILY or result["failed"]:
            result["kind"] = "timing"
            result["inputs"] = reader.inputs
            return result
        arms = list((record.get("family_configuration") or {}).get("arms") or ())
        require(len(arms) == 1 and arms[0] in (PREP0_ARM, HISTORY_ARM), f"{run_dir}: arms {arms}")
        require(len(completed) == 1 and len(completed[0][0]["pubs"]) == 1, f"{run_dir}: expects one job, one PUB")
        job, timing, pubs = completed[0]
        manifest = job["pubs"][0]
        arm = arms[0]
        executed = _executions(collect, str(run_dir))
        window = _window(manifest, executed, f"{run_dir} {manifest['name']}")
        qubits, bits = _bits(pubs[0], manifest, arm)
        shots = int(bits.shape[1])
        require(shots == timing["shots"], f"{run_dir}: registers hold {shots} shots, options {timing['shots']}")
        scheduled = sorted(int(q) for q in timing["pubs"][0]["schedule"]["qubits"])
        require(scheduled == qubits, f"{run_dir}: INIT qubits {scheduled} differ from the member qubits")
        readout = _sidecar(
            reader,
            run_dir / READOUT_NAME,
            READOUT_SCHEMA,
            record_bytes,
            collect_bytes,
            str(job["job_id"]),
            window,
            str(manifest["name"]),
        )
        ones = bits.sum(axis=1, dtype=np.int64)
        couplings = self.couplings.get(str(job["backend"]), [])
        families = _run_families(Path(run).name, qubits, bits, couplings)
        excitation = _excitation(qubits, ones, shots, readout["qubits"])
        result.update(
            {
                "kind": "control",
                "arm": arm,
                "backend": str(job["backend"]),
                "rep_delay_seconds": timing["rep_delay_seconds"],
                "execution_calibration": window["calibration"],
                "calibration_changed_during_shots": window["changed"],
                "shots": shots,
                "qubits": qubits,
                "excitation": excitation,
                "families": families,
                "drift": _drift(qubits, bits),
                "correlation": _correlation(qubits, bits, couplings),
                "lag1": _lag(qubits, bits),
            }
        )
        declared = {entry["name"].split("/")[0]: entry["members"] for entry in families}
        require(
            declared["E_pairs"] == result["correlation"]["coupled_pairs"]["count"]
            and declared["F_lag1"] == result["lag1"]["defined_qubits"],
            f"{run_dir}: a section tested another member count than its declared family",
        )
        properties_path = run_dir / PROPERTIES_NAME
        if properties_path.is_file():
            properties = _sidecar(
                reader,
                properties_path,
                PROPERTIES_SCHEMA,
                record_bytes,
                collect_bytes,
                str(job["job_id"]),
                window,
                str(manifest["name"]),
            )
            result["properties"] = _properties_block(arm, qubits, excitation, properties)
        else:
            result["properties"] = {
                "class": "sidecar",
                "available": False,
                "not_run": f"no {PROPERTIES_NAME}; run --fetch-properties {run}",
            }
        result["inputs"] = reader.inputs
        return result


# Cross-run sections.


def _history_excess(controls: list[dict[str, Any]]) -> dict[str, Any]:
    cells: dict[tuple[float, datetime], dict[str, dict[str, Any]]] = {}
    for run in controls:
        key = (run["rep_delay_seconds"], _instant(run["execution_calibration"], run["path"]))
        arm_runs = cells.setdefault(key, {})
        require(run["arm"] not in arm_runs, f"two {run['arm']} runs share delay and calibration {key}")
        arm_runs[run["arm"]] = run
    z95 = two_sided_z(1.0 - CONFIDENCE)
    matched: dict[str, Any] = {}
    unmatched: list[str] = []
    for (delay, _), arm_runs in sorted(cells.items(), key=lambda item: (item[0][0], item[0][1])):
        if set(arm_runs) != {PREP0_ARM, HISTORY_ARM}:
            unmatched.extend(run["path"] for run in arm_runs.values())
            continue
        prep0, history = arm_runs[PREP0_ARM], arm_runs[HISTORY_ARM]
        qubits = sorted(set(prep0["qubits"]) & set(history["qubits"]))

        def column(run: dict[str, Any], field: str, qubits: list[int] = qubits) -> np.ndarray:
            return np.asarray([run["excitation"]["qubits"][str(q)][field] for q in qubits], dtype=float)

        args = (
            column(history, "excited"),
            column(history, "shots"),
            column(prep0, "excited"),
            column(prep0, "shots"),
        )
        difference, lower, upper = newcombe(*args, z95)
        # Family C/<delay>: one difference per qubit both jobs read.
        p_values = newcombe_p(*args)
        adjusted = bonferroni(p_values, len(qubits))
        values = [float(v) for v in difference]
        ranked = sorted(range(len(qubits)), key=lambda i: (float(adjusted[i]), qubits[i]))
        matched[_delay_label(delay)] = {
            "prep0_run": prep0["path"],
            "x_history_run": history["path"],
            "execution_calibration": prep0["execution_calibration"],
            "qubit_count": len(qubits),
            "per_qubit": {
                str(q): {
                    "difference": values[i],
                    "newcombe_95": [float(lower[i]), float(upper[i])],
                    "p": float(p_values[i]),
                    "bonferroni_p": float(adjusted[i]),
                }
                for i, q in enumerate(qubits)
            },
            "median_difference": _median(values),
            "mean_difference": math.fsum(values) / len(values),
            "quartiles_difference": _quartiles(values),
            "positive_count": sum(1 for v in values if v > 0.0),
            "smallest_bonferroni_p": [
                {"qubit": qubits[i], "difference": values[i], "bonferroni_p": float(adjusted[i])} for i in ranked[:TOP]
            ],
        }
    return {
        "class": "exact",
        "design": "difference between separately executed jobs: the x_history job minus the prep0 job at one delay "
        "and one execution calibration; the two jobs share no shots",
        "interval": "Newcombe hybrid score (1998 method 10); p inverts the interval at the z where it touches zero",
        "delays": matched,
        "unmatched_runs": sorted(unmatched),
    }


def _cross_delay(controls: list[dict[str, Any]]) -> dict[str, Any]:
    cells: dict[tuple[str, float], dict[str, Any]] = {}
    for run in controls:
        key = (run["arm"], run["rep_delay_seconds"])
        require(key not in cells, f"two {run['arm']} runs at {_delay_label(run['rep_delay_seconds'])}")
        cells[key] = run
    delays = sorted({delay for _, delay in cells})
    arms = sorted({arm for arm, _ in cells})
    qubits = sorted(set.intersection(*(set(run["qubits"]) for run in controls)))
    fractions = {
        arm: {
            _delay_label(delay): {
                str(q): cells[(arm, delay)]["excitation"]["qubits"][str(q)]["fraction"] for q in qubits
            }
            for delay in delays
            if (arm, delay) in cells
        }
        for arm in arms
    }
    medians = {
        arm: {label: _median(list(values.values())) for label, values in by_delay.items()}
        for arm, by_delay in fractions.items()
    }
    sign_tests = {}
    if len(delays) >= 2:
        short, long = _delay_label(delays[0]), _delay_label(delays[1])
        for arm in arms:
            if short not in fractions[arm] or long not in fractions[arm]:
                continue
            pairs = [(fractions[arm][short][str(q)], fractions[arm][long][str(q)]) for q in qubits]
            greater = sum(1 for a, b in pairs if a > b)
            less = sum(1 for a, b in pairs if a < b)
            sign_tests[arm] = {
                "comparison": f"{short} vs {long}",
                "greater": greater,
                "less": less,
                "ties": len(pairs) - greater - less,
                "two_sided_p": float(binomtest(greater, greater + less, 0.5).pvalue) if greater + less else None,
                "median_difference": _median([a - b for a, b in pairs]),
            }
        # Family H_sign: one sign test per arm holding both delays.
        for entry in sign_tests.values():
            p_value = entry["two_sided_p"]
            entry["bonferroni_p"] = None if p_value is None else float(bonferroni(p_value, len(sign_tests)))
    return {
        "class": "exploratory",
        "confounds": [
            "the delays ran under different execution calibrations: "
            + ", ".join(
                f"{arm}@{_delay_label(delay)} {run['execution_calibration']}"
                for (arm, delay), run in sorted(cells.items())
            ),
            "the delays ran different shot counts: "
            + ", ".join(f"{arm}@{_delay_label(delay)} {run['shots']}" for (arm, delay), run in sorted(cells.items())),
        ],
        "qubits": qubits,
        "qubit_count": len(qubits),
        "fractions": fractions,
        "median_fraction": medians,
        "sign_test": sign_tests,
    }


def _families(controls: list[dict[str, Any]]) -> dict[str, Any]:
    """Every test family, sized from run structure alone; each section adjusts its p-values over its family."""
    bonf = "Bonferroni: adjusted p = min(1, members x p)"
    declared = [
        family(
            "B_clopper_pearson",
            sum(len(run["qubits"]) for run in controls),
            "none: marginal two-sided 95 % intervals, descriptive",
            "excited fraction of each member qubit in each control run",
        )
    ]
    cells: dict[tuple[float, datetime], dict[str, dict[str, Any]]] = {}
    for run in controls:
        key = (run["rep_delay_seconds"], _instant(run["execution_calibration"], run["path"]))
        cells.setdefault(key, {})[run["arm"]] = run
    for (delay, _), arm_runs in sorted(cells.items(), key=lambda item: (item[0][0], item[0][1])):
        if set(arm_runs) == {PREP0_ARM, HISTORY_ARM}:
            common = set(arm_runs[PREP0_ARM]["qubits"]) & set(arm_runs[HISTORY_ARM]["qubits"])
            declared.append(
                family(
                    f"C/{_delay_label(delay)}",
                    len(common),
                    bonf,
                    "x_history minus prep0 fraction of each qubit both separately executed jobs read",
                )
            )
    declared.append(family("D_slope", len(controls), bonf, "block-index trend of each control run"))
    for run in controls:
        declared.extend(run["families"])
    delays = sorted({run["rep_delay_seconds"] for run in controls})
    arms_with_both = sorted(
        {
            arm
            for arm in {run["arm"] for run in controls}
            if len(delays) >= 2
            and {delays[0], delays[1]} <= {run["rep_delay_seconds"] for run in controls if run["arm"] == arm}
        }
    )
    declared.append(family("H_sign", len(arms_with_both), bonf, "shortest vs next delay, one sign test per arm"))
    return {
        "alpha": FAMILY_ALPHA,
        "rule": "each family is declared from run structure before its tests run; every p-value is reported raw "
        "and Bonferroni-adjusted over its own family, and no section thresholds an adjusted p-value",
        "families": declared,
    }


def _targets(root: Path, reader: Reader) -> tuple[dict[str, float], dict[str, list[list[int]]]]:
    targets = reader.json(root / TARGETS)
    dt = {name: float(entry["dt"]) for name, entry in targets["backends"].items()}
    couplings = {
        name: [list(map(int, pair)) for pair in entry["instructions"]["cz"]["qargs"]]
        for name, entry in targets["backends"].items()
    }
    return dt, couplings


def evaluate(root: Path, runs: Sequence[str]) -> dict[str, Any]:
    require(bool(runs) and len(set(runs)) == len(runs), "the extraction needs distinct run directories")
    reader = Reader(root)
    dt, couplings = _targets(root, reader)
    extracted = parallel.ordered_map(RunExtractor(str(root), dt, couplings), list(runs), min_items=2)
    inputs = dict(reader.inputs)
    for run in extracted:
        inputs.update(run.pop("inputs", {}))
    controls = [run for run in extracted if run["kind"] == "control"]
    by_name = {Path(run["path"]).name: run for run in extracted}
    families = _families(controls)
    # Family D_slope: one block-index trend test per control run.
    for run in controls:
        slope = run["drift"]["slope"]
        p_value = slope["two_sided_p"]
        slope["bonferroni_p"] = None if p_value is None else float(bonferroni(p_value, len(controls)))
    completed = [timing for run in extracted for timing in run["timing"] if timing["billed_seconds"] is not None]
    relation = {
        timing["job_id"]: {
            "circuits_execution_time_seconds": timing["circuits_execution_time_seconds"],
            "rounded_2_plus_circuit_seconds": math.floor(2.0 + timing["circuits_execution_time_seconds"] + 0.5),
            "final_charge_seconds": timing["billed_seconds"],
        }
        for timing in completed
    }
    for row in relation.values():
        row["equal"] = int(row["final_charge_seconds"]) == row["rounded_2_plus_circuit_seconds"]
    payload: dict[str, Any] = {
        "inference_families": families,
        "schema": SCHEMA,
        "classes": CLASSES,
        "runs": list(runs),
        "inputs": dict(sorted(inputs.items())),
        "dt_seconds": {
            backend: dt[backend] for backend in sorted({t["backend"] for run in extracted for t in run["timing"]})
        },
        "A_timing": {
            "class": "exact",
            "jobs": {name: run["timing"] for name, run in by_name.items() if run["timing"]},
            "failed_jobs": {name: run["failed"] for name, run in by_name.items() if run["failed"]},
            "billed_vs_rounded_circuit": {
                "scope": "observed comparison of each completed job's final charge with floor(2 + circuits execution "
                "seconds + 0.5); failed jobs carry no final charge and stay outside it",
                "jobs": relation,
                "count": len(relation),
                "all_equal": all(row["equal"] for row in relation.values()),
            },
        },
        "run_kinds": {
            name: {
                "kind": run["kind"],
                "family": run["family"],
                **(
                    {"arm": run["arm"], "rep_delay_seconds": run["rep_delay_seconds"]}
                    if run["kind"] == "control"
                    else {}
                ),
            }
            for name, run in by_name.items()
        },
    }
    label = {Path(run["path"]).name: f"{run['arm']}_{_delay_label(run['rep_delay_seconds'])}" for run in controls}
    for section, key in (
        ("B_excitation", "excitation"),
        ("D_drift", "drift"),
        ("E_correlation", "correlation"),
        ("F_lag1", "lag1"),
        ("G_properties", "properties"),
    ):
        payload[section] = {
            name: {
                "label": label[name],
                "execution_calibration": by_name[name]["execution_calibration"],
                **by_name[name][key],
            }
            for name in label
        }
    payload["C_history_excess"] = _history_excess(controls) if controls else {"class": "exact", "delays": {}}
    payload["H_cross_delay"] = _cross_delay(controls) if controls else {"class": "exploratory"}
    return payload


def write(path: Path, root: Path, runs: Sequence[str]) -> dict[str, Any]:
    payload = evaluate(root, runs)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(payload))
    return payload


def _replay_mismatch(retained: Any, recomputed: Any, path: str = "") -> str | None:
    """The first field where recomputed departs from retained: floats within REPLAY_REL_TOL, all else exact."""
    if isinstance(retained, float) and isinstance(recomputed, float):
        return None if math.isclose(retained, recomputed, rel_tol=REPLAY_REL_TOL, abs_tol=0.0) else path
    if type(retained) is not type(recomputed):
        return path
    if isinstance(retained, dict):
        if retained.keys() != recomputed.keys():
            return path
        for key in retained:
            mismatch = _replay_mismatch(retained[key], recomputed[key], f"{path}/{key}")
            if mismatch is not None:
                return mismatch
        return None
    if isinstance(retained, list):
        if len(retained) != len(recomputed):
            return path
        for index, (left, right) in enumerate(zip(retained, recomputed, strict=True)):
            mismatch = _replay_mismatch(left, right, f"{path}[{index}]")
            if mismatch is not None:
                return mismatch
        return None
    return None if retained == recomputed else path


def check(root: Path, output: Path = OUTPUT) -> int:
    """Verify every recorded input digest, recompute the retained JSON from its runs and compare it."""
    payload = json.loads((root / output).read_bytes())
    require(payload.get("schema") == SCHEMA, f"{output}: schema {payload.get('schema')}")
    for name, digest in payload["inputs"].items():
        path = root / name
        require(path.is_file(), f"{output}: input {name} is missing")
        require(sha256_bytes(path.read_bytes()) == digest, f"{output}: input {name} sha256 differs")
    recomputed = json.loads(encode(evaluate(root, payload["runs"])))
    mismatch = _replay_mismatch(payload, recomputed)
    require(mismatch is None, f"{output}: the replay differs from the retained output at {mismatch or '/'}")
    return len(payload["runs"])


# Read-only properties sidecar.


def fetch_properties(run_dir: Path) -> Path:
    """Retain each member qubit's calibration values at every control PUB's execution start.

    Reads the IBM service (calibration reads need no approval). The start
    fetch must read the calibration collect.json recorded for the PUB, and a
    calibration change during the shots adds a stop fetch, as
    state_prep_excess.fetch_readout does.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    from live_run import readout_flips

    record_bytes = (run_dir / "record.json").read_bytes()
    record = json.loads(record_bytes)
    collect_bytes = (run_dir / "collect.json").read_bytes()
    executed = _executions(json.loads(collect_bytes), str(run_dir))
    service = QiskitRuntimeService()
    windows = []

    def value(props: Any, qubit: int, name: str) -> float | None:
        try:
            return float(props.qubit_property(qubit, name)[0])
        except Exception:  # BackendPropertyError: the property is absent for this qubit
            return None

    for job in (record.get("submission") or {}).get("jobs") or []:
        backend = service.backend(str(job["backend"]))
        for manifest in job["pubs"]:
            window = _window(manifest, executed, f"{run_dir} {manifest['name']}")
            qubits = sorted({_member_qubit(str(component["member"]))[1] for component in manifest["components"]})
            for edge in ["start", "stop"] if window["changed"] else ["start"]:
                props = backend.properties(datetime=_instant(window[edge], f"{manifest['name']} {edge}"))
                calibration = props.last_update_date.isoformat()
                same = _instant(calibration, "fetched") == _instant(window["calibration"], "collect")
                require(
                    same if edge == "start" else not same,
                    f"{manifest['name']}: properties at {window[edge]} read calibration {calibration}, "
                    f"collect recorded {window['calibration']} (changed during shots: {window['changed']})",
                )
                values = {}
                for qubit in qubits:
                    e10, e01 = readout_flips(props, qubit)
                    values[str(qubit)] = {
                        "frequency_hz": value(props, qubit, "frequency"),
                        "anharmonicity_hz": value(props, qubit, "anharmonicity"),
                        "T1_seconds": value(props, qubit, "T1"),
                        "T2_seconds": value(props, qubit, "T2"),
                        "readout_error": value(props, qubit, "readout_error"),
                        "prob_meas1_prep0": float(e10),
                        "prob_meas0_prep1": float(e01),
                        "readout_length_seconds": value(props, qubit, "readout_length"),
                    }
                windows.append(
                    {
                        "job_id": str(job["job_id"]),
                        "pub": str(manifest["name"]),
                        "edge": edge,
                        "at": window[edge],
                        "calibration": calibration,
                        "qubits": values,
                    }
                )
    payload = {
        "schema": PROPERTIES_SCHEMA,
        "record_sha256": sha256_bytes(record_bytes),
        "collect_sha256": sha256_bytes(collect_bytes),
        "windows": windows,
    }
    destination = run_dir / PROPERTIES_NAME
    destination.write_bytes((json.dumps(payload, indent=1, sort_keys=True, allow_nan=False) + "\n").encode())
    return destination


# Self-test.

SYNTHETIC_BACKEND = "fake_backend"
SYNTHETIC_DT = 4e-9
SYNTHETIC_DURATION = 2790
SYNTHETIC_CALIBRATION = "2026-01-01T00:00:00+00:00"
SYNTHETIC_START = "2026-01-01T00:10:00+00:00"
SYNTHETIC_STOP = "2026-01-01T00:10:04+00:00"
SYNTHETIC_COUPLINGS = [[0, 1], [1, 0], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [0, 7]]


def _dump(path: Path, payload: Any) -> bytes:
    data = (json.dumps(payload, indent=1, sort_keys=True) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def _synthetic_timing(qubits: list[int], arm: str) -> str:
    rows = []
    for q in qubits:
        cursor = 33
        for role in ("INIT",):
            for duration in (64, 108, 64, 64, 8, 64, 108, 64, 64, 8):
                rows.append(f"main,{role}_{q},Qubit {q},{cursor},{duration},play")
                cursor += duration
            rows.append(f"main,{role}_{q},AWGR0_{q},154,325,capture")
            rows.append(f"main,{role}_{q},AWGR0_{q},707,325,capture")
        rows.append(f"main,measure_{q},Qubit {q},1139,300,play")
        rows.append(f"main,measure_{q},AWGR0_{q},1260,325,capture")
        start = 1684
        if arm == HISTORY_ARM:
            rows.append(f"main,x_{q},Qubit {q},1684,8,play")
            start = 1692
        rows.append(f"main,barrier,Qubit {q},{start},0,barrier")
        rows.append(f"main,FINI_{q},Qubit {q},{start},1098,play")
    return "\n".join(rows)


def _synthetic_run(
    root: Path,
    name: str,
    arm: str,
    delay: float,
    bits: np.ndarray,
    qubits: list[int],
    readout: dict[int, tuple[float, float]],
    properties: dict[int, dict[str, Any]] | None = None,
    failed: bool = False,
) -> str:
    """A collected run in live_run's raw and collect layouts, with its readout and optional properties sidecars."""
    run = root / "results" / "live" / name
    job_id = f"job_{name}"
    shots = int(bits.shape[1])
    kind = "dynamic" if arm == HISTORY_ARM else "static"
    pub_name = f"{SYNTHETIC_BACKEND}_{kind}_pub_01"
    components = []
    registers = {}
    executed = {}
    for index, qubit in enumerate(qubits):
        register = f"g{index}_r0_c"
        member = f"spc_{arm}_q{qubit}"
        components.append({"member": member, "physical_qubits": [qubit], "registers_by_replica": [[register]]})
        registers[register] = {
            "num_bits": 1,
            "num_shots": shots,
            "bitstrings": ["1" if b else "0" for b in bits[index]],
        }
        executed[member] = {
            "pub": pub_name,
            "start": SYNTHETIC_START,
            "stop": SYNTHETIC_STOP,
            "calibration": SYNTHETIC_CALIBRATION,
            "calibration_changed_during_shots": False,
        }
    options = {
        "default_shots": shots,
        "execution": {"init_qubits": True, "rep_delay": delay, "meas_type": "classified", "scheduler_timing": True},
        "max_execution_time": 8,
        "twirling": {"enable_gates": False, "enable_measure": False},
        "dynamical_decoupling": {"enable": False},
    }
    period_ns = round(delay * 1e9) + SYNTHETIC_DURATION * 4
    pub_cost = {
        "name": pub_name,
        "shots": shots,
        "scheduled_seconds": 2.18e-06,
        "repetition_delay_seconds": delay,
        "classical_latency_seconds": 0.0,
        "estimated_execution_seconds": shots * (delay + 2.18e-06),
    }
    planned = {
        "name": f"{SYNTHETIC_BACKEND}/{kind}/1",
        "pubs": [pub_cost],
        "overhead_seconds": 2.3,
        "estimated_charge_seconds": 2.3 + shots * (delay + 2.18e-06),
        "max_execution_seconds": 8,
    }
    record = {
        "family_configuration": {"name": FAMILY, "qubits": qubits, "arms": {arm: "steps"}},
        "policy": {"rep_delay_seconds": delay},
        "backends": {SYNTHETIC_BACKEND: {"backend_version": "1.0.0", "processor_type": {"family": "Heron"}}},
        "groups": [{"backend": SYNTHETIC_BACKEND, "calibration": SYNTHETIC_CALIBRATION}],
        "optimization": {"selected": "candidate-000", "candidates": [{"name": "candidate-000", "jobs": [planned]}]},
        "execution_contract": {"selected_job_costs": [planned]},
        "submission": {
            "jobs": [
                {
                    "job_id": job_id,
                    "backend": SYNTHETIC_BACKEND,
                    "options": options,
                    "pubs": [{"name": pub_name, "kind": kind, "components": components}],
                }
            ]
        },
    }
    usage: dict[str, Any]
    if failed:
        usage = {
            "job_status": "ERROR",
            "usage_status": "pending",
            "submitted_pub_shots": shots,
            "raw_usage_metadata": {"qpu_charge_time_seconds": 2, "value": 0.03, "status": "pending"},
        }
        collected = {
            "kind": kind,
            "usage": usage,
            "result_unavailable": "RuntimeJobMaxTimeoutError: 'Error code 1305; Job ran longer than allowed.'",
        }
    else:
        collected = {"kind": kind, "usage": {"job_status": "DONE", "usage_status": "final"}}
    collect = [{"jobs": {job_id: collected}}, {"group": "state_prep", "job_id": job_id, "executed": executed}]
    record_bytes = _dump(run / "record.json", record)
    collect_bytes = _dump(run / "collect.json", collect)
    if failed:
        return f"results/live/{name}"
    raw = run / "raw" / job_id
    pub = _dump(
        raw / "pub_00.json",
        {
            "pub_index": 0,
            "pub_name": pub_name,
            "registers": registers,
            "metadata": {
                "compilation": {
                    "scheduler_timing": {
                        "circuit_duration": SYNTHETIC_DURATION,
                        "timing": _synthetic_timing(qubits, arm),
                    }
                }
            },
        },
    )
    chunk = {"parts": [{"idx_item": 0, "size": 1}], "start": SYNTHETIC_START, "stop": SYNTHETIC_STOP}
    metadata = _dump(raw / RESULT_METADATA, {"executor": {"chunk_timing": [chunk]}, "options": options, "shots": shots})
    circuit_ns = shots * period_ns
    metrics = _dump(
        raw / "job_metrics.json",
        {
            "circuits_execution_time_ns": circuit_ns,
            "timestamps": {
                "created": "2026-01-01T00:09:50Z",
                "running": "2026-01-01T00:09:58Z",
                "finished": "2026-01-01T00:10:06Z",
            },
            "usage": {
                "qpu_charge_time_seconds": math.floor(2.0 + circuit_ns * 1e-9 + 0.5),
                "value": 0.05,
                "status": "complete",
            },
        },
    )
    _dump(
        raw / "index.json",
        {
            "job_id": job_id,
            "files": {"pub_00.json": sha256_bytes(pub), RESULT_METADATA: sha256_bytes(metadata)},
            "metrics": ["job_metrics.json"],
            "metrics_latest": "job_metrics.json",
            "metrics_sha256": [sha256_bytes(metrics)],
        },
    )
    readout_qubits = {str(q): {"prob_meas1_prep0": readout[q][0], "prob_meas0_prep1": readout[q][1]} for q in qubits}
    window = {"job_id": job_id, "pub": pub_name, "edge": "start", "at": SYNTHETIC_START}
    sidecar = {"record_sha256": sha256_bytes(record_bytes), "collect_sha256": sha256_bytes(collect_bytes)}
    _dump(
        run / READOUT_NAME,
        {
            "schema": READOUT_SCHEMA,
            **sidecar,
            "windows": [{**window, "calibration": SYNTHETIC_CALIBRATION, "qubits": readout_qubits}],
        },
    )
    if properties is not None:
        _dump(
            run / PROPERTIES_NAME,
            {
                "schema": PROPERTIES_SCHEMA,
                **sidecar,
                "windows": [
                    {
                        **window,
                        "calibration": SYNTHETIC_CALIBRATION,
                        "qubits": {str(q): properties[q] for q in qubits},
                    }
                ],
            },
        )
    return f"results/live/{name}"


def _expect_refusal(action: Any, fragment: str) -> None:
    try:
        action()
    except ValueError as error:
        require(fragment in str(error), f"refused for another reason: {error}")
        return
    raise AssertionError(f"accepted input the extraction refuses ({fragment})")


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
    """The root in [0, 1] of a function decreasing in p."""
    low, high = 0.0, 1.0
    for _ in range(60):
        middle = (low + high) / 2
        if function(middle) > target:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def self_test() -> None:
    from diagnostic_experiments import STATE_PREP_FAMILY, STATE_PREP_HISTORY_ARM

    require(FAMILY == STATE_PREP_FAMILY and HISTORY_ARM == STATE_PREP_HISTORY_ARM, "family constants moved")
    with tempfile.TemporaryDirectory(prefix="state-prep-control-parameters-") as scratch:
        _self_test(Path(scratch))


def _self_test(scratch: Path) -> None:
    # Clopper-Pearson against an independent binomial-tail inversion.
    for k, n in ((0, 50), (3, 50), (50, 50), (109, 4096), (281, 32768)):
        lower, upper = (float(v[0]) for v in clopper_pearson(np.asarray([k]), np.asarray([n])))
        reference_upper = 1.0 if k == n else _bisect(lambda p, k=k, n=n: _binomial_cdf(k, n, p), 0.025)
        reference_lower = 0.0 if k == 0 else _bisect(lambda p, k=k, n=n: _binomial_cdf(k - 1, n, p), 0.975)
        require(abs(upper - reference_upper) <= 1e-9, f"upper {k}/{n}: {upper} vs {reference_upper}")
        require(abs(lower - reference_lower) <= 1e-9, f"lower {k}/{n}: {lower} vs {reference_lower}")
    # Newcombe (1998) Table II example (a), 56/70 - 48/80, method 10: 0.0524 to 0.3339.
    _, low, high = (
        float(v) for v in newcombe(np.asarray(56), np.asarray(70), np.asarray(48), np.asarray(80), 1.959964)
    )
    require(abs(low - 0.0524) < 5e-5 and abs(high - 0.3339) < 5e-5, f"Newcombe example: {low}, {high}")
    # Poisson-binomial convolution against enumeration on three qubits.
    probabilities = [0.1, 0.35, 0.8]
    brute = [0.0] * 4
    for outcome in range(8):
        weight = 1.0
        for bit, p in enumerate(probabilities):
            weight *= p if outcome >> bit & 1 else 1.0 - p
        brute[bin(outcome).count("1")] += weight
    require(np.allclose(poisson_binomial(probabilities), brute, rtol=0.0, atol=1e-15), "Poisson-binomial law")

    rng = np.random.default_rng(20261018)
    qubits = list(range(8))
    shots = 4096
    readout = {q: (0.0005 + 0.0002 * q, 0.012) for q in qubits}
    marginals = np.asarray([0.006 + 0.003 * q for q in qubits])
    independent = (rng.random((len(qubits), shots)) < marginals[:, None]).astype(np.uint8)
    # Exact counts: the first ones[q] shots of qubit q are excited, so fractions are known.
    known_ones = [5 * (q + 1) for q in qubits]
    known = np.zeros((len(qubits), shots), dtype=np.uint8)
    for index, count in enumerate(known_ones):
        known[index, rng.permutation(shots)[:count]] = 1
    burst = independent.copy()
    burst_shots = rng.permutation(shots)[:40]
    burst[:6, burst_shots] = 1
    ramp = (rng.random((len(qubits), shots)) < np.linspace(0.0, 0.12, shots)[None, :]).astype(np.uint8)
    memory = np.zeros((len(qubits), shots), dtype=np.uint8)
    draws = rng.random((len(qubits), shots))
    for s in range(1, shots):
        memory[:, s] = np.where(memory[:, s - 1] == 1, draws[:, s] < 0.5, draws[:, s] < 0.02)
    properties = {
        q: {
            "frequency_hz": 4.5e9 + 1e7 * q,
            "anharmonicity_hz": -3.1e8,
            "T1_seconds": 2e-4,
            "T2_seconds": 1e-4 + 1e-6 * q,
            "readout_error": 0.01,
            "prob_meas1_prep0": readout[q][0],
            "prob_meas0_prep1": readout[q][1],
            "readout_length_seconds": 2.18e-6,
        }
        for q in qubits
    }
    root = scratch / "main"
    _dump(
        root / TARGETS,
        {"backends": {SYNTHETIC_BACKEND: {"dt": SYNTHETIC_DT, "instructions": {"cz": {"qargs": SYNTHETIC_COUPLINGS}}}}},
    )
    runs = [
        _synthetic_run(root, "p20", PREP0_ARM, 2e-5, known, qubits, readout, properties),
        _synthetic_run(root, "h20", HISTORY_ARM, 2e-5, independent, qubits, readout),
        _synthetic_run(root, "p50", PREP0_ARM, 5e-5, burst, qubits, readout),
        _synthetic_run(root, "h50", HISTORY_ARM, 5e-5, ramp, qubits, readout),
        _synthetic_run(root, "p250", PREP0_ARM, 2.5e-4, memory, qubits, readout),
        _synthetic_run(root, "h250", HISTORY_ARM, 2.5e-4, independent, qubits, readout),
        _synthetic_run(root, "f20", PREP0_ARM, 2e-5, independent, qubits, readout, failed=True),
    ]
    output = Path("results/live/parameters.json")
    payload = json.loads(encode(write(root / output, root, runs)))
    # B: known counts give exact fractions and the readout correction.
    row = payload["B_excitation"]["p20"]["qubits"]["3"]
    require(row["excited"] == known_ones[3] and row["fraction"] == known_ones[3] / shots, f"fraction {row}")
    corrected = (known_ones[3] / shots - readout[3][0]) / (1.0 - readout[3][1] - readout[3][0])
    require(math.isclose(row["readout_corrected"], corrected, rel_tol=1e-11), "readout correction")
    # A: a job whose circuit time equals shots x (rep_delay + duration x dt) leaves a zero residual.
    timing = payload["A_timing"]["jobs"]["p20"][0]
    require(abs(timing["per_shot_residual_seconds"]) < 1e-15, f"residual {timing['per_shot_residual_seconds']}")
    relation = payload["A_timing"]["billed_vs_rounded_circuit"]
    require(relation["all_equal"] and relation["count"] == len(runs) - 1, f"billed relation {relation}")
    require(math.isclose(timing["lock_overhead_seconds"], 4.0 - shots * 3.116e-5, rel_tol=1e-9), "lock overhead")
    patterns = timing["pubs"][0]["schedule"]["patterns"]
    require(
        patterns["INIT"]["uniform"] and patterns["INIT"]["distinct_patterns"][0]["captures_dt"] == [325, 325], "INIT"
    )
    require(timing["planner_per_shot_undercount_seconds"] > 0, "planner undercount sign")
    failed = payload["A_timing"]["failed_jobs"]["f20"][0]
    require(failed["error_code"] == 1305 and failed["billed_seconds"] is None, f"failed job {failed}")
    require(failed["provisional_usage"]["usage_status"] == "pending", "provisional usage status")
    # Families: every declared family carries its member count before the sections adjust over it.
    declared = {entry["name"]: entry["members"] for entry in payload["inference_families"]["families"]}
    require(declared["C/20us"] == len(qubits) and declared["D_slope"] == len(runs) - 1, f"families {declared}")
    require(declared["E_pairs/p50"] == payload["E_correlation"]["p50"]["coupled_pairs"]["count"], "E family")
    # C: x_history minus prep0 matches every delay under one calibration; p inverts the 95 % interval.
    cells = payload["C_history_excess"]["delays"]
    require(set(cells) == {"20us", "50us", "250us"}, f"history cells {sorted(cells)}")
    for row in cells["50us"]["per_qubit"].values():
        lower, upper = row["newcombe_95"]
        require((lower > 0.0 or upper < 0.0) == (row["p"] < 0.05), f"interval and p disagree: {row}")
    # D: the ramp drifts, the independent run does not.
    ramped, steady = payload["D_drift"]["h50"], payload["D_drift"]["h20"]
    require(ramped["smallest_bonferroni_p"][5]["bonferroni_p"] < 1e-3, f"drift {ramped['smallest_bonferroni_p']}")
    require(ramped["slope"]["bonferroni_p"] < 1e-6 and ramped["slope"]["slope_per_block"] > 0, f"{ramped['slope']}")
    require(steady["smallest_bonferroni_p"][0]["bonferroni_p"] > 0.01, f"steady {steady['smallest_bonferroni_p']}")
    # E: the burst raises simultaneous excitation and coupled-pair correlation; independent bits do not.
    bursty, calm = payload["E_correlation"]["p50"], payload["E_correlation"]["h20"]
    require(bursty["variance_ratio"] > 1.5 and bursty["top_events"][0]["excited"] >= 6, "burst variance")
    require(bursty["coupled_pairs"]["top"][2]["bonferroni_p"] < 1e-6, f"burst pairs {bursty['coupled_pairs']}")
    require(abs(calm["variance_ratio"] - 1.0) < 0.15, f"calm variance {calm['variance_ratio']}")
    require(calm["coupled_pairs"]["top"][0]["bonferroni_p"] > 0.01, f"calm pairs {calm['coupled_pairs']['top'][0]}")
    require(bursty["tail_at_least"]["6"]["observed"] >= 40 / shots, "burst tail")
    # F: a Markov chain shows lag-1 memory.
    require(payload["F_lag1"]["p250"]["median_difference"] > 0.3, "lag-1 memory")
    require(abs(payload["F_lag1"]["h20"]["median_difference"]) < 0.05, "lag-1 on independent bits")
    # G: the population temperature follows h f / (k_B ln((1 - p) / p)); absent sidecars read not run.
    sidecar = payload["G_properties"]["p20"]
    temperatures = sidecar["population_temperature"]["kelvin"]
    require(bool(temperatures), "no population temperature on the synthetic prep0 run")
    for key, kelvin in temperatures.items():
        p = payload["B_excitation"]["p20"]["qubits"][key]["readout_corrected"]
        frequency = float(properties[int(key)]["frequency_hz"])
        expected = PLANCK * frequency / (BOLTZMANN * math.log((1.0 - p) / p))
        require(math.isclose(kelvin, expected, rel_tol=1e-10), f"q{key}: {kelvin} K vs {expected} K")
    require(sidecar["spearman_fraction"]["fields"]["frequency_hz"]["rho"] == 1.0, "Spearman on a monotone field")
    require(not payload["G_properties"]["h20"]["available"], "absent sidecar")
    require(payload["H_cross_delay"]["qubit_count"] == len(qubits), "cross-delay qubits")
    # The replay reproduces the output; a float past the tolerance or a changed input refuses.
    require(check(root, output) == len(runs), "the replay found no run")
    pristine = (root / output).read_bytes()
    nudged = json.loads(pristine)
    nudged["E_correlation"]["p50"]["variance_ratio"] *= 1.0 + 1e-13
    (root / output).write_bytes((json.dumps(nudged, indent=1, sort_keys=True) + "\n").encode())
    require(check(root, output) == len(runs), "a last-digit change refused the replay")
    nudged["E_correlation"]["p50"]["variance_ratio"] *= 1.0 + 1e-6
    (root / output).write_bytes((json.dumps(nudged, indent=1, sort_keys=True) + "\n").encode())
    _expect_refusal(lambda: check(root, output), "at /E_correlation/p50/variance_ratio")
    (root / output).write_bytes(pristine)
    readout_path = root / "results/live/h20" / READOUT_NAME
    readout_path.write_bytes(readout_path.read_bytes().replace(b"0.012", b"0.013", 1))
    _expect_refusal(lambda: check(root, output), "sha256 differs")
    # Refusals: mismatched shots and a missing raw file.
    other = scratch / "refusals"
    _dump(other / TARGETS, json.loads((root / TARGETS).read_bytes()))
    short_run = _synthetic_run(other, "short", PREP0_ARM, 2e-5, known, qubits, readout)
    pub_path = other / short_run / "raw" / "job_short" / "pub_00.json"
    pub = json.loads(pub_path.read_bytes())
    pub["registers"]["g0_r0_c"]["bitstrings"] = pub["registers"]["g0_r0_c"]["bitstrings"][:-1]
    index_path = pub_path.parent / "index.json"
    index = json.loads(index_path.read_bytes())
    index["files"]["pub_00.json"] = sha256_bytes(_dump(pub_path, pub))
    _dump(index_path, index)
    _expect_refusal(lambda: evaluate(other, [short_run]), "outcomes for")
    missing_run = _synthetic_run(other, "missing", PREP0_ARM, 2e-5, known, qubits, readout)
    (other / missing_run / "raw" / "job_missing" / "pub_00.json").unlink()
    _expect_refusal(lambda: evaluate(other, [missing_run]), "raw file missing")
    ledger_run = _synthetic_run(other, "ledger", PREP0_ARM, 2e-5, known, qubits, readout)
    collect_path = other / ledger_run / "collect.json"
    collect = json.loads(collect_path.read_bytes())
    ledger_index = json.loads((other / ledger_run / "raw" / "job_ledger" / "index.json").read_bytes())
    files = dict(ledger_index["files"]) | {"pub_00.json": "0" * 64}
    collect[0]["jobs"]["job_ledger"]["raw"] = {"directory": "raw/job_ledger", "files": files}
    _dump(collect_path, collect)
    _expect_refusal(lambda: evaluate(other, [ledger_run]), "differs from the raw ledger")
    print(
        "state_prep_control_parameters: Clopper-Pearson matches the binomial-tail inversion to 1e-9, Newcombe's "
        "example reproduces, the Poisson-binomial law matches enumeration; known fractions, a zero timing residual, "
        "an injected burst, drift and lag-1 memory are recovered; the replay holds to 1e-9 and refuses changed "
        "inputs, mismatched shots, a missing raw file and a raw index that differs from its collection ledger"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="JSON to write from the given run directories")
    parser.add_argument("runs", nargs="*", type=Path, help="run directories under results/live")
    parser.add_argument("--check", action="store_true", help=f"replay {OUTPUT} from its recorded inputs")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--fetch-properties",
        action="store_true",
        help=f"retain {PROPERTIES_NAME} beside each given completed control run (read-only service call)",
    )
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        return 0
    if arguments.check:
        count = check(ROOT)
        print(f"state_prep_control_parameters: {OUTPUT} replays from its {count} runs within {REPLAY_REL_TOL:g}")
        return 0
    if not arguments.runs:
        parser.error("name run directories")
    if arguments.fetch_properties:
        for run_dir in arguments.runs:
            print(f"{fetch_properties(run_dir)}: execution properties retained")
        return 0
    if arguments.out is None:
        parser.error("--out, --check, --self-test or --fetch-properties is required")
    runs = [_relative(run, ROOT) for run in arguments.runs]
    payload = write(arguments.out, ROOT, runs)
    print(f"{arguments.out}: {len(runs)} runs, {len(payload['inputs'])} inputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
