"""The echo-matched dilation pair under retained calibrations: which error class each channel lands in.

Design B's block encoding U of B = L_a / 2, a = e1 + e10
(singular_sector_dynamics.lcu_circuit), acts on the dark input
(e4 - e15)/sqrt2, which cd_core puts in the kernel of L_a. The two arms

- amplified: U Z U^dagger Z U, with Z on the ancilla;
- echo: U U^dagger U, the same circuit without the two Z;

read P(anc = 0), ideally 0 in both. A PREP angle beta = pi/4 + eps is an
error the compiled inverse undoes: ideally amplified - echo =
sin^2(6 eps) - sin^2(2 eps) > 0. A conditional phase after every CZ enters U
and U^dagger alike and survives the inverse. This script measures, under each
retained calibration's noise, which class each physical channel falls in:

1. Compile. Separate compiles of the two arms route differently, so a pair
   compiles once as U R U^dagger R U with R = RZ(reflection) on the
   ancilla, at optimization level 3 (seed SEED), and binds reflection = pi
   (amplified, Z up to a global phase) or 0 (echo); both arms then carry the
   identical sequence of non-virtual (gate, physical qubits). The device
   compile binds beta = pi/4 and picks the layout; it is the circuit a device
   case would run and is retained as QPY. The eps family compiles once with
   beta = pi/4 + eps symbolic on the same layout and binds each eps, since a
   bound pi/4 synthesizes differently from a generic angle. Noiseless
   P(anc = 0) must equal sin^2(6 eps) and sin^2(2 eps) to 1e-9.
2. Model. Each compiled arm moves onto its active qubits with its barriers,
   is scheduled ALAP on the restricted Target, and runs live_run's gate, idle
   and assignment noise (walk_scaffold_channels.LaneModel). On the device
   compile a channel is inserted after the gates it modifies, uniformly on
   every qubit or edge: sx_overrotation, cz_local_phase,
   cz_conditional_phase, and extra_depolarizing as the incoherent control.
   With every parameter at zero the law equals the baseline.
3. Mixtures. Family members at eps in MIX_EPS also run with a conditional
   phase delta, which locates where the two classes cancel in
   amplified - echo.
4. CZ-phase reference. On every edge the device compile uses: control in
   |+>, target in |0> or |1>, 2m barrier-separated CZ, control read in the Y
   basis, so P(0) = (1 + sin phi)/2. The target-1 minus target-0 readout
   carries 2m delta and cancels each qubit's local phase. It runs under
   every channel, which measures its cross-sensitivity.
5. Sizing. Shots per arm that resolve each channel's shift of
   amplified - echo at z = Z_SCORE. The conditional phase moves the pair
   about evenly in delta, so the reference must bound |delta| below the
   magnitude whose shift equals the pair's standard error at each budget,
   for the more responsive sign (power-law interpolation between two
   sampled points of each sign's delta grid that bracket it; a level below
   the smallest sampled response stops the run); its shots per edge and
   target state reach that bound at z = Z_SCORE through the reference's own
   slope in delta.

Preregistered reading, per backend:
- The device baseline difference is a matched null when it lies within one
  standard error of the largest budget (BUDGETS, shots per arm).
- A class's verdict is the sign of its shift of amplified - echo, against
  its own compile's baseline, at both signs of its magnitude: "undone" when
  every shift of size NULL_SHIFT or more is positive (the eps class),
  "surviving" when every such shift is negative, "odd" when they differ, and
  "null" when every shift is below NULL_SHIFT.
- The pair separates rotation errors from CZ phases on a calibration only
  when cz_conditional_phase is "surviving" and some physical rotation
  channel (sx_overrotation or cz_local_phase) is "undone"; otherwise the
  eps class has no physical member there.

Algebra: the dark witness and its bright partner are certified with cd_core
on the 32 basis products SELECT encodes (L_e1 and L_e10 on every e_k), and
the same products are recomputed with the pinned python-hypercomplex (exact
Fraction coefficients) and python-hypercomplex-engine under their declared
identity map; the run fails on any difference.

Laws run through parallel.ordered_map. The entry reads GOROROBA_AER_DEVICE
(CPU by default). ``--check FILE --run DIR`` binds FILE and the retained arms
to the Kaggle run's collect.json digests, recomputes the cd_core side of the
algebra record, recompiles Kingston and requires its compile summary and
device arms to match, recomputes a reduced set of Kingston laws on
GOROROBA_AER_DEVICE to 1e-8, and recomputes every verdict and shot count from
the retained laws.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit, qpy, transpile  # noqa: E402
from qiskit.circuit import Parameter  # noqa: E402
from singular_sector_dynamics import lcu_circuit  # noqa: E402
from walk_scaffold_channels import LaneModel, edges, local_circuit  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402
from cd_core import cd_sign  # noqa: E402
from select_lcu import sparse_pair_prep  # noqa: E402

OUTPUT = "results/kaggle_out/echo_dilation_noise.json"
OUTPUT_QPY = "results/kaggle_out/echo_dilation_arms.qpy"
HISTORY = "docs/evidence/calibration/history"
SNAPSHOTS = {
    "ibm_fez": f"{HISTORY}/ibm_fez/20261015T2031280700.json",
    "ibm_kingston": f"{HISTORY}/ibm_kingston/20261015T2035330700.json",
    "ibm_marrakesh": f"{HISTORY}/ibm_marrakesh/20261015T2046350700.json",
}
DIM = 16
ELEMENT = (1, 10)
DARK = (4, 15)
SEED = 7
ARMS = ("amplified", "echo")
EPS = (-0.1, -0.06, -0.03, -0.01, 0.01, 0.03, 0.06, 0.1)
CHANNELS: dict[str, tuple[float, ...]] = {
    "sx_overrotation": (-0.04, -0.02, -0.01, 0.01, 0.02, 0.04),
    "cz_local_phase": (-0.05, -0.02, -0.01, 0.01, 0.02, 0.05),
    # The magnitudes below 0.01 bracket the uniform-phase tolerance, which
    # sign_tolerance reads by interpolation between sampled points only.
    "cz_conditional_phase": (
        -0.1,
        -0.05,
        -0.02,
        -0.01,
        -0.007,
        -0.005,
        -0.003,
        0.003,
        0.005,
        0.007,
        0.01,
        0.02,
        0.05,
        0.1,
    ),
    "extra_depolarizing": (0.002, 0.005, 0.01),
}
ROTATIONS = ("sx_overrotation", "cz_local_phase")
# Each edge alone carries a conditional phase of these magnitudes, which
# tests whether the edges' shifts of amplified - echo add up to the uniform one.
EDGE_DELTA = (-0.02, -0.01, -0.005, 0.005, 0.01, 0.02)
EDGE_CHANNEL = "cz_conditional_phase"
MIX_EPS = (0.03, 0.06)
MIX_DELTA = (-0.02, -0.01, 0.01, 0.02)
REFERENCE_M = (8, 24)
Z_SCORE = 3.0
BUDGETS = (4096, 16384, 40000)
NULL_SHIFT = 1e-3
# The reference's slope in delta is the central difference over +-SLOPE_DELTA,
# a point of the conditional-phase grid.
SLOPE_DELTA = 0.01
# The replay recomputes the laws at these magnitudes, eps values and edges.
REPLAY_MAGNITUDES = (0.002, 0.02)
REPLAY_EPS = (-0.03, 0.03)
REFLECTION = Parameter("reflection")
EPS_PARAMETER = Parameter("eps")


def algebra_record() -> dict[str, Any]:
    """The products SELECT encodes, the dark witness and its bright partner, in cd_core and the packages."""
    products = [(m, k) for m in ELEMENT for k in range(DIM)]
    signs = [cd_sign(DIM, a, b) for a, b in products]

    def image(minus: bool) -> dict[int, int]:
        out: dict[int, int] = {}
        for m in ELEMENT:
            for k, c in ((DARK[0], 1), (DARK[1], -1 if minus else 1)):
                out[m ^ k] = out.get(m ^ k, 0) + c * cd_sign(DIM, m, k)
        return {label: value for label, value in sorted(out.items()) if value}

    dark, bright = image(True), image(False)
    if dark or sorted(abs(v) for v in bright.values()) != [2, 2]:
        raise SystemExit(f"cd_core: (e1 + e10)(e4 -+ e15) gives {dark} and {bright}")
    record: dict[str, Any] = {
        "dim": DIM,
        "products": [list(p) for p in products],
        "cd_core_signs": signs,
        "dark_image": {str(k): v for k, v in dark.items()},
        "bright_image": {str(k): v for k, v in bright.items()},
    }
    try:
        import hypercomplex
        import hypercomplex_engine
    except ImportError as error:
        record["packages"] = {"unavailable": str(error)}
        return record
    algebra = hypercomplex.cayley_dickson_algebra(DIM.bit_length() - 1, Fraction)

    def hypercomplex_sign(a: int, b: int) -> int:
        coefficients = (algebra.e(a) * algebra.e(b)).coefficients()
        nonzero = [(k, c) for k, c in enumerate(coefficients) if c != 0]
        if len(nonzero) != 1 or nonzero[0][0] != a ^ b or abs(nonzero[0][1]) != 1:
            raise SystemExit(f"hypercomplex e{a} e{b} is not the signed unit e{a ^ b}: {nonzero}")
        return int(nonzero[0][1])

    def engine_sign(a: int, b: int) -> int:
        sign, index = hypercomplex_engine.multiply("standard", (1, a), (1, b))
        if int(index) != a ^ b:
            raise SystemExit(f"hypercomplex-engine e{a} e{b} lands on e{index}, not e{a ^ b}")
        return int(sign)

    record["packages"] = {
        "hypercomplex": {
            "version": importlib.metadata.version("hypercomplex"),
            "coefficients": "fractions.Fraction",
            "signs": [hypercomplex_sign(a, b) for a, b in products],
        },
        "hypercomplex-engine": {
            "version": importlib.metadata.version("hypercomplex-engine"),
            "signs": [engine_sign(a, b) for a, b in products],
        },
    }
    for name, entry in record["packages"].items():
        if entry["signs"] != signs:
            raise SystemExit(f"{name} differs from cd_core on SELECT's dim-{DIM} products")
    return record


def pair_template(eps: Any) -> QuantumCircuit:
    """U R U^dagger R U on the dark input, R = RZ(reflection) on the ancilla, ancilla measured."""
    u = lcu_circuit(ELEMENT[0], ELEMENT[1], 1, math.pi / 4 + eps)
    circuit = QuantumCircuit(5, 1)
    circuit.compose(sparse_pair_prep(4, DARK[0], DARK[1], math.pi), range(4), inplace=True)
    circuit.compose(u, inplace=True)
    circuit.barrier()
    circuit.rz(REFLECTION, 4)
    circuit.compose(u.inverse(), inplace=True)
    circuit.barrier()
    circuit.rz(REFLECTION, 4)
    circuit.compose(u, inplace=True)
    circuit.measure(4, 0)
    return circuit


def ideal(arm: str, eps: float) -> float:
    return math.sin((6.0 if arm == "amplified" else 2.0) * eps) ** 2


def physical_sequence(compiled: QuantumCircuit) -> list[tuple[str, tuple[int, ...]]]:
    """Every non-virtual instruction as (name, physical qubits), in order."""
    return [
        (i.operation.name, tuple(compiled.find_bit(q).index for q in i.qubits))
        for i in compiled.data
        if i.operation.name not in ("rz", "barrier")
    ]


def bind(template: QuantumCircuit, arm: str, eps: float | None = None) -> QuantumCircuit:
    values = {"reflection": math.pi if arm == "amplified" else 0.0, "eps": eps}
    return template.assign_parameters({p: values[p.name] for p in template.parameters})


def reference_circuit(m: int, target: int) -> QuantumCircuit:
    """Control |+>, target |target>, 2m barrier-separated CZ, control read in the Y basis."""
    circuit = QuantumCircuit(2, 1)
    circuit.h(0)
    if target:
        circuit.x(1)
    circuit.barrier()
    for _ in range(2 * m):
        circuit.cz(0, 1)
        circuit.barrier()
    circuit.sdg(0)
    circuit.h(0)
    circuit.measure(0, 0)
    return circuit


def compile_all(snapshot: dict[str, Any]) -> dict[str, Any]:
    """The device pair, the eps family and the reference circuits, each noiselessly checked."""
    view = calibration_snapshot.snapshot_backend(snapshot)

    def compiled(eps: Any, layout: list[int] | None) -> QuantumCircuit:
        return transpile(pair_template(eps), view, initial_layout=layout, optimization_level=3, seed_transpiler=SEED)

    device_template = compiled(0.0, None)
    layout = list(device_template.layout.initial_index_layout(filter_ancillas=True)[:5])
    family_template = compiled(EPS_PARAMETER, layout)
    pairs: dict[tuple[str, float], dict[str, QuantumCircuit]] = {
        ("device", 0.0): {arm: bind(device_template, arm) for arm in ARMS}
    }
    for eps in (0.0, *EPS):
        pairs[("family", eps)] = {arm: bind(family_template, arm, eps) for arm in ARMS}
    for (name, eps), pair in pairs.items():
        if physical_sequence(pair["amplified"]) != physical_sequence(pair["echo"]):
            raise SystemExit(f"{name} eps {eps}: the arms differ in their non-virtual gates")
        for arm, circuit in pair.items():
            noiseless = float(snapshot_laws.outcome_law(snapshot, circuit, noisy=False)[0])
            if abs(noiseless - ideal(arm, eps)) > 1e-9:
                raise SystemExit(f"{name} eps {eps} {arm}: noiseless P(anc = 0) {noiseless} against {ideal(arm, eps)}")
    reference = {}
    device = pairs[("device", 0.0)]["echo"]
    for a, b in sorted({tuple(sorted(q)) for _, q in physical_sequence(device) if len(q) == 2}):
        for m in REFERENCE_M:
            for target in (0, 1):
                circuit = transpile(
                    reference_circuit(m, target),
                    view,
                    initial_layout=[a, b],
                    optimization_level=1,
                    seed_transpiler=SEED,
                )
                if sum(1 for i in circuit.data if i.operation.name == "cz") != 2 * m:
                    raise SystemExit(f"reference ({a}, {b}) m = {m}: the compile changed the CZ count")
                noiseless = float(snapshot_laws.outcome_law(snapshot, circuit, noisy=False)[0])
                if abs(noiseless - 0.5) > 1e-9:
                    raise SystemExit(f"reference ({a}, {b}) m = {m}: noiseless P(0) {noiseless} against 1/2")
                reference[(a, b, m, target)] = circuit
    return {"layout": layout, "target": view.target, "pairs": pairs, "reference": reference}


_MODELS: dict[tuple[str, str], LaneModel] = {}


class LawTask:
    """Picklable worker: (backend, key, circuit, channel, magnitude) -> P(clbit 0 = 0)."""

    def __init__(self, device: str) -> None:
        self.device = device

    def __call__(self, item: tuple[str, str, QuantumCircuit, str | None, float]) -> float:
        backend, key, compiled, channel, magnitude = item
        if (backend, key) not in _MODELS:
            snapshot = json.loads((ROOT / SNAPSHOTS[backend]).read_text(encoding="utf-8"))
            local, qubits = local_circuit(compiled)
            _MODELS[(backend, key)] = LaneModel(local, snapshot, qubits, self.device)
        model = _MODELS[(backend, key)]
        name, _, edge = (channel or "").partition("@")
        if edge:
            params = np.zeros(len(model.edges))
            params[int(edge)] = magnitude
            return float(model.law(name, params)[0])
        size = len(model.edges) if channel == EDGE_CHANNEL else model.scheduled.num_qubits
        return float(model.law(channel, np.full(size, magnitude))[0])


def law_items(backend: str, compiled: dict[str, Any], reduced: bool = False) -> list[dict[str, Any]]:
    """Every (circuit, channel, magnitude) the analysis needs; reduced keeps the replay subset."""
    channels = {
        name: tuple(v for v in values if not reduced or abs(v) in REPLAY_MAGNITUDES)
        for name, values in CHANNELS.items()
    }
    eps_grid = (0.0, *REPLAY_EPS) if reduced else (0.0, *EPS)
    mixtures = [(MIX_EPS[0], MIX_DELTA[-1])] if reduced else [(e, d) for e in MIX_EPS for d in MIX_DELTA]

    def pair(compile_name: str, eps: float, channel: str | None, magnitude: float) -> list[dict[str, Any]]:
        return [
            {
                "kind": "pair",
                "compile": compile_name,
                "eps": eps,
                "arm": arm,
                "channel": channel,
                "magnitude": magnitude,
            }
            for arm in ARMS
        ]

    items = pair("device", 0.0, None, 0.0)
    items += [row for name, values in channels.items() for v in values for row in pair("device", 0.0, name, v)]
    edge_count = len(edges(compiled["pairs"][("device", 0.0)]["echo"]))
    edge_sweep = [(0, max(EDGE_DELTA))] if reduced else [(k, d) for k in range(edge_count) for d in EDGE_DELTA]
    items += [row for k, d in edge_sweep for row in pair("device", 0.0, f"{EDGE_CHANNEL}@{k}", d)]
    items += [row for eps in eps_grid for row in pair("family", eps, None, 0.0)]
    items += [row for eps, delta in mixtures for row in pair("family", eps, "cz_conditional_phase", delta)]
    refs = sorted(compiled["reference"])
    for a, b, m, target in refs[: 2 * len(REFERENCE_M)] if reduced else refs:
        settings = [(None, 0.0)] + [(name, v) for name, values in channels.items() for v in values]
        for channel, magnitude in settings:
            items.append(
                {
                    "kind": "reference",
                    "edge": [a, b],
                    "m": m,
                    "target": target,
                    "channel": channel,
                    "magnitude": magnitude,
                }
            )
    return [item | {"backend": backend} for item in items]


def task(item: dict[str, Any], compiled: dict[str, Any]) -> tuple[str, str, QuantumCircuit, str | None, float]:
    if item["kind"] == "pair":
        key = f"pair:{item['compile']}:{item['eps']}:{item['arm']}"
        circuit = compiled["pairs"][(item["compile"], item["eps"])][item["arm"]]
    else:
        a, b = item["edge"]
        key = f"reference:{a}:{b}:{item['m']}:{item['target']}"
        circuit = compiled["reference"][(a, b, item["m"], item["target"])]
    return (item["backend"], key, circuit, item["channel"], float(item["magnitude"]))


def evaluate(
    compiled_by_backend: dict[str, dict[str, Any]], device: str, reduced: bool = False
) -> list[dict[str, Any]]:
    items = [i for backend, c in compiled_by_backend.items() for i in law_items(backend, c, reduced)]
    tasks = [task(i, compiled_by_backend[i["backend"]]) for i in items]
    values = parallel.ordered_map(LawTask(device), tasks, min_items=1)
    return [item | {"p0": value} for item, value in zip(items, values, strict=True)]


KEY_FIELDS = ("backend", "kind", "compile", "eps", "arm", "edge", "m", "target", "channel", "magnitude")


def _key(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(tuple(row[k]) if isinstance(row.get(k), list) else row.get(k) for k in KEY_FIELDS)


def magnitude_at(level: float, points: list[tuple[float, float]]) -> float | None:
    """The smallest sampled crossing x where a response y(x) reaches level, power-law between grid points.

    The answer comes from two sampled points that bracket level, the first
    such pair in x, so a response that already exceeds level at the smallest
    sampled magnitude raises: the grid has to extend below it. A response
    that stays below level on the whole grid gives no answer.
    """
    if points and points[0][1] > level:
        raise ValueError(f"response {points[0][1]:.3g} at |x| = {points[0][0]} already exceeds {level:.3g}")
    pairs = list(zip(points, points[1:], strict=False))
    for (x0, y0), (x1, y1) in pairs:
        if y0 <= level <= y1 and y1 > y0:
            if y0 <= 0:
                return x0 + (x1 - x0) * (level - y0) / (y1 - y0)
            return x0 * (level / y0) ** (math.log(x1 / x0) / math.log(y1 / y0))
    return None


def sign_tolerance(level: float, shifts: dict[float, float]) -> float | None:
    """The |delta| below which both signs of the conditional phase shift the pair by less than level.

    The reference bounds |delta|, so the sign whose response grows faster sets
    the bound: each sign's |shift| curve gives its own magnitude, and the
    smaller one holds for both. A sign that stays below level on the whole
    grid imposes no bound within it.
    """
    bounds = []
    for sign in (1.0, -1.0):
        points = sorted((abs(v), abs(s)) for v, s in shifts.items() if v * sign > 0)
        bound = magnitude_at(level, points)
        if bound is not None:
            bounds.append(bound)
    return min(bounds) if bounds else None


def _reference_shots(variance: float, tolerance: float | None, slope: float) -> int | None:
    """Shots per target state that bound delta to tolerance at z = Z_SCORE through the reference slope."""
    return math.ceil(Z_SCORE**2 * variance / (tolerance * slope) ** 2) if tolerance else None


def verdict(shifts: list[tuple[float, float]]) -> str:
    large = [s for _, s in shifts if abs(s) >= NULL_SHIFT]
    if not large:
        return "null"
    if all(s > 0 for s in large):
        return "undone"
    if all(s < 0 for s in large):
        return "surviving"
    return "odd"


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Class verdicts, mixture cancellation and shot sizing per backend, from the laws alone."""
    p = {_key(row): row["p0"] for row in rows}
    out: dict[str, Any] = {}
    for backend in sorted({row["backend"] for row in rows}):

        def arms(compile_name: str, eps: float, channel: str | None, magnitude: float, b: str = backend) -> list[float]:
            return [p[(b, "pair", compile_name, eps, arm, None, None, None, channel, magnitude)] for arm in ARMS]

        def diff(compile_name: str, eps: float, channel: str | None, magnitude: float) -> float:
            amplified, echo = arms(compile_name, eps, channel, magnitude)
            return amplified - echo

        def variance(compile_name: str, eps: float, channel: str | None, magnitude: float) -> float:
            return sum(x * (1.0 - x) for x in arms(compile_name, eps, channel, magnitude))

        base = diff("device", 0.0, None, 0.0)
        base_var = variance("device", 0.0, None, 0.0)
        family_base = diff("family", 0.0, None, 0.0)
        # Each sweep's shots compare it with its own compile's baseline arm pair.
        family_var = variance("family", 0.0, None, 0.0)
        se = {n: math.sqrt(base_var / n) for n in BUDGETS}
        sweeps = {
            "prep_eps": [
                (eps, diff("family", eps, None, 0.0) - family_base, variance("family", eps, None, 0.0)) for eps in EPS
            ]
        }
        sweeps |= {
            name: [(v, diff("device", 0.0, name, v) - base, variance("device", 0.0, name, v)) for v in values]
            for name, values in CHANNELS.items()
        }
        classes = {
            name: {
                "verdict": verdict([(v, s) for v, s, _ in sweep]),
                "rows": [
                    {
                        "magnitude": v,
                        "shift": s,
                        "shots_per_arm": (
                            math.ceil(Z_SCORE**2 * (var + (family_var if name == "prep_eps" else base_var)) / s**2)
                            if s
                            else None
                        ),
                    }
                    for v, s, var in sweep
                ],
            }
            for name, sweep in sweeps.items()
        }
        uniform = {v: s for v, s, _ in sweeps["cz_conditional_phase"]}
        tolerance = {n: sign_tolerance(se[n], uniform) for n in BUDGETS}
        reference_edges = sorted(
            {tuple(r["edge"]) for r in rows if r["backend"] == backend and r["kind"] == "reference"}
        )
        swept = sorted(
            {
                int(r["channel"].split("@")[1])
                for r in rows
                if r["backend"] == backend and r["kind"] == "pair" and "@" in (r["channel"] or "")
            }
        )
        per_edge: list[dict[str, Any]] = []
        for k in swept:
            shifts = {d: diff("device", 0.0, f"{EDGE_CHANNEL}@{k}", d) - base for d in EDGE_DELTA}
            per_edge.append(
                {
                    "edge": list(reference_edges[k]),
                    "shifts": {str(d): v for d, v in shifts.items()},
                    "delta_tolerance": {str(n): sign_tolerance(se[n], shifts) for n in BUDGETS},
                }
            )
        additivity = [
            {
                "delta": d,
                "uniform_shift": diff("device", 0.0, EDGE_CHANNEL, d) - base,
                "sum_of_edge_shifts": sum(e["shifts"][str(d)] for e in per_edge),
            }
            for d in EDGE_DELTA
        ]
        edge_tolerance = {tuple(e["edge"]): e["delta_tolerance"] for e in per_edge}
        mixtures = []
        for eps in MIX_EPS:
            alone = diff("family", eps, None, 0.0) - family_base
            shifts = {d: diff("family", eps, "cz_conditional_phase", d) - family_base for d in MIX_DELTA}
            cancel = {}
            for side in (1, -1):
                path = [(0.0, alone)] + sorted((abs(d), s) for d, s in shifts.items() if d * side > 0)
                cancel["+" if side > 0 else "-"] = next(
                    (
                        side * (x0 + (x1 - x0) * s0 / (s0 - s1))
                        for (x0, s0), (x1, s1) in zip(path, path[1:], strict=False)
                        if s0 * s1 <= 0 and s0 != s1
                    ),
                    None,
                )
            mixtures.append(
                {
                    "eps": eps,
                    "eps_alone_shift": alone,
                    "shifts": {str(d): s for d, s in shifts.items()},
                    "cancelling_delta": cancel,
                }
            )
        reference = []
        refs = sorted(
            {(tuple(r["edge"]), r["m"]) for r in rows if r["backend"] == backend and r["kind"] == "reference"}
        )
        for edge, m in refs:

            def ref(
                target: int, channel: str | None, magnitude: float, edge: Any = edge, m: int = m, b: str = backend
            ) -> float:
                return p[(b, "reference", None, None, None, edge, m, target, channel, magnitude)]

            def readout(channel: str | None, magnitude: float) -> float:
                return ref(1, channel, magnitude) - ref(0, channel, magnitude)

            zero = readout(None, 0.0)
            slope = (readout("cz_conditional_phase", SLOPE_DELTA) - readout("cz_conditional_phase", -SLOPE_DELTA)) / (
                2 * SLOPE_DELTA
            )
            ref_var = sum(x * (1.0 - x) for x in (ref(1, None, 0.0), ref(0, None, 0.0)))
            reference.append(
                {
                    "edge": list(edge),
                    "m": m,
                    "readout": zero,
                    "slope_per_rad": slope,
                    "cross_sensitivity_rad": {
                        name: max(abs(readout(name, v) - zero) for v in values) / abs(slope)
                        for name, values in CHANNELS.items()
                        if name != "cz_conditional_phase"
                    },
                    "shots_per_target_uniform": {
                        str(n): _reference_shots(ref_var, tolerance[n], slope) for n in BUDGETS
                    },
                    "shots_per_target_edge": {
                        str(n): _reference_shots(ref_var, edge_tolerance[edge][str(n)], slope) for n in BUDGETS
                    },
                }
            )
        undone = [n for n in ROTATIONS if classes[n]["verdict"] == "undone"]
        out[backend] = {
            "baseline": dict(zip(ARMS, arms("device", 0.0, None, 0.0), strict=True)) | {"difference": base},
            "family_baseline_difference": family_base,
            "standard_error": {str(n): v for n, v in se.items()},
            "baseline_is_null": abs(base) <= se[max(BUDGETS)],
            "classes": classes,
            "delta_tolerance": {str(n): v for n, v in tolerance.items()},
            "per_edge": per_edge,
            "additivity": additivity,
            "mixtures": mixtures,
            "reference": reference,
            "undone_rotations": undone,
            "separates": classes["cz_conditional_phase"]["verdict"] == "surviving" and bool(undone),
        }
    return out


def environment(device: str) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "qiskit": qiskit.__version__,
        "qiskit_aer": qiskit_aer.__version__,
        "device": device,
        "workers": parallel.workers(),
    }


def compile_backends(backends: list[str]) -> dict[str, dict[str, Any]]:
    return {
        backend: compile_all(json.loads((ROOT / SNAPSHOTS[backend]).read_text(encoding="utf-8")))
        for backend in backends
    }


def _sequence_digest(circuit: QuantumCircuit) -> str:
    return hashlib.sha256(json.dumps(physical_sequence(circuit)).encode()).hexdigest()


def compile_summary(compiled: dict[str, Any]) -> dict[str, Any]:
    device = compiled["pairs"][("device", 0.0)]["echo"]
    family = compiled["pairs"][("family", 0.0)]["echo"]
    return {
        "layout": compiled["layout"],
        "active_qubits": snapshot_laws.active_qubits(device),
        "device_cz": sum(1 for name, _ in physical_sequence(device) if name == "cz"),
        "family_cz": sum(1 for name, _ in physical_sequence(family) if name == "cz"),
        "device_sequence_sha256": _sequence_digest(device),
        "family_sequence_sha256": _sequence_digest(family),
        "device_duration_dt": int(device.estimate_duration(compiled["target"], unit="dt")),
        "edges": [list(e) for e in edges(device)],
        "reference_edges": sorted({(a, b) for a, b, _, _ in compiled["reference"]}),
    }


def run(device: str) -> tuple[dict[str, Any], list[QuantumCircuit]]:
    started = time.time()
    algebra = algebra_record()
    backends = sorted(SNAPSHOTS)
    compiled = compile_backends(backends)
    rows = evaluate(compiled, device)
    arms = [compiled[b]["pairs"][("device", 0.0)][arm] for b in backends for arm in ARMS]
    result = {
        "schema": "gororoba-echo-dilation-noise-v1",
        "snapshots": {
            b: {"path": SNAPSHOTS[b], "sha256": hashlib.sha256((ROOT / SNAPSHOTS[b]).read_bytes()).hexdigest()}
            for b in backends
        },
        "seed_transpiler": SEED,
        "element": "e1 + e10",
        "input": "(e4 - e15)/sqrt2",
        "algebra": algebra,
        "grid": {
            "eps": EPS,
            "channels": CHANNELS,
            "mix_eps": MIX_EPS,
            "mix_delta": MIX_DELTA,
            "reference_m": REFERENCE_M,
            "budgets": BUDGETS,
            "z_score": Z_SCORE,
            "null_shift": NULL_SHIFT,
        },
        "qpy_arms": [f"{b}:{arm}" for b in backends for arm in ARMS],
        "compiles": {b: compile_summary(compiled[b]) for b in backends},
        "rows": rows,
        "analysis": analyze(rows),
        "environment": environment(device),
        "seconds": round(time.time() - started, 1),
    }
    return result, arms


def bound_to_run(path: Path, arms_path: Path, run_dir: Path) -> list[str]:
    """FILE and the arms must be the byte-identical outputs that run_dir's collect.json ledger records."""
    ledger = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    failures = []
    for name, local in ((OUTPUT, path), (OUTPUT_QPY, arms_path)):
        recorded = ledger["files"].get(f"output/repo/{name}")
        if recorded is None:
            failures.append(f"{run_dir}/collect.json records no {name}")
        elif hashlib.sha256(local.read_bytes()).hexdigest() != recorded:
            failures.append(f"{local} differs from the collected {name}")
    return failures


def check(path: Path, arms_path: Path, run_dir: Path) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    failures = bound_to_run(path, arms_path, run_dir)
    algebra = retained["algebra"]
    signs = [cd_sign(DIM, a, b) for a, b in algebra["products"]]
    if signs != algebra["cd_core_signs"]:
        failures.append("cd_core signs differ from the retained algebra record")
    for name, entry in algebra.get("packages", {}).items():
        if name == "unavailable" or entry["signs"] != signs:
            failures.append(f"package record {name} is unavailable or differs from cd_core")
    backend = "ibm_kingston"
    compiled = compile_backends([backend])
    fresh = json.loads(json.dumps(compile_summary(compiled[backend])))
    if fresh != retained["compiles"][backend]:
        failures.append(f"{backend} compile summary {fresh} against {retained['compiles'][backend]}")
    with arms_path.open("rb") as stream:
        kept_arms = qpy.load(stream)
    for kept, label in zip(kept_arms, retained["qpy_arms"], strict=True):
        name, arm = label.split(":")
        if name != backend:
            continue
        recompiled = compiled[backend]["pairs"][("device", 0.0)][arm]
        angles = [[float(x) for x in i.operation.params] for i in kept.data if i.operation.name == "rz"]
        fresh_angles = [[float(x) for x in i.operation.params] for i in recompiled.data if i.operation.name == "rz"]
        if physical_sequence(kept) != physical_sequence(recompiled) or not np.allclose(angles, fresh_angles):
            failures.append(f"retained {label} differs from the recompiled arm")
    kept_rows = {_key(row): row["p0"] for row in retained["rows"]}
    for row in evaluate(compiled, calibration_snapshot.aer_device(), reduced=True):
        old = kept_rows.get(_key(row))
        if old is None:
            failures.append(f"{_key(row)} is absent from {path}")
        elif not math.isclose(row["p0"], old, rel_tol=1e-8, abs_tol=1e-10):
            failures.append(f"{_key(row)}: P0 {row['p0']} against {old}")
    if json.loads(json.dumps(analyze(retained["rows"]))) != retained["analysis"]:
        failures.append("the analysis recomputed from the retained laws differs from the retained analysis")
    for failure in failures:
        print(failure)
    print(f"echo dilation noise replay: {backend} compile and reduced laws, every verdict, {len(failures)} departures")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="write the result here and the device arms beside it as QPY")
    parser.add_argument("--check", type=Path)
    parser.add_argument("--arms", type=Path, help="the retained device arms (QPY) --check binds")
    parser.add_argument("--run", type=Path, help="Kaggle run directory whose collected output --check binds")
    args = parser.parse_args()
    if args.check:
        if args.run is None or args.arms is None:
            parser.error("--check needs --arms and --run")
        return check(args.check, args.arms, args.run)
    if args.out is None:
        parser.error("--out is required without --check")
    result, arms = run(calibration_snapshot.aer_device())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    with args.out.with_name(Path(OUTPUT_QPY).name).open("wb") as stream:
        qpy.dump(arms, stream)
    verdicts = {b: {n: c["verdict"] for n, c in a["classes"].items()} for b, a in result["analysis"].items()}
    print(f"wrote {args.out} in {result['seconds']} s: {verdicts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
