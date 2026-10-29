"""Stochastic null of the measurement-sequence envelope successor.

``RECORD_DIR --arm ARM --replicates N --out FILE`` runs the arm's replicates on the calibrations of the dry-run
record's snapshot at the record's shot count (docs/design/measurement-sequence-envelope-successor.md, "Null
calibration") and writes a record of schema msq-successor-null-v2. ``RECORD_DIR... --arms ARM... --out-dir DIR``
(``--arms all`` for every arm) runs the arms of msq_successor_null_batch.NULL_PLAN at its caps and seeds from each
record's setup through one process pool and writes DIR/ARM.json, the bytes each single-arm run writes; with several
record directories it writes DIR/<record directory name>/ARM.json, each record the bytes of its own single-record
run. ``--cap [RECORD:]ARM=N`` replaces an arm's cap, and ``--limit [RECORD:]ARM=N`` or ``[RECORD:]ARM/CASE=N``
stops a case below replicate N without entering the record; a RECORD prefix (a record directory name) targets one
record and no prefix applies to every record.
``--shard INDEX --shards COUNT`` runs the replicates congruent to INDEX modulo COUNT and writes a shard record
(DIR/ARM-shardINDEX.json under ``--arms``), which runs every case to its limit; ``--merge FILE...`` combines shard
records into the arm's record, byte for byte the record of one unsharded run, and refuses a case its limit cut
short of its verdict count and records whose shots differ. ``RECORD_DIR... --calibrate-sparse`` measures the sparse
settle arm's detectable-gap scale of every pool size of every record on its own seed (``--calibration-seed``), the
secant steps of all records sharing the pool's rounds, and writes each record the path
msq_successor_null_batch.sparse_evidence_path names (``--out FILE`` for a single record). With ``--arms`` it then
runs the null on the fresh scales in the same process. ``--summarize FILE...`` writes the row-free summary of
finished arm records, v1 records included, that docs/evidence/measurement_sequence/successor-null.json retains. The
seed is a QRNG value (``--seed qrng:<draw>#<index>``) or the default. docs/runbooks/null-shards.md routes long runs.
GOROROBA_WORKERS caps the worker count.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import msq_successor_null_batch as nl  # noqa: E402
import qrng_seeds  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("record_dirs", nargs="*", type=Path, metavar="RECORD_DIR", help="dry-run record directories")
    parser.add_argument("--arm", choices=nl.ARMS)
    parser.add_argument("--arms", nargs="+", choices=[*nl.ARMS, "all"], help="NULL_PLAN arms through one pool")
    parser.add_argument("--cap", action="append", default=[], metavar="[RECORD:]ARM=N", help="an --arms cap override")
    parser.add_argument(
        "--limit",
        action="append",
        default=[],
        metavar="[RECORD:]ARM[/CASE]=N",
        help="an --arms per-case stop limit",
    )
    parser.add_argument("--out-dir", type=Path, help="the record directory of --arms")
    parser.add_argument(
        "--replicates", type=int, default=400, help="replicates (the cap, for an arm with a verdict count)"
    )
    qrng_seeds.add_seed_argument(parser, "--seed", default=nl.SUCCESSOR_NULL_SEED, help="qrng:<draw>#<index>")
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, help="the shard count; given, even as 1, the run writes shard records")
    parser.add_argument("--merge", nargs="+", type=Path, metavar="FILE", help="combine shard records")
    parser.add_argument("--summarize", nargs="+", type=Path, metavar="FILE", help="summarize finished arm records")
    parser.add_argument("--calibrate-sparse", action="store_true", help="measure the sparse detectable-gap scale")
    qrng_seeds.add_seed_argument(
        parser, "--calibration-seed", default=nl.SPARSE_CALIBRATION_SEED, help="qrng:<draw>#<index>"
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    dirs: list[Path] = args.record_dirs
    if args.merge:
        record = nl.merge_records([json.loads(path.read_text()) for path in args.merge])
    elif args.summarize:
        record = nl.null_summary([path.read_text() for path in args.summarize])
    elif args.calibrate_sparse or args.arms:
        if args.arm is not None or not dirs:
            parser.error("--calibrate-sparse and --arms need RECORD_DIR and replace --arm")
        if args.arms and args.out_dir is None:
            parser.error("--arms needs --out-dir")
        names = [path.name for path in dirs]
        if len(set(names)) != len(names):
            parser.error(f"record directory names repeat: {names}")
        if args.out is not None and (len(dirs) > 1 or not args.calibrate_sparse):
            parser.error("--out names the one calibration record of a single RECORD_DIR with --calibrate-sparse")
        try:
            setups = [nl.build_setup(path, () if args.calibrate_sparse else None) for path in dirs]
            if args.calibrate_sparse:
                setups = calibrate_and_write(setups, names, args)
            if args.arms:
                run_and_write(setups, names, args)
        except ValueError as error:
            parser.error(str(error))
        return 0
    else:
        if len(dirs) != 1 or args.arm is None:
            parser.error("one RECORD_DIR and --arm are required unless --merge or --summarize is given")
        if args.arm == "settle-sparse" and args.seed == nl.SPARSE_CALIBRATION_SEED:
            parser.error("the sparse settle null draws from the calibration's own seed")
        setup = nl.build_setup(dirs[0])
        shard = nl.run_arm(
            setup,
            args.arm,
            args.seed,
            args.replicates,
            args.shard,
            1 if args.shards is None else args.shards,
            qrng_seeds.seed_record("scripts/msq_successor_null.py", "--seed", args.arm, args.seed_source),
            dirs[0].name,
        )
        record = shard if args.shards is not None else nl.merge_records([shard])
    text = nl.dumps(record)
    if args.out:
        args.out.write_text(text)
    else:
        print(text, end="")
    return 0


def calibrate_and_write(setups: list[nl.Setup], names: list[str], args: argparse.Namespace) -> list[nl.Setup]:
    """Calibrate the sparse scales of every setup through one pool, write each calibration record to `--out` or the
    path sparse_evidence_path names, and return the setups carrying the fresh scales."""
    records = nl.sparse_calibration_records(
        setups,
        args.calibration_seed,
        qrng_seeds.seed_record(
            "scripts/msq_successor_null.py", "--calibration-seed", "settle-sparse", args.calibration_seed_source
        ),
        names,
    )
    for setup, record in zip(setups, records, strict=True):
        path = args.out or nl.sparse_evidence_path(setup.digests["snapshot_sha256"], setup.width, setup.shots)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(nl.dumps(record))
    return nl.with_calibrated_scales(setups, records)


def run_and_write(setups: list[nl.Setup], names: list[str], args: argparse.Namespace) -> None:
    """Run the --arms plan of every record's setup through one `run_arms` call and write each record's arm records
    to --out-dir, under the record's name when several records run."""
    runs: list[nl.ArmRun] = []
    for setup, name in zip(setups, names, strict=True):
        found = plan_runs(args.arms, for_record(args.cap, name, names), name, for_record(args.limit, name, names))
        labels = {run.arm: {case.label for case in nl.arm_cases(run.arm, setup.width)} for run in found}
        runs.extend(run._replace(limits=expand_limits(run, labels[run.arm]), setup=setup) for run in found)
    records = nl.run_arms(setups[0], runs, args.shard, 1 if args.shards is None else args.shards)
    shard = args.shard if args.shards is not None else None
    for name in names:
        mine = [record for record in records if record["record"] == name]
        write_arm_records(args.out_dir if len(names) == 1 else args.out_dir / name, mine, shard)


def for_record(entries: list[str], record_name: str, record_names: list[str]) -> list[str]:
    """The --cap or --limit entries that apply to one record, without their `RECORD:` prefix: an unprefixed entry
    applies to every record, a prefixed entry to the record it names, and a prefix that names none of `record_names`
    is refused."""
    kept = []
    for entry in entries:
        spec, equals, value = entry.partition("=")
        prefix, colon, rest = spec.partition(":")
        if not colon:
            kept.append(entry)
            continue
        if prefix not in record_names:
            raise ValueError(f"{entry}: {prefix!r} names none of the records {record_names}")
        if prefix == record_name:
            kept.append(f"{rest}{equals}{value}")
    return kept


def plan_runs(arms: list[str], caps: list[str], record_name: str, limits: list[str] | None = None) -> list[nl.ArmRun]:
    """The ArmRun of each named arm (every arm for "all") at its NULL_PLAN cap and seed, a --cap ARM=N replacing the
    cap, with the seed_source a single-arm run of the same seed spelling records. Each --limit ARM=N or ARM/CASE=N
    lands in the arm's `limits` under the key "*" or CASE, which `expand_limits` resolves against the arm's cases."""
    plan = {arm: (cap, spelling) for arm, cap, spelling in nl.NULL_PLAN}
    chosen = list(nl.ARMS) if "all" in arms else list(dict.fromkeys(arms))
    overrides: dict[str, int] = {}
    for entry in caps:
        arm, _, value = entry.partition("=")
        if arm not in chosen or not value.isdigit() or int(value) < 1:
            raise ValueError(f"--cap {entry}: name a chosen arm and a positive replicate count")
        overrides[arm] = int(value)
    stops: dict[str, dict[str, int]] = {}
    for entry in limits or []:
        name, _, value = entry.partition("=")
        arm, _, case = name.partition("/")
        if arm not in chosen or not value.isdigit() or int(value) < 1:
            raise ValueError(f"--limit {entry}: name a chosen arm and a positive replicate count")
        stops.setdefault(arm, {})[case or "*"] = int(value)
    runs = []
    for arm in chosen:
        cap, spelling = plan[arm]
        if spelling is None:
            seed, source = nl.SUCCESSOR_NULL_SEED, "default"
        else:
            seed, source = qrng_seeds.parse_value(spelling, [nl.SUCCESSOR_NULL_SEED])
        record = qrng_seeds.seed_record("scripts/msq_successor_null.py", "--seed", arm, source)
        runs.append(nl.ArmRun(arm, seed, overrides.get(arm, cap), record, record_name, limits=stops.get(arm)))
    return runs


def write_arm_records(out_dir: Path, records: list[dict[str, object]], shard: int | None) -> None:
    """Write each arm's record to DIR/ARM.json, or its shard record to DIR/ARM-shardINDEX.json when `shard` names
    the index of an explicit --shards run (a single shard included), so the runbook's merge reads every shard."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for record in records:
        if shard is None:
            (out_dir / f"{record['arm']}.json").write_text(nl.dumps(nl.merge_records([record])))
        else:
            (out_dir / f"{record['arm']}-shard{shard}.json").write_text(nl.dumps(record))


def expand_limits(run: nl.ArmRun, labels: set[str]) -> dict[str, int] | None:
    """The run's per-case limits over the case labels of its arm: an ARM=N limit ("*") applies to every case that
    names no limit of its own."""
    if not run.limits:
        return None
    named = {label: value for label, value in run.limits.items() if label != "*"}
    if set(named) - labels:
        raise ValueError(
            f"--limit: {run.arm} has no case {sorted(set(named) - labels)}; its cases are {sorted(labels)}"
        )
    if "*" in run.limits:
        named = {label: named.get(label, run.limits["*"]) for label in labels}
    return named


if __name__ == "__main__":
    raise SystemExit(main())
