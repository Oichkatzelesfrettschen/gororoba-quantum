# Serialized Ascella order replay

The [producer](producer.py) executes the failed acquisition's actual serialized
computation on local Perceval SLOS and Naive backends with network connections
forbidden. Both backends complete eight settings with 65,536 simulated samples.
Sixteen probability comparisons agree with the frozen manifest within 4.45e-16.

The [retained report](replay.json) binds its producer, dependencies and both
failed and successful request bodies by SHA-256. The producer compares the two
bodies after removing only the top-level `process_id`. Every other request
field must match. The [hardware acquisition](../../quandela/runs/ascella-mosaiq-update-order-retry/README.md)
separately establishes successful physical sampling. The local replay tests
ideal request semantics; the hardware instrument configuration remains outside
its execution boundary.

Run from the repository root with the pinned Perceval 1.3.1 and exqalibur 1.4.2
environment:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" results/local-simulation/ascella-serialized-order-replay/producer.py --check
```

The checksum-bound parent README retains its original bytes. This separate
note documents the newly retained replay without rewriting that artifact.
