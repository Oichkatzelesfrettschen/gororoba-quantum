"""Ghost error-scale sweep on exact branching density matrices: every replica's law at every (c, r) grid point.

Each retained run's members are rebuilt as scripts/ghost_run.py prepares
them, under the calibration snapshot in force when each member's PUB began.
Every replica becomes a gororoba_quantum/branch_dm.py program under that
snapshot's factor-1 noise model; replicas of one dynamic key share a
template export, and one batch carries the key's replicas, the ten CZ
factors of scripts/ghost_error_scale.py and every live branch. A key fixes
the physical qubits, so each group's noise model is built in a pool worker
from the snapshot restricted to those qubits (GroupBuilder), which carries
the full snapshot's channels on them. The CZ
factor c enters only through the CZ steps, jax_bridge.CzChannel at
min(c * error, CZ_CAP) as ghost_error_scale.scaled reports it; the readout
factor r enters only classically, through ghost_error_scale.flip in the
mid-circuit weights and the terminal readout, so one evolution per
(replica, c, branch) serves all five r. The result is each replica's exact
law over its classical register at all fifty points.

Two estimators per replica and point, kept apart:

- ``tvd``: the exact TV distance from the model law to the retained hardware
  distribution, which carries hardware shot noise only.
- ``sampled_tvd``: the TV distance from a sampled model distribution at the
  member's shots, with common random numbers. Per run a numpy Generator
  seeded with (SEED, run-name digest) draws one set of uniforms per replica
  at its shot count, in member and replica order, before any mapping; every
  grid point maps the same uniforms through its law's inverse CDF (float64,
  index clamped to the last outcome), so differences between points come
  from the model alone, as in the Aer sweep's common seed.

``--engine numpy`` evolves in complex128 numpy with the structure batches
spread over parallel.ordered_map; ``--engine torch`` evolves on
``--device cuda|cpu`` in ``--dtype complex64|complex128`` (branch_dm.py
documents both contraction ``--form`` choices and ``--no-fuse``), staying
on the device from the plan upload to the law tensor. Each run records the
seconds of its phases: prepare (records and snapshot files), export
(restricted noise models, templates and plans in the pool, upload to the
device), evolve (laws ready on the device) and sample (distances on the
host). The output's ``warmup_seconds`` is the pool start, plus the CUDA
context and cuBLAS start on cuda, which no phase includes.
``--profile-only RUN`` runs the four phases on one run and prints the
seconds as JSON without writing a file.

``--compare-parts FILE`` reads a ghost_error_scale part (Aer, sampled) and
reports, per run, the sampled-estimator mean at every point minus the Aer
part's, how many points fall within ghost_error_scale.tolerance, and
whether the minimizing (c, r) of either estimator matches the Aer one; with
``--result OUT`` it compares a retained sweep output without sweeping.

``--replay FILE`` recomputes the reduced case, run REDUCED_RUN at the grid
corners on numpy complex128, and requires FILE to equal its deterministic
fields byte for byte; ``--write`` writes FILE instead.

``--self-test`` runs the contracts on numpy (torch only for (g)). Each
noise model except (h)'s full one is built on the snapshot restricted to
the case circuit's active qubits, as the sweep builds them; the circuits
are real part-a replicas except the toys of (a) and (d).

(a) Readout and feed-forward, analytic: q0 in |1>, P(record 0 | 1) = 0.3,
    ``if_else`` on c0 flips q1; the law is {00: 1 - p, 11: p} with
    p = 1 - flip(0.3, r) at r in (0.5, 1, 1.5).
(b) A static replica's laws equal jax_bridge.export, evolve_numpy and
    probabilities at every readout factor within 1e-12.
(c) Static replicas' final diagonals equal Aer's save_density_matrix
    diagonals in place of the terminal measurements within 1e-9, one with
    a delay and a reset.
(d) Dynamic replicas (mid-circuit measurement, reset, ``if_else``) at (1, 1)
    and (12, 3), and a toy whose ``if_else`` body holds a delay and noisy sx
    gates on a qubit with T1 = T2 = 10 us, against Aer density-matrix counts
    at DYNAMIC_SHOTS shots with seed SEED. The test is the likelihood-ratio
    G test of the counts against the exact law: cells whose expected count
    is below 5 pool into one cell, a cell of zero exact probability with a
    count fails outright, and the statistic has (cells - 1) degrees of
    freedom; each case passes at p >= 1e-4.
(e) The rescaled CZ superoperator of every coupler the cases drive equals
    the channel of a freshly built scaled noise model at CONTRACT_FACTORS,
    which reach the zero-depolarizing branch, the interior and both caps,
    and the rescaled plan's law equals the law of a fresh export under each
    scaled model within 1e-10.
(f) Every law sums to 1 within 1e-12 and is nonnegative within float64
    epsilon.
(g) torch complex128 on the CPU equals numpy within 1e-12 (reported as not
    run when torch is not importable).
(h) Laws from the restricted snapshot equal laws from the full 156-qubit
    snapshot within 1e-12 at CZ factors 1 and 12 and every readout factor,
    on a replica with a delay and a reset and one with feed-forward.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_error_scale  # noqa: E402
import ghost_run  # noqa: E402
import jax_bridge_sweep  # noqa: E402
import numpy as np  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import SuperOp  # noqa: E402
from qiskit_aer.noise import NoiseModel, ReadoutError  # noqa: E402

import branch_dm  # noqa: E402
import calibration_snapshot  # noqa: E402
import jax_bridge  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402

SCHEMA = "ghost-error-scale-branching-v1"
SEED = ghost_error_scale.SEED
CZ_FACTORS = ghost_error_scale.CZ_FACTORS
READOUT_FACTORS = ghost_error_scale.READOUT_FACTORS
REDUCED_RUN = "results/live/2026-10-11T152922.787095Z"
CORNER_CZ = (CZ_FACTORS[0], CZ_FACTORS[-1])
CORNER_READOUT = (READOUT_FACTORS[0], READOUT_FACTORS[-1])
PART_A_RUNS = ("results/live/2026-10-11T152922.787095Z", "results/live/2026-10-12T055624.091217Z")
DYNAMIC_CASES = (
    ("results/live/2026-10-11T152922.787095Z", "hybrid_shor_N15_a2_null"),
    ("results/live/2026-10-11T152922.787095Z", "folded_qpe_null"),
)
STATIC_CASES = (
    ("results/live/2026-10-12T055624.091217Z", "qpe_coherent_s0"),
    ("results/live/2026-10-12T055624.091217Z", "qpe_delay_s0"),
)
RESTRICTION_CASES = (
    ("results/live/2026-10-12T055624.091217Z", "qpe_delay_s0"),
    ("results/live/2026-10-12T055624.091217Z", "qpe_archived_s0"),
)
RESTRICTION_FACTORS = (1.0, 12.0)
RESTRICTION_TOLERANCE = 1e-12
DYNAMIC_POINTS = ((1.0, 1.0), (12.0, 3.0))
DYNAMIC_SHOTS = 200_000
G_TEST_FLOOR = 1e-4
G_POOL = 5.0
CONTRACT_FACTORS = jax_bridge_sweep.CONTRACT_FACTORS
JAX_TOLERANCE = 1e-12
AER_DIAGONAL_TOLERANCE = 1e-9
RESCALE_TOLERANCE = 1e-10
SUM_TOLERANCE = 1e-12
TORCH_TOLERANCE = 1e-12
require = ghost_run.require


def flip(value: float, factor: float) -> float:
    return ghost_error_scale.flip(value, factor)


def run_digest(run_name: str) -> int:
    return int(hashlib.sha256(run_name.encode()).hexdigest()[:8], 16)


@dataclass
class SnapshotState:
    """One snapshot's factor-1 noise model, superoperator cache, dynamic-key templates and CZ superoperators."""

    snapshot: dict[str, Any]
    noise: Any
    cache: dict[int, np.ndarray] = field(default_factory=dict)
    templates: dict[tuple[Any, ...], branch_dm.DynamicProgram] = field(default_factory=dict)
    channels: dict[tuple[int, ...], tuple[jax_bridge.CzChannel, float | None]] = field(default_factory=dict)
    superops: dict[tuple[tuple[int, ...], float], np.ndarray] = field(default_factory=dict)

    @classmethod
    def build(cls, snapshot: dict[str, Any]) -> SnapshotState:
        return cls(snapshot=snapshot, noise=calibration_snapshot.noise_model(snapshot)[1])

    def skeleton(self, replica: QuantumCircuit) -> tuple[tuple[Any, ...], branch_dm.DynamicProgram]:
        key = branch_dm.dynamic_key(replica)
        if key not in self.templates:
            self.templates[key] = branch_dm.template(replica, self.noise, self.cache)
        return key, self.templates[key]

    def cz_superop(self, qargs: tuple[int, ...], factor: float) -> np.ndarray:
        if (qargs, factor) not in self.superops:
            if qargs not in self.channels:
                self.channels[qargs] = jax_bridge.cz_channel(self.snapshot, qargs)
            channel, reported = self.channels[qargs]
            self.superops[(qargs, factor)] = branch_dm.cz_superop(channel, jax_bridge_sweep.cz_error(reported, factor))
        return self.superops[(qargs, factor)]

    def plan(self, replicas: Sequence[QuantumCircuit], factors: Sequence[float], fuse: bool) -> branch_dm.Plan:
        """The plan of replicas sharing one dynamic key at the CZ factors."""
        _, skeleton = self.skeleton(replicas[0])
        couplers = sorted({qargs for _, qargs in skeleton.cz})
        stacks = {q: np.stack([self.cz_superop(q, c) for c in factors]) for q in couplers}
        return branch_dm.build_plan(skeleton, replicas, stacks, len(factors), fuse)


def make_backend(engine: str, device: str, dtype: str) -> branch_dm.Backend:
    if engine == "numpy":
        require(device == "cpu" and dtype == "complex128", "the numpy engine runs complex128 on the cpu")
        return branch_dm.NumpyBackend()
    return branch_dm.TorchBackend(device, dtype)


@dataclass
class NumpyEvolver:
    """evolve() of one plan on numpy complex128, for the process pool; returns the law and the branch counts."""

    readout_factors: tuple[float, ...]

    def __call__(self, plan: branch_dm.Plan) -> tuple[np.ndarray, dict[str, int]]:
        backend = branch_dm.NumpyBackend()
        return branch_dm.evolve(branch_dm.stage(plan, backend), backend, self.readout_factors, flip)


@dataclass
class Group:
    """Replicas of one dynamic key under one snapshot: their labels and plan."""

    relative: str
    labels: list[str]
    plan: branch_dm.Plan


def restricted(circuit: QuantumCircuit) -> tuple[QuantumCircuit, list[int]]:
    """circuit without barriers on its active qubits, renumbered in ascending physical order (restrict_circuit)."""
    body = circuit.copy_empty_like()
    for instruction in circuit.data:
        if instruction.operation.name not in branch_dm.SKIPPED:
            body.append(instruction.operation, instruction.qubits, instruction.clbits, copy=False)
    return snapshot_laws.restrict_circuit(body)


@dataclass
class GroupBuilder:
    """The plan of one group from its restricted snapshot and circuits, for the process pool.

    NoiseModel.from_backend builds every gate, reset and readout channel
    from that qubit's or coupler's own Target entries, and the relaxation
    pass from that qubit's T1, T2 and the dt, so the snapshot restricted to
    the group's active qubits (snapshot_laws.restrict) carries the same
    channels as the full one; the self-test's (h) compares them. A worker
    then builds a noise model of n qubits in place of 156.
    """

    cz_factors: tuple[float, ...]
    fuse: bool

    def __call__(self, item: tuple[dict[str, Any], list[QuantumCircuit]]) -> branch_dm.Plan:
        snapshot, circuits = item
        return SnapshotState.build(snapshot).plan(circuits, self.cz_factors, self.fuse)


def build_groups(
    prepared: dict[str, Any],
    members: list[str],
    snapshots: dict[str, dict[str, Any]],
    cz_factors: Sequence[float],
    fuse: bool,
) -> list[Group]:
    """Every dynamic-key group of the run's replicas, in first-appearance order, with plans built in the pool."""
    execution = prepared["execution"]
    keyed: dict[tuple[str, tuple[Any, ...]], list[tuple[str, QuantumCircuit]]] = {}
    for m in members:
        for k, replica in enumerate(prepared["replicas"][m][1]):
            keyed.setdefault((execution[m], branch_dm.dynamic_key(replica)), []).append((f"{m}#{k}", replica))
    items = []
    for (relative, _), rows in keyed.items():
        circuits = []
        for _, replica in rows:
            circuit, qubits = restricted(replica)
            circuits.append(circuit)
        items.append((snapshot_laws.restrict(snapshots[relative], qubits), circuits))
    plans = parallel.ordered_map(GroupBuilder(tuple(cz_factors), fuse), items, min_items=2)
    return [
        Group(relative, [label for label, _ in rows], plan)
        for ((relative, _), rows), plan in zip(keyed.items(), plans, strict=True)
    ]


def inverse_cdf_tv(law: np.ndarray, uniforms: np.ndarray, measured: np.ndarray) -> np.ndarray:
    """Per row of law (points, outcomes): TV distance of the uniforms' inverse-CDF sample to measured."""
    cdf = np.cumsum(np.clip(law, 0.0, None), axis=1)
    cdf /= cdf[:, -1:]
    out = np.empty(len(law))
    for j in range(len(law)):
        index = np.minimum(np.searchsorted(cdf[j], uniforms, side="right"), law.shape[1] - 1)
        counts = np.bincount(index, minlength=law.shape[1]) / len(uniforms)
        out[j] = 0.5 * np.abs(counts - measured).sum()
    return out


def torch_distances(backend: branch_dm.TorchBackend, law: Any, uniforms: np.ndarray, measured: np.ndarray) -> Any:
    """inverse_cdf_tv and the exact TV distance on the device; law is (points, outcomes) float64."""
    torch = backend.torch
    target = torch.as_tensor(measured, device=backend.device)
    exact = 0.5 * (law - target).abs().sum(dim=1)
    cdf = torch.cumsum(law.clamp(min=0.0), dim=1)
    cdf = cdf / cdf[:, -1:]
    points, outcomes = law.shape
    u = torch.as_tensor(uniforms, device=backend.device).expand(points, -1).contiguous()
    index = torch.searchsorted(cdf, u, right=True).clamp(max=outcomes - 1)
    counts = torch.zeros((points, outcomes), dtype=torch.float64, device=backend.device)
    counts.scatter_add_(1, index, torch.ones_like(u))
    sampled = 0.5 * (counts / len(uniforms) - target).abs().sum(dim=1)
    return torch.stack([exact, sampled])


def sweep_run(
    run_name: str,
    index: dict[str, Any],
    engine: str,
    device: str,
    dtype: str,
    form: str = "local",
    fuse: bool = True,
    cz_factors: Sequence[float] = CZ_FACTORS,
    readout_factors: Sequence[float] = READOUT_FACTORS,
) -> dict[str, Any]:
    """The run's exact and sampled TV distances at every (c, r) point, its branch counts and phase seconds."""
    seconds: dict[str, float] = {}
    clock = time.perf_counter()
    prepared = ghost_run.prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "skipped": prepared["skipped"]}
    execution = prepared["execution"]
    members = [m for m in prepared["members"] if m in execution]
    snapshots = {
        relative: json.loads((ROOT / relative).read_text(encoding="utf-8"))
        for relative in sorted({execution[m] for m in members})
    }
    seconds["prepare"] = time.perf_counter() - clock

    clock = time.perf_counter()
    backend = make_backend(engine, device, dtype)
    groups = build_groups(prepared, members, snapshots, cz_factors, fuse)
    staged = [branch_dm.stage(group.plan, backend, form) for group in groups] if engine == "torch" else []
    backend.synchronize()
    seconds["export"] = time.perf_counter() - clock

    clock = time.perf_counter()
    factors = tuple(readout_factors)
    if engine == "numpy":
        evolved = parallel.ordered_map(NumpyEvolver(factors), [group.plan for group in groups], min_items=2)
    else:
        evolved = [branch_dm.evolve(s, backend, factors, flip) for s in staged]
    backend.synchronize()
    seconds["evolve"] = time.perf_counter() - clock

    clock = time.perf_counter()
    grid = [(c, r) for c in cz_factors for r in readout_factors]
    labels = [f"{m}#{k}" for m in members for k in range(len(prepared["replicas"][m][1]))]
    rng = np.random.default_rng([SEED, run_digest(run_name)])
    uniforms = {label: rng.random(prepared["shots"][label.rsplit("#", 1)[0]]) for label in labels}
    rows: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    branches: dict[str, dict[str, int]] = {}
    plans = []
    for group, (law, stats) in zip(groups, evolved, strict=True):
        plans.append(
            {
                "replicas": group.labels,
                "qubits": group.plan.n,
                "exported_ops": group.plan.exported_ops,
                "steps": stats["ops"],
                "splits": stats["splits"],
                "live_branches": stats["live"],
            }
        )
        flat = law.reshape((law.shape[0], len(grid), law.shape[-1]))
        for g, label in enumerate(group.labels):
            m, k = label.rsplit("#", 1)
            measured = prepared["measured"][m][int(k)]
            branches[label] = {"splits": stats["splits"], "children": stats["children"], "live": stats["live"]}
            if engine == "numpy":
                exact = 0.5 * np.abs(flat[g] - measured).sum(axis=1)
                rows[label] = (exact, inverse_cdf_tv(flat[g], uniforms[label], measured))
            else:
                assert isinstance(backend, branch_dm.TorchBackend)
                pair = backend.host(torch_distances(backend, flat[g], uniforms[label], measured))
                rows[label] = (pair[0], pair[1])
    points: list[dict[str, Any]] = [{"cz": c, "readout": r, "tvd": {}, "sampled_tvd": {}} for c, r in grid]
    for m in members:
        own = [label for label in labels if label.rsplit("#", 1)[0] == m]
        for j, point in enumerate(points):
            point["tvd"][m] = [round(float(rows[label][0][j]), 6) for label in own]
            point["sampled_tvd"][m] = [round(float(rows[label][1][j]), 6) for label in own]
    means = ghost_error_scale.grid_means(points, members)
    sampled_means = [round(float(np.mean([v for m in members for v in p["sampled_tvd"][m]])), 6) for p in points]
    seconds["sample"] = time.perf_counter() - clock
    best, sampled_best = int(np.argmin(means)), int(np.argmin(sampled_means))
    print(
        json.dumps(
            {
                "run": run_name,
                "best": list(grid[best]),
                "mean_tvd": means[best],
                "sampled_best": list(grid[sampled_best]),
            }
        ),
        flush=True,
    )
    return {
        "run": run_name,
        "backend": prepared["backend"],
        "members": members,
        "member_shots": {m: prepared["shots"][m] for m in members},
        "execution_snapshot": {m: execution[m] for m in members},
        "structures": plans,
        "branches": branches,
        "mean_tvd": means,
        "sampled_mean_tvd": sampled_means,
        "best": {"cz": grid[best][0], "readout": grid[best][1], "mean_tvd": means[best]},
        "sampled_best": {
            "cz": grid[sampled_best][0],
            "readout": grid[sampled_best][1],
            "mean_tvd": sampled_means[sampled_best],
        },
        "points": points,
        "seconds": {k: round(v, 3) for k, v in seconds.items()},
    }


def versions(engine: str) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    names = ["numpy", "qiskit", "qiskit-aer"] + (["torch"] if engine == "torch" else [])
    for name in names:
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = None
    return out


def header(engine: str, device: str, dtype: str, form: str, fuse: bool) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "engine": engine,
        "device": device,
        "dtype": dtype,
        "form": form,
        "fuse": fuse,
        "seed": SEED,
        "prune_floor": branch_dm.PRUNE_FLOOR,
        "grid": [[c, r] for c in CZ_FACTORS for r in READOUT_FACTORS],
        "scaled": {
            "cz": "jax_bridge.CzChannel at min(c * error, cz_cap)",
            "readout": "ghost_error_scale.flip on e01 and e10",
            "cz_cap": ghost_error_scale.CZ_CAP,
            "readout_cap": ghost_error_scale.FLIP_CAP,
        },
        "versions": versions(engine),
        "runs": [],
    }


def compare_parts(result: dict[str, Any], part_path: Path) -> dict[str, Any]:
    """Per run in both files: sampled-estimator mean minus the Aer part's mean, tolerance count and best points."""
    part = json.loads(part_path.read_text(encoding="utf-8"))
    aer = {run["run"]: run for run in part["runs"] if "skipped" not in run}
    grid = [tuple(p) for p in part["grid"]]
    rows = []
    for run in result["runs"]:
        if "skipped" in run or run["run"] not in aer:
            continue
        reference = aer[run["run"]]
        require(reference["members"] == run["members"], f"{run['run']}: members differ from the Aer part")
        tolerance = ghost_error_scale.tolerance(reference, reference["members"])
        delta = [round(s - a, 6) for s, a in zip(run["sampled_mean_tvd"], reference["mean_tvd"], strict=True)]
        best_aer = grid[int(np.argmin(reference["mean_tvd"]))]
        best_sampled = grid[int(np.argmin(run["sampled_mean_tvd"]))]
        best_exact = grid[int(np.argmin(run["mean_tvd"]))]
        rows.append(
            {
                "run": run["run"],
                "tolerance": round(tolerance, 6),
                "sampled_minus_aer": delta,
                "max_abs_sampled_minus_aer": max(abs(v) for v in delta),
                "mean_sampled_minus_aer": round(float(np.mean(delta)), 6),
                "points_within_tolerance": sum(abs(v) <= tolerance for v in delta),
                "points": len(delta),
                "aer_best": list(best_aer),
                "sampled_best": list(best_sampled),
                "exact_best": list(best_exact),
                "sampled_best_matches_aer": best_sampled == best_aer,
                "exact_best_matches_aer": best_exact == best_aer,
                "aer_mean_at_sampled_best": reference["mean_tvd"][grid.index(best_sampled)],
                "aer_best_mean": min(reference["mean_tvd"]),
            }
        )
    return {"part": part_path.as_posix(), "runs": rows}


def replay_document(index: dict[str, Any]) -> str:
    """The reduced case's deterministic fields: REDUCED_RUN at the grid corners on numpy complex128."""
    run = sweep_run(
        REDUCED_RUN,
        index,
        "numpy",
        "cpu",
        "complex128",
        cz_factors=CORNER_CZ,
        readout_factors=CORNER_READOUT,
    )
    deterministic = {key: value for key, value in run.items() if key != "seconds"}
    document = {
        "schema": SCHEMA + "-reduced",
        "engine": "numpy",
        "dtype": "complex128",
        "seed": SEED,
        "cz_factors": list(CORNER_CZ),
        "readout_factors": list(CORNER_READOUT),
        "run": deterministic,
    }
    return json.dumps(document, indent=1) + "\n"


# Self-test.


def g_test(law: np.ndarray, counts: np.ndarray) -> dict[str, Any]:
    """Likelihood-ratio G test of counts against law; see the module docstring for the pooling rule."""
    from scipy.stats import chi2

    shots = float(counts.sum())
    expected = law * shots
    impossible = int(counts[law <= 0].sum())
    if impossible:
        return {"cells": 0, "g": math.inf, "p": 0.0, "impossible_counts": impossible}
    big = expected >= G_POOL
    observed_cells = list(counts[big])
    expected_cells = list(expected[big])
    rest_e, rest_o = float(expected[~big].sum()), float(counts[~big].sum())
    if rest_e > 0:
        observed_cells.append(rest_o)
        expected_cells.append(rest_e)
    o = np.array(observed_cells, dtype=float)
    e = np.array(expected_cells, dtype=float)
    terms = np.where(o > 0, o * np.log(np.where(o > 0, o, 1.0) / e), 0.0)
    statistic = 2.0 * float(terms.sum())
    dof = len(o) - 1
    p = float(chi2.sf(statistic, dof)) if dof > 0 else 1.0
    return {"cells": len(o), "g": round(statistic, 4), "p": p}


def restricted_case(run: str, member: str, index: dict[str, Any]) -> tuple[QuantumCircuit, dict[str, Any]]:
    """Replica 0 of member on its active qubits and the member's execution snapshot restricted to them."""
    prepared = ghost_run.prepare(run, index)
    require("skipped" not in prepared, f"{run}: {prepared.get('skipped')}")
    circuit, qubits = restricted(prepared["replicas"][member][1][0])
    snapshot = json.loads((ROOT / prepared["execution"][member]).read_text(encoding="utf-8"))
    return circuit, snapshot_laws.restrict(snapshot, qubits)


def law_of(
    state: SnapshotState, circuit: QuantumCircuit, cz_factors: Sequence[float], readout_factors: Sequence[float]
) -> np.ndarray:
    """The circuit's law at every (c, r), (F, R, outcomes), on numpy."""
    backend = branch_dm.NumpyBackend()
    plan = state.plan([circuit], cz_factors, True)
    law, _ = branch_dm.evolve(branch_dm.stage(plan, backend), backend, tuple(readout_factors), flip)
    return np.asarray(law)[0]


def final_diagonal(state: SnapshotState, circuit: QuantumCircuit) -> np.ndarray:
    """The factor-1 register diagonal of a circuit without splitting measures."""
    backend = branch_dm.NumpyBackend()
    plan = state.plan([circuit], (1.0,), True)
    require(plan.splits == 0, f"{circuit.name}: a static case splits")
    staged = branch_dm.stage(plan, backend)
    rho = backend.initial(1, 1, 2**plan.n)
    for step, operator in zip(plan.steps, staged.operators, strict=True):
        assert isinstance(step, branch_dm.Step)
        rho = branch_dm._apply_local(rho, step.qargs, operator, plan.n, backend)
    return np.real(np.diagonal(rho[0, 0, 0]))


def aer_simulator(snapshot: dict[str, Any], cz: float, readout: float) -> Any:
    return calibration_snapshot.noise_simulator(ghost_error_scale.scaled(snapshot, cz, readout), "CPU")


def aer_counts(simulator: Any, circuit: QuantumCircuit, shots: int) -> np.ndarray:
    result = simulator.run(circuit, shots=shots, seed_simulator=SEED).result()
    return ghost_run.distribution(result.get_counts(), circuit.num_clbits) * shots


def toy_feed_forward() -> dict[str, Any]:
    """(a): the analytic readout and if_else law on a readout-only noise model."""
    noise = NoiseModel()
    noise.add_readout_error(ReadoutError([[1.0, 0.0], [0.3, 0.7]]), [0])
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.x(1)
    circuit.measure(1, 1)
    program = branch_dm.export(circuit, noise)
    plan = branch_dm.build_plan(program, [circuit], {}, 1, True)
    backend = branch_dm.NumpyBackend()
    factors = (0.5, 1.0, 1.5)
    law, stats = branch_dm.evolve(branch_dm.stage(plan, backend), backend, factors, flip)
    gap = 0.0
    for j, r in enumerate(factors):
        p = 1 - flip(0.3, r)
        gap = max(gap, float(np.max(np.abs(law[0, 0, j] - np.array([1 - p, 0.0, 0.0, p])))))
    require(gap <= 1e-12, f"(a) feed-forward law differs from the analytic one by {gap}")
    require(stats["splits"] == 1 and stats["live"] == 2, f"(a) branch counts {stats}")
    return {"max_abs_minus_analytic": gap, "branches": stats}


def body_noise_toy(index: dict[str, Any]) -> tuple[QuantumCircuit, dict[str, Any]]:
    """(d) toy: a delay and noisy sx gates inside an if_else body on a short-T1 qubit, two Kingston qubits."""
    snapshot = json.loads(
        (ROOT / ghost_run.prepare(DYNAMIC_CASES[0][0], index)["execution"][DYNAMIC_CASES[0][1]]).read_text(
            encoding="utf-8"
        )
    )
    edge = tuple(snapshot["instructions"]["cz"][0]["qargs"])
    reduced = snapshot_laws.restrict(snapshot, sorted(edge))
    reduced = copy.deepcopy(reduced)
    for qubit in reduced["qubits"]:
        qubit["t1"], qubit["t2"] = 10e-6, 10e-6
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.measure(0, 0)
    circuit.x(1)
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.delay(1000, 1, unit="dt")
        for _ in range(20):
            circuit.sx(1)
    circuit.measure(1, 1)
    return circuit, reduced


def self_test() -> dict[str, Any]:
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    timing: dict[str, float] = {}
    laws: list[np.ndarray] = []
    out: dict[str, Any] = {}

    clock = time.perf_counter()
    out["a_feed_forward"] = toy_feed_forward()
    timing["a"] = time.perf_counter() - clock

    clock = time.perf_counter()
    cases = {(run, member): restricted_case(run, member, index) for run, member in (*STATIC_CASES, *DYNAMIC_CASES)}
    states = {key: SnapshotState.build(snapshot) for key, (_, snapshot) in cases.items()}
    timing["prepare"] = time.perf_counter() - clock

    # (b) The static replica that jax_bridge exports.
    clock = time.perf_counter()
    circuit, _ = cases[STATIC_CASES[0]]
    state = states[STATIC_CASES[0]]
    program = jax_bridge.export(circuit, state.noise, {})
    diagonal = np.real(np.diag(jax_bridge.evolve_numpy(program)))
    mine = law_of(state, circuit, (1.0,), READOUT_FACTORS)
    laws.append(mine)
    gap = max(
        float(np.max(np.abs(mine[0, j] - jax_bridge.probabilities(program, diagonal, r, ghost_error_scale.FLIP_CAP))))
        for j, r in enumerate(READOUT_FACTORS)
    )
    require(gap <= JAX_TOLERANCE, f"(b) laws differ from jax_bridge by {gap}")
    out["b_jax_bridge"] = {"case": "#".join(STATIC_CASES[0]), "max_abs_probability_minus_jax_bridge": gap}
    timing["b"] = time.perf_counter() - clock

    # (c) Static diagonals against Aer's density matrix.
    clock = time.perf_counter()
    gaps = {}
    for key in STATIC_CASES:
        circuit, snapshot = cases[key]
        body = circuit.copy_empty_like()
        for instruction in circuit.data:
            if instruction.operation.name != "measure":
                body.append(instruction.operation, instruction.qubits, instruction.clbits)
        physical = jax_bridge._active(circuit)
        body.save_density_matrix(qubits=[body.qubits[q] for q in physical])
        simulator = calibration_snapshot.noise_simulator(snapshot, "CPU")
        reference = np.real(np.diag(np.asarray(simulator.run(body, shots=1).result().data(0)["density_matrix"])))
        gaps["#".join(key)] = float(np.max(np.abs(final_diagonal(states[key], circuit) - reference)))
    require(max(gaps.values()) <= AER_DIAGONAL_TOLERANCE, f"(c) diagonals differ from Aer by {gaps}")
    out["c_aer_diagonal"] = {"max_abs_diagonal_minus_aer": gaps}
    timing["c"] = time.perf_counter() - clock

    # (d) Dynamic laws against Aer density-matrix counts.
    clock = time.perf_counter()
    tests: dict[str, Any] = {}
    for key in DYNAMIC_CASES:
        circuit, snapshot = cases[key]
        for cz, readout in DYNAMIC_POINTS:
            law = law_of(states[key], circuit, (cz,), (readout,))[0, 0]
            laws.append(law[None, None])
            counts = aer_counts(aer_simulator(snapshot, cz, readout), circuit, DYNAMIC_SHOTS)
            tests[f"{'#'.join(key)}@{cz}x{readout}"] = g_test(law, counts)
    toy, toy_snapshot = body_noise_toy(index)
    toy_law = law_of(SnapshotState.build(toy_snapshot), toy, (1.0,), (1.0,))[0, 0]
    laws.append(toy_law[None, None])
    toy_counts = aer_counts(calibration_snapshot.noise_simulator(toy_snapshot, "CPU"), toy, DYNAMIC_SHOTS)
    tests["if_else body delay and sx"] = {**g_test(toy_law, toy_counts), "law": [round(float(v), 6) for v in toy_law]}
    failing = {name: test for name, test in tests.items() if test["p"] < G_TEST_FLOOR}
    require(not failing, f"(d) G tests below p = {G_TEST_FLOOR}: {failing}")
    out["d_aer_counts"] = {"shots": DYNAMIC_SHOTS, "tests": tests}
    timing["d"] = time.perf_counter() - clock

    # (e) CZ rescaling against freshly built scaled noise models.
    clock = time.perf_counter()
    rescale: dict[str, Any] = {}
    channel_distance = 0.0
    law_distance = 0.0
    branches_seen = {"zero_depolarizing": 0, "interior": 0, "error_cap": 0, "depolarizing_cap": 0}
    for key in (DYNAMIC_CASES[1], STATIC_CASES[0]):
        circuit, snapshot = cases[key]
        state = states[key]
        _, skeleton = state.skeleton(circuit)
        couplers = sorted({qargs for _, qargs in skeleton.cz})
        check = jax_bridge_sweep.ScaledModelCheck(
            snapshot, jax_bridge_sweep.non_cz_channels(state.noise), couplers, CONTRACT_FACTORS, CONTRACT_FACTORS
        )
        built = dict(zip(CONTRACT_FACTORS, parallel.ordered_map(check, CONTRACT_FACTORS, min_items=1), strict=True))
        mine = law_of(state, circuit, CONTRACT_FACTORS, (1.0,))
        for j, factor in enumerate(CONTRACT_FACTORS):
            equal, model, errors = built[factor]
            require(equal, f"(e) factor {factor}: a channel other than cz differs from the factor-1 model")
            for qargs in couplers:
                channel, reported = state.channels[qargs]
                error = jax_bridge_sweep.cz_error(reported, factor)
                p = channel.depolarizing(error)
                branches_seen[
                    "zero_depolarizing" if p == 0 else "depolarizing_cap" if p == 16 / 15 else "interior"
                ] += 1
                branches_seen["error_cap"] += error is not None and error > 4 / 5
                aer = branch_dm.from_superop(SuperOp(errors[qargs].to_quantumchannel()).data)
                distance = float(np.max(np.abs(state.cz_superop(qargs, factor) - aer)))
                channel_distance = max(channel_distance, distance)
            fresh = branch_dm.template(circuit, model, {})
            plan = branch_dm.build_plan(fresh, [circuit], None, 1, True)
            backend = branch_dm.NumpyBackend()
            reference = np.asarray(branch_dm.evolve(branch_dm.stage(plan, backend), backend, (1.0,), flip)[0])
            laws.append(reference[0])
            law_distance = max(law_distance, float(np.max(np.abs(mine[j, 0] - reference[0, 0, 0]))))
        rescale["#".join(key)] = {"couplers": len(couplers)}
    require(
        channel_distance <= jax_bridge_sweep.CHANNEL_TOLERANCE, f"(e) CZ superoperators differ by {channel_distance}"
    )
    require(law_distance <= RESCALE_TOLERANCE, f"(e) rescaled laws differ from fresh exports by {law_distance}")
    require(all(branches_seen.values()), f"(e) the factors leave a branch unreached: {branches_seen}")
    out["e_cz_rescale"] = {
        "factors": list(CONTRACT_FACTORS),
        "cases": rescale,
        "max_superop_minus_aer": channel_distance,
        "max_law_minus_fresh_export": law_distance,
        "branches": branches_seen,
    }
    timing["e"] = time.perf_counter() - clock

    # (h) The restricted snapshot gives the full snapshot's laws, one static
    # replica with a delay and a reset and one with feed-forward.
    clock = time.perf_counter()
    run, _ = RESTRICTION_CASES[0]
    prepared = ghost_run.prepare(run, index)
    full = json.loads((ROOT / prepared["execution"][RESTRICTION_CASES[0][1]]).read_text(encoding="utf-8"))
    state = SnapshotState.build(full)
    restriction: dict[str, float] = {}
    for _, member in RESTRICTION_CASES:
        require(prepared["execution"][member] == prepared["execution"][RESTRICTION_CASES[0][1]], "(h) snapshots differ")
        original = prepared["replicas"][member][1][0]
        circuit, qubits = restricted(original)
        small = SnapshotState.build(snapshot_laws.restrict(full, qubits))
        mine = law_of(small, circuit, RESTRICTION_FACTORS, READOUT_FACTORS)
        reference = law_of(state, original, RESTRICTION_FACTORS, READOUT_FACTORS)
        laws += [mine, reference]
        restriction[member] = float(np.max(np.abs(mine - reference)))
    require(max(restriction.values()) <= RESTRICTION_TOLERANCE, f"(h) restricted laws differ by {restriction}")
    out["h_restriction"] = {"factors": list(RESTRICTION_FACTORS), "max_abs_restricted_minus_full": restriction}
    timing["h"] = time.perf_counter() - clock

    # (f) Normalization and sign of every law above.
    sums = max(float(np.max(np.abs(law.sum(axis=-1) - 1))) for law in laws)
    lowest = min(float(law.min()) for law in laws)
    require(sums <= SUM_TOLERANCE, f"(f) laws sum to 1 within {sums}")
    require(lowest >= -np.finfo(np.float64).eps, f"(f) a law entry is {lowest}")
    out["f_normalization"] = {"max_abs_sum_minus_1": sums, "min_probability": lowest}

    # (g) torch complex128 on the CPU against numpy.
    clock = time.perf_counter()
    if branch_dm.load_torch() is None:
        out["g_torch"] = "not run: torch is not importable"
    else:
        key = DYNAMIC_CASES[1]
        circuit, _ = cases[key]
        plan = states[key].plan([circuit], CZ_FACTORS, True)
        numpy_law = np.asarray(
            branch_dm.evolve(
                branch_dm.stage(plan, branch_dm.NumpyBackend()), branch_dm.NumpyBackend(), READOUT_FACTORS, flip
            )[0]
        )
        torch_backend = branch_dm.TorchBackend("cpu", "complex128")
        torch_law = torch_backend.host(
            branch_dm.evolve(branch_dm.stage(plan, torch_backend), torch_backend, READOUT_FACTORS, flip)[0]
        )
        gap = float(np.max(np.abs(numpy_law - torch_law)))
        require(gap <= TORCH_TOLERANCE, f"(g) torch complex128 differs from numpy by {gap}")
        out["g_torch"] = {"case": "#".join(key), "max_abs_torch_minus_numpy": gap}
    timing["g"] = time.perf_counter() - clock
    out["seconds"] = {k: round(v, 2) for k, v in timing.items()}
    return out


def warm_worker(item: int) -> int:
    """A pool item whose unpickling imports this module, and with it numpy, qiskit and branch_dm, in the worker."""
    import qiskit_aer.noise.errors.base_quantum_error  # noqa: F401
    import qiskit_aer.utils  # noqa: F401

    return item


def warmup(backend: branch_dm.Backend) -> float:
    """Seconds to start what the timed phases reuse: the process pool, or the CUDA context and cuBLAS."""
    clock = time.perf_counter()
    if isinstance(backend, branch_dm.TorchBackend):
        probe = backend.upload(np.eye(4))
        (probe @ probe).sum().item()
        backend.synchronize()
    parallel.ordered_map(warm_worker, list(range(parallel.workers())), min_items=1)
    return round(time.perf_counter() - clock, 3)


def profile(run: str, engine: str, device: str, dtype: str, form: str, fuse: bool) -> dict[str, Any]:
    """The four phases on one run, after warmup() has started the pool and any CUDA context."""
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    started = warmup(make_backend(engine, device, dtype))
    result = sweep_run(run, index, engine, device, dtype, form, fuse)
    return {
        "run": run,
        "engine": engine,
        "device": device,
        "dtype": dtype,
        "form": form,
        "fuse": fuse,
        "workers": parallel.workers(),
        "wall_clock_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "warmup_seconds": started,
        "seconds": result.get("seconds"),
        "structures": len(result.get("structures", [])),
        "steps": sum(p["steps"] for p in result.get("structures", [])),
        "exported_ops": sum(p["exported_ops"] for p in result.get("structures", [])),
        "versions": versions(engine),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default=",".join(PART_A_RUNS), help="run directories, comma separated, or all")
    parser.add_argument("--engine", choices=("numpy", "torch"), default="numpy")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--dtype", choices=("complex64", "complex128"), default="complex128")
    parser.add_argument("--form", choices=branch_dm.FORMS, default="local")
    parser.add_argument("--no-fuse", action="store_true", help="one step per exported operation")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--compare-parts", type=Path, help="a ghost_error_scale part file to compare with")
    parser.add_argument("--result", type=Path, help="with --compare-parts, a retained sweep output to compare")
    parser.add_argument("--profile-only", metavar="RUN", help="time the four phases on one run and print them")
    parser.add_argument("--replay", type=Path, help="the retained reduced-case file")
    parser.add_argument("--write", action="store_true", help="with --replay, write the file instead of comparing")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    fuse = not args.no_fuse
    if args.self_test:
        print(json.dumps(self_test(), indent=1))
        return 0
    if args.profile_only:
        print(json.dumps(profile(args.profile_only, args.engine, args.device, args.dtype, args.form, fuse)))
        return 0
    if args.compare_parts and args.result:
        result = json.loads(args.result.read_text(encoding="utf-8"))
        print(json.dumps(compare_parts(result, args.compare_parts), indent=1))
        return 0
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    if args.replay:
        text = replay_document(index)
        if args.write:
            args.replay.parent.mkdir(parents=True, exist_ok=True)
            args.replay.write_text(text, encoding="utf-8")
            return 0
        require(args.replay.read_text(encoding="utf-8") == text, f"{args.replay}: the reduced case differs")
        print(f"{args.replay}: reduced case reproduced byte for byte")
        return 0
    require(args.out is not None, "--out is required")
    runs = ghost_run.audited_runs() if args.runs == "all" else args.runs.split(",")
    out = header(args.engine, args.device, args.dtype, args.form, fuse)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out["warmup_seconds"] = warmup(make_backend(args.engine, args.device, args.dtype))
    for run in runs:
        # Written after every run, so a failure keeps every finished one.
        out["runs"].append(sweep_run(run, index, args.engine, args.device, args.dtype, args.form, fuse))
        args.out.write_text(json.dumps(out) + "\n", encoding="utf-8")
    if args.compare_parts:
        print(json.dumps(compare_parts(out, args.compare_parts), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
