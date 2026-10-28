"""Stochastic null of the measurement-sequence envelope successor.

``RECORD_DIR --arm ARM --replicates N --out FILE`` runs the arm's replicates on the calibrations of the dry-run
record's snapshot (docs/design/measurement-sequence-envelope-successor.md, "Null calibration") and writes a record
of schema msq-successor-null-v1. ``RECORD_DIR --arms ARM... --out-dir DIR`` (``--arms all`` for every arm) runs
the arms of msq_successor_null_batch.NULL_PLAN at its caps and seeds from one setup through one process pool and
writes DIR/ARM.json, the bytes each single-arm run writes; ``--cap ARM=N`` replaces an arm's cap.
``--shard INDEX --shards COUNT`` runs the replicates congruent to INDEX modulo COUNT and writes a shard record
(DIR/ARM-shardINDEX.json under ``--arms``), which runs every case to its cap; ``--merge FILE...`` combines shard
records into the arm's record, byte for byte the record of one unsharded run. ``RECORD_DIR --calibrate-sparse
--out FILE`` measures the sparse settle arm's detectable-gap scale of every pool size on its own seed
(``--calibration-seed``) and writes the record that msq_successor_null_batch.SPARSE_SCALE_EVIDENCE names.
``--summarize FILE...`` writes the row-free summary of finished arm records that
docs/evidence/measurement_sequence/successor-null.json retains. The seed is a QRNG value
(``--seed qrng:<draw>#<index>``) or the default. docs/runbooks/null-shards.md routes long runs.
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
    parser.add_argument("record_dir", nargs="?", type=Path, help="a dry-run record directory")
    parser.add_argument("--arm", choices=nl.ARMS)
    parser.add_argument("--arms", nargs="+", choices=[*nl.ARMS, "all"], help="NULL_PLAN arms through one pool")
    parser.add_argument("--cap", action="append", default=[], metavar="ARM=N", help="an --arms cap override")
    parser.add_argument("--out-dir", type=Path, help="the record directory of --arms")
    parser.add_argument(
        "--replicates", type=int, default=400, help="replicates (the cap, for an arm with a verdict count)"
    )
    qrng_seeds.add_seed_argument(parser, "--seed", default=nl.SUCCESSOR_NULL_SEED, help="qrng:<draw>#<index>")
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--merge", nargs="+", type=Path, metavar="FILE", help="combine shard records")
    parser.add_argument("--summarize", nargs="+", type=Path, metavar="FILE", help="summarize finished arm records")
    parser.add_argument("--calibrate-sparse", action="store_true", help="measure the sparse detectable-gap scale")
    qrng_seeds.add_seed_argument(
        parser, "--calibration-seed", default=nl.SPARSE_CALIBRATION_SEED, help="qrng:<draw>#<index>"
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.merge:
        record = nl.merge_records([json.loads(path.read_text()) for path in args.merge])
    elif args.summarize:
        record = nl.null_summary([path.read_text() for path in args.summarize])
    elif args.calibrate_sparse:
        if args.record_dir is None:
            parser.error("RECORD_DIR is required with --calibrate-sparse")
        record = nl.sparse_calibration_record(
            nl.build_setup(args.record_dir),
            args.calibration_seed,
            qrng_seeds.seed_record(
                "scripts/msq_successor_null.py", "--calibration-seed", "settle-sparse", args.calibration_seed_source
            ),
            args.record_dir.name,
        )
    elif args.arms:
        if args.record_dir is None or args.out_dir is None or args.arm is not None:
            parser.error("--arms needs RECORD_DIR and --out-dir and replaces --arm")
        try:
            runs = plan_runs(args.arms, args.cap, args.record_dir.name)
        except ValueError as error:
            parser.error(str(error))
        shards = nl.run_arms(nl.build_setup(args.record_dir), runs, args.shard, args.shards)
        args.out_dir.mkdir(parents=True, exist_ok=True)
        for run, shard in zip(runs, shards, strict=True):
            name = f"{run.arm}-shard{args.shard}.json" if args.shards > 1 else f"{run.arm}.json"
            (args.out_dir / name).write_text(nl.dumps(shard if args.shards > 1 else nl.merge_records([shard])))
        return 0
    else:
        if args.record_dir is None or args.arm is None:
            parser.error("RECORD_DIR and --arm are required unless --merge or --summarize is given")
        if args.arm == "settle-sparse" and args.seed == nl.SPARSE_CALIBRATION_SEED:
            parser.error("the sparse settle null draws from the calibration's own seed")
        setup = nl.build_setup(args.record_dir)
        shard = nl.run_arm(
            setup,
            args.arm,
            args.seed,
            args.replicates,
            args.shard,
            args.shards,
            qrng_seeds.seed_record("scripts/msq_successor_null.py", "--seed", args.arm, args.seed_source),
            args.record_dir.name,
        )
        record = shard if args.shards > 1 else nl.merge_records([shard])
    text = nl.dumps(record)
    if args.out:
        args.out.write_text(text)
    else:
        print(text, end="")
    return 0


def plan_runs(arms: list[str], caps: list[str], record_name: str) -> list[nl.ArmRun]:
    """The ArmRun of each named arm (every arm for "all") at its NULL_PLAN cap and seed, a --cap ARM=N replacing the
    cap, with the seed_source a single-arm run of the same seed spelling records."""
    plan = {arm: (cap, spelling) for arm, cap, spelling in nl.NULL_PLAN}
    chosen = list(nl.ARMS) if "all" in arms else list(dict.fromkeys(arms))
    overrides: dict[str, int] = {}
    for entry in caps:
        arm, _, value = entry.partition("=")
        if arm not in chosen or not value.isdigit() or int(value) < 1:
            raise ValueError(f"--cap {entry}: name a chosen arm and a positive replicate count")
        overrides[arm] = int(value)
    runs = []
    for arm in chosen:
        cap, spelling = plan[arm]
        if spelling is None:
            seed, source = nl.SUCCESSOR_NULL_SEED, "default"
        else:
            seed, source = qrng_seeds.parse_value(spelling, [nl.SUCCESSOR_NULL_SEED])
        record = qrng_seeds.seed_record("scripts/msq_successor_null.py", "--seed", arm, source)
        runs.append(nl.ArmRun(arm, seed, overrides.get(arm, cap), record, record_name))
    return runs


if __name__ == "__main__":
    raise SystemExit(main())
