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
for 1886 CPU-s in one call, against 415 s run one arm at a time on four workers. The full plan, `--arms all` at
the plan's caps, took 4185 s wall for 29 800 CPU-s (712 % of the 12 threads) while other jobs shared the host (load
average 12 to 20 at its end), and wrote every arm record the retained summary names, plateau-retained included.

## Shards

A shard (`--shard K --shards N`) runs the replicates congruent to K modulo N, and no shard sees the others' verdict
counts, so it runs every case to its limit. `--limit ARM=N` (every case of the arm) or `--limit ARM/CASE=N` stops a
case below replicate N and enters no record: when the merged rows reach the case's verdict count below the limit,
the merged record is byte for byte the unsharded run at the plan's cap, and `--merge` refuses a case its limit cut
short of that count. The replicates each case of the arm's last unsharded run needed, plus a margin, set the
limits; on the record above, each case's replicates plus 10 % give

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
the public repository's runners (four vCPUs each); its logs and artifacts are public. The record directory must
be on the dispatched ref.

```sh
gh workflow run null-shards.yml --ref BRANCH -f record_dir=RECORD -f arms=all \
  -f limits="LIMITS" -f shards=20
gh run download RUN_ID --dir OUT
```

`gh run download` extracts each artifact `null-shard-K` into its own directory, holding the shard records, `lscpu`
and `/usr/bin/time -v` of its job (the runner's per-replicate speed), so the merge reads across them:

```sh
"$PYTHON" -B scripts/msq_successor_null.py --merge OUT/null-shard-*/ARM-shard*.json --out OUT/ARM.json
```
