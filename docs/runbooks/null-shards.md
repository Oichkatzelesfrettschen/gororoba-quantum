# Successor null: one pool, Kaggle and hosted-runner shards

`scripts/msq_successor_null.py` runs the measurement-sequence successor's classical null
([design](../design/measurement-sequence-envelope-successor.md#null-calibration)). Every route below writes the
bytes of one unsharded single-arm run per arm, so their records merge, summarize and replay alike.

## One host, every arm

```sh
"$PYTHON" -B scripts/msq_successor_null.py results/live/RECORD --arms all --out-dir OUT
```

One setup and one process pool serve every arm of `msq_successor_null_batch.NULL_PLAN`, at its caps and seeds. The
shots per member come from the dry-run record's `shots`, so the null samples at the shot count the record plans; a
record without `shots` is refused.
Each round fills the pool with two blocks per worker across all running cases (`round_size`), and an arm with a
verdict count stops each case at it. Measured on the 6-core build host (12 threads), on the width-24 record
`2026-10-28T163139.827337Z`: the arms carryover-positive, q-tolerance, plateau-low and gamma took 222 s wall
for 1886 CPU-s in one call, against 415 s run one arm at a time on four workers. The full plan, `--arms all` at
the plan's caps, took 4185 s wall for 29 800 CPU-s (712 % of the 12 threads) while other jobs shared the host (load
average 12 to 20 at its end), and wrote every arm record the retained summary names, plateau-retained included.

## Several records in one invocation

```sh
"$PYTHON" -B scripts/msq_successor_null.py results/live/RECORD_A results/live/RECORD_B \
  --calibrate-sparse --arms all --out-dir OUT
```

Each record builds its own setup, and every round of the run fills one pool with the blocks of every record's running
cases. A record's arm file is the bytes a single-record, single-arm call writes for the same record, arm, seed and
cap: `OUT/RECORD_A/ARM.json` and `OUT/RECORD_B/ARM.json` for several records, `OUT/ARM.json` for one (shard records
follow the same layout as `ARM-shardK.json`). `--cap` and `--limit` keep their `ARM[/CASE]=N` spelling and apply to
every record; a `RECORD:` prefix (the record directory name) targets one record, as in `--limit
RECORD_A:settle-sparse/8-qubits=9800`, and a prefix that names no record is refused.

`--calibrate-sparse` measures the sparse settle arm's detectable-gap scale of the pool sizes 8, 9 and the record's
width, with the secant step of every (record, pool size) pair measured in one pool map per round, and writes each
calibration to `docs/evidence/measurement_sequence/successor-sparse-scale/SNAPSHOT16-wWIDTH-sSHOTS.json`: the first 16
hex digits of the snapshot sha256, the layout width and the shots. `build_setup` reads that file, else the legacy
`successor-sparse-scale.json` when it was measured on the same snapshot and width at 8192 shots, so a calibration
holds for one snapshot, width and shot count. With `--arms` in the same call, the null runs on the fresh scales in
the same process; the calibration needs its own `--calibration-seed`, which differs from the null's seeds.

The case labels of the settle arms follow the layout width: `8-qubits`, `9-qubits` and `WIDTH-qubits`. A width-32
record labels its third case `32-qubits`, so the `settle-sparse/24-qubits` limit below applies to a width-24 record
only, and a width-32 record takes `settle-sparse/32-qubits` instead.

## Shards

A shard (`--shard K --shards N`) runs the replicates congruent to K modulo N, and no shard sees the others' verdict
counts, so it runs every case to its limit. `--limit ARM=N` (every case of the arm) or `--limit ARM/CASE=N` stops a
case below replicate N and enters no record: when the merged rows reach the case's verdict count below the limit,
the merged record is byte for byte the unsharded run at the plan's cap, and `--merge` refuses a case its limit cut
short of that count. The replicates each case of the arm's last unsharded run needed, plus a margin, set the
limits; on the width-24 record above, each case's replicates plus 10 % give

```text
carryover-positive=390 carryover-negative=420 q-minority=500 plateau-minority=1150 plateau-retained=17300
settle-sparse/8-qubits=9800 settle-sparse/9-qubits=3550 settle-sparse/24-qubits=2350
```

An arm-wide `--cap ARM=N` also bounds the work but changes the record's
`cap` field, so its record differs from the design table's in that field.

Merge and check:

```sh
"$PYTHON" -B scripts/msq_successor_null.py --merge OUT/ARM-shard*.json --out OUT/ARM.json
```

Before a shard record enters evidence, the host recomputes the first two and the last replicate of each shard
with `msq_successor_null_batch.analyse_block` and compares the rows byte for byte.

### Kaggle CPU kernels

`scripts/kaggle_run.py push --ci-env --dataset ...` with the record's inputs in a private dataset (the script
limit is 1 MB). One Kaggle vCPU ran the null 2.9 times slower than a build-host thread (4000 plateau-retained
replicates in 24 to 46 minutes on four vCPUs), and setup takes about 2.5 minutes.

### Hosted runners

[.github/workflows/null-shards.yml](../../.github/workflows/null-shards.yml) runs up to 20 shards in parallel on
the public repository's runners (four vCPUs each); its logs and artifacts are public. The record input takes one or
several space-separated record directories, run through one pool in each shard, and the limits take the `RECORD:`
prefix; the directories must be on the dispatched ref. With several records, each shard's artifact holds
`RECORD/ARM-shardK.json` per record, and the merge reads `OUT/null-shard-*/RECORD/ARM-shard*.json`.

```sh
gh workflow run null-shards.yml --ref BRANCH -f record_dir="RECORD [RECORD ...]" -f arms=all \
  -f limits="LIMITS" -f shards=20
gh run download RUN_ID --dir OUT
```

`gh run download` extracts each artifact `null-shard-K` into its own directory, holding the shard records, `lscpu`
and `/usr/bin/time -v` of its job (the runner's per-replicate speed), so the merge reads across them:

```sh
"$PYTHON" -B scripts/msq_successor_null.py --merge OUT/null-shard-*/ARM-shard*.json --out OUT/ARM.json
```
