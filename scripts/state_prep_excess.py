"""Preregistered initial excitation of an n21 placement from state-prep-control raw shots.

The Sampler's implicit initialization (init_qubits) is imperfect: the
residual excitation it leaves depends on the state the previous shot ended
in and shrinks with the repetition delay. The initialization is one channel
acting on the previous shot's end state, so on a diagonal end state with
|1> population q the excitation it leaves is affine in q,
eps(q) = eps_0 + (eps_1 - eps_0) q, and an all-|1> history (q = 1) leaves
eps_1, the largest an n21 shot can leave behind. The x_history arm (init,
measure, x) ends a shot in |1> unless its own initialization left |1> (the
measurement projects that branch and x maps it to |0>) or the x fails, so
its shots run at q >= (1 - pi)(1 - delta), with pi the arm's true
excitation and delta the probability that the x leaves |0> unflipped. Its
excitation eps_h = eps(q) bounds the all-|1> one: eps_1 = eps_h / q -
eps_0 (1 - q) / q <= eps_h / q when eps_1 >= eps_0, and eps_1 < eps_h
otherwise. prep0 (init, measure) reads the excitation after a history near
|0>. The shots of one job's circuits interleave, so prep0 and x_history
counts come only from a job holding no other arm. Measurement is
projective, the model dynamic_density's exact law applies.

Readout. A control PUB's counts pass through the readout in force while its
shots ran, which live_run --collect records per member as the PUB's
execution calibration. --fetch-readout RUN_DIR reads properties(datetime=...)
at each PUB's execution start, and at its stop when the calibration changed
during the shots, requires each fetched stamp to equal the calibration
collect recorded, and retains prob_meas1_prep0, prob_meas0_prep1 (through
live_run.readout_flips), the x error, the x duration and T1 of every member
qubit in state-prep-readout.json beside the run. The n21 model applies its
own placed_qubit_calibration readout. The rule takes the envelope: e10 is
the smallest and e01 the largest value among the model's and every
execution calibration of the qubit's control PUBs. These are the
calibration's reported values, each the parameter of a readout channel; the
rule assigns them no sampling distribution.

Rule. C is the set of qubits read by x_history at 50 and 250 us and by
prep0 at 250 us in the supplied control runs. The family-wise alpha splits
evenly over 3|C| one-sided Clopper-Pearson bounds, three per controlled
qubit, so the bounds hold simultaneously over every placement inside C and
the fixed-point iteration below may inspect any number of placements. For
each qubit q of the placement S, which must lie inside C:

- U50_q, U250_q: upper bounds on the x_history excited fraction.
- L0_q: lower bound on the prep0 excited fraction at 250 us.
- A PUB's shots run in sequence inside each executor chunk
  (result_metadata.json's chunk_timing), so the first shot of each of its
  s chunks follows an uncontrolled shot. The upper bounds count all ones
  against the n - s controlled shots, and the lower bound removes s ones
  first.
- b_q = min(L0_q, the e10 envelope); e01_q the e01 envelope.
- u_q(d) = max(0, state_prep_excitation(U_d, b_q, e01_q)), the x_history
  arm's own excitation at delay d.
- delta_q: the largest x error plus (x duration + measure duration) / T1
  over the execution calibrations of q's x_history PUBs. live_run's noise
  model composes thermal relaxation over the gate duration with a
  depolarizing error whose total average infidelity is the reported error,
  and a depolarizing error of average infidelity r leaves |0> unflipped
  with probability r. A measurement can also excite |0> before the x: on
  ibm_kingston the measurement instrument's 0 -> 1 rate sits one to two
  orders below its T1-dominated 1 -> 0 rate
  (docs/notes/ibm_quantum/heron-r2-readout-resonator.md), so measure
  duration / T1 bounds it with at least a factor of ten to spare. Leakage
  out of the qubit subspace lies outside the model.
- eps_q(d) = u_q(d) / ((1 - u_q(d)) (1 - delta_q)).

eps = (P - e10) / (1 - e01 - e10) rises in P, falls in e10 wherever
P < 1 - e01 and rises in e01 wherever P > e10, and u / ((1 - u)(1 - delta))
rises in u and delta, so the upper P, the lower baseline, the upper e01 and
the larger delta give the largest eps the data admit; an upper P at or
above 1 - e01 reverses the e10 direction and the rule refuses it. eps50 and
eps250 are the maxima over S. prep0 at 50 us, where present, enters the
report as a history-versus-delay decomposition of point estimates and
stays outside the bound family.

The bounds cover each placed qubit's marginal excitation.
dynamic_density.with_prep_excitation applies independent local channels, so
a plan built on eps covers correlated initialization failures only as far
as they factor. The report keeps, for each control cell whose placed
members share one PUB (and therefore one shot order), the number of shots
in which two or more placed qubits read 1 beside the number their point
marginals predict under independence; correlated readout raises that count
as well, so it is a diagnostic outside the bound family.

eps bounds the initialization at the controls' execution calibrations.
Applying it to the n21 plan assumes that initialization channel unchanged
until the n21 shots run; calibration_scope records both calibrations and
whether the plan's noise model shares one with the controls, and the
stage-2 case states the assumption. An eps at or above 1 lies outside the
planner's --prep-excitation domain and is refused.

A plan at any repetition delay D other than 50 and 250 us takes the
single-delay rule: C is the set of qubits read by x_history and prep0 at D,
alpha splits over 2|C| bounds, U_D and L0_q are both read at D, and
eps_target is the maximum of eps_q(D) over S. prep0 after a near-|0>
history reads (1 - eps_0) e10 + eps_0 (1 - e01), which lies at or above e10,
so b_q = min(L0_q, e10 envelope) stays a baseline from below at any delay.
Control runs at other delays enter the report only.

Placement and eps depend on each other, so the plan iterates to a fixed
point: plan at --prep-excitation 0, read S0, compute eps(S0) at the plan's
delay; while eps(S_k) exceeds the eps_k planned with, re-plan at
eps_{k+1} = max(eps_k, eps(S_k)) and read S_{k+1}; stop at the first k with
eps(S_k) <= eps_k. eps_k never decreases and every eps(S) is a maximum of
per-qubit values over C, a finite set, so the iteration stops. The report's
fixed_point block carries the verdict and the next --prep-excitation,
rounded up to 1e-6.

Each run writes state-prep-excess.json beside the n21 record; --check
recomputes every retained one from the inputs it names and requires the same
bytes, and --self-test exercises the rule on synthetic runs in the raw,
collect and readout layouts the runner and --fetch-readout write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tempfile
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import ibm_account  # noqa: E402
from diagnostic_experiments import (  # noqa: E402
    N21_FAMILIES,
    STATE_PREP_FAMILY,
    STATE_PREP_HISTORY_ARM,
    state_prep_excitation,
)

SCHEMA = "state-prep-excess-v2"
OUTPUT_NAME = "state-prep-excess.json"
READOUT_SCHEMA = "state-prep-readout-v1"
READOUT_NAME = "state-prep-readout.json"
RESULT_METADATA = "result_metadata.json"
SHORT_DELAY = 5e-05
LONG_DELAY = 2.5e-04
DELAY_LABELS = {SHORT_DELAY: "50us", LONG_DELAY: "250us"}
DEFAULT_ALPHA = 0.01
# The x_history fraction at each delay and prep0 at 250 us enter the rule.
REQUIRED_CELLS = ((STATE_PREP_HISTORY_ARM, SHORT_DELAY), (STATE_PREP_HISTORY_ARM, LONG_DELAY), ("prep0", LONG_DELAY))
READOUT_FIELDS = (
    "prob_meas1_prep0",
    "prob_meas0_prep1",
    "x_error",
    "x_duration_seconds",
    "measure_duration_seconds",
    "T1_seconds",
)


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
    require(math.isfinite(float(value)) and float(value) >= 0.0, f"{where}: repetition delay {value} s")
    for delay in DELAY_LABELS:
        if math.isclose(float(value), delay, rel_tol=1e-9, abs_tol=0.0):
            return delay
    return float(value)


def _label(delay: float) -> str:
    """The cell key for a delay: the named label at 50 and 250 us, else the delay's shortest round-trip repr in seconds.

    repr round-trips every float, so two distinct delays never share a key
    and no cell overwrites another in the label-keyed tables.
    """
    return DELAY_LABELS.get(delay) or f"{delay!r}s"


def rule_cells(delay: float) -> tuple[tuple[tuple[str, float], ...], tuple[float, ...], float]:
    """The control cells the rule bounds for a plan at delay, the x_history delays among them and prep0's delay.

    A plan at 50 or 250 us takes the two-delay rule; a plan at any other
    delay D takes x_history upper and prep0 lower at D alone.
    """
    if delay in DELAY_LABELS:
        return REQUIRED_CELLS, (SHORT_DELAY, LONG_DELAY), LONG_DELAY
    return ((STATE_PREP_HISTORY_ARM, delay), ("prep0", delay)), (delay,), delay


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"{path} lies outside {root}") from error


def _instant(stamp: Any, where: str) -> datetime:
    require(isinstance(stamp, str), f"{where}: no calibration stamp")
    moment = datetime.fromisoformat(stamp)
    require(moment.tzinfo is not None, f"{where}: calibration stamp {stamp} carries no UTC offset")
    return moment


def _utc(stamp: Any) -> str:
    return _instant(stamp, "calibration").astimezone(UTC).isoformat()


def _member_qubit(member: str) -> tuple[str, int]:
    require(member.startswith("spc_") and "_q" in member, f"{member}: not a state-prep member")
    arm, qubit_text = member.removeprefix("spc_").rsplit("_q", 1)
    return arm, int(qubit_text)


def _executions(run_dir: Path) -> tuple[bytes, dict[str, dict[str, Any]]]:
    """collect.json's bytes and its per-member execution record (PUB, window, calibration)."""
    data = (run_dir / "collect.json").read_bytes()
    entries = json.loads(data)
    require(isinstance(entries, list) and bool(entries), f"{run_dir}/collect.json: not a collection")
    executed: dict[str, dict[str, Any]] = {}
    for entry in entries[1:]:
        for member, execution in (entry.get("executed") or {}).items():
            require(executed.setdefault(member, execution) == execution, f"{run_dir}: {member} executed twice")
    return data, executed


def _pub_windows(job: dict[str, Any], manifest: dict[str, Any], executed: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The one execution window and calibration every member of a fused PUB shares."""
    where = f"job {job['job_id']} PUB {manifest['name']}"
    windows = set()
    for component in manifest["components"]:
        execution = executed.get(str(component["member"]))
        if execution is None:
            raise ValueError(f"{where}: collect.json records no execution of {component['member']}")
        require(execution.get("pub") == manifest["name"], f"{where}: {component['member']} ran in another PUB")
        require(
            execution.get("start") is not None and execution.get("calibration") is not None,
            f"{where}: no execution window, so the readout in force is unknown "
            f"({execution.get('window_unavailable_reason')})",
        )
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


def _pub_segments(raw: Path, index: dict[str, Any], count: int) -> list[int]:
    """Execution chunks holding each PUB's shots, from the executor's chunk_timing in result_metadata.json.

    A PUB's shots run in sequence inside a chunk, so the first shot of each
    chunk follows a shot of another PUB or job rather than one of its own.
    """
    require(RESULT_METADATA in index.get("files", {}), f"{raw}: index.json lacks {RESULT_METADATA}")
    data = (raw / RESULT_METADATA).read_bytes()
    require(sha256_bytes(data) == index["files"][RESULT_METADATA], f"{raw / RESULT_METADATA}: sha256 differs")
    chunks = (json.loads(data).get("executor") or {}).get("chunk_timing")
    if not chunks:
        raise ValueError(f"{raw / RESULT_METADATA}: no executor chunk_timing, so segment starts are unknown")
    segments = [0] * count
    for chunk in chunks:
        for item in {int(part["idx_item"]) for part in chunk["parts"]}:
            require(0 <= item < count, f"{raw / RESULT_METADATA}: chunk names PUB {item} of {count}")
            segments[item] += 1
    require(all(segments), f"{raw / RESULT_METADATA}: a PUB lies in no chunk")
    return segments


def read_control(run_dir: Path, root: Path) -> dict[str, Any]:
    """Per-qubit counts, shot-ordered bits and execution readout of one collected state-prep-control run.

    record.json's submission names each job, its options and its PUB
    manifests; a manifest component maps a member spc_<arm>_q<qubit> on its
    one physical qubit to a one-bit register of the PUB file. Every PUB file
    must carry the sha256 index.json recorded for it, every PUB must carry
    the execution window collect.json recorded, and state-prep-readout.json
    must name these record and collect bytes and hold the readout fetched at
    that window's calibration.
    """
    record_bytes = (run_dir / "record.json").read_bytes()
    record = json.loads(record_bytes)
    configuration = record.get("family_configuration") or {}
    require(configuration.get("name") == STATE_PREP_FAMILY, f"{run_dir}: not a state-prep-control record")
    arms = list(configuration.get("arms") or ())
    require(bool(arms), f"{run_dir}: the record names no arms")
    jobs = (record.get("submission") or {}).get("jobs") or []
    require(bool(jobs), f"{run_dir}: the record holds no submitted job")
    collect_bytes, executed = _executions(run_dir)
    readout_path = run_dir / READOUT_NAME
    require(readout_path.is_file(), f"{run_dir}: no {READOUT_NAME}; run --fetch-readout {run_dir}")
    readout_bytes = readout_path.read_bytes()
    readout = json.loads(readout_bytes)
    require(readout.get("schema") == READOUT_SCHEMA, f"{readout_path}: schema {readout.get('schema')}")
    require(
        readout.get("record_sha256") == sha256_bytes(record_bytes)
        and readout.get("collect_sha256") == sha256_bytes(collect_bytes),
        f"{readout_path}: fetched for other record or collect bytes",
    )
    fetched = {
        (str(window["job_id"]), str(window["pub"]), str(window["edge"])): window for window in readout["windows"]
    }
    policy_delay = (record.get("policy") or {}).get("rep_delay_seconds")
    counts: dict[str, dict[int, list[int]]] = {}
    bits: dict[str, dict[int, tuple[str, str]]] = {}
    readouts: dict[str, dict[int, list[dict[str, Any]]]] = {}
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
            _member_qubit(str(component["member"]))[0]
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
        segments = _pub_segments(raw, index, len(job["pubs"]))
        raw_digests[_relative(raw / RESULT_METADATA, root)] = index["files"][RESULT_METADATA]
        for position, manifest in enumerate(job["pubs"]):
            window = _pub_windows(job, manifest, executed)
            edges = ["start", "stop"] if window["changed"] else ["start"]
            pub_readouts = []
            for edge in edges:
                key = (job_id, str(manifest["name"]), edge)
                require(key in fetched, f"{readout_path}: no readout at the {edge} of {manifest['name']}")
                entry = fetched[key]
                require(entry.get("at") == window[edge], f"{readout_path}: {key} fetched at another instant")
                if edge == "start":
                    require(
                        _instant(entry.get("calibration"), str(key)) == _instant(window["calibration"], str(key)),
                        f"{readout_path}: {key} calibration {entry.get('calibration')} differs from the "
                        f"{window['calibration']} collect replayed under",
                    )
                pub_readouts.append(entry)
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
                arm, qubit = _member_qubit(member)
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
                require(segments[position] < shots, f"{member}: {segments[position]} segments for {shots} shots")
                cell[qubit] = [ones, shots, segments[position]]
                bits.setdefault(arm, {})[qubit] = (f"{job_id}/{manifest['name']}", "".join(bitstrings))
                values = []
                for entry in pub_readouts:
                    qubit_values = (entry.get("qubits") or {}).get(str(qubit))
                    if qubit_values is None:
                        raise ValueError(f"{readout_path}: no readout of q{qubit} at {entry['edge']}")
                    require(
                        all(isinstance(qubit_values.get(field), (int, float)) for field in READOUT_FIELDS),
                        f"{readout_path}: q{qubit} lacks one of {READOUT_FIELDS}",
                    )
                    values.append({"calibration": entry["calibration"], **{f: qubit_values[f] for f in READOUT_FIELDS}})
                readouts.setdefault(arm, {})[qubit] = values
    require(len(delays) == 1 and len(backends) == 1, f"{run_dir}: jobs span delays {delays} or backends {backends}")
    return {
        "path": _relative(run_dir, root),
        "record_sha256": sha256_bytes(record_bytes),
        "collect_sha256": sha256_bytes(collect_bytes),
        "readout_sha256": sha256_bytes(readout_bytes),
        "raw_sha256": raw_digests,
        "backend": backends.pop(),
        "rep_delay_seconds": delays.pop(),
        "arms": arms,
        "job_ids": sorted(str(job["job_id"]) for job in jobs),
        "planning_calibrations": sorted({str(group.get("calibration")) for group in record.get("groups", [])}),
        "counts": counts,
        "bits": bits,
        "readouts": readouts,
    }


def fetch_readout(run_dir: Path) -> Path:
    """Retain the readout, x error, x duration and T1 in force at each control PUB's execution window.

    Reads the IBM service (calibration reads need no approval) and writes
    state-prep-readout.json; read_control binds its stamps to collect.json.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    from live_run import readout_flips

    record_bytes = (run_dir / "record.json").read_bytes()
    record = json.loads(record_bytes)
    collect_bytes, executed = _executions(run_dir)
    service = ibm_account.open_service(QiskitRuntimeService)
    windows = []
    for job in (record.get("submission") or {}).get("jobs") or []:
        backend = service.backend(str(job["backend"]))
        for manifest in job["pubs"]:
            window = _pub_windows(job, manifest, executed)
            qubits = sorted({_member_qubit(str(component["member"]))[1] for component in manifest["components"]})
            for edge in ["start", "stop"] if window["changed"] else ["start"]:
                props = backend.properties(datetime=_instant(window[edge], f"{manifest['name']} {edge}"))
                calibration = props.last_update_date.isoformat()
                if edge == "start":
                    require(
                        _instant(calibration, "fetched") == _instant(window["calibration"], "collect"),
                        f"{manifest['name']}: properties at {window['start']} read calibration {calibration}, "
                        f"collect replayed under {window['calibration']}",
                    )
                else:
                    require(
                        _instant(calibration, "fetched") != _instant(window["calibration"], "collect"),
                        f"{manifest['name']}: collect records a calibration change the stop fetch does not show",
                    )
                values = {}
                for qubit in qubits:
                    e10, e01 = readout_flips(props, qubit)
                    values[str(qubit)] = {
                        "prob_meas1_prep0": float(e10),
                        "prob_meas0_prep1": float(e01),
                        "x_error": float(props.gate_error("x", qubit)),
                        "x_duration_seconds": float(props.gate_length("x", qubit)),
                        "measure_duration_seconds": float(props.readout_length(qubit)),
                        "T1_seconds": float(props.t1(qubit)),
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
        "schema": READOUT_SCHEMA,
        "record_sha256": sha256_bytes(record_bytes),
        "collect_sha256": sha256_bytes(collect_bytes),
        "windows": windows,
    }
    destination = run_dir / READOUT_NAME
    destination.write_bytes(encode(payload))
    return destination


def read_placement(record_path: Path, root: Path) -> dict[str, Any]:
    """Placed qubits, their model readout calibration, the plan's delay and the excitation it was planned with."""
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


def _round_up(value: float) -> float:
    """value rounded up to a multiple of 1e-6, never below value, so the next plan covers it."""
    rounded = math.ceil(value * 1e6) / 1e6
    while rounded < value:
        rounded += 1e-6
    return rounded


def coincidence(by_qubit: dict[int, tuple[str, str]], qubits: list[int]) -> dict[str, Any]:
    """Shots in which two or more of qubits read 1, beside the count independent point marginals predict."""
    pubs = {by_qubit[q][0] for q in qubits}
    if len(pubs) != 1:
        return {"scope": "placed members span PUBs, whose shot orders are unrelated", "pubs": sorted(pubs)}
    matrix = np.stack([np.frombuffer(by_qubit[q][1].encode(), dtype=np.uint8) - ord("0") for q in qubits])
    shots = int(matrix.shape[1])
    marginals = matrix.mean(axis=1)
    if np.any(marginals >= 1.0):
        return {"scope": "a placed qubit read 1 in every shot", "pubs": sorted(pubs)}
    none = float(np.prod(1.0 - marginals))
    single = none * float(np.sum(marginals / (1.0 - marginals)))
    multiple = int(np.count_nonzero(matrix.sum(axis=0) >= 2))
    return {
        "pub": pubs.pop(),
        "shots": shots,
        "multiple_ones_shots": multiple,
        "independent_expected_shots": shots * (1.0 - none - single),
    }


def excess(placement: dict[str, Any], controls: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    """The rule's per-qubit bounds and eps on placement S, and the fixed-point step for its plan."""
    require(0.0 < alpha < 1.0, f"alpha {alpha} lies outside (0, 1)")
    cells: dict[tuple[str, float], dict[int, list[int]]] = {}
    cell_bits: dict[tuple[str, float], dict[int, tuple[str, str]]] = {}
    cell_readouts: dict[tuple[str, float], dict[int, list[dict[str, Any]]]] = {}
    for control in controls:
        require(control["backend"] == placement["backend"], f"{control['path']}: runs on {control['backend']}")
        delay = control["rep_delay_seconds"]
        for arm, by_qubit in control["counts"].items():
            cell = cells.setdefault((arm, delay), {})
            for qubit, pair in by_qubit.items():
                require(qubit not in cell, f"two control runs read {arm} on q{qubit} at {delay}")
                cell[qubit] = pair
            cell_bits.setdefault((arm, delay), {}).update(control["bits"][arm])
            cell_readouts.setdefault((arm, delay), {}).update(control["readouts"][arm])
    qubits = placement["qubits"]
    target = placement["rep_delay_seconds"]
    required, history_delays, prep0_delay = rule_cells(target)
    legacy = required == REQUIRED_CELLS
    missing = {
        f"{arm}@{_label(delay)}": [q for q in qubits if q not in cells.get((arm, delay), {})] for arm, delay in required
    }
    missing = {cell: absent for cell, absent in missing.items() if absent}
    require(not missing, f"placed qubits lack control data: {missing}")
    controlled = sorted(set.intersection(*(set(cells[cell]) for cell in required)))
    bounds_per_qubit = len(required)
    bound_count = bounds_per_qubit * len(controlled)
    level = alpha / bound_count

    def column(arm: str, delay: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        triples = np.asarray([cells[(arm, delay)][q] for q in qubits], dtype=np.int64)
        return triples[:, 0], triples[:, 1], triples[:, 2]

    # The s segment-leading shots of a PUB follow an uncontrolled shot: an upper bound counts their ones against
    # the n - s controlled shots, and a lower bound removes s ones before it.
    def history_upper(delay: float) -> np.ndarray:
        ones, shots, segments = column(STATE_PREP_HISTORY_ARM, delay)
        return cp_upper(ones, shots - segments, level)

    upper = {delay: history_upper(delay) for delay in history_delays}
    prep0_ones, prep0_shots, prep0_segments = column("prep0", prep0_delay)
    prep0_lower = cp_lower(np.maximum(prep0_ones - prep0_segments, 0), prep0_shots - prep0_segments, level)
    per_qubit: dict[str, Any] = {}
    eps: dict[float, dict[int, float]] = {delay: {} for delay in history_delays}
    for index, qubit in enumerate(qubits):
        model_e10, model_e01 = placement["calibration"][qubit]
        execution = {f"{arm}_{_label(delay)}": cell_readouts[(arm, delay)][qubit] for arm, delay in required}
        e10_floor = min([model_e10] + [v["prob_meas1_prep0"] for values in execution.values() for v in values])
        e01_ceiling = max([model_e01] + [v["prob_meas0_prep1"] for values in execution.values() for v in values])
        flip_failure = max(
            v["x_error"] + (v["x_duration_seconds"] + v["measure_duration_seconds"]) / v["T1_seconds"]
            for (arm, delay) in required
            if arm == STATE_PREP_HISTORY_ARM
            for v in cell_readouts[(arm, delay)][qubit]
        )
        require(0.0 <= flip_failure < 1.0, f"q{qubit}: end-state failure {flip_failure} leaves no |1> history")
        baseline = min(float(prep0_lower[index]), e10_floor)
        row: dict[str, Any] = {
            "model_readout": {"prob_meas1_prep0": model_e10, "prob_meas0_prep1": model_e01},
            "execution_readout": execution,
            "counts": {},
            "bounds": {
                f"prep0_{_label(prep0_delay)}_lower": float(prep0_lower[index]),
                "e10_envelope": e10_floor,
                "e01_envelope": e01_ceiling,
                "baseline": baseline,
                "end_state_failure": flip_failure,
            },
            "history_excitation": {},
            "eps_unclamped": {},
            "eps": {},
        }
        fractions: dict[str, float] = {}
        for (arm, delay), cell in sorted(cells.items()):
            if qubit in cell:
                key = f"{arm}_{_label(delay)}"
                row["counts"][key] = cell[qubit][:2]
                row.setdefault("segments", {})[key] = cell[qubit][2]
                fractions[key] = cell[qubit][0] / cell[qubit][1]
        row["fractions"] = fractions
        for delay in history_delays:
            label = _label(delay)
            bound = float(upper[delay][index])
            row["bounds"][f"x_history_{label}_upper"] = bound
            require(
                bound < 1.0 - e01_ceiling,
                f"q{qubit}: x_history upper bound {bound} at {label} reaches 1 - e01, where eps is not monotone",
            )
            value = state_prep_excitation(bound, baseline, e01_ceiling)
            own = max(0.0, value)
            row["eps_unclamped"][label] = value
            row["history_excitation"][label] = own
            bounded = own / ((1.0 - own) * (1.0 - flip_failure))
            require(
                bounded < 1.0,
                f"q{qubit}: eps {bounded} at {label} lies outside the planner's [0, 1) --prep-excitation domain",
            )
            row["eps"][label] = bounded
            eps[delay][qubit] = bounded
        if legacy and "prep0_50us" in fractions:
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
    control_calibrations = sorted(
        {_utc(v["calibration"]) for arm, delay in required for q in qubits for v in cell_readouts[(arm, delay)][q]}
    )
    plan_calibrations = sorted(_utc(stamp) for stamp in placement["noise_model_calibrations"])
    joint = {
        f"{arm}_{_label(delay)}": coincidence(cell_bits[(arm, delay)], qubits)
        for (arm, delay) in sorted(cells)
        if all(q in cell_bits[(arm, delay)] for q in qubits)
    }
    label = _label(prep0_delay)
    bounds = (
        "one-sided Clopper-Pearson over every controlled qubit: x_history upper at 50 and 250 us, prep0 lower at 250 us"
        if legacy
        else f"one-sided Clopper-Pearson over every controlled qubit: x_history upper and prep0 lower at {label}"
    )
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "rule": {
            "alpha": alpha,
            "bounds_per_qubit": bounds_per_qubit,
            "controlled_qubits": controlled,
            "bound_count": bound_count,
            "alpha_per_bound": level,
            "bounds": bounds,
            "readout": "e10 the smallest and e01 the largest of the n21 model's and every execution calibration's "
            "reported values",
            "eps": f"u / ((1 - u)(1 - delta)), u = max(0, (U - b) / (1 - e01 - b)), b = min(prep0_{label}_lower, e10), "
            "delta = max(x_error + (x_duration + measure_duration) / T1) over the x_history execution calibrations; "
            "each PUB's segment-leading shots are counted at their worst value",
            "joint": "marginal coverage under independent local preparation channels; joint_coincidences is a "
            "diagnostic outside the bound family",
        },
        "inputs": {
            "n21_record": {key: placement[key] for key in placement if key not in ("calibration", "qubits")},
            "controls": sorted(
                (
                    {key: value for key, value in control.items() if key not in ("counts", "bits", "readouts")}
                    for control in controls
                ),
                key=lambda control: str(control["path"]),
            ),
        },
        "placement": {"qubits": qubits, "rep_delay_seconds": placement["rep_delay_seconds"]},
        "qubits": per_qubit,
        "joint_coincidences": joint,
        "calibration_scope": {
            "control_execution_calibrations": control_calibrations,
            "n21_noise_model_calibrations": plan_calibrations,
            "matched": set(plan_calibrations) <= set(control_calibrations),
            "scope": "eps bounds the initialization at the control's execution calibrations; applying it to the "
            "n21 plan assumes that initialization channel unchanged until the n21 shots run",
        },
        "fixed_point": {
            "planned_prep_excitation": planned,
            "measured_at_plan_delay": measured,
            "verdict": "converged" if converged else "replan",
            "next_prep_excitation": planned if converged else max(planned, _round_up(measured)),
        },
    }
    if legacy:
        result["eps50"] = maxima[SHORT_DELAY]
        result["eps250"] = maxima[LONG_DELAY]
        result["argmax50"] = [q for q in qubits if eps[SHORT_DELAY][q] == maxima[SHORT_DELAY]]
        result["argmax250"] = [q for q in qubits if eps[LONG_DELAY][q] == maxima[LONG_DELAY]]
    else:
        result["rule"]["target_delay_seconds"] = target
        result["eps_target"] = maxima[target]
        result["argmax_target"] = [q for q in qubits if eps[target][q] == maxima[target]]
    return result


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


# scipy.stats.beta.ppf inverts the incomplete beta through Boost, whose last
# bits differ between scipy builds of one version (a distribution package
# against the pip wheel CI installs): about 1e-15 relative on the bounds.
REPLAY_REL_TOL = 1e-12


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


def check(root: Path) -> int:
    """Recompute every retained output under results/live from the inputs it names and compare it.

    Strings, integers, verdicts and qubit lists compare exactly; floats
    compare within REPLAY_REL_TOL, the build-to-build spread of beta.ppf.
    """
    retained = sorted((root / "results" / "live").glob(f"*/{OUTPUT_NAME}"))
    for output in retained:
        payload = json.loads(output.read_bytes())
        inputs = payload["inputs"]
        recomputed = json.loads(
            encode(
                evaluate(
                    root / inputs["n21_record"]["path"],
                    [root / control["path"] for control in inputs["controls"]],
                    float(payload["rule"]["alpha"]),
                    root,
                )
            )
        )
        mismatch = _replay_mismatch(payload, recomputed)
        require(mismatch is None, f"{output}: the replay differs from the retained output at {mismatch or '/'}")
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


SYNTHETIC_CALIBRATION = "2026-01-01T00:00:00+00:00"
SYNTHETIC_START = "2026-01-01T00:10:00+00:00"
SYNTHETIC_STOP = "2026-01-01T00:11:00+00:00"


def _synthetic_run(
    root: Path,
    name: str,
    arm: str,
    delay: float,
    counts: dict[int, tuple[int, int]],
    readout: dict[int, dict[str, float]],
    twirl: bool = False,
    companion: str | None = None,
    staggered: bool = False,
    changed: bool = False,
    fetched_calibration: str = SYNTHETIC_CALIBRATION,
    chunks: int = 1,
) -> Path:
    """A collected run directory in live_run's raw and collect layouts with its fetched readout sidecar.

    One job and one PUB hold a one-bit register per qubit and arm; the ones
    of every qubit lead its shot order, or follow one another without
    overlap when staggered. companion adds a second arm's members, with the
    same counts, to the same PUB. changed records a calibration change
    during the shots, and the sidecar then carries the stop fetch too;
    chunks sets how many executor chunks hold the PUB's shots.
    """
    run = root / "results" / "live" / name
    raw = run / "raw" / f"job_{name}"
    raw.mkdir(parents=True)
    arms = [arm] if companion is None else [arm, companion]
    kind = "dynamic" if arm == STATE_PREP_HISTORY_ARM else "static"
    pub_name = f"fake_backend_{kind}_pub_01"
    components = []
    registers: dict[str, Any] = {}
    executed: dict[str, Any] = {}
    offset = 0
    for index, (member_arm, (qubit, (ones, shots))) in enumerate(
        (member_arm, item) for member_arm in arms for item in sorted(counts.items())
    ):
        register = f"g{index}_r0_c"
        member = f"spc_{member_arm}_q{qubit}"
        components.append(
            {
                "group": f"state_prep_q{qubit}",
                "member": member,
                "reference": False,
                "register_prefix": f"g{index}_",
                "physical_qubits": [qubit],
                "registers_by_replica": [[register]],
            }
        )
        lead = offset if staggered else 0
        offset += ones
        bitstrings = ["0"] * lead + ["1"] * ones + ["0"] * (shots - ones - lead)
        registers[register] = {"num_bits": 1, "num_shots": shots, "bitstrings": bitstrings}
        executed[member] = {
            "pub": pub_name,
            "start": SYNTHETIC_START,
            "stop": SYNTHETIC_STOP,
            "calibration": SYNTHETIC_CALIBRATION,
            "calibration_changed_during_shots": changed,
            "window_unavailable_reason": None,
            "shots": shots,
        }
    pub = encode({"pub_index": 0, "pub_name": pub_name, "registers": registers, "metadata": {}})
    (raw / "pub_00.json").write_bytes(pub)
    chunk = {"parts": [{"idx_item": 0, "size": 1}], "start": SYNTHETIC_START, "stop": SYNTHETIC_STOP}
    metadata = encode({"executor": {"chunk_timing": [chunk] * chunks}})
    (raw / RESULT_METADATA).write_bytes(metadata)
    files = {"pub_00.json": sha256_bytes(pub), RESULT_METADATA: sha256_bytes(metadata)}
    (raw / "index.json").write_bytes(encode({"job_id": f"job_{name}", "files": files}))
    record = {
        "family_configuration": {
            "name": STATE_PREP_FAMILY,
            "qubits": sorted(counts),
            "arms": {member_arm: "steps" for member_arm in arms},
        },
        "policy": {"rep_delay_seconds": delay, "twirl": twirl},
        "groups": [{"backend": "fake_backend", "calibration": SYNTHETIC_CALIBRATION}],
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
    record_bytes = encode(record)
    (run / "record.json").write_bytes(record_bytes)
    collect_bytes = encode([{"jobs": {}}, {"group": "state_prep", "job_id": f"job_{name}", "executed": executed}])
    (run / "collect.json").write_bytes(collect_bytes)
    qubit_values = {str(q): readout[q] for q in sorted(counts)}
    windows = [
        {
            "job_id": f"job_{name}",
            "pub": pub_name,
            "edge": edge,
            "at": at,
            "calibration": calibration,
            "qubits": qubit_values,
        }
        for edge, at, calibration in (
            [("start", SYNTHETIC_START, fetched_calibration)]
            + ([("stop", SYNTHETIC_STOP, "2026-01-01T00:10:30+00:00")] if changed else [])
        )
    ]
    sidecar = {
        "schema": READOUT_SCHEMA,
        "record_sha256": sha256_bytes(record_bytes),
        "collect_sha256": sha256_bytes(collect_bytes),
        "windows": windows,
    }
    (run / READOUT_NAME).write_bytes(encode(sidecar))
    return run


def _synthetic_placement(
    root: Path,
    qubits: list[int],
    calibration: dict[int, tuple[float, float]],
    planned: float | None,
    delay: float = SHORT_DELAY,
) -> Path:
    run = root / "results" / "live" / "n21-plan"
    run.mkdir(parents=True)
    record = {
        "family_configuration": {"name": "n21-feedback-encoded"},
        "experiment_digest": "0" * 64,
        "policy": {"design": {} if planned is None else {"prep_excitation": planned}, "rep_delay_seconds": delay},
        "execution_contract": {"backends": [{"name": "fake_backend", "repetition_delay_seconds": delay}]},
        "groups": [
            {
                "backend": "fake_backend",
                "noise_model_calibration": SYNTHETIC_CALIBRATION,
                "replicas": [{"physical_qubits": qubits}],
                "placed_qubit_calibration": {
                    str(q): {"prob_meas1_prep0": calibration[q][0], "prob_meas0_prep1": calibration[q][1]}
                    for q in qubits
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
    # Delays that agree to six significant digits keep distinct cell keys.
    require(_label(2e-05) != _label(2.0000001e-05), "delay labels collide")
    require(_label(SHORT_DELAY) == "50us" and _label(LONG_DELAY) == "250us", "named delay labels moved")
    # Clopper-Pearson bounds against an independent binomial-tail inversion.
    cases = [(0, 50), (3, 50), (50, 50), (0, 4096), (109, 4096), (4096, 4096), (281, 32768), (1500, 16384)]
    for level in (0.01 / 453, 0.05):
        for k, n in cases:
            upper = float(cp_upper([k], [n], level)[0])
            lower = float(cp_lower([k], [n], level)[0])
            reference_upper = 1.0 if k == n else _bisect(lambda p, k=k, n=n: _binomial_cdf(k, n, p), level)
            reference_lower = 0.0 if k == 0 else _bisect(lambda p, k=k, n=n: _binomial_cdf(k - 1, n, p), 1.0 - level)
            require(abs(upper - reference_upper) <= 1e-9, f"upper bound {k}/{n}: {upper} vs {reference_upper}")
            require(abs(lower - reference_lower) <= 1e-9, f"lower bound {k}/{n}: {lower} vs {reference_lower}")
            require(lower <= k / n <= upper, f"{k}/{n}: bounds exclude the fraction")
    placed = [3, 4, 7]
    calibration: dict[int, tuple[float, float]] = {3: (0.0098, 0.0146), 4: (0.0200, 0.0259), 7: (0.0049, 0.0122)}
    # q9 is controlled but unplaced: it widens C, and with it the bound count, without entering eps.
    base = {
        "history50": {3: (300, 32768), 4: (900, 32768), 7: (150, 32768), 9: (200, 32768)},
        "history250": {3: (120, 16384), 4: (400, 16384), 7: (60, 16384), 9: (90, 16384)},
        "prep0_250": {3: (150, 16384), 4: (430, 16384), 7: (70, 16384), 9: (100, 16384)},
    }
    nominal = {"x_error": 2e-4, "x_duration_seconds": 3.6e-8, "measure_duration_seconds": 1.56e-6, "T1_seconds": 2e-4}
    readout_base = {
        q: {"prob_meas1_prep0": e10, "prob_meas0_prep1": e01, **nominal}
        for q, (e10, e01) in {**calibration, 9: (0.006, 0.012)}.items()
    }

    roots = (scratch / str(index) for index in range(1000))

    def run(
        overrides: dict[str, dict[int, tuple[int, int]]] | None = None,
        cal: dict[int, tuple[float, float]] | None = None,
        planned: float | None = None,
        prep0_50: dict[int, tuple[int, int]] | None = None,
        readout: dict[str, dict[int, dict[str, float]]] | None = None,
        twirl: bool = False,
        companion: str | None = None,
        staggered: bool = False,
        changed: bool = False,
        fetched_calibration: str = SYNTHETIC_CALIBRATION,
        chunks: int = 1,
    ) -> tuple[Path, dict[str, Any]]:
        sets = {**base, **(overrides or {})}
        reads = {name: readout_base for name in ("history50", "history250", "prep0_250", "prep0_50")}
        reads.update(readout or {})
        root = next(roots)
        record = _synthetic_placement(root, placed, cal or calibration, planned)
        controls = [
            _synthetic_run(
                root,
                "h50",
                STATE_PREP_HISTORY_ARM,
                SHORT_DELAY,
                sets["history50"],
                reads["history50"],
                twirl,
                staggered=staggered,
                changed=changed,
                fetched_calibration=fetched_calibration,
                chunks=chunks,
            ),
            _synthetic_run(root, "h250", STATE_PREP_HISTORY_ARM, LONG_DELAY, sets["history250"], reads["history250"]),
            _synthetic_run(
                root, "p250", "prep0", LONG_DELAY, sets["prep0_250"], reads["prep0_250"], companion=companion
            ),
        ]
        if prep0_50 is not None:
            controls.append(_synthetic_run(root, "p50", "prep0", SHORT_DELAY, prep0_50, reads["prep0_50"]))
        return root, evaluate(record, controls, DEFAULT_ALPHA, root)

    root, result = run()
    rule = result["rule"]
    require(rule["controlled_qubits"] == [3, 4, 7, 9], f"controlled set {rule['controlled_qubits']}")
    require(rule["bound_count"] == 12, f"bound count {rule['bound_count']} for 4 controlled qubits")
    require(math.isclose(rule["alpha_per_bound"] * 12, DEFAULT_ALPHA), "the alpha split moved")
    require(result["eps50"] == max(row["eps"]["50us"] for row in result["qubits"].values()), "eps50 is not the max")
    require("9" not in result["qubits"], "an unplaced controlled qubit entered eps")
    require(result["argmax50"] == [4], f"arg-max {result['argmax50']}")
    require(result["eps50"] > result["eps250"] > 0, "the synthetic history excess vanished")
    # The CLI path writes, and the replay reproduces the bytes.
    destination = write(
        root / "results/live/n21-plan/record.json", sorted((root / "results/live").glob("[hp]*")), DEFAULT_ALPHA, root
    )
    require(destination.name == OUTPUT_NAME and check(root) == 1, "the replay found no retained output")
    # A last-bit float change replays; a change past the build tolerance, or in a verdict, refuses.
    pristine = destination.read_bytes()
    for nudge, accepted in ((1.0 + 1e-15, True), (1.0 + 1e-9, False)):
        payload = json.loads(pristine)
        payload["eps50"] *= nudge
        destination.write_bytes(encode(payload))
        if accepted:
            require(check(root) == 1, "a last-bit float change refused the replay")
        else:
            _expect_refusal(lambda: check(root), "at /eps50")
    payload = json.loads(pristine)
    payload["fixed_point"]["verdict"] = "replan" if payload["fixed_point"]["verdict"] == "converged" else "converged"
    destination.write_bytes(encode(payload))
    _expect_refusal(lambda: check(root), "at /fixed_point/verdict")
    destination.write_bytes(pristine)
    raw = root / "results/live/h50/raw/job_h50/pub_00.json"
    raw.write_bytes(raw.read_bytes().replace(b'"0"', b'"1"', 1))
    _expect_refusal(lambda: check(root), "sha256 differs")
    # A wider controlled set divides alpha further and raises every upper bound.
    narrow = run({name: {q: c for q, c in cells.items() if q != 9} for name, cells in base.items()})[1]
    require(narrow["rule"]["bound_count"] == 9, f"narrow bound count {narrow['rule']['bound_count']}")
    require(result["eps50"] > narrow["eps50"], "the wider controlled set left eps unchanged")
    # The history correction: eps = u / ((1 - u)(1 - delta)) exceeds the arm's own excitation and rises with delta.
    reference = result["qubits"]["4"]
    own, delta = reference["history_excitation"]["50us"], reference["bounds"]["end_state_failure"]
    require(math.isclose(delta, 2e-4 + (3.6e-8 + 1.56e-6) / 2e-4), f"end-state failure {delta}")
    require(reference["eps"]["50us"] == own / ((1.0 - own) * (1.0 - delta)) > own, "the history correction moved")
    slow = {q: {**values, "T1_seconds": 5e-5} for q, values in readout_base.items()}
    require(run(readout={"history50": slow})[1]["eps50"] > result["eps50"], "a larger delta left eps unchanged")
    # Monotonicity on q4, whose e10 envelope sets the baseline: eps rises with the history fraction, with e01 in
    # either calibration and with a lower e10 in either, falls when e10 rises in every calibration, and rises when
    # a lower prep0 bound takes over the baseline.
    require(reference["bounds"]["baseline"] == reference["bounds"]["e10_envelope"] == 0.0200, "baseline source")
    lower_e10 = {**readout_base, 4: {**readout_base[4], "prob_meas1_prep0": 0.0150}}
    higher_e10 = {**readout_base, 4: {**readout_base[4], "prob_meas1_prep0": 0.0215}}
    higher_e01 = {**readout_base, 4: {**readout_base[4], "prob_meas0_prep1": 0.0400}}
    everywhere = {name: higher_e10 for name in ("history50", "history250", "prep0_250")}
    for label, outcome, sign in (
        ("history fraction", run({"history50": {**base["history50"], 4: (950, 32768)}}), 1),
        ("model e10 (lowered)", run(cal={**calibration, 4: (0.0150, 0.0259)}), 1),
        ("e10 in every calibration", run(cal={**calibration, 4: (0.0215, 0.0259)}, readout=everywhere), -1),
        ("model e01", run(cal={**calibration, 4: (0.0200, 0.0400)}), 1),
        ("execution e01", run(readout={"prep0_250": higher_e01}), 1),
        ("execution e10 (lowered)", run(readout={"history250": lower_e10}), 1),
        ("prep0 baseline", run({"prep0_250": {**base["prep0_250"], 4: (200, 16384)}}), 1),
    ):
        shifted = outcome[1]["qubits"]["4"]
        moved = shifted["eps"]["50us"] - reference["eps"]["50us"]
        require(moved * sign > 0, f"changing the {label} moved eps by {moved}")
    require(shifted["bounds"]["baseline"] == shifted["bounds"]["prep0_250us_lower"], "prep0 left the baseline")
    # Clamping: a qubit with no history excitation reads eps 0 from a negative value.
    clamped = run({"history50": {**base["history50"], 7: (0, 32768)}})[1]["qubits"]["7"]
    require(clamped["eps"]["50us"] == 0.0 and clamped["eps_unclamped"]["50us"] < 0, "eps was not clamped at 0")
    # prep0 at 50 us is reported and leaves the rule unchanged.
    reported = run(prep0_50={3: (160, 32768), 4: (450, 32768), 7: (80, 32768), 9: (100, 32768)})[1]
    require(reported["eps50"] == result["eps50"] and reported["eps250"] == result["eps250"], "prep0 50 us moved eps")
    require("decomposition" in reported["qubits"]["4"] and "decomposition" not in result["qubits"]["4"], "report")
    # Joint diagnostic: ones that lead every qubit's shot order coincide; staggered ones never do.
    aligned = result["joint_coincidences"]["x_history_50us"]
    require(aligned["multiple_ones_shots"] == 300 > aligned["independent_expected_shots"], f"aligned {aligned}")
    apart = run(staggered=True)[1]["joint_coincidences"]["x_history_50us"]
    require(apart["multiple_ones_shots"] == 0 < apart["independent_expected_shots"], f"staggered {apart}")
    require(run(staggered=True)[1]["eps50"] == result["eps50"], "the joint diagnostic moved eps")
    # Segment-leading shots: more executor chunks leave fewer controlled shots and raise the upper bound.
    require(result["qubits"]["4"]["segments"]["x_history_50us"] == 1, "one chunk reads as one segment")
    require(run(chunks=8)[1]["eps50"] > result["eps50"], "more segment starts left eps unchanged")
    _expect_refusal(lambda: run(chunks=0), "segment starts are unknown")
    # Calibration scope: the synthetic plan shares the controls' execution calibration.
    scope = result["calibration_scope"]
    require(scope["matched"] and scope["control_execution_calibrations"] == ["2026-01-01T00:00:00+00:00"], f"{scope}")
    # A calibration change during the shots adds the stop readout to the envelope.
    require(run(changed=True)[1]["qubits"]["4"]["execution_readout"]["x_history_50us"][1]["calibration"], "stop")
    # Fixed point: below the planned value the plan stands; above it the next plan rises, rounded up.
    step = result["fixed_point"]
    require(step["verdict"] == "replan" and step["next_prep_excitation"] >= result["eps50"], f"{step}")
    stays = run(planned=0.5)[1]["fixed_point"]
    require(stays["verdict"] == "converged" and stays["next_prep_excitation"] == 0.5, f"{stays}")
    # Refusals: a placed qubit without control data, twirled readout, prep0 sharing its job with x, a saturated
    # bound, readout fetched under another calibration, a missing or stale sidecar.
    _expect_refusal(lambda: run({"history250": {3: (120, 16384), 4: (400, 16384)}}), "lack control data")
    _expect_refusal(lambda: run(twirl=True), "twirling")
    _expect_refusal(lambda: run(companion="x"), "share one job")
    _expect_refusal(lambda: run({"history50": {**base["history50"], 3: (32700, 32768)}}), "not monotone")
    _expect_refusal(lambda: run(fetched_calibration="2026-01-01T00:05:00+00:00"), "collect replayed under")
    _expect_refusal(lambda: run({"history50": {**base["history50"], 4: (18000, 32768)}}), "planner's [0, 1)")

    # A plan at another delay takes the single-delay rule: x_history upper and prep0 lower at that delay alone.
    def single(with_prep0: bool = True, extra: bool = False) -> tuple[Path, dict[str, Any]]:
        root = next(roots)
        record = _synthetic_placement(root, placed, calibration, None, delay=0.0)
        controls = [_synthetic_run(root, "h0", STATE_PREP_HISTORY_ARM, 0.0, base["history50"], readout_base)]
        if with_prep0:
            controls.append(_synthetic_run(root, "p0", "prep0", 0.0, base["prep0_250"], readout_base))
        if extra:
            controls.append(
                _synthetic_run(root, "h50", STATE_PREP_HISTORY_ARM, SHORT_DELAY, base["history50"], readout_base)
            )
        return root, evaluate(record, controls, DEFAULT_ALPHA, root)

    root, zero = single()
    require(zero["rule"]["target_delay_seconds"] == 0.0 and zero["rule"]["bound_count"] == 8, f"{zero['rule']}")
    require("eps50" not in zero and "eps250" not in zero, "the single-delay rule reported the two-delay maxima")
    require(zero["eps_target"] == max(row["eps"]["0.0s"] for row in zero["qubits"].values()), "eps_target")
    require(zero["argmax_target"] == [4], f"arg-max {zero['argmax_target']}")
    require(zero["fixed_point"]["measured_at_plan_delay"] == zero["eps_target"], "fixed point reads another delay")
    require("prep0_0.0s_lower" in zero["qubits"]["4"]["bounds"], "prep0 baseline at the target delay")
    # Fewer bounds share alpha, so the same history counts give a smaller eps than the two-delay rule's eps50.
    require(zero["eps_target"] < result["eps50"], "the single-delay rule spent more alpha than the two-delay rule")
    require(single(extra=True)[1]["eps_target"] == zero["eps_target"], "a control at another delay moved eps")
    _expect_refusal(lambda: single(with_prep0=False), "prep0@0.0s")
    write(
        root / "results/live/n21-plan/record.json", sorted((root / "results/live").glob("[hp]*")), DEFAULT_ALPHA, root
    )
    require(check(root) == 1, "the single-delay output does not replay")
    root, _ = run()
    (root / "results/live/h250" / READOUT_NAME).unlink()
    _expect_refusal(lambda: check_inputs(root), f"no {READOUT_NAME}")
    root, _ = run()
    collect = root / "results/live/p250/collect.json"
    collect.write_bytes(collect.read_bytes().replace(b'"shots"', b'"shots_"'))
    _expect_refusal(lambda: check_inputs(root), "other record or collect bytes")
    print(
        "state_prep_excess: Clopper-Pearson bounds match the binomial-tail inversion to 1e-9; 3|C| bounds share "
        "alpha over the controlled set; eps rises with the history fraction, e01 and the x flip failure, falls with "
        "the baseline, takes the readout envelope, clamps at 0; the joint diagnostic and prep0 at 50 us stay "
        "outside the rule; a plan at another delay takes x_history and prep0 at that delay alone; the fixed point "
        "never lowers eps; refusals hold and the replay holds to the build tolerance"
    )


def check_inputs(root: Path) -> dict[str, Any]:
    """Evaluate the synthetic layout under root: its n21 plan against its h50, h250 and p250 runs."""
    live = root / "results/live"
    return evaluate(
        live / "n21-plan/record.json", [live / name for name in ("h50", "h250", "p250")], DEFAULT_ALPHA, root
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--n21-record", type=Path, help="record.json of the n21 plan whose placement S is bounded")
    parser.add_argument("--control", type=Path, action="append", default=[], help="collected control run directory")
    parser.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    parser.add_argument(
        "--fetch-readout",
        type=Path,
        action="append",
        default=[],
        help="collected control run directory whose execution-time readout to fetch and retain",
    )
    parser.add_argument("--check", action="store_true", help="replay every retained output under results/live")
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        return 0
    if arguments.check:
        count = check(ROOT)
        plural = "s" if count != 1 else ""
        print(f"state_prep_excess: {count} retained output{plural} replay within the build tolerance")
        return 0
    if arguments.fetch_readout:
        for run_dir in arguments.fetch_readout:
            print(f"{fetch_readout(run_dir)}: execution readout retained")
        return 0
    if arguments.n21_record is None or not arguments.control:
        parser.error("--n21-record and at least one --control are required")
    destination = write(arguments.n21_record, arguments.control, arguments.alpha, ROOT)
    result = json.loads(destination.read_bytes())
    if "eps_target" in result:
        delay = _label(result["rule"]["target_delay_seconds"])
        print(f"{destination}: eps at {delay} {result['eps_target']:.6g}, {result['fixed_point']}")
    else:
        print(f"{destination}: eps50 {result['eps50']:.6g}, eps250 {result['eps250']:.6g}, {result['fixed_point']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
