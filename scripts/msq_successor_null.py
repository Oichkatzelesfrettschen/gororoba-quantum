"""Stochastic null of the measurement-sequence envelope successor, one arm at a time.

``RECORD_DIR --arm ARM --replicates N --out FILE`` runs the arm's replicates on the calibrations of the dry-run
record's snapshot (docs/design/measurement-sequence-envelope-successor.md, "Null calibration") and writes a record
of schema msq-successor-null-v1. ``--shard INDEX --shards COUNT`` runs the replicates congruent to INDEX modulo
COUNT and writes a shard record; ``--merge FILE...`` combines shard records into the arm's record, byte for byte
the record of one unsharded run. The seed is a QRNG value (``--seed qrng:<draw>#<index>``) or the default.
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
    parser.add_argument(
        "--replicates", type=int, default=400, help="replicates (the cap, for an arm with a verdict count)"
    )
    qrng_seeds.add_seed_argument(parser, "--seed", default=nl.SUCCESSOR_NULL_SEED, help="qrng:<draw>#<index>")
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--merge", nargs="+", type=Path, metavar="FILE", help="combine shard records")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.merge:
        record = nl.merge_records([json.loads(path.read_text()) for path in args.merge])
    else:
        if args.record_dir is None or args.arm is None:
            parser.error("RECORD_DIR and --arm are required unless --merge is given")
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


if __name__ == "__main__":
    raise SystemExit(main())
