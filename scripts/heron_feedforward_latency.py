"""Feed-forward latency of the Heron r2 account devices, read from retained compiled schedules.

A dynamic PUB collected with ``execution.scheduler_timing`` carries the service's compiled schedule in
``metadata.compilation.scheduler_timing.timing``: one row ``branch,instruction,channel,t0,duration,kind``
per instruction, times in scheduling cycles of the backend ``dt``
(docs/notes/ibm_quantum/qiskit-runtime-circuit-timing.md). A mid-circuit measurement whose outcome a
branch reads plays its pulses on ``Qubit q``, captures on ``AWGRx_q``, and the ``Hub`` channel broadcasts
the outcome from the capture start; the ``Receive`` instruction marks its arrival, after which the
``then``/``else`` rows play.

Every broadcast row of every retained ``results/live/*/raw/<job>/pub_NN.json`` yields, in cycles:
the measure play start, the capture start and length, the broadcast length, the receive start and
length, the latency from capture end to receive start, and the number of captures the broadcast carries.
The schedule names no branch condition, so no branch row is attributed to a broadcast.
The backend comes from the run's collect.json job table or, for
a retrospective retrieval, its retention.json; the backend version comes from record.json where the run
recorded one. The cycle length is bound to the retained Target snapshot
(docs/evidence/heron_platform/targets.json): its ``dt`` must be a whole number of nanoseconds and every
scheduled ``sx`` play must last the Target ``sx`` duration divided by ``dt``.

The values are the scheduler's plan, device-matched but not timed on the device, so they carry no jitter.
Each PUB file's extraction is independent and runs through parallel.ordered_map. ``--out`` writes the
integer-only JSON record with the sha256 of every consumed file over every retained PUB; ``--check``
verifies those digests, recomputes the record from the PUB files it names and compares bytes; ``--self-test``
exercises the extraction on synthetic schedules.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402

SCHEMA = "heron-feedforward-latency-v2"
OUTPUT = Path("docs/evidence/heron_platform/feedforward-latency.json")
TARGETS = Path("docs/evidence/heron_platform/targets.json")
LIVE = Path("results/live")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_rows(timing: str) -> list[tuple[str, str, str, int, int, str]]:
    rows = []
    for line in timing.splitlines():
        fields = line.split(",")
        require(len(fields) == 6, f"schedule row has {len(fields)} fields: {line!r}")
        rows.append((fields[0], fields[1], fields[2], int(fields[3]), int(fields[4]), fields[5]))
    return rows


def broadcasts(timing: str) -> list[dict[str, int]]:
    """One entry per Hub broadcast, anchored on the captures that start with it.

    A broadcast carries the outcome bits of every capture that starts at its own start; the schedule
    names no condition, so the record counts those captures and attributes no branch row to a broadcast.
    """
    rows = parse_rows(timing)
    captures: dict[int, list[tuple[str, str, str, int, int, str]]] = {}
    for row in rows:
        if row[5] == "capture" and row[0] == "main" and not row[1].startswith(("INIT", "FINI")):
            captures.setdefault(row[3], []).append(row)
    receives = sorted(row[3] for row in rows if row[1] == "receive")
    out = []
    for row in rows:
        if row[1] != "broadcast":
            continue
        start = row[3]
        require(start in captures, f"broadcast at {start} has no capture starting with it")
        lengths = {capture[4] for capture in captures[start]}
        require(len(lengths) == 1, f"captures starting at {start} differ in length: {sorted(lengths)}")
        capture = min(captures[start], key=lambda c: c[1])
        # The measurement instance is the run of back-to-back plays ending with the last one that starts by the
        # capture; an earlier measurement of the same qubit is separated from it by a gap.
        plays = sorted(
            (
                (r[3], r[4])
                for r in rows
                if r[1] == capture[1] and r[2].startswith("Qubit") and r[5] == "play" and r[3] <= start
            ),
            reverse=True,
        )
        require(bool(plays), f"capture {capture[1]} at {start} has no preceding measure play")
        first = plays[0][0]
        for t0, duration in plays[1:]:
            if t0 + duration != first:
                break
            first = t0
        later = [t for t in receives if t >= start]
        require(bool(later), f"broadcast at {start} has no receive")
        receive = later[0]
        receive_row = next(r for r in rows if r[1] == "receive" and r[3] == receive)
        out.append(
            {
                "measure_start": first,
                "capture_start": start,
                "capture_cycles": capture[4],
                "captures": len(captures[start]),
                "broadcast_cycles": row[4],
                "receive_start": receive,
                "receive_cycles": receive_row[4],
                "post_capture_cycles": receive - start - capture[4],
            }
        )
    return out


def sx_cycles(timing: str) -> set[int]:
    return {row[4] for row in parse_rows(timing) if row[1].startswith("sx_") and row[5] == "play"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def job_backend(run: Path, job_id: str) -> tuple[str, str | None]:
    backend = None
    collect = run / "collect.json"
    if collect.exists():
        payload = json.loads(collect.read_text())
        for entry in payload if isinstance(payload, list) else [payload]:
            jobs = entry.get("jobs") if isinstance(entry, dict) else None
            if jobs and job_id in jobs:
                backend = jobs[job_id]["backend"]
    retention = run / "retention.json"
    if backend is None and retention.exists():
        backend = json.loads(retention.read_text()).get("backend")
    if not isinstance(backend, str):
        raise ValueError(f"{run}: no backend recorded for job {job_id}")
    version = None
    record = run / "record.json"
    if record.exists():
        version = ((json.loads(record.read_text()).get("backends") or {}).get(backend) or {}).get("backend_version")
    return backend, version


def extract_pub(path_text: str) -> dict[str, Any] | None:
    path = ROOT / path_text
    payload = json.loads(path.read_text())
    timing = (payload.get("metadata") or {}).get("compilation", {}).get("scheduler_timing")
    if not timing:
        return None
    return {
        "file": path_text,
        "sha256": sha256(path),
        "pub_name": payload.get("pub_name"),
        "broadcasts": broadcasts(timing["timing"]),
        "sx_cycles": sorted(sx_cycles(timing["timing"])),
    }


def target_cycles() -> dict[str, dict[str, int]]:
    targets = json.loads((ROOT / TARGETS).read_text())
    out = {}
    for name, backend in targets["backends"].items():
        dt_ns = round(backend["dt"] * 1e9)
        require(abs(backend["dt"] - dt_ns * 1e-9) < 1e-15, f"{name}: dt {backend['dt']} is no whole nanosecond")
        sx = {round(d / backend["dt"]) for d in backend["instructions"]["sx"]["duration"] if d is not None}
        measure = {round(d / backend["dt"]) for d in backend["instructions"]["measure"]["duration"] if d is not None}
        require(len(sx) == 1 and len(measure) == 1, f"{name}: sx or measure duration varies across qubits")
        out[name] = {"dt_ns": dt_ns, "sx_cycles": sx.pop(), "measure_cycles": measure.pop()}
    return out


def build(files: Sequence[str] | None = None) -> dict[str, Any]:
    """The record over ``files``, every retained raw PUB when None."""
    if files is None:
        files = sorted(str(p.relative_to(ROOT)) for p in (ROOT / LIVE).glob("*/raw/*/pub_*.json"))
    extracted = parallel.ordered_map(extract_pub, files)
    cycles = target_cycles()
    rows: list[dict[str, Any]] = []
    inputs = {str(TARGETS): sha256(ROOT / TARGETS)}
    for item in extracted:
        if item is None or not item["broadcasts"]:
            continue
        path = Path(item["file"])
        run, job_id = path.parents[2], path.parent.name
        backend, version = job_backend(ROOT / run, job_id)
        require(backend in cycles, f"{item['file']}: backend {backend} absent from {TARGETS}")
        require(
            item["sx_cycles"] in ([], [cycles[backend]["sx_cycles"]]),
            f"{item['file']}: scheduled sx {item['sx_cycles']} cycles, Target {cycles[backend]['sx_cycles']}",
        )
        inputs[item["file"]] = item["sha256"]
        for meta in ("collect.json", "retention.json", "record.json"):
            if (ROOT / run / meta).exists():
                inputs[str(run / meta)] = sha256(ROOT / run / meta)
        for index, entry in enumerate(item["broadcasts"]):
            rows.append(
                {
                    "run": run.name,
                    "job_id": job_id,
                    "pub_file": path.name,
                    "pub_name": item["pub_name"],
                    "broadcast_index": index,
                    "backend": backend,
                    "backend_version": version,
                    **entry,
                    "target_measure_end_to_receive_cycles": entry["receive_start"]
                    - entry["measure_start"]
                    - cycles[backend]["measure_cycles"],
                }
            )
    summary = {}
    for backend in sorted({row["backend"] for row in rows}):
        mine = [row for row in rows if row["backend"] == backend]
        single = [row for row in mine if row["captures"] == 1]
        summary[backend] = {
            "target": cycles[backend],
            "broadcasts": len(mine),
            "runs": len({row["run"] for row in mine}),
            "backend_versions": sorted({row["backend_version"] for row in mine if row["backend_version"]}),
            "single_capture": {
                key: dict(sorted(Counter(row[key] for row in single).items()))
                for key in (
                    "capture_cycles",
                    "broadcast_cycles",
                    "receive_cycles",
                    "post_capture_cycles",
                    "target_measure_end_to_receive_cycles",
                )
            }
            | {
                "measure_to_capture_cycles": dict(
                    sorted(Counter(r["capture_start"] - r["measure_start"] for r in single).items())
                )
            },
            "post_capture_cycles_by_captures": {
                str(n): sorted({row["post_capture_cycles"] for row in mine if row["captures"] == n})
                for n in sorted({row["captures"] for row in mine})
            },
        }
    return {"schema": SCHEMA, "inputs": dict(sorted(inputs.items())), "broadcasts": rows, "summary": summary}


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


SYNTHETIC = "\n".join(
    [
        "main,sx_3,Qubit 3,0,8,play",
        "main,measure_3,Qubit 3,10,64,play",
        "main,measure_3,AWGR1_3,131,325,capture",
        "main,broadcast,Hub,131,526,broadcast",
        "main,receive,Receive,657,7,receive",
        "then,x_3,Qubit 3,669,8,play",
        "main,measure_4,Qubit 4,500,64,play",
        "main,measure_4,Qubit 4,700,64,play",
        "main,measure_4,Qubit 4,764,57,play",
        "main,measure_4,AWGR1_4,821,325,capture",
        "main,measure_5,Qubit 5,700,121,play",
        "main,measure_5,AWGR1_5,821,325,capture",
        "main,broadcast,Hub,821,533,broadcast",
        "main,receive,Receive,1354,7,receive",
        "then,x_4,Qubit 4,1370,8,play",
        "then,x_5,Qubit 5,1370,8,play",
        "else,x_6,Qubit 6,1370,8,play",
    ]
)


def self_test() -> str:
    got = broadcasts(SYNTHETIC)
    require(len(got) == 2, f"two broadcasts expected, got {len(got)}")
    first, second = got
    require(first["post_capture_cycles"] == 201 and first["captures"] == 1, f"first broadcast {first}")
    require(first["measure_start"] == 10 and first["receive_cycles"] == 7, f"first anchors {first}")
    require(second["post_capture_cycles"] == 208 and second["captures"] == 2, f"second broadcast {second}")
    require(second["measure_start"] == 700, f"an earlier measurement of qubit 4 moved the anchor: {second}")
    require(sx_cycles(SYNTHETIC) == {8}, "sx cycles")
    unequal = SYNTHETIC.replace("main,measure_5,AWGR1_5,821,325,capture", "main,measure_5,AWGR1_5,821,320,capture")
    try:
        broadcasts(unequal)
    except ValueError:
        pass
    else:
        raise ValueError("simultaneous captures of unequal length were accepted")
    orphan = SYNTHETIC.replace("main,measure_3,AWGR1_3,131,325,capture\n", "")
    try:
        broadcasts(orphan)
    except ValueError:
        pass
    else:
        raise ValueError("a broadcast without its capture was accepted")
    try:
        parse_rows("main,x_0,Qubit 0,1,8")
    except ValueError:
        pass
    else:
        raise ValueError("a five-field schedule row was accepted")
    return "heron_feedforward_latency self-test passed"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="write the record to this path")
    mode.add_argument("--check", action="store_true", help=f"recompute {OUTPUT} and compare bytes")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        print(self_test())
        return 0
    if args.out is not None:
        args.out.write_text(render(build()))
        return 0
    # The check replays the PUB set the record names, so a run retained later leaves it valid until --out
    # adds that run.
    retained = (ROOT / OUTPUT).read_text()
    inputs = json.loads(retained)["inputs"]
    for name, digest in inputs.items():
        require(sha256(ROOT / name) == digest, f"{name}: sha256 differs from {OUTPUT}")
    pubs = sorted(name for name in inputs if Path(name).name.startswith("pub_"))
    if retained != render(build(pubs)):
        raise ValueError(f"{OUTPUT} differs from the record its pinned schedules produce")
    print(f"{OUTPUT}: matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
