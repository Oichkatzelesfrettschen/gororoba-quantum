# Successor null: one pool, Kaggle and hosted-runner shards

`scripts/msq_successor_null.py` runs the measurement-sequence successor's classical null
([design](../design/measurement-sequence-envelope-successor.md#null-calibration)). Every route below writes the
bytes of one unsharded single-arm run per arm, so their records merge, summarize and replay alike.

## One host, every arm

```sh
"$PYTHON" -B scripts/msq_successor_null.py results/live/RECORD --arms all --out-dir OUT
```

One setup and one process pool serve every arm of `msq_successor_null_batch.NULL_PLAN`, at its caps and seeds.
Each round fills the pool with two blocks per worker across all running cases (`round_size`), and an arm with a
verdict count stops each case at it. Measured on the 6-core build host (12 threads), on the width-24 record
`2026-10-28T163139.827337Z`: the arms carryover-positive, q-tolerance, plateau-low and gamma took 222 s wall
for 1886 CPU-s in one call, against 415 s run one arm at a time on four workers. The full plan is about
20 000 CPU-s on this host.

## Shards

A shard (`--shard K --shards N`) runs the replicates congruent to K modulo N and every case to its cap, since
no shard sees the others' verdict counts. `--cap ARM=N` sets a cap near the arm's verdict count, read from the
replicates the arm's last unsharded run needed plus a margin, so the overshoot stays small; a merged record whose
case misses its verdict count needs a rerun at a larger cap. The cap is part of the record identity, so a record
run at an overridden cap differs from the design table's in that field.

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
the public repository's runners (four vCPUs each); its logs and artifacts are public. The record directory must
be on the dispatched ref.

```sh
gh workflow run null-shards.yml --ref BRANCH -f record_dir=RECORD -f arms=all \
  -f caps="settle-sparse=11000 plateau-retained=19000" -f shards=20
gh run download RUN_ID --dir OUT
```

Each artifact `null-shard-K` holds the shard records, `lscpu` and `/usr/bin/time -v` of its job, which give the
runner's per-replicate speed.
