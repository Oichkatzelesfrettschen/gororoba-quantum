"""Ghost event-scale sweep: scheduled idle, a per-event error and the CZ factor, fitted per run against hardware.

scripts/ghost_error_scale.py fits one CZ factor c and one readout factor r
per run; the dynamic-circuit runs (mid-circuit measurement, feed-forward and
reset) fit c = 5 to 6 while idle relaxation supplies about 2
(docs/evidence/ghost_error_scale/README.md). This sweep separates three error
sources on those runs, with the two static runs as controls, on a grid with
the readout factor fixed at 1:

1. Scheduled idle (``pad``). The replay simulates the unscheduled ISA
   circuit, so a qubit that waits stays ideal. With padding on, every replica
   carries explicit ``delay`` instructions that reproduce the executed idle
   gaps of its PUB's retained ``scheduler_timing`` table
   (raw/JOB/pub_NN.json metadata.compilation.scheduler_timing), and
   NoiseModel.from_backend relaxes each delay at the qubit's T1 and T2
   (RelaxationNoisePass, zero temperature).
2. A per-event error m: a single-qubit depolarizing channel of probability m,
   ``(1 - m) rho + m I / 2``, on the measured qubit immediately after every
   mid-circuit measurement (a measure followed by a later non-barrier
   instruction on its qubit) and after every reset. The channel is appended
   to the circuit as an Aer QuantumError instruction; in density-matrix mode
   it acts as a superoperator and draws no random number. A terminal
   measurement gets no channel, since nothing after it reaches a recorded
   bit. On a qubit measured and then reset, the post-measurement channel is
   inert because the reset erases it.
3. The CZ factor c, applied as ghost_error_scale.scaled does.

Grid: c in CZ_FACTORS, m in EVENT_ERRORS, padding off and on, readout
factor 1. Every grid point samples every replica with the same seed
(ghost_run.sample, SEED), so shot noise is common along the grid. At m = 0 no
channel is inserted; the self-test requires an inserted zero-probability
channel to reproduce the unmodified replay's counts exactly under the same
seed. A static run has no event, so its circuits are identical across m and
its m = 0 column is computed once and copied to every m. At each padding
state's minimizing point a second draw under ghost_run.RESAMPLE_SEED gives
the resample floor.

Padding rule. Each replica qubit keeps a replay clock that starts at its
first timed operation (sx, x, cz, measure, reset). A timed operation
advances the clock by its Target duration in the execution snapshot; an ISA
``delay`` advances it by its own duration, since the replay already relaxes
it and the schedule carries no row for it. Before each timed operation the
pad is the executed start minus the clock, inserted as a delay on that
qubit; a negative pad stops the run. Schedule rows are the main-branch
``play`` and ``capture`` rows on a channel whose trailing digits name the
qubit (``Qubit 93``, ``AWGR11_93``), less INIT and FINI; shift_phase,
barrier, broadcast and receive rows carry no pulse on a qubit. An event's
rows start with the next unconsumed row on each of its qubits and include
every following row of the same label that starts inside
``[start, start + duration)``, so back-to-back events of one label stay
separate. Before padding, every replica qubit's operation sequence must equal
its row sequence label by label (``cz_79_93`` names a cz on 79 and 93 in
either order), a cz must start at one time on both qubits, every event's rows
must end inside its Target duration, and every row must be consumed; any
difference stops the run. ``if_else`` blocks of the retained runs hold only
virtual rz; a block with any other operation stops the run. An ``if_else``
takes zero time on the clock: its then and else rows carry only phase
shifts and stay out of the sequence, and the feed-forward wait it spans lands
in the pad before the next main-branch operation. Idle time before a qubit's
first operation (the qubit sits in |0>) and after its last is not padded. The
measured qubit's own capture window is outside the clock's relaxation, as in
the unpadded replay, which gives a measurement only its readout flip; m
absorbs any error there.

Falsifiers, stated before any fit. Each dynamic run is compared with the
static control on its backend (CONTROLS); "within one grid step" is an index
distance of at most 1 in CZ_FACTORS, and every verdict reads the padded
grid:

- If padding moves both static runs' best c to within one grid step of 1
  while every dynamic run keeps its best c >= 4 at m = 0, idle relaxation is
  not the dynamic excess.
- If a nonzero m brings every dynamic run's best c to within one grid step of
  its static control's, the excess is per-event.
- If neither holds, the excess is elsewhere.

Argmin ties resolve to the first grid point in grid order (m ascending), so
a static run's best m is 0.

``--report FILE...`` gives per run and padding state the minimizing (c, m),
the best c at m = 0, the paired change from (c, m) = (1, 0) with the
standard error clustered by executed PUB, a bootstrap over PUBs of the
minimizing (c, m) (BOOTSTRAP draws, the PUB count beside the quantiles, and
the fraction of draws at each axis's floor and top), the resample floor and
the uniform-distribution distance, then the three verdicts.

``--check FILE...`` validates every run the files hold: members, shots,
execution snapshots, PUBs, event counts and padding are rebuilt from the
archived inputs and must match; the grid, coverage, means and floors must
follow from the retained distances; the (1, 0, padding off) means must agree
with docs/evidence/ghost_runs/result.json within five standard errors. It
then reruns the ``--runs`` subset (default every run the files hold) on the
CPU at (1, 0) and the top corner (6, 0.2) of each padding state and at each
padding state's minimizing point and floor, each within five standard
errors.

``--self-test`` runs on the CPU in well under a minute: it pads every replica
of every default run (parsing only), requires a dropped row, a relabeled row
and a pulse inside an if_else block to fail the match, and on a synthetic
two-qubit dynamic circuit with a synthetic schedule requires the computed
pads to equal the planted gaps, an inserted m = 0 channel to reproduce the
unmodified counts, the padding-off m = 0 point to equal the
ghost_error_scale path at (c, 1), padding and a nonzero m each to change the
counts, and the pooled grid to equal the serial one.

Kaggle. The full sweep runs on Kaggle CPU kernels; the retained runs come
from the gororoba-retained-runs dataset and kaggle_run bundles this script's
imports (ghost_error_scale, ghost_run, calibration_snapshot, packing,
parallel), so no --include is needed. One part per kernel, for example:

    "$PYTHON" scripts/kaggle_run.py push scripts/ghost_event_scale.py \\
        --slug gororoba-ghost-event-scale-a --dataset gororoba-retained-runs \\
        --machine cpu --timeout 43200 -- \\
        --runs results/live/2026-10-11T152922.787095Z \\
        --out results/kaggle_out/ghost_event_scale_a.json

Usage:
    "$PYTHON" scripts/ghost_event_scale.py --runs RUN[,RUN] --out FILE
    "$PYTHON" scripts/ghost_event_scale.py --report FILE...
    "$PYTHON" scripts/ghost_event_scale.py --check FILE... [--runs RUN[,RUN]]
    "$PYTHON" scripts/ghost_event_scale.py --self-test
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_error_scale  # noqa: E402
import ghost_run  # noqa: E402
import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.circuit import Delay  # noqa: E402
from qiskit_aer.noise import depolarizing_error  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "ghost-event-scale-v1"
CZ_FACTORS = (1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0)
EVENT_ERRORS = (0.0, 0.01, 0.02, 0.05, 0.1, 0.2)
PADDING = (False, True)
READOUT_FACTOR = 1.0
SEED = ghost_run.SEED
BOOTSTRAP = 2000
DYNAMIC_RUNS = (
    "results/live/2026-10-13T020454.599853Z",
    "results/live/2026-10-13T022433.333775Z",
    "results/live/2026-10-13T080216.451663Z",
    "results/live/2026-10-13T083417.634585Z",
    "results/live/2026-10-11T152922.787095Z",
    "results/live/2026-10-12T055624.091217Z",
    "results/live/2026-10-13T201757.782152Z",
    "results/live/2026-10-15T030748.903241Z",
)
STATIC_RUNS = ("results/live/2026-10-13T032011.664435Z", "results/live/2026-10-15T030903.235380Z")
DEFAULT_RUNS = DYNAMIC_RUNS + STATIC_RUNS
CONTROLS = {"ibm_fez": STATIC_RUNS[0], "ibm_kingston": STATIC_RUNS[1]}
TIMED = ("sx", "x", "cz", "measure", "reset")
VIRTUAL = ("rz", "barrier")
CHANNEL_QUBIT = re.compile(r"(\d+)$")
require = ghost_run.require

Point = tuple[bool, float, float]
Row = tuple[str, int, int]


def full_grid() -> list[Point]:
    return [(pad, c, m) for pad in PADDING for c in CZ_FACTORS for m in EVENT_ERRORS]


def schedule_rows(table: str) -> dict[int, list[Row]]:
    """Main-branch play and capture rows per qubit, less INIT and FINI, in start order."""
    rows: dict[int, list[tuple[int, int, Row]]] = collections.defaultdict(list)
    for position, line in enumerate(table.splitlines()):
        branch, label, channel, start_text, duration_text, kind = line.split(",")
        match = CHANNEL_QUBIT.search(channel)
        if branch != "main" or kind not in ("play", "capture") or match is None:
            continue
        if label.startswith(("INIT_", "FINI_")):
            continue
        start = int(start_text)
        rows[int(match.group(1))].append((start, position, (label, start, int(duration_text))))
    return {q: [row for _, _, row in sorted(entries)] for q, entries in rows.items()}


def target_durations(snapshot: dict[str, Any]) -> dict[tuple[str, tuple[int, ...]], int]:
    """Every timed operation's Target duration in dt, keyed by name and qubits."""
    dt = snapshot["dt"]
    out = {}
    for name in TIMED:
        for entry in snapshot["instructions"][name]:
            ticks = entry["duration"] / dt
            require(abs(ticks - round(ticks)) < 1e-6, f"{name}{entry['qargs']}: duration is not a whole dt")
            out[name, tuple(entry["qargs"])] = round(ticks)
    return out


def label_matches(label: str, name: str, qubits: list[int]) -> bool:
    head, *rest = label.split("_")
    return head == name and sorted(int(q) for q in rest) == sorted(qubits)


def pad(
    replica: QuantumCircuit, rows: dict[int, list[Row]], durations: dict[tuple[str, tuple[int, ...]], int]
) -> tuple[QuantumCircuit, dict[str, Any]]:
    """The replica with a delay before each timed operation that reproduces its executed idle gap.

    The module docstring states the matching rule and the replay clock.
    """
    name = replica.name
    out = QuantumCircuit(*replica.qregs, *replica.cregs, name=name)
    active = sorted({replica.find_bit(q).index for inst in replica.data for q in inst.qubits})
    cursor: dict[int, int] = collections.defaultdict(int)
    clock: dict[int, int] = {}
    pads: list[int] = []
    for inst in replica.data:
        operation = inst.operation
        qubits = [replica.find_bit(q).index for q in inst.qubits]
        if operation.name in VIRTUAL:
            out.append(inst)
            continue
        if operation.name == "delay":
            require(operation.unit == "dt", f"{name}: delay in {operation.unit}, not dt")
            for q in qubits:
                if q in clock:
                    clock[q] += int(operation.duration)
            out.append(inst)
            continue
        if operation.name == "if_else":
            for block in operation.blocks:
                inner = [i.operation.name for i in block.data]
                require(
                    all(n in VIRTUAL for n in inner), f"{name}: if_else block holds {inner}, outside the padding rule"
                )
            out.append(inst)
            continue
        require(operation.name in TIMED, f"{name}: {operation.name} on {qubits} has no padding rule")
        key = (operation.name, tuple(qubits))
        if key not in durations and len(qubits) == 2:
            key = (operation.name, (qubits[1], qubits[0]))
        require(key in durations, f"{name}: {operation.name} on {qubits} has no Target duration")
        duration = durations[key]
        starts = []
        for q in qubits:
            stream = rows.get(q, [])
            k = cursor[q]
            require(k < len(stream), f"{name}: qubit {q} runs {operation.name} after its last schedule row")
            label, start, length = stream[k]
            require(
                label_matches(label, operation.name, qubits),
                f"{name}: qubit {q} executed {label} where the circuit has {operation.name} on {qubits}",
            )
            end = start + duration
            require(start + length <= end, f"{name}: {label} at {start} outlasts its Target duration {duration}")
            k += 1
            while k < len(stream) and stream[k][1] < end:
                require(stream[k][0] == label, f"{name}: {stream[k][0]} starts inside {label} at {start}")
                require(stream[k][1] + stream[k][2] <= end, f"{name}: {label} at {start} outlasts {duration} dt")
                k += 1
            cursor[q] = k
            starts.append(start)
        require(len(set(starts)) == 1, f"{name}: {operation.name} on {qubits} starts at {starts}")
        for q in qubits:
            if q in clock:
                gap = starts[0] - clock[q]
                require(gap >= 0, f"{name}: qubit {q} starts {operation.name} {-gap} dt before its replay clock")
                if gap:
                    out.append(Delay(gap, unit="dt"), [replica.qubits[q]])
                    pads.append(gap)
            clock[q] = starts[0] + duration
        out.append(inst)
    for q in active:
        require(cursor[q] == len(rows.get(q, [])), f"{name}: qubit {q} leaves schedule rows unmatched")
    return out, {"delays": len(pads), "pad_dt": sum(pads), "max_pad_dt": max(pads, default=0)}


def event_count(circuit: QuantumCircuit) -> int:
    return len(event_positions(circuit))


def event_positions(circuit: QuantumCircuit) -> list[tuple[int, int]]:
    """(instruction index, qubit) of every reset and every measurement followed by a later use of its qubit."""
    last_use: dict[int, int] = {}
    for position, inst in enumerate(circuit.data):
        if inst.operation.name in ("barrier", "delay"):
            continue
        for q in inst.qubits:
            last_use[circuit.find_bit(q).index] = position
    out = []
    for position, inst in enumerate(circuit.data):
        if inst.operation.name in ("reset", "measure"):
            q = circuit.find_bit(inst.qubits[0]).index
            if inst.operation.name == "reset" or last_use[q] > position:
                out.append((position, q))
    return out


def with_events(circuit: QuantumCircuit, probability: float) -> QuantumCircuit:
    """The circuit with a depolarizing channel of the given probability after each event."""
    positions = dict(event_positions(circuit))
    out = QuantumCircuit(*circuit.qregs, *circuit.cregs, name=circuit.name)
    error = depolarizing_error(probability, 1)
    for position, inst in enumerate(circuit.data):
        out.append(inst)
        if position in positions:
            out.append(error, [circuit.qubits[positions[position]]])
    return out


def pub_timings(run: Path) -> dict[str, str]:
    """Each executed PUB's scheduler_timing table by PUB name; a name may occur once."""
    out: dict[str, str] = {}
    for path in sorted(run.glob("raw/*/pub_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        require(data["pub_name"] not in out, f"{run.name}: PUB {data['pub_name']} occurs in two raw files")
        out[data["pub_name"]] = data["metadata"]["compilation"]["scheduler_timing"]["timing"]
    return out


def member_pubs(record: dict[str, Any]) -> dict[str, str]:
    return {
        component["member"]: pub["name"]
        for job in record["submission"]["planned_jobs"]
        for pub in job["pubs"]
        for component in pub["components"]
    }


def prepare(run_name: str, index: dict[str, Any]) -> dict[str, Any]:
    """ghost_run.prepare restricted to members with an execution snapshot, plus each replica padded."""
    prepared = ghost_run.prepare(run_name, index)
    require("skipped" not in prepared, f"{run_name}: {prepared.get('skipped')}")
    run = ROOT / run_name
    execution = prepared["execution"]
    members = [m for m in prepared["members"] if m in execution]
    record = json.loads((run / "record.json").read_text(encoding="utf-8"))
    pubs = member_pubs(record)
    executed = ghost_run.measured_members(run)[1]
    timings = pub_timings(run)
    snapshots = {
        relative: json.loads((ROOT / relative).read_text(encoding="utf-8"))
        for relative in sorted(set(execution[m] for m in members))
    }
    durations = {relative: target_durations(snapshot) for relative, snapshot in snapshots.items()}
    padded: dict[str, list[QuantumCircuit]] = {}
    padding: dict[str, list[dict[str, Any]]] = {}
    for m in members:
        require(executed[m]["pub"] == pubs[m], f"{run_name}: {m} executed in {executed[m]['pub']}, planned {pubs[m]}")
        rows = schedule_rows(timings[pubs[m]])
        results = [pad(replica, rows, durations[execution[m]]) for replica in prepared["replicas"][m][1]]
        padded[m] = [circuit for circuit, _ in results]
        padding[m] = [summary for _, summary in results]
    return {
        "backend": prepared["backend"],
        "members": members,
        "shots": {m: prepared["shots"][m] for m in members},
        "execution": {m: execution[m] for m in members},
        "snapshots": snapshots,
        "pubs": {m: pubs[m] for m in members},
        "measured": {m: prepared["measured"][m] for m in members},
        "replicas": {m: prepared["replicas"][m][1] for m in members},
        "padded": padded,
        "padding": padding,
        "events": {m: [event_count(r) for r in prepared["replicas"][m][1]] for m in members},
    }


class RunSampler:
    """Samples one run's replicas at a grid point; picklable, so the process pool maps it over points.

    Each worker builds the scaled noise simulator of the point itself, with
    Aer limited to its share of the CPUs; Aer counts do not depend on its
    thread count under a fixed seed.
    """

    def __init__(self, prepared: dict[str, Any], device: str, threads: int) -> None:
        self.device = device
        self.threads = threads
        self.measured = prepared["measured"]
        self.groups = []
        for relative in sorted(set(prepared["execution"].values())):
            chosen = [m for m in prepared["members"] if prepared["execution"][m] == relative]
            self.groups.append(
                (
                    prepared["snapshots"][relative],
                    chosen,
                    {
                        False: [r for m in chosen for r in prepared["replicas"][m]],
                        True: [r for m in chosen for r in prepared["padded"][m]],
                    },
                    [prepared["shots"][m] for m in chosen for _ in prepared["replicas"][m]],
                    [len(prepared["replicas"][m]) for m in chosen],
                )
            )

    def simulator(self, snapshot: dict[str, Any], cz: float) -> Any:
        simulator = calibration_snapshot.noise_simulator(
            ghost_error_scale.scaled(snapshot, cz, READOUT_FACTOR), self.device
        )
        simulator.set_options(max_parallel_threads=self.threads)
        return simulator

    def __call__(self, item: tuple[bool, float, float, bool]) -> dict[str, list[float]]:
        """Per member, each replica's TV distance to hardware, or with floor set to a second model draw."""
        padded, cz, event, floor = item
        out: dict[str, list[float]] = {}
        for snapshot, chosen, circuits, shots, widths in self.groups:
            batch = [with_events(c, event) if event else c for c in circuits[padded]]
            simulator = self.simulator(snapshot, cz)
            first = iter(ghost_run.sample(simulator, batch, shots, SEED))
            second = iter(ghost_run.sample(simulator, batch, shots, ghost_run.RESAMPLE_SEED)) if floor else None
            position = iter(batch)
            for m, width in zip(chosen, widths, strict=True):
                row = []
                for k in range(width):
                    clbits = next(position).num_clbits
                    model = ghost_run.distribution(next(first), clbits)
                    other = ghost_run.distribution(next(second), clbits) if second is not None else self.measured[m][k]
                    row.append(round(ghost_run.tv(other, model), 6))
                out[m] = row
        return out


class TimedSampler:
    """A RunSampler call and its wall seconds, which size the Kaggle split."""

    def __init__(self, sampler: RunSampler) -> None:
        self.sampler = sampler

    def __call__(self, item: tuple[bool, float, float, bool]) -> tuple[dict[str, list[float]], float]:
        start = time.time()
        return self.sampler(item), round(time.time() - start, 1)


def aer_threads(items: int) -> int:
    """Aer threads per pooled point, so the pool's workers share the CPUs without oversubscribing them."""
    workers = min(parallel.workers(), items)
    return max(1, parallel.available_cpus() // max(1, workers))


def padding_summary(prepared: dict[str, Any]) -> dict[str, Any]:
    rows = [s for m in prepared["members"] for s in prepared["padding"][m]]
    return {
        "delays": sum(s["delays"] for s in rows),
        "pad_dt": sum(s["pad_dt"] for s in rows),
        "max_pad_dt": max((s["max_pad_dt"] for s in rows), default=0),
    }


def sweep_run(
    run_name: str,
    device: str,
    index: dict[str, Any],
    grid: list[Point],
    floors: dict[bool, tuple[float, float]] | None = None,
) -> dict[str, Any]:
    """The run's TV distances at every grid point and the resample floor of each padding state."""
    start = time.time()
    prepared = prepare(run_name, index)
    members = prepared["members"]
    event_free = all(n == 0 for m in members for n in prepared["events"][m])
    # An event-free run's circuits are identical across m, so one m = 0
    # draw per (padding, c) stands for every m under the common seed.
    sampled = sorted({(pad, c, 0.0 if event_free else m) for pad, c, m in grid}, key=grid_order)
    sampler = TimedSampler(RunSampler(prepared, device, aer_threads(len(sampled))))
    values = parallel.ordered_map(sampler, [(pad, c, m, False) for pad, c, m in sampled], min_items=1)
    by_point = {point: tvd for point, (tvd, _) in zip(sampled, values, strict=True)}
    seconds = [[*point, elapsed] for point, (_, elapsed) in zip(sampled, values, strict=True)]
    points = [{"pad": pad, "cz": c, "m": m, "tvd": by_point[pad, c, 0.0 if event_free else m]} for pad, c, m in grid]
    means = ghost_error_scale.grid_means(points, members)
    chosen = {}
    for padded in PADDING:
        if floors is not None and padded in floors:
            chosen[padded] = floors[padded]
            continue
        own = [j for j, p in enumerate(points) if p["pad"] == padded]
        if own:
            best = min(own, key=lambda j: (means[j], j))
            chosen[padded] = (points[best]["cz"], points[best]["m"])
    floor_values = parallel.ordered_map(sampler, [(p, c, m, True) for p, (c, m) in chosen.items()], min_items=1)
    floor_rows = {}
    for (padded, (c, m)), (tvd, elapsed) in zip(chosen.items(), floor_values, strict=True):
        seconds.append([padded, c, m, elapsed])
        floor_rows["padded" if padded else "unpadded"] = {
            "cz": c,
            "m": m,
            "tvd": tvd,
            "mean_tvd": round(float(np.mean([v for row in tvd.values() for v in row])), 6),
        }
    out = {
        "run": run_name,
        "backend": prepared["backend"],
        "control": None if run_name in STATIC_RUNS else CONTROLS.get(prepared["backend"]),
        "members": members,
        "member_shots": prepared["shots"],
        "execution_snapshot": prepared["execution"],
        "member_pub": prepared["pubs"],
        "events": prepared["events"],
        "event_free": event_free,
        "padding": prepared["padding"],
        "padding_total": padding_summary(prepared),
        "mean_tvd": means,
        "points": points,
        "floor": floor_rows,
        # Wall seconds of each sampled point, then of each floor's two draws.
        "draw_seconds": seconds,
        "seconds": round(time.time() - start, 1),
    }
    print(json.dumps({"run": run_name, "seconds": out["seconds"], "best": best_points(out)}), flush=True)
    return out


def grid_order(point: Point) -> int:
    return full_grid().index(point)


def best_index(run: dict[str, Any], padded: bool, event: float | None = None) -> int:
    """The minimizing point of one padding state, optionally at one m; ties go to the first point."""
    own = [j for j, p in enumerate(run["points"]) if p["pad"] == padded and (event is None or p["m"] == event)]
    return min(own, key=lambda j: (run["mean_tvd"][j], j))


def best_points(run: dict[str, Any]) -> dict[str, list[float]]:
    out = {}
    for padded in PADDING:
        j = best_index(run, padded)
        out["padded" if padded else "unpadded"] = [run["points"][j]["cz"], run["points"][j]["m"], run["mean_tvd"][j]]
    return out


def load(paths: list[Path]) -> list[dict[str, Any]]:
    """The runs of every part file, which must share the schema and the module's grid; a run occurs once."""
    runs: list[dict[str, Any]] = []
    for path in paths:
        part = json.loads(path.read_text(encoding="utf-8"))
        require(part["schema"] == SCHEMA, f"{path}: schema must be {SCHEMA}")
        require(part["grid"] == [list(p) for p in full_grid()], f"{path}: grid differs from the module's axes")
        runs += part["runs"]
    names = [run["run"] for run in runs]
    require(len(set(names)) == len(names), "a run occurs in more than one part")
    return runs


def bootstrap(run: dict[str, Any], padded: bool) -> dict[str, Any]:
    """PUB bootstrap of the minimizing (c, m) of one padding state, seeded by the run name."""
    pubs, sums, counts = ghost_error_scale.pub_sums(run)
    own = [j for j, p in enumerate(run["points"]) if p["pad"] == padded]
    rng = np.random.default_rng(int(hashlib.sha256(run["run"].encode()).hexdigest()[:8], 16))
    draws = rng.integers(0, len(pubs), size=(BOOTSTRAP, len(pubs)))
    means = sums[draws][:, :, own].sum(axis=1) / counts[draws].sum(axis=1)[:, None]
    picks = [own[j] for j in np.argmin(means, axis=1)]
    cz = np.array([run["points"][j]["cz"] for j in picks])
    event = np.array([run["points"][j]["m"] for j in picks])

    def quantiles(values: np.ndarray) -> list[float]:
        return [float(np.quantile(values, q, method="inverted_cdf")) for q in (0.16, 0.5, 0.84)]

    return {
        "draws": BOOTSTRAP,
        "pubs": len(pubs),
        "cz_quantiles_16_50_84": quantiles(cz),
        "m_quantiles_16_50_84": quantiles(event),
        "cz_at_floor": round(float(np.mean(cz == CZ_FACTORS[0])), 4),
        "cz_at_top": round(float(np.mean(cz == CZ_FACTORS[-1])), 4),
        "m_at_floor": round(float(np.mean(event == EVENT_ERRORS[0])), 4),
        "m_at_top": round(float(np.mean(event == EVENT_ERRORS[-1])), 4),
    }


def state_report(run: dict[str, Any], padded: bool) -> dict[str, Any]:
    points, means = run["points"], run["mean_tvd"]
    base = full_grid().index((padded, 1.0, 0.0))
    best = best_index(run, padded)
    at_zero = best_index(run, padded, 0.0)
    floor = run["floor"]["padded" if padded else "unpadded"]
    return {
        "mean_tvd_at_1_0": means[base],
        "best": {"cz": points[best]["cz"], "m": points[best]["m"], "mean_tvd": means[best]},
        "best_cz_at_m0": {"cz": points[at_zero]["cz"], "mean_tvd": means[at_zero]},
        "best_minus_1_0": ghost_error_scale.clustered_delta(run, best, base),
        "cz_profile_at_m0": {
            str(p["cz"]): means[j] for j, p in enumerate(points) if p["pad"] == padded and p["m"] == 0
        },
        "m_profile": {
            str(m): min(means[j] for j, p in enumerate(points) if p["pad"] == padded and p["m"] == m)
            for m in EVENT_ERRORS
        },
        "resample_floor": {"cz": floor["cz"], "m": floor["m"], "mean_tvd": floor["mean_tvd"]},
        "bootstrap": bootstrap(run, padded),
    }


def step(c: float) -> int:
    return CZ_FACTORS.index(c)


def verdicts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """The three falsifier readings of the module docstring on the padded grid."""
    by_run = {row["run"]: row for row in rows}
    static = [by_run[r] for r in STATIC_RUNS if r in by_run]
    dynamic = [by_run[r] for r in DYNAMIC_RUNS if r in by_run]
    complete = len(static) == len(STATIC_RUNS) and len(dynamic) == len(DYNAMIC_RUNS)
    static_near_1 = {row["run"]: step(row["padded"]["best"]["cz"]) <= 1 for row in static}
    dynamic_ge_4 = {row["run"]: row["padded"]["best_cz_at_m0"]["cz"] >= 4.0 for row in dynamic}
    per_event: dict[str, bool | None] = {}
    for row in dynamic:
        control = by_run.get(row["control"])
        if control is None:
            per_event[row["run"]] = None
            continue
        best = row["padded"]["best"]
        per_event[row["run"]] = best["m"] > 0 and abs(step(best["cz"]) - step(control["padded"]["best"]["cz"])) <= 1
    idle_not_excess = all(static_near_1.values()) and all(dynamic_ge_4.values()) if complete else None
    excess_per_event = all(v is True for v in per_event.values()) if complete else None
    return {
        "complete": complete,
        "static_best_cz_within_one_step_of_1": static_near_1,
        "dynamic_best_cz_at_m0_at_least_4": dynamic_ge_4,
        "dynamic_nonzero_m_best_cz_within_one_step_of_control": per_event,
        "idle_relaxation_not_the_dynamic_excess": idle_not_excess,
        "excess_per_event": excess_per_event,
        "excess_elsewhere": (not idle_not_excess and not excess_per_event) if complete else None,
    }


def report(paths: list[Path]) -> dict[str, Any]:
    rows = []
    for run in load(paths):
        rows.append(
            {
                "run": run["run"],
                "backend": run["backend"],
                "control": run["control"],
                "members": len(run["members"]),
                "events": sum(n for row in run["events"].values() for n in row),
                "padding_total": run["padding_total"],
                "uniform_mean_tvd": ghost_error_scale.uniform_tvd(run),
                "unpadded": state_report(run, False),
                "padded": state_report(run, True),
            }
        )
    return {
        "schema": "ghost-event-scale-report-v1",
        "sources": [path.as_posix() for path in paths],
        "cz_factors": list(CZ_FACTORS),
        "event_errors": list(EVENT_ERRORS),
        "runs": rows,
        "verdicts": verdicts(rows),
    }


def validate(run: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    """Require every field the archived inputs and the retained distances determine; return the rebuild."""
    name = run["run"]
    prepared = prepare(name, index)
    members = prepared["members"]
    grid = full_grid()
    require(run["backend"] == prepared["backend"], f"{name}: backend differs")
    require(run["control"] == (None if name in STATIC_RUNS else CONTROLS.get(prepared["backend"])), f"{name}: control")
    require(run["members"] == members, f"{name}: members differ")
    for key, value in (
        ("member_shots", prepared["shots"]),
        ("execution_snapshot", prepared["execution"]),
        ("member_pub", prepared["pubs"]),
        ("events", prepared["events"]),
        ("padding", prepared["padding"]),
        ("padding_total", padding_summary(prepared)),
    ):
        require(run[key] == value, f"{name}: {key} differs from the archived inputs")
    event_free = all(n == 0 for m in members for n in prepared["events"][m])
    require(run["event_free"] == event_free, f"{name}: event_free differs")
    require([(p["pad"], p["cz"], p["m"]) for p in run["points"]] == grid, f"{name}: grid differs")
    for point in run["points"]:
        require(list(point["tvd"]) == members, f"{name}: {point['pad']} {point['cz']} {point['m']} coverage")
        for m, row in point["tvd"].items():
            require(len(row) == len(prepared["replicas"][m]), f"{name}: {m} replica count")
        if event_free:
            twin = run["points"][grid.index((point["pad"], point["cz"], 0.0))]
            require(point["tvd"] == twin["tvd"], f"{name}: an event-free run's distances differ across m")
    require(run["mean_tvd"] == ghost_error_scale.grid_means(run["points"], members), f"{name}: means differ")
    for padded in PADDING:
        floor = run["floor"]["padded" if padded else "unpadded"]
        best = run["points"][best_index(run, padded)]
        require((floor["cz"], floor["m"]) == (best["cz"], best["m"]), f"{name}: floor is not at the minimizing point")
        require(list(floor["tvd"]) == members, f"{name}: floor coverage")
        require(
            floor["mean_tvd"] == round(float(np.mean([v for row in floor["tvd"].values() for v in row])), 6),
            f"{name}: floor mean differs from its distances",
        )
    return prepared


def check(paths: list[Path], runs: str, index: dict[str, Any]) -> None:
    retained = load(paths)
    ghosts = {r["run"]: r for r in json.loads(ghost_error_scale.GHOST_RESULT.read_text(encoding="utf-8"))["runs"]}
    grid = full_grid()
    base = grid.index((False, 1.0, 0.0))
    for run in retained:
        validate(run, index)
        # Padding off at (1, 0) is the unmodified replay, so its execution
        # means agree with the ghost runs' execution-state means.
        for relative in sorted(set(run["execution_snapshot"].values())):
            own = [m for m in run["members"] if run["execution_snapshot"][m] == relative]
            mine = float(np.mean([v for m in own for v in run["points"][base]["tvd"][m]]))
            theirs = ghosts[run["run"]]["summary"][relative]["execution_mean_tvd"]
            bound = ghost_error_scale.tolerance(run, own)
            require(abs(mine - theirs) <= bound, f"{run['run']}: (1, 0) {mine} vs ghost {theirs}")
    named = [r["run"] for r in retained] if runs == "all" else runs.split(",")
    held = {r["run"]: r for r in retained}
    require(all(n in held for n in named), "--runs names a run the files lack")
    for name in named:
        run = held[name]
        floors = {p: (run["floor"][s]["cz"], run["floor"][s]["m"]) for p, s in ((False, "unpadded"), (True, "padded"))}
        picks = sorted(
            {grid.index((p, 1.0, 0.0)) for p in PADDING}
            | {grid.index((p, CZ_FACTORS[-1], EVENT_ERRORS[-1])) for p in PADDING}
            | {grid.index((p, *floors[p])) for p in PADDING}
        )
        fresh = sweep_run(name, "CPU", index, [grid[j] for j in picks], floors)
        bound = ghost_error_scale.tolerance(run, run["members"])
        for k, j in enumerate(picks):
            old, new = run["mean_tvd"][j], fresh["mean_tvd"][k]
            require(abs(old - new) <= bound, f"{name}: {grid[j]} {old} vs {new}")
        for state in ("unpadded", "padded"):
            old, new = run["floor"][state]["mean_tvd"], fresh["floor"][state]["mean_tvd"]
            require(abs(old - new) <= bound, f"{name}: {state} floor {old} vs {new}")
    print(f"{len(retained)} runs validated; {len(named)} rerun on the CPU")


def expect_failure(action: Callable[[], Any], fragment: str) -> None:
    try:
        action()
    except SystemExit as reason:
        require(fragment in str(reason), f"self-test: failure {reason!s} lacks {fragment!r}")
        return
    raise SystemExit(f"self-test: expected a failure naming {fragment!r}")


def restricted(snapshot: dict[str, Any], qubits: list[int]) -> dict[str, Any]:
    """The snapshot on the named qubits alone, renumbered in their order, so a probe simulates them only."""
    index = {q: k for k, q in enumerate(qubits)}
    instructions = {
        name: [{**e, "qargs": [index[q] for q in e["qargs"]]} for e in entries if set(e["qargs"]) <= set(index)]
        for name, entries in snapshot["instructions"].items()
    }
    out = {**snapshot, "num_qubits": len(qubits), "qubits": [snapshot["qubits"][q] for q in qubits]}
    return {**out, "instructions": instructions}


def synthetic(snapshot: dict[str, Any]) -> tuple[QuantumCircuit, str, list[int]]:
    """A two-qubit dynamic circuit on a coupled pair, its synthetic schedule and the delays padding must give.

    Each timed operation starts at the latest replay clock of its qubits plus
    a planted gap; the expected delays are the per-qubit pads in circuit
    order, with the circuit's own delay in its place.
    """
    a, b = snapshot["instructions"]["cz"][0]["qargs"]
    durations = target_durations(snapshot)
    circuit = QuantumCircuit(snapshot["num_qubits"], 3, name="synthetic")
    circuit.sx(a)
    circuit.sx(b)
    circuit.cz(a, b)
    circuit.measure(a, 0)
    circuit.reset(a)
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.rz(0.3, b)
    circuit.delay(400, b, unit="dt")
    circuit.x(a)
    circuit.cz(a, b)
    circuit.sx(b)
    circuit.measure(b, 1)
    circuit.measure(a, 2)
    gaps = iter([0, 0, 30, 7, 900, 2000, 0, 12, 25, 3])
    rows = [f"main,INIT_{a},Qubit {a},0,64,play", "main,broadcast,Hub,10,500,broadcast"]
    rows.append(f"then,rz_{b},Qubit {b},5,0,shift_phase")
    clock: dict[int, int] = {}
    expected: list[int] = []
    for inst in circuit.data:
        name = inst.operation.name
        qubits = [circuit.find_bit(q).index for q in inst.qubits]
        if name == "delay":
            clock[b] += int(inst.operation.duration)
            expected.append(int(inst.operation.duration))
            continue
        if name not in TIMED:
            continue
        start = max(clock.get(q, 100) for q in qubits) + next(gaps)
        label = "_".join([name, *(str(q) for q in qubits)])
        for q in qubits:
            if q in clock and start > clock[q]:
                expected.append(start - clock[q])
            clock[q] = start + durations[name, tuple(qubits)]
            if name in ("measure", "reset"):
                rows.append(f"main,{label},Qubit {q},{start},64,play")
                rows.append(f"main,{label},Qubit {q},{start + 64},64,play")
                rows.append(f"main,{label},AWGR0_{q},{start + 70},200,capture")
            else:
                rows.append(f"main,{label},Qubit {q},{start},0,shift_phase")
                rows.append(f"main,{label},Qubit {q},{start},{durations[name, tuple(qubits)]},play")
    return circuit, "\n".join(rows), expected


def self_test() -> None:
    start = time.time()
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    for run_name in DEFAULT_RUNS:
        require(padding_summary(prepare(run_name, index))["delays"] > 0, f"self-test: {run_name} pads nothing")
    # A real PUB: a dropped row, a relabeled row and a pulse inside an
    # if_else block each break the match.
    run = ROOT / DYNAMIC_RUNS[2]
    prepared = ghost_run.prepare(DYNAMIC_RUNS[2], index)
    member, replica = next(
        (m, r)
        for m in prepared["members"]
        for r in prepared["replicas"][m][1]
        if any(inst.operation.name == "if_else" for inst in r.data)
    )
    record = json.loads((run / "record.json").read_text(encoding="utf-8"))
    rows = schedule_rows(pub_timings(run)[member_pubs(record)[member]])
    snapshot = json.loads((ROOT / prepared["execution"][member]).read_text(encoding="utf-8"))
    durations = target_durations(snapshot)
    pad(replica, rows, durations)
    qubit, k = next((q, i) for q, stream in rows.items() for i, r in enumerate(stream) if r[0].startswith("sx_"))
    dropped = {q: [r for i, r in enumerate(s) if (q, i) != (qubit, k)] for q, s in rows.items()}
    expect_failure(lambda: pad(replica, dropped, durations), replica.name)
    relabeled = {
        q: [("x" + r[0][2:], r[1], r[2]) if (q, i) == (qubit, k) else r for i, r in enumerate(s)]
        for q, s in rows.items()
    }
    expect_failure(lambda: pad(replica, relabeled, durations), "executed x_")
    branched = QuantumCircuit(*replica.qregs, *replica.cregs, name=replica.name)
    for inst in replica.data:
        if inst.operation.name == "if_else":
            body = inst.operation.blocks[0].copy()
            body.x(0)
            inst = inst.replace(operation=inst.operation.replace_blocks([body]))
        branched.append(inst)
    expect_failure(lambda: pad(branched, rows, durations), "outside the padding rule")
    # A synthetic schedule: the pads equal the planted gaps, and the
    # simulation laws of the module docstring hold.
    snapshot = restricted(snapshot, snapshot["instructions"]["cz"][0]["qargs"])
    durations = target_durations(snapshot)
    circuit, table, expected = synthetic(snapshot)
    padded, summary = pad(circuit, schedule_rows(table), durations)
    delays = [int(inst.operation.duration) for inst in padded.data if inst.operation.name == "delay"]
    require(delays == expected, f"self-test: delays {delays} differ from the planted {expected}")
    require(summary["pad_dt"] == sum(expected) - 400, "self-test: pad total differs")
    require(event_count(circuit) == 2, "self-test: the synthetic circuit carries a mid-circuit measure and a reset")
    simulator = calibration_snapshot.noise_simulator(ghost_error_scale.scaled(snapshot, 2.0, 1.0), "CPU")
    shots = [1000]
    unmodified = ghost_run.sample(simulator, [circuit], shots, SEED)[0]
    zero = ghost_run.sample(simulator, [with_events(circuit, 0.0)], shots, SEED)[0]
    require(zero == unmodified, "self-test: an inserted m = 0 channel changes the counts")
    require(
        ghost_run.sample(simulator, [with_events(circuit, 0.2)], shots, SEED)[0] != unmodified,
        "self-test: m = 0.2 leaves the counts unchanged",
    )
    require(ghost_run.sample(simulator, [padded], shots, SEED)[0] != unmodified, "self-test: padding changes nothing")
    # The sampler at padding off and m = 0 is the ghost_error_scale replay
    # at (c, 1): its draw reproduces the unmodified counts exactly.
    fake = {
        "measured": {"synthetic": [ghost_run.distribution(unmodified, circuit.num_clbits)]},
        "execution": {"synthetic": "synthetic"},
        "snapshots": {"synthetic": snapshot},
        "members": ["synthetic"],
        "replicas": {"synthetic": [circuit]},
        "padded": {"synthetic": [padded]},
        "shots": {"synthetic": shots[0]},
    }
    sampler = RunSampler(fake, "CPU", 1)
    require(sampler((False, 2.0, 0.0, False)) == {"synthetic": [0.0]}, "self-test: (c, 0) differs from the replay")
    items = [(False, 1.0, 0.1, False), (True, 1.0, 0.0, False), (True, 3.0, 0.05, True)]
    serial = [sampler(item) for item in items]
    require(parallel.ordered_map(sampler, items, min_items=1) == serial, "self-test: pooled grid differs")
    elapsed = time.time() - start
    print(f"ghost event scale self-test: {len(DEFAULT_RUNS)} runs padded, synthetic laws hold ({elapsed:.1f} s)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path, nargs="+", help="retained part files")
    parser.add_argument("--report", type=Path, nargs="+", help="print the fitted (c, m) of retained part files")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.report:
        print(json.dumps(report(args.report), indent=1))
        return 0
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    if args.check:
        check(args.check, args.runs, index)
        return 0
    require(args.out is not None, "--out is required")
    runs = list(DEFAULT_RUNS) if args.runs == "all" else args.runs.split(",")
    device = os.environ.get("GOROROBA_AER_DEVICE", "CPU")
    grid = full_grid()
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "device": device,
        "max_qubits": ghost_run.MAX_QUBITS,
        "seed": SEED,
        "grid": [list(p) for p in grid],
        "axes": {"pad": list(PADDING), "cz": list(CZ_FACTORS), "m": list(EVENT_ERRORS), "readout": READOUT_FACTOR},
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "workers": parallel.workers(),
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
