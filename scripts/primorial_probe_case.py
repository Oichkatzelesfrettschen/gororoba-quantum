"""Simulation design of the primorial coherence probes, the twirled gap-88 arms and the run's interleave schedule.

docs/design/primorial-cover-joint-coherent-bounds.md reduces the gap-88 device question to the coherent tilt,
CZ conditional phase, static detuning and static ZZ of the chosen path. This script designs the hardware case
that measures them and decides the gap-88 run from them, on the ibm_kingston snapshot and the best and median
paths of docs/evidence/primorial_cover/noise.json:

1. **Detuning mapping.** A constant-amplitude pulse of Rabi rate Omega under a detuning Delta,
   exp(-i t (Omega X + Delta Z) / 2), equals primorial_bound_residuals' tilt RY(-beta) R RY(beta) with
   beta = Delta / Omega to first order (``detuned_pulse_check``). The gapless probe trains therefore measure
   the whole in-pulse Z action as tilt, the Ramsey idles measure the detuning, and every prediction applies
   the detuning to idles and CZs only (spec key ``detuning_gates``), so no in-pulse detuning is counted twice.
2. **Recovery and sensitivity.** gororoba_quantum/coherence_probes.py's circuits run noise-free through
   primorial_bound_residuals.law under injected parameter vectors (``RECOVERY_VECTORS``, every family at once)
   and the estimators return each parameter; the record keeps the largest error per estimate. The Jacobian
   of every estimate against every family parameter at zero is the probe's first-order response matrix.
3. **Noisy probes.** Each probe circuit compiles on the path as primorial_cover_noise.compile_arm compiles the
   gap-88 arms and runs under the snapshot's noise model with the coherent errors inserted as noiseless
   unitaries after each native gate, so the native gates keep their snapshot errors. The record keeps every
   estimate's bias against its injected value and its one-shot standard error, and the shots per circuit
   that resolve each decision threshold at three standard deviations: tilt at 0.2 of its sx and x gate-error
   bounds, CZ phase at 0.7 of its bound, detuning of 5 kHz and ZZ of 2 kHz.
4. **Twirled gap-88 arms.** The client-side Sampler of qiskit-ibm-runtime 0.50 twirls a static job by
   samplomatic's generate_boxing_pass_manager (gates and measurements, the TwirlingOptions default strategy
   and group) and build, then samples randomizations of the template. This script does the same on each
   compiled gap-88 and null arm, samples ``TWIRL_INSTANCES`` randomizations from QRNG seed ``TWIRL_SEED``
   and ``TWIRL_LIMIT_INSTANCES`` from ``TWIRL_LIMIT_SEED``, applies the coherent families to each instance's
   own sx and CZ pulses, undoes each instance's measurement flips and averages the laws.
5. **Interleave schedule.** IBM executes a job column-wise, every circuit of a batch once per shot, with no
   order across PUBs and no single-batch guarantee. The record gives each job's per-shot period from the
   compiled schedules and the 250 us default repetition delay, and the drift-monitor resolution of a
   repeated null arm.
6. **Decision rule.** The gap-88 run is untwirled: an exploratory run of this script found 32 independent
   randomizations of the signal and null arms leave their coherent errors unshared, raising the joint max_z
   far above the untwirled value (the ``twirl`` section keeps the evidence). The probe estimates map to a
   predicted untwirled gap-88 max_z through the mapping of item 1. The estimates' uncertainty enters as
   ``DECISION_POINTS`` unscrambled Sobol points mapped to standard normal quantiles, so the rule needs no
   seed; the gap-88 run proceeds only when the 95th percentile of max_z is below 1.

Falsifiers fixed before the retained run: a probe whose noise-free recovery error exceeds 5 percent of its
decision threshold, or whose noisy bias exceeds one standard error at the chosen shots, is rejected; a
twirled mode whose zero-error max_z exceeds 0.01 fails the instance check.

``--out FILE`` writes the record; ``--check FILE --run DIR`` requires FILE to be byte-identical to the collected
output of Kaggle run DIR, recomputes the record and requires every count, boolean and string to match and every
float to 1e-8.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import primorial_bound_residuals as br  # noqa: E402
import primorial_cover_noise as noise  # noqa: E402
import primorial_null_residuals as nr  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit.library import UnitaryGate  # noqa: E402

import calibration_snapshot  # noqa: E402
import coherence_probes as cp  # noqa: E402
import parallel  # noqa: E402
import primorial_tomography as tomo  # noqa: E402
import snapshot_laws  # noqa: E402

BOUND_RECORD = ROOT / "docs/evidence/primorial_cover/bound_residuals.json"
OUTPUT = "results/kaggle_out/primorial_probe_case.json"
# docs/evidence/anu_qrng/draw-2026-10-25T231051Z.json, indices 0 and 1.
TWIRL_SEED = 2441
TWIRL_LIMIT_SEED = 50280
TWIRL_INSTANCES = 32
TWIRL_LIMIT_INSTANCES = 512
# The Heron r2 default repetition delay (docs/notes/ibm_heron_platform.md, measured Targets).
REP_DELAY_SECONDS = 250e-6
DECISION_POINTS = 128
Z3 = 3.0
MAPPED_DETUNING = ("cz", "delay")
# Recovery vectors: every family at once, at two scales and two sign patterns; tilt in rad, CZ phase in rad,
# detuning and ZZ in kHz (primorial_bound_residuals units), amplitude as a fraction.
RECOVERY_VECTORS = tuple(
    {
        "tilt": tuple(s * scale * v for s, v in zip(signs, (0.004, 0.007, 0.010), strict=True)),
        "tilt_x": tuple(-s * scale * v for s, v in zip(signs, (0.003, 0.005, 0.002), strict=True)),
        "cz_phase": (signs[0] * scale * 0.03, -signs[1] * scale * 0.05),
        "detuning": tuple(s * scale * v for s, v in zip(signs, (12.0, 20.0, 7.0), strict=True)),
        "zz": (signs[1] * scale * 3.0, -signs[2] * scale * 5.0),
        "amplitude": tuple(s * scale * v for s, v in zip(signs, (0.004, 0.003, 0.002), strict=True)),
        "detuning_gates": MAPPED_DETUNING,
    }
    for scale in (0.5, 2.0)
    for signs in ((1, 1, 1), (1, -1, -1))
)
PARAMETERS = (
    *((f"tilt_sx_q{w}", "tilt", w, 1e-4) for w in range(3)),
    *((f"tilt_x_q{w}", "tilt_x", w, 1e-4) for w in range(3)),
    *((f"cz_phase_c{c}", "cz_phase", c, 1e-4) for c in range(2)),
    *((f"detuning_q{w}", "detuning", w, 0.1) for w in range(3)),
    *((f"zz_c{c}", "zz", c, 0.1) for c in range(2)),
    *((f"amplitude_q{w}", "amplitude", w, 1e-4) for w in range(3)),
)
# Estimate keys in Hz convert to the kHz of primorial_bound_residuals.
HZ_KEYS = ("detuning", "zz")


def kilohertz(key: str, value: float) -> float:
    return value / 1e3 if key.startswith(HZ_KEYS) else value


# ------------------------------------------------------------ probe circuits


def logical_ops(circuit: QuantumCircuit, durations: dict[str, float]) -> list[br.Op]:
    """Timed ops of a native probe circuit in program order, with the snapshot's sx, x and cz durations."""
    out: list[br.Op] = []
    for instruction in circuit.data:
        operation = instruction.operation
        wires = tuple(circuit.find_bit(q).index for q in instruction.qubits)
        if operation.name in ("measure", "barrier"):
            continue
        if operation.name == "delay":
            out.append(("delay", wires, 0.0, float(operation.duration) * cp.DT_SECONDS))
            continue
        angle = float(operation.params[0]) if operation.name == "rz" else 0.0
        out.append((operation.name, wires, angle, durations.get(operation.name, 0.0)))
    return out


def path_durations(view: Any, layout: list[int]) -> dict[str, float]:
    """The sx, x and cz durations of the path, which must be equal on every path qubit and coupler."""
    out: dict[str, float] = {}
    for name in ("sx", "x", "cz"):
        values = {
            float(props.duration)
            for qargs, props in view.target[name].items()
            if qargs is not None and props is not None and set(qargs) <= set(layout)
        }
        if len(values) != 1:
            raise SystemExit(f"{name} durations differ along {layout}: {sorted(values)}")
        out[name] = values.pop()
    return out


class ProbeLaws:
    """Picklable worker: one spec -> every probe circuit's noise-free law and the probe summary."""

    def __init__(self, ops: dict[str, list[br.Op]]) -> None:
        self.ops = ops

    def __call__(self, spec: dict[str, Any]) -> dict[str, float]:
        return cp.summarize({name: np.asarray(br.law(ops, spec)) for name, ops in self.ops.items()})


def truth_of(spec: dict[str, Any]) -> dict[str, float]:
    """The injected value of every estimate, in the estimators' units (rad, Hz)."""
    out: dict[str, float] = {}
    for key, family, index, _ in PARAMETERS:
        if family == "amplitude":
            continue
        value = float(spec.get(family, (0.0,) * 3)[index]) if family in spec else 0.0
        if family == "tilt_x" and "tilt_x" not in spec:
            value = float(spec.get("tilt", (0.0,) * 3)[index])
        out[key] = value * 1e3 if family in HZ_KEYS else value
    return out


def recovery(worker: ProbeLaws) -> dict[str, Any]:
    rows = parallel.ordered_map(worker, list(RECOVERY_VECTORS), min_items=1)
    errors: dict[str, float] = {}
    for spec, row in zip(RECOVERY_VECTORS, rows, strict=True):
        for key, value in truth_of(spec).items():
            errors[key] = max(errors.get(key, 0.0), abs(row[key] - value))
    return {"vectors": len(RECOVERY_VECTORS), "max_abs_error": errors}


def sensitivity(worker: ProbeLaws) -> dict[str, Any]:
    """d estimate / d parameter at zero by central differences, under the mapped detuning."""
    specs = []
    for _, family, index, step in PARAMETERS:
        size = 2 if family in ("cz_phase", "zz") else 3
        for sign in (1.0, -1.0):
            values = tuple(sign * step if k == index else 0.0 for k in range(size))
            specs.append({family: values, "detuning_gates": MAPPED_DETUNING})
    rows = parallel.ordered_map(worker, specs, min_items=1)
    keys = [key for key, family, _, _ in PARAMETERS if family != "amplitude"]
    matrix: dict[str, dict[str, float]] = {key: {} for key in keys}
    for k, (name, family, _, step) in enumerate(PARAMETERS):
        plus, minus = rows[2 * k], rows[2 * k + 1]
        unit = step * (1e3 if family in HZ_KEYS else 1.0)
        for key in keys:
            matrix[key][name] = (plus[key] - minus[key]) / (2 * unit)
    return {"estimates": keys, "parameters": [p[0] for p in PARAMETERS], "jacobian": matrix}


def detuned_pulse_check() -> dict[str, float]:
    """Largest gap between a detuned constant-amplitude pulse and the tilt beta = Delta / Omega, over 0 to 60 kHz."""
    from scipy.linalg import expm

    x = np.asarray([[0, 1], [1, 0]], dtype=complex)
    z = np.diag([1.0, -1.0]).astype(complex)
    worst = 0.0
    for name, angle in (("sx", math.pi / 2), ("x", math.pi)):
        for khz in (5.0, 30.0, 60.0):
            t = 32e-9
            omega, delta = angle / t, 2 * math.pi * khz * 1e3
            exact = expm(-1j * t * (omega * x + delta * z) / 2)
            worst = max(worst, br.infidelity(br.driven(name, delta / omega, 0.0), exact))
    return {"largest_infidelity_against_tilt": worst}


# ------------------------------------------------------------- noisy probes


class NoisyProbe:
    """Picklable worker: (probe name, compiled circuit, spec) -> the noisy law with inserted coherent errors."""

    def __init__(self, snapshot: dict[str, Any], layout: list[int], durations: dict[str, float]) -> None:
        self.snapshot = snapshot
        self.layout = layout
        self.durations = durations

    def inject(self, compiled: QuantumCircuit, spec: dict[str, Any]) -> QuantumCircuit:
        wire = {q: k for k, q in enumerate(self.layout)}
        tilts = {"sx": spec.get("tilt", (0.0,) * 3), "x": spec.get("tilt_x", spec.get("tilt", (0.0,) * 3))}
        amplitude = spec.get("amplitude", (0.0,) * 3)
        cz_phase = spec.get("cz_phase", (0.0, 0.0))
        detuning = spec.get("detuning", (0.0,) * 3)
        out = compiled.copy_empty_like()
        for instruction in compiled.data:
            out.append(instruction)
            name = instruction.operation.name
            physical = [compiled.find_bit(q).index for q in instruction.qubits]
            if name in ("sx", "x"):
                k = wire[physical[0]]
                actual = br.driven(name, tilts[name][k], amplitude[k])
                error = actual @ br.TARGET[name].conj().T
                out.append(UnitaryGate(error, label=f"{name}_error"), instruction.qubits)
            elif name == "cz":
                pair = tuple(sorted(wire[q] for q in physical))
                phi = cz_phase[nr.COUPLERS.index(pair)]
                if phi:
                    out.append(UnitaryGate(np.diag([1, 1, 1, np.exp(1j * phi)]), label="cz_phase"), instruction.qubits)
            if name in MAPPED_DETUNING:
                seconds = (
                    float(instruction.operation.duration) * cp.DT_SECONDS
                    if name == "delay"
                    else self.durations.get(name, 0.0)
                )
                for q in instruction.qubits:
                    k = wire[compiled.find_bit(q).index]
                    if detuning[k] and seconds:
                        out.rz(2 * math.pi * detuning[k] * 1e3 * seconds, q)
        return out

    def __call__(self, item: tuple[str, QuantumCircuit, dict[str, Any]]) -> list[float]:
        name, compiled, spec = item
        law = snapshot_laws.outcome_law(self.snapshot, self.inject(compiled, spec), "CPU")
        return [float(v) for v in law]


def thresholds(gates: list[dict[str, float]], cz: list[float]) -> dict[str, float]:
    """Decision thresholds: tilt 0.2 of each sx and x bound, CZ phase 0.7 of its bound, 5 kHz and 2 kHz."""
    out: dict[str, float] = {}
    for w, g in enumerate(gates):
        out[f"tilt_sx_q{w}"] = 0.2 * br.scale_to_budget((1, 0), {"sx": g["sx"]})[0]
        out[f"tilt_x_q{w}"] = 0.2 * br.scale_to_budget((1, 0), {"x": g["x"]})[0]
        out[f"detuning_q{w}"] = 5e3
    for c, r in enumerate(cz):
        out[f"cz_phase_c{c}"] = 0.7 * br.cz_bound(r)
        out[f"zz_c{c}"] = 2e3
    return out


def noisy_probes(
    snapshot: dict[str, Any], view: Any, layout: list[int], durations: dict[str, float], limits: dict[str, float]
) -> dict[str, Any]:
    probes = cp.circuits()
    compiled = parallel.ordered_map(noise.ArmCompile(snapshot), [(c, layout) for _, c in probes], min_items=1)
    named = [(name, circuit) for (name, _), circuit in zip(probes, compiled, strict=True)]
    truth_spec = {
        "tilt": tuple(limits[f"tilt_sx_q{w}"] for w in range(3)),
        "tilt_x": tuple(-limits[f"tilt_x_q{w}"] for w in range(3)),
        "cz_phase": (limits["cz_phase_c0"], -limits["cz_phase_c1"]),
        "detuning": (5.0, -5.0, 5.0),
    }
    worker = NoisyProbe(snapshot, layout, durations)
    out: dict[str, Any] = {}
    for label, spec in (("zero", {}), ("thresholds", truth_spec)):
        laws = parallel.ordered_map(worker, [(name, c, spec) for name, c in named], min_items=1)
        summary = cp.summarize({name: np.asarray(law) for (name, _), law in zip(named, laws, strict=True)})
        truth = truth_of(spec)
        out[label] = {
            "estimates": {k: v for k, v in summary.items() if not k.startswith("se_")},
            "bias": {k: summary[k] - truth[k] for k in truth},
            "se_one_shot": {k[3:]: v for k, v in summary.items() if k.startswith("se_")},
        }
    se = out["thresholds"]["se_one_shot"]
    shots = {k: math.ceil((Z3 * se[k] / limits[k]) ** 2) for k in limits}
    out["shots_to_resolve_threshold_at_3sd"] = shots
    out["shots_per_circuit"] = max(shots.values())
    out["circuits"] = len(named)
    out["circuit_seconds"] = {name: schedule_seconds(c, view) for name, c in named}
    return out


def schedule_seconds(compiled: QuantumCircuit, view: Any) -> float:
    """End time of the ALAP schedule, measurement included, from the Target's durations."""
    dt = float(view.target.dt)
    cursor: dict[int, float] = {}
    for instruction in compiled.data:
        name = instruction.operation.name
        if name == "barrier":
            continue
        physical = [compiled.find_bit(q).index for q in instruction.qubits]
        start = max((cursor.get(q, 0.0) for q in physical), default=0.0)
        if name == "delay":
            seconds = float(instruction.operation.duration) * (dt if instruction.operation.unit == "dt" else 1.0)
        else:
            props = view.target[name].get(tuple(physical))
            seconds = float(props.duration) if props is not None and props.duration else 0.0
        for q in physical:
            cursor[q] = start + seconds
    return max(cursor.values())


# ------------------------------------------------------------ twirled arms


def boxing_pass_manager() -> Any:
    """The boxing pass of executor_sampler.prepare for gates and measurements at the TwirlingOptions defaults."""
    from qiskit_ibm_runtime.options_models.twirling import TwirlingOptions
    from samplomatic.transpiler import generate_boxing_pass_manager

    options = TwirlingOptions()
    return generate_boxing_pass_manager(
        enable_gates=True,
        enable_measures=True,
        twirling_strategy=options.strategy.replace("-", "_"),
        inject_noise_site="after",
        add_tags="none",
        twirling_group=options.group,
    )


class TemplateBuild:
    """Picklable worker: one compiled arm -> its samplomatic (template, samplex)."""

    def __call__(self, compiled: QuantumCircuit) -> tuple[QuantumCircuit, Any]:
        from samplomatic import build

        return build(boxing_pass_manager().run(compiled))


class InstanceOps:
    """Picklable worker: (template, parameter row, flip row) -> the bound instance's timed ops and flip mask."""

    def __init__(self, layout: list[int], durations: dict[tuple[str, tuple[int, ...]], float], dt: float) -> None:
        self.layout = layout
        self.durations = durations
        self.dt = dt

    def __call__(self, item: tuple[QuantumCircuit, np.ndarray, np.ndarray]) -> tuple[list[br.Op], int]:
        template, values, flips = item
        bound = template.assign_parameters(values)
        ops = br.compact(nr.timed(bound, self.layout, self.durations, self.dt), self.layout, self.durations, self.dt)
        return ops, sum(int(b) << k for k, b in enumerate(flips))


def twirled_arms(
    snapshot: dict[str, Any],
    view: Any,
    layout: list[int],
    logical: list[tuple[dict[str, Any], QuantumCircuit]],
    count: int,
    seed: int,
) -> list[tuple[dict[str, Any], list[tuple[list[br.Op], int]]]]:
    """Each compiled arm's ``count`` sampled twirl instances: (timed ops, measurement flip mask).

    One generator seeded with ``seed`` draws every arm's randomizations in arm order before any binding, so a
    pooled and a serial run sample the same instances.
    """
    durations = {
        (name, tuple(qargs)): float(props.duration)
        for name in view.target.operation_names
        for qargs, props in view.target[name].items()
        if qargs is not None and props is not None and props.duration and set(qargs) <= set(layout)
    }
    dt = float(view.target.dt)
    compiled = parallel.ordered_map(noise.ArmCompile(snapshot), [(c, layout) for _, c in logical], min_items=1)
    built = parallel.ordered_map(TemplateBuild(), compiled, min_items=1)
    rng = np.random.default_rng(seed)
    items: list[tuple[QuantumCircuit, np.ndarray, np.ndarray]] = []
    for template, samplex in built:
        # Samplomatic samples on a thread pool by default; one worker keeps BLAS calls on one thread, and the
        # draws follow the generator's order either way.
        sample = samplex.sample(None, num_randomizations=count, rng=rng, max_workers=1)
        values = np.asarray(sample["parameter_values"])
        flips = np.asarray(sample["measurement_flips.c"]).reshape(count, -1)
        items.extend((template, values[r], flips[r]) for r in range(count))
    instances = parallel.ordered_map(InstanceOps(layout, durations, dt), items, min_items=1)
    return [(meta, instances[k * count : (k + 1) * count]) for k, (meta, _) in enumerate(logical)]


class TwirlArmLaw:
    """Picklable worker: (instances, spec) -> the instance-averaged law with each instance's flips undone."""

    def __call__(self, item: tuple[list[tuple[list[br.Op], int]], dict[str, Any]]) -> list[float]:
        instances, spec = item
        total = np.zeros(8)
        for ops, mask in instances:
            raw = br.law(ops, spec)
            total += np.asarray([raw[k ^ mask] for k in range(8)])
        return [float(v) for v in total / len(instances)]


class TwirlFit:
    """Picklable worker: one spec -> the null-subtracted gap-88 fit of the instance-averaged twirled laws."""

    def __init__(self, arms: list[tuple[dict[str, Any], list[tuple[list[br.Op], int]]]], fit: br.Fit) -> None:
        self.arms = arms
        self.fit = fit

    def __call__(self, spec: dict[str, Any]) -> dict[str, Any]:
        law = TwirlArmLaw()
        rows = [{**meta, "law": law((instances, spec))} for meta, instances in self.arms]
        return self.fit.fit_rows(rows)


def twirl_fit_by_arm(fit: br.Fit, arms: Any, spec: dict[str, Any]) -> dict[str, Any]:
    """One spec's twirled fit with the arms, not the specs, spread over the pool."""
    laws = parallel.ordered_map(TwirlArmLaw(), [(instances, spec) for _, instances in arms], min_items=1)
    return fit.fit_rows([{**meta, "law": law} for (meta, _), law in zip(arms, laws, strict=True)])


def twirl_scenarios(tilt: list[float], phi: list[float]) -> dict[str, list[dict[str, Any]]]:
    signs3 = list(itertools.product((1.0, -1.0), repeat=3))
    signs2 = list(itertools.product((1.0, -1.0), repeat=2))
    out: dict[str, list[dict[str, Any]]] = {
        "none": [{}],
        "tilt_sx": [{"tilt": tuple(s * t for s, t in zip(p, tilt, strict=True))} for p in signs3],
        "cz_phase": [{"cz_phase": tuple(s * f for s, f in zip(p, phi, strict=True))} for p in signs2],
        "joint_tilt_cz": [
            {
                "tilt": tuple(s * t for s, t in zip(p[:3], tilt, strict=True)),
                "cz_phase": tuple(s * f for s, f in zip(p[3:], phi, strict=True)),
            }
            for p in itertools.product((1.0, -1.0), repeat=5)
        ],
        "detuning_30_cz": [
            {
                "detuning": tuple(30.0 * a for a in d),
                "cz_phase": tuple(s * f for s, f in zip(p, phi, strict=True)),
                "detuning_gates": MAPPED_DETUNING,
            }
            for d in signs3
            for p in signs2
        ],
    }
    return out


def twirl_record(fit: br.Fit, arms32: Any, arms_limit: Any, tilt: list[float], phi: list[float]) -> dict[str, Any]:
    worker = TwirlFit(arms32, fit)
    scenarios = twirl_scenarios(tilt, phi)
    names = list(scenarios)
    flat = [spec for name in names for spec in scenarios[name]]
    rows = parallel.ordered_map(worker, flat, min_items=1)
    out: dict[str, Any] = {"instances": TWIRL_INSTANCES, "families": {}}
    start = 0
    worst_joint: dict[str, Any] = {}
    for name in names:
        count = len(scenarios[name])
        chunk = rows[start : start + count]
        k = br.first_max([r["max_z"] for r in chunk])
        out["families"][name] = {
            "scenarios": count,
            "max_z": chunk[k]["max_z"],
            "max_z_coefficient": chunk[k]["max_z_coefficient"],
            "null_subtracted_max_bias": chunk[k]["null_subtracted_max_bias"],
            "spec": br.round_spec(scenarios[name][k]),
        }
        if name == "joint_tilt_cz":
            worst_joint = scenarios[name][k]
        start += count
    fractions = [
        {"tilt": tuple(f * t for t in worst_joint["tilt"]), "cz_phase": tuple(g * c for c in worst_joint["cz_phase"])}
        for f in br.FRACTIONS
        for g in (0.4, 0.7, 1.0)
    ]
    scan = parallel.ordered_map(worker, fractions, min_items=1)
    out["fraction_scan"] = {
        "sign_pattern": "joint_tilt_cz worst",
        "columns": [0.4, 0.7, 1.0],
        "rows": list(br.FRACTIONS),
        "max_z": [[scan[3 * a + b]["max_z"] for b in range(3)] for a in range(len(br.FRACTIONS))],
    }
    limit = [twirl_fit_by_arm(fit, arms_limit, spec) for spec in ({}, worst_joint)]
    out["limit"] = {
        "instances": TWIRL_LIMIT_INSTANCES,
        "none_max_z": limit[0]["max_z"],
        "joint_tilt_cz_max_z": limit[1]["max_z"],
    }
    return out


# ------------------------------------------------------- interleave schedule


def ops_seconds(ops: list[br.Op], measure_seconds: float) -> float:
    """Schedule length of timed ops plus the final measurement."""
    if not ops:
        return measure_seconds
    starts = br.starts(ops)
    return max(s + op[3] for s, op in zip(starts, ops, strict=True)) + measure_seconds


def job_schedule(seconds: list[float], shots: int, randomizations: int = 1) -> dict[str, Any]:
    """Per-shot column period and QPU-time estimate of one job: 2 s per sub-job plus (rep_delay + circuit) per shot.

    Each randomization is its own bound circuit run shots / randomizations times, so one column holds every
    circuit of every randomization once.
    """
    period = randomizations * sum(s + REP_DELAY_SECONDS for s in seconds)
    per_randomization = shots // randomizations
    executions_seconds = period * per_randomization
    return {
        "circuits": len(seconds) * randomizations,
        "shots_per_circuit": per_randomization,
        "column_period_seconds": period,
        "qpu_seconds_one_subjob": 2.0 + executions_seconds,
    }


def twirled_shots(shots: int) -> int:
    """The smallest shot count at or above ``shots`` that live_run's twirled jobs accept."""
    floor = 32 * 64
    return max(floor, -(-shots // 32) * 32)


# ------------------------------------------------------------ decision rule

ESTIMATES = (
    *(f"tilt_sx_q{w}" for w in range(3)),
    *(f"tilt_x_q{w}" for w in range(3)),
    *(f"cz_phase_c{c}" for c in range(2)),
    *(f"detuning_q{w}" for w in range(3)),
    *(f"zz_c{c}" for c in range(2)),
)


def spec_of(values: dict[str, float]) -> dict[str, Any]:
    """Probe estimates (rad, Hz) as a primorial_bound_residuals spec under the detuning mapping."""
    return {
        "tilt": tuple(values[f"tilt_sx_q{w}"] for w in range(3)),
        "tilt_x": tuple(values[f"tilt_x_q{w}"] for w in range(3)),
        "cz_phase": tuple(values[f"cz_phase_c{c}"] for c in range(2)),
        "detuning": tuple(values[f"detuning_q{w}"] / 1e3 for w in range(3)),
        "zz": tuple(values[f"zz_c{c}"] / 1e3 for c in range(2)),
        "detuning_gates": MAPPED_DETUNING,
    }


def decision_points(dims: int = len(ESTIMATES)) -> list[list[float]]:
    """Standard normal quantiles of ``dims``-dimensional unscrambled Sobol points, the all-zero first point dropped."""
    from scipy.stats import qmc

    unit = qmc.Sobol(d=dims, scramble=False).random_base2(8)[1 : DECISION_POINTS + 1]
    normal = statistics.NormalDist()
    return [[normal.inv_cdf(min(max(u, 1e-9), 1 - 1e-9)) for u in row] for row in unit]


def decide(fit: br.Fit, estimate: dict[str, float], se: dict[str, float], points: list[list[float]]) -> dict[str, Any]:
    """Untwirled max_z quantiles over the estimates' uncertainty and the verdict."""
    specs = [spec_of({k: estimate[k] + z * se[k] for k, z in zip(ESTIMATES, row, strict=True)}) for row in points]
    rows = parallel.ordered_map(fit, [(s, s) for s in specs], min_items=1)
    values = sorted(r["max_z"] for r in rows)
    p95 = values[min(len(values) - 1, math.ceil(0.95 * len(values)) - 1)]
    point = spec_of(estimate)
    return {
        "point_estimate_max_z": fit((point, point))["max_z"],
        "median_max_z": values[len(values) // 2],
        "p95_max_z": p95,
        "largest_max_z": values[-1],
        "proceed": p95 < 1.0,
    }


def outcomes(limits: dict[str, float], gates: list[dict[str, float]], cz: list[float]) -> dict[str, dict[str, float]]:
    """Illustrative probe results: zero, the repository's measured scales, and the decision thresholds."""
    sx_tilt = 2 * math.pi * 30e3 * 32e-9 / (math.pi / 2)
    measured = {
        **{f"tilt_sx_q{w}": (1, -1, 1)[w] * sx_tilt for w in range(3)},
        **{f"tilt_x_q{w}": (1, -1, 1)[w] * sx_tilt / 2 for w in range(3)},
        "cz_phase_c0": 0.04,
        "cz_phase_c1": -0.04,
        **{f"detuning_q{w}": (1, -1, 1)[w] * 30e3 for w in range(3)},
        "zz_c0": 2e3,
        "zz_c1": 2e3,
    }
    threshold = {
        **{f"tilt_sx_q{w}": (1, -1, 1)[w] * limits[f"tilt_sx_q{w}"] for w in range(3)},
        **{f"tilt_x_q{w}": (1, -1, 1)[w] * limits[f"tilt_x_q{w}"] for w in range(3)},
        "cz_phase_c0": -br.cz_bound(cz[0]),
        "cz_phase_c1": br.cz_bound(cz[1]),
        **{f"detuning_q{w}": (1, -1, 1)[w] * 5e3 for w in range(3)},
        "zz_c0": 2e3,
        "zz_c1": 2e3,
    }
    del gates
    return {"zero": dict.fromkeys(ESTIMATES, 0.0), "measured_scale": measured, "threshold": threshold}


# ------------------------------------------------------- noise-model check


def noisy_fit(
    worker: NoisyProbe,
    compiled: list[tuple[dict[str, Any], QuantumCircuit]],
    snapshot: dict[str, Any],
    layout: list[int],
    fit: br.Fit,
    spec: dict[str, Any],
) -> float:
    """The largest gap-88 null-subtracted coefficient bias of the arms run under the snapshot's noise with ``spec``.

    Each quadrature is inverted through the snapshot's assignment channel of the read qubit before the fit.
    """
    laws = parallel.ordered_map(worker, [(str(k), c, spec) for k, (_, c) in enumerate(compiled)], min_items=1)
    rows = [{**meta, "law": law} for (meta, _), law in zip(compiled, laws, strict=True)]
    edges = tomo.edges()
    a = np.asarray([snapshot["qubits"][layout[j]]["e10"] for j, _ in edges])
    b = np.asarray([snapshot["qubits"][layout[j]]["e01"] for j, _ in edges])
    readings = {}
    for cost in ("gap88", "null"):
        x_read, y_read = tomo.gradient_readings(rows, cost)
        readings[cost] = (tomo.corrected(x_read, a, b), tomo.corrected(y_read, a, b))
    unit = np.ones(len(edges))
    sub = tomo.null_subtracted(fit.table, *readings["gap88"], readings["null"], unit, unit)
    return float(sub["max_coefficient_bias"])


def noise_model_check(
    snapshot: dict[str, Any],
    layout: list[int],
    durations: dict[str, float],
    logical: list[tuple[dict[str, Any], QuantumCircuit]],
    fit: br.Fit,
    bound_patch: dict[str, Any],
) -> dict[str, Any]:
    """The decisive coherent scenarios under the snapshot's noise model against the noise-free law.

    docs/notes/algebra_circuit_rules.md requires a coherent-error response derived through the device's noise
    model. The scenarios are the record's worst joint tilt and CZ-phase vertex and the repository's measured
    scales (30 kHz detuning, its in-pulse tilt, 0.04 rad CZ phase). Static ZZ is left out of both, because
    the noisy insertion models tilt, amplitude, CZ phase and detuning only. The noisy bias includes the
    incoherent model's own bias, which the zero-error row gives.
    """
    circuits = parallel.ordered_map(noise.ArmCompile(snapshot), [(c, layout) for _, c in logical], min_items=1)
    compiled = [(meta, circuit) for (meta, _), circuit in zip(logical, circuits, strict=True)]
    worst = bound_patch["families"]["joint_sx"]["worst_max_z"]["spec"]
    sx_tilt = 2 * math.pi * 30e3 * 32e-9 / (math.pi / 2)
    scenarios: dict[str, dict[str, Any]] = {
        "zero": {},
        "joint_bound": {"tilt": tuple(worst["tilt"]), "cz_phase": tuple(worst["cz_phase"])},
        "measured_scale": {
            "tilt": (sx_tilt, -sx_tilt, sx_tilt),
            "tilt_x": (sx_tilt / 2, -sx_tilt / 2, sx_tilt / 2),
            "cz_phase": (0.04, -0.04),
            "detuning": (30.0, -30.0, 30.0),
            "detuning_gates": MAPPED_DETUNING,
        },
    }
    worker = NoisyProbe(snapshot, layout, durations)
    out: dict[str, Any] = {}
    for name, spec in scenarios.items():
        noisy = noisy_fit(worker, compiled, snapshot, layout, fit, spec)
        clean = fit((spec, spec))["null_subtracted_max_bias"]
        out[name] = {"noisy_bias": noisy, "noise_free_bias": clean}
    return out


# ------------------------------------------------------------------ record


def evaluate(snapshot: dict[str, Any], noise_record: dict[str, Any], bound_record: dict[str, Any]) -> dict[str, Any]:
    view = calibration_snapshot.snapshot_backend(snapshot)
    logical = [(m, c) for m, c in noise.arms() if m["family"] == "gradient" and m["cost"] in ("gap88", "null")]
    measure = {float(props.duration) for qargs, props in view.target["measure"].items() if qargs is not None and props}
    points = decision_points()
    out: dict[str, Any] = {"detuned_pulse": detuned_pulse_check(), "patches": {}}
    for patch in nr.PATCHES:
        layout = noise_record["layouts"]["3"][patch]
        if bound_record["patches"][patch]["layout"] != layout:
            raise SystemExit(f"{patch}: bound_residuals layout differs from noise.json")
        durations = path_durations(view, layout)
        gates, cz = br.gate_errors(snapshot, layout)
        limits = thresholds(gates, cz)
        probe_ops = {name: logical_ops(circuit, durations) for name, circuit in cp.circuits()}
        worker = ProbeLaws(probe_ops)
        rec = recovery(worker)
        noisy = noisy_probes(snapshot, view, layout, durations, limits)
        shots = noisy["shots_per_circuit"]
        se = {k: noisy["thresholds"]["se_one_shot"][k] / math.sqrt(shots) for k in ESTIMATES}
        accepted = {
            k: rec["max_abs_error"][k] <= 0.05 * limits[k] and abs(noisy["thresholds"]["bias"][k]) <= se[k]
            for k in ESTIMATES
        }
        budget, variance = br.budget(noise_record, patch)
        arms = br.path_arms(snapshot, view, layout, logical)
        fit = br.Fit(arms, variance, budget)
        arms32 = twirled_arms(snapshot, view, layout, logical, TWIRL_INSTANCES, TWIRL_SEED)
        arms_limit = twirled_arms(snapshot, view, layout, logical, TWIRL_LIMIT_INSTANCES, TWIRL_LIMIT_SEED)
        bounds = bound_record["patches"][patch]["bounds"]
        tilt = [b["tilt"] for b in bounds["sx"]]
        twirl = twirl_record(fit, arms32, arms_limit, tilt, bounds["cz_phase"])
        measure_seconds = max(view.target["measure"][(q,)].duration for q in layout)
        arm_seconds = [ops_seconds(ops, measure_seconds) for _, ops in arms]
        readout_seconds = [measure_seconds + 32e-9] * 8
        gap88_seconds = arm_seconds * 2 + readout_seconds
        twirled_seconds = [ops_seconds(instances[0][0], measure_seconds) for _, instances in arms32] * 2
        twirled_seconds += readout_seconds
        probe_seconds = list(noisy["circuit_seconds"].values())
        schedule = {
            "rep_delay_seconds": REP_DELAY_SECONDS,
            "measure_seconds": measure_seconds,
            "probe_job": job_schedule(probe_seconds, shots),
            "gap88_untwirled_job": job_schedule(gap88_seconds, budget),
            "gap88_twirled_job": job_schedule(twirled_seconds, twirled_shots(budget), TWIRL_INSTANCES),
            "gap88_arms": "per edge setting gap88, null, null and gap88 again (+, -, -, +), and 8 basis preparations",
        }
        decisions = {label: decide(fit, values, se, points) for label, values in outcomes(limits, gates, cz).items()}
        check = noise_model_check(snapshot, layout, durations, logical, fit, bound_record["patches"][patch])
        out["patches"][patch] = {
            "noise_model_check": check,
            "layout": layout,
            "durations": durations,
            "thresholds": limits,
            "recovery": rec,
            "sensitivity": sensitivity(worker),
            "noisy_probes": noisy,
            "probe_se_at_shots": se,
            "probe_accepted": accepted,
            "twirl": twirl,
            "schedule": schedule,
            "decision": decisions,
        }
    del measure
    return out


def run() -> dict[str, Any]:
    snapshot = json.loads(noise.SNAPSHOT.read_text(encoding="utf-8"))
    noise_record = json.loads(nr.NOISE_RECORD.read_text(encoding="utf-8"))
    bound_record = json.loads(BOUND_RECORD.read_text(encoding="utf-8"))
    import samplomatic

    started = time.time()
    result = evaluate(snapshot, noise_record, bound_record)
    return {
        "schema": "gororoba-primorial-probe-case-v1",
        "snapshot": str(noise.SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(noise.SNAPSHOT.read_bytes()).hexdigest(),
        "noise_record_sha256": hashlib.sha256(nr.NOISE_RECORD.read_bytes()).hexdigest(),
        "bound_record_sha256": hashlib.sha256(BOUND_RECORD.read_bytes()).hexdigest(),
        "calibration": snapshot["calibration"],
        **calibration_snapshot.backend_identity(snapshot),
        "samplomatic": samplomatic.__version__,
        "twirl_seeds": {"instances": TWIRL_SEED, "limit": TWIRL_LIMIT_SEED},
        "environment": {k: v for k, v in noise.environment("CPU").items() if k != "device"},
        "seconds": round(time.time() - started, 1),
        **result,
    }


def path_budgets(snapshot: dict[str, Any], layouts: list[list[int]]) -> list[dict[str, Any]]:
    """The gap-88 null-subtracted budget of each path: primorial_cover_noise's noisy analysis on that layout.

    Returns, per path, the per-shot variance of every coefficient, the shots that identify all seven at the
    incoherent bias, and that bias. Every path's arms compile and simulate in one pooled map.
    """
    logical = [
        (m, c)
        for m, c in noise.arms()
        if (m["family"] == "gradient" and m["cost"] in ("gap88", "null")) or m["family"] == "readout3"
    ]
    jobs = [(c, layout) for layout in layouts for _, c in logical]
    compiled = parallel.ordered_map(noise.ArmCompile(snapshot), jobs, min_items=1)
    items = [(meta, circuit, isa) for (meta, circuit), isa in zip(logical * len(layouts), compiled, strict=True)]
    rows = parallel.ordered_map(noise.ArmLaw(snapshot, "CPU"), items, min_items=1)
    out = []
    for k in range(len(layouts)):
        fit = tomo.gradient_analysis(rows[k * len(logical) : (k + 1) * len(logical)], "gap88")["null_subtracted"]
        out.append(
            {
                "per_shot_coefficient_variance": {
                    key: float(v) for key, v in fit["per_shot_coefficient_variance"].items()
                },
                "shots_identify_all": fit["shots_identify_all"],
                "incoherent_max_bias": float(fit["max_coefficient_bias"]),
            }
        )
    return out


def path_budget(snapshot: dict[str, Any], layout: list[int]) -> dict[str, Any]:
    """path_budgets for one path."""
    return path_budgets(snapshot, [layout])[0]


# The decision's sampled inputs: the independent components (each its own circuits' quadrature noise) and the
# assignment flips of the in-job readout calibration, which the components share.
JOINT_INPUTS = (*cp.COMPONENTS, *(f"{flip}_q{wire}" for wire, flip in cp.FLIPS))


def joint_sample(probe: dict[str, float], shots: int, normals: list[float]) -> dict[str, float]:
    """The estimates at one joint draw: each component moved by its quadrature normal and every flip's normal.

    ``probe`` is coherence_probes.summarize's output; one-shot errors scale by 1 / sqrt(shots).
    """
    draw = dict(zip(JOINT_INPUTS, normals, strict=True))
    root = math.sqrt(shots)
    components = {}
    for c in cp.COMPONENTS:
        moved = float(probe[c]) + draw[c] * float(probe[f"qse_{c}"]) / root
        for wire, flip in cp.FLIPS:
            sigma = math.sqrt(float(probe[f"var_{flip}_q{wire}"])) / root
            moved += float(probe[f"d_{c}__{flip}_q{wire}"]) * draw[f"{flip}_q{wire}"] * sigma
        components[c] = moved
    return {**{k: components[k] for k in cp.COMPONENTS if k in ESTIMATES}, **cp.derived(components)}


class PathFits:
    """Picklable worker: (path index, spec) -> that path's br.Fit of the spec as a shared error."""

    def __init__(self, fits: list[br.Fit]) -> None:
        self.fits = fits

    def __call__(self, item: tuple[int, dict[str, Any]]) -> dict[str, Any]:
        index, spec = item
        return self.fits[index]((spec, spec))


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, math.ceil(q * len(ordered)) - 1))]


def decide_many(
    snapshot: dict[str, Any],
    paths: list[tuple[list[int], dict[str, float]]],
    probe_shots: int,
    gap88_shots: int,
    family_size: int = 1,
) -> list[dict[str, Any]]:
    """The preregistered stage-2 decision for each (path, probe summary) at ``probe_shots`` shots per circuit.

    Each probe summary holds every estimate of ESTIMATES and its one-shot standard error ``se_<estimate>``, as
    coherence_probes.summarize reports them; the estimates' uncertainty is sampled jointly over the independent
    components and the shared readout flips (``joint_sample``), so the ZZ, detuning and CZ-phase estimates keep
    the correlations their shared slopes give them. Each gap-88 reading averages two executions of ``gap88_shots``
    shots (primorial_campaigns' gap-88, null, null, gap-88 order), so the path's coefficient standard
    deviations are taken at twice that count. Stage 2 proceeds on a path when, over its estimates' uncertainty,
    the 95th percentile of max_z is below 1 and the 95th percentile of the shots that identify all seven
    coefficients (primorial_tomography.phase_fit's rule) is at most the per-reading count.

    The falsifier band of a path's stage-2 largest bias spans the predicted largest bias from its
    alpha / 2 quantile to its 1 - alpha / 2 quantile, widened by z(1 - alpha / 2) of the largest coefficient
    standard deviations (at least three) and by the path's incoherent bias, with alpha = 0.05 / family_size: a
    Bonferroni band over the family_size paths that reach stage 2 together.
    """
    view = calibration_snapshot.snapshot_backend(snapshot)
    logical = [(m, c) for m, c in noise.arms() if m["family"] == "gradient" and m["cost"] in ("gap88", "null")]
    budgets = path_budgets(snapshot, [layout for layout, _ in paths])
    per_reading = 2 * gap88_shots
    fits = [
        br.Fit(br.path_arms(snapshot, view, layout, logical), budget["per_shot_coefficient_variance"], per_reading)
        for (layout, _), budget in zip(paths, budgets, strict=True)
    ]
    points = decision_points(len(JOINT_INPUTS))
    specs = [[spec_of(joint_sample(probe, probe_shots, row)) for row in points] for _, probe in paths]
    jobs = [(k, spec) for k, path_specs in enumerate(specs) for spec in path_specs]
    flat = parallel.ordered_map(PathFits(fits), jobs, min_items=1)
    alpha = 0.05 / family_size
    z = max(3.0, statistics.NormalDist().inv_cdf(1 - alpha / 2))
    out = []
    for k, ((layout, probe), budget, fit) in enumerate(zip(paths, budgets, fits, strict=True)):
        rows = flat[k * len(points) : (k + 1) * len(points)]
        max_z = [r["max_z"] for r in rows]
        shots = [math.inf if r["shots_identify_all"] is None else float(r["shots_identify_all"]) for r in rows]
        bias = [r["null_subtracted_max_bias"] for r in rows]
        widen = z * max(fit.sd.values()) + budget["incoherent_max_bias"]
        p95_shots = _quantile(shots, 0.95)
        out.append(
            {
                "calibration": snapshot["calibration"],
                **calibration_snapshot.backend_identity(snapshot),
                "layout": layout,
                "budget": budget,
                "gap88_shots_per_circuit": gap88_shots,
                "shots_per_reading": per_reading,
                "coefficient_sd": fit.sd,
                "probe_shots": probe_shots,
                "estimate": {key: float(probe[key]) for key in ESTIMATES},
                "se": {key: float(probe[f"se_{key}"]) / math.sqrt(probe_shots) for key in ESTIMATES},
                "decision": {
                    "median_max_z": _quantile(max_z, 0.5),
                    "p95_max_z": _quantile(max_z, 0.95),
                    "p95_shots_identify_all": None if math.isinf(p95_shots) else int(p95_shots),
                    "proceed": _quantile(max_z, 0.95) < 1.0 and p95_shots <= per_reading,
                },
                "falsifier_family_size": family_size,
                "falsifier_band": [
                    max(0.0, _quantile(bias, alpha / 2) - widen),
                    _quantile(bias, 1 - alpha / 2) + widen,
                ],
            }
        )
    return out


def decide_path(
    snapshot: dict[str, Any], layout: list[int], probe: dict[str, float], probe_shots: int, gap88_shots: int
) -> dict[str, Any]:
    """decide_many for one path, whose falsifier band covers that path alone."""
    return decide_many(snapshot, [(layout, probe)], probe_shots, gap88_shots)[0]


# The readout floor below which a wire's in-job calibration voids every estimate that reads or postselects on it.
READOUT_FLOOR = cp.READOUT_FLOOR
# Shots per gap-88 circuit: the cap the approval binds and the floor the decision may lower it to.
GAP88_CAP, GAP88_FLOOR = 3200, 1600


def _group_record(run_dir: Path, group: str) -> tuple[dict[str, Any], dict[str, Any], list[list[int]]]:
    """The run record, the collected entry of ``group`` and the pinned paths in replica order."""
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collected = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    entry = next((item for item in collected if isinstance(item, dict) and item.get("group") == group), None)
    if entry is None:
        raise SystemExit(f"{run_dir}: no collected {group} group")
    pin = record["policy"]["design"]["pin_layout"]
    return record, entry, [list(path) for path in pin.get("replicas", [pin["qubits"]])]


def readout_by_path(entry: dict[str, Any], paths: list[list[int]]) -> list[dict[str, Any]]:
    """Each path's in-job e10, e01 and 1 - e10 - e01 per wire from its own cp_readout distributions."""
    measured = entry["measured"]
    out = []
    for k, path in enumerate(paths):
        flips = cp.assignment(
            {name: np.asarray(measured[name][k], dtype=float) for name in ("cp_readout_0", "cp_readout_1")}
        )
        fidelity = [1.0 - e10 - e01 for e10, e01 in flips]
        out.append(
            {
                "path": path,
                "e10": [e10 for e10, _ in flips],
                "e01": [e01 for _, e01 in flips],
                "fidelity": fidelity,
                "passed": all(f >= READOUT_FLOOR for f in fidelity),
            }
        )
    return out


def with_excitation(snapshot: dict[str, Any], excess: dict[int, float]) -> dict[str, Any]:
    """The snapshot with each named qubit's e10 raised by its excess preparation excitation."""
    moved = json.loads(json.dumps(snapshot))
    for qubit, value in excess.items():
        moved["qubits"][qubit]["e10"] = moved["qubits"][qubit]["e10"] + value
    return moved


def decide_delay(snapshot: dict[str, Any], slow_dir: Path, fast_dir: Path) -> dict[str, Any]:
    """The preregistered repetition-delay rule from the readout preflight at the longer and the shorter delay.

    A path is retained when every wire reaches READOUT_FLOOR at the longer delay. The shorter delay is taken when
    every retained path also reaches the floor there and its zero-estimate decision at GAP88_CAP still proceeds
    with each wire's e10 raised by the upper bound (estimate plus two standard errors, floored at zero) of its
    excess excitation, the shorter-delay e10 less the longer-delay e10; otherwise the longer delay is kept. The
    zero estimate isolates the excitation's effect on the incoherent budget.
    """
    _, slow, paths = _group_record(slow_dir, "readout_preflight")
    _, fast, fast_paths = _group_record(fast_dir, "readout_preflight")
    if fast_paths != paths:
        raise SystemExit(f"preflight paths differ: {paths} against {fast_paths}")
    shots = [int(json.loads((d / "record.json").read_text(encoding="utf-8"))["shots"]) for d in (slow_dir, fast_dir)]
    readout = [readout_by_path(entry, paths) for entry in (slow, fast)]
    retained = [k for k, row in enumerate(readout[0]) if row["passed"]]
    excess: dict[int, float] = {}
    for k in retained:
        for wire, qubit in enumerate(paths[k]):
            e_slow, e_fast = readout[0][k]["e10"][wire], readout[1][k]["e10"][wire]
            se = math.sqrt(e_slow * (1 - e_slow) / shots[0] + e_fast * (1 - e_fast) / shots[1])
            excess[qubit] = max(0.0, e_fast - e_slow + 2 * se)
    zero = {key: 0.0 for key in (*cp.COMPONENTS, *ESTIMATES)} | {f"se_{key}": 0.0 for key in ESTIMATES}
    zero |= {f"qse_{c}": 0.0 for c in cp.COMPONENTS}
    zero |= {f"d_{c}__{flip}_q{w}": 0.0 for c in cp.COMPONENTS for w, flip in cp.FLIPS}
    zero |= {f"var_{flip}_q{w}": 0.0 for w, flip in cp.FLIPS}
    fast_pass = all(readout[1][k]["passed"] for k in retained)
    verdicts = (
        decide_many(with_excitation(snapshot, excess), [(paths[k], zero) for k in retained], 1, GAP88_CAP)
        if retained and fast_pass
        else []
    )
    shorter = bool(retained) and fast_pass and all(v["decision"]["proceed"] for v in verdicts)
    return {
        "calibration": snapshot["calibration"],
        "paths": paths,
        "readout": {"longer": readout[0], "shorter": readout[1]},
        "retained": [paths[k] for k in retained],
        "excess_e10_upper": {str(q): v for q, v in sorted(excess.items())},
        "shorter_delay_decisions": [v["decision"] | {"layout": v["layout"]} for v in verdicts],
        "use_shorter_delay": shorter,
    }


def decide_paths(snapshot: dict[str, Any], run_dir: Path, excess: dict[int, float] | None = None) -> dict[str, Any]:
    """The preregistered multi-path stage-2 rule from a collected coherence-probe run.

    Each path is voided when a wire's in-job readout calibration falls below READOUT_FLOOR. Every other path is
    decided at GAP88_CAP from its own per-replica summary (live_run's summary_per_replica, the raw distributions
    with that path's own in-job readout inversion); the paths that proceed set the stage-2 shots, the smallest
    multiple of 100 between GAP88_FLOOR and GAP88_CAP that covers their largest 95th-percentile identification
    need, and are decided again at that count with a Bonferroni falsifier band over the paths that proceed.
    ``excess`` raises each qubit's e10 (the shorter-delay rule's excitation) before every decision.
    """
    record, entry, paths = _group_record(run_dir, "coherence_probes")
    probe_shots = int(record["shots"])
    moved = with_excitation(snapshot, excess or {})
    readout = readout_by_path(entry, paths)
    summaries = entry["measured_statistics"]["summary_per_replica"]
    valid = [k for k, row in enumerate(readout) if row["passed"]]
    first = decide_many(moved, [(paths[k], summaries[k]) for k in valid], probe_shots, GAP88_CAP) if valid else []
    proceeding = [k for k, v in zip(valid, first, strict=True) if v["decision"]["proceed"]]
    need = max(
        (v["decision"]["p95_shots_identify_all"] for k, v in zip(valid, first, strict=True) if k in proceeding),
        default=None,
    )
    shots = None if need is None else min(GAP88_CAP, max(GAP88_FLOOR, 100 * math.ceil(need / 200)))
    final = (
        decide_many(moved, [(paths[k], summaries[k]) for k in proceeding], probe_shots, shots, len(proceeding))
        if shots is not None
        else []
    )
    # A smaller shot count raises every coefficient's standard deviation, so max_z only falls, and the count covers
    # each proceeding path's identification need: every path that proceeds at the cap proceeds again.
    stage2 = [paths[k] for k, v in zip(proceeding, final, strict=True) if v["decision"]["proceed"]]
    if len(stage2) != len(proceeding):
        raise SystemExit(f"paths proceeding at the cap failed at {shots} shots: {proceeding} against {stage2}")
    return {
        "calibration": snapshot["calibration"],
        "probe_shots": probe_shots,
        "paths": paths,
        "readout": readout,
        "voided": [paths[k] for k in range(len(paths)) if k not in valid],
        "at_cap": first,
        "gap88_shots": shots,
        "decisions": final,
        "stage2_paths": stage2,
        "proceed": bool(stage2),
    }


# live_run.ISOLATED_SUFFIX: the name suffix of a group's isolated reference entry.
ISOLATED_SUFFIX = "_isolated"
# The packed-against-isolated homogeneity test rejects at this level.
CROSSTALK_ALPHA = 0.01


def crosstalk(run_dir: Path, group: str) -> dict[str, Any]:
    """The packed-against-isolated check of a multi-path run's first member on the first path.

    live_run's isolated reference runs the group's first member on the first path alone in its own PUB. A
    chi-square homogeneity test of its outcome counts against the same member's first-path counts in the packed
    PUB, where every path runs at once, detects crosstalk from the other paths at CROSSTALK_ALPHA.
    """
    record, entry, paths = _group_record(run_dir, group)
    shots = int(record["shots"])
    measured = entry["measured"]
    reference = next((name for name in measured if name.endswith(ISOLATED_SUFFIX)), None)
    if reference is None:
        return {"group": group, "paths": len(paths), "reference": None, "crosstalk_detected": False}
    member = reference[: -len(ISOLATED_SUFFIX)]
    counts = np.rint(shots * np.asarray([measured[member][0], measured[reference][0]], dtype=float))
    counts = counts[:, counts.sum(axis=0) > 0]
    statistic, p_value, dof, _ = stats.chi2_contingency(counts, correction=False)
    return {
        "group": group,
        "paths": len(paths),
        "reference": reference,
        "member": member,
        "chi_square": float(statistic),
        "degrees_of_freedom": int(dof),
        "p_value": float(p_value),
        "crosstalk_detected": bool(p_value < CROSSTALK_ALPHA),
    }


def check(path: Path, run_dir: Path) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    ledger = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    recorded = ledger["files"].get(f"output/repo/{OUTPUT}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    failures = [] if digest == recorded else [f"{path} sha256 {digest} against the collected {recorded}"]
    br.compare(json.loads(json.dumps(run())), retained, "", failures)
    for failure in failures[:50]:
        print(failure)
    print(f"primorial probe case replay: {len(failures)} departures")
    return 1 if failures else 0


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--run", type=Path, help="Kaggle run directory whose collected output --check binds")
    parser.add_argument("--decide", action="store_true", help="apply the decision rule to a collected probe summary")
    parser.add_argument("--snapshot", type=Path, help="--decide: the calibration snapshot of the run")
    parser.add_argument("--layout", type=lambda text: [int(q) for q in text.split(",")], help="--decide: the path")
    parser.add_argument("--probe-summary", type=Path, help="--decide: JSON of the probe estimates and se_ keys")
    parser.add_argument("--probe-shots", type=int, help="--decide: shots per probe circuit")
    parser.add_argument("--gap88-shots", type=int, help="--decide: shots per gap-88 circuit")
    parser.add_argument(
        "--decide-delay", type=Path, metavar="RUN", help="apply the delay rule; RUN is the shorter-delay preflight"
    )
    parser.add_argument("--preflight-slow", type=Path, help="--decide-delay: the longer-delay preflight run")
    parser.add_argument(
        "--decide-paths", type=Path, metavar="RUN", help="apply the multi-path stage-2 rule to a collected probe run"
    )
    parser.add_argument("--delay-verdict", type=Path, help="--decide-paths: the --decide-delay output")
    parser.add_argument("--crosstalk", type=Path, metavar="RUN", help="packed-against-isolated check of a run")
    parser.add_argument("--group", help="--crosstalk: the campaign")
    args = parser.parse_args()
    if args.decide_delay:
        if args.snapshot is None or args.preflight_slow is None or args.out is None:
            parser.error("--decide-delay needs --snapshot, --preflight-slow, --out and the run directory")
        verdict = decide_delay(
            json.loads(args.snapshot.read_text(encoding="utf-8")), args.preflight_slow, args.decide_delay
        )
        _write(args.out, verdict)
        print(f"delay rule: retained {len(verdict['retained'])} paths, shorter delay {verdict['use_shorter_delay']}")
        return 0
    if args.decide_paths:
        if args.snapshot is None or args.out is None:
            parser.error("--decide-paths needs --snapshot and --out")
        excess = None
        if args.delay_verdict is not None:
            rule = json.loads(args.delay_verdict.read_text(encoding="utf-8"))
            if rule["use_shorter_delay"]:
                excess = {int(q): float(v) for q, v in rule["excess_e10_upper"].items()}
        verdict = decide_paths(json.loads(args.snapshot.read_text(encoding="utf-8")), args.decide_paths, excess)
        _write(args.out, verdict)
        print(
            f"stage 2: {len(verdict['stage2_paths'])} of {len(verdict['paths'])} paths at "
            f"{verdict['gap88_shots']} shots, {len(verdict['voided'])} voided"
        )
        return 0
    if args.crosstalk:
        if args.group is None or args.out is None:
            parser.error("--crosstalk needs --group and --out")
        verdict = crosstalk(args.crosstalk, args.group)
        _write(args.out, verdict)
        print(f"crosstalk {args.group}: detected {verdict['crosstalk_detected']}")
        return 0
    if args.decide:
        needed = (args.snapshot, args.layout, args.probe_summary, args.probe_shots, args.gap88_shots, args.out)
        if any(value is None for value in needed):
            parser.error("--decide needs --snapshot, --layout, --probe-summary, --probe-shots, --gap88-shots, --out")
        verdict = decide_path(
            json.loads(args.snapshot.read_text(encoding="utf-8")),
            args.layout,
            json.loads(args.probe_summary.read_text(encoding="utf-8")),
            args.probe_shots,
            args.gap88_shots,
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(verdict, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        decision = verdict["decision"]
        print(f"decision for {args.layout}: proceed={decision['proceed']} p95={decision['p95_max_z']}")
        return 0
    if args.check:
        if args.run is None:
            parser.error("--check needs --run")
        return check(args.check, args.run)
    if args.out is None:
        parser.error("--out is required without --check")
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out} in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
