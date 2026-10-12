# Mixed static and dynamic PUB client qualification

The retained probe exercises Runtime 0.50.0 client-side Sampler and Executor
through a credential-free CPU Aer backend. One circuit list contains a dynamic
Clifford circuit with measurement, `if_else`, and reset, followed by a static
Clifford circuit. Each PUB uses 64 shots. Explicit result validation checks both
deterministic distributions and returned order under normal and optimized Python.

The probe uses the local service. The probe establishes client preparation, local execution, and result decoding. Hardware service acceptance, scheduling, calibration continuity, hardware subjob count, and charged overhead require separate evidence. The local Executor implementation iterates program items through Aer; one LocalRuntimeJob does not establish one hardware subjob.

The formatted source retains the original circuit construction and replaces its
assertion with an explicit failure. The two retained result files come from fresh
replays of that source with warnings treated as errors. Each replay returns one
`LocalRuntimeJob`, with dynamic counts `{"11": 64}` and static counts `{"01": 64}`.

Replay command (from the repository root):

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "$PYTHON" -W error results/local_compute/mixed_pub_client/probe.py
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 "$PYTHON" -O -W error results/local_compute/mixed_pub_client/probe.py
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error results/local_compute/mixed_pub_client/check_probe.py
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error results/local_compute/mixed_pub_client/check_probe.py
ruff check results/local_compute/mixed_pub_client/probe.py results/local_compute/mixed_pub_client/check_probe.py
ruff format --check results/local_compute/mixed_pub_client/probe.py results/local_compute/mixed_pub_client/check_probe.py
mypy results/local_compute/mixed_pub_client/probe.py results/local_compute/mixed_pub_client/check_probe.py
(cd results/local_compute/mixed_pub_client && sha256sum -c SHA256SUMS)
```

`result.json` and `result-optimized.json` retain the normal and optimized
outputs. `status.json` records commands, exit statuses, and source/output hashes;
`SHA256SUMS` binds every published file. `RUNTIME_AUDIT.md` and
`registry_detection.json` record the scoped migration-skill audit. The probe
reads its installed dependencies and writes JSON to stdout; evidence capture
writes only inside this directory. Hardware submission and raw hardware results
remain separate evidence surfaces.
