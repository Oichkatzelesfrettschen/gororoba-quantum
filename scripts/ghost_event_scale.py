"""Ghost event-scale sweep: scheduled idle, a per-event error and the CZ factor, fitted per run against hardware.

scripts/ghost_error_scale.py fits one CZ factor c and one readout factor r
per run; the dynamic-circuit runs (mid-circuit measurement, feed-forward and
reset) fit c = 5 to 6 while idle relaxation supplies about 2
(docs/evidence/ghost_error_scale/README.md). This sweep separates three error
sources on those runs, with the two static runs as controls, and carries the
readout factor r as a fourth axis:

1. Scheduled idle (``pad``). The replay simulates the unscheduled ISA
   circuit, so a qubit that waits stays ideal. With padding on, every replica
   carries explicit ``delay`` instructions that reproduce the executed idle
   gaps of its PUB's retained ``scheduler_timing`` table
   (raw/JOB/pub_NN.json metadata.compilation.scheduler_timing), and
   NoiseModel.from_backend relaxes each delay at the qubit's T1 and T2
   (RelaxationNoisePass, zero temperature).
2. A per-event assignment error m: an X flip of probability m on the
   measured qubit immediately before every mid-circuit measurement (a
   measure followed by a later non-barrier instruction on its qubit) and
   immediately after every reset. The flip before a measurement changes the
   outcome the circuit records and its feed-forward reads; in the retained
   runs the qubit is reset next (all but two measurements of
   2026-10-13T083417, whose qubit is measured again and keeps the flipped
   state), so the flip acts as an assignment error. A reset is a measurement
   followed by a conditional flip, so the flip after it is that internal
   assignment failing and leaving the qubit excited. m is therefore excess
   mid-circuit assignment error beyond the snapshot's readout flips, which
   the replay already applies to every measurement and which r scales. The
   flip is appended to the circuit as an Aer QuantumError instruction; in
   density-matrix mode it acts as a superoperator and draws no random
   number. A terminal measurement gets no flip, since r already covers its
   assignment.
3. The CZ factor c and the readout factor r, applied as
   ghost_error_scale.scaled does. A static control sweeps the full readout
   axis STATIC_READOUT; a dynamic run sweeps r = 1 and the factor the
   retained ghost_error_scale part fitted to it
   (docs/evidence/ghost_error_scale/part_*.json, bound by digest in the run's
   ``readout_fit``), since that fit, made at m = 0 without padding, may have
   absorbed per-event error into r.

Grid: padding off and on, then r, then c in CZ_FACTORS, then m in
EVENT_ERRORS. Every grid point samples every replica with the same seed
(ghost_run.sample, SEED), so shot noise is common along the grid; the point
(padding off, c 1, m 0, r 1) is the unmodified ghost replay. At m = 0 no
channel is inserted; the self-test requires an inserted zero-probability
channel to reproduce the unmodified replay's counts exactly under the same
seed. A static run has no event, so its circuits are identical across m and
its m = 0 column is computed once and copied to every m. At each padding
state's minimizing point a second draw under ghost_run.RESAMPLE_SEED gives
the resample floor (the two draws' distance) and the reseeded point's
distance to hardware.

Resolution. The minimum of 84 or more points that share one seed sits
inside model shot noise, so every reading uses a near-best set: the points
of a padding state whose mean lies within one resolution unit of its
minimum. The unit is the larger of one standard error of the difference of
two independent model draws, sqrt(2 mean(1/shots) / replicas), and the
observed shift of the minimum's mean under the reseeded draw.

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
distance of at most 1 in CZ_FACTORS between a point's c and some c of the
control's padded near-best set. Every reading uses padded near-best sets and
is three-valued: true when every point of the set satisfies it, false when
none does, and unresolved (null) when the set straddles it; over runs a
reading is true when every run's is, false when any run's is, and
unresolved otherwise.

- Registered first: if padding puts both static runs' c within one grid step
  of 1 while every dynamic run keeps c >= 4 at m = 0, idle relaxation is not
  the dynamic excess.
- Scheduled idle: every near-best point of a dynamic run has m = 0 and c
  within one grid step of its control.
- Per-event: every near-best point has m > 0 and c within one grid step of
  its control.
- Elsewhere: no near-best point has c within one grid step of its control.

Argmin ties resolve to the first grid point in grid order, so a static run's
best m is 0.

``--report FILE...`` gives per run and padding state the minimizing
(c, m, r), the best point at m = 0, the paired change from the anchor
(c 1, m 0, r 1) with the standard error clustered by executed PUB, the
resolution and the near-best set, the profile of each axis, a bootstrap over
PUBs of the minimizing point (BOOTSTRAP draws, the PUB count beside the
quantiles, and the fraction of draws at each axis's floor and top), the
resample floor and the uniform-distribution distance, then the readings.

``--check FILE...`` validates every run the files hold: members, shots,
execution snapshots, PUBs, event counts and padding are rebuilt from the
archived inputs and must match; the grid, coverage, means and floors must
follow from the retained distances; the (1, 0, padding off) means must agree
with docs/evidence/ghost_runs/result.json within five standard errors; the
readout axis and its fit must follow from the retained ghost_error_scale
parts. It then reruns the ``--runs`` subset (default every run the files
hold) on the CPU at the anchor and the top corner (c 6, m 0.2, largest r) of
each padding state and at each padding state's minimizing point and floor,
each within five standard errors.

``--pad off|on`` sweeps one padding state and ``--readout one|other`` the
readout factor 1 or the others, so one run's grid splits over up to four
kernels; --report and --check merge parts whose (padding, readout) states
partition the run's grid.

``--self-test`` runs on the CPU in well under a minute: it pads every replica
of every default run (parsing only), requires a dropped row, a relabeled row
and a pulse inside an if_else block to fail the match, and on a synthetic
two-qubit dynamic circuit with a synthetic schedule requires the computed
pads to equal the planted gaps, an inserted m = 0 channel to reproduce the
unmodified counts, the padding-off m = 0 point to equal the
ghost_error_scale path at (c, 1), padding, a nonzero m and r = 2 each to
change the counts, and the pooled grid to equal the serial one. On synthetic
records it requires parts split by padding and readout to merge into the
whole record, a missing or doubled part to fail, and the readings to follow
their definitions.

Kaggle. The full sweep runs on Kaggle CPU kernels; the retained runs come
from the gororoba-retained-runs dataset, kaggle_run bundles this script's
imports (ghost_error_scale, ghost_run, calibration_snapshot, packing,
parallel), and ``--include`` supplies the ghost_error_scale part that fits
each dynamic run. The pool maps the grid points over the kernel's CPUs with
one Aer thread each. A dynamic run costs 44 sampled points and one floor of
two draws per padding state and readout factor, a static run 14 points per
readout factor, each draw about the run's replicas times shots times
non-virtual operations, and a padded draw about 2.4 times an unpadded one.
One part per kernel:

    "$PYTHON" scripts/kaggle_run.py push scripts/ghost_event_scale.py \\
        --slug gororoba-ghost-event-scale-d1 --dataset gororoba-retained-runs \\
        --include docs/evidence/ghost_error_scale/part_b.json \\
        --machine cpu --timeout 43200 -- \\
        --runs results/live/2026-10-13T020454.599853Z \\
        --out results/kaggle_out/ghost_event_scale_d1.json

Usage:
    "$PYTHON" scripts/ghost_event_scale.py --runs RUN[,RUN] [--pad off|on] [--readout one|other] --out FILE
    "$PYTHON" scripts/ghost_event_scale.py --report FILE...
    "$PYTHON" scripts/ghost_event_scale.py --check FILE... [--runs RUN[,RUN]]
    "$PYTHON" scripts/ghost_event_scale.py --self-test
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
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
from qiskit_aer.noise import pauli_error  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "ghost-event-scale-v2"
CZ_FACTORS = (1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0)
EVENT_ERRORS = (0.0, 0.01, 0.02, 0.05, 0.1, 0.2)
PADDING = (False, True)
STATIC_READOUT = ghost_error_scale.READOUT_FACTORS
ERROR_SCALE_PARTS = ROOT / "docs/evidence/ghost_error_scale"
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

Point = tuple[bool, float, float, float]
Row = tuple[str, int, int]


def axes() -> dict[str, Any]:
    return {"pad": list(PADDING), "cz": list(CZ_FACTORS), "m": list(EVENT_ERRORS), "static_r": list(STATIC_READOUT)}


def readout_fits() -> dict[str, Any]:
    """Each run's minimizing readout factor in the retained ghost_error_scale parts, with its part's digest.

    The minimum is ghost_error_scale --report's ``best``: the first grid point
    of least mean TV distance over (c, r). A run's record binds the one part
    that fits it, so a part added later leaves earlier records valid.
    """
    grid = ghost_error_scale.full_grid()
    fitted = {}
    for path in sorted(ERROR_SCALE_PARTS.glob("part_*.json")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for run in ghost_error_scale.load([path])["runs"]:
            if "skipped" not in run:
                require(run["run"] not in fitted, f"{run['run']}: two ghost_error_scale parts fit it")
                r = grid[int(np.argmin(run["mean_tvd"]))][1]
                fitted[run["run"]] = {"r": r, "source": path.relative_to(ROOT).as_posix(), "sha256": digest}
    return fitted


def readout_fit(run_name: str, fits: dict[str, Any]) -> dict[str, Any] | None:
    return None if run_name in STATIC_RUNS else fits[run_name]


def readout_axis(run_name: str, fits: dict[str, Any]) -> tuple[float, ...]:
    """The run's readout factors: the full static axis on a control, 1 and the fitted factor on a dynamic run."""
    if run_name in STATIC_RUNS:
        return tuple(STATIC_READOUT)
    require(run_name in fits, f"{run_name}: no retained ghost_error_scale part fits its readout factor")
    return tuple(sorted({1.0, fits[run_name]["r"]}))


def run_grid(axis: tuple[float, ...]) -> list[Point]:
    """Grid order: padding, then readout, then c, then m, so ties go to the lower factors."""
    return [(pad, c, m, r) for pad in PADDING for r in axis for c in CZ_FACTORS for m in EVENT_ERRORS]


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
    """The circuit with an X flip of the given probability before each mid-circuit measure and after each reset."""
    positions = dict(event_positions(circuit))
    out = QuantumCircuit(*circuit.qregs, *circuit.cregs, name=circuit.name)
    error = pauli_error([("X", probability), ("I", 1.0 - probability)])
    for position, inst in enumerate(circuit.data):
        event = positions.get(position)
        if event is not None and inst.operation.name == "measure":
            out.append(error, [circuit.qubits[event]])
        out.append(inst)
        if event is not None and inst.operation.name == "reset":
            out.append(error, [circuit.qubits[event]])
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
        self.members = prepared["members"]
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

    def simulator(self, snapshot: dict[str, Any], cz: float, readout: float) -> Any:
        simulator = calibration_snapshot.noise_simulator(ghost_error_scale.scaled(snapshot, cz, readout), self.device)
        simulator.set_options(max_parallel_threads=self.threads)
        return simulator

    def __call__(self, item: tuple[bool, float, float, float, bool]) -> dict[str, dict[str, list[float]]]:
        """Per member, each replica's TV distance to hardware; with floor set, also the second draw's.

        The floor item returns ``tvd`` (first draw against hardware),
        ``floor_tvd`` (first draw against the RESAMPLE_SEED draw) and
        ``resample_tvd`` (that second draw against hardware).
        """
        padded, cz, event, readout, floor = item
        out: dict[str, dict[str, list[float]]] = {"tvd": {}}
        if floor:
            out |= {"floor_tvd": {}, "resample_tvd": {}}
        for snapshot, chosen, circuits, shots, widths in self.groups:
            batch = [with_events(c, event) if event else c for c in circuits[padded]]
            simulator = self.simulator(snapshot, cz, readout)
            first = iter(ghost_run.sample(simulator, batch, shots, SEED))
            second = iter(ghost_run.sample(simulator, batch, shots, ghost_run.RESAMPLE_SEED)) if floor else None
            position = iter(batch)
            for m, width in zip(chosen, widths, strict=True):
                rows: dict[str, list[float]] = {key: [] for key in out}
                for k in range(width):
                    clbits = next(position).num_clbits
                    model = ghost_run.distribution(next(first), clbits)
                    hardware = self.measured[m][k]
                    rows["tvd"].append(round(ghost_run.tv(hardware, model), 6))
                    if second is not None:
                        other = ghost_run.distribution(next(second), clbits)
                        rows["floor_tvd"].append(round(ghost_run.tv(other, model), 6))
                        rows["resample_tvd"].append(round(ghost_run.tv(hardware, other), 6))
                for key, row in rows.items():
                    out[key][m] = row
        # Groups follow execution snapshots; the record keys members in plan order.
        return {key: {m: rows_by[m] for m in self.members} for key, rows_by in out.items()}


class TimedSampler:
    """A RunSampler call and its wall seconds, which size the Kaggle split."""

    def __init__(self, sampler: RunSampler) -> None:
        self.sampler = sampler

    def __call__(self, item: tuple[bool, float, float, float, bool]) -> tuple[dict[str, Any], float]:
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


def mean_of(rows: dict[str, list[float]]) -> float:
    return round(float(np.mean([v for row in rows.values() for v in row])), 6)


def sweep_run(
    run_name: str,
    device: str,
    index: dict[str, Any],
    states: list[tuple[bool, float]],
    fits: dict[str, Any],
    floors: dict[bool, Point] | None = None,
    points_only: list[Point] | None = None,
) -> dict[str, Any]:
    """The run's TV distances over the named (padding, readout) states and a resample floor per padding state.

    The floor of a padding state is drawn at that state's minimizing point
    over the swept states, or at ``floors`` when given; ``points_only``
    restricts the sampled points (``--check``).
    """
    start = time.time()
    prepared = prepare(run_name, index)
    members = prepared["members"]
    event_free = all(n == 0 for m in members for n in prepared["events"][m])
    axis = readout_axis(run_name, fits)
    grid = [p for p in run_grid(axis) if (p[0], p[3]) in states]
    if points_only is not None:
        grid = [p for p in grid if p in points_only]
    # An event-free run's circuits are identical across m, so one m = 0
    # draw per (padding, c, r) stands for every m under the common seed.
    sampled = sorted({(pad, c, 0.0 if event_free else m, r) for pad, c, m, r in grid}, key=run_grid(axis).index)
    sampler = TimedSampler(RunSampler(prepared, device, aer_threads(len(sampled))))
    values = parallel.ordered_map(sampler, [(*point, False) for point in sampled], min_items=1)
    by_point = {point: result["tvd"] for point, (result, _) in zip(sampled, values, strict=True)}
    seconds = [[*point, elapsed] for point, (_, elapsed) in zip(sampled, values, strict=True)]
    points = [
        {"pad": pad, "cz": c, "m": m, "r": r, "tvd": by_point[pad, c, 0.0 if event_free else m, r]}
        for pad, c, m, r in grid
    ]
    means = ghost_error_scale.grid_means(points, members)
    chosen: dict[bool, Point] = {}
    for padded in PADDING:
        if floors is not None:
            if padded in floors:
                chosen[padded] = floors[padded]
            continue
        own = [j for j, p in enumerate(points) if p["pad"] == padded]
        if own:
            best = min(own, key=lambda j: (means[j], j))
            chosen[padded] = point_of(points[best])
    floor_values = parallel.ordered_map(sampler, [(*point, True) for point in chosen.values()], min_items=1)
    floor_rows = []
    for (pad, c, m, r), (result, elapsed) in zip(chosen.values(), floor_values, strict=True):
        seconds.append([pad, c, m, r, elapsed])
        floor_rows.append(
            {
                "pad": pad,
                "cz": c,
                "m": m,
                "r": r,
                "floor_tvd": result["floor_tvd"],
                "mean_floor_tvd": mean_of(result["floor_tvd"]),
                "resample_tvd": result["resample_tvd"],
                "mean_resample_tvd": mean_of(result["resample_tvd"]),
            }
        )
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
        "readout_axis": list(axis),
        "readout_fit": readout_fit(run_name, fits),
        "states": [list(s) for s in sorted(set(states))],
        "points": points,
        "mean_tvd": means,
        "floors": floor_rows,
        # Wall seconds of each sampled point, then of each floor's two draws.
        "draw_seconds": seconds,
        "seconds": round(time.time() - start, 1),
    }
    if points_only is None:
        print(json.dumps({"run": run_name, "seconds": out["seconds"], "floors": chosen}), flush=True)
    return out


def point_of(point: dict[str, Any]) -> Point:
    return (point["pad"], point["cz"], point["m"], point["r"])


def step(c: float) -> int:
    return CZ_FACTORS.index(c)


# Fields that one part of a run carries for its own (padding, readout)
# states; every other field of a run's parts must agree.
PER_STATE = ("states", "points", "mean_tvd", "floors", "draw_seconds", "seconds")


def merge(name: str, parts: list[dict[str, Any]]) -> dict[str, Any]:
    """One run's record from parts whose (padding, readout) states partition the run's grid.

    A part's floor sits at its padding state's minimizing point over the
    part's states; the merged floor of a padding state is the part floor at
    the merged minimum, which is that part's own minimum, since points keep
    the run grid's order and ties go to the first point.
    """
    first = parts[0]
    shared = set(first) - set(PER_STATE)
    for part in parts[1:]:
        require(set(part) - set(PER_STATE) == shared, f"{name}: the parts carry different fields")
        require(all(part[key] == first[key] for key in shared), f"{name}: the parts disagree outside their states")
    states = [tuple(s) for part in parts for s in part["states"]]
    require(len(states) == len(set(states)), f"{name}: two parts sweep one (padding, readout) state")
    axis = tuple(first["readout_axis"])
    grid = run_grid(axis)
    require(set(states) == {(pad, r) for pad in PADDING for r in axis}, f"{name}: the parts leave states unswept")
    points = sorted((p for part in parts for p in part["points"]), key=lambda p: grid.index(point_of(p)))
    require([point_of(p) for p in points] == grid, f"{name}: the parts' points differ from the run grid")
    merged = {key: first[key] for key in shared}
    run = merged | {
        "states": [list(s) for s in sorted(states)],
        "points": points,
        "mean_tvd": ghost_error_scale.grid_means(points, first["members"]),
        "draw_seconds": [row for part in parts for row in part["draw_seconds"]],
        "seconds": round(sum(part["seconds"] for part in parts), 1),
    }
    floors = []
    for padded in PADDING:
        best = point_of(points[best_index(run, padded)])
        at = [row for part in parts for row in part["floors"] if point_of(row) == best]
        require(len(at) == 1, f"{name}: no part floor sits at the {'padded' if padded else 'unpadded'} minimum")
        floors.append(at[0])
    return run | {"floors": floors}


def load(paths: list[Path]) -> list[dict[str, Any]]:
    """The runs of every part file, which must share the schema and the module's axes."""
    parts: dict[str, list[dict[str, Any]]] = {}
    for path in paths:
        part = json.loads(path.read_text(encoding="utf-8"))
        require(part["schema"] == SCHEMA, f"{path}: schema must be {SCHEMA}")
        require(part["axes"] == axes(), f"{path}: axes differ from the module's")
        for run in part["runs"]:
            parts.setdefault(run["run"], []).append(run)
    return [merge(name, rows) for name, rows in parts.items()]


def best_index(run: dict[str, Any], padded: bool, event: float | None = None) -> int:
    """The minimizing point of one padding state, optionally at one m; ties go to the first point."""
    own = [j for j, p in enumerate(run["points"]) if p["pad"] == padded and (event is None or p["m"] == event)]
    return min(own, key=lambda j: (run["mean_tvd"][j], j))


def floor_at(run: dict[str, Any], padded: bool) -> dict[str, Any]:
    return next(row for row in run["floors"] if row["pad"] == padded)


def resolution(run: dict[str, Any], padded: bool) -> float:
    """The mean-TV difference the grid cannot resolve: the larger of the analytic and the observed reseed shift.

    The analytic term is one standard error of the difference of two
    independent model draws, sqrt(2 mean(1/shots) / replicas), the unit
    ghost_run --check bounds at five; the observed term is the shift of the
    minimizing point's mean when its model draw is replaced by the
    RESAMPLE_SEED draw.
    """
    replicas = [(m, k) for m in run["members"] for k in range(len(run["points"][0]["tvd"][m]))]
    inverse_shots = float(np.mean([1 / run["member_shots"][m] for m, _ in replicas]))
    analytic = math.sqrt(2.0 * inverse_shots / len(replicas))
    floor = floor_at(run, padded)
    observed = abs(floor["mean_resample_tvd"] - run["mean_tvd"][best_index(run, padded)])
    return round(max(analytic, observed), 6)


def near_best(run: dict[str, Any], padded: bool) -> list[int]:
    """Points of one padding state whose mean lies within the resolution of its minimum, in grid order."""
    best = run["mean_tvd"][best_index(run, padded)]
    bound = best + resolution(run, padded)
    return [j for j, p in enumerate(run["points"]) if p["pad"] == padded and run["mean_tvd"][j] <= bound]


def bootstrap(run: dict[str, Any], padded: bool) -> dict[str, Any]:
    """PUB bootstrap of the minimizing (c, m, r) of one padding state, seeded by the run name."""
    pubs, sums, counts = ghost_error_scale.pub_sums(run)
    own = [j for j, p in enumerate(run["points"]) if p["pad"] == padded]
    rng = np.random.default_rng(int(hashlib.sha256(run["run"].encode()).hexdigest()[:8], 16))
    draws = rng.integers(0, len(pubs), size=(BOOTSTRAP, len(pubs)))
    means = sums[draws][:, :, own].sum(axis=1) / counts[draws].sum(axis=1)[:, None]
    picks = [own[j] for j in np.argmin(means, axis=1)]
    axes_drawn = {key: np.array([run["points"][j][key] for j in picks]) for key in ("cz", "m", "r")}

    def quantiles(values: np.ndarray) -> list[float]:
        return [float(np.quantile(values, q, method="inverted_cdf")) for q in (0.16, 0.5, 0.84)]

    return {
        "draws": BOOTSTRAP,
        "pubs": len(pubs),
        **{f"{key}_quantiles_16_50_84": quantiles(values) for key, values in axes_drawn.items()},
        "cz_at_floor": round(float(np.mean(axes_drawn["cz"] == CZ_FACTORS[0])), 4),
        "cz_at_top": round(float(np.mean(axes_drawn["cz"] == CZ_FACTORS[-1])), 4),
        "m_at_floor": round(float(np.mean(axes_drawn["m"] == EVENT_ERRORS[0])), 4),
        "m_at_top": round(float(np.mean(axes_drawn["m"] == EVENT_ERRORS[-1])), 4),
    }


def state_report(run: dict[str, Any], padded: bool) -> dict[str, Any]:
    points, means = run["points"], run["mean_tvd"]
    anchor = run_grid(tuple(run["readout_axis"])).index((padded, 1.0, 0.0, 1.0))
    best = best_index(run, padded)
    at_zero = best_index(run, padded, 0.0)
    floor = floor_at(run, padded)
    own = [j for j, p in enumerate(points) if p["pad"] == padded]

    def profile(key: str, values: list[float]) -> dict[str, float]:
        return {str(v): min(means[j] for j in own if points[j][key] == v) for v in values}

    return {
        "mean_tvd_at_anchor": means[anchor],
        "best": {**{key: points[best][key] for key in ("cz", "m", "r")}, "mean_tvd": means[best]},
        "best_at_m0": {"cz": points[at_zero]["cz"], "r": points[at_zero]["r"], "mean_tvd": means[at_zero]},
        "best_minus_anchor": ghost_error_scale.clustered_delta(run, best, anchor),
        "resolution": resolution(run, padded),
        "near_best": [
            {key: points[j][key] for key in ("cz", "m", "r")} | {"mean_tvd": means[j]} for j in near_best(run, padded)
        ],
        "cz_profile": profile("cz", list(CZ_FACTORS)),
        "m_profile": profile("m", list(EVENT_ERRORS)),
        "r_profile": profile("r", run["readout_axis"]),
        "resample_floor": {
            "mean_floor_tvd": floor["mean_floor_tvd"],
            "mean_resample_tvd": floor["mean_resample_tvd"],
        },
        "bootstrap": bootstrap(run, padded),
    }


def every(values: list[bool]) -> bool | None:
    """True when every value holds, False when none does, None when the near-best set straddles the test."""
    if all(values):
        return True
    return False if not any(values) else None


def combine(readings: list[bool | None]) -> bool | None:
    """A reading over runs: True when every run's holds, False when any run's fails, else unresolved."""
    if any(v is False for v in readings):
        return False
    return True if all(v is True for v in readings) else None


def verdicts(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """The falsifier readings of the module docstring, read on each run's padded near-best set."""
    by_run = {run["run"]: run for run in runs}
    static = [by_run[r] for r in STATIC_RUNS if r in by_run]
    dynamic = [by_run[r] for r in DYNAMIC_RUNS if r in by_run]
    complete = len(static) == len(STATIC_RUNS) and len(dynamic) == len(DYNAMIC_RUNS)

    def near(run: dict[str, Any]) -> list[dict[str, Any]]:
        return [run["points"][j] for j in near_best(run, True)]

    def near_m0(run: dict[str, Any]) -> list[dict[str, Any]]:
        best = run["mean_tvd"][best_index(run, True, 0.0)]
        bound = best + resolution(run, True)
        return [p for j, p in enumerate(run["points"]) if p["pad"] and p["m"] == 0 and run["mean_tvd"][j] <= bound]

    control_steps = {run["run"]: {step(p["cz"]) for p in near(run)} for run in static}

    def close(point: dict[str, Any], control: str) -> bool:
        return min(abs(step(point["cz"]) - s) for s in control_steps[control]) <= 1

    static_near_1 = {run["run"]: every([step(p["cz"]) <= 1 for p in near(run)]) for run in static}
    dynamic_ge_4 = {run["run"]: every([p["cz"] >= 4.0 for p in near_m0(run)]) for run in dynamic}
    readings: dict[str, dict[str, bool | None]] = {}
    for run in dynamic:
        if run["control"] not in control_steps:
            continue
        points = near(run)
        readings[run["run"]] = {
            "idle": every([p["m"] == 0 and close(p, run["control"]) for p in points]),
            "per_event": every([p["m"] > 0 and close(p, run["control"]) for p in points]),
            "elsewhere": every([not close(p, run["control"]) for p in points]),
        }
    covered = complete and len(readings) == len(dynamic)

    def overall(key: str) -> bool | None:
        return combine([row[key] for row in readings.values()]) if covered else None

    return {
        "complete": covered,
        "static_best_cz_within_one_step_of_1": static_near_1,
        "dynamic_best_cz_at_m0_at_least_4": dynamic_ge_4,
        "dynamic_readings": readings,
        "idle_relaxation_not_the_dynamic_excess": (
            combine(list(static_near_1.values()) + list(dynamic_ge_4.values())) if complete else None
        ),
        "excess_from_scheduled_idle": overall("idle"),
        "excess_per_event": overall("per_event"),
        "excess_elsewhere": overall("elsewhere"),
    }


def report(paths: list[Path]) -> dict[str, Any]:
    runs = load(paths)
    rows = [
        {
            "run": run["run"],
            "backend": run["backend"],
            "control": run["control"],
            "members": len(run["members"]),
            "events": sum(n for row in run["events"].values() for n in row),
            "padding_total": run["padding_total"],
            "readout_axis": run["readout_axis"],
            "uniform_mean_tvd": ghost_error_scale.uniform_tvd(run),
            "unpadded": state_report(run, False),
            "padded": state_report(run, True),
        }
        for run in runs
    ]
    return {
        "schema": "ghost-event-scale-report-v2",
        "sources": [path.as_posix() for path in paths],
        "axes": axes(),
        "runs": rows,
        "verdicts": verdicts(runs),
    }


def validate(run: dict[str, Any], index: dict[str, Any], fits: dict[str, Any]) -> dict[str, Any]:
    """Require every field the archived inputs and the retained distances determine; return the rebuild."""
    name = run["run"]
    prepared = prepare(name, index)
    members = prepared["members"]
    grid = run_grid(readout_axis(name, fits))
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
        ("readout_axis", list(readout_axis(name, fits))),
        ("readout_fit", readout_fit(name, fits)),
    ):
        require(run[key] == value, f"{name}: {key} differs from the archived inputs")
    event_free = all(n == 0 for m in members for n in prepared["events"][m])
    require(run["event_free"] == event_free, f"{name}: event_free differs")
    require([point_of(p) for p in run["points"]] == grid, f"{name}: grid differs")
    for point in run["points"]:
        require(list(point["tvd"]) == members, f"{name}: {point_of(point)} coverage")
        for m, row in point["tvd"].items():
            require(len(row) == len(prepared["replicas"][m]), f"{name}: {m} replica count")
        if event_free:
            twin = run["points"][grid.index((point["pad"], point["cz"], 0.0, point["r"]))]
            require(point["tvd"] == twin["tvd"], f"{name}: an event-free run's distances differ across m")
    require(run["mean_tvd"] == ghost_error_scale.grid_means(run["points"], members), f"{name}: means differ")
    for padded in PADDING:
        floor = floor_at(run, padded)
        require(point_of(floor) == point_of(run["points"][best_index(run, padded)]), f"{name}: floor off the minimum")
        for key in ("floor_tvd", "resample_tvd"):
            require(list(floor[key]) == members, f"{name}: floor {key} coverage")
            require(floor[f"mean_{key}"] == mean_of(floor[key]), f"{name}: floor {key} mean differs")
    return prepared


def check(paths: list[Path], runs: str, index: dict[str, Any]) -> None:
    retained = load(paths)
    fits = readout_fits()
    ghosts = {r["run"]: r for r in json.loads(ghost_error_scale.GHOST_RESULT.read_text(encoding="utf-8"))["runs"]}
    for run in retained:
        validate(run, index, fits)
        # The anchor (padding off, c 1, m 0, r 1) is the unmodified replay,
        # so its execution means agree with the ghost runs' execution means.
        anchor = run_grid(tuple(run["readout_axis"])).index((False, 1.0, 0.0, 1.0))
        for relative in sorted(set(run["execution_snapshot"].values())):
            own = [m for m in run["members"] if run["execution_snapshot"][m] == relative]
            mine = float(np.mean([v for m in own for v in run["points"][anchor]["tvd"][m]]))
            theirs = ghosts[run["run"]]["summary"][relative]["execution_mean_tvd"]
            bound = ghost_error_scale.tolerance(run, own)
            require(abs(mine - theirs) <= bound, f"{run['run']}: anchor {mine} vs ghost {theirs}")
    named = [r["run"] for r in retained] if runs == "all" else runs.split(",")
    held = {r["run"]: r for r in retained}
    require(all(n in held for n in named), "--runs names a run the files lack")
    for name in named:
        run = held[name]
        axis = tuple(run["readout_axis"])
        floors = {p: point_of(floor_at(run, p)) for p in PADDING}
        picks = {(p, 1.0, 0.0, 1.0) for p in PADDING} | {
            (p, CZ_FACTORS[-1], EVENT_ERRORS[-1], axis[-1]) for p in PADDING
        }
        picks |= set(floors.values())
        states = sorted({(p[0], p[3]) for p in picks})
        fresh = sweep_run(name, "CPU", index, states, fits, floors, sorted(picks, key=run_grid(axis).index))
        bound = ghost_error_scale.tolerance(run, run["members"])
        grid = run_grid(axis)
        for point, mean in zip(fresh["points"], fresh["mean_tvd"], strict=True):
            old = run["mean_tvd"][grid.index(point_of(point))]
            require(abs(old - mean) <= bound, f"{name}: {point_of(point)} {old} vs {mean}")
        for padded in PADDING:
            old_floor, new_floor = floor_at(run, padded), floor_at(fresh, padded)
            for key in ("mean_floor_tvd", "mean_resample_tvd"):
                require(abs(old_floor[key] - new_floor[key]) <= bound, f"{name}: {padded} {key} differs")
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


def synthetic_run(name: str, axis: tuple[float, ...], best: Point, control: str | None) -> dict[str, Any]:
    """A run record over the full grid of the axis with mean TV 0.1 everywhere except 0.01 at ``best``."""
    grid = run_grid(axis)
    points = [
        {"pad": p[0], "cz": p[1], "m": p[2], "r": p[3], "tvd": {"x": [0.01 if p[1:] == best[1:] else 0.1]}}
        for p in grid
    ]
    run: dict[str, Any] = {
        "run": name,
        "control": control,
        "members": ["x"],
        "member_shots": {"x": 8192},
        "readout_axis": list(axis),
    }
    run |= {"states": [[pad, r] for pad in PADDING for r in axis], "points": points, "draw_seconds": [], "seconds": 1.0}
    run["mean_tvd"] = ghost_error_scale.grid_means(points, ["x"])
    run["floors"] = []
    for padded in PADDING:
        at = point_of(points[best_index(run, padded)])
        floor = {"pad": at[0], "cz": at[1], "m": at[2], "r": at[3], "floor_tvd": {"x": [0.01]}, "mean_floor_tvd": 0.01}
        run["floors"].append(floor | {"resample_tvd": {"x": [0.01]}, "mean_resample_tvd": 0.01})
    return run


def record_laws() -> None:
    """Parts split by padding and readout merge into the full record; the verdicts read the near-best sets."""
    axis = (1.0, 2.0)
    whole = synthetic_run("synthetic", axis, (True, 3.0, 0.05, 2.0), None)
    parts = []
    for pad in PADDING:
        for r in axis:
            own = [j for j, p in enumerate(whole["points"]) if (p["pad"], p["r"]) == (pad, r)]
            part = {k: v for k, v in whole.items() if k not in PER_STATE}
            part |= {
                "states": [[pad, r]],
                "points": [whole["points"][j] for j in own],
                "draw_seconds": [],
                "seconds": 0.25,
            }
            part["mean_tvd"] = [whole["mean_tvd"][j] for j in own]
            sub = part | {"floors": []}
            for padded in PADDING:
                if padded == pad:
                    at = point_of(part["points"][min(range(len(own)), key=lambda j: (part["mean_tvd"][j], j))])
                    row = {"pad": at[0], "cz": at[1], "m": at[2], "r": at[3], "floor_tvd": {"x": [0.01]}}
                    sub["floors"].append(
                        row | {"mean_floor_tvd": 0.01, "resample_tvd": {"x": [0.01]}, "mean_resample_tvd": 0.01}
                    )
            parts.append(sub)
    merged = merge("synthetic", parts)
    require(
        {k: merged[k] for k in whole if k != "seconds"} == {k: whole[k] for k in whole if k != "seconds"},
        "self-test: merge",
    )
    expect_failure(lambda: merge("synthetic", parts[:3]), "unswept")
    expect_failure(lambda: merge("synthetic", [*parts, parts[0]]), "two parts")
    require(near_best(whole, True) == [run_grid(axis).index((True, 3.0, 0.05, 2.0))], "self-test: near-best set")
    # Static controls at c = 1 and every dynamic run at c = 1.5 with m > 0
    # give the per-event reading; moving one dynamic run to c = 5 at m = 0
    # turns it false and the registered first falsifier true for that run.
    runs = [synthetic_run(name, STATIC_READOUT, (True, 1.0, 0.0, 1.0), None) for name in STATIC_RUNS]
    runs += [synthetic_run(name, (1.0,), (True, 1.5, 0.05, 1.0), STATIC_RUNS[0]) for name in DYNAMIC_RUNS]
    reading = verdicts(runs)
    require(reading["complete"] and reading["excess_per_event"] is True, f"self-test: per-event reading {reading}")
    require(reading["excess_from_scheduled_idle"] is False and reading["excess_elsewhere"] is False, "self-test: idle")
    runs[-1] = synthetic_run(DYNAMIC_RUNS[-1], (1.0,), (True, 5.0, 0.0, 1.0), STATIC_RUNS[0])
    reading = verdicts(runs)
    require(reading["excess_per_event"] is False, "self-test: a dynamic run at c = 5 keeps the per-event reading")
    require(reading["dynamic_best_cz_at_m0_at_least_4"][DYNAMIC_RUNS[-1]] is True, "self-test: m = 0 test")


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
    # On an ideal measure, reset, measure circuit a certain flip reports 1
    # from the mid-circuit measure and leaves the reset qubit excited.
    probe = QuantumCircuit(1, 2)
    probe.measure(0, 0)
    probe.reset(0)
    probe.measure(0, 1)
    ideal = qiskit_aer.AerSimulator(method="density_matrix")
    require(ideal.run(probe, shots=64, seed_simulator=SEED).result().get_counts() == {"00": 64}, "self-test: probe")
    flipped = ideal.run(with_events(probe, 1.0), shots=64, seed_simulator=SEED).result().get_counts()
    require(flipped == {"11": 64}, f"self-test: a certain event flip gives {flipped}, not 11 on every shot")
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
    require(
        sampler((False, 2.0, 0.0, 1.0, False)) == {"tvd": {"synthetic": [0.0]}},
        "self-test: (c, 0, 1) differs from the replay",
    )
    require(sampler((False, 2.0, 0.0, 2.0, False)) != {"tvd": {"synthetic": [0.0]}}, "self-test: r = 2 changes nothing")
    items = [(False, 1.0, 0.1, 1.0, False), (True, 1.0, 0.0, 1.5, False), (True, 3.0, 0.05, 1.0, True)]
    serial = [sampler(item) for item in items]
    require(parallel.ordered_map(sampler, items, min_items=1) == serial, "self-test: pooled grid differs")
    record_laws()
    elapsed = time.time() - start
    print(f"ghost event scale self-test: {len(DEFAULT_RUNS)} runs padded, synthetic laws hold ({elapsed:.1f} s)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path, nargs="+", help="retained part files")
    parser.add_argument("--report", type=Path, nargs="+", help="print the fitted (c, m) of retained part files")
    parser.add_argument("--pad", choices=("both", "off", "on"), default="both", help="padding states to sweep")
    parser.add_argument(
        "--readout",
        choices=("all", "one", "other"),
        default="all",
        help="readout factors to sweep: all, 1, or all but 1",
    )
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
    device = calibration_snapshot.aer_device()
    fits = readout_fits()
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "device": device,
        "max_qubits": ghost_run.MAX_QUBITS,
        "seed": SEED,
        "axes": axes(),
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "workers": parallel.workers(),
        "runs": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    pads = {"both": PADDING, "off": (False,), "on": (True,)}[args.pad]
    for run in runs:
        axis = readout_axis(run, fits)
        factors = {"all": axis, "one": (1.0,), "other": tuple(r for r in axis if r != 1.0)}[args.readout]
        require(bool(factors), f"{run}: --readout {args.readout} leaves no readout factor")
        states = [(pad, r) for pad in pads for r in factors]
        # Written after every run, so a failure keeps every finished one.
        out["runs"].append(sweep_run(run, device, index, states, fits))
        args.out.write_text(json.dumps(out) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
