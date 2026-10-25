"""IQM Garnet diagnostic of the unitary-arm excess of the pinching case: axis phase or |1> loss.

The retained QPU window probes read the N = 16 unitary circuit (sixteen prx(pi/18, 0) on six qubits, a 2 us idle, one
measure) at P(0) = 0.14 to 0.38 against planning values of 0.053 to 0.094. A hidden Markov fit of the measure probe's
mid-circuit keys disfavors a shared under-rotation of the pi/18 pulses, which leaves two causes (docs/design/
iqm-garnet-measurement-sequence-pinching.md, "Pre-flight stop rule"): (a) an axis phase per small-angle prx pulse,
and (b) |1> loss during the 2 us idle and the readout. This case runs eight circuits on the same six qubits in one job,
each ending with the 2 us pre-readout delay and a final measure keyed `f` over all six, except D3:

- D1 ro0: no pulse.
- D2 ro1: prx(pi, 0). The in-situ P(0|1) after the idle.
- D3 ro1-now: prx(pi, 0) and the measure at once. Against D2 it separates idle relaxation from readout error.
- D4 unitary-n16: the probe circuit, 16 x prx(pi/18, 0), instruction for instruction.
- D5 single: prx(8 pi/9, 0).
- D6 pair-n16: 16 steps of RX(pi/18), each two prx(pi/2) pulses whose phases fold the virtual Z rotations in: step k
  plays prx(pi/2, a_k) then prx(pi/2, a_k + pi + alpha) with a_k = pi/2 + k alpha, alpha = pi/18, and the product is
  RZ(zeta) RX(16 alpha) up to a global phase (pair_product, checked by the self-test).
- D7: 8 x prx(pi/9, 0). D8: 4 x prx(2 pi/9, 0).

Every circuit's ideal P(0) is cos(4 pi/9)^2 = 0.0302. The prediction is the Bloch model of scripts/
iqm_measurement_sequence.py with the calibration's T1, T2, prx error and readout errors.

Preregistered decision rule (diagnose), per qubit with binomial standard errors propagated by the delta method through
the in-situ correction and a prx-error systematic of 100 % of the calibrated value. D1 and D2 correct D4 to D8: the
corrected z is (Zobs - o)/s with o and s from the pair, and every corrected prediction a + b q is the response to
the initial z plus the response to the relaxation source times q = 1/(1 - 2 p) at the planning excitation p = 0.068.
z is (measured - model)/SE.

- L is the set of qubits whose raw D4 P(0) exceeds the raw model by more than Z_DECIDE = 3 standard errors.
- Readout-loss cause: on every qubit of L, D2's raw P(0) exceeds the model's (calibration e10 and T1 decay over the
  idle) by more than 3 standard errors and the corrected D4 lies within 3 standard errors of its model.
- Phase cause: on every qubit of L, D2 does not exceed its model by 3 standard errors, the corrected D4 exceeds its
  model by more than 3, the corrected D5 lies within 3, and the pooled corrected excess ranks D4, D7, D8 without a
  significant inversion (D4 - D7 and D7 - D8 not below -3 standard errors).
- Rebuild criterion: the corrected D6 lies within 3 standard errors of its model on all six qubits, and the main case
  is rebuilt with pi/2-pair steps.
- No excess: L is empty. Neither: L is not empty and neither pattern holds; the readings are reported without a choice.

Mock outcomes are random bits and never enter the analysis (analyze --mock only exercises the pipeline).

Usage: "$PYTHON" scripts/iqm_measurement_diagnostic.py (build DIR [--calibration-dir DIR | --live] | check DIR
       | analyze RUN_DIR --out FILE [--replay] [--mock] | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_measurement_sequence as seq  # noqa: E402
from iqm_jobs import CANCEL_MARGIN, CASE_SCHEMA, JOB_SECONDS, dump, run_facts  # noqa: E402
from iqm_platform import sha256  # noqa: E402

from parallel import ordered_map  # noqa: E402

CASE = "measurement-sequence-diagnostic"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
JOB = "diagnostic"
EXCERPT = "calibration/excerpt.json"
MAIN_CASE = ROOT / "results/iqm/cases" / seq.CASE
PROBE_CASE = ROOT / "results/iqm/cases/measurement-window-qpu-probe"
OPTIONS: dict[str, Any] = {"heralding_mode": "none", "active_reset_cycles": 1}
SHOTS = 1000
MAX_CREDITS = {"garnet": 1.0, "garnet:mock": 0.0}
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
ALPHA = math.pi / 18
Z_DECIDE = seq.Z_DECIDE
NAMES = ("d1-ro0", "d2-ro1", "d3-ro1-now", "d4-unitary-n16", "d5-single", "d6-pair-n16", "d7-n8", "d8-n4")
CORRECTED = ("d4-unitary-n16", "d5-single", "d6-pair-n16", "d7-n8", "d8-n4")
IDEAL = (1 + math.cos(8 * math.pi / 9)) / 2


def pair_phases(steps: int = 16, alpha: float = ALPHA) -> list[tuple[float, float]]:
    """The two prx(pi/2) phases of each step: (a_k, a_k + pi + alpha) with a_k = pi/2 + k alpha."""
    return [(math.pi / 2 + k * alpha, math.pi / 2 + k * alpha + math.pi + alpha) for k in range(steps)]


def pulses_of(name: str) -> list[tuple[float, float]]:
    """The (angle, phase) of each prx layer of a diagnostic circuit, in order."""
    if name in ("d2-ro1", "d3-ro1-now"):
        return [(math.pi, 0.0)]
    if name == "d4-unitary-n16":
        return [(ALPHA, 0.0)] * 16
    if name == "d5-single":
        return [(8 * math.pi / 9, 0.0)]
    if name == "d6-pair-n16":
        return [(math.pi / 2, phase) for pair in pair_phases() for phase in pair]
    if name == "d7-n8":
        return [(math.pi / 9, 0.0)] * 8
    if name == "d8-n4":
        return [(2 * math.pi / 9, 0.0)] * 4
    return []


def circuit_of(name: str, qubits: list[str]) -> dict[str, Any]:
    if name == "d4-unitary-n16":
        # Instruction for instruction the probe circuit.
        return {**seq.circuit(name, qubits, "unitary", 16, 1, paired=False), "name": name}
    instructions: list[dict[str, Any]] = []
    for angle, phase in pulses_of(name):
        instructions += [seq.op("prx", [q], angle=angle, phase=phase) for q in qubits]
    if name != "d3-ro1-now":
        instructions.append(seq.op("delay", qubits, duration=seq.PRE_READOUT_SECONDS))
    instructions.append(seq.op("measure", qubits, key=seq.FINAL_KEY))
    return {"name": name, "instructions": instructions}


def pair_product(steps: int = 16, alpha: float = ALPHA) -> Any:
    """The SU(2) product of the pair pulses, later pulses to the left."""
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    y = np.array([[0, -1j], [1j, 0]])

    def prx(theta: float, phase: float) -> Any:
        return math.cos(theta / 2) * np.eye(2) - 1j * math.sin(theta / 2) * (math.cos(phase) * x + math.sin(phase) * y)

    product = np.eye(2, dtype=complex)
    for first, second in pair_phases(steps, alpha):
        product = prx(math.pi / 2, second) @ prx(math.pi / 2, first) @ product
    return product


def rx(theta: float) -> Any:
    return math.cos(theta / 2) * np.eye(2) - 1j * math.sin(theta / 2) * np.array([[0, 1], [1, 0]], dtype=complex)


def evolve(
    pulses: list[tuple[float, float]],
    t1: float,
    t2: float,
    gate_p: float,
    z0: float,
    z_eq: float = 1.0,
    advance: float = 0.0,
) -> float:
    """The Bloch z after the pulses (before any wait): each prx a rotation about (cos phi, sin phi, 0) with the
    depolarizing error and T1/T2 relaxation over the compiled layer of seq.PRX_LAYER_SECONDS. `advance` adds that
    many radians of axis phase per pulse (a model device)."""
    t2 = min(t2, 2 * t1)
    decay_t2 = math.exp(-seq.PRX_LAYER_SECONDS / t2)
    decay_t1 = math.exp(-seq.PRX_LAYER_SECONDS / t1)
    v = np.array([0.0, 0.0, z0])
    for k, (theta, phase) in enumerate(pulses):
        phi = phase + advance * k
        n = np.array([math.cos(phi), math.sin(phi), 0.0])
        v = v * math.cos(theta) + np.cross(n, v) * math.sin(theta) + n * float(n @ v) * (1 - math.cos(theta))
        v = v * (1 - gate_p)
        v[0] *= decay_t2
        v[1] *= decay_t2
        v[2] = z_eq - (z_eq - v[2]) * decay_t1
    return float(v[2])


def corrected_model(name: str, cal: dict[str, float], gate_p: float, q: float) -> float:
    """The corrected z the in-situ pair recovers: the response a to a unit initial z plus b q with b the response
    to the relaxation source."""
    pulses = pulses_of(name)
    b = evolve(pulses, cal["t1_s"], cal["t2_s"], gate_p, 0.0)
    return evolve(pulses, cal["t1_s"], cal["t2_s"], gate_p, 1.0) - b + b * q


def raw_p0(name: str, cal: dict[str, float], device: dict[str, Any]) -> float:
    """P(read 0) of a circuit on a model device: the initialization excitation p_init, the pulses with an axis-phase
    advance, relaxation over the pre-readout wait at the wait T1, and the assignment errors."""
    z = evolve(
        pulses_of(name),
        device["t1_s"],
        device["t2_s"],
        device["prx_p"],
        1 - 2 * device["p_init"],
        advance=device["advance"],
    )
    if name != "d3-ro1-now":
        z = 1 - (1 - z) * math.exp(-seq.PRE_READOUT_SECONDS / device["wait_t1_s"])
    observed = (1 - device["e01"] - device["e10"]) * z + device["e10"] - device["e01"]
    return (1 + observed) / 2


def device_of(cal: dict[str, float], **over: Any) -> dict[str, Any]:
    device = {
        "t1_s": cal["t1_s"],
        "t2_s": cal["t2_s"],
        "prx_p": cal["prx_p"],
        "e01": cal["e01"],
        "e10": cal["e10"],
        "p_init": seq.ACTIVE_RESET_EXCITED,
        "advance": 0.0,
        "wait_t1_s": cal["t1_s"],
    }
    device.update(over)
    return device


def excerpt_of(calibration_dir: Path) -> dict[str, Any]:
    """The six qubits of the main case with their T1, T2, prx error and readout errors from one calibration set."""
    metrics = seq.load_json(calibration_dir / "metrics.json")
    architecture = seq.load_json(calibration_dir / "dynamic-quantum-architecture.json")
    identity = architecture["calibration_set_id"]
    if metrics.get("describes_id") != identity:
        raise ValueError(f"{calibration_dir}: the metrics and the architecture describe different sets")
    values = {o["dut_field"]: o["value"] for o in metrics["observations"] if not o.get("invalid")}
    qubits = sorted(seq.load_json(MAIN_CASE / seq.EXCERPT)["qubits"], key=lambda q: int(q[2:]))
    coupled = {
        frozenset(locus) for impl in architecture["gates"]["cz"]["implementations"].values() for locus in impl["loci"]
    }
    pairs = sorted(f"{a}-{b}" for a in qubits for b in qubits if a < b and frozenset((a, b)) in coupled)
    return {
        "schema": "iqm-measurement-diagnostic-calibration-v1",
        "calibration_set": identity,
        "source_sha256": {
            name: sha256((calibration_dir / name).read_bytes())
            for name in ("metrics.json", "dynamic-quantum-architecture.json")
        },
        "couplers_among_qubits": pairs,
        "qubits": {
            q: {
                "t1_s": values[f"characterization.model.{q}.t1_time"],
                "t2_s": values[f"characterization.model.{q}.t2_time"],
                "prx_p": 2 * (1 - values[f"metrics.rb.prx.drag_crf_sx.{q}.fidelity:par=d2"]),
                "e01": values[f"metrics.ssro.measure.constant.{q}.error_0_to_1"],
                "e10": values[f"metrics.ssro.measure.constant.{q}.error_1_to_0"],
            }
            for q in qubits
        },
    }


def fetch_live(calibration_dir: Path) -> None:
    """Garnet's current default calibration set (network, read-only): its architecture and metrics, read by id."""
    from iqm_platform import Client, calibration_paths, default_calibration_path, read_tokens, tokens_path

    client = Client(read_tokens(tokens_path())["access_token"])
    status, body = client.get(default_calibration_path(QC))
    if status != 200:
        raise ValueError(f"GET the default calibration set answered {status}")
    identity = json.loads(body)["observation_set_id"]
    calibration_dir.mkdir(parents=True, exist_ok=True)
    for name, path in calibration_paths(QC, identity).items():
        status, data = client.get(path)
        if status != 200:
            raise ValueError(f"GET {path} answered {status}")
        (calibration_dir / name).write_bytes(data)


def billing(circuits: list[dict[str, Any]], shots: int) -> dict[str, Any]:
    """The seq.billing model at this case's ceiling: compiled schedule + fixed + per circuit-shot, plus the margins."""
    schedule = shots * sum(seq.estimator_shot_seconds(c) for c in circuits)
    execution = schedule + seq.EXECUTION_FIXED_SECONDS + seq.EXECUTION_PER_CIRCUIT_SHOT_SECONDS * len(circuits) * shots
    worst = execution + seq.EXECUTION_FIT_RESIDUAL_SECONDS + seq.RUNTIME_OVER_EXECUTION_SECONDS
    threshold = MAX_CREDITS[QC] / PRICE[QC] - CANCEL_MARGIN
    return {
        "shots": shots,
        "circuits": len(circuits),
        "compiled_schedule_seconds": schedule,
        "execution_seconds": execution,
        "worst_case_runtime_seconds": worst,
        "billed_seconds": math.ceil(worst),
        "credits": math.ceil(worst) * PRICE[QC],
        "cancel_threshold_seconds": threshold,
        "cancel_margin_seconds": threshold - worst,
    }


def predict(excerpt: dict[str, Any], circuits: list[dict[str, Any]]) -> dict[str, Any]:
    """The planning table: raw and corrected P(0) per circuit and qubit at the calibration."""
    q = seq.PLANNING_Q
    table: dict[str, Any] = {}
    for qubit, cal in excerpt["qubits"].items():
        device = device_of(cal)
        table[qubit] = {
            name: {
                "raw_p0": raw_p0(name, cal, device),
                "corrected_p0": (1 + corrected_model(name, cal, cal["prx_p"], q)) / 2,
            }
            for name in NAMES
        }
    return {
        "calibration_set": excerpt["calibration_set"],
        "ideal_p0": IDEAL,
        "p_init_assumed": seq.ACTIVE_RESET_EXCITED,
        "qubits": table,
        "billing": billing(circuits, SHOTS),
        "estimator_per_shot_seconds_all_circuits": sum(seq.estimator_shot_seconds(c) for c in circuits),
        "note": (
            "raw_p0 is the probability of reading 0 with the calibration readout errors; corrected_p0 is the value the "
            "in-situ D1/D2 correction recovers at q = 1/(1 - 2 p)"
        ),
    }


def build_files(excerpt: dict[str, Any]) -> dict[str, str]:
    if excerpt["couplers_among_qubits"]:
        raise ValueError(f"the qubits share couplers {excerpt['couplers_among_qubits']}")
    qubits = sorted(excerpt["qubits"], key=lambda q: int(q[2:]))
    circuits = [circuit_of(name, qubits) for name in NAMES]
    files = {f"circuits/{c['name']}.json": dump(c) for c in circuits}
    prediction = predict(excerpt, circuits)
    job = {
        "job": JOB,
        "circuits": [{"file": rel, "sha256": sha256(text.encode())} for rel, text in files.items()],
        "shots": SHOTS,
        "options": {**OPTIONS, "calibration_set_id": {QC: excerpt["calibration_set"]}},
        "expected_seconds": round(prediction["billing"]["execution_seconds"], 3),
        "max_credits": MAX_CREDITS,
    }
    files["prediction.json"] = dump(prediction)
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Is the excess of the N = 16 unitary circuit over its model on QB5, QB7, QB11, QB14, QB17 and QB19 "
                "an axis phase per small-angle prx pulse or |1> loss during the pre-readout idle and the readout, "
                "and do pi/2-pair steps avoid it?"
            ),
            "qcs": QCS,
            "jobs": [job],
            "prediction_sha256": sha256(files["prediction.json"].encode()),
        }
    )
    files[EXCERPT] = dump(excerpt)
    return files


def write(directory: Path, calibration_dir: Path) -> None:
    files = build_files(excerpt_of(calibration_dir))
    stale_dir = directory / "circuits"
    for stale in stale_dir.glob("*.json") if stale_dir.exists() else []:
        if stale.relative_to(directory).as_posix() not in files:
            stale.unlink()
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    prediction = json.loads(files["prediction.json"])
    print(
        json.dumps({"circuits": len(NAMES), "calibration_set": prediction["calibration_set"], **prediction["billing"]})
    )


def check(directory: Path) -> None:
    files = build_files(seq.load_json(directory / EXCERPT))
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if present != set(files):
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ set(files))}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from its retained calibration excerpt")


def quantities(p: dict[str, float], ctx: dict[str, Any]) -> dict[str, float]:
    """The readings and their models as a function of P(1) of each circuit and the prx error."""
    cal, gate_p, q = ctx["cal"], p["prx_p"], seq.PLANNING_Q
    z1, z2 = 1 - 2 * p["d1-ro0"], 1 - 2 * p["d2-ro1"]
    scale, offset = (z1 - z2) / 2, (z1 + z2) / 2
    out: dict[str, float] = {"scale": scale, "offset": offset}
    device = device_of({**cal, "prx_p": gate_p})
    for name in NAMES:
        raw = 1 - p[name]
        out[f"raw:{name}"] = raw
        out[f"raw_model:{name}"] = raw_p0(name, cal, device)
        out[f"raw_diff:{name}"] = raw - out[f"raw_model:{name}"]
    for name in CORRECTED:
        measured = (1 + ((1 - 2 * p[name]) - offset) / scale) / 2
        model = (1 + corrected_model(name, cal, gate_p, q)) / 2
        out[f"p0c:{name}"] = measured
        out[f"p0c_model:{name}"] = model
        out[f"diff:{name}"] = measured - model
    return out


def evaluate_qubit(item: tuple[str, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """The readings, models and z of one qubit from the counts of the eight circuits."""
    qubit, counts, ctx = item
    obs = {name: seq.pooled_two_state(counts, qubit, [name]) for name in NAMES}
    keys = [*NAMES, "prx_p"]
    x = [*(k / n for k, n in obs.values()), ctx["cal"]["prx_p"]]
    variances = [*(seq.var(k, n) for k, n in obs.values()), (seq.PRX_SYSTEMATIC * ctx["cal"]["prx_p"]) ** 2]
    # (Z1 - Z2)/2 with Z = 1 - 2 P(1) is P(1) of D2 less P(1) of D1.
    scale = x[keys.index("d2-ro1")] - x[keys.index("d1-ro0")]
    if not scale >= seq.READOUT_CONTRAST_FLOOR:
        return {"usable": False, "reason": f"readout scale {scale:.4f} lies below {seq.READOUT_CONTRAST_FLOOR}"}
    value, se = seq.propagate_many(lambda xs: quantities(dict(zip(keys, xs, strict=True)), ctx), x, variances)
    z = {k: (value[k] / se[k] if se[k] > 0 else math.inf) for k in value if k.startswith(("diff:", "raw_diff:"))}
    return {
        "usable": True,
        "scale": value["scale"],
        "raw": {
            name: {"p0": value[f"raw:{name}"], "model": value[f"raw_model:{name}"], "z": z[f"raw_diff:{name}"]}
            for name in NAMES
        },
        "corrected": {
            name: {
                "p0": value[f"p0c:{name}"],
                "model": value[f"p0c_model:{name}"],
                "difference": value[f"diff:{name}"],
                "se": se[f"diff:{name}"],
                "z": z[f"diff:{name}"],
            }
            for name in CORRECTED
        },
        "idle_relaxation": {
            "d2_minus_d3_raw_p0": value["raw:d2-ro1"] - value["raw:d3-ro1-now"],
            "model": value["raw_model:d2-ro1"] - value["raw_model:d3-ro1-now"],
        },
    }


def pooled(rows: list[tuple[float, float]]) -> tuple[float, float]:
    """The inverse-variance pooled estimate and its standard error."""
    weights = [1 / se**2 for _, se in rows]
    total = sum(weights)
    return sum(w * e for w, (e, _) in zip(weights, rows, strict=True)) / total, 1 / math.sqrt(total)


def diagnose(qubits: dict[str, Any]) -> dict[str, Any]:
    """The preregistered verdict over the usable qubits (see the module docstring)."""
    usable = {q: r for q, r in qubits.items() if r["usable"]}
    large = sorted(q for q, r in usable.items() if r["raw"]["d4-unitary-n16"]["z"] > Z_DECIDE)
    d2_excess = {q: r["raw"]["d2-ro1"]["z"] > Z_DECIDE for q, r in usable.items()}

    def corrected(q: str, name: str) -> dict[str, float]:
        return usable[q]["corrected"][name]

    excess = {
        name: pooled([(corrected(q, name)["difference"], corrected(q, name)["se"]) for q in large]) if large else None
        for name in ("d4-unitary-n16", "d7-n8", "d8-n4")
    }

    def inversion(high: str, low: str) -> bool:
        upper, lower = excess[high], excess[low]
        if upper is None or lower is None:
            return False
        return upper[0] - lower[0] < -Z_DECIDE * math.hypot(upper[1], lower[1])

    ranking_ok = bool(large) and not inversion("d4-unitary-n16", "d7-n8") and not inversion("d7-n8", "d8-n4")
    readout_loss = bool(large) and all(
        d2_excess[q] and abs(corrected(q, "d4-unitary-n16")["z"]) <= Z_DECIDE for q in large
    )
    phase = (
        bool(large)
        and ranking_ok
        and all(
            not d2_excess[q]
            and corrected(q, "d4-unitary-n16")["z"] > Z_DECIDE
            and abs(corrected(q, "d5-single")["z"]) <= Z_DECIDE
            for q in large
        )
    )
    verdict = "no_excess" if not large else "readout_loss" if readout_loss else "phase" if phase else "neither"
    return {
        "usable_qubits": sorted(usable),
        "large_excess_qubits": large,
        "verdict": verdict,
        "d2_excess_over_model": d2_excess,
        "pooled_corrected_excess": {
            k: None if v is None else {"estimate": v[0], "se": v[1]} for k, v in excess.items()
        },
        "ranking_ok": ranking_ok,
        "rebuild_with_pi2_pairs": bool(usable)
        and all(abs(corrected(q, "d6-pair-n16")["z"]) <= Z_DECIDE for q in usable),
    }


def evaluate(counts: dict[str, Any], prediction: dict[str, Any], excerpt: dict[str, Any]) -> dict[str, Any]:
    qubits = sorted(excerpt["qubits"], key=lambda q: int(q[2:]))
    items = [(q, counts, {"cal": excerpt["qubits"][q]}) for q in qubits]
    results = dict(zip(qubits, ordered_map(evaluate_qubit, items, min_items=2), strict=True))
    return {"qubits": results, "diagnosis": diagnose(results)}


def analyze(run_dir: Path, mock: bool = False) -> dict[str, Any]:
    """The preregistered diagnosis of a garnet run; with mock the same pipeline over a garnet:mock run, whose random
    outcomes decide nothing."""
    facts = run_facts(run_dir)
    submission = seq.load_json(run_dir / "submission.json")
    record = json.loads((run_dir / "raw/job.json").read_bytes())
    case = seq.load_json(run_dir / "cases.json")
    prediction_bytes = (run_dir / "prediction.json").read_bytes()
    if sha256(prediction_bytes) != case.get("prediction_sha256"):
        raise ValueError(f"{run_dir}/prediction.json is not the prediction cases.json binds")
    if facts["statuses"] != {"completed": 1}:
        raise ValueError(f"{run_dir}: the job is {sorted(facts['statuses'])}; the analysis reads completed jobs")
    qc = f"{QC}:mock" if mock else QC
    if submission["qc"] != qc or case.get("case") != CASE:
        raise ValueError(f"{run_dir}: a {case.get('case')} run on {submission['qc']}, not a {CASE} run on {qc}")
    prediction = json.loads(prediction_bytes)
    if not mock and record["compilation"]["calibration_set_id"] != prediction["calibration_set"]:
        raise ValueError(f"{run_dir}: compiled against another calibration set than the case's")
    excerpt = seq.load_json(run_dir / EXCERPT)
    row = next(r for r in case["jobs"] if r["job"] == submission["job"])
    circuits = [seq.load_json(run_dir / entry["file"]) for entry in row["circuits"]]
    counts = seq.tally(circuits, json.loads((run_dir / "raw/measurements.json").read_bytes()))
    estimated = record["compilation"]["execution_runtime_estimate_seconds"] - JOB_SECONDS
    predicted = prediction["estimator_per_shot_seconds_all_circuits"] * row["shots"]
    metrics = record["metrics"]
    return {
        "schema": "iqm-measurement-diagnostic-analysis-v1",
        "run": run_dir.name,
        "mock": mock,
        "calibration_set": record["compilation"]["calibration_set_id"],
        "charge": facts["charge"],
        "runtime_seconds": metrics["runtime_seconds"],
        "billed_seconds": metrics["billed_seconds"],
        "compiled_schedule": {
            "predicted_seconds": predicted,
            "estimated_seconds": estimated,
            "ratio": estimated / predicted,
        },
        **evaluate(counts, prediction, excerpt),
    }


def synthetic_counts(excerpt: dict[str, Any], devices: dict[str, dict[str, Any]], shots: int = SHOTS) -> dict[str, Any]:
    """Expected counts of model devices, rounded to whole shots, in the layout of seq.tally."""
    counts: dict[str, Any] = {}
    for name in NAMES:
        row: dict[str, Any] = {"shots": shots, "final": {}}
        for q, cal in excerpt["qubits"].items():
            k0 = round(shots * raw_p0(name, cal, devices[q]))
            row["final"][q] = [k0, shots - k0]
        counts[name] = row
    return counts


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def self_test() -> str:
    excerpt = seq.load_json(ROOT / "results/iqm/cases" / CASE / EXCERPT)
    files = build_files(excerpt)
    expect(files == build_files(excerpt), "the build is not deterministic")
    qubits = sorted(excerpt["qubits"], key=lambda q: int(q[2:]))
    # D6: the pairs compose to 16 RX(pi/18) up to a global phase and a final Z rotation.
    leftover = pair_product() @ rx(16 * ALPHA).conj().T
    expect(abs(leftover[0, 1]) < 1e-12 and abs(leftover[1, 0]) < 1e-12, f"pair product off-diagonal {leftover}")
    expect(abs(abs(leftover[0, 0]) - 1) < 1e-12, "pair product is not a unit Z rotation")
    # Every circuit ends with the pre-readout delay (D3 excepted) and a six-qubit final measure.
    circuits = {json.loads(t)["name"]: json.loads(t) for r, t in files.items() if r.startswith("circuits/")}
    expect(list(circuits) == list(NAMES), f"circuits {list(circuits)}")
    for name, c in circuits.items():
        ops = c["instructions"]
        expect(ops[-1] == seq.op("measure", qubits, key="f"), f"{name}: final measure")
        delayed = ops[-2] == seq.op("delay", qubits, duration=seq.PRE_READOUT_SECONDS)
        expect(delayed == (name != "d3-ro1-now"), f"{name}: pre-readout delay")
        expect(sum(o["name"] == "prx" for o in ops) == len(qubits) * len(pulses_of(name)), f"{name}: prx count")
    probe = seq.load_json(PROBE_CASE / "circuits/unitary-n16-s0p.json")
    expect(circuits["d4-unitary-n16"]["instructions"] == probe["instructions"], "D4 is not the probe circuit")
    # The model: D4 is the main case's unitary arm; every circuit's ideal P(0) is cos(4 pi/9)^2.
    cal = excerpt["qubits"][qubits[0]]
    unitary = seq.bloch_z(
        "unitary", 16, cal["t1_s"], cal["t2_s"], seq.PRX_LAYER_SECONDS, 0.0, 1.0, cal["prx_p"], paired=False
    )
    got = evolve(pulses_of("d4-unitary-n16"), cal["t1_s"], cal["t2_s"], cal["prx_p"], 1.0)
    expect(abs(got - unitary) < 1e-12, f"D4 model {got} against the unitary arm {unitary}")
    for name in CORRECTED:
        ideal = (1 + evolve(pulses_of(name), 1e9, 1e9, 0.0, 1.0)) / 2
        expect(abs(ideal - IDEAL) < 1e-9, f"{name}: ideal {ideal}")
    prediction = json.loads(files["prediction.json"])
    bill = prediction["billing"]
    expect(bill["billed_seconds"] <= 1 and bill["credits"] <= MAX_CREDITS[QC], f"billing {bill}")
    expect(
        json.loads(files["cases.json"])["jobs"][0]["max_credits"] == {"garnet": 1.0, "garnet:mock": 0.0}, "max_credits"
    )

    # Synthetic devices off the model: each pattern reads as its cause.
    def verdict(**over: Any) -> dict[str, Any]:
        devices = {q: device_of(cal, **over) for q, cal in excerpt["qubits"].items()}
        return evaluate(synthetic_counts(excerpt, devices), prediction, excerpt)["diagnosis"]

    quiet = verdict()
    expect(quiet["verdict"] == "no_excess", f"a model device reads {quiet['verdict']}")
    loss = verdict(wait_t1_s=6e-6)
    expect(loss["verdict"] == "readout_loss", f"idle loss reads {loss}")
    phase = verdict(advance=0.1)
    expect(phase["verdict"] == "phase" and phase["ranking_ok"], f"axis phase reads {phase}")
    expect(
        not phase["rebuild_with_pi2_pairs"] or phase["verdict"] == "phase", "the rebuild flag contradicts the verdict"
    )
    mixed = verdict(advance=0.1, wait_t1_s=6e-6)
    expect(mixed["verdict"] == "neither", f"both causes read {mixed['verdict']}")
    # The thresholds of the rules.
    expect(abs(pooled([(0.1, 0.1), (0.3, 0.1)])[0] - 0.2) < 1e-12, "pooled estimate")
    return (
        f"measurement diagnostic: {len(NAMES)} circuits on {', '.join(qubits)}, {SHOTS} shots, "
        f"{bill['execution_seconds']:.2f} s predicted execution, {bill['worst_case_runtime_seconds']:.2f} s worst-case "
        f"runtime, {bill['credits']} credits; the pair product, the circuits, the model and the three patterns hold"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    bd = sub.add_parser("build")
    bd.add_argument("directory", type=Path)
    group = bd.add_mutually_exclusive_group(required=True)
    group.add_argument("--calibration-dir", type=Path)
    group.add_argument("--live", action="store_true", help="read Garnet's current calibration set (network)")
    sub.add_parser("check").add_argument("directory", type=Path)
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
    an.add_argument("--mock", action="store_true", help="analyze a garnet:mock run; its numbers decide nothing")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        if args.live:
            with tempfile.TemporaryDirectory() as scratch:
                fetch_live(Path(scratch))
                write(args.directory, Path(scratch))
        else:
            write(args.directory, args.calibration_dir)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "analyze":
        text = dump(analyze(args.run_dir, args.mock))
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise ValueError(f"{args.out} differs from the recomputation")
            print(f"{args.out}: replays byte for byte")
        else:
            args.out.write_text(text, encoding="utf-8")
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
