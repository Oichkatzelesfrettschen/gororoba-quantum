"""Coset-block map of the 32-dimensional Cayley-Dickson kernel map on Tuna-17, and its QX twin.

gororoba_quantum/pathion_kernel_map.py defines the pair-resolved kernel map of the operand e_i + t e_j of A_5 on six
qubits; the full map routes to 116 to 144 CZ on the admitted Tuna-17 qubits and does not resolve at the retained
0.955 to 0.9654 contrast per CZ. gororoba_quantum/pathion_coset_block.py restricts it exactly to a coset block, 8
inputs, 4 XOR pairs and 16 SELECT signs on three data qubits and the selector. This case runs three blocks on one
admitted 4-qubit region of Tuna-17:

| template | operand | V = span | coset | aligned pairs N_b |
|---|---|---|---|---|
| ba | e1 + e18 | 19, 2, 12 | 1 | 2 |
| bb | e1 + e26 | 27, 2, 9 | 0 | 2 |
| b0 | e1 + e17 | 16, 1, 2 | 0 | 0 |
| xor_ba | ba with every SELECT sign table replaced by its cocycle-free XOR permutation | | | selector contrast -1 |

Each template compiles once with the orientation phase as a parameter (``ORIENTATION``), so the minus and plus arms
bind one routed circuit, share every CZ and differ by a phase pi on data qubit 0 before routing. Every rotation is
rounded to the nearest multiple of pi/36, the grid Tuna applies itself, and the ideal law of record is the
Statevector of the exact rounded routed circuit, read through the circuit's final layout.

Region and routing. The admitted qubits are the complement of zd.excluded_qubits() (the readout faults and the Ramsey
visibility floor of qi_zero_divisor_cases) and of q15, which reads P(0|1) 0.270 (tuna17-bipartite-designs.md). A
connected 4-qubit region is admitted when every coupler inside it has a retained residual coupling |J| of at most
J_LIMIT_HZ (the coupler-ZZ analysis, which rejects (1,4) at -19.3 kHz and (11,14) at -31.4 kHz). Every template
routes onto every admitted region at the candidate transpiler seeds of its own slice of one retained ANU QRNG draw
(DRAW, CANDIDATES per template, slice t holds draw indices t * CANDIDATES to (t + 1) * CANDIDATES - 1), and the whole
series runs on the one region with the fewest routed CZ summed over ba, bb and b0 (ties: the lexicographically least
region). Each template keeps the fewest-CZ candidate on that region (ties: the lowest index).

Series. One batch holds an arm pair and one readout circuit, so the minus and plus arm of a contrast share a
calibration, and each template runs two replicates, the first as (plus, minus), the second as (minus, plus). Batch
index 4 * replicate + template carries readout-0 when replicate + template is even and readout-1 otherwise, so every
contrast sees both readout references and neither reference follows one replicate.

Preregistered decisions (Z_RESOLVE standard errors; raw counts, pooled over a template's replicates):
- resolution: ba and bb each read the ideal sign of at least 6 of their 8 bins at Z_RESOLVE;
- pattern: ba and bb differ in two bins of c(y), and the two blocks read opposite signs there at Z_RESOLVE, so the
  selector contrast (0.5 for both) is not the observable;
- null: the b0 selector contrast lies within Z_RESOLVE standard errors of zero;
- cocycle-free: the xor_ba selector contrast is negative at Z_RESOLVE and the ba selector contrast positive;
- depth: the contraction per CZ implied by each template's visibility lies inside or outside the retained band
  RHO_BAND, reported with the template's routed CZ;
- cross-platform: the readout-corrected Tuna ratio c(y) / V of ba, bb and b0 differs from the measured IBM ratio
  c(k) / V_I of the same algebra labels (ibm_fez and ibm_marrakesh coset-map runs, IBM_RECORDS) by at most Z_RESOLVE
  combined standard errors on at least CROSS_BINS_MIN of 8 bins against each device, D(y) = 0 being the prediction;
- drift: no readout circuit moves a register qubit by more than 0.02 against the previous circuit of its kind
  (qi_pathion_coset_block_series.DRIFT_STOP); the series gate stops before the next batch is submitted.

Usage: "$PYTHON" scripts/qi_pathion_coset_block_cases.py
       (--write DIR | --check DIR | --select-region | --qx-conformance RUN_DIR | --analyze RUN_DIR... --out FILE
        | --self-test)
--analyze scores the collected batches of one series: the preregistered decisions, per-template c(y), visibility,
nullity estimate N_hat and selector contrast with delta-method errors, the comparison with the measured IBM runs
and the drift rule; a stopped series reports its batches and drift only, and a QX series reports the control verdict
that qi_pathion_coset_block_series.py --submit-next needs before the first Tuna-17 batch.
--write DIR writes DIR/pathion_coset_block_tuna_17/ and DIR/pathion_coset_block_qx/ (batch-NN/ cases under a series
cases.json); --check regenerates both and compares bytes and file sets; --qx-conformance reads a local qxelarator run
of the Tuna series (scripts/qx_local_series.py) and compares each circuit with its ideal law. Bit strings put qubit 0
at the rightmost character.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_cancellation_cases as kcc  # noqa: E402
import qi_pathion_coset_block_series as pcs  # noqa: E402
import qi_zero_divisor_cases as zd  # noqa: E402

import parallel  # noqa: E402
import pathion_coset_block as pcb  # noqa: E402
import pathion_kernel_map as pkm  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

TUNA_SERIES = "pathion_coset_block_tuna_17"
QX_SERIES = "pathion_coset_block_qx"
NQUBITS = 17
SHOTS = 16384
QX_QUBITS = 10
QX_SHOTS = 2048
GRID = kcc.GRID
BASIS = kcc.BASIS
Z_RESOLVE = 3.0
ANALYSIS_SCHEMA = "qi-pathion-coset-block-analysis-v2"
# The ANU QRNG draw whose 64 values seed every routing candidate; it belongs to this case's manifest.
DRAW = "docs/evidence/anu_qrng/draw-2026-11-06T184327Z.json"
CANDIDATES = 16
EXTRA_EXCLUDED = (15,)
J_LIMIT_HZ = 1.0e4
REGION_SIZE = 4
RHO_BAND = (0.955, 0.9654)
# Retained per-qubit readout of the region qubits: the six readout circuits of the kernel-cancellation series.
READOUT_RUNS = tuple(
    ROOT / "results/quantum_inspire/runs" / f"2026-10-23T{stamp}-kernel_cancellation_tuna_17-batch-{batch:02d}"
    for batch, stamp in enumerate(("075543Z", "080006Z", "080624Z", "081101Z", "081536Z", "082011Z"))
)

BLOCKS = {
    "ba": pcb.Block("ba", (1, 18, 1), (19, 2, 12), 1),
    "bb": pcb.Block("bb", (1, 26, 1), (27, 2, 9), 0),
    "b0": pcb.Block("b0", (1, 17, 1), (16, 1, 2), 0),
}
# (template name, block key, cocycle-free); the order fixes the draw slice and the batch order.
TEMPLATES = (("ba", "ba", False), ("bb", "bb", False), ("b0", "b0", False), ("xor_ba", "ba", True))
PRIMARY = ("ba", "bb", "b0")
SELECTOR = 3


def template_circuit(name: str) -> Any:
    _, key, free = next(t for t in TEMPLATES if t[0] == name)
    return pcb.block_template(BLOCKS[key], cocycle_free=free, measure=False)


def logical_laws(name: str) -> dict[bool, Any]:
    _, key, free = next(t for t in TEMPLATES if t[0] == name)
    return {
        plus: pcb.block_law(pcb.block_circuit(BLOCKS[key], plus, cocycle_free=free, measure=False))
        for plus in (False, True)
    }


def draw_values() -> list[int]:
    values = read_record(DRAW)["values"]
    if len(values) != CANDIDATES * len(TEMPLATES):
        raise ValueError(f"{DRAW} holds {len(values)} values, not {CANDIDATES * len(TEMPLATES)}")
    return [int(v) for v in values]


def candidate_seeds(index: int) -> list[tuple[int, int]]:
    """(draw index, transpiler seed value) of the candidates of template `index`."""
    values = draw_values()
    return [(n, values[n]) for n in range(index * CANDIDATES, (index + 1) * CANDIDATES)]


def coupler_limit_regions(topology: tuple[tuple[int, int], ...]) -> list[tuple[int, ...]]:
    """Connected REGION_SIZE-qubit regions off the excluded qubits whose inner couplers all satisfy J_LIMIT_HZ."""
    analysis = json.loads(zd.COUPLER_ZZ_ANALYSIS.read_text(encoding="utf-8"))
    coupling = {tuple(sorted(row["edge"])): abs(row["j_hz"]) for row in analysis["edges"]}
    out = []
    for region in zd.connected_regions(topology, REGION_SIZE):
        inside = {tuple(sorted(e)) for e in topology if e[0] in region and e[1] in region}
        if set(region) & set(EXTRA_EXCLUDED) or any(coupling[e] > J_LIMIT_HZ for e in inside):
            continue
        out.append(region)
    return out


class RouteCount:
    """Routed CZ count of one (template index, region, seed value); a module-level callable for the pool."""

    def __init__(self, topology: tuple[tuple[int, int], ...]) -> None:
        self.topology = topology

    def __call__(self, item: tuple[int, tuple[int, ...], int]) -> int:
        index, region, seed = item
        return int(compile_template(self.topology, index, region, seed).count_ops().get("cz", 0))


def compile_template(topology: tuple[tuple[int, int], ...], index: int, region: tuple[int, ...], seed: int) -> Any:
    from qiskit import transpile
    from qiskit.transpiler import CouplingMap

    local = {q: n for n, q in enumerate(region)}
    edges = [[local[a], local[b]] for a, b in topology if a in local and b in local]
    coupling = CouplingMap(edges + [[b, a] for a, b in edges])
    return transpile(
        template_circuit(TEMPLATES[index][0]),
        coupling_map=coupling,
        basis_gates=BASIS,
        optimization_level=2,
        seed_transpiler=seed,
    )


@cache
def routing_table(
    topology: tuple[tuple[int, int], ...],
) -> dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int]]]:
    """(template index, region) -> [(draw index, seed value, routed CZ)] over every admitted region."""
    regions = coupler_limit_regions(topology)
    items = [(t, region, seed) for t in range(len(TEMPLATES)) for region in regions for _, seed in candidate_seeds(t)]
    counts = parallel.ordered_map(RouteCount(topology), items)
    table: dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int]]] = {}
    position = 0
    for t in range(len(TEMPLATES)):
        for region in regions:
            row = []
            for n, seed in candidate_seeds(t):
                row.append((n, seed, counts[position]))
                position += 1
            table[(t, region)] = row
    return table


def choose_region(table: dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int]]]) -> tuple[int, ...]:
    regions = sorted({region for _, region in table})
    primary = [i for i, t in enumerate(TEMPLATES) if t[0] in PRIMARY]
    return min(regions, key=lambda r: (sum(min(c for *_, c in table[(t, r)]) for t in primary), r))


def round_to_grid(circuit: Any) -> Any:
    from qiskit.circuit.library import RZGate

    out = circuit.copy()
    for k, instruction in enumerate(out.data):
        if instruction.operation.name == "rz":
            angle = float(instruction.operation.params[0])
            out.data[k] = instruction.replace(operation=RZGate(round(angle / GRID) * GRID))
    return out


def bind_arm(compiled: Any, plus: bool) -> Any:
    """The compile bound at one orientation, every rotation on the pi/36 grid; parameters bind by name."""
    value = math.pi if plus else 0.0
    bound = compiled.assign_parameters({p: value for p in compiled.parameters if p.name == pcb.ORIENTATION.name})
    return round_to_grid(bound)


def skeleton(circuit: Any) -> list[tuple[str, tuple[int, ...]]]:
    """Every non-rotation operation in order with its qubits: the part the two arms must share."""
    return [
        (i.operation.name, tuple(circuit.find_bit(q).index for q in i.qubits))
        for i in circuit.data
        if i.operation.name != "rz"
    ]


def rz_sites(circuit: Any) -> list[tuple[int, ...]]:
    return [tuple(circuit.find_bit(q).index for q in i.qubits) for i in circuit.data if i.operation.name == "rz"]


def ideal_of_record(bound: Any) -> np.ndarray:
    """Outcome law of the rounded routed circuit over the logical bits (data 0-2, selector 3), index y + 8 s."""
    from qiskit.quantum_info import Statevector

    final = bound.layout.final_index_layout()
    physical = Statevector(bound).probabilities()
    logical = np.zeros_like(physical)
    for index, value in enumerate(physical):
        v = sum(1 << bit for bit in range(bound.num_qubits) if index >> final[bit] & 1)
        logical[v] += value
    return logical


def retained_readout(region: tuple[int, ...]) -> dict[int, tuple[float, float]]:
    """(e01, e10) of each region qubit from the retained readout circuits: mean P(1 | prepared 0) and
    1 - mean P(1 | prepared 1) over the readout-0 and readout-1 runs of the kernel-cancellation series."""
    zero: dict[int, list[float]] = {q: [] for q in region}
    one: dict[int, list[float]] = {q: [] for q in region}
    for run in READOUT_RUNS:
        for name, bucket in (("readout-0.cq", zero), ("readout-1.cq", one)):
            path = run / "raw" / f"{name}.json"
            if not path.exists():
                continue
            shots = json.loads(path.read_text(encoding="utf-8"))
            for q in region:
                bucket[q].append(sum(bit(s, q) for s in shots) / len(shots))
    return {q: (float(np.mean(zero[q])), 1.0 - float(np.mean(one[q]))) for q in region if zero[q] and one[q]}


bit = pcs.bit


def confusion(readout: list[tuple[float, float]]) -> np.ndarray:
    """Joint assignment matrix over the logical bits: row = measured, column = true, bit v of the index."""
    matrix = np.ones((1, 1))
    for e01, e10 in reversed(readout):
        matrix = np.kron(matrix, np.array([[1 - e01, e10], [e01, 1 - e10]]))
    return matrix


def conditional_contrast(plus: np.ndarray, minus: np.ndarray) -> tuple[float, np.ndarray]:
    return pcb.selector_contrast(plus, minus), pcb.output_contrast(plus, minus)


def forecast(ideal: dict[bool, np.ndarray], cz: int, rho: float, readout: list[tuple[float, float]]) -> dict[str, Any]:
    """Raw contrasts of a device that contracts the 16-outcome law toward uniform by rho^cz and then misassigns each
    bit with the retained single-qubit assignment (hypothesis-level model), and the shot error of pooled replicates."""
    retention = rho**cz
    matrix = confusion(readout)
    law = {p: matrix @ (retention * ideal[p] + (1 - retention) / ideal[p].size) for p in (False, True)}
    selector, per_bin = conditional_contrast(law[True], law[False])
    ideal_bins = pcb.output_contrast(ideal[True], ideal[False])
    sign = np.sign(ideal_bins)
    decided = np.abs(ideal_bins) > 0.5
    half = law[True].size // 2
    sigma = []
    for y in range(half):
        var = 0.0
        for p in (False, True):
            weight = law[p][y] + law[p][y + half]
            p0 = law[p][y] / weight
            var += p0 * (1 - p0) / (SHOTS * 2 * weight)
        sigma.append(math.sqrt(var))
    return {
        "retention": retention,
        "selector_contrast": selector,
        "c": [round(float(x), 6) for x in per_bin],
        "visibility": float(np.mean(per_bin[decided] * sign[decided])),
        "se_per_bin_two_replicates": [round(s, 6) for s in sigma],
        "z_per_bin": [round(float(abs(c) / s), 2) for c, s in zip(per_bin, sigma, strict=True)],
        "selector_se": math.sqrt(2 * 0.25 / (SHOTS * 2)),
    }


# Cross-platform reference: the measured IBM coset-map runs ---------------------------------------------------

IBM_GROUP = "pathion_coset_map"
IBM_RECORDS = {
    "ibm_fez": {
        "collect": "results/live/2026-11-06T201037.234804Z/collect.json",
        "job": "dbn3a55t7fqc73ais42g",
        "sha256": "bbb2415b53e07e97e745b3da472114afb84cb0fc8be34686a39b7fac18d15051",
    },
    "ibm_marrakesh": {
        "collect": "results/live/2026-11-06T200832.558771Z/collect.json",
        "job": "dbn38t0ou4as73b3q1n0",
        "sha256": "003031ac080ca40af9c20924109b5659c38b06554591eb65ef1f68e853c76093",
    },
}
# The cross-platform rule decides on the readout-corrected Tuna ratio c(y) / V: a device that contracts every bin
# alike and then misassigns each bit reads a raw ratio that departs from the ideal sign by its assignment asymmetry,
# which the correction from the series' own readout circuits removes.
CROSS_STATISTIC = "readout_corrected"
CROSS_BINS_MIN = 7
# A QX control arm passes when its total variation distance to the ideal law of record stays within this factor of
# the sampling floor expected under that law.
CONTROL_FLOOR_FACTOR = 2.0
REPLICATES = 2


def operand_tag(block_key: str) -> str:
    return pkm.operand_tag(BLOCKS[block_key].operand)


@cache
def ideal_block_contrast(operand: tuple[int, int, int], basis: tuple[int, ...], k0: int) -> np.ndarray:
    block = pcb.Block(f"k{k0}", operand, basis, k0)
    return pcb.output_contrast(
        pcb.block_law(pcb.block_circuit(block, True, measure=False)),
        pcb.block_law(pcb.block_circuit(block, False, measure=False)),
    )


@cache
def ibm_reference(device: str) -> dict[str, dict[str, Any]]:
    """Measured IBM per-output ratio c(k) / V of every coset block of each primary operand, keyed by operand tag.

    The collect record holds, per member `cmap_<operand>_k<coset>_{plus,minus}`, one 16-outcome law per replica
    (index y + 8 s, data bits first). Per replica: c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y), V the mean of c
    times the ideal sign, and the ratio c / V; a bin's ratio is the mean over replicas. `ratio_se` is the standard
    error of that mean and `ratio_spread` the standard deviation over replicas, which `labels[...]["se"]` carries:
    the Tuna block is one placement, so the IBM ratio it is compared with is one placement's draw from the
    replica distribution, and the tolerance of D is that spread (the IBM ratio departs from the ideal sign by its
    own readout asymmetry and noise, which the replica spread brackets). `labels` maps the algebra output index of
    each bin to its entry, so a Tuna block with another basis compares by label."""
    spec = IBM_RECORDS[device]
    path = ROOT / spec["collect"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != spec["sha256"]:
        raise ValueError(f"{path} differs from the retained record its digest pins")
    group = next(
        g for g in json.loads(path.read_text(encoding="utf-8")) if isinstance(g, dict) and g.get("group") == IBM_GROUP
    )
    if group["backend"] != device or group["job_id"] != spec["job"]:
        raise ValueError(f"{path} is not the {device} job {spec['job']}")
    measured = group["measured"]
    out: dict[str, dict[str, Any]] = {}
    for key in PRIMARY:
        operand = BLOCKS[key].operand
        basis = pcb.default_basis(operand)
        labels: dict[int, dict[str, Any]] = {}
        blocks: dict[int, dict[str, Any]] = {}
        replicas = 0
        for k0 in pcb.cosets(basis):
            ideal = ideal_block_contrast(operand, basis, k0)
            sign = np.sign(ideal)
            prefix = f"cmap_{pkm.operand_tag(operand)}_k{k0}"
            plus, minus = np.array(measured[f"{prefix}_plus"]), np.array(measured[f"{prefix}_minus"])
            c = np.array([pcb.output_contrast(p, m) for p, m in zip(plus, minus, strict=True)])
            visibility = (c * sign).mean(axis=1)
            ratio = c / visibility[:, None]
            nullity = c.sum(axis=1) / 2.0 / visibility
            replicas = len(c)
            root = math.sqrt(replicas)
            block = pcb.Block(f"k{k0}", operand, basis, k0)
            blocks[k0] = {
                "visibility": float(visibility.mean()),
                "visibility_se": float(visibility.std(ddof=1) / root),
                "nullity_estimate": float(nullity.mean()),
                "nullity_se": float(nullity.std(ddof=1) / root),
                "nullity_ideal": float(ideal.sum() / 2.0),
                "bin_labels": pcb.output_labels(block),
                "c": [float(x) for x in c.mean(axis=0)],
                "ratio": [float(x) for x in ratio.mean(axis=0)],
                "ratio_se": [float(x) for x in ratio.std(axis=0, ddof=1) / root],
                "ratio_spread": [float(x) for x in ratio.std(axis=0, ddof=1)],
            }
            for y, label in enumerate(pcb.output_labels(block)):
                labels[label] = {
                    "coset": k0,
                    "bin": y,
                    "ratio": blocks[k0]["ratio"][y],
                    "se": blocks[k0]["ratio_spread"][y],
                    "se_mean": blocks[k0]["ratio_se"][y],
                    "visibility": blocks[k0]["visibility"],
                }
        if sorted(labels) != list(range(pkm.DIM)):
            raise ValueError(f"{device} {key}: the coset blocks do not cover the 32 output labels once")
        out[operand_tag(key)] = {"replicas": replicas, "blocks": blocks, "labels": labels}
    return out


def contrast_outputs(counts: np.ndarray, sign: np.ndarray, matrix: np.ndarray | None) -> np.ndarray:
    """c(y) of the 8 bins, c / V, V and the nullity estimate N_hat from stacked [plus, minus] counts of 16 outcomes.

    V is the mean of c times the ideal sign and N_hat = (sum of c) / (2 V); `matrix`, when given, is the joint
    assignment matrix the counts are corrected with first."""
    plus, minus = counts[:16], counts[16:]
    if matrix is not None:
        plus, minus = np.linalg.solve(matrix, plus), np.linalg.solve(matrix, minus)
    c = pcb.output_contrast(plus / plus.sum(), minus / minus.sum())
    v = float(np.mean(c * sign))
    return np.concatenate([c, c / v, [v, c.sum() / 2.0 / v]])


def contrast_statistics(
    plus: np.ndarray, minus: np.ndarray, sign: np.ndarray, matrix: np.ndarray | None = None
) -> dict[str, Any]:
    """c(y), c / V, V and N_hat of an arm pair with standard errors by the delta method.

    The counts of each arm are multinomial, so the covariance is N (diag p - p p^T) per arm; the Jacobian of
    contrast_outputs is a central difference of one count, which is deterministic and needs no random draw."""
    x = np.concatenate([plus, minus]).astype(float)
    base = contrast_outputs(x, sign, matrix)
    jac = np.empty((base.size, x.size))
    for i in range(x.size):
        up, down = x.copy(), x.copy()
        up[i] += 1.0
        down[i] -= 1.0
        jac[:, i] = (contrast_outputs(up, sign, matrix) - contrast_outputs(down, sign, matrix)) / 2.0
    cov = np.zeros((x.size, x.size))
    for low, arm in ((0, plus), (16, minus)):
        p = arm / arm.sum()
        cov[low : low + 16, low : low + 16] = arm.sum() * (np.diag(p) - np.outer(p, p))
    se = np.sqrt(np.einsum("ij,jk,ik->i", jac, cov, jac))
    return {
        "c": [float(v) for v in base[:8]],
        "c_se": [float(v) for v in se[:8]],
        "ratio": [float(v) for v in base[8:16]],
        "ratio_se": [float(v) for v in se[8:16]],
        "visibility": float(base[16]),
        "visibility_se": float(se[16]),
        "nullity_estimate": float(base[17]),
        "nullity_se": float(se[17]),
    }


def cross_platform(
    statistics: dict[str, Any], labels: list[int], reference: dict[str, Any], z_limit: float = Z_RESOLVE
) -> dict[str, Any]:
    """D(y) = c_T(y) / V_T - c_I(label(y)) / V_I on the 8 bins of a Tuna block, against one IBM device.

    `labels` is the block's algebra index of each bin (the case's label table), `reference` one operand's entry of
    ibm_reference; the Tuna side carries its delta-method error, the IBM side the replica spread, and the bins are
    compared at the quadrature sum.
    The prediction is D = 0 within z_limit combined standard errors on at least CROSS_BINS_MIN of the 8 bins;
    `z_of_mean` reports the same difference against the standard error of the IBM mean instead of its spread."""
    ibm = [reference["labels"][label] for label in labels]
    tuna = statistics["ratio"]
    difference = [t - i["ratio"] for t, i in zip(tuna, ibm, strict=True)]
    se = [math.hypot(s, i["se"]) for s, i in zip(statistics["ratio_se"], ibm, strict=True)]
    z = [float(v) for v in z_score(difference, se)]
    se_mean = [math.hypot(s, i["se_mean"]) for s, i in zip(statistics["ratio_se"], ibm, strict=True)]
    z_mean = [float(v) for v in z_score(difference, se_mean)]
    return {
        "labels": list(labels),
        "tuna_ratio": list(tuna),
        "ibm_ratio": [i["ratio"] for i in ibm],
        "ibm_coset": [i["coset"] for i in ibm],
        "difference": difference,
        "se": se,
        "z": z,
        "z_of_mean": z_mean,
        "bins_within": int(sum(abs(v) <= z_limit for v in z)),
    }


def refutation_probability(difference: list[float], se: list[float], tuna_se: list[float]) -> float:
    """Probability that a device obeying the model reads fewer than CROSS_BINS_MIN of 8 bins inside Z_RESOLVE
    combined standard errors, by exact enumeration of the independent bins.

    Each bin reads D ~ Normal(difference, tuna_se) around the predicted difference, because the IBM ratio is a
    fixed measured number; a bin fails when |D| exceeds Z_RESOLVE * se."""

    def cdf(x: float) -> float:
        return 0.5 * math.erfc(-x / math.sqrt(2.0))

    fail = [
        cdf((-Z_RESOLVE * s - d) / t) + cdf((-Z_RESOLVE * s + d) / t)
        for d, s, t in zip(difference, se, tuna_se, strict=True)
    ]
    # Poisson-binomial law of the number of failing bins; the rule holds up to len(fail) - CROSS_BINS_MIN of them.
    law = np.array([1.0])
    for q in fail:
        law = np.convolve(law, [1.0 - q, q])
    return float(law[len(fail) - CROSS_BINS_MIN + 1 :].sum())


def model_statistics(
    template: dict[str, Any], rho: float, readout: list[tuple[float, float]]
) -> dict[str, dict[str, Any]]:
    """Expected raw and readout-corrected statistics of the contraction model at pooled replicates: the law
    of record contracted by rho^cz, misassigned by the retained readout, as expected counts at 2 x SHOTS per arm."""
    retention = rho ** template["cz"]
    matrix = confusion(readout)
    ideal = template["ideal"]
    law = {p: matrix @ (retention * ideal[p] + (1 - retention) / ideal[p].size) for p in (False, True)}
    counts = {p: law[p] * REPLICATES * SHOTS for p in law}
    sign = np.sign(pcb.output_contrast(ideal[True], ideal[False]))
    return {
        "raw": contrast_statistics(counts[True], counts[False], sign),
        "readout_corrected": contrast_statistics(counts[True], counts[False], sign, matrix),
    }


def build_plan() -> dict[str, Any]:
    tuna, _ = zd.catalogue_check()
    topology = tuple(sorted({tuple(sorted(edge)) for edge in tuna["topology"]}))
    table = routing_table(topology)
    region = choose_region(table)
    templates: dict[str, dict[str, Any]] = {}
    for t, (name, key, free) in enumerate(TEMPLATES):
        n, seed, cz = min(table[(t, region)], key=lambda row: (row[2], row[0]))
        compiled = compile_template(topology, t, region, seed)
        arms = {plus: bind_arm(compiled, plus) for plus in (False, True)}
        if skeleton(arms[False]) != skeleton(arms[True]) or rz_sites(arms[False]) != rz_sites(arms[True]):
            raise ValueError(f"{name}: the two arms do not share one routed gate sequence")
        final = compiled.layout.final_index_layout()
        templates[name] = {
            "block": key,
            "cocycle_free": free,
            "draw_index": n,
            "transpiler_seed": seed,
            "cz": cz,
            "roles": {f"d{v}": int(final[v]) for v in range(3)} | {"selector": int(final[SELECTOR])},
            "arms": arms,
            "ideal": {plus: ideal_of_record(arms[plus]) for plus in (False, True)},
            "unrounded": logical_laws(name),
        }
    return {"region": region, "table": table, "templates": templates}


def rounding_gap(template: dict[str, Any]) -> float:
    return float(max(np.abs(template["ideal"][p] - template["unrounded"][p]).max() for p in (False, True)))


def label_table() -> dict[str, Any]:
    """Tuna bin y of each block against the IBM full-map outcome index k_out (add 32 for the selector value 1)."""
    return {
        key: {
            "operand": list(block.operand),
            "basis": list(block.basis),
            "coset": block.coset,
            "ibm_data_index_of_bin": pcb.output_labels(block),
        }
        for key, block in BLOCKS.items()
    }


def ideal_summary(template: dict[str, Any]) -> dict[str, Any]:
    plus, minus = template["ideal"][True], template["ideal"][False]
    selector, per_bin = conditional_contrast(plus, minus)
    return {
        "selector_contrast": round(float(selector), 6),
        "c": [round(float(x), 6) for x in per_bin],
    }


def predictions(plan: dict[str, Any]) -> dict[str, Any]:
    readout = retained_readout(plan["region"])
    out: dict[str, Any] = {
        "model": "contraction of the 16-outcome law toward uniform by rho^cz, then the retained single-qubit "
        "assignment; hypothesis-level",
        "rho_band": list(RHO_BAND),
        "readout_runs": [p.relative_to(ROOT).as_posix() for p in READOUT_RUNS],
        "readout_e01_e10": {str(q): [round(a, 4), round(b, 4)] for q, (a, b) in readout.items()},
        "templates": {},
    }
    for name, t in plan["templates"].items():
        roles = t["roles"]
        per_bit = [readout[plan["region"][roles[k]]] for k in ("d0", "d1", "d2", "selector")]
        out["templates"][name] = {f"rho_{rho}": forecast(t["ideal"], t["cz"], rho, per_bit) for rho in RHO_BAND}
    out["ibm_measured"] = {device: ibm_summary(device) for device in IBM_RECORDS}
    out["cross_platform"] = cross_platform_prediction(plan, readout)
    return out


def rounded(values: list[float]) -> list[float]:
    return [round(float(v), 6) for v in values]


def ibm_summary(device: str) -> dict[str, Any]:
    """The measured IBM values the cross-platform rule compares against, per operand and coset block."""
    spec = IBM_RECORDS[device]
    reference = ibm_reference(device)
    return {
        "collect": spec["collect"],
        "collect_sha256": spec["sha256"],
        "job": spec["job"],
        "operands": {
            tag: {
                "replicas": entry["replicas"],
                "blocks": {
                    f"k{k0}": {
                        "bin_labels": block["bin_labels"],
                        "visibility": round(block["visibility"], 6),
                        "visibility_se": round(block["visibility_se"], 6),
                        "c": rounded(block["c"]),
                        "ratio": rounded(block["ratio"]),
                        "ratio_se": rounded(block["ratio_se"]),
                        "ratio_spread": rounded(block["ratio_spread"]),
                        "nullity_estimate": round(block["nullity_estimate"], 6),
                        "nullity_se": round(block["nullity_se"], 6),
                        "nullity_ideal": block["nullity_ideal"],
                    }
                    for k0, block in sorted(entry["blocks"].items())
                },
            }
            for tag, entry in reference.items()
        },
    }


def cross_platform_prediction(plan: dict[str, Any], readout: dict[int, tuple[float, float]]) -> dict[str, Any]:
    """The preregistered D(y) of each primary template against each measured IBM device, under the contraction
    model of the Tuna block: the expected D from the modeled ratio and the measured IBM ratio, with the number
    of bins inside the combined error. The decision statistic is CROSS_STATISTIC; the raw ratio is reported."""
    out: dict[str, Any] = {
        "rule": f"D(y) = c_T(y) / V_T - c_I(label(y)) / V_I within {Z_RESOLVE} combined standard errors on at least "
        f"{CROSS_BINS_MIN} of 8 bins of each primary template, against each IBM device; the Tuna ratio is "
        f"{CROSS_STATISTIC}, assignment from the series' own readout circuits",
        "statistic": CROSS_STATISTIC,
        "templates": {},
    }
    survive = {f"rho_{rho}": 1.0 for rho in RHO_BAND}
    for name in PRIMARY:
        t = plan["templates"][name]
        labels = pcb.output_labels(BLOCKS[t["block"]])
        roles = t["roles"]
        per_bit = [readout[plan["region"][roles[k]]] for k in ("d0", "d1", "d2", "selector")]
        entry: dict[str, Any] = {"labels": labels}
        for device in IBM_RECORDS:
            reference = ibm_reference(device)[operand_tag(t["block"])]
            cell: dict[str, Any] = {}
            for rho in RHO_BAND:
                model = model_statistics(t, rho, per_bit)
                cell[f"rho_{rho}"] = {
                    statistic: {
                        key: value if key in ("labels", "ibm_coset", "bins_within") else rounded(value)
                        for key, value in cross_platform(model[statistic], labels, reference).items()
                    }
                    for statistic in model
                }
                compared = cross_platform(model[CROSS_STATISTIC], labels, reference)
                refuted = refutation_probability(
                    compared["difference"], compared["se"], model[CROSS_STATISTIC]["ratio_se"]
                )
                cell[f"rho_{rho}"]["refutation_probability"] = round(refuted, 6)
                survive[f"rho_{rho}"] *= 1.0 - refuted
            entry[device] = cell
        out["templates"][name] = entry
    out["refutation_probability_any_pair"] = {rho: round(1.0 - kept, 6) for rho, kept in survive.items()}
    return out


def circuit_text(compiled: Any, place: dict[int, int], nqubits: int, note: str) -> str:
    lines = zd.header(nqubits) + [note]
    return "\n".join(lines + kcc.emit(compiled, place) + ["", "barrier q", "b = measure q", ""])


def batch_plan() -> list[dict[str, Any]]:
    """The eight batches: (batch, template, replicate, arm order, readout state)."""
    plan = []
    for replicate in (0, 1):
        for t, (name, *_rest) in enumerate(TEMPLATES):
            order = (True, False) if replicate == 0 else (False, True)
            plan.append(
                {
                    "batch": f"batch-{4 * replicate + t:02d}",
                    "template": name,
                    "replicate": replicate,
                    "order": order,
                    "readout": (replicate + t) % 2,
                }
            )
    return plan


def arm_file(name: str, plus: bool, replicate: int) -> str:
    return f"{name}-{'plus' if plus else 'minus'}-r{replicate}.cq"


def series(
    plan: dict[str, Any], backend: dict[str, Any], nqubits: int, shots: int, place: dict[int, int]
) -> dict[str, str]:
    region = plan["region"]
    files: dict[str, str] = {}
    texts = {"readout-0.cq": kcc.readout(nqubits, False), "readout-1.cq": kcc.readout(nqubits, True)}
    common = {
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": nqubits,
        "shots": shots,
        "region": list(region),
        "placement": {str(k): v for k, v in place.items()},
        "qrng_draw": DRAW,
        "candidates_per_template": CANDIDATES,
        "templates": {
            name: {
                "block": t["block"],
                "operand": list(BLOCKS[t["block"]].operand),
                "basis": list(BLOCKS[t["block"]].basis),
                "coset": BLOCKS[t["block"]].coset,
                "cocycle_free": t["cocycle_free"],
                "draw_index": t["draw_index"],
                "draw_indices_searched": [
                    TEMPLATES.index(next(x for x in TEMPLATES if x[0] == name)) * CANDIDATES,
                    (TEMPLATES.index(next(x for x in TEMPLATES if x[0] == name)) + 1) * CANDIDATES - 1,
                ],
                "transpiler_seed": t["transpiler_seed"],
                "cz": t["cz"],
                "roles": {k: place[v] for k, v in t["roles"].items()},
                "ideal_selector_contrast": ideal_summary(t)["selector_contrast"],
                "ideal_c": ideal_summary(t)["c"],
                "rounding_gap": round(rounding_gap(t), 6),
            }
            for name, t in plan["templates"].items()
        },
        "labels": label_table(),
        "preregistered": preregistered(),
    }
    batches = []
    for row in batch_plan():
        name = row["template"]
        t = plan["templates"][name]
        rows: list[dict[str, Any]] = []
        for plus in row["order"]:
            fname = arm_file(name, plus, row["replicate"])
            texts[fname] = circuit_text(
                t["arms"][plus],
                place,
                nqubits,
                f"// region {list(region)} template {name} seed {t['transpiler_seed']} {'plus' if plus else 'minus'}",
            )
            rows.append(
                {
                    "file": fname,
                    "kind": "arm",
                    "template": name,
                    "arm": "plus" if plus else "minus",
                    "replicate": row["replicate"],
                    "ideal": [round(float(x), 12) for x in t["ideal"][plus]],
                }
            )
        rows.append({"file": f"readout-{row['readout']}.cq", "kind": "readout"})
        for r in rows:
            r["sha256"] = hashlib.sha256(texts[r["file"]].encode()).hexdigest()
            files[f"{row['batch']}/{r['file']}"] = texts[r["file"]]
        manifest = {"schema": "qi-pathion-coset-block-cases-v1", **common, "batch": row["batch"], "circuits": rows}
        files[f"{row['batch']}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": row["batch"], "files": [r["file"] for r in rows]})
    files["cases.json"] = (
        json.dumps(
            {"schema": "qi-pathion-coset-block-series-v1", "backend": backend["identifier"], "batches": batches},
            indent=1,
        )
        + "\n"
    )
    return files


def preregistered() -> dict[str, str]:
    return {
        "resolution": f"ba and bb each read the ideal sign of at least 6 of 8 bins at {Z_RESOLVE} se",
        "pattern": f"ba and bb read opposite signs in their two differing bins at {Z_RESOLVE} se",
        "null": f"b0 selector contrast within {Z_RESOLVE} se of zero",
        "cocycle_free": f"xor_ba selector contrast below -{Z_RESOLVE} se and ba selector contrast above {Z_RESOLVE} se",
        "depth": "contraction per CZ implied by each template visibility against RHO_BAND, reported with its CZ",
        "cross_platform": f"D(y) = c_T(y) / V_T - c_I(label(y)) / V_I of ba, bb and b0 within {Z_RESOLVE} combined "
        f"standard errors on at least {CROSS_BINS_MIN} of 8 bins, against each of ibm_fez and ibm_marrakesh "
        f"(IBM_RECORDS); the Tuna ratio is the {CROSS_STATISTIC} one, the raw ratio is reported",
        "drift": f"a readout circuit moving a register qubit by more than {pcs.DRIFT_STOP} against the previous "
        "circuit of its kind (e01 on readout-0, e10 on readout-1) stops the series and fails the rule",
    }


def build() -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    tuna, qx = zd.catalogue_check()
    plan = build_plan()
    region = plan["region"]
    return {
        TUNA_SERIES: series(plan, tuna, NQUBITS, SHOTS, dict(enumerate(region))),
        QX_SERIES: series(plan, qx, QX_QUBITS, QX_SHOTS, {n: n for n in range(REGION_SIZE)}),
    }, plan


def write(directory: Path) -> None:
    built, plan = build()
    for name, files in built.items():
        for rel, text in files.items():
            path = directory / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    proposal = directory / TUNA_SERIES / "prediction.json"
    proposal.write_text(json.dumps(predictions(plan), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {TUNA_SERIES} and {QX_SERIES} under {directory}")


def check(directory: Path) -> None:
    built, plan = build()
    built[TUNA_SERIES]["prediction.json"] = json.dumps(predictions(plan), indent=1, sort_keys=True) + "\n"
    for name, files in built.items():
        root = directory / name
        present = {
            p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and not p.name.startswith(".")
        }
        if present != set(files):
            raise ValueError(f"{root}: files differ from the build: {sorted(present ^ set(files))}")
        for rel, text in files.items():
            if (root / rel).read_text(encoding="utf-8") != text:
                raise ValueError(f"{root}/{rel} differs from the build")
    print(f"{directory}: {TUNA_SERIES} and {QX_SERIES} match the build")


def select_region() -> None:
    tuna, _ = zd.catalogue_check()
    topology = tuple(sorted({tuple(sorted(edge)) for edge in tuna["topology"]}))
    table = routing_table(topology)
    primary = [i for i, t in enumerate(TEMPLATES) if t[0] in PRIMARY]
    ranking = sorted(
        {r for _, r in table},
        key=lambda r: (sum(min(c for *_, c in table[(t, r)]) for t in primary), r),
    )
    for r in ranking:
        per = {TEMPLATES[t][0]: min(c for *_, c in table[(t, r)]) for t in range(len(TEMPLATES))}
        print(r, per, sum(per[n] for n in PRIMARY))


# Analysis -------------------------------------------------------------------------------------------------


def outcome_counts(shots: list[str], roles: dict[str, int]) -> np.ndarray:
    """Counts over the logical outcome index y + 8 s read from the physical qubits of `roles`."""
    counts = np.zeros(16)
    keys = ("d0", "d1", "d2", "selector")
    for shot in shots:
        counts[sum(bit(shot, roles[k]) << v for v, k in enumerate(keys))] += 1
    return counts


def bin_contrast(plus: np.ndarray, minus: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """c(y) and its standard error from counts (conditional P(s = 0 | y) of each arm, binomial error)."""
    values = np.zeros(8)
    errors = np.zeros(8)
    for y in range(8):
        var = 0.0
        for counts, sign in ((plus, 1.0), (minus, -1.0)):
            n = counts[y] + counts[y + 8]
            p = counts[y] / n if n else 0.5
            values[y] += sign * p
            var += p * (1 - p) / max(n, 1.0)
        errors[y] = math.sqrt(var)
    return values, errors


def selector_stat(plus: np.ndarray, minus: np.ndarray) -> tuple[float, float]:
    n_plus, n_minus = plus.sum(), minus.sum()
    p, m = plus[:8].sum() / n_plus, minus[:8].sum() / n_minus
    return p - m, math.sqrt(p * (1 - p) / n_plus + m * (1 - m) / n_minus)


def corrected(counts: np.ndarray, readout: list[tuple[float, float]]) -> np.ndarray:
    return np.linalg.solve(confusion(readout), counts)


def register_assignment(shots: dict[str, list[str]]) -> dict[int, tuple[float, float]] | None:
    """(e01, e10) of every register qubit from the readout-0 and readout-1 circuits of the shot lists, None when
    the series lacks either reference."""
    zero = [v for k, v in shots.items() if k.endswith("/readout-0.cq")]
    one = [v for k, v in shots.items() if k.endswith("/readout-1.cq")]
    if not zero or not one:
        return None
    width = len(zero[0][0])
    return {
        q: (
            float(np.mean([sum(bit(s, q) for s in run) / len(run) for run in zero])),
            1.0 - float(np.mean([sum(bit(s, q) for s in run) / len(run) for run in one])),
        )
        for q in range(width)
    }


Z_EXACT = 1.0e6


def z_score(value: Any, error: Any) -> Any:
    """value / error, elementwise; a statistic with no sampling variance (an emulator bin whose counts are all one
    outcome) reads +-Z_EXACT in the direction of its sign and 0 at zero, so a record stays finite JSON."""
    value, error = np.asarray(value, dtype=float), np.asarray(error, dtype=float)
    safe = np.where(error > 0, error, 1.0)
    return np.where(error > 0, value / safe, np.sign(value) * Z_EXACT)


def control_floor(law: np.ndarray, shots: int) -> float:
    """Expected total variation distance of `shots` draws from `law`: the sum of the mean absolute deviations
    sqrt(2 p (1 - p) / (pi N)) of each outcome, halved."""
    return float(0.5 * np.sum(np.sqrt(2.0 * law * (1.0 - law) / (math.pi * shots))))


def qx_control(arms: dict[str, tuple[list[str], dict[str, int], list[float]]]) -> dict[str, Any]:
    """Each arm's observed law against its ideal law of record at CONTROL_FLOOR_FACTOR times the sampling floor.

    `arms` maps "batch/file" to (shots, roles, ideal law); the verdict is the QX dry run's preregistered pass."""
    report: dict[str, Any] = {}
    for key, (listed, roles, ideal) in sorted(arms.items()):
        counts = outcome_counts(listed, roles)
        law = np.array(ideal)
        tvd = 0.5 * float(np.abs(counts / counts.sum() - law).sum())
        floor = control_floor(law, len(listed))
        report[key] = {"tvd": tvd, "floor": floor, "ok": tvd <= CONTROL_FLOOR_FACTOR * floor}
    return {
        "arms": report,
        "factor": CONTROL_FLOOR_FACTOR,
        "pass": bool(report) and all(v["ok"] for v in report.values()),
    }


def drift_decision(drift: dict[str, Any]) -> dict[str, Any]:
    """The readout-bracket drift rule: no readout circuit moves a register qubit by more than the threshold
    against the previous circuit of its kind; a flag stops the series and fails the rule."""
    return {
        "threshold": drift["threshold"],
        "max_abs_delta": drift["max_abs_delta"],
        "flagged": drift["flagged"],
        "holds": not drift["flagged"],
    }


def evaluate(
    shots: dict[str, list[str]],
    manifest: dict[str, Any],
    executed: dict[str, str] | None = None,
    references: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Preregistered decisions from shot lists keyed by "batch/file"; manifest is any batch's cases.json.

    `references` maps an IBM device to its ibm_reference table (default: the retained measured runs)."""
    templates = manifest["templates"]
    rows: dict[str, dict[str, Any]] = {}
    ideal_c = {n: np.array(t["ideal_c"]) for n, t in templates.items()}
    assignment = register_assignment(shots)
    ibm = {device: ibm_reference(device) for device in IBM_RECORDS} if references is None else references
    for name, t in templates.items():
        roles = t["roles"]
        plus = np.zeros(16)
        minus = np.zeros(16)
        replicate_rows = []
        for key in sorted(shots):
            batch, fname = key.split("/")
            if not fname.startswith(f"{name}-"):
                continue
            counts = outcome_counts(shots[key], roles)
            if "-plus-" in fname:
                plus += counts
            else:
                minus += counts
            replicate_rows.append(key)
        c, se = bin_contrast(plus, minus)
        selector, selector_se = selector_stat(plus, minus)
        sign = np.sign(ideal_c[name])
        decided = np.abs(ideal_c[name]) > 0.5
        z_signed = z_score(c * sign, se)
        visibility = float(np.mean(c[decided] * sign[decided]))
        cz = t["cz"]
        statistics: dict[str, Any] = {"raw": contrast_statistics(plus, minus, sign)}
        corrected_visibility = float("nan")
        if assignment is not None:
            keys = ("d0", "d1", "d2", "selector")
            matrix = confusion([assignment[roles[k]] for k in keys])
            statistics["readout_corrected"] = contrast_statistics(plus, minus, sign, matrix)
            corrected_visibility = statistics["readout_corrected"]["visibility"]
        implied = corrected_visibility ** (1.0 / cz) if corrected_visibility > 0 else float("nan")
        position = "below" if implied < RHO_BAND[0] else "above" if implied > RHO_BAND[1] else "inside"
        rows[name] = {
            "files": replicate_rows,
            "c": [float(x) for x in c],
            "se": [float(x) for x in se],
            "z_signed": [float(x) for x in z_signed],
            "bins_with_ideal_sign": int(np.sum(z_signed >= Z_RESOLVE)),
            "selector_contrast": selector,
            "selector_se": selector_se,
            "visibility": visibility,
            "cz": cz,
            "visibility_readout_corrected": corrected_visibility,
            "contraction_per_cz_implied": implied,
            "against_rho_band": position if implied == implied else "not read",
            "statistics": statistics,
        }
        if name in PRIMARY:
            rows[name]["nullity_ideal"] = float(ideal_c[name].sum() / 2.0)
    ba, bb, b0, xor = rows["ba"], rows["bb"], rows["b0"], rows["xor_ba"]
    differing = [y for y in range(8) if ideal_c["ba"][y] != ideal_c["bb"][y]]
    pattern_z = [
        min(
            abs(float(z_score(ba["c"][y], ba["se"][y]))) if ba["c"][y] * ideal_c["ba"][y] > 0 else 0.0,
            abs(float(z_score(bb["c"][y], bb["se"][y]))) if bb["c"][y] * ideal_c["bb"][y] > 0 else 0.0,
        )
        for y in differing
    ]
    cross: dict[str, Any] = {"statistic": CROSS_STATISTIC, "bins_min": CROSS_BINS_MIN, "devices": {}}
    for device, reference in ibm.items():
        per_template: dict[str, Any] = {}
        for name in PRIMARY:
            stats = rows[name]["statistics"]
            if CROSS_STATISTIC not in stats:
                per_template[name] = {"read": False}
                continue
            labels = manifest["labels"][templates[name]["block"]]["ibm_data_index_of_bin"]
            tag = pkm.operand_tag(tuple(templates[name]["operand"]))
            per_template[name] = {
                "read": True,
                **{s: cross_platform(stats[s], labels, reference[tag]) for s in stats},
            }
        cross["devices"][device] = {
            "templates": per_template,
            "holds": all(
                v["read"] and v[CROSS_STATISTIC]["bins_within"] >= CROSS_BINS_MIN for v in per_template.values()
            ),
        }
    cross["holds"] = bool(cross["devices"]) and all(d["holds"] for d in cross["devices"].values())
    drift = pcs.reference_drift(
        [(key.split("/")[0], key.split("/")[1], shots[key]) for key in shots if key.split("/")[1] in pcs.READOUT_KIND],
        pcs.register_qubits(manifest),
    )
    decisions = {
        "resolution": {
            "ba": ba["bins_with_ideal_sign"] >= 6,
            "bb": bb["bins_with_ideal_sign"] >= 6,
        },
        "pattern": {"bins": differing, "z": pattern_z, "resolved": bool(all(z >= Z_RESOLVE for z in pattern_z))},
        "null": {
            "z": float(z_score(b0["selector_contrast"], b0["selector_se"])),
            "holds": bool(abs(b0["selector_contrast"]) <= Z_RESOLVE * b0["selector_se"]),
        },
        "cocycle_free": {
            "xor_z": float(z_score(xor["selector_contrast"], xor["selector_se"])),
            "ba_z": float(z_score(ba["selector_contrast"], ba["selector_se"])),
            "resolved": bool(
                xor["selector_contrast"] <= -Z_RESOLVE * xor["selector_se"]
                and ba["selector_contrast"] >= Z_RESOLVE * ba["selector_se"]
            ),
        },
        "cross_platform": cross,
        "drift": drift_decision(drift),
    }
    order: dict[str, str] | None = None
    if executed is not None:
        order = {}
        for key in sorted(executed, key=lambda k: executed[k]):
            batch, fname = key.split("/")
            if not fname.startswith("readout"):
                order[batch] = order.get(batch, "") + ("+" if "-plus-" in fname else "-")
    return {
        "templates": rows,
        "decisions": decisions,
        "references": drift,
        "stopped": not decisions["drift"]["holds"],
        "all_decisions_met": bool(
            all(decisions["resolution"].values())
            and decisions["pattern"]["resolved"]
            and decisions["null"]["holds"]
            and decisions["cocycle_free"]["resolved"]
            and decisions["cross_platform"]["holds"]
            and decisions["drift"]["holds"]
        ),
        "executed_order": order,
    }


def analyze(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Score collected batches of one series: decisions, per-block statistics, the IBM comparison and the drift rule.

    A series that holds fewer batches than the case (a stopped run) reports its drift and batch list only. A QX
    series (backend type 1) reports the control verdict a Tuna-17 submission needs."""
    shared: dict[str, Any] | None = None
    shots: dict[str, list[str]] = {}
    executed: dict[str, str] = {}
    digests: dict[str, str] = {}
    arms: dict[str, tuple[list[str], dict[str, int], list[float]]] = {}
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        series_name = pcs.series_of(run_dir)
        case_batch = None if case_root is None else case_root / series_name / f"batch-{run_dir.name[-2:]}"
        run = pcs.load_run(run_dir, case_batch)
        cases = run["cases"]
        fields = {k: v for k, v in cases.items() if k not in ("batch", "circuits")}
        if shared is None:
            shared = fields
        elif fields != shared:
            raise ValueError(f"{run_dir}/cases.json describes a different series")
        digests[cases["batch"]] = pcs.file_sha256(run_dir / "cases.json")
        for row in cases["circuits"]:
            key = f"{cases['batch']}/{row['file']}"
            shots[key] = run["shots"][row["file"]]
            executed[key] = run["jobs"][row["file"]]["queued_at"]
            if row["kind"] == "arm":
                arms[key] = (shots[key], cases["templates"][row["template"]]["roles"], row["ideal"])
    if shared is None:
        raise ValueError("an analysis needs its run directories")
    expected = sorted(row["batch"] for row in batch_plan())
    held = sorted({k.split("/")[0] for k in shots})
    emulator = shared["backend_type_id"] == 1
    claim_kind = pcs.CONTROL_KIND if emulator else "hardware acquisition"
    head: dict[str, Any] = {
        "schema": ANALYSIS_SCHEMA,
        "claim_kind": claim_kind,
        "backend": shared["backend"],
        "batch_cases_sha256": digests,
    }
    if emulator:
        head["qx_control"] = qx_control(arms)
    if held != expected:
        drift = pcs.reference_drift(
            [(k.split("/")[0], k.split("/")[1], v) for k, v in shots.items() if k.split("/")[1] in pcs.READOUT_KIND],
            pcs.register_qubits(shared),
        )
        return {
            **head,
            "complete": False,
            "batches": held,
            "references": drift,
            "stopped": bool(drift["flagged"]),
        }
    return {**head, "complete": True, **evaluate(shots, shared, executed)}


def qx_conformance(run_dir: Path, bound: float = 0.025) -> dict[str, Any]:
    """Each circuit of a local qxelarator run of the Tuna series against its ideal law of record."""
    report: dict[str, Any] = {}
    for batch_dir in sorted(run_dir.glob("batch-*")):
        cases = json.loads((batch_dir / "cases.json").read_text(encoding="utf-8"))
        for row in cases["circuits"]:
            if row["kind"] != "arm":
                continue
            template = cases["templates"][row["template"]]
            shots = json.loads((batch_dir / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
            counts = outcome_counts(shots, template["roles"])
            tvd = 0.5 * float(np.abs(counts / counts.sum() - np.array(row["ideal"])).sum())
            report[f"{batch_dir.name}/{row['file']}"] = {
                "shots": int(counts.sum()),
                "tvd": round(tvd, 6),
                "ok": tvd <= bound,
            }
    if not report:
        raise ValueError(f"{run_dir} holds no arm circuits")
    if not all(v["ok"] for v in report.values()):
        raise SystemExit(f"a circuit departs from its ideal by more than {bound}: {report}")
    return report


# Self-test --------------------------------------------------------------------------------------------------


def self_test() -> str:
    built, plan = build()
    files = built[TUNA_SERIES]
    manifest = json.loads(files["batch-00/cases.json"])
    arms = [rel for rel in files if rel.endswith(".cq") and "/readout" not in rel]
    if len(arms) != 16 or any(len(json.loads(files[f"batch-{n:02d}/cases.json"])["circuits"]) != 3 for n in range(8)):
        raise RuntimeError("the series does not hold sixteen arms in eight batches of three circuits")
    angles = [
        float(line[3:].split(")")[0]) for rel in arms for line in files[rel].splitlines() if line.startswith("Rz(")
    ]
    if not all(kcc.on_grid(a) for a in angles):
        raise RuntimeError("an emitted angle lies off the pi/36 grid")
    for key, block in BLOCKS.items():
        for plus in (False, True):
            if pcb.restriction_error(block, plus) > 1e-12:
                raise RuntimeError(f"{key}: the block law departs from the six-qubit law")
        if pcb.contrast_restriction_error(block) > 1e-12 or pcb.orientation_error(block) > 1e-12:
            raise RuntimeError(f"{key}: the contrast or the orientation phase departs")
    for t in plan["templates"].values():
        if rounding_gap(t) > 0.05:
            raise RuntimeError("grid rounding moved a law by more than 0.05")

    def device(
        retention: float,
        swap: tuple[str, str] | None = None,
        offset_b0: float = 0.0,
        drift: tuple[str, float] | None = None,
    ) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for rel in files:
            if rel.endswith("readout-0.cq") or rel.endswith("readout-1.cq"):
                out[rel] = [("0" if rel.endswith("readout-0.cq") else "1") * NQUBITS] * SHOTS
                if drift is not None and rel == drift[0]:
                    flipped = format(int(out[rel][0], 2) ^ (1 << manifest["region"][0]), f"0{NQUBITS}b")
                    moved = int(drift[1] * SHOTS)
                    out[rel] = [flipped] * moved + out[rel][moved:]
                continue
            if not rel.endswith(".cq"):
                continue
            batch, fname = rel.split("/")
            row = next(r for r in json.loads(files[f"{batch}/cases.json"])["circuits"] if r["file"] == fname)
            template = row["template"]
            plus = row["arm"] == "plus"
            source = swap[1] if swap and template == swap[0] else template
            law = plan["templates"][source]["ideal"][plus]
            law = retention * law + (1 - retention) / 16
            if template == "b0" and offset_b0 and plus:
                law = np.concatenate([law[:8] * (1 + offset_b0), law[8:] * (1 - offset_b0)])
            roles = manifest["templates"][template]["roles"]
            # Expected counts by largest remainder: the logic test carries no sampling noise and no random seed.
            expected = law / law.sum() * SHOTS
            counts = np.floor(expected).astype(int)
            for v in np.argsort(counts - expected)[: SHOTS - counts.sum()]:
                counts[v] += 1
            strings = []
            for v, count in enumerate(counts):
                value = 0
                for k, key in enumerate(("d0", "d1", "d2", "selector")):
                    value |= (v >> k & 1) << roles[key]
                strings += [format(value, f"0{NQUBITS}b")] * int(count)
            out[rel] = strings
        return out

    honest = evaluate(device(0.5), manifest)
    if not honest["all_decisions_met"]:
        raise RuntimeError(f"an honest device at retention 0.5 fails a decision: {honest['decisions']}")
    implied = honest["templates"]["ba"]["contraction_per_cz_implied"]
    if abs(implied - 0.5 ** (1 / plan["templates"]["ba"]["cz"])) > 2e-3:
        raise RuntimeError(f"a device of retention 0.5 implies {implied} per CZ")
    if not np.allclose(confusion([(0.1, 0.2)] * 4).sum(axis=0), 1.0):
        raise RuntimeError("an assignment matrix column does not sum to 1")
    free = evaluate(device(0.5, swap=("ba", "xor_ba")), manifest)
    if free["all_decisions_met"] or free["decisions"]["cocycle_free"]["resolved"]:
        raise RuntimeError("a cocycle-free circuit in the ba slot left the decisions standing")
    biased = evaluate(device(0.5, offset_b0=0.3), manifest)
    if biased["decisions"]["null"]["holds"]:
        raise RuntimeError("a b0 selector offset left the null standing")
    dead = evaluate(device(0.02), manifest)
    if dead["all_decisions_met"]:
        raise RuntimeError("a device at retention 0.02 resolves the map")
    steady = evaluate(device(0.5, drift=("batch-02/readout-0.cq", 0.019)), manifest)
    if not steady["decisions"]["drift"]["holds"]:
        raise RuntimeError("a readout bracket moving 0.019 trips the 0.02 drift stop")
    drifted = evaluate(device(0.5, drift=("batch-02/readout-0.cq", 0.05)), manifest)
    if drifted["decisions"]["drift"]["holds"] or not drifted["stopped"] or drifted["all_decisions_met"]:
        raise RuntimeError("a readout bracket moving 0.05 left the drift rule standing")
    return (
        f"qi pathion coset block: region {plan['region']}, routed CZ "
        + ", ".join(f"{n} {t['cz']}" for n, t in plan["templates"].items())
        + f"; {len(angles)} Rz on the pi/36 grid; honest device resolves every decision, a cocycle-free circuit in "
        "the ba slot, a b0 selector offset, a retention of 0.02 and a readout bracket drift of 0.05 each fail one"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--select-region", action="store_true")
    mode.add_argument("--qx-conformance", type=Path)
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.write:
        write(args.write)
    elif args.check:
        check(args.check)
    elif args.select_region:
        select_region()
    elif args.qx_conformance:
        print(json.dumps(qx_conformance(args.qx_conformance), indent=1))
    else:
        if args.out is None:
            parser.error("--analyze needs --out")
        args.out.write_text(json.dumps(analyze(args.analyze), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
