"""Series gate of the coin-arm coset-block case on Quantum Inspire: collected-run checks, drift record, submission.

qi_pathion_coset_coin_cases.py generates the cases and scores a returned series; this module holds the part that runs
under the Quantum Inspire interpreter, which has no python-flint and so cannot import the case generator. It succeeds
qi_pathion_coset_block_series.py, whose series stopped on a readout-bracket drift: here a drift is recorded per
batch and never refuses a submission. The run-directory readers (load_run, series_runs, reference_drift,
register_qubits) are that module's.

The Tuna series holds three batches of [readout-0, template, readout-1] (ba, bb, b0) and one batch of xor_ba, so
every primary template is corrected with the assignment of its own batch. A collected batch must hold completed
jobs, full shot lists and case bytes equal to the series; a platform failure (a failed job, a short shot list, a
submission the API refuses) stops the series and raises the pause ladder, which is the only stop.

--sanity RUN_DIR... checks the collected batches and prints the drift record (exit 0 whatever it holds).
--submit-next SERIES_DIR copies the next batch into its run directory and submits it through qi_platform.submit
once every earlier batch passes that check; a Tuna-17 batch also needs the analysis of the collected QX series
(--control) with a passing control verdict bound to the QX case digests. The last stdout line is the run directory;
--dry prints the gate receipt and sends nothing.

Usage: "$QI_PYTHON" scripts/qi_pathion_coset_coin_series.py
       (--sanity RUN_DIR... | --submit-next SERIES_DIR --approval QUOTE [--control FILE] [--runs DIR] [--dry])
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_coset_block_series as pcs  # noqa: E402

TUNA_SERIES = "pathion_coset_coin_tuna_17"
QX_SERIES = "pathion_coset_coin_qx"
CASES_ROOT = pcs.CASES_ROOT
RUNS_ROOT = pcs.RUNS_ROOT


def series_of(run_dir: Path) -> str:
    """The series a run directory `<stamp>-<series>-batch-NN` belongs to."""
    stem = run_dir.name.rpartition("-batch-")[0]
    for name in (TUNA_SERIES, QX_SERIES):
        if stem.endswith(f"-{name}"):
            return name
    raise SystemExit(f"{run_dir.name} is not a run directory of {TUNA_SERIES} or {QX_SERIES}")


def drift_record(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Drift over loaded runs: the readout rates of each bracket and the change between successive brackets of one
    kind. `flagged` lists the changes above pcs.DRIFT_STOP and stops nothing."""
    return pcs.runs_drift(runs)


def sanity(run_dirs: list[Path], case_root: Path | None = CASES_ROOT) -> dict[str, Any]:
    """Load every collected batch (in batch order) and report its drift record."""
    loaded = []
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        case_batch = None if case_root is None else case_root / series_of(run_dir) / cases["batch"]
        loaded.append(pcs.load_run(run_dir, case_batch))
    batches = [r["cases"]["batch"] for r in loaded]
    if len(set(batches)) != len(batches):
        raise SystemExit(f"a batch appears twice in {batches}")
    has_pair = [
        r
        for r in loaded
        if {row["file"] for row in r["cases"]["circuits"] if row["kind"] == "readout"} == set(pcs.READOUT_KIND)
    ]
    return {"batches": batches, "drift": drift_record(has_pair) if has_pair else None}


def check_control(control_path: Path, case_root: Path) -> dict[str, Any]:
    """The QX control analysis a Tuna-17 batch needs: a passing verdict bound to the QX series case digests."""
    analysis = json.loads(control_path.read_text(encoding="utf-8"))
    want = {
        batch.name: pcs.file_sha256(batch / "cases.json") for batch in sorted((case_root / QX_SERIES).glob("batch-*"))
    }
    if analysis.get("claim_kind") != pcs.CONTROL_KIND or analysis.get("batch_cases_sha256") != want:
        raise SystemExit(f"{control_path} is not the analysis of the remote {QX_SERIES} series of these cases")
    if not analysis.get("qx_control", {}).get("pass"):
        raise SystemExit(f"the QX control missed its ideal: {analysis.get('qx_control')}")
    try:
        name = control_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        raise SystemExit(f"{control_path} lies outside the repository; retain the control analysis first") from None
    return {"file": name, "sha256": pcs.file_sha256(control_path), "batch_cases_sha256": want}


def submit_next(
    series_dir: Path,
    runs: Path,
    approval: str,
    control: Path | None = None,
    dry: bool = False,
    client: Any = None,
) -> tuple[Path, dict[str, Any]]:
    """Copy the next batch of a series into its run directory and submit it, after every earlier batch is clear.

    Every earlier batch must be submitted, collected with completed jobs and full shot lists and equal to the series
    case. The readout drift over the collected brackets is written into the gate receipt (`drift`) and refuses
    nothing. A hardware pause held by an earlier batch (series-gate.json) carries to the rest of the series, and a
    call holds an exclusive lock on the series case directory. `client` replaces qi_platform.Client for the pause
    wait (tests)."""
    import fcntl
    import os
    import shutil
    import time

    name = series_dir.name
    case_root = series_dir.parent
    batches = [r["batch"] for r in json.loads((series_dir / "cases.json").read_text(encoding="utf-8"))["batches"]]
    done = pcs.series_runs(name, runs)
    pending = [b for b in batches if b not in done]
    if not pending:
        raise SystemExit(f"every batch of {name} is submitted")
    if any(b in done for b in batches[batches.index(pending[0]) :]):
        raise SystemExit(f"{name}: a later batch was submitted before {pending[0]}")
    batch = pending[0]
    first = json.loads((series_dir / batch / "cases.json").read_text(encoding="utf-8"))
    hardware = name == TUNA_SERIES
    fd = os.open(series_dir, os.O_RDONLY)
    try:
        if not dry:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise SystemExit(f"another --submit-next holds {name}") from None
        loaded = [pcs.load_run(done[b], series_dir / b) for b in batches if b in done]
        stops: dict[str, Any] = {"batches_checked": [r["cases"]["batch"] for r in loaded], "drift": None}
        paired = [
            r
            for r in loaded
            if {row["file"] for row in r["cases"]["circuits"] if row["kind"] == "readout"} == set(pcs.READOUT_KIND)
        ]
        if paired:
            drift = drift_record(paired)
            stops["drift"] = {"max_abs_delta": drift["max_abs_delta"], "flagged": drift["flagged"]}
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
            "schema": "qi-pathion-coset-coin-gate-v1",
            "series": name,
            "batch": batch,
            "cases_sha256": pcs.file_sha256(series_dir / batch / "cases.json"),
            "predecessors": [
                {
                    "batch": r["cases"]["batch"],
                    "run_dir": r["run_dir"].name,
                    "results_sha256": pcs.file_sha256(r["run_dir"] / "results.json"),
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
        print(json.dumps(sanity(args.sanity), indent=1, sort_keys=True))
        return 0
    if not args.approval:
        parser.error("--submit-next needs --approval")
    run_dir, receipt = submit_next(args.submit_next, args.runs, args.approval, args.control, args.dry)
    if args.dry:
        print(json.dumps(receipt, indent=1, sort_keys=True), file=sys.stderr)
    print(run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
