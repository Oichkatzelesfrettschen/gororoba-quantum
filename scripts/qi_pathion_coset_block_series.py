"""Series gate of the A_5 coset-block case on Quantum Inspire: collected-run checks, readout-bracket drift, submission.

qi_pathion_coset_block_cases.py generates the cases and scores a returned series; this module holds the part of the
series that runs under the Quantum Inspire interpreter, which has no python-flint and so cannot import the case
generator. It reads only run directories, so it needs numpy and the standard library; qi_platform loads on the
submission path alone.

A batch carries one readout circuit, readout-0 (every qubit prepared in 0) or readout-1 (prepared in 1), and the
series alternates the two. A readout-0 circuit reads e01 = P(read 1) of each register qubit and a readout-1 circuit
reads e10 = 1 - P(read 1). The preregistered drift stop compares every readout circuit with the previous circuit of
the same kind, qubit by qubit, and stops the series when any change exceeds DRIFT_STOP.

--sanity RUN_DIR... checks the collected batches (case bytes, receipt digest, completed jobs, full shot lists), prints
the drift report and exits 1 when the stop fires. --submit-next SERIES_DIR copies the next batch of a case series
into its run directory and submits it through qi_platform.submit once every earlier batch passes that check; a
Tuna-17 batch also needs the analysis of the collected QX series (--control) with a passing control verdict bound to
the QX case digests. The last stdout line of --submit-next is the run directory; --dry prints the gate receipt and
sends nothing.

Usage: "$QI_PYTHON" scripts/qi_pathion_coset_block_series.py
       (--sanity RUN_DIR... | --submit-next SERIES_DIR --approval QUOTE [--control FILE] [--runs DIR] [--dry])
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]

TUNA_SERIES = "pathion_coset_block_tuna_17"
QX_SERIES = "pathion_coset_block_qx"
DRIFT_STOP = 0.02
READOUT_KIND = {"readout-0.cq": "e01", "readout-1.cq": "e10"}
CASES_ROOT = ROOT / "results/quantum_inspire/cases"
RUNS_ROOT = ROOT / "results/quantum_inspire/runs"
CONTROL_KIND = "preregistered emulator control"


def bit(shot: str, qubit: int) -> int:
    """Bit of `qubit` in a shot string that puts qubit 0 at the rightmost character."""
    return int(shot[len(shot) - 1 - qubit])


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def series_runs(series_name: str, runs: Path) -> dict[str, Path]:
    """The run directory of each submitted batch of a series, keyed by batch name."""
    found: dict[str, Path] = {}
    stamps = set()
    for path in sorted(runs.glob(f"*-{series_name}-batch-*")):
        stamp, _, batch = path.name.partition(f"-{series_name}-")
        if batch in found:
            raise SystemExit(f"{batch} of {series_name} has two run directories")
        found[batch] = path
        stamps.add(stamp)
    if len(stamps) > 1:
        raise SystemExit(f"run directories of {series_name} carry several stamps {sorted(stamps)}")
    return found


def series_of(run_dir: Path) -> str:
    """The series a run directory `<stamp>-<series>-batch-NN` belongs to."""
    stem = run_dir.name.rpartition("-batch-")[0]
    for name in (TUNA_SERIES, QX_SERIES):
        if stem.endswith(f"-{name}"):
            return name
    raise SystemExit(f"{run_dir.name} is not a run directory of {TUNA_SERIES} or {QX_SERIES}")


def load_run(run_dir: Path, case_batch: Path | None = None) -> dict[str, Any]:
    """One collected batch: cases, shot lists and job records, every check of a returned batch applied.

    The run's cases.json must equal the series case when `case_batch` is given and must be the file the
    submission receipt binds; every job completed; every shot list holds cases["shots"] strings of
    cases["nqubits"] bits. A short list stops the series (qi_platform.collect retains a list as returned).
    """
    cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
    if case_batch is not None:
        for row in cases["circuits"]:
            if file_sha256(run_dir / row["file"]) != row["sha256"]:
                raise SystemExit(f"{run_dir}/{row['file']} differs from the series case")
        if file_sha256(run_dir / "cases.json") != file_sha256(case_batch / "cases.json"):
            raise SystemExit(f"{run_dir}/cases.json differs from {case_batch}/cases.json")
    receipt_path = run_dir / "submission.json"
    results_path = run_dir / "results.json"
    if not receipt_path.exists() or not results_path.exists():
        raise SystemExit(f"{run_dir} is not collected; run qi_platform.py collect first")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["cases_sha256"] != file_sha256(run_dir / "cases.json"):
        raise SystemExit(f"{run_dir}/cases.json is not the case its submission receipt binds")
    results = json.loads(results_path.read_text(encoding="utf-8"))
    jobs = {row["file"]: row["job"] for row in results["jobs"]}
    shots: dict[str, list[str]] = {}
    for row in cases["circuits"]:
        job = jobs.get(row["file"])
        if job is None or job["status"] != "completed":
            state = "has no job" if job is None else f"job {job['id']} is {job['status']}"
            raise SystemExit(f"{run_dir}/{row['file']} {state}: the series stops")
        listed = json.loads((run_dir / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
        if len(listed) != cases["shots"]:
            raise SystemExit(
                f"{run_dir}/{row['file']} holds {len(listed)} shots of the {cases['shots']} requested: the series stops"
            )
        width = cases["nqubits"]
        if any(len(s) != width or set(s) - {"0", "1"} for s in listed):
            raise SystemExit(f"{run_dir}/{row['file']} holds a shot that is not a {width}-bit string")
        shots[row["file"]] = listed
    return {"cases": cases, "shots": shots, "jobs": jobs, "run_dir": run_dir}


def register_qubits(cases: dict[str, Any]) -> list[int]:
    """Physical qubits the templates read: the data and selector roles of every template."""
    return sorted({int(q) for t in cases["templates"].values() for q in t["roles"].values()})


def reference_drift(
    references: list[tuple[str, str, list[str]]], qubits: list[int], threshold: float = DRIFT_STOP
) -> dict[str, Any]:
    """Readout rates of each reference and the change between successive references of one kind.

    `references` lists (batch, file, shots) for each readout circuit; rows are ordered by batch. A change of
    more than `threshold` on any qubit is flagged, and any flag stops the series."""
    rows: list[dict[str, Any]] = []
    for batch, file, listed in sorted(references):
        kind = READOUT_KIND[file]
        ones = {q: sum(bit(s, q) for s in listed) / len(listed) for q in qubits}
        rows.append(
            {
                "batch": batch,
                "reference": file,
                "kind": kind,
                "rates": {q: (ones[q] if kind == "e01" else 1.0 - ones[q]) for q in qubits},
            }
        )
    pairs: list[dict[str, Any]] = []
    for file in READOUT_KIND:
        same = [r for r in rows if r["reference"] == file]
        for before, after in zip(same, same[1:], strict=False):
            for q in qubits:
                delta = after["rates"][q] - before["rates"][q]
                pairs.append(
                    {
                        "kind": before["kind"],
                        "from": before["batch"],
                        "to": after["batch"],
                        "qubit": q,
                        "rate_from": before["rates"][q],
                        "rate_to": after["rates"][q],
                        "delta": delta,
                        "flag": abs(delta) > threshold,
                    }
                )
    return {
        "threshold": threshold,
        "references": rows,
        "pairs": pairs,
        "max_abs_delta": max((abs(p["delta"]) for p in pairs), default=0.0),
        "flagged": [p for p in pairs if p["flag"]],
    }


def runs_drift(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Drift report over loaded runs (load_run results of one series)."""
    if not runs:
        raise SystemExit("a drift report needs collected runs")
    qubits = register_qubits(runs[0]["cases"])
    references = [
        (run["cases"]["batch"], row["file"], run["shots"][row["file"]])
        for run in runs
        for row in run["cases"]["circuits"]
        if row["kind"] == "readout"
    ]
    return reference_drift(references, qubits)


def sanity(run_dirs: list[Path], case_root: Path | None = CASES_ROOT) -> dict[str, Any]:
    """Load every collected batch (in batch order) and report its drift; the caller exits 1 on a flag."""
    loaded = []
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        case_batch = None if case_root is None else case_root / series_of(run_dir) / cases["batch"]
        loaded.append(load_run(run_dir, case_batch))
    batches = [r["cases"]["batch"] for r in loaded]
    if len(set(batches)) != len(batches):
        raise SystemExit(f"a batch appears twice in {batches}")
    drift = runs_drift(loaded)
    return {"batches": batches, "drift": drift, "stopped": bool(drift["flagged"])}


def check_control(control_path: Path, case_root: Path) -> dict[str, Any]:
    """The QX control analysis a Tuna-17 batch needs: a passing verdict bound to the QX series case digests."""
    analysis = json.loads(control_path.read_text(encoding="utf-8"))
    want = {batch.name: file_sha256(batch / "cases.json") for batch in sorted((case_root / QX_SERIES).glob("batch-*"))}
    if analysis.get("claim_kind") != CONTROL_KIND or analysis.get("batch_cases_sha256") != want:
        raise SystemExit(f"{control_path} is not the analysis of the remote {QX_SERIES} series of these cases")
    if not analysis.get("qx_control", {}).get("pass"):
        raise SystemExit(f"the QX control missed its ideal: {analysis.get('qx_control')}")
    try:
        name = control_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        raise SystemExit(f"{control_path} lies outside the repository; retain the control analysis first") from None
    return {"file": name, "sha256": file_sha256(control_path), "batch_cases_sha256": want}


def submit_next(
    series_dir: Path,
    runs: Path,
    approval: str,
    control: Path | None = None,
    dry: bool = False,
    client: Any = None,
) -> tuple[Path, dict[str, Any]]:
    """Copy the next batch of a series into its run directory and submit it, after every stop is clear.

    Every earlier batch must be submitted, collected with completed jobs and full shot lists and equal to the
    series case, and the readout drift over them must stay at or below DRIFT_STOP. A hardware pause held by an
    earlier batch (series-gate.json) carries to the rest of the series, and a call holds an exclusive lock on the
    series case directory. `client` replaces qi_platform.Client for the pause wait (tests)."""
    import fcntl
    import os
    import shutil
    import time

    name = series_dir.name
    case_root = series_dir.parent
    batches = [r["batch"] for r in json.loads((series_dir / "cases.json").read_text(encoding="utf-8"))["batches"]]
    hardware = name == TUNA_SERIES
    fd = os.open(series_dir, os.O_RDONLY)
    try:
        if not dry:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise SystemExit(f"another --submit-next holds {name}") from None
        # The submitted set is read under the lock: a snapshot taken before it goes stale when another call
        # submits the batch in between, and a first batch re-run in a new run directory is a duplicate.
        done = series_runs(name, runs)
        pending = [b for b in batches if b not in done]
        if not pending:
            raise SystemExit(f"every batch of {name} is submitted")
        if any(b in done for b in batches[batches.index(pending[0]) :]):
            raise SystemExit(f"{name}: a later batch was submitted before {pending[0]}")
        batch = pending[0]
        first = json.loads((series_dir / batch / "cases.json").read_text(encoding="utf-8"))
        loaded = [load_run(done[b], series_dir / b) for b in batches if b in done]
        stops: dict[str, Any] = {"batches_checked": [r["cases"]["batch"] for r in loaded]}
        if loaded:
            drift = runs_drift(loaded)
            if drift["flagged"]:
                raise SystemExit(
                    f"the readout-bracket drift stop fired (limit {DRIFT_STOP}): {drift['flagged']}; the series stops"
                )
            stops |= {"bracket_drift_flagged": [], "max_drift": drift["max_abs_delta"]}
        control_record = None
        if hardware:
            if control is None:
                raise SystemExit("a Tuna-17 batch needs --control, the analysis of the collected QX series")
            control_record = check_control(control, case_root)
        import qi_platform

        if hardware:
            if client is None:
                client = qi_platform.Client()
            pause = qi_platform.HARDWARE_PAUSE_SECONDS
            recorded = [
                json.loads((done[b] / "series-gate.json").read_text(encoding="utf-8")).get("pause_seconds", 0)
                for b in batches
                if b in done and (done[b] / "series-gate.json").exists()
            ]
            if recorded and pause < max(recorded):
                raise SystemExit(
                    f"an earlier batch of {name} ran at a {max(recorded)} s pause; "
                    f"set QI_HARDWARE_PAUSE_SECONDS to at least that step"
                )
        else:
            pause = 0
        stamp = (
            next(iter(done.values())).name.partition(f"-{name}-")[0]
            if done
            else datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")
        )
        run_dir = runs / f"{stamp}-{name}-{batch}"
        receipt = {
            "schema": "qi-pathion-coset-block-gate-v1",
            "series": name,
            "batch": batch,
            "cases_sha256": file_sha256(series_dir / batch / "cases.json"),
            "predecessors": [
                {
                    "batch": r["cases"]["batch"],
                    "run_dir": r["run_dir"].name,
                    "results_sha256": file_sha256(r["run_dir"] / "results.json"),
                }
                for r in loaded
            ],
            "stops": stops,
            "control": control_record,
            "pause_seconds": pause,
        }
        if dry:
            return run_dir, receipt
        if hardware:
            # hardware_pause_left refuses while any hardware job of the account is unfinished.
            while (left := qi_platform.hardware_pause_left(client)) > 0:
                time.sleep(left + 1)
        if run_dir.exists():
            raise SystemExit(f"{run_dir.name} already exists; another submission holds it")
        try:
            shutil.copytree(series_dir / batch, run_dir)
            (run_dir / "series-gate.json").write_text(json.dumps(receipt, indent=1) + "\n", encoding="utf-8")
            record = qi_platform.submit(
                run_dir, first["backend_type_id"], approval, expected_cases_sha256=receipt["cases_sha256"]
            )
        except BaseException:
            # A refusal or a failure before the checkpoint leaves nothing on the service; the copy goes so the
            # next call does not read an unsent batch as submitted.
            if run_dir.exists() and not (run_dir / "submission-state.json").exists():
                shutil.rmtree(run_dir)
            raise
        print(
            f"{run_dir.name}: batch {record['batch_job']}, jobs {[row['job'] for row in record['jobs']]}",
            file=sys.stderr,
        )
        return run_dir, receipt
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sanity", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--submit-next", type=Path, metavar="SERIES_DIR")
    parser.add_argument("--approval")
    parser.add_argument("--control", type=Path)
    parser.add_argument("--runs", type=Path, default=RUNS_ROOT)
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()
    if args.sanity:
        report = sanity(args.sanity)
        print(json.dumps(report, indent=1, sort_keys=True))
        return 1 if report["stopped"] else 0
    if not args.approval:
        parser.error("--submit-next needs --approval")
    run_dir, receipt = submit_next(args.submit_next, args.runs, args.approval, args.control, args.dry)
    if args.dry:
        print(json.dumps(receipt, indent=1, sort_keys=True), file=sys.stderr)
    print(run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
