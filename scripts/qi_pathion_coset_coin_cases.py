"""Coin-arm coset-block map of the 32-dimensional Cayley-Dickson kernel map on Tuna-17, and its QX twin.

This case succeeds qi_pathion_coset_block_cases.py, whose generator and retained cases keep their bytes (the stopped
series under results/quantum_inspire/runs/*-pathion_coset_block_tuna_17-batch-* stays a drift record). The blocks,
the routing rules, the ideal laws and the IBM comparison are the predecessor's; the successor changes how a job is
spent. gororoba_quantum/pathion_coset_block.py `block_template(coin=True)` replaces the phase pi on data qubit 0 by a
CZ from a fifth, coin qubit prepared in |+>, so the state is (|0> minus-arm + |1> plus-arm) / sqrt(2) and a Z-basis
read of the coin labels each shot with the orientation it ran. One job therefore carries both orientation arms of a
block, interleaved shot by shot, at a cost of one routed CZ. Quantum Inspire runs one circuit per job (OpenAPI
`JobIn` holds one `file_id`), so the coin is the only way to put both arms in one job: reuse of the qubits by
`reset` is refused because qxelarator's reset discards phase (qx-runs.md), which no local check of such a circuit
can bear. Each arm's data marginal is uniform, because the data qubits are read after H, diagonal phases and one
CNOT; a coin misread (readout error, relaxation of |1> after the CZ) therefore moves a fraction of each arm into the
other pile and shrinks every c(y) by one common factor, which leaves c / V, the nullity estimate, every sign
decision and the null unchanged and biases only V and the depth reading low.

| template | operand | V = span | coset | aligned pairs N_b |
|---|---|---|---|---|
| ba | e1 + e18 | 19, 2, 12 | 1 | 2 |
| bb | e1 + e26 | 27, 2, 9 | 0 | 2 |
| b0 | e1 + e17 | 16, 1, 2 | 0 | 0 |
| xor_ba | ba with every SELECT sign table replaced by its cocycle-free XOR permutation | | | selector contrast -1 |

Region and routing. The admitted qubits are the complement of zd.excluded_qubits(), of q15 (P(0|1) 0.270,
tuna17-bipartite-designs.md) and of q13 (CONTEXT_EXCLUDED: its |1> misassignment doubles beside an excited q11,
tuna-17.md "Readout context"). A connected 5-qubit region is admitted when every coupler inside it has a retained
residual coupling |J| of at most J_LIMIT_HZ. Under that limit the admitted qubits hold no two disjoint 4-qubit
regions, so two blocks never share a circuit. Every template routes onto every admitted region at the candidate
transpiler seeds of its own slice of one retained ANU QRNG draw (DRAW, CANDIDATES per template, slice t holds draw
indices t * CANDIDATES to (t + 1) * CANDIDATES - 1); the series runs on the region with the fewest routed CZ summed
over ba, bb and b0 (ties: the lexicographically least region). Each template keeps the fewest-CZ candidate on that
region; among equal counts the candidate that puts the physical qubit POOR_READOUT_QUBIT (q11, the register qubit
with the least stable readout) on the selector or the coin comes first, then the lowest draw index. Every rotation
rounds to the nearest multiple of pi/36, and the ideal law of record is the Statevector of the exact rounded routed
circuit read through the final layout, over 32 outcomes (index y + 8 s + 16 c with c the coin).

Series. Batch 00 to 02 each hold one primary template as [readout-0, template, readout-1] at SHOTS; batch 03 holds
xor_ba alone at XOR_SHOTS. A readout circuit excites the five register qubits and measures all 17, so each primary
is corrected with the assignment its own batch measured and a drift between batches is a stratum, never a stop. The
QX series holds the four templates in one batch at QX_SHOTS.

Preregistered decisions (Z_RESOLVE standard errors; raw counts, the coin read as the arm):
- resolution: ba and bb each read the ideal sign of at least 6 of their 8 bins;
- pattern: ba and bb differ in two bins of c(y), and the two blocks read opposite signs there;
- null: the b0 selector contrast lies within Z_RESOLVE standard errors of zero (it also tests that the coin adds no
  arm-dependent offset); its difference from the coin-free value of the stopped series (STOPPED_B0_SELECTOR) is
  reported, so a nonzero reading separates a device offset from a coin-induced one;
- cocycle-free: the xor_ba selector contrast is negative at Z_RESOLVE and the ba selector contrast positive;
- depth, reported: the contraction per CZ implied by each template's readout-corrected visibility against RHO_BAND,
  with the coin read fraction beside it; the correction removes the readout part of the coin factor and the relaxation
  part is unidentified, so the reading is a lower bound;
- cross-platform: the readout-corrected ratio c(y) / V of ba, bb and b0 differs from the measured IBM ratio of the
  same algebra labels (qi_pathion_coset_block_cases.IBM_RECORDS) by at most Z_RESOLVE combined standard errors on at
  least CROSS_BINS_MIN of 8 bins against each device;
- drift: recorded, never a stop. The analysis reports the change of every register qubit between successive
  brackets and recomputes the cross-platform statistic of each primary under every bracket of the series.

Usage: "$PYTHON" scripts/qi_pathion_coset_coin_cases.py
       (--write DIR | --check DIR | --select-region | --qx-conformance RUN_DIR | --analyze RUN_DIR... --out FILE
        | --self-test)
Bit strings put qubit 0 at the rightmost character.
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
import qi_pathion_coset_block_cases as blk  # noqa: E402
import qi_pathion_coset_block_series as pcs  # noqa: E402
import qi_pathion_coset_coin_series as coin_series  # noqa: E402
import qi_zero_divisor_cases as zd  # noqa: E402

import parallel  # noqa: E402
import pathion_coset_block as pcb  # noqa: E402
import pathion_kernel_map as pkm  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

TUNA_SERIES = coin_series.TUNA_SERIES
QX_SERIES = coin_series.QX_SERIES
NQUBITS = 17
SHOTS = 65536
XOR_SHOTS = 16384
QX_QUBITS = 10
QX_SHOTS = 2048
GRID = kcc.GRID
BASIS = kcc.BASIS
Z_RESOLVE = blk.Z_RESOLVE
ANALYSIS_SCHEMA = "qi-pathion-coset-coin-analysis-v1"
# The ANU QRNG draw whose 64 values seed every routing candidate; it belongs to this case's manifest.
DRAW = "docs/evidence/anu_qrng/draw-2026-11-06T225841Z.json"
CANDIDATES = 16
EXTRA_EXCLUDED = (15,)
CONTEXT_EXCLUDED = (13,)
POOR_READOUT_QUBIT = 11
J_LIMIT_HZ = blk.J_LIMIT_HZ
REGION_SIZE = 5
RHO_BAND = blk.RHO_BAND
CROSS_BINS_MIN = blk.CROSS_BINS_MIN
CROSS_STATISTIC = blk.CROSS_STATISTIC
IBM_RECORDS = blk.IBM_RECORDS
# Readout of the register qubits at the calibration the stopped series measured: its four readout circuits.
STOPPED_RUN = "results/quantum_inspire/runs/2026-11-06T221626Z-pathion_coset_block_tuna_17"
READOUT_RUNS = tuple(ROOT / f"{STOPPED_RUN}-batch-{batch:02d}" for batch in range(4))
# The stopped series' files the forecast and the null reference read, pinned like IBM_RECORDS: a missing or changed
# file refuses the build.
STOPPED_FILES = {
    "batch-00/raw/readout-0.cq.json": "8175eed671fa54916a314c5abe054c40d22b71cde0563010516c8248735932c2",
    "batch-01/raw/readout-1.cq.json": "627c8a41f49df74201f15340056b0b89d4e9b9114dbd1092314dccc47f0aae61",
    "batch-02/raw/readout-0.cq.json": "b38ad99ab891ee31076e6c0d8ff34823ab3d598d50a3a3561ba7d3154d535336",
    "batch-03/raw/readout-1.cq.json": "85da50f2a8cafb97bf887fac757f917aea667a93b73938d4a284d7b773f7c76e",
    "batch-02/raw/b0-plus-r0.cq.json": "0ecd4ed9d7b0fb9e2a2ea113353579a9e96fd910847f7ea786b02cb8220aefc4",
    "batch-02/raw/b0-minus-r0.cq.json": "0fb5ec77c458c72146b83c23a406fd0c9f96373d20238f0bacee59bc44b99761",
    "batch-02/cases.json": "a6cdf65c28b76d06633661f5d17e8e22107b6235abed2d677611dffff4f037d2",
}
# b0 selector contrast and its standard error in the stopped series (no coin; one replicate at 16384 shots per arm,
# STOPPED_RUN batch-02, recomputed from the pinned files by verify_stopped_files): the null's reference when the coin
# series reads a nonzero value, which separates a device offset from a coin-induced one.
STOPPED_B0_SELECTOR = (0.016663, 0.005523)
KEYS = ("d0", "d1", "d2", "selector", "coin")
BLOCKS = blk.BLOCKS
TEMPLATES = blk.TEMPLATES
PRIMARY = blk.PRIMARY
NOUT = 32
HALF = 16
BATCH_TEMPLATES = (("batch-00", "ba"), ("batch-01", "bb"), ("batch-02", "b0"), ("batch-03", "xor_ba"))
bit = pcs.bit


def template_circuit(name: str) -> Any:
    _, key, free = next(t for t in TEMPLATES if t[0] == name)
    return pcb.block_template(BLOCKS[key], cocycle_free=free, measure=False, coin=True)


def draw_values() -> list[int]:
    values = read_record(DRAW)["values"]
    if len(values) != CANDIDATES * len(TEMPLATES):
        raise ValueError(f"{DRAW} holds {len(values)} values, not {CANDIDATES * len(TEMPLATES)}")
    return [int(v) for v in values]


def candidate_seeds(index: int) -> list[tuple[int, int]]:
    """(draw index, transpiler seed value) of the candidates of template `index`."""
    values = draw_values()
    return [(n, values[n]) for n in range(index * CANDIDATES, (index + 1) * CANDIDATES)]


def admitted_regions(topology: tuple[tuple[int, int], ...]) -> list[tuple[int, ...]]:
    """Connected REGION_SIZE-qubit regions off the excluded qubits whose inner couplers all satisfy J_LIMIT_HZ."""
    analysis = json.loads(zd.COUPLER_ZZ_ANALYSIS.read_text(encoding="utf-8"))
    coupling = {tuple(sorted(row["edge"])): abs(row["j_hz"]) for row in analysis["edges"]}
    out = []
    for region in zd.connected_regions(topology, REGION_SIZE):
        inside = {tuple(sorted(e)) for e in topology if e[0] in region and e[1] in region}
        if set(region) & set(EXTRA_EXCLUDED + CONTEXT_EXCLUDED) or any(coupling[e] > J_LIMIT_HZ for e in inside):
            continue
        out.append(region)
    return out


def disjoint_pair_count(topology: tuple[tuple[int, int], ...], size: int) -> int:
    """Disjoint pairs of admitted `size`-qubit regions under the same exclusions and coupler limit."""
    analysis = json.loads(zd.COUPLER_ZZ_ANALYSIS.read_text(encoding="utf-8"))
    coupling = {tuple(sorted(row["edge"])): abs(row["j_hz"]) for row in analysis["edges"]}
    regions = []
    for region in zd.connected_regions(topology, size):
        inside = {tuple(sorted(e)) for e in topology if e[0] in region and e[1] in region}
        if not set(region) & set(EXTRA_EXCLUDED + CONTEXT_EXCLUDED) and all(coupling[e] <= J_LIMIT_HZ for e in inside):
            regions.append(set(region))
    return sum(1 for i, a in enumerate(regions) for b in regions[i + 1 :] if not a & b)


def local_coupling(topology: tuple[tuple[int, int], ...], region: tuple[int, ...]) -> Any:
    from qiskit.transpiler import CouplingMap

    local = {q: n for n, q in enumerate(region)}
    edges = [[local[a], local[b]] for a, b in topology if a in local and b in local]
    return CouplingMap(edges + [[b, a] for a, b in edges])


def compile_template(topology: tuple[tuple[int, int], ...], index: int, region: tuple[int, ...], seed: int) -> Any:
    from qiskit import transpile

    return transpile(
        template_circuit(TEMPLATES[index][0]),
        coupling_map=local_coupling(topology, region),
        basis_gates=BASIS,
        optimization_level=2,
        seed_transpiler=seed,
    )


class RouteScore:
    """(routed CZ, 0 when the poor-readout qubit holds the selector or the coin else 1) of one candidate; a
    module-level callable for the pool."""

    def __init__(self, topology: tuple[tuple[int, int], ...]) -> None:
        self.topology = topology

    def __call__(self, item: tuple[int, tuple[int, ...], int]) -> tuple[int, int]:
        index, region, seed = item
        compiled = compile_template(self.topology, index, region, seed)
        final = compiled.layout.final_index_layout()
        poor = {region[final[3]], region[final[4]]}
        return int(compiled.count_ops().get("cz", 0)), 0 if POOR_READOUT_QUBIT in poor else 1


@cache
def routing_table(
    topology: tuple[tuple[int, int], ...],
) -> dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int, int]]]:
    """(template index, region) -> [(draw index, seed value, routed CZ, poor-readout flag)] over every region."""
    regions = admitted_regions(topology)
    items = [(t, region, seed) for t in range(len(TEMPLATES)) for region in regions for _, seed in candidate_seeds(t)]
    scores = parallel.ordered_map(RouteScore(topology), items)
    table: dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int, int]]] = {}
    position = 0
    for t in range(len(TEMPLATES)):
        for region in regions:
            row = []
            for n, seed in candidate_seeds(t):
                row.append((n, seed, *scores[position]))
                position += 1
            table[(t, region)] = row
    return table


def best_candidate(row: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    return min(row, key=lambda r: (r[2], r[3], r[0]))


def choose_region(table: dict[tuple[int, tuple[int, ...]], list[tuple[int, int, int, int]]]) -> tuple[int, ...]:
    regions = sorted({region for _, region in table})
    primary = [i for i, t in enumerate(TEMPLATES) if t[0] in PRIMARY]
    return min(regions, key=lambda r: (sum(best_candidate(table[(t, r)])[2] for t in primary), r))


def skeleton(circuit: Any) -> list[tuple[str, tuple[int, ...]]]:
    return blk.skeleton(circuit)


def coin_ideal(compiled: Any) -> np.ndarray:
    """Outcome law of the rounded routed circuit over the logical bits (d0, d1, d2, selector, coin), index
    y + 8 s + 16 c."""
    return blk.ideal_of_record(blk.round_to_grid(compiled))


def arm_laws(ideal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(plus, minus) law over the 16 outcomes y + 8 s from the joint law (each arm holds half the shots)."""
    return 2.0 * ideal[HALF:], 2.0 * ideal[:HALF]


def logical_arm_laws(name: str) -> dict[bool, Any]:
    _, key, free = next(t for t in TEMPLATES if t[0] == name)
    plus, minus = pcb.coin_arm_laws(pcb.block_template(BLOCKS[key], cocycle_free=free, measure=False, coin=True))
    return {True: plus, False: minus}


def stopped_path(name: str) -> Path:
    batch, _, rest = name.partition("/")
    return ROOT / f"{STOPPED_RUN}-{batch}" / rest


@cache
def verify_stopped_files() -> None:
    """Refuse the build unless every pinned stopped-series file is present with its digest and the b0 reference
    constant equals the selector contrast those files give."""
    for name, digest in STOPPED_FILES.items():
        path = stopped_path(name)
        if not path.exists():
            raise ValueError(f"{path} is missing: the stopped series' run directories must accompany this case")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"{path} differs from the retained record its digest pins")
    cases = json.loads(stopped_path("batch-02/cases.json").read_text(encoding="utf-8"))
    roles = cases["templates"]["b0"]["roles"]
    plus, minus = (
        blk.outcome_counts(
            json.loads(stopped_path(f"batch-02/raw/b0-{arm}-r0.cq.json").read_text(encoding="utf-8")), roles
        )
        for arm in ("plus", "minus")
    )
    selector, se = blk.selector_stat(plus, minus)
    if abs(selector - STOPPED_B0_SELECTOR[0]) > 1e-6 or abs(se - STOPPED_B0_SELECTOR[1]) > 1e-6:
        raise ValueError(f"STOPPED_B0_SELECTOR differs from the pinned files: {selector} +- {se}")


@cache
def retained_readout(region: tuple[int, ...]) -> dict[int, tuple[float, float]]:
    """(e01, e10) of each region qubit at the calibration of the stopped series: mean P(1 | prepared 0) over its
    readout-0 circuits and 1 - mean P(1 | prepared 1) over its readout-1 circuits (all 17 qubits excited)."""
    verify_stopped_files()
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


confusion = blk.confusion
z_score = blk.z_score


def coin_counts(shots: list[str], roles: dict[str, int]) -> np.ndarray:
    """Counts over the logical outcome index y + 8 s + 16 c read from the physical qubits of `roles`."""
    counts = np.zeros(NOUT)
    for shot in shots:
        counts[sum(bit(shot, roles[k]) << v for v, k in enumerate(KEYS))] += 1
    return counts


def coin_outputs(counts: np.ndarray, sign: np.ndarray, matrix: np.ndarray | None) -> np.ndarray:
    """c(y) of the 8 bins, c / V, V and N_hat from the 32 counts of one coin job, the plus pile the coin = 1 half.

    `matrix`, when given, is the joint assignment matrix over the 5 bits that the counts are corrected with
    before they split by coin."""
    x = counts if matrix is None else np.linalg.solve(matrix, counts)
    plus, minus = x[HALF:], x[:HALF]
    c = pcb.output_contrast(plus / plus.sum(), minus / minus.sum())
    v = float(np.mean(c * sign))
    return np.concatenate([c, c / v, [v, c.sum() / 2.0 / v]])


def coin_statistics(counts: np.ndarray, sign: np.ndarray, matrix: np.ndarray | None = None) -> dict[str, Any]:
    """c(y), c / V, V and N_hat of a coin job with delta-method standard errors.

    The 32 counts are one multinomial with covariance N (diag p - p p^T); the Jacobian is a central difference of
    one count, which is deterministic and needs no random draw."""
    x = counts.astype(float)
    base = coin_outputs(x, sign, matrix)
    jac = np.empty((base.size, x.size))
    for i in range(x.size):
        up, down = x.copy(), x.copy()
        up[i] += 1.0
        down[i] -= 1.0
        jac[:, i] = (coin_outputs(up, sign, matrix) - coin_outputs(down, sign, matrix)) / 2.0
    p = x / x.sum()
    cov = x.sum() * (np.diag(p) - np.outer(p, p))
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


def piles(counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return counts[HALF:], counts[:HALF]


def model_law(ideal: np.ndarray, cz: int, rho: float, readout: list[tuple[float, float]]) -> np.ndarray:
    """Joint law of a device that contracts the 32-outcome law toward uniform by rho^cz, then misassigns each of the
    five bits with the retained single-qubit assignment (hypothesis-level)."""
    retention = rho**cz
    return confusion(readout) @ (retention * ideal + (1 - retention) / ideal.size)


def forecast(ideal: np.ndarray, cz: int, rho: float, readout: list[tuple[float, float]], shots: int) -> dict[str, Any]:
    """Raw contrasts and their expected z of one coin job at `shots` shots under the contraction model."""
    law = model_law(ideal, cz, rho, readout)
    counts = law * shots
    plus, minus = piles(counts)
    selector, selector_se = blk.selector_stat(plus, minus)
    c, se = blk.bin_contrast(plus, minus)
    plus_ideal, minus_ideal = arm_laws(ideal)
    ideal_c = pcb.output_contrast(plus_ideal, minus_ideal)
    sign = np.sign(ideal_c)
    decided = np.abs(ideal_c) > 0.5
    return {
        "retention": rho**cz,
        "selector_contrast": float(selector),
        "selector_se": float(selector_se),
        "c": [round(float(x), 6) for x in c],
        "se_per_bin": [round(float(x), 6) for x in se],
        "z_per_bin": [round(float(abs(a) / b), 2) for a, b in zip(c, se, strict=True)],
        "visibility": float(np.mean(c[decided] * sign[decided])),
    }


def ideal_summary(ideal: np.ndarray) -> dict[str, Any]:
    plus, minus = arm_laws(ideal)
    return {
        "selector_contrast": round(float(pcb.selector_contrast(plus, minus)), 6),
        "c": [round(float(x), 6) for x in pcb.output_contrast(plus, minus)],
    }


def build_plan() -> dict[str, Any]:
    tuna, _ = zd.catalogue_check()
    topology = tuple(sorted({tuple(sorted(edge)) for edge in tuna["topology"]}))
    table = routing_table(topology)
    region = choose_region(table)
    templates: dict[str, dict[str, Any]] = {}
    for t, (name, key, free) in enumerate(TEMPLATES):
        n, seed, cz, _poor = best_candidate(table[(t, region)])
        compiled = blk.round_to_grid(compile_template(topology, t, region, seed))
        final = compiled.layout.final_index_layout()
        templates[name] = {
            "block": key,
            "cocycle_free": free,
            "draw_index": n,
            "transpiler_seed": seed,
            "cz": cz,
            "roles": {k: int(final[v]) for v, k in enumerate(KEYS)},
            "circuit": compiled,
            "ideal": blk.ideal_of_record(compiled),
            "unrounded": logical_arm_laws(name),
        }
    return {"region": region, "table": table, "templates": templates, "topology": topology}


def rounding_gap(template: dict[str, Any]) -> float:
    plus, minus = arm_laws(template["ideal"])
    return float(
        max(np.abs(plus - template["unrounded"][True]).max(), np.abs(minus - template["unrounded"][False]).max())
    )


def marginal_gap(name: str) -> float:
    """Largest departure of either arm's data marginal from uniform: the property that makes a coin misread a
    common factor of every c(y)."""
    out = 0.0
    for law in logical_arm_laws(name).values():
        marginal = law[:8] + law[8:]
        out = max(out, float(np.abs(marginal - 1.0 / 8.0).max()))
    return out


def label_table() -> dict[str, Any]:
    return blk.label_table()


def preregistered() -> dict[str, str]:
    return {
        "resolution": f"ba and bb each read the ideal sign of at least 6 of 8 bins at {Z_RESOLVE} se",
        "pattern": f"ba and bb read opposite signs in their two differing bins at {Z_RESOLVE} se",
        "null": f"b0 selector contrast within {Z_RESOLVE} se of zero; its difference from the stopped series' "
        f"coin-free {STOPPED_B0_SELECTOR[0]} +- {STOPPED_B0_SELECTOR[1]} is reported",
        "cocycle_free": f"xor_ba selector contrast below -{Z_RESOLVE} se and ba selector contrast above {Z_RESOLVE} se",
        "depth": "contraction per CZ implied by each corrected template visibility against RHO_BAND, reported with "
        "its CZ and the coin read fraction; the correction removes the readout part of the coin factor, the "
        "relaxation part is unidentified, so depth is a lower bound",
        "cross_platform": f"D(y) = c_T(y) / V_T - c_I(label(y)) / V_I of ba, bb and b0 within {Z_RESOLVE} combined "
        f"standard errors on at least {CROSS_BINS_MIN} of 8 bins, against each of ibm_fez and ibm_marrakesh "
        f"(IBM_RECORDS); the Tuna ratio is the {CROSS_STATISTIC} one with the assignment of its own batch, the raw "
        "ratio is reported",
        "drift": "recorded, never a stop: per-batch assignment of every register qubit, the change between "
        f"successive brackets (flag above {pcs.DRIFT_STOP}), and the cross-platform statistic of each primary "
        "under every bracket of the series",
    }


def predictions(plan: dict[str, Any]) -> dict[str, Any]:
    readout = retained_readout(plan["region"])
    out: dict[str, Any] = {
        "model": "contraction of the 32-outcome law toward uniform by rho^cz, then the retained single-qubit "
        "assignment; hypothesis-level",
        "rho_band": list(RHO_BAND),
        "readout_runs": [p.relative_to(ROOT).as_posix() for p in READOUT_RUNS],
        "readout_e01_e10": {str(q): [round(a, 4), round(b, 4)] for q, (a, b) in readout.items()},
        "templates": {},
    }
    for name, t in plan["templates"].items():
        per_bit = [readout[plan["region"][t["roles"][k]]] for k in KEYS]
        shots = XOR_SHOTS if name == "xor_ba" else SHOTS
        out["templates"][name] = {f"rho_{rho}": forecast(t["ideal"], t["cz"], rho, per_bit, shots) for rho in RHO_BAND}
    out["ibm_measured"] = {device: blk.ibm_summary(device) for device in IBM_RECORDS}
    out["cross_platform"] = cross_platform_prediction(plan, readout)
    return out


def cross_platform_prediction(plan: dict[str, Any], readout: dict[int, tuple[float, float]]) -> dict[str, Any]:
    """The preregistered D(y) of each primary template against each measured IBM device under the contraction
    model, with the number of bins inside the combined error and the chance that a device obeying the model fails
    the rule."""
    out: dict[str, Any] = {
        "rule": preregistered()["cross_platform"],
        "statistic": CROSS_STATISTIC,
        "templates": {},
    }
    survive = {f"rho_{rho}": 1.0 for rho in RHO_BAND}
    for name in PRIMARY:
        t = plan["templates"][name]
        labels = pcb.output_labels(BLOCKS[t["block"]])
        per_bit = [readout[plan["region"][t["roles"][k]]] for k in KEYS]
        matrix = confusion(per_bit)
        plus_ideal, minus_ideal = arm_laws(t["ideal"])
        sign = np.sign(pcb.output_contrast(plus_ideal, minus_ideal))
        entry: dict[str, Any] = {"labels": labels}
        for device in IBM_RECORDS:
            reference = blk.ibm_reference(device)[blk.operand_tag(t["block"])]
            cell: dict[str, Any] = {}
            for rho in RHO_BAND:
                counts = model_law(t["ideal"], t["cz"], rho, per_bit) * SHOTS
                model = {
                    "raw": coin_statistics(counts, sign),
                    "readout_corrected": coin_statistics(counts, sign, matrix),
                }
                cell[f"rho_{rho}"] = {
                    statistic: {
                        key: value if key in ("labels", "ibm_coset", "bins_within") else blk.rounded(value)
                        for key, value in blk.cross_platform(model[statistic], labels, reference).items()
                    }
                    for statistic in model
                }
                compared = blk.cross_platform(model[CROSS_STATISTIC], labels, reference)
                refuted = blk.refutation_probability(
                    compared["difference"], compared["se"], model[CROSS_STATISTIC]["ratio_se"]
                )
                cell[f"rho_{rho}"]["refutation_probability"] = round(refuted, 6)
                survive[f"rho_{rho}"] *= 1.0 - refuted
            entry[device] = cell
        out["templates"][name] = entry
    out["refutation_probability_any_pair"] = {rho: round(1.0 - kept, 6) for rho, kept in survive.items()}
    return out


# Circuits and cases -------------------------------------------------------------------------------------------


def circuit_text(compiled: Any, place: dict[int, int], nqubits: int, note: str) -> str:
    lines = zd.header(nqubits) + [note]
    return "\n".join(lines + kcc.emit(compiled, place) + ["", "barrier q", "b = measure q", ""])


def readout_text(nqubits: int, excited: bool, qubits: list[int]) -> str:
    """Every register qubit prepared in |1> (readout-1) or left in |0> (readout-0), all qubits measured."""
    lines = zd.header(nqubits)
    if excited:
        lines += [f"X q[{q}]" for q in qubits] + [""]
    return "\n".join(lines + ["barrier q", "b = measure q", ""])


def batch_rows(series_name: str) -> list[dict[str, Any]]:
    """The batches of a series: name, templates and whether a readout pair brackets the data circuit."""
    if series_name == QX_SERIES:
        return [{"batch": "batch-00", "templates": [t for _, t in BATCH_TEMPLATES], "readout": False}]
    return [{"batch": b, "templates": [t], "readout": t in PRIMARY} for b, t in BATCH_TEMPLATES]


def series(
    plan: dict[str, Any],
    backend: dict[str, Any],
    series_name: str,
    nqubits: int,
    place: dict[int, int],
) -> dict[str, str]:
    region = plan["region"]
    register = [place[n] for n in range(len(region))]
    files: dict[str, str] = {}
    common = {
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": nqubits,
        "region": list(region),
        "placement": {str(k): v for k, v in place.items()},
        "register": register,
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
                "ideal_selector_contrast": ideal_summary(t["ideal"])["selector_contrast"],
                "ideal_c": ideal_summary(t["ideal"])["c"],
                "rounding_gap": round(rounding_gap(t), 6),
            }
            for name, t in plan["templates"].items()
        },
        "labels": label_table(),
        "preregistered": preregistered(),
    }
    batches = []
    for row in batch_rows(series_name):
        shots = QX_SHOTS if series_name == QX_SERIES else XOR_SHOTS if row["templates"] == ["xor_ba"] else SHOTS
        circuits: list[dict[str, Any]] = []
        texts: dict[str, str] = {}
        if row["readout"]:
            texts["readout-0.cq"] = readout_text(nqubits, False, register)
            circuits.append({"file": "readout-0.cq", "kind": "readout"})
        for name in row["templates"]:
            t = plan["templates"][name]
            fname = f"{name}.cq"
            texts[fname] = circuit_text(
                t["circuit"],
                place,
                nqubits,
                f"// region {list(region)} template {name} seed {t['transpiler_seed']} coin",
            )
            circuits.append(
                {
                    "file": fname,
                    "kind": "data",
                    "template": name,
                    "ideal": [round(float(x), 12) for x in t["ideal"]],
                }
            )
        if row["readout"]:
            texts["readout-1.cq"] = readout_text(nqubits, True, register)
            circuits.append({"file": "readout-1.cq", "kind": "readout"})
        for r in circuits:
            r["sha256"] = hashlib.sha256(texts[r["file"]].encode()).hexdigest()
            files[f"{row['batch']}/{r['file']}"] = texts[r["file"]]
        manifest = {
            "schema": "qi-pathion-coset-coin-cases-v1",
            **common,
            "shots": shots,
            "batch": row["batch"],
            "circuits": circuits,
        }
        files[f"{row['batch']}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": row["batch"], "files": [r["file"] for r in circuits]})
    files["cases.json"] = (
        json.dumps(
            {"schema": "qi-pathion-coset-coin-series-v1", "backend": backend["identifier"], "batches": batches},
            indent=1,
        )
        + "\n"
    )
    return files


def build() -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    tuna, qx = zd.catalogue_check()
    plan = build_plan()
    region = plan["region"]
    return {
        TUNA_SERIES: series(plan, tuna, TUNA_SERIES, NQUBITS, dict(enumerate(region))),
        QX_SERIES: series(plan, qx, QX_SERIES, QX_QUBITS, {n: n for n in range(REGION_SIZE)}),
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
    for r in sorted({r for _, r in table}, key=lambda r: (sum(best_candidate(table[(t, r)])[2] for t in primary), r)):
        per = {TEMPLATES[t][0]: best_candidate(table[(t, r)])[2] for t in range(len(TEMPLATES))}
        print(r, per, sum(per[n] for n in PRIMARY))
    print(
        "disjoint admitted pairs: "
        f"4-qubit regions {disjoint_pair_count(topology, 4)}, 5-qubit regions {disjoint_pair_count(topology, 5)}"
    )


# Analysis -------------------------------------------------------------------------------------------------------


def batch_assignment(
    shots: dict[str, list[str]], batch: str, qubits: list[int]
) -> dict[int, tuple[float, float]] | None:
    """(e01, e10) of the register qubits from the readout pair of one batch, None when the batch holds no pair."""
    zero = shots.get(f"{batch}/readout-0.cq")
    one = shots.get(f"{batch}/readout-1.cq")
    if zero is None or one is None:
        return None
    return {q: (sum(bit(s, q) for s in zero) / len(zero), 1.0 - sum(bit(s, q) for s in one) / len(one)) for q in qubits}


def control_arms(
    arms: dict[str, tuple[list[str], dict[str, int], list[float]]],
) -> dict[str, Any]:
    """Each data circuit's observed 32-outcome law against its ideal law of record at the sampling floor."""
    report: dict[str, Any] = {}
    for key, (listed, roles, ideal) in sorted(arms.items()):
        counts = coin_counts(listed, roles)
        law = np.array(ideal)
        tvd = 0.5 * float(np.abs(counts / counts.sum() - law).sum())
        floor = blk.control_floor(law, len(listed))
        report[key] = {"tvd": tvd, "floor": floor, "ok": tvd <= blk.CONTROL_FLOOR_FACTOR * floor}
    return {
        "arms": report,
        "factor": blk.CONTROL_FLOOR_FACTOR,
        "pass": bool(report) and all(v["ok"] for v in report.values()),
    }


def template_file(shots: dict[str, list[str]], name: str) -> str:
    keys = [k for k in shots if k.endswith(f"/{name}.cq")]
    if len(keys) != 1:
        raise ValueError(f"the series holds {len(keys)} circuits of template {name}")
    return keys[0]


def template_row(
    name: str, t: dict[str, Any], counts: np.ndarray, matrix: np.ndarray | None, ideal_c: np.ndarray
) -> dict[str, Any]:
    plus, minus = piles(counts)
    c, se = blk.bin_contrast(plus, minus)
    selector, selector_se = blk.selector_stat(plus, minus)
    sign = np.sign(ideal_c)
    decided = np.abs(ideal_c) > 0.5
    z_signed = z_score(c * sign, se)
    statistics: dict[str, Any] = {"raw": coin_statistics(counts, sign)}
    corrected_visibility: float | None = None
    implied: float | None = None
    position = "not read"
    coin_read = float(counts[HALF:].sum() / counts.sum())
    if matrix is not None:
        statistics["readout_corrected"] = coin_statistics(counts, sign, matrix)
        corrected_visibility = statistics["readout_corrected"]["visibility"]
        if corrected_visibility > 0:
            implied = corrected_visibility ** (1.0 / t["cz"])
            position = "below" if implied < RHO_BAND[0] else "above" if implied > RHO_BAND[1] else "inside"
    cz = t["cz"]
    row = {
        "c": [float(x) for x in c],
        "se": [float(x) for x in se],
        "z_signed": [float(x) for x in z_signed],
        "bins_with_ideal_sign": int(np.sum(z_signed >= Z_RESOLVE)),
        "selector_contrast": selector,
        "selector_se": selector_se,
        "visibility": float(np.mean(c[decided] * sign[decided])),
        "cz": cz,
        "coin_read_fraction": coin_read,
        "visibility_readout_corrected": corrected_visibility,
        "contraction_per_cz_implied": implied,
        "against_rho_band": position,
        "statistics": statistics,
    }
    if name in PRIMARY:
        row["nullity_ideal"] = float(ideal_c.sum() / 2.0)
    return row


def cross_decision(
    rows: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
    ibm: dict[str, dict[str, Any]],
    statistic: Any,
) -> dict[str, Any]:
    """The cross-platform rule over the primary templates; `statistic(name)` supplies a template's ratio table or
    None when it cannot be read."""
    templates = manifest["templates"]
    devices: dict[str, Any] = {}
    for device, reference in ibm.items():
        per_template: dict[str, Any] = {}
        for name in PRIMARY:
            stats = statistic(name)
            if stats is None:
                per_template[name] = {"read": False}
                continue
            labels = manifest["labels"][templates[name]["block"]]["ibm_data_index_of_bin"]
            tag = pkm.operand_tag(tuple(templates[name]["operand"]))
            per_template[name] = {
                "read": True,
                **{s: blk.cross_platform(v, labels, reference[tag]) for s, v in stats.items()},
            }
        devices[device] = {
            "templates": per_template,
            "holds": all(
                v["read"] and v[CROSS_STATISTIC]["bins_within"] >= CROSS_BINS_MIN for v in per_template.values()
            ),
        }
    return {
        "statistic": CROSS_STATISTIC,
        "bins_min": CROSS_BINS_MIN,
        "devices": devices,
        "holds": bool(devices) and all(d["holds"] for d in devices.values()),
    }


def evaluate(
    shots: dict[str, list[str]],
    manifest: dict[str, Any],
    executed: dict[str, str] | None = None,
    references: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Preregistered decisions from shot lists keyed by "batch/file"; manifest is any batch's cases.json.

    Each primary template is corrected with the assignment of its own batch. The drift between brackets is a
    covariate: its report and the cross-platform statistic under every bracket of the series enter the output, and
    no drift value stops a decision."""
    templates = manifest["templates"]
    register = [int(q) for q in manifest["register"]]
    ibm = {device: blk.ibm_reference(device) for device in IBM_RECORDS} if references is None else references
    ideal_c = {n: np.array(t["ideal_c"]) for n, t in templates.items()}
    brackets = {
        batch: asg
        for batch in sorted({k.split("/")[0] for k in shots})
        if (asg := batch_assignment(shots, batch, register)) is not None
    }
    counts: dict[str, np.ndarray] = {}
    owner: dict[str, str] = {}
    rows: dict[str, dict[str, Any]] = {}
    for name, t in templates.items():
        key = template_file(shots, name)
        owner[name] = key.split("/")[0]
        counts[name] = coin_counts(shots[key], t["roles"])

    def matrix_of(name: str, batch: str) -> np.ndarray | None:
        asg = brackets.get(batch)
        if asg is None:
            return None
        return confusion([asg[templates[name]["roles"][k]] for k in KEYS])

    for name, t in templates.items():
        rows[name] = template_row(name, t, counts[name], matrix_of(name, owner[name]), ideal_c[name])
    ba, bb, b0, xor = rows["ba"], rows["bb"], rows["b0"], rows["xor_ba"]
    differing = [y for y in range(8) if np.sign(ideal_c["ba"][y]) != np.sign(ideal_c["bb"][y])]
    pattern_z = [
        min(
            abs(float(z_score(ba["c"][y], ba["se"][y]))) if ba["c"][y] * ideal_c["ba"][y] > 0 else 0.0,
            abs(float(z_score(bb["c"][y], bb["se"][y]))) if bb["c"][y] * ideal_c["bb"][y] > 0 else 0.0,
        )
        for y in differing
    ]
    cross = cross_decision(
        rows, manifest, ibm, lambda n: rows[n]["statistics"] if CROSS_STATISTIC in rows[n]["statistics"] else None
    )
    drift = pcs.reference_drift(
        [(k.split("/")[0], k.split("/")[1], v) for k, v in shots.items() if k.split("/")[1] in pcs.READOUT_KIND],
        register,
    )
    sensitivity: dict[str, Any] = {}
    for batch in brackets:
        alternative = {n: coin_statistics(counts[n], np.sign(ideal_c[n]), matrix_of(n, batch)) for n in PRIMARY}
        under = cross_decision(
            rows, manifest, ibm, lambda n, alternative=alternative: {CROSS_STATISTIC: alternative[n]}
        )
        sensitivity[batch] = {
            "holds": under["holds"],
            "bins_within": {
                device: {n: cell[CROSS_STATISTIC]["bins_within"] for n, cell in entry["templates"].items()}
                for device, entry in under["devices"].items()
            },
            "max_ratio_shift_over_se": {
                n: float(
                    np.max(
                        np.abs(
                            np.array(alternative[n]["ratio"])
                            - np.array(rows[n]["statistics"][CROSS_STATISTIC]["ratio"])
                        )
                        / np.array(rows[n]["statistics"][CROSS_STATISTIC]["ratio_se"])
                    )
                )
                for n in PRIMARY
            },
        }
    decisions = {
        "resolution": {"ba": ba["bins_with_ideal_sign"] >= 6, "bb": bb["bins_with_ideal_sign"] >= 6},
        "pattern": {"bins": differing, "z": pattern_z, "resolved": bool(all(z >= Z_RESOLVE for z in pattern_z))},
        "null": {
            "z": float(z_score(b0["selector_contrast"], b0["selector_se"])),
            "holds": bool(abs(b0["selector_contrast"]) <= Z_RESOLVE * b0["selector_se"]),
            "stopped_series_reference": {
                "selector_contrast": STOPPED_B0_SELECTOR[0],
                "se": STOPPED_B0_SELECTOR[1],
                "z_of_difference": float(
                    z_score(
                        b0["selector_contrast"] - STOPPED_B0_SELECTOR[0],
                        math.hypot(b0["selector_se"], STOPPED_B0_SELECTOR[1]),
                    )
                ),
            },
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
    }
    order: dict[str, str] | None = None
    if executed is not None:
        order = {}
        for key in sorted(executed, key=lambda k: executed[k]):
            batch, fname = key.split("/")
            order[batch] = order.get(batch, "") + fname.removesuffix(".cq") + " "
    return {
        "templates": rows,
        "decisions": decisions,
        "drift_covariate": {
            "references": drift,
            "brackets": {b: {str(q): list(v) for q, v in asg.items()} for b, asg in brackets.items()},
            "cross_platform_under_each_bracket": sensitivity,
            "stable": all(s["holds"] for s in sensitivity.values()) if sensitivity else False,
        },
        "all_decisions_met": bool(
            all(decisions["resolution"].values())
            and decisions["pattern"]["resolved"]
            and decisions["null"]["holds"]
            and decisions["cocycle_free"]["resolved"]
            and decisions["cross_platform"]["holds"]
        ),
        "executed_order": order,
    }


def analyze(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Score collected batches of one series: decisions, per-template statistics, the IBM comparison and the drift
    covariate. A series that holds fewer batches than the case reports its batch list and drift covariate only; a
    QX series reports the control verdict a Tuna-17 submission needs."""
    shared: dict[str, Any] | None = None
    shots: dict[str, list[str]] = {}
    executed: dict[str, str] = {}
    digests: dict[str, str] = {}
    arms: dict[str, tuple[list[str], dict[str, int], list[float]]] = {}
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        series_name = coin_series.series_of(run_dir)
        case_batch = None if case_root is None else case_root / series_name / f"batch-{run_dir.name[-2:]}"
        run = pcs.load_run(run_dir, case_batch)
        cases = run["cases"]
        fields = {k: v for k, v in cases.items() if k not in ("batch", "circuits", "shots")}
        if shared is None:
            shared = fields
        elif fields != shared:
            raise ValueError(f"{run_dir}/cases.json describes a different series")
        digests[cases["batch"]] = pcs.file_sha256(run_dir / "cases.json")
        for row in cases["circuits"]:
            key = f"{cases['batch']}/{row['file']}"
            shots[key] = run["shots"][row["file"]]
            executed[key] = run["jobs"][row["file"]]["queued_at"]
            if row["kind"] == "data":
                arms[key] = (shots[key], cases["templates"][row["template"]]["roles"], row["ideal"])
    if shared is None:
        raise ValueError("an analysis needs its run directories")
    emulator = shared["backend_type_id"] == 1
    expected = sorted(r["batch"] for r in batch_rows(QX_SERIES if emulator else TUNA_SERIES))
    held = sorted({k.split("/")[0] for k in shots})
    head: dict[str, Any] = {
        "schema": ANALYSIS_SCHEMA,
        "claim_kind": pcs.CONTROL_KIND if emulator else "hardware acquisition",
        "backend": shared["backend"],
        "batch_cases_sha256": digests,
    }
    if emulator:
        head["qx_control"] = control_arms(arms)
    if held != expected:
        drift = pcs.reference_drift(
            [(k.split("/")[0], k.split("/")[1], v) for k, v in shots.items() if k.split("/")[1] in pcs.READOUT_KIND],
            [int(q) for q in shared["register"]],
        )
        return {**head, "complete": False, "batches": held, "drift_covariate": {"references": drift}}
    return {**head, "complete": True, **evaluate(shots, shared, executed)}


def qx_conformance(run_dir: Path, bound: float = 0.025) -> dict[str, Any]:
    """Each data circuit of a local qxelarator run of the Tuna series against its ideal law of record."""
    report: dict[str, Any] = {}
    for batch_dir in sorted(run_dir.glob("batch-*")):
        cases = json.loads((batch_dir / "cases.json").read_text(encoding="utf-8"))
        for row in cases["circuits"]:
            if row["kind"] != "data":
                continue
            template = cases["templates"][row["template"]]
            listed = json.loads((batch_dir / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
            counts = coin_counts(listed, template["roles"])
            tvd = 0.5 * float(np.abs(counts / counts.sum() - np.array(row["ideal"])).sum())
            report[f"{batch_dir.name}/{row['file']}"] = {
                "shots": int(counts.sum()),
                "tvd": round(tvd, 6),
                "ok": tvd <= bound,
            }
    if not report:
        raise ValueError(f"{run_dir} holds no data circuits")
    if not all(v["ok"] for v in report.values()):
        raise SystemExit(f"a circuit departs from its ideal by more than {bound}: {report}")
    return report


# Self-test --------------------------------------------------------------------------------------------------


def largest_remainder(law: np.ndarray, total: int) -> np.ndarray:
    """Expected counts of `law` by largest remainder: the logic test carries no sampling noise and no random seed."""
    expected = law / law.sum() * total
    counts = np.floor(expected).astype(int)
    for v in np.argsort(counts - expected)[: total - counts.sum()]:
        counts[v] += 1
    return counts


def place_counts(counts: np.ndarray, keys: tuple[str, ...], roles: dict[str, int], width: int) -> list[str]:
    strings: list[str] = []
    for v, count in enumerate(counts):
        value = 0
        for k, key in enumerate(keys):
            value |= (v >> k & 1) << roles[key]
        strings += [format(value, f"0{width}b")] * int(count)
    return strings


def simulated_series(
    files: dict[str, str],
    plan: dict[str, Any],
    manifest: dict[str, Any],
    retention: float,
    assignment: dict[str, dict[int, tuple[float, float]]] | None = None,
    swap: tuple[str, str] | None = None,
    offset_b0: float = 0.0,
) -> dict[str, list[str]]:
    """Shot lists of a device that contracts every law by `retention` and misassigns the register qubits with the
    assignment of the batch (default none), as expected counts."""
    out: dict[str, list[str]] = {}
    register = [int(q) for q in manifest["register"]]
    for rel in files:
        if not rel.endswith(".cq"):
            continue
        batch, fname = rel.split("/")
        cases = json.loads(files[f"{batch}/cases.json"])
        total = cases["shots"]
        asg = (assignment or {}).get(batch, {q: (0.0, 0.0) for q in register})
        if fname.startswith("readout"):
            excited = fname == "readout-1.cq"
            law = np.ones(1)
            for q in reversed(register):
                e01, e10 = asg[q]
                p1 = 1.0 - e10 if excited else e01
                law = np.kron(law, np.array([1.0 - p1, p1]))
            counts = largest_remainder(law, total)
            roles = {f"q{n}": q for n, q in enumerate(register)}
            out[rel] = place_counts(counts, tuple(roles), roles, NQUBITS)
            continue
        template = next(r for r in cases["circuits"] if r["file"] == fname)["template"]
        source = swap[1] if swap and template == swap[0] else template
        ideal = plan["templates"][source]["ideal"]
        law = retention * ideal + (1 - retention) / ideal.size
        if template == "b0" and offset_b0:
            plus_half = np.arange(NOUT) >= HALF
            selector0 = (np.arange(NOUT) % 16) < 8
            law = law * np.where(plus_half & selector0, 1 + offset_b0, np.where(plus_half, 1 - offset_b0, 1.0))
        roles = cases["templates"][template]["roles"]
        matrix = confusion([asg[roles[k]] for k in KEYS])
        out[rel] = place_counts(largest_remainder(matrix @ law, total), KEYS, roles, NQUBITS)
    return out


def self_test() -> str:
    built, plan = build()
    files = built[TUNA_SERIES]
    manifest = json.loads(files["batch-00/cases.json"])
    circuits = [rel for rel in files if rel.endswith(".cq") and "/readout" not in rel]
    if len(circuits) != 4 or len(files["batch-00/cases.json"]) == 0:
        raise RuntimeError("the series does not hold four coin circuits")
    jobs = sum(len(json.loads(files[f"batch-{n:02d}/cases.json"])["circuits"]) for n in range(4))
    if jobs != 10 or any(len(json.loads(files[f"batch-{n:02d}/cases.json"])["circuits"]) > 3 for n in range(4)):
        raise RuntimeError("the series does not hold ten jobs in batches of at most three")
    angles = [
        float(line[3:].split(")")[0]) for rel in circuits for line in files[rel].splitlines() if line.startswith("Rz(")
    ]
    if not all(kcc.on_grid(a) for a in angles):
        raise RuntimeError("an emitted angle lies off the pi/36 grid")
    for key, block in BLOCKS.items():
        for plus in (False, True):
            if pcb.restriction_error(block, plus) > 1e-12:
                raise RuntimeError(f"{key}: the block law departs from the six-qubit law")
    for name, t in plan["templates"].items():
        if rounding_gap(t) > 0.05:
            raise RuntimeError("grid rounding moved a law by more than 0.05")
        if marginal_gap(name) > 1e-12:
            raise RuntimeError(f"{name}: an arm's data marginal is not uniform")
        coin_plus, coin_minus = pcb.coin_arm_laws(
            pcb.block_template(BLOCKS[t["block"]], cocycle_free=t["cocycle_free"], measure=False, coin=True)
        )
        reference = {
            p: pcb.block_law(pcb.block_circuit(BLOCKS[t["block"]], p, cocycle_free=t["cocycle_free"], measure=False))
            for p in (False, True)
        }
        if max(np.abs(coin_plus - reference[True]).max(), np.abs(coin_minus - reference[False]).max()) > 1e-12:
            raise RuntimeError(f"{name}: the coin arms differ from the phase arms")
    assignment = {
        batch: {int(q): (0.02 + 0.01 * n, 0.04 + 0.01 * n) for n, q in enumerate(manifest["register"])}
        for batch in ("batch-00", "batch-01", "batch-02")
    }
    honest = evaluate(simulated_series(files, plan, manifest, 0.5, assignment), manifest)
    if not honest["all_decisions_met"]:
        raise RuntimeError(f"an honest device at retention 0.5 fails a decision: {honest['decisions']}")
    implied = honest["templates"]["ba"]["contraction_per_cz_implied"]
    if implied is None or abs(implied - 0.5 ** (1 / plan["templates"]["ba"]["cz"])) > 2e-3:
        raise RuntimeError(f"a device of retention 0.5 implies {implied} per CZ")
    free = evaluate(simulated_series(files, plan, manifest, 0.5, assignment, swap=("ba", "xor_ba")), manifest)
    if free["all_decisions_met"] or free["decisions"]["cocycle_free"]["resolved"]:
        raise RuntimeError("a cocycle-free circuit in the ba slot left the decisions standing")
    biased = evaluate(simulated_series(files, plan, manifest, 0.5, assignment, offset_b0=0.3), manifest)
    if biased["decisions"]["null"]["holds"]:
        raise RuntimeError("a b0 selector offset left the null standing")
    dead = evaluate(simulated_series(files, plan, manifest, 0.02, assignment), manifest)
    if dead["all_decisions_met"]:
        raise RuntimeError("a device at retention 0.02 resolves the map")
    poor = manifest["templates"]["bb"]["roles"]["d2"]
    moved = {
        **assignment,
        "batch-01": {q: (e01, e10 + (0.17 if q == poor else 0.0)) for q, (e01, e10) in assignment["batch-01"].items()},
    }
    drifted = evaluate(simulated_series(files, plan, manifest, 0.5, moved), manifest)
    cover = drifted["drift_covariate"]
    if not drifted["all_decisions_met"] or not cover["references"]["flagged"] or cover["stable"]:
        raise RuntimeError("a bracket that moves one qubit by 0.17 stops a decision or escapes the covariate")
    return (
        f"qi pathion coset coin: region {plan['region']}, routed CZ "
        + ", ".join(f"{n} {t['cz']}" for n, t in plan["templates"].items())
        + f"; {len(angles)} Rz on the pi/36 grid; {jobs} jobs in 4 batches; honest device resolves every decision, "
        "a cocycle-free circuit in the ba slot, a b0 selector offset and a retention of 0.02 each fail one, and a "
        "0.17 assignment move between brackets is recorded and corrected without a stop"
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
