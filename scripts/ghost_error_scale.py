"""Ghost error-scale sweep: per run, the CZ and readout error factors that bring Aer closest to the hardware.

Each retained run's members are rebuilt and sampled as scripts/ghost_run.py
does (prepare, sample, each member at its pub_shots tier, under the
calibration snapshot in force when its PUB began). The snapshot is first
scaled: every cz error by a factor c and every readout flip probability
(e01, e10) by a factor r. A scaled CZ error stops at 1 and a scaled flip at
0.5, where the readout channel starts to invert the bit (a reported flip
above 0.5 keeps its value). NoiseModel.from_backend then
builds each CZ channel as thermal relaxation over the gate duration plus the
depolarizing part that brings its error to the scaled value, so c scales the
modeled CZ infidelity until the depolarizing part reaches zero at the
relaxation floor. Single-qubit gate errors, T1 and T2 keep their reported
values. Every grid point samples with the same seed, so shot noise is common
along the grid and differences between points come from the model.

The output keeps every replica's TV distance to its hardware distribution at
every grid point. Per snapshot it records the run's couplers and qubits,
their mean reported CZ and readout error, the modeled mean CZ infidelity at
each c (which shows the relaxation floor), and how many of them each factor
caps. At each run's minimizing point a second draw under an independent
seed gives the resample floor, the TV distance between two model draws at
the members' shots, which the hardware distance reaches only when the model
is exact.

``--report FILE...`` gives, per run, the mean distance at every grid point, the
minimizing (c, r), its paired change from (1, 1) with the standard error
clustered by executed PUB, and a bootstrap over PUBs of the minimizing
factors. Two reference ends bound the reading: the resample floor, and the
TV distance from each hardware distribution to the uniform one, which every
model approaches as its errors grow without bound. ``--check FILE...`` requires the files (one per kernel) to hold
every audited run exactly once, rebuilds
each run's members, shots, execution snapshots, grid, coverage, means and
cap counts from the archived inputs and the retained distances, requires the
(1, 1) means to agree with docs/evidence/ghost_runs/result.json, and reruns
the ``--runs`` subset on the CPU at (1, 1), its minimizing point and the
grid's top corner, each within five standard errors.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_run  # noqa: E402
import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import average_gate_fidelity  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402

GHOST_RESULT = ROOT / "docs/evidence/ghost_runs/result.json"
CZ_FACTORS = (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 12.0)
READOUT_FACTORS = (0.5, 1.0, 1.5, 2.0, 3.0)
SEED = ghost_run.SEED
BOOTSTRAP = 2000
SCHEMA = "ghost-error-scale-v1"
CZ_CAP = 1.0
FLIP_CAP = 0.5
require = ghost_run.require


def scaled(snapshot: dict[str, Any], cz: float, readout: float) -> dict[str, Any]:
    """The snapshot with every cz error times cz and every readout flip times readout, under the caps."""
    out = copy.deepcopy(snapshot)
    for entry in out["instructions"]["cz"]:
        if entry["error"] is not None:
            entry["error"] = min(cz * entry["error"], CZ_CAP)
    for qubit in out["qubits"]:
        qubit["e01"] = flip(qubit["e01"], readout)
        qubit["e10"] = flip(qubit["e10"], readout)
    return out


def flip(value: float, factor: float) -> float:
    """A readout flip times factor, stopping at FLIP_CAP; a reported flip above the cap keeps its value."""
    return min(factor * value, max(value, FLIP_CAP))


def footprint(circuits: list[QuantumCircuit]) -> tuple[set[int], set[frozenset[int]]]:
    """Physical qubits and CZ couplers the circuits act on; ISA circuits index qubits physically."""
    qubits: set[int] = set()
    couplers: set[frozenset[int]] = set()
    for circuit in circuits:
        for instruction in circuit.data:
            indices = [circuit.find_bit(q).index for q in instruction.qubits]
            if instruction.operation.name == "barrier":
                continue
            qubits.update(indices)
            if instruction.operation.name == "cz":
                couplers.add(frozenset(indices))
    return qubits, couplers


def diagnostics(snapshot: dict[str, Any], circuits: list[QuantumCircuit], infidelity: bool) -> dict[str, Any]:
    """Reported means, cap counts per factor and, with infidelity, the modeled mean CZ infidelity per factor."""
    qubits, couplers = footprint(circuits)
    # The Target lists every coupler in both orientations; a footprint edge
    # counts once, under its first listed orientation.
    entries = []
    seen: set[frozenset[int]] = set()
    for e in snapshot["instructions"]["cz"]:
        edge = frozenset(e["qargs"])
        if edge in couplers and edge not in seen and e["error"] is not None:
            seen.add(edge)
            entries.append(e)
    flips = [v for q in sorted(qubits) for v in (snapshot["qubits"][q]["e01"], snapshot["qubits"][q]["e10"])]
    cz_rows = []
    for factor in CZ_FACTORS:
        row: dict[str, Any] = {"factor": factor, "capped": sum(factor * e["error"] > CZ_CAP for e in entries)}
        if infidelity:
            channels = calibration_snapshot.channel_table(
                calibration_snapshot.noise_model(scaled(snapshot, factor, 1.0))[1]
            )
            row["model_infidelity_mean"] = (
                round(
                    float(
                        np.mean(
                            [
                                1 - average_gate_fidelity(channels[f"cz{e['qargs']}"].to_quantumchannel())
                                for e in entries
                            ]
                        )
                    ),
                    9,
                )
                if entries
                else None
            )
        cz_rows.append(row)
    return {
        "qubits": len(qubits),
        "couplers": len(entries),
        "reported_cz_error_mean": round(float(np.mean([e["error"] for e in entries])), 9) if entries else None,
        "reported_readout_error_mean": round(
            float(np.mean([(snapshot["qubits"][q]["e01"] + snapshot["qubits"][q]["e10"]) / 2 for q in sorted(qubits)])),
            9,
        ),
        "cz": cz_rows,
        "readout": [{"factor": f, "capped": sum(flip(e, f) < f * e for e in flips)} for f in READOUT_FACTORS],
    }


def grid_means(points: list[dict[str, Any]], members: list[str]) -> list[float]:
    return [round(float(np.mean([v for m in members for v in p["tvd"][m]])), 6) for p in points]


def aer_threads(items: int) -> int:
    """Aer threads per pooled point, so the pool's workers share the CPUs without oversubscribing them."""
    return max(1, parallel.available_cpus() // max(1, min(parallel.workers(), items)))


class GridSampler:
    """One snapshot group's TV distances at a (c, r) point; picklable, so the process pool maps it over the grid.

    Aer counts do not depend on its thread count under a fixed seed, so the
    pooled grid equals the serial one.
    """

    def __init__(
        self,
        snapshot: dict[str, Any],
        device: str,
        threads: int,
        chosen: list[str],
        replicas: dict[str, list[QuantumCircuit]],
        measured: dict[str, list[np.ndarray]],
        shots: dict[str, int],
    ) -> None:
        self.snapshot, self.device, self.threads = snapshot, device, threads
        self.chosen, self.replicas = chosen, replicas
        self.measured = {m: measured[m] for m in chosen}
        self.circuits = [r for m in chosen for r in replicas[m]]
        self.shots = [shots[m] for m in chosen for _ in replicas[m]]

    def __call__(self, point: tuple[float, float]) -> dict[str, list[float]]:
        simulator = calibration_snapshot.noise_simulator(scaled(self.snapshot, *point), self.device)
        simulator.set_options(max_parallel_threads=self.threads)
        counts = iter(ghost_run.sample(simulator, self.circuits, self.shots, SEED))
        return {
            m: [
                round(ghost_run.tv(self.measured[m][k], ghost_run.distribution(next(counts), r.num_clbits)), 6)
                for k, r in enumerate(self.replicas[m])
            ]
            for m in self.chosen
        }


def sweep_run(
    run_name: str,
    device: str,
    index: dict[str, Any],
    grid: list[tuple[float, float]],
    floor_point: tuple[float, float] | None = None,
) -> dict[str, Any]:
    """The run's TV distances at every grid point, and the resample floor at floor_point or the minimizing point."""
    prepared = ghost_run.prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "skipped": prepared["skipped"]}
    replicas, measured, shots, execution = (
        prepared["replicas"],
        prepared["measured"],
        prepared["shots"],
        prepared["execution"],
    )
    members = [m for m in prepared["members"] if m in execution]
    points: list[dict[str, Any]] = [{"cz": c, "readout": r, "tvd": {}} for c, r in grid]
    snapshots = {}
    for relative in sorted(set(execution.values())):
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        chosen = [m for m in members if execution[m] == relative]
        circuits = [replica for m in chosen for replica in replicas[m][1]]
        circuit_shots = [shots[m] for m in chosen for _ in replicas[m][1]]
        snapshots[relative] = {"members": len(chosen), **diagnostics(snapshot, circuits, infidelity=True)}
        sampler = GridSampler(
            snapshot, device, aer_threads(len(points)), chosen, {m: replicas[m][1] for m in chosen}, measured, shots
        )
        for point, distances in zip(points, parallel.ordered_map(sampler, grid, min_items=1), strict=True):
            point["tvd"].update(distances)
    means = grid_means(points, members)
    best = int(np.argmin(means))
    cz, readout = floor_point or (points[best]["cz"], points[best]["readout"])
    floor: dict[str, Any] = {"cz": cz, "readout": readout, "tvd": {}}
    for relative in sorted(set(execution.values())):
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        chosen = [m for m in members if execution[m] == relative]
        circuits = [replica for m in chosen for replica in replicas[m][1]]
        circuit_shots = [shots[m] for m in chosen for _ in replicas[m][1]]
        simulator = calibration_snapshot.noise_simulator(scaled(snapshot, cz, readout), device)
        first = iter(ghost_run.sample(simulator, circuits, circuit_shots, SEED))
        second = iter(ghost_run.sample(simulator, circuits, circuit_shots, ghost_run.RESAMPLE_SEED))
        for m in chosen:
            floor["tvd"][m] = [
                round(
                    ghost_run.tv(
                        ghost_run.distribution(next(first), r.num_clbits),
                        ghost_run.distribution(next(second), r.num_clbits),
                    ),
                    6,
                )
                for r in replicas[m][1]
            ]
    floor["mean_tvd"] = round(float(np.mean([v for m in members for v in floor["tvd"][m]])), 6)
    print(
        json.dumps({"run": run_name, "best": [points[best]["cz"], points[best]["readout"]], "mean_tvd": means[best]}),
        flush=True,
    )
    return {
        "run": run_name,
        "backend": prepared["backend"],
        "members": members,
        "member_shots": {m: shots[m] for m in members},
        "execution_snapshot": {m: execution[m] for m in members},
        "snapshots": snapshots,
        "mean_tvd": means,
        "points": points,
        "floor": floor,
    }


def full_grid() -> list[tuple[float, float]]:
    return [(c, r) for c in CZ_FACTORS for r in READOUT_FACTORS]


def pub_sums(run: dict[str, Any]) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Per executed PUB: the summed TV distance at each grid point and its replica count."""
    executed = ghost_run.measured_members(ROOT / run["run"])[1]
    pubs = sorted({executed[m]["pub"] for m in run["members"]})
    position = {pub: k for k, pub in enumerate(pubs)}
    sums = np.zeros((len(pubs), len(run["points"])))
    counts = np.zeros(len(pubs))
    for m in run["members"]:
        k = position[executed[m]["pub"]]
        counts[k] += len(run["points"][0]["tvd"][m])
        for j, point in enumerate(run["points"]):
            sums[k, j] += sum(point["tvd"][m])
    return pubs, sums, counts


def clustered_delta(run: dict[str, Any], j: int, base: int) -> dict[str, Any]:
    """Mean per-replica distance at point j minus at point base, standard error clustered by PUB."""
    executed = ghost_run.measured_members(ROOT / run["run"])[1]
    pairs = [
        (executed[m]["pub"], b - a)
        for m in run["members"]
        for a, b in zip(run["points"][base]["tvd"][m], run["points"][j]["tvd"][m], strict=True)
    ]
    deltas = np.array([d for _, d in pairs])
    mean = float(deltas.mean())
    residual: dict[str, float] = {}
    for pub, d in pairs:
        residual[pub] = residual.get(pub, 0.0) + d - mean
    clusters = len(residual)
    error = (
        math.sqrt(clusters / (clusters - 1) * sum(v * v for v in residual.values())) / len(pairs)
        if clusters > 1
        else None
    )
    return {"mean_delta": round(mean, 6), "standard_error": round(error, 6) if error is not None else None}


def load(paths: list[Path]) -> dict[str, Any]:
    """The runs of every part file, which must share the schema and the module's grid."""
    runs: list[dict[str, Any]] = []
    for path in paths:
        part = json.loads(path.read_text(encoding="utf-8"))
        require(part["schema"] == SCHEMA, f"{path}: schema must be {SCHEMA}")
        require(part["grid"] == [list(p) for p in full_grid()], f"{path}: grid differs from the module's factors")
        runs += part["runs"]
    return {"runs": runs}


def report(paths: list[Path]) -> dict[str, Any]:
    retained = load(paths)
    grid = full_grid()
    base = grid.index((1.0, 1.0))
    rows = []
    for run in retained["runs"]:
        if "skipped" in run:
            rows.append({"run": run["run"], "skipped": run["skipped"]})
            continue
        means = run["mean_tvd"]
        best = int(np.argmin(means))
        pubs, sums, counts = pub_sums(run)
        # A PUB bootstrap with a seed fixed by the run name, so the report is reproducible.
        rng = np.random.default_rng(int(hashlib.sha256(run["run"].encode()).hexdigest()[:8], 16))
        draws = rng.integers(0, len(pubs), size=(BOOTSTRAP, len(pubs)))
        boot = np.argmin(sums[draws].sum(axis=1) / counts[draws].sum(axis=1)[:, None], axis=1)
        cz_draws = np.array([grid[j][0] for j in boot])
        readout_draws = np.array([grid[j][1] for j in boot])
        cz_profile = {str(c): min(m for (gc, _), m in zip(grid, means, strict=True) if gc == c) for c in CZ_FACTORS}
        readout_profile = {
            str(r): min(m for (_, gr), m in zip(grid, means, strict=True) if gr == r) for r in READOUT_FACTORS
        }
        rows.append(
            {
                "run": run["run"],
                "backend": run["backend"],
                "members": len(run["members"]),
                "pubs": len(pubs),
                "mean_tvd_at_reported": means[base],
                "resample_floor": {
                    "cz": run["floor"]["cz"],
                    "readout": run["floor"]["readout"],
                    "mean_tvd": run["floor"]["mean_tvd"],
                },
                "uniform_mean_tvd": uniform_tvd(run),
                "best": {"cz": grid[best][0], "readout": grid[best][1], "mean_tvd": means[best]},
                "best_minus_reported": clustered_delta(run, best, base),
                "cz_profile": cz_profile,
                "readout_profile": readout_profile,
                "bootstrap": {
                    "draws": BOOTSTRAP,
                    "cz_quantiles_16_50_84": [
                        float(np.quantile(cz_draws, q, method="inverted_cdf")) for q in (0.16, 0.5, 0.84)
                    ],
                    "readout_quantiles_16_50_84": [
                        float(np.quantile(readout_draws, q, method="inverted_cdf")) for q in (0.16, 0.5, 0.84)
                    ],
                    "cz_above_1": round(float(np.mean(cz_draws > 1.0)), 4),
                    "cz_at_grid_top": round(float(np.mean(cz_draws == CZ_FACTORS[-1])), 4),
                    "readout_above_1": round(float(np.mean(readout_draws > 1.0)), 4),
                    "readout_at_grid_top": round(float(np.mean(readout_draws == READOUT_FACTORS[-1])), 4),
                },
            }
        )
    fitted = [r for r in rows if "skipped" not in r]
    return {
        "schema": "ghost-error-scale-report-v1",
        "sources": [path.as_posix() for path in paths],
        "cz_factors": list(CZ_FACTORS),
        "readout_factors": list(READOUT_FACTORS),
        "runs": rows,
        "counts": {
            "runs": len(fitted),
            "cz_above_1_in_84_percent": sum(r["bootstrap"]["cz_above_1"] >= 0.84 for r in fitted),
            "cz_at_most_1_in_84_percent": sum(r["bootstrap"]["cz_above_1"] <= 0.16 for r in fitted),
            "readout_above_1_in_84_percent": sum(r["bootstrap"]["readout_above_1"] >= 0.84 for r in fitted),
            "readout_at_most_1_in_84_percent": sum(r["bootstrap"]["readout_above_1"] <= 0.16 for r in fitted),
        },
    }


def uniform_tvd(run: dict[str, Any]) -> float:
    """Mean TV distance from each hardware distribution to the uniform distribution over its outcomes."""
    measured = ghost_run.measured_members(ROOT / run["run"])[0]
    return round(
        float(np.mean([ghost_run.tv(d, np.full(len(d), 1 / len(d))) for m in run["members"] for d in measured[m]])), 6
    )


def tolerance(run: dict[str, Any], members: list[str]) -> float:
    """Five standard errors of the difference of two independent draws of the mean over the members' replicas.

    The mean runs over every replica row, so the sample count is the
    members' replica count, each row weighted by its member's shots.
    """
    rows = [run["member_shots"][m] for m in members for _ in run["points"][0]["tvd"][m]]
    inverse_shots = float(np.mean([1 / shots for shots in rows]))
    return 5 * math.sqrt(2.0 * inverse_shots / len(rows)) + 1e-3


def validate(run: dict[str, Any], index: dict[str, Any], grid: list[tuple[float, float]]) -> None:
    """Require every field the archived inputs and the retained distances determine."""
    name = run["run"]
    prepared = ghost_run.prepare(name, index)
    if "skipped" in prepared:
        require(run.get("skipped") == prepared["skipped"], f"{name}: skip reason differs")
        return
    require("skipped" not in run, f"{name}: marked skipped although its inputs rebuild")
    execution = prepared["execution"]
    members = [m for m in prepared["members"] if m in execution]
    require(run["backend"] == prepared["backend"], f"{name}: backend differs")
    require(run["members"] == members, f"{name}: members differ")
    require(run["member_shots"] == {m: prepared["shots"][m] for m in members}, f"{name}: member shots differ")
    require(run["execution_snapshot"] == {m: execution[m] for m in members}, f"{name}: execution snapshots differ")
    require([(p["cz"], p["readout"]) for p in run["points"]] == grid, f"{name}: grid differs")
    # The sampler groups members by execution snapshot, so a run that spans
    # a calibration change keys its distances in group order.
    for point in run["points"]:
        require(sorted(point["tvd"]) == sorted(members), f"{name}: {point['cz']}x{point['readout']} member coverage")
        for m, row in point["tvd"].items():
            require(len(row) == len(prepared["replicas"][m][1]), f"{name}: {m} replica count")
    require(run["mean_tvd"] == grid_means(run["points"], members), f"{name}: means differ from the distances")
    best = int(np.argmin(run["mean_tvd"]))
    floor = run["floor"]
    require((floor["cz"], floor["readout"]) == grid[best], f"{name}: resample floor is not at the minimizing point")
    require(sorted(floor["tvd"]) == sorted(members), f"{name}: resample floor member coverage")
    for m, row in floor["tvd"].items():
        require(len(row) == len(prepared["replicas"][m][1]), f"{name}: {m} floor replica count")
    require(
        floor["mean_tvd"] == round(float(np.mean([v for m in members for v in floor["tvd"][m]])), 6),
        f"{name}: floor mean differs from its distances",
    )
    require(sorted(run["snapshots"]) == sorted(set(execution.values())), f"{name}: snapshots differ")
    for relative, entry in run["snapshots"].items():
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        chosen = [m for m in members if execution[m] == relative]
        circuits = [replica for m in chosen for replica in prepared["replicas"][m][1]]
        rebuilt = diagnostics(snapshot, circuits, infidelity=False)
        retained = {
            **entry,
            "cz": [{k: v for k, v in row.items() if k != "model_infidelity_mean"} for row in entry["cz"]],
        }
        require(retained == {"members": len(chosen), **rebuilt}, f"{name}: {relative} diagnostics differ")


def check(paths: list[Path], runs: str, index: dict[str, Any]) -> None:
    retained = load(paths)
    grid = full_grid()
    listed = [run["run"] for run in retained["runs"]]
    require(
        sorted(listed) == ghost_run.audited_runs() and len(set(listed)) == len(listed),
        "the files do not hold each audited run exactly once",
    )
    for run in retained["runs"]:
        validate(run, index, grid)
    # The (1, 1) point is the unscaled noise model, so its execution means
    # agree with the ghost runs' execution-state means.
    ghosts = {run["run"]: run for run in json.loads(GHOST_RESULT.read_text(encoding="utf-8"))["runs"]}
    base = grid.index((1.0, 1.0))
    for run in retained["runs"]:
        if "skipped" in run:
            continue
        for relative in run["snapshots"]:
            own = [m for m in run["members"] if run["execution_snapshot"][m] == relative]
            mine = float(np.mean([v for m in own for v in run["points"][base]["tvd"][m]]))
            theirs = ghosts[run["run"]]["summary"][relative]["execution_mean_tvd"]
            require(abs(mine - theirs) <= tolerance(run, own), f"{run['run']}: (1, 1) {mine} vs ghost {theirs}")
    named = None if runs == "all" else set(runs.split(","))
    checked = 0
    for run in retained["runs"]:
        if "skipped" in run or (named is not None and run["run"] not in named):
            continue
        checked += 1
        best = int(np.argmin(run["mean_tvd"]))
        picks = sorted({base, best, len(grid) - 1})
        fresh = sweep_run(run["run"], "CPU", index, [grid[j] for j in picks], grid[best])
        for relative, entry in run["snapshots"].items():
            require(
                fresh["snapshots"][relative]["cz"] == entry["cz"],
                f"{run['run']}: {relative} modeled infidelity differs",
            )
        for k, j in enumerate(picks):
            old, new = run["mean_tvd"][j], fresh["mean_tvd"][k]
            require(abs(old - new) <= tolerance(run, run["members"]), f"{run['run']}: {grid[j]} {old} vs {new}")
        old, new = run["floor"]["mean_tvd"], fresh["floor"]["mean_tvd"]
        require(abs(old - new) <= tolerance(run, run["members"]), f"{run['run']}: floor {old} vs {new}")
    require(checked > 0 and (named is None or checked == len(named)), "--runs names a run the files lack")
    print(f"{len(listed)} runs validated; {checked} rerun on the CPU")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path, nargs="+", help="retained part files that together hold every run")
    parser.add_argument("--report", type=Path, nargs="+", help="print the fitted factors of retained part files")
    args = parser.parse_args()
    if args.report:
        print(json.dumps(report(args.report), indent=1))
        return 0
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    if args.check:
        check(args.check, args.runs, index)
        return 0
    require(args.out is not None, "--out is required")
    runs = ghost_run.audited_runs() if args.runs == "all" else args.runs.split(",")
    device = os.environ.get("GOROROBA_AER_DEVICE", "CPU")
    grid = full_grid()
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "device": device,
        "max_qubits": ghost_run.MAX_QUBITS,
        "seed": SEED,
        "grid": [list(p) for p in grid],
        "scaled": {
            "cz": "instructions.cz[].error",
            "readout": "qubits[].e01 and qubits[].e10",
            "cz_cap": CZ_CAP,
            "readout_cap": FLIP_CAP,
        },
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "runs": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for run in runs:
        # Written after every run, so a failure keeps every finished one.
        out["runs"].append(sweep_run(run, device, index, grid))
        args.out.write_text(json.dumps(out) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
