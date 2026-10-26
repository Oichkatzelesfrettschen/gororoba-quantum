"""Per-qubit idle multipliers and the readout-crosstalk contrast of an idle_penalty run.

The campaign (gororoba_quantum/idle_penalty.py) places a target T (clbit 0) and a
coupled spectator S (clbit 1) on every replica. Each replica's ordered role map
is its `initial_layout` in the record's group replicas: entry 0 is the physical
qubit behind clbit 0. The members' `replica_qubits` are sorted ownership sets
and carry no role, so the report checks only that both name the same qubits.

Sources. A dry run's noisy predictions (record.json, each replica's `noisy`) or a
collected run's measured laws (collect.json, `measured`, decoded through
law_encoding.dense). A collected block that withholds comparisons, lacks a
summary, ran a member under an unknown window or across a calibration update,
or ran its members under different calibrations is refused: every estimator
here compares PUBs. A collected run also passes the exposure check before any
estimate: the service schedule of each PUB (`metadata.compilation.scheduler_timing`
in raw/, read through scripts/scheduled_idle_replay.py) gives every replica the
same idle sequence, each probe the free-evolution gaps the member plans, and
each readout arm the probe sequence of its quiet Ramsey reference; a schedule
that breaks any of these is refused, because the contrasts assume equal
exposure. Measured multipliers normalize against the calibration in
force at execution start (`executed[member].placed_qubit_calibration`); the
planning calibration normalizes predictions. dt comes from the backend's Target
in docs/evidence/heron_platform/targets.json.

Estimators, each per physical qubit:
- relaxation multiplier kappa_1 = Gamma_1 T1_reported. P1 of the relax ladder
  follows b + a exp(-Gamma_1 t) with b = P1(ground) and a = P1(excited) - b
  from the same job's references; Gamma_1 is the binomial maximum likelihood
  over a grid, its error the inverse Fisher information with the references
  held fixed (a conditional lower bound).
- free and echoed decay multipliers kappa_2* = T2_reported / T2* and
  kappa_2e = T2_reported / T2e: each quadrature is unfolded through the probe's
  assignment references, <Z> = (z - (p0e - p1g)) / (1 - p1g - p0e), the
  visibility is hypot(<X>, <Y>), and ln V = ln A - t / T is fitted by weighted
  least squares over the ladder (A absorbs pulse and preparation loss). Points
  below VISIBILITY_FLOOR leave the fit. The echo-over-free ratio measures how
  much dephasing one echo removes under exponential decay; it identifies no
  noise spectrum.
- readout contrast per probe: the during arm against two quiet references in
  their own PUBs, the after arm and the Ramsey arm at MEAS_DT, as dV and as a
  frequency shift averaged over the idle. The MEAS_DT phase fixes the shift
  modulo 1 / MEAS_DT (25 kHz); the short arm against the Ramsey arm at
  SHORT_MEAS_DT fixes it modulo 100 kHz, and the reported shift is the MEAS_DT
  branch nearest the short-arm value.
- static ZZ per pair: (phi(zz) - phi(ramsey at ZZ_DT)) / (2 pi ZZ_DT dt), modulo
  1 / (ZZ_DT dt), with and without post-selection on S read 1.
- CZ kickback: P(T reads 0) in cz_kick less the excited reference's |1>
  assignment error.

Statistical unit. The two probes of one pair share a coupler, a readout train
and every shot, so readout decisions average each pair's two probes and test
the pair means: a t statistic on n - 1 degrees of freedom and a chi-square of
pair means over their standard errors on n degrees of freedom, each at alpha
CHI2_ALPHA. Shots of one wide PUB are shared across pairs too; the two quiet
references and the null between them guard against a common-mode difference
between PUBs, the dependence this design cannot remove. Medians carry
distribution-free order-statistic 95% intervals.

Preregistered decisions (fixed before any hardware data):
- the self-check passes when, on the dry run's predictions, which Aer draws from
  the reported T1 and T2 with no readout crosstalk, the median kappa_1 and
  kappa_2e lie within SELF_CHECK_TOLERANCE of 1 and no readout decision or
  quiet null reads "present";
- optimistic T1 "present" when the median kappa_1 exceeds 1.5 and its interval
  lies above 1;
- echo gain "present" when the interval of the median kappa_2* / kappa_2e lies
  above 1;
- each readout contrast (during against after, during against Ramsey) reads
  "present" when the pair-mean t statistic passes its CHI2_ALPHA quantile, or
  the chi-square tail falls below CHI2_ALPHA, with the right sign: dephasing
  needs a negative mean, a shift either sign; "absent" when the mean's 95%
  interval lies inside the band ([-0.02, 0.02] in visibility, [-0.5, 0.5] kHz)
  and the chi-square tail exceeds 0.05; otherwise "unresolved";
- a readout decision is "present" when both contrasts read present with one
  sign and the quiet null (after against Ramsey) does not read present,
  "absent" when both contrasts and the null read absent, else "unresolved";
- across two measured runs on one backend at distinct execution calibrations
  (--compare), over the qubits that keep their role and partner, a multiplier
  is "stable" when the per-qubit values correlate at r >= 0.5 and the interval
  of the median second/first ratio lies inside [0.8, 1.25], "drifted" when it
  lies wholly outside, otherwise "unresolved".
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import scheduled_idle_replay  # noqa: E402

import idle_penalty as ip  # noqa: E402
import law_encoding  # noqa: E402

ANALYZER_SOURCES = (
    "scripts/idle_penalty_report.py",
    "gororoba_quantum/idle_penalty.py",
    "gororoba_quantum/law_encoding.py",
    "scripts/scheduled_idle_replay.py",
)
VISIBILITY_FLOOR = 0.06
SELF_CHECK_TOLERANCE = 0.15
CHI2_ALPHA = 1e-3
STABLE_RATIO = (0.8, 1.25)
STABLE_CORRELATION = 0.5
GAMMA_GRID = np.linspace(0.0, 2e5, 4001)


class RefusedAnalysis(ValueError):
    """The inputs cannot support the comparison the report would make."""


def analysis_digest() -> str:
    digest = hashlib.sha256()
    for relative in ANALYZER_SOURCES:
        digest.update(relative.encode())
        digest.update((ROOT / relative).read_bytes())
    return digest.hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _portable(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else resolved.name


def _p1(law: list[float] | np.ndarray, bit: int) -> float:
    return ip.bit_one_probability(np.asarray(law, dtype=float), bit)


def relaxation_rate(p_excited: float, p_ground: float, points: list[tuple[float, float]], shots: int) -> dict[str, Any]:
    """Binomial maximum likelihood of Gamma_1 (1 / s) from (t seconds, P1) points with fixed references."""
    a, b = p_excited - p_ground, p_ground
    if a <= 0.1:
        return {"gamma": None, "reason": f"excited reference contrast {a:.3f} at or below 0.1"}
    t = np.array([point[0] for point in points])
    p = np.array([point[1] for point in points])

    def loglik(gammas: np.ndarray) -> np.ndarray:
        model = np.clip(b + a * np.exp(-np.outer(gammas, t)), 1e-9, 1 - 1e-9)
        return np.asarray(shots * (p * np.log(model) + (1 - p) * np.log(1 - model)).sum(axis=1))

    best = int(np.argmax(loglik(GAMMA_GRID)))
    fine = np.linspace(GAMMA_GRID[max(best - 1, 0)], GAMMA_GRID[min(best + 1, len(GAMMA_GRID) - 1)], 2001)
    gamma = float(fine[int(np.argmax(loglik(fine)))])
    if gamma in (float(GAMMA_GRID[0]), float(GAMMA_GRID[-1])):
        return {"gamma": None, "reason": f"Gamma_1 at the grid boundary {gamma:.3g} 1/s"}
    model = np.clip(b + a * np.exp(-gamma * t), 1e-9, 1 - 1e-9)
    slope = -a * t * np.exp(-gamma * t)
    fisher = float((shots * slope * slope / (model * (1 - model))).sum())
    return {"gamma": gamma, "gamma_se": 1 / math.sqrt(fisher) if fisher > 0 else None}


def unfold(z: float, p1g: float, p0e: float) -> float:
    return (z - (p0e - p1g)) / (1.0 - p1g - p0e)


def _probe_z(law: list[float], probe: int, partner: int | None = None) -> float:
    """<Z> of the probe qubit, or of the probe given its partner read partner (post-selection)."""
    p = np.asarray(law, dtype=float)
    if partner is None:
        return 1.0 - 2.0 * _p1(p, probe)
    other = 1 - probe
    rows = [o for o in range(len(p)) if (o >> other & 1) == partner]
    kept = sum(p[o] for o in rows)
    return float(1.0 - 2.0 * sum(p[o] for o in rows if o >> probe & 1) / kept)


def visibility(
    laws: dict[str, Any],
    stem: str,
    k: int,
    refs: tuple[float, float],
    probe: int = ip.TARGET,
    partner: int | None = None,
) -> tuple[float, float]:
    p1g, p0e = refs
    x = unfold(_probe_z(laws[stem.format(q="x")][k], probe, partner), p1g, p0e)
    y = unfold(_probe_z(laws[stem.format(q="y")][k], probe, partner), p1g, p0e)
    return math.hypot(x, y), math.atan2(y, x)


def visibility_se(shots: int, p1g: float, p0e: float) -> float:
    """Upper bound on one visibility's standard error: var(<Z>) <= 1 / shots per quadrature, unfolded."""
    return 1.0 / (math.sqrt(shots) * (1.0 - p1g - p0e))


def decay_time(points: list[tuple[float, float]], shots: int) -> dict[str, Any]:
    """Weighted least squares of ln V = ln A - t / T over points (t seconds, V) above the floor."""
    kept = [(t, v) for t, v in points if v > VISIBILITY_FLOOR]
    if len(kept) < 2:
        return {"time": None, "reason": f"{len(kept)} points above visibility {VISIBILITY_FLOOR}"}
    t = np.array([point[0] for point in kept])
    lnv = np.log([point[1] for point in kept])
    # var(ln V) ~ var(V) / V^2 with var(V) ~ 1 / shots per quadrature.
    w = np.array([point[1] ** 2 * shots for point in kept])
    design = np.vstack([np.ones_like(t), -t]).T
    cov = np.linalg.inv(design.T @ (w[:, None] * design))
    intercept, rate = cov @ design.T @ (w * lnv)
    residual = lnv - design @ np.array([intercept, rate])
    if rate <= 0:
        return {"time": None, "reason": f"non-decaying fit, rate {rate:.3g} 1/s"}
    return {
        "time": 1.0 / rate,
        "rate": float(rate),
        "rate_se": float(math.sqrt(cov[1, 1])),
        "amplitude": math.exp(intercept),
        "chi2": float((w * residual**2).sum()),
        "dof": len(kept) - 2,
    }


def _phase_khz(during: float, reference: float, idle_dt: int, dt: float) -> float:
    return math.remainder(during - reference, 2 * math.pi) / (2 * math.pi * idle_dt * dt) / 1e3


def unwrap_shift(long_khz: float, short_khz: float, dt: float) -> float:
    """The MEAS_DT branch, long_khz + m / MEAS_DT, nearest the short-window value."""
    period = 1 / (ip.MEAS_DT * dt) / 1e3
    return long_khz + round((short_khz - long_khz) / period) * period


def role_map(group: dict[str, Any]) -> list[tuple[int, int]]:
    """Each replica's (T, S) physical qubits from its initial layout, checked against every member's ownership."""
    roles = [tuple(int(q) for q in replica["initial_layout"]) for replica in group["replicas"]]
    for member in group["members"]:
        for k, owned in enumerate(member["replica_qubits"]):
            if len(roles[k]) != ip.WIDTH or set(owned) != set(roles[k]):
                raise RefusedAnalysis(f"{member['name']} replica {k} owns {owned}, the role map names {roles[k]}")
    return [(role[0], role[1]) for role in roles]


Instances = tuple[tuple[str, int, int], ...]
Gaps = tuple[tuple[str, int], ...]


def _gaps(instances: Instances) -> Gaps:
    """(instruction, idle in dt before the next instruction) for consecutive instances on one qubit."""
    return tuple((a[0], b[1] - a[2]) for a, b in zip(instances, instances[1:], strict=False))


def _probe(name: str) -> int:
    return ip.SPECTATOR if name.startswith(ip.probe_prefix(ip.SPECTATOR)) else ip.TARGET


def planned_idles(name: str) -> dict[int, list[int]]:
    """The nonzero free-evolution gaps, in dt, a member puts on each role it probes."""
    probe = _probe(name)
    arm = name.removeprefix(ip.probe_prefix(probe))
    delay = int(arm.rsplit("_", 1)[1].removesuffix("dt")) if arm.endswith("dt") else 0
    if arm.startswith("relax_"):
        return {ip.TARGET: [delay], ip.SPECTATOR: [delay]}
    if arm.startswith(("zz_", "ramsey_")):
        return {probe: [delay]}
    if arm.startswith("echo_"):
        return {probe: [delay // 2, delay - delay // 2]}
    if arm.startswith(("meas_during_", "meas_after_")):
        return {probe: [ip.MEAS_DT]}
    if arm.startswith("meas_short_"):
        return {probe: [ip.SHORT_MEAS_DT]}
    return {}


def quiet_reference(name: str) -> str | None:
    """The Ramsey member whose probe sequence a readout arm must repeat."""
    head = ip.probe_prefix(_probe(name))
    arm = name.removeprefix(head)
    quadrature = arm.rsplit("_", 1)[-1]
    if arm.startswith(("meas_during_", "meas_after_")):
        return f"{head}ramsey_{quadrature}_{ip.MEAS_DT}dt"
    if arm.startswith("meas_short_"):
        return f"{head}ramsey_{quadrature}_{ip.SHORT_MEAS_DT}dt"
    return None


def reader_train(name: str) -> tuple[int, bool] | None:
    """(intermediate reads, whether they fall inside the probe idle) a readout arm puts on its reader role."""
    arm = name.removeprefix(ip.probe_prefix(_probe(name)))
    if arm.startswith("meas_during_"):
        return ip.MEAS_COUNT, True
    if arm.startswith("meas_after_"):
        return ip.MEAS_COUNT, False
    if arm.startswith("meas_short_"):
        return ip.SHORT_MEAS_COUNT, True
    return None


def _raw_pub_files(run: Path) -> dict[str, Path]:
    jobs = sorted(d for d in (run / "raw").iterdir() if d.is_dir()) if (run / "raw").is_dir() else []
    if len(jobs) != 1:
        raise RefusedAnalysis(f"exposure needs one retained raw job directory, found {len(jobs)}")
    return {json.loads(path.read_text())["pub_name"]: path for path in sorted(jobs[0].glob("pub_*.json"))}


def _instances(rows: list[tuple[str, str, str, int, int, str]], qubit: int) -> Instances:
    return tuple(
        (label.split("_")[0], start, end) for label, start, end in scheduled_idle_replay.instances(rows, qubit)
    )


def schedule_timelines(
    run: Path, executed: dict[str, Any], names: list[str], roles: list[tuple[int, int]]
) -> dict[str, list[tuple[Instances, Instances]]]:
    """Each member's per-replica (T, S) main-branch instances (instruction, start, end) from its PUB's schedule."""
    files = _raw_pub_files(run)
    timelines: dict[str, list[tuple[Instances, Instances]]] = {}
    for name in names:
        pub = executed[name].get("pub")
        if pub not in files:
            raise RefusedAnalysis(f"{name}: no retained schedule for PUB {pub}")
        rows = scheduled_idle_replay.schedule_rows(files[pub])
        lines = {q: _instances(rows, q) for pair in roles for q in pair}
        timelines[name] = [(lines[target], lines[spectator]) for target, spectator in roles]
    return timelines


def skeleton_violations(run: Path, record: dict[str, Any], names: list[str]) -> list[str]:
    """Replicas whose compiled instructions, qubit by qubit and in order, differ from their scheduled instances.

    scheduled_idle_replay.padded_replica walks the fused ISA circuit of the PUB on each replica's physical qubits
    and consumes one schedule instance per non-virtual instruction; a missing, extra or reordered instruction on any
    role (a dropped read of the train, an added pulse) raises there.
    """
    from qiskit import qpy

    files = _raw_pub_files(run)
    with (run / "isa.qpy").open("rb") as stream:
        fused = {circuit.name: circuit for circuit in qpy.load(stream)}
    reasons, seen = [], set()
    for pub in record["execution_pubs"]:
        for component in pub["components"]:
            if component["group"] != "idle_penalty" or component["member"] not in names:
                continue
            seen.add(component["member"])
            rows = scheduled_idle_replay.schedule_rows(files[pub["name"]])
            replicas = scheduled_idle_replay.component_replicas(record, component)
            for k, (qubits, registers) in enumerate(zip(replicas, component["registers_by_replica"], strict=True)):
                try:
                    scheduled_idle_replay.padded_replica(fused[pub["name"]], rows, qubits, registers, insert=False)
                except RuntimeError as error:
                    reasons.append(f"{component['member']} replica {k}: {error}")
    reasons += [f"{name}: no execution PUB component" for name in names if name not in seen]
    return reasons


def exposure_violations(timelines: dict[str, list[tuple[Instances, Instances]]]) -> list[str]:
    """Departures of the scheduled idles from equal replicas, planned probe gaps, matched readout arms and the
    reader's train: its count of intermediate reads, inside the probe idle for the during and short arms and after
    the probe's final read for the after arm. Instance ends are the last pulse on the qubit channel."""
    reasons = []
    gapped = {name: [(_gaps(t), _gaps(s)) for t, s in replicas] for name, replicas in timelines.items()}
    for name in timelines:
        if len(set(gapped[name])) != 1:
            reasons.append(f"{name}: {len(set(gapped[name]))} distinct replica schedules")
        for k, sequence in enumerate(gapped[name]):
            for role, planned in planned_idles(name).items():
                idles = [gap for _, gap in sequence[role] if gap]
                if idles != planned:
                    reasons.append(f"{name} replica {k} role {role}: idles {idles}, planned {planned}")
            reference = quiet_reference(name)
            if reference is None:
                continue
            probe = next(iter(planned_idles(name)))
            if reference not in gapped or gapped[reference][k][probe] != sequence[probe]:
                reasons.append(f"{name} replica {k}: probe schedule differs from {reference}")
            train = reader_train(name)
            if train is None:
                continue
            count, inside = train
            probe_line, reader_line = timelines[name][k][probe], timelines[name][k][1 - probe]
            pulses = [i for i in probe_line if i[0] not in ("reset", "measure")]
            finals = [i for i in probe_line if i[0] == "measure"]
            reads = [i for i in reader_line if i[0] == "measure"]
            between = reads[:-1] if inside else reads[1:]
            if len(pulses) != 2 or len(finals) != 1 or len(between) != count:
                reasons.append(f"{name} replica {k}: {len(between)} reader reads, planned {count}")
            elif inside and not (pulses[0][2] <= between[0][1] and between[-1][2] <= pulses[1][1]):
                reasons.append(f"{name} replica {k}: reader train leaves the probe idle")
            elif not inside and between[0][1] < finals[0][2]:
                reasons.append(f"{name} replica {k}: reader train starts before the probe's final read ends")
    return reasons


def load(run: Path, predicted: bool) -> dict[str, Any]:
    record_path = run / "record.json"
    record = json.loads(record_path.read_text())
    group = next(g for g in record["groups"] if g["group"] == "idle_penalty")
    names = [m["name"] for m in group["members"] if not m["reference"]]
    identity: dict[str, Any] = {
        "run": _portable(run),
        "record_sha256": _sha256(record_path),
        "experiment_digest": record["experiment_digest"],
        "analysis_digest": analysis_digest(),
        "backend": group["backend"],
        "shots": int(record["shots"]),
        "repetition_delay_seconds": record["policy"].get("rep_delay_seconds"),
        "ladders": {"relax": ip.RELAX_DT, "ramsey": ip.RAMSEY_DT, "echo": ip.ECHO_DT, "meas": ip.MEAS_DT},
    }
    calibration: dict[str, Any]
    if predicted:
        laws = {m["name"]: [r["noisy"] for r in m["replicas"]] for m in group["members"] if not m["reference"]}
        calibration = group["placed_qubit_calibration"]
        identity |= {"source": "predicted", "calibration": group["calibration"]}
    else:
        collect_path = run / "collect.json"
        collected = json.loads(collect_path.read_text())
        block = next(c for c in collected if isinstance(c, dict) and c.get("group") == "idle_penalty")
        for key in ("comparisons_withheld", "summary_unavailable", "calibration_dependent_summaries_unavailable"):
            if key in block:
                raise RefusedAnalysis(f"the collector set {key}: {block[key]}")
        executed = block["executed"]
        missing = [n for n in names if n not in executed or n not in block["measured"]]
        if missing:
            raise RefusedAnalysis(f"members without an execution record or law: {missing}")
        unwindowed = [n for n in names if executed[n].get("calibration") is None]
        straddling = [n for n in names if executed[n].get("calibration_changed_during_shots")]
        stamps = {executed[n]["calibration"] for n in names}
        if unwindowed or straddling or len(stamps) != 1:
            raise RefusedAnalysis(
                f"windows unknown {unwindowed}, straddling {straddling}, calibrations {sorted(map(str, stamps))}"
            )
        calibration = {}
        for name in names:
            for qubit, values in executed[name]["placed_qubit_calibration"].items():
                if qubit in calibration and calibration[qubit] != values:
                    raise RefusedAnalysis(f"members disagree on qubit {qubit}'s execution calibration")
                calibration[qubit] = values
        exposure = skeleton_violations(run, record, names)
        exposure += exposure_violations(schedule_timelines(run, executed, names, role_map(group)))
        if exposure:
            raise RefusedAnalysis("scheduled exposure: " + "; ".join(exposure[:8]))
        identity["exposure"] = (
            f"{len(names)} members on {len(group['replicas'])} replicas: compiled instructions match the schedule, "
            "planned idles and reader trains hold"
        )
        laws = {n: [law_encoding.dense(stored) for stored in block["measured"][n]] for n in names}
        identity |= {"source": "measured", "calibration": stamps.pop(), "collect_sha256": _sha256(collect_path)}
    targets = json.loads((ROOT / "docs/evidence/heron_platform/targets.json").read_text())
    return {
        "roles": role_map(group),
        "laws": laws,
        "calibration": calibration,
        "identity": identity,
        "dt": float(targets["backends"][group["backend"]]["dt"]),
    }


def report(run: Path, predicted: bool) -> dict[str, Any]:
    data = load(run, predicted)
    laws, calibration, dt = data["laws"], data["calibration"], data["dt"]
    shots = data["identity"]["shots"]
    qubits: dict[str, Any] = {}
    pairs: list[dict[str, Any]] = []
    for k, pair in enumerate(data["roles"]):
        refs: dict[int, tuple[float, float]] = {}
        for bit, qubit in enumerate(pair):
            p1g = _p1(laws["idle_ground"][k], bit)
            p1e = _p1(laws["idle_excited"][k], bit)
            refs[bit] = (p1g, 1.0 - p1e)
            points = [(d * dt, _p1(laws[f"idle_relax_{d}dt"][k], bit)) for d in ip.RELAX_DT]
            fit = relaxation_rate(p1e, p1g, points, shots)
            t1 = calibration[str(qubit)]["T1"] * 1e-6
            entry = qubits.setdefault(str(qubit), {})
            entry |= {"role": "target" if bit == ip.TARGET else "spectator", "partner": pair[1 - bit], "replica": k}
            entry["t1_reported_us"] = t1 * 1e6
            if fit["gamma"] is not None:
                entry["kappa_1"] = fit["gamma"] * t1
                entry["kappa_1_se"] = fit["gamma_se"] * t1 if fit["gamma_se"] else None
            else:
                entry["kappa_1_reason"] = fit["reason"]
        contrasts = []
        for probe, qubit in enumerate(pair):
            head = ip.probe_prefix(probe)
            entry = qubits[str(qubit)]
            t2 = calibration[str(qubit)]["T2"] * 1e-6
            entry["t2_reported_us"] = t2 * 1e6
            for label, ladder, kind in (("kappa_2star", ip.RAMSEY_DT, "ramsey"), ("kappa_2echo", ip.ECHO_DT, "echo")):
                points = [
                    (d * dt, visibility(laws, f"{head}{kind}_{{q}}_{d}dt", k, refs[probe], probe)[0]) for d in ladder
                ]
                fit = decay_time(points, shots)
                entry[f"{label}_visibilities"] = [round(v, 5) for _, v in points]
                if fit["time"] is not None:
                    entry[label] = t2 / fit["time"]
                    entry[f"{label}_se"] = fit["rate_se"] * t2
                    entry[f"{label}_amplitude"] = fit["amplitude"]
                    entry[f"{label}_fit_chi2"] = fit["chi2"]
                else:
                    entry[f"{label}_reason"] = fit["reason"]
            if "kappa_2star" in entry and "kappa_2echo" in entry:
                entry["free_over_echo"] = entry["kappa_2star"] / entry["kappa_2echo"]
            v_during, phi_during = visibility(laws, f"{head}meas_during_{{q}}", k, refs[probe], probe)
            v_after, phi_after = visibility(laws, f"{head}meas_after_{{q}}", k, refs[probe], probe)
            v_quiet, phi_quiet = visibility(laws, f"{head}ramsey_{{q}}_{ip.MEAS_DT}dt", k, refs[probe], probe)
            _, phi_short = visibility(laws, f"{head}meas_short_{{q}}", k, refs[probe], probe)
            _, phi_short_quiet = visibility(laws, f"{head}ramsey_{{q}}_{ip.SHORT_MEAS_DT}dt", k, refs[probe], probe)
            short_khz = _phase_khz(phi_short, phi_short_quiet, ip.SHORT_MEAS_DT, dt)
            se_v = math.sqrt(2) * visibility_se(shots, *refs[probe])
            denominator = max(min(v_during, v_after, v_quiet), VISIBILITY_FLOOR)
            contrast = {
                "probe": qubit,
                "reader": pair[1 - probe],
                "dV": v_during - v_after,
                "dV_quiet": v_during - v_quiet,
                "null_dV": v_after - v_quiet,
                "shift_khz": unwrap_shift(_phase_khz(phi_during, phi_after, ip.MEAS_DT, dt), short_khz, dt),
                "shift_quiet_khz": unwrap_shift(_phase_khz(phi_during, phi_quiet, ip.MEAS_DT, dt), short_khz, dt),
                "null_shift_khz": _phase_khz(phi_after, phi_quiet, ip.MEAS_DT, dt),
                "short_shift_khz": short_khz,
                "dV_se": se_v,
                "shift_se_khz": se_v / denominator / (2 * math.pi * ip.MEAS_DT * dt) / 1e3,
            }
            contrasts.append(contrast)
            entry["readout"] = contrast
        target = qubits[str(pair[ip.TARGET])]
        _, phi_free = visibility(laws, f"idle_ramsey_{{q}}_{ip.ZZ_DT}dt", k, refs[ip.TARGET])
        _, phi_zz = visibility(laws, f"idle_zz_{{q}}_{ip.ZZ_DT}dt", k, refs[ip.TARGET])
        # S relaxes from |1> during the idle; conditioning on S's final read keeps the shots whose S stayed excited.
        _, phi_kept = visibility(laws, f"idle_zz_{{q}}_{ip.ZZ_DT}dt", k, refs[ip.TARGET], partner=1)
        target["zz_khz"] = _phase_khz(phi_zz, phi_free, ip.ZZ_DT, dt)
        target["zz_postselected_khz"] = _phase_khz(phi_kept, phi_free, ip.ZZ_DT, dt)
        target["cz_kick_p0_excess"] = (1.0 - _p1(laws["idle_cz_kick"][k], ip.TARGET)) - refs[ip.TARGET][1]
        pair_entry: dict[str, Any] = {"replica": k, "target": pair[0], "spectator": pair[1]}
        for key in ("dV", "dV_quiet", "null_dV", "shift_khz", "shift_quiet_khz", "null_shift_khz"):
            pair_entry[key] = float(np.mean([c[key] for c in contrasts]))
        pair_entry["dV_se"] = math.sqrt(sum(c["dV_se"] ** 2 for c in contrasts)) / len(contrasts)
        pair_entry["shift_se_khz"] = math.sqrt(sum(c["shift_se_khz"] ** 2 for c in contrasts)) / len(contrasts)
        pairs.append(pair_entry)
    return {"identity": data["identity"], "qubits": qubits, "pairs": pairs, "pooled": pooled(qubits, pairs)}


def median_interval(values: list[float]) -> dict[str, Any]:
    """The median with its distribution-free 95% order-statistic interval."""
    if not values:
        return {"n": 0}
    arr = np.sort(np.asarray(values, dtype=float))
    n = len(arr)
    low = int(stats.binom.ppf(0.025, n, 0.5))
    high = int(stats.binom.isf(0.025, n, 0.5))
    return {
        "n": n,
        "median": float(np.median(arr)),
        "low": float(arr[max(low - 1, 0)]),
        "high": float(arr[min(high, n - 1)]),
    }


def _mean_decision(values: list[float], errors: list[float], band: float, sign_rule: str) -> dict[str, Any]:
    """Pair-mean t statistic and chi-square against zero, with the sign the endpoint requires."""
    arr, err = np.asarray(values), np.asarray(errors)
    mean, se = float(arr.mean()), float(arr.std(ddof=1) / math.sqrt(len(arr)))
    t = mean / se if se > 0 else float("nan")
    chi2 = float(np.sum((arr / err) ** 2))
    tail = float(stats.chi2.sf(chi2, len(arr)))
    dof = len(arr) - 1
    if sign_rule == "negative":
        signed = mean < 0 and (t < stats.t.ppf(CHI2_ALPHA, dof) or tail < CHI2_ALPHA)
    else:
        signed = abs(t) > stats.t.ppf(1 - CHI2_ALPHA / 2, dof) or tail < CHI2_ALPHA
    if signed:
        verdict = "present"
    elif -band <= mean - 1.96 * se and mean + 1.96 * se <= band and tail > 0.05:
        verdict = "absent"
    else:
        verdict = "unresolved"
    return {
        "n": len(arr),
        "mean": mean,
        "se": se,
        "t": t,
        "chi2": chi2,
        "chi2_tail": tail,
        "band": band,
        "verdict": verdict,
    }


def pooled(qubits: dict[str, Any], pairs: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {
        key: median_interval([q[key] for q in qubits.values() if key in q])
        for key in ("kappa_1", "kappa_2star", "kappa_2echo", "free_over_echo")
    }
    k1, ratio = out["kappa_1"], out["free_over_echo"]
    out["optimistic_t1"] = "present" if k1.get("n") and k1["median"] > 1.5 and k1["low"] > 1 else "absent or unresolved"
    out["echo_gain"] = "present" if ratio.get("n") and ratio["low"] > 1 else "absent or unresolved"
    for endpoint, value, quiet, null, error, band, sign in (
        ("dephasing", "dV", "dV_quiet", "null_dV", "dV_se", 0.02, "negative"),
        ("shift", "shift_khz", "shift_quiet_khz", "null_shift_khz", "shift_se_khz", 0.5, "either"),
    ):
        errors = [p[error] for p in pairs]
        first = _mean_decision([p[value] for p in pairs], errors, band, sign)
        second = _mean_decision([p[quiet] for p in pairs], errors, band, sign)
        nulled = _mean_decision([p[null] for p in pairs], errors, band, "either")
        same_sign = math.copysign(1, first["mean"]) == math.copysign(1, second["mean"])
        if first["verdict"] == second["verdict"] == "present" and same_sign and nulled["verdict"] != "present":
            decision = "present"
        elif first["verdict"] == second["verdict"] == nulled["verdict"] == "absent":
            decision = "absent"
        else:
            decision = "unresolved"
        out[f"readout_{endpoint}"] = {"vs_after": first, "vs_quiet": second, "null": nulled, "decision": decision}
    return out


def compare(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    """Cross-calibration stability over the qubits that keep their role and partner in both measured runs."""
    a, b = first["identity"], second["identity"]
    reasons = []
    if a["source"] != "measured" or b["source"] != "measured":
        reasons.append("both reports must come from measured runs")
    if a["backend"] != b["backend"]:
        reasons.append(f"backends differ: {a['backend']} and {b['backend']}")
    if a["calibration"] == b["calibration"] or a.get("collect_sha256") == b.get("collect_sha256"):
        reasons.append("the reports share an execution calibration or a collection")
    for key in ("shots", "ladders", "experiment_digest"):
        if a[key] != b[key]:
            reasons.append(f"{key} differs")
    if reasons:
        raise RefusedAnalysis("; ".join(reasons))
    out: dict[str, Any] = {"first": a["run"], "second": b["run"]}
    for key in ("kappa_1", "kappa_2star", "kappa_2echo"):
        common = [
            q
            for q, entry in first["qubits"].items()
            if key in entry
            and key in second["qubits"].get(q, {})
            and (entry["role"], entry["partner"]) == (second["qubits"][q]["role"], second["qubits"][q]["partner"])
        ]
        if len(common) < 3:
            out[key] = {"n": len(common), "verdict": "unresolved"}
            continue
        x = np.array([first["qubits"][q][key] for q in common])
        y = np.array([second["qubits"][q][key] for q in common])
        r = float(np.corrcoef(x, y)[0, 1])
        band = median_interval(list(y / x))
        inside = STABLE_RATIO[0] <= band["low"] and band["high"] <= STABLE_RATIO[1]
        outside = band["high"] < STABLE_RATIO[0] or band["low"] > STABLE_RATIO[1]
        verdict = "stable" if inside and r >= STABLE_CORRELATION else "drifted" if outside else "unresolved"
        out[key] = {"n": len(common), "pearson_r": r, "ratio": band, "verdict": verdict}
    return out


def placement_violations(run: Path, snapshot: Path | None = None) -> list[str]:
    """Why a run's placement fails the campaign: a pair off a coupler, or a coupler joining two replicas.

    The guard ring of live_run.place_replicas blocks neighbors on the admitted
    graph; a coupler the quality policy excluded still couples its endpoints,
    so the check reads every coupler of the given calibration snapshot
    (calibration_snapshot.py --export) or of the retained Target snapshot.
    """
    record = json.loads((run / "record.json").read_text())
    group = next(g for g in record["groups"] if g["group"] == "idle_penalty")
    if snapshot is not None:
        source = json.loads(snapshot.read_text())
        if source["backend"] != group["backend"]:
            raise RefusedAnalysis(f"snapshot backend {source['backend']} differs from {group['backend']}")
        qargs = [entry["qargs"] for entry in source["instructions"]["cz"]]
    else:
        targets = json.loads((ROOT / "docs/evidence/heron_platform/targets.json").read_text())
        qargs = targets["backends"][group["backend"]]["instructions"]["cz"]["qargs"]
    edges = {(min(e), max(e)) for e in qargs}
    pairs = role_map(group)
    owner = {q: k for k, p in enumerate(pairs) for q in p}
    reasons = [f"replica {k} pair {p} is not a coupler" for k, p in enumerate(pairs) if (min(p), max(p)) not in edges]
    reasons += [
        f"coupler {e} joins replicas {owner[e[0]]} and {owner[e[1]]}"
        for e in sorted(edges)
        if e[0] in owner and e[1] in owner and owner[e[0]] != owner[e[1]]
    ]
    return reasons


def _print(result: dict[str, Any]) -> None:
    p = result["pooled"]
    nan = float("nan")
    for key in ("kappa_1", "kappa_2star", "kappa_2echo", "free_over_echo"):
        band = p[key]
        low, high = band.get("low", nan), band.get("high", nan)
        print(f"{key}: n={band.get('n')} median={band.get('median', nan):.3f} [{low:.3f}, {high:.3f}]")
    print(f"optimistic_t1: {p['optimistic_t1']}; echo_gain: {p['echo_gain']}")
    for endpoint in ("dephasing", "shift"):
        block = p[f"readout_{endpoint}"]
        parts = [
            f"{name} mean={block[name]['mean']:.4f} se={block[name]['se']:.4f} t={block[name]['t']:.2f} "
            f"tail={block[name]['chi2_tail']:.3g} {block[name]['verdict']}"
            for name in ("vs_after", "vs_quiet", "null")
        ]
        print(f"readout_{endpoint}: {block['decision']} | " + " | ".join(parts))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("--predicted", action="store_true", help="read the dry run's noisy predictions")
    parser.add_argument("--self-check", action="store_true", help="require the no-crosstalk null on predictions")
    parser.add_argument("--check-placement", action="store_true", help="check couplers against the record's pairs")
    parser.add_argument("--snapshot", type=Path, help="calibration_snapshot.py export for --check-placement")
    parser.add_argument("--compare", nargs=2, type=Path, metavar=("FIRST", "SECOND"), help="two --out reports")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.compare:
            first, second = (json.loads(path.read_text()) for path in args.compare)
            text = json.dumps(compare(first, second), indent=1, sort_keys=True)
            print(text)
            if args.out:
                args.out.write_text(text + "\n")
            return 0
        if args.run is None:
            parser.error("a run directory is required without --compare")
        if args.check_placement:
            reasons = placement_violations(args.run, args.snapshot)
            print("\n".join(reasons) if reasons else "placement: every pair on a coupler, no coupler between replicas")
            if reasons:
                return 1
        result = report(args.run, args.predicted or args.self_check)
    except RefusedAnalysis as refusal:
        print(f"refused: {refusal}")
        return 2
    if args.out:
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    _print(result)
    if args.self_check:
        p = result["pooled"]
        misses = [k for k in ("kappa_1", "kappa_2echo") if abs(p[k]["median"] - 1) > SELF_CHECK_TOLERANCE]
        for endpoint in ("dephasing", "shift"):
            block = p[f"readout_{endpoint}"]
            if block["decision"] == "present" or block["null"]["verdict"] == "present":
                misses.append(f"readout_{endpoint}")
        if misses:
            print(f"self-check failed: {misses}")
            return 1
        print("self-check: kappa_1 and kappa_2echo medians lie near 1; no readout decision or null reads present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
