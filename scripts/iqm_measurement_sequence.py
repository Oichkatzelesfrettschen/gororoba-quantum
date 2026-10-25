"""IQM Garnet case of the measurement-sequence pinching test: does a mid-circuit measurement act as ideal pinching?

Ideal pinching is the nonselective projective measurement in Z, rho -> sum_m |m><m| rho |m><m|. The case drives four
pairwise uncoupled qubits (QB1, QB3, QB7, QB14) in parallel with N rotations of THETA/N about X, THETA = 8 pi/9, and
reads a final Z measurement. A sign s = +-1 flips every rotation; the four signed circuits of each (arm, N) run in
the order +, -, -, + (docs/notes/iqm/README.md, "Batch order"). Three arms:

- measure: a Z measurement after each rotation, outcomes recorded and never conditioning anything. A pinched qubit's
  Bloch z multiplies by cos(THETA/N) per step, so P0 = (1 + cos(THETA/N)^N)/2: 0.030 at N = 1 and 0.891 at N = 16.
- unitary (N = 16 only): the same rotations back to back with no mid-circuit operation. They compose to one rotation
  of THETA, so the ideal P0 is cos(THETA/2)^2 = 0.030. This is the mutation null: it removes the measurements and
  nothing else of consequence, since the compiled rotation layer lasts 40 ns.
- delay (every N): each mid-circuit measure replaced by a `delay` of the measure operation's duration. It is the
  elapsed-time control. Idle time dephases the qubit, which is a partial Z measurement of its own, so its P0 rises
  with N without any measurement; the arm quantifies how much of the measure arm's Zeno effect idle dephasing
  alone produces. It decides nothing.

- settle (N = 16 only): the measure arm with a `delay` of SETTLE_SECONDS = 2.0 us after each mid-circuit measure,
  several ring-down times of the readout resonator (docs/notes/ibm_quantum/heron-r2-readout-resonator.md records no
  Garnet figure; docs/notes/quantum_inspire/tuna-17.md, "Readout ring-down results", holds the repository's ring-down
  design). Its ideal P0 equals the measure arm's. It supports the departure decision and decides nothing: where a
  qubit departs, the model-adjusted difference (settle minus measure, each against its own T1 model) within
  Z_DECIDE standard errors of zero is a match that excludes a readout tail as the cause, and at least Z_DECIDE
  standard errors above zero attributes part of the departure to the tail. A readout-induced frequency shift that
  outlasts the measure enters only during the next prx, at second order in delta*tau; for tau <= 100 ns and
  delta <= 2 pi 100 kHz it moves the N = 16 flip probability by about 2.5e-6 per step, far below the departure
  threshold, so a larger departure needs this control to be read as measurement-induced.

Idle. The circuit-job body takes a native `delay` operation with a duration in seconds, at least that long and
rounded up to hardware granularity (docs/notes/iqm/docs/iqm-client/api/iqm.iqm_client.models.md, operation table and
"Delay"; docs/notes/iqm/os-4.7.md, "Client", lists `delay` in every Target). Garnet's dynamic quantum architecture
lists no `delay` gate, so acceptance on the QPU is settled by the garnet:mock run. The delay lasts
MEASURE_WINDOW_SECONDS, the compiled duration of a mid-circuit measure on garnet:mock (calibration set f04fe114),
which five single-circuit probe jobs fix from the compiler's per-shot qpu_execution estimates (see the constant). It
exceeds the acquisition_delay + integration_length of the calibration (1.024 us) by the post-acquisition time of the
measure operation, and the QPU job's own estimate is compared with the case's predicted schedule in `analyze`. One
joint measure over the four qubits holds all of them for that time.

Initialization. The job runs one active-reset cycle without heralding. All-zeros heralding over four qubits keeps
about three quarters of the shots and passive reset takes 316 us per shot against 37.5 us (docs/design/
iqm-garnet-timing-pilot.md). Rotations and pinching act linearly on the Bloch z, so an initialization flip
probability p scales the final z by (1 - 2p), the factor the per-qubit ro0 and ro1 circuits measure, and the
readout correction removes it exactly. T1 relaxation toward |0> is the non-unital residue and enters at second
order. ro1 uses a pi pulse, whose own over-rotation the correction absorbs into the readout scale.

Preregistered decisions, per qubit, from the readout-corrected final P0 pooled over the four signed circuits, with
standard errors that propagate the binomial variances of the arm and of ro0 and ro1 through the correction by the
delta method:

- the mutation test passes when the N = 16 contrast measure minus unitary exceeds CONTRAST_MIN = 0.5 by at least
  Z_DECIDE = 3 standard errors;
- the device departs from ideal pinching when the measured N = 16 measure-arm P0 lies below the prediction of an
  ideal projective measurement by at least Z_DECIDE standard errors. The prediction (prediction.json) iterates the
  Bloch z: a rotation, an ideal pinch, then T1 relaxation toward |0> over the rotation and the measure window. T2
  does not enter, because the state is diagonal after every measurement. The calibration's T1, the window and
  the readout errors are its inputs.

Descriptive outputs, deciding nothing: the delay arm's measured and modeled (T1 and T2) P0 per N and their
difference, the delay minus unitary difference at N = 16, the per-N measure-arm deficit against the ideal, the fit
P0(N) = (1 + ((1 - 2 eps) cos(THETA/N))^N)/2 for eps per qubit (weighted least squares, no randomness), the
transition rate between consecutive mid-circuit outcomes against sin(THETA/(2N))^2.

The case draws no random number; it holds no seed.

Usage: "$PYTHON" scripts/iqm_measurement_sequence.py (build DIR [--calibration-dir DIR] | check DIR
       | analyze RUN_DIR --out FILE [--replay] | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, ceiling_credits, dump, run_facts  # noqa: E402
from iqm_platform import sha256  # noqa: E402

from parallel import ordered_map  # noqa: E402

CASE = "measurement-sequence-pinching"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
JOB = "pinching"
CALIBRATION_DIR = ROOT / "docs/evidence/iqm/qc/garnet/calibration"
EXCERPT = "calibration/excerpt.json"
OPTIONS: dict[str, Any] = {"heralding_mode": "none", "active_reset_cycles": 1}

THETA = 8 * math.pi / 9
STEPS = (1, 2, 4, 8, 16)
TOP_STEPS = 16
SIGNS = (1, -1, -1, 1)
ARMS = ("measure", "delay", "unitary", "settle")
ARM_STEPS = {"measure": STEPS, "delay": STEPS, "unitary": (TOP_STEPS,), "settle": (TOP_STEPS,)}
# Idle after each mid-circuit measure of the settle arm: several resonator ring-down times of a few hundred ns.
SETTLE_SECONDS = 2.0e-6
PINCHED_ARMS = ("measure", "settle")
QUBITS = ("QB1", "QB3", "QB7", "QB14")
FINAL_KEY = "f"
GRANULARITY_PS = 4000
# Compiled schedule of garnet:mock (calibration set f04fe114): the qpu_execution estimate per shot, the job's
# execution_runtime_estimate_seconds less the fixed 1.6 s over 100 shots, of five single-circuit probe jobs on QB1,
# QB3, QB7 and QB14 (results/iqm/cases/measurement-timing-probe):
#   ro0 01a1747a-dd17-76ae-abf5-cb2840e5bdbd       8.684 us
#   unitary-n16 01a1747a-74f4-7343-90cf-309ff22ec8aa  9.324 us -> (9.324 - 8.684)/16 = 40 ns per prx layer
#   measure-n16 01a1747a-9d43-72dd-8656-a44458628ca9 37.676 us -> (37.676 - 9.324)/16 = 1.772 us per measure
#   measure-n1  01a1747a-d133-7756-8fae-5bcfde902635 10.496 us -> 10.496 - 8.684 - 0.040 = 1.772 us
#   delay-n16   01a1747a-ab9e-77d1-bc48-4f93ad45b5a8 25.708 us -> (25.708 - 9.324)/16 = 1.024 us per delay,
#                                                                 the duration that probe's circuit carried
ESTIMATOR_BASE_SECONDS = 8.684e-6
PRX_LAYER_SECONDS = 40e-9
MEASURE_WINDOW_SECONDS = 1.772e-6

SHOTS = 2400
# Seconds of execution per active-reset shot of a one-prx circuit, measured on Garnet QB1 by the reset and billing
# pilot (docs/design/iqm-garnet-timing-pilot.md); each prx layer and mid-circuit measure or delay adds its duration.
ACTIVE_SHOT_SECONDS = 0.0000375
# Billing is ceil(runtime); collect cancels a run within 1.0 s of the seconds max_credits buys (iqm_jobs.CANCEL_MARGIN),
# so the shot schedule plus JOB_SECONDS stays at least PLAN_HEADROOM below them.
MAX_CREDITS = {"garnet": 5.0, "garnet:mock": 0.0}
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
PLAN_HEADROOM = 2.0
MAX_BILLED_SECONDS = 10.0
GARNET_MAX_CIRCUITS = 100
GARNET_MAX_INSTRUCTIONS = 10000

Z_DECIDE = 3.0
CONTRAST_MIN = 0.5
# README, "Reset": one active-reset cycle leaves a qubit about 6.8 % excited; the prediction assumes it.
ACTIVE_RESET_EXCITED = 0.068
FIT_GRID = [-0.05 + 0.0005 * i for i in range(1001)]


def ideal_measure(n: int) -> float:
    """Final P0 of the pinched chain of n rotations of THETA/n."""
    return (1 + math.cos(THETA / n) ** n) / 2


def ideal_delay() -> float:
    """Final P0 of the coherent chain, which composes to one rotation of THETA."""
    return (1 + math.cos(THETA)) / 2


def ideal_arm(arm: str, n: int) -> float:
    return ideal_measure(n) if arm in PINCHED_ARMS else ideal_delay()


def ideal_flip(n: int) -> float:
    """Probability that consecutive mid-circuit outcomes differ: a pinched qubit rotates by THETA/n."""
    return math.sin(THETA / (2 * n)) ** 2


def model_p0(n: int, eps: float) -> float:
    return (1 + math.pow((1 - 2 * eps) * math.cos(THETA / n), n)) / 2


def sign_tag(sign: int) -> str:
    return "p" if sign > 0 else "m"


def group_names(arm: str, n: int) -> list[str]:
    return [f"{arm}-n{n}-s{i}{sign_tag(s)}" for i, s in enumerate(SIGNS)]


RO_NAMES = ("ro0", "ro1")


def circuit(name: str, arm: str | None, n: int, sign: int, delay_seconds: float) -> dict[str, Any]:
    """n rotations of sign*THETA/n on every qubit, each followed by a keyed measure or a delay, then the final
    measure."""
    instructions: list[dict[str, Any]] = []
    for step in range(n if arm else 0):
        angle = sign * THETA / n
        instructions += [{"name": "prx", "locus": [q], "args": {"angle": angle, "phase": 0.0}} for q in QUBITS]
        if arm in PINCHED_ARMS:
            instructions.append({"name": "measure", "locus": list(QUBITS), "args": {"key": f"m{step}"}})
        if arm == "settle":
            instructions.append({"name": "delay", "locus": list(QUBITS), "args": {"duration": SETTLE_SECONDS}})
        elif arm == "delay":
            instructions.append({"name": "delay", "locus": list(QUBITS), "args": {"duration": delay_seconds}})
    instructions.append({"name": "measure", "locus": list(QUBITS), "args": {"key": FINAL_KEY}})
    return {"name": name, "instructions": instructions}


def ro_circuit(name: str) -> dict[str, Any]:
    out = circuit(name, None, 0, 1, 0.0)
    if name.startswith("ro1"):
        flips = [{"name": "prx", "locus": [q], "args": {"angle": math.pi, "phase": 0.0}} for q in QUBITS]
        out["instructions"] = [*flips, *out["instructions"]]
    return out


def circuits_of(delay_seconds: float) -> list[dict[str, Any]]:
    """The job's circuit list: per N the measure group beside the delay group, then the readout calibration."""
    out: list[dict[str, Any]] = []
    for n in STEPS:
        for arm in ARMS:
            if n in ARM_STEPS[arm]:
                out += [
                    circuit(name, arm, n, s, delay_seconds) for name, s in zip(group_names(arm, n), SIGNS, strict=True)
                ]
    out += [ro_circuit(name) for name in RO_NAMES]
    return out


def mid_seconds(c: dict[str, Any]) -> float:
    """Time of the mid-circuit operations of a circuit: a measure at the compiled window, a delay at its duration."""
    return sum(
        MEASURE_WINDOW_SECONDS if op["name"] == "measure" else op["args"]["duration"]
        for op in c["instructions"][:-1]
        if op["name"] in ("measure", "delay")
    )


def layers_of(c: dict[str, Any]) -> int:
    return sum(1 for op in c["instructions"] if op["name"] == "prx" and op["locus"] == [QUBITS[0]])


def shot_seconds(c: dict[str, Any]) -> float:
    """Upper bound of one shot for billing: the active-reset shot measured on Garnet, plus the rotation layers and
    each mid-circuit measure or delay."""
    return ACTIVE_SHOT_SECONDS + layers_of(c) * PRX_LAYER_SECONDS + mid_seconds(c)


def estimator_shot_seconds(c: dict[str, Any]) -> float:
    """The compiler's qpu_execution estimate per shot: the ro0 shot plus the same terms."""
    return ESTIMATOR_BASE_SECONDS + layers_of(c) * PRX_LAYER_SECONDS + mid_seconds(c)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def excerpt_of(calibration_dir: Path) -> dict[str, Any]:
    """The calibration facts the case rests on, from a set, its metrics and its architecture that describe one
    calibration set: per-qubit T1, T2, readout errors and measure timing, and the couplers
    among the case's qubits."""
    paths = {name: calibration_dir / name for name in ("set.json", "metrics.json", "dynamic-quantum-architecture.json")}
    calibration_set, metrics, architecture = (load_json(p) for p in paths.values())
    identity = calibration_set["observation_set_id"]
    if metrics.get("describes_id") != identity or architecture.get("calibration_set_id") != identity:
        raise ValueError(f"{calibration_dir}: the set, metrics and architecture do not all describe set {identity}")
    values = {o["dut_field"]: o["value"] for o in calibration_set["observations"] if not o.get("invalid")}
    characterization = {o["dut_field"]: o["value"] for o in metrics["observations"] if not o.get("invalid")}
    per_qubit: dict[str, Any] = {}
    for q in QUBITS:
        gate = f"gates.measure.constant.{q}"
        per_qubit[q] = {
            "t1_s": characterization[f"characterization.model.{q}.t1_time"],
            "t2_s": characterization[f"characterization.model.{q}.t2_time"],
            "e01": characterization[f"metrics.ssro.measure.constant.{q}.error_0_to_1"],
            "e10": characterization[f"metrics.ssro.measure.constant.{q}.error_1_to_0"],
            "probe_duration_s": values[f"{gate}.duration"],
            "acquisition_delay_s": values[f"{gate}.acquisition_delay"],
            "integration_length_s": values[f"{gate}.integration_length"],
        }
    if not set(QUBITS) <= set(architecture["qubits"]):
        raise ValueError(f"{calibration_dir}: the architecture lacks one of {QUBITS}")
    cz_loci = [
        tuple(locus) for impl in architecture["gates"]["cz"]["implementations"].values() for locus in impl["loci"]
    ]
    coupled = sorted(f"{a}-{b}" for a, b in cz_loci if a in QUBITS and b in QUBITS)
    return {
        "schema": "iqm-measurement-sequence-calibration-v1",
        "calibration_set": identity,
        "source_sha256": {name: sha256(p.read_bytes()) for name, p in paths.items()},
        "couplers_among_qubits": coupled,
        "qubits": per_qubit,
    }


def acquisition_ps(excerpt: dict[str, Any]) -> int:
    """The longest acquisition_delay + integration_length of the qubits, rounded up to the channel granularity; the
    compiled measure window exceeds it and is not derived from it."""
    longest = max(
        round((q["acquisition_delay_s"] + q["integration_length_s"]) * 1e12) for q in excerpt["qubits"].values()
    )
    return -(-longest // GRANULARITY_PS) * GRANULARITY_PS


def bloch_z(arm: str, n: int, t1: float, t2: float, tau: float, eps: float = 0.0) -> float:
    """Final Bloch z of the chain from |0> with T1 and Ramsey T2 relaxation over tau per step.

    Each step rotates by THETA/n about X, then pinches (the measure arm zeroes the transverse part and loses a
    fraction eps of z to transitions) or leaves the state coherent (delay and unitary arms), then relaxes for tau.
    The measure arm's state is diagonal after the pinch, so t2 never reaches its result.
    """
    y, z = 0.0, 1.0
    c, s = math.cos(THETA / n), math.sin(THETA / n)
    for _ in range(n):
        y, z = y * c - z * s, y * s + z * c
        if arm in PINCHED_ARMS:
            y = 0.0
            z *= 1 - 2 * eps
        y *= math.exp(-tau / t2)
        z = 1 - (1 - z) * math.exp(-tau / t1)
    return z


def var(k: int, n: int) -> float:
    """Binomial variance of k/n, from the Agresti-Coull-shifted proportion so that k = 0 or k = n keeps a spread."""
    p = (k + 1) / (n + 2)
    return p * (1 - p) / n


def corrected_p0(x: list[float]) -> float:
    """P0 from the observed P(1) of a circuit and of ro0 and ro1: ro0 and ro1 read z0 = o + s and z1 = o - s."""
    z0, z1 = 1 - 2 * x[1], 1 - 2 * x[2]
    scale = (z0 - z1) / 2
    if scale <= 0:
        raise ValueError(f"readout contrast {scale} of ro0 and ro1 is not positive")
    return (1 + ((1 - 2 * x[0]) - (z0 + z1) / 2) / scale) / 2


def propagate(f: Callable[[list[float]], float], x: list[float], variances: list[float]) -> tuple[float, float]:
    """f(x) and its standard error from independent variances, by the delta method with central differences."""
    total = 0.0
    for i, v in enumerate(variances):
        up, down = list(x), list(x)
        up[i] += 1e-6
        down[i] -= 1e-6
        total += ((f(up) - f(down)) / 2e-6) ** 2 * v
    return f(x), math.sqrt(total)


def finite(x: float) -> float | None:
    return x if math.isfinite(x) else None


def fit_eps(points: list[tuple[int, float, float]]) -> dict[str, Any]:
    """Weighted least squares of P0(N) = model_p0(N, eps) over (N, P0, se): grid, golden section, curvature."""

    def chi2(eps: float) -> float:
        return sum(((p - model_p0(n, eps)) / se) ** 2 for n, p, se in points)

    best = min(range(len(FIT_GRID)), key=lambda i: chi2(FIT_GRID[i]))
    low, high = FIT_GRID[max(best - 1, 0)], FIT_GRID[min(best + 1, len(FIT_GRID) - 1)]
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(100):
        a, b = high - ratio * (high - low), low + ratio * (high - low)
        low, high = (low, b) if chi2(a) < chi2(b) else (a, high)
    eps = (low + high) / 2
    h = 1e-4
    curvature = (chi2(eps + h) - 2 * chi2(eps) + chi2(eps - h)) / h**2
    return {
        "eps": eps,
        "eps_se": finite(math.sqrt(2 / curvature)) if curvature > 0 else None,
        "chi2": chi2(eps),
        "dof": len(points) - 1,
        "at_grid_edge": best in (0, len(FIT_GRID) - 1),
    }


def decide(contrast: float, contrast_se: float, shortfall: float, shortfall_se: float) -> dict[str, Any]:
    """The two preregistered decisions of one qubit: the measure-minus-unitary contrast against CONTRAST_MIN, and
    the measure arm's shortfall below the ideal-projective prediction."""
    if contrast_se <= 0 or shortfall_se <= 0:
        raise ValueError("a decision needs positive standard errors")
    z_mutation = (contrast - CONTRAST_MIN) / contrast_se
    z_shortfall = shortfall / shortfall_se
    return {
        "mutation_test": {"z": z_mutation, "passes": z_mutation >= Z_DECIDE},
        "departs_from_ideal_pinching": {"z": z_shortfall, "departs": z_shortfall >= Z_DECIDE},
    }


def pooled(counts: dict[str, Any], qubit: str, names: list[str]) -> list[int]:
    total = [0, 0]
    for name in names:
        for i, value in enumerate(counts[name]["final"][qubit]):
            total[i] += value
    return total


def pooled_two_state(counts: dict[str, Any], qubit: str, names: list[str]) -> tuple[int, int]:
    """(ones, shots) of the named circuits."""
    n0, n1 = pooled(counts, qubit, names)
    return n1, n0 + n1


def difference(x: list[float]) -> float:
    """P0 of one circuit group minus another's, both corrected with the same ro0 and ro1: x = [p1_a, p1_b, r0, r1]."""
    return corrected_p0([x[0], x[2], x[3]]) - corrected_p0([x[1], x[2], x[3]])


def implied_loss(z_measured: float, t1: float, t2: float, tau: float) -> float:
    """The per-step z loss eps at which the measure arm's modeled final z equals z_measured (bisection)."""
    low, high = -0.05, 0.5
    for _ in range(80):
        middle = (low + high) / 2
        if bloch_z("measure", TOP_STEPS, t1, t2, tau, middle) > z_measured:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def model_tables(qubits: dict[str, Any]) -> dict[str, Any]:
    """Per qubit the model's P0 tables with the relaxation inputs the settle comparison needs."""
    return {q: {**row["p0"], "inputs": row["departure_inputs"]} for q, row in qubits.items()}


def evaluate_qubit(item: tuple[str, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """The decisions and descriptive outputs of one qubit from the per-circuit counts and the model's P0 tables."""
    qubit, counts, tables = item
    k0, n0 = pooled_two_state(counts, qubit, ["ro0"])
    k1, n1 = pooled_two_state(counts, qubit, ["ro1"])
    r0, r1 = k0 / n0, k1 / n1
    z0, z1 = 1 - 2 * r0, 1 - 2 * r1
    p0: dict[str, dict[str, Any]] = {arm: {} for arm in ARMS}
    for arm in ARMS:
        for n in ARM_STEPS[arm]:
            k, shots = pooled_two_state(counts, qubit, group_names(arm, n))
            value, se = propagate(corrected_p0, [k / shots, r0, r1], [var(k, shots), var(k0, n0), var(k1, n1)])
            ideal = ideal_arm(arm, n)
            modeled_p0 = tables[arm][str(n)]
            p0[arm][str(n)] = {
                "p0": value,
                "se": se,
                "ideal": ideal,
                "deficit": ideal - value,
                "modeled": modeled_p0,
                "measured_minus_modeled": value - modeled_p0,
            }

    def between(arm_a: str, arm_b: str) -> tuple[float, float]:
        ka, na = pooled_two_state(counts, qubit, group_names(arm_a, TOP_STEPS))
        kb, nb = pooled_two_state(counts, qubit, group_names(arm_b, TOP_STEPS))
        return propagate(difference, [ka / na, kb / nb, r0, r1], [var(ka, na), var(kb, nb), var(k0, n0), var(k1, n1)])

    contrast, contrast_se = between("measure", "unitary")
    dephasing, dephasing_se = between("delay", "unitary")
    last = p0["measure"][str(TOP_STEPS)]
    shortfall = last["modeled"] - last["p0"]
    # Descriptive support for the departure decision: the settle arm waits SETTLE_SECONDS after each measure, so a
    # readout tail that lowers the measure arm's P0 is absent from it. The settle arm relaxes longer, which raises
    # its P0 on any device, so its measured P0 is compared with the settle prediction at the per-step z loss the
    # measure arm implies.
    inputs = tables["inputs"]
    t1, t2 = inputs["t1_s"], inputs["t2_s_delay_and_unitary_only"]
    tau = inputs["prx_layer_s"] + inputs["measure_window_s"]
    ks, ns = pooled_two_state(counts, qubit, group_names("settle", TOP_STEPS))
    km_, nm_ = pooled_two_state(counts, qubit, group_names("measure", TOP_STEPS))

    def tail_gap(x: list[float]) -> float:
        loss = implied_loss(2 * corrected_p0([x[1], x[2], x[3]]) - 1, t1, t2, tau)
        predicted = (1 + bloch_z("settle", TOP_STEPS, t1, t2, tau + SETTLE_SECONDS, loss)) / 2
        return corrected_p0([x[0], x[2], x[3]]) - predicted

    variances = [var(ks, ns), var(km_, nm_), var(k0, n0), var(k1, n1)]
    gap, gap_se = propagate(tail_gap, [ks / ns, km_ / nm_, r0, r1], variances)
    z_gap = gap / gap_se
    settle = {
        "raw_difference": p0["settle"][str(TOP_STEPS)]["p0"] - last["p0"],
        "measure_implied_loss": implied_loss(2 * last["p0"] - 1, t1, t2, tau),
        "tail_gap": gap,
        "se": gap_se,
        "z": z_gap,
        "verdict": "tail_attributed"
        if z_gap >= Z_DECIDE
        else "match"
        if abs(z_gap) < Z_DECIDE
        else "settle_below_measure",
    }
    transitions: dict[str, Any] = {}
    for n in STEPS[1:]:
        flips = sum(counts[name]["flips"][qubit][0] for name in group_names("measure", n))
        pairs = sum(counts[name]["flips"][qubit][1] for name in group_names("measure", n))
        transitions[str(n)] = {"rate": flips / pairs, "se": math.sqrt(var(flips, pairs)), "ideal": ideal_flip(n)}
    points = [(n, p0["measure"][str(n)]["p0"], p0["measure"][str(n)]["se"]) for n in STEPS]
    return {
        "readout": {"z0": z0, "z1": z1, "scale": (z0 - z1) / 2, "offset": (z0 + z1) / 2},
        "p0": p0,
        "contrast_n16": {
            "contrast": contrast,
            "se": contrast_se,
            "ideal": ideal_measure(TOP_STEPS) - ideal_delay(),
        },
        "departure_n16": {
            "prediction": last["modeled"],
            "measured": last["p0"],
            "shortfall": shortfall,
            "se": last["se"],
        },
        "decisions": decide(contrast, contrast_se, shortfall, last["se"]),
        "settle_n16": settle,
        "delay_arm": {
            "dephasing_zeno_n16": {
                "measured": dephasing,
                "se": dephasing_se,
                "modeled": tables["delay"][str(TOP_STEPS)] - tables["unitary"][str(TOP_STEPS)],
            }
        },
        "fit": fit_eps(points),
        "transitions": transitions,
    }


def evaluate(counts: dict[str, Any], tables: dict[str, Any]) -> dict[str, Any]:
    results = ordered_map(evaluate_qubit, [(q, counts, tables[q]) for q in QUBITS])
    return dict(zip(QUBITS, results, strict=True))


def tally(circuits: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, Any]:
    """Per circuit name: shots, the final readout's counts of states 0 and 1 per qubit, and for the measure arm
    the shots whose consecutive mid-circuit outcomes differ, summed over its consecutive pairs, per qubit."""
    out: dict[str, Any] = {}
    for c, result in zip(circuits, results, strict=True):
        final = result[FINAL_KEY]
        row: dict[str, Any] = {"shots": len(final), "final": {}}
        for position, qubit in enumerate(QUBITS):
            counts = [0, 0]
            for shot in final:
                if shot[position] not in (0, 1):
                    raise ValueError(f"{c['name']}: outcome {shot[position]} is not a state 0 or 1")
                counts[shot[position]] += 1
            row["final"][qubit] = counts
        mids = [
            op["args"]["key"] for op in c["instructions"] if op["name"] == "measure" and op["args"]["key"] != FINAL_KEY
        ]
        if len(mids) > 1:
            row["flips"] = {}
            for position, qubit in enumerate(QUBITS):
                flips = sum(
                    1
                    for a, b in zip(mids, mids[1:], strict=False)
                    for x, y in zip(result[a], result[b], strict=True)
                    if x[position] != y[position]
                )
                row["flips"][qubit] = [flips, len(final) * (len(mids) - 1)]
        out[c["name"]] = row
    return out


def device_counts(models: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Expected counts of a model device, rounded to whole shots. Each model holds, per arm and N, the true final z
    from a perfect start, the consecutive-outcome flip probability per N, the readout errors, the initialization
    excitation p_init."""
    counts: dict[str, Any] = {}

    def put(name: str, z: dict[str, float], flips: dict[str, float] | None, n: int) -> None:
        row: dict[str, Any] = {"shots": SHOTS, "final": {}}
        for q, model in models.items():
            observed = (
                (1 - model["e01"] - model["e10"]) * (1 - 2 * model["p_init"]) * z[q] + model["e10"] - model["e01"]
            )
            k0 = round(SHOTS * (1 + observed) / 2)
            row["final"][q] = [k0, SHOTS - k0]
        if flips is not None:
            row["flips"] = {q: [round(SHOTS * (n - 1) * flips[q]), SHOTS * (n - 1)] for q in models}
        counts[name] = row

    for arm in ARMS:
        for n in ARM_STEPS[arm]:
            z = {q: m["z"][arm][str(n)] for q, m in models.items()}
            flips = {q: m["flip"][str(n)] for q, m in models.items()} if arm in PINCHED_ARMS and n > 1 else None
            for name in group_names(arm, n):
                put(name, z, flips, n)
    ro = {"ro0": 1.0, "ro1": -1.0}
    for name, sign in ro.items():
        put(name, dict.fromkeys(models, sign), None, 0)
    return counts


def modeled(
    excerpt: dict[str, Any], eps: dict[str, float] | None = None, relax: bool = True
) -> dict[str, dict[str, Any]]:
    """Model devices from the calibration's T1, T2 and readout errors.

    With relax, the Bloch iteration of bloch_z over one prx and, for the measure and delay arms, one trigger per step,
    the measure arm losing eps of z per step (zero by default, the ideal projective prediction). Without relax, the
    closed laws: the pinching law with eps for the measure arm and one rotation of THETA for the others.
    """
    trigger = MEASURE_WINDOW_SECONDS
    loss = eps or dict.fromkeys(excerpt["qubits"], 0.0)
    models: dict[str, dict[str, Any]] = {}
    for q, cal in excerpt["qubits"].items():
        z: dict[str, dict[str, float]] = {arm: {} for arm in ARMS}
        for arm in ARMS:
            for n in ARM_STEPS[arm]:
                if relax:
                    tau = PRX_LAYER_SECONDS + (0.0 if arm == "unitary" else trigger)
                    tau += SETTLE_SECONDS if arm == "settle" else 0.0
                    z[arm][str(n)] = bloch_z(arm, n, cal["t1_s"], cal["t2_s"], tau, loss[q])
                elif arm in PINCHED_ARMS:
                    z[arm][str(n)] = math.pow((1 - 2 * loss[q]) * math.cos(THETA / n), n)
                else:
                    z[arm][str(n)] = math.cos(THETA)
        flip = {str(n): (1 - (1 - 2 * loss[q]) * math.cos(THETA / n)) / 2 for n in STEPS}
        models[q] = {
            "z": z,
            "flip": flip,
            "e01": cal["e01"],
            "e10": cal["e10"],
            "p_init": ACTIVE_RESET_EXCITED,
        }
    return models


def p0_tables(models: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {q: {arm: {n: (1 + v) / 2 for n, v in m["z"][arm].items()} for arm in ARMS} for q, m in models.items()}


def predict(excerpt: dict[str, Any], shot: float, estimator_shot: float) -> dict[str, Any]:
    models = modeled(excerpt)
    tables = p0_tables(models)
    inputs = {
        q: {
            "t1_s": cal["t1_s"],
            "t2_s_delay_and_unitary_only": cal["t2_s"],
            "measure_window_s": MEASURE_WINDOW_SECONDS,
            "prx_layer_s": PRX_LAYER_SECONDS,
            "settle_idle_s": SETTLE_SECONDS,
            "e01": cal["e01"],
            "e10": cal["e10"],
            "p_init": models[q]["p_init"],
        }
        for q, cal in excerpt["qubits"].items()
    }
    expected = evaluate(
        device_counts(models), model_tables({q: {"p0": tables[q], "departure_inputs": inputs[q]} for q in models})
    )
    qubits: dict[str, Any] = {}
    for q in models:
        row = expected[q]
        qubits[q] = {
            "p0": tables[q],
            "departure_inputs": inputs[q],
            "contrast_n16": row["contrast_n16"]["contrast"],
            "contrast_se": row["contrast_n16"]["se"],
            "departure_se": row["departure_n16"]["se"],
            "dephasing_zeno_n16": tables[q]["delay"]["16"] - tables[q]["unitary"]["16"],
            "decisions_on_the_model_device": row["decisions"],
        }
    return {
        "calibration_set": excerpt["calibration_set"],
        "ideal": {
            "measure": {str(n): ideal_measure(n) for n in STEPS},
            "delay_and_unitary": ideal_delay(),
            "contrast_n16": ideal_measure(TOP_STEPS) - ideal_delay(),
        },
        "measure_window_seconds": MEASURE_WINDOW_SECONDS,
        "prx_layer_seconds": PRX_LAYER_SECONDS,
        "acquisition_window_seconds": acquisition_ps(excerpt) / 1e12,
        "timing_source": (
            "garnet:mock compiler estimates, calibration set f04fe114: ro0 8.684 us, unitary-n16 9.324 us, "
            "measure-n16 37.676 us, measure-n1 10.496 us and delay-n16 25.708 us per shot (jobs 01a1747a-dd17, "
            "01a1747a-74f4, 01a1747a-9d43, 01a1747a-d133, 01a1747a-ab9e)"
        ),
        "estimator_per_shot_seconds_all_circuits": estimator_shot,
        "probe_duration_seconds": max(q["probe_duration_s"] for q in excerpt["qubits"].values()),
        "per_shot_seconds_all_circuits": shot,
        "active_reset_excited": ACTIVE_RESET_EXCITED,
        "model": (
            "Bloch iteration from |0>: a rotation of THETA/N per step, then an ideal pinch (measure arm; T2 does not "
            "enter because the state is diagonal) or coherent evolution (delay and unitary arms), then T1 and "
            "Ramsey T2 relaxation over the rotation layer and, for measure and delay, one measure window; readout "
            "through the calibrated errors and an initialization excitation. The measure arm's N = 16 P0 is the "
            "departure prediction. decisions_on_the_model_device applies the run's estimator to the model's expected "
            "counts, so the mutation margin and the standard errors are those the analysis reports at the case's shots"
        ),
        "qubits": qubits,
    }


def build_files(excerpt: dict[str, Any]) -> dict[str, str]:
    if excerpt["couplers_among_qubits"]:
        raise ValueError(f"the qubits share couplers {excerpt['couplers_among_qubits']}")
    delay_seconds = MEASURE_WINDOW_SECONDS
    circuits = circuits_of(delay_seconds)
    if len(circuits) > GARNET_MAX_CIRCUITS or any(len(c["instructions"]) > GARNET_MAX_INSTRUCTIONS for c in circuits):
        raise ValueError("the job exceeds Garnet's circuits or instructions per job")
    files = {f"circuits/{c['name']}.json": dump(c) for c in circuits}
    shot = sum(shot_seconds(c) for c in circuits)
    estimator_shot = sum(estimator_shot_seconds(c) for c in circuits)
    expected = round(SHOTS * shot, 3)
    budget = MAX_CREDITS[QC] / PRICE[QC]
    if JOB_SECONDS + expected > budget - PLAN_HEADROOM or math.ceil(JOB_SECONDS + expected) > MAX_BILLED_SECONDS:
        raise ValueError(f"{expected} s of shots plus {JOB_SECONDS} s leave less than {PLAN_HEADROOM} s of {budget} s")
    if ceiling_credits(expected, PRICE[QC]) > MAX_CREDITS[QC]:
        raise ValueError("the expected bill exceeds max_credits")
    job = {
        "job": JOB,
        "circuits": [{"file": rel, "sha256": sha256(text.encode())} for rel, text in files.items()],
        "shots": SHOTS,
        # The job compiles against the calibration set the case was planned from, or fails if it is gone.
        "options": {**OPTIONS, "calibration_set_id": {QC: excerpt["calibration_set"]}},
        "expected_seconds": expected,
        "max_credits": MAX_CREDITS,
    }
    files["prediction.json"] = dump(predict(excerpt, shot, estimator_shot))
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Does a Garnet mid-circuit measurement act as ideal pinching, a nonselective projective "
                "measurement in Z, on QB1, QB3, QB7 and QB14, read by the Zeno build-up of N rotations of "
                "8 pi/9 over N against the same rotations with no measurement, with a delay of the measure "
                "duration as the elapsed-time control?"
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
    predicted = json.loads(files["prediction.json"])["qubits"]
    print(
        json.dumps(
            {
                "circuits": len(files) - 3,
                "calibration_set": json.loads(files[EXCERPT])["calibration_set"],
                "weakest_predicted_mutation_z": min(
                    v["decisions_on_the_model_device"]["mutation_test"]["z"] for v in predicted.values()
                ),
            }
        )
    )


def check(directory: Path) -> None:
    files = build_files(load_json(directory / EXCERPT))
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if present != set(files):
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ set(files))}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from its retained calibration excerpt")


def analyze(run_dir: Path) -> dict[str, Any]:
    facts = run_facts(run_dir)
    submission = load_json(run_dir / "submission.json")
    record = json.loads((run_dir / "raw/job.json").read_bytes())
    case = load_json(run_dir / "cases.json")
    prediction_bytes = (run_dir / "prediction.json").read_bytes()
    if sha256(prediction_bytes) != case.get("prediction_sha256"):
        raise ValueError(f"{run_dir}/prediction.json is not the prediction cases.json binds")
    if facts["statuses"] != {"completed": 1}:
        raise ValueError(f"{run_dir}: the job is {sorted(facts['statuses'])}; the analysis reads completed jobs")
    # Mock outcomes are random bits and never enter the analysis.
    if submission["qc"] != QC or case.get("case") != CASE:
        raise ValueError(f"{run_dir}: a {case.get('case')} run on {submission['qc']}, not a {CASE} run on {QC}")
    prediction = json.loads(prediction_bytes)
    if record["compilation"]["calibration_set_id"] != prediction["calibration_set"]:
        raise ValueError(f"{run_dir}: compiled against another calibration set than the case's")
    row = next(r for r in case["jobs"] if r["job"] == submission["job"])
    circuits = [load_json(run_dir / entry["file"]) for entry in row["circuits"]]
    counts = tally(circuits, json.loads((run_dir / "raw/measurements.json").read_bytes()))
    tables = model_tables(prediction["qubits"])
    predicted = prediction["estimator_per_shot_seconds_all_circuits"] * row["shots"]
    estimated = record["compilation"]["execution_runtime_estimate_seconds"] - JOB_SECONDS
    schedule: dict[str, Any] = {
        "predicted_qpu_execution_seconds": predicted,
        "estimated_qpu_execution_seconds": estimated,
        "ratio": estimated / predicted,
    }
    artifact = run_dir / "raw/runtime_estimates.json"
    if artifact.exists():
        schedule["runtime_estimates_sha256"] = sha256(artifact.read_bytes())
    return {
        "schema": "iqm-measurement-sequence-analysis-v1",
        "run": run_dir.name,
        "calibration_set": record["compilation"]["calibration_set_id"],
        "estimate_seconds": record["compilation"]["execution_runtime_estimate_seconds"],
        "runtime_seconds": record["metrics"]["runtime_seconds"],
        "billed_seconds": record["metrics"]["billed_seconds"],
        "charge": facts["charge"],
        "compiled_schedule": schedule,
        "qubits": evaluate(counts, tables),
    }


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def self_test() -> str:
    excerpt = excerpt_of(CALIBRATION_DIR)
    files = build_files(excerpt)
    expect(files == build_files(excerpt), "the build is not deterministic")
    # Exact ideals.
    expect(
        [round(ideal_measure(n), 4) for n in STEPS] == [0.0302, 0.5151, 0.6722, 0.8040, 0.8914],
        f"ideal P0 {[round(ideal_measure(n), 4) for n in STEPS]}",
    )
    expect(round(ideal_delay(), 4) == 0.0302, "the delay and unitary ideal is not 0.0302")
    expect(round(ideal_measure(16) - ideal_delay(), 4) == 0.8612, "the N = 16 contrast ideal is not 0.8612")
    expect(abs(ideal_flip(1) - (1 - math.cos(THETA)) / 2) < 1e-15, "the flip ideal at N = 1")
    for n in STEPS:
        expect(abs(model_p0(n, 0.0) - ideal_measure(n)) < 1e-15, f"the fit law at eps = 0 differs at N = {n}")
    # Circuit structure.
    case = json.loads(files["cases.json"])
    job = case["jobs"][0]
    expect(case["prediction_sha256"] == sha256(files["prediction.json"].encode()), "cases.json lacks the prediction")
    expect(job["max_credits"] == {"garnet": 5.0, "garnet:mock": 0.0}, f"max_credits {job['max_credits']}")
    expect(job["expected_seconds"] + JOB_SECONDS <= 8.0, f"{job['expected_seconds']} s of shots exceed the plan")
    expect(math.ceil(JOB_SECONDS + job["expected_seconds"]) * PRICE[QC] <= 5.0, "the expected bill exceeds 5 credits")
    circuits = [json.loads(text) for rel, text in files.items() if rel.startswith("circuits/")]
    expect(len(circuits) == 50 and len({c["name"] for c in circuits}) == 50, f"{len(circuits)} circuits")
    delay_seconds = MEASURE_WINDOW_SECONDS
    expect(delay_seconds > acquisition_ps(excerpt) / 1e12, "the measure window is under the acquisition window")
    expect(round(delay_seconds * 1e12) % GRANULARITY_PS == 0, "the measure window is off the 4 ns granularity")
    # The compiled-schedule model reproduces the five probe estimates (microseconds per shot).
    probes = {
        "ro0": (ro_circuit("ro0"), 8.684),
        "unitary-n16": (circuit("u", "unitary", 16, 1, 0.0), 9.324),
        "measure-n16": (circuit("m", "measure", 16, 1, 0.0), 37.676),
        "measure-n1": (circuit("m", "measure", 1, 1, 0.0), 10.496),
        "delay-n16": (circuit("d", "delay", 16, 1, 1.024e-6), 25.708),
    }
    for label, (probe, microseconds) in probes.items():
        expect(
            abs(estimator_shot_seconds(probe) * 1e6 - microseconds) < 1e-6, f"{label}: {estimator_shot_seconds(probe)}"
        )
    expect(
        abs(
            json.loads(files["prediction.json"])["estimator_per_shot_seconds_all_circuits"]
            - sum(estimator_shot_seconds(c) for c in circuits)
        )
        < 1e-15,
        "prediction.json lacks the estimator schedule",
    )
    by_name = {c["name"]: c for c in circuits}
    for arm in ARMS:
        for n in ARM_STEPS[arm]:
            names = group_names(arm, n)
            signs = []
            for name in names:
                ops = by_name[name]["instructions"]
                prx = [op for op in ops if op["name"] == "prx"]
                expect(len(prx) == 4 * n, f"{name}: {len(prx)} prx")
                signs.append(1 if prx[0]["args"]["angle"] > 0 else -1)
                expect(all(abs(op["args"]["angle"] - signs[-1] * THETA / n) < 1e-15 for op in prx), f"{name}: angles")
                measures = [op for op in ops if op["name"] == "measure"]
                delays = [op for op in ops if op["name"] == "delay"]
                keys = [op["args"]["key"] for op in measures]
                expect(len(set(keys)) == len(keys) and keys[-1] == FINAL_KEY, f"{name}: keys {keys}")
                if arm == "measure":
                    expect(len(measures) == n + 1 and not delays, f"{name}: {len(measures)} measures")
                elif arm == "settle":
                    expect(len(measures) == n + 1 and len(delays) == n, f"{name}: {len(measures)} measures")
                    expect(all(d["args"]["duration"] == SETTLE_SECONDS for d in delays), f"{name}: settle duration")
                    expect(
                        [op["name"] for op in ops[4:6]] == ["measure", "delay"],
                        f"{name}: delay does not follow measure",
                    )
                elif arm == "delay":
                    expect(len(measures) == 1 and len(delays) == n, f"{name}: {len(delays)} delays")
                    expect(all(d["args"]["duration"] == delay_seconds for d in delays), f"{name}: delay duration")
                else:
                    expect(len(measures) == 1 and not delays, f"{name}: a mid-circuit operation in the unitary arm")
                    expect(all(op["name"] == "prx" for op in ops[:-1]), f"{name}: not back-to-back rotations")
                expect(all(op["locus"] == list(QUBITS) for op in measures + delays), f"{name}: locus")
                expect({op["locus"][0] for op in prx} == set(QUBITS), f"{name}: prx qubits")
            expect(signs == list(SIGNS), f"{arm} N = {n}: sign order {signs}")
    expect([c["name"] for c in circuits[:8]] == group_names("measure", 1) + group_names("delay", 1), "arm order")
    expect(by_name["ro1"]["instructions"][0]["name"] == "prx" and len(by_name["ro0"]["instructions"]) == 1, "ro")
    tables = model_tables(json.loads(files["prediction.json"])["qubits"])
    planted = {"QB1": 0.0, "QB3": 0.004, "QB7": 0.02, "QB14": 0.0}

    def tilt(models: dict[str, dict[str, Any]]) -> None:
        for q, shift in zip(QUBITS, (0.01, 0.02, 0.03, 0.015), strict=True):
            models[q]["e01"], models[q]["e10"] = shift, 2 * shift

    # Planted eps on a relaxation-free device: the fit, and the flips are recovered.
    models = modeled(excerpt, planted, relax=False)
    tilt(models)
    result = evaluate(device_counts(models), tables)
    for q, eps in planted.items():
        row = result[q]
        fit = row["fit"]
        expect(fit["eps_se"] is not None and abs(fit["eps"] - eps) <= 4 * fit["eps_se"] + 1e-4, f"{q}: eps {fit}")
        for n in STEPS[1:]:
            rate = row["transitions"][str(n)]
            expect(abs(rate["rate"] - (1 - (1 - 2 * eps) * math.cos(THETA / n)) / 2) < 1e-3, f"{q}: flips {n}")
    # Planted eps on a device with the calibrated relaxation: the decisions.
    models = modeled(excerpt, planted)
    tilt(models)
    result = evaluate(device_counts(models), tables)
    for q, eps in planted.items():
        row = result[q]
        expect(row["decisions"]["mutation_test"]["passes"], f"{q}: the mutation test fails on a pinching device")
        expect(row["decisions"]["departs_from_ideal_pinching"]["departs"] == (eps != 0.0), f"{q}: departure {row}")
        for arm in ARMS:
            for n, value in row["p0"][arm].items():
                expect(
                    eps != 0.0 and arm in PINCHED_ARMS or abs(value["measured_minus_modeled"]) < 1e-3,
                    f"{q}: {arm} N = {n} departs from its model without a planted loss",
                )
    expect(result["QB7"]["delay_arm"]["dephasing_zeno_n16"]["modeled"] > 0.2, "idle dephasing produces no Zeno rise")
    # The settle arm reads a readout tail: a device whose measure arm alone loses z per step is attributed to it.
    base = modeled(excerpt)
    for q in planted:
        expect(result[q]["settle_n16"]["verdict"] == "match", f"{q}: settle {result[q]['settle_n16']}")
    tail = modeled(excerpt, planted)
    for q, model in tail.items():
        model["z"]["settle"] = base[q]["z"]["settle"]
    for q, row in evaluate(device_counts(tail), tables).items():
        expect(
            row["settle_n16"]["verdict"] == ("tail_attributed" if planted[q] else "match"),
            f"{q}: tail device settle {row['settle_n16']}",
        )
    # A device without pinching: the measure arm follows the unitary law.
    flat = modeled(excerpt)
    for model in flat.values():
        model["z"]["measure"] = {str(n): model["z"]["unitary"][str(TOP_STEPS)] for n in STEPS}
    for row in evaluate(device_counts(flat), tables).values():
        expect(not row["decisions"]["mutation_test"]["passes"], "the mutation test passes without pinching")
        expect(row["decisions"]["departs_from_ideal_pinching"]["departs"], "no departure without pinching")
    # The decision rule at its thresholds.
    expect(decide(0.5301, 0.01, 0.0, 0.01)["mutation_test"]["passes"], "3.01 standard errors above 0.5 fails")
    expect(not decide(0.5299, 0.01, 0.0, 0.01)["mutation_test"]["passes"], "2.99 standard errors above 0.5 passes")
    expect(decide(0.9, 0.01, 0.0301, 0.01)["departs_from_ideal_pinching"]["departs"], "a 3.01 shortfall is missed")
    expect(not decide(0.9, 0.01, 0.0299, 0.01)["departs_from_ideal_pinching"]["departs"], "a 2.99 shortfall departs")
    predicted = json.loads(files["prediction.json"])["qubits"]
    margin = min(v["decisions_on_the_model_device"]["mutation_test"]["z"] for v in predicted.values())
    return (
        f"measurement sequence pinching: {len(circuits)} circuits, {job['expected_seconds']} s of shots; the ideal "
        f"laws, circuit structure, planted eps, the no-pinching device and the decision thresholds hold; the "
        f"weakest predicted mutation margin is {margin:.1f} standard errors"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    bd = sub.add_parser("build")
    bd.add_argument("directory", type=Path)
    bd.add_argument("--calibration-dir", type=Path, default=CALIBRATION_DIR)
    sub.add_parser("check").add_argument("directory", type=Path)
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.calibration_dir)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "analyze":
        text = dump(analyze(args.run_dir))
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
