# Ascella approved order retry

The user authorized one retry of the unchanged eight-setting order pilot after
the instrument-error execution hold. The retained user words are:

> ascella authorized.

> our belenos run has been submitted. keep doing wha tyou are doing but the ascella run is approved for your subagent to handle.

The user then constrained the ordering:

> wait for the belenos queue to clear and our job to pull by the claude agent.

The [planned case directory](../../results/quandela/cases/ascella-hypercomplex-order-approved-retry/)
contains byte-identical copies of the original order pilot's frozen inputs.
The case manifest SHA-256 is
`1d1b9abfe727d92f6af1c81002b3e41e056b1b16330d3b8ae9746303bc3968fa`;
the circuit SHA-256 is
`f2e7ea115d91f962cb045e824d8d3f5c3da432fe0b812e0e58dfc7b23f7ac550`.
Each of eight settings permits at most 8192 detected samples and 16384 shots.
The aggregate caps are 65536 samples, 131072 shots, 180 seconds and
1.016384 credits under the recorded tariff
`1 + 0.000001 * largest_iteration_max_shots`.

The device question concerns measured photonic mesh conformance, loss and
drift. Local synthesis validates the requested operator; a local simulation
cannot measure Ascella's instrument or establish recovery from the retained
`hardware_info.circuit_input_ports` configuration error. The
[instrument-readiness design](ascella-instrument-readiness-and-packed-tests.md)
owns that incident and its evidence boundary. The original failed job
`e6f2cc2d-e4f8-4b78-ad4a-d16dbf8e9f95` retains its receipts and zero-sample
result in its original directory.

## Admission and execution

The retry waits until Belenos job
`4058ce4e-7892-4da4-9e86-7f78f5fa9777` reaches a terminal status, the token's
running and queued counts both equal zero, and the independent Claude
collector retains that Belenos result. Read-only observations through
21:30:26 UTC on 22 October 2026 reported `waiting`, zero shots, zero running
jobs and one queued job. The [bounded observation record](../evidence/quandela/ascella-order-pilot-retry-preflight/approval-wait.json)
retains the observation and separates the planned retry from an acquisition.
The observer performs status and occupancy GETs; the observer never submits
or cancels a job.

After those checks, refresh the catalogue, processor, token occupancy, public
per-shot tariff and software versions. The token cannot read the authenticated
current per-job offer or remaining account balance. The one-credit job price
remains a recorded tariff rather than a fresh authenticated quote. A changed
case or an increased charge requires another user decision. `available`
establishes the reported platform status; a successful acquisition must
establish instrument recovery.

Run from the checkout root with the intended `PYTHON`,
`QUANDELA_TOKEN_FILE` and
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` exported:

```sh
RETRY=results/quandela/cases/ascella-hypercomplex-order-approved-retry
"$PYTHON" scripts/qd_platform.py plan "$RETRY" \
  --platform qpu:ascella --max-credits 1.016384 \
  --expected-seconds 180 --per-job-credits 1
```

The planned directory carries only frozen case inputs. The research-state
adapter treats every directory under `results/quandela/runs/` as a retained
job and requires a submission receipt, so the planned directory stays under
`cases/` as the immutable planned source. At admission, create the single new
`results/quandela/runs/ascella-hypercomplex-order-approved-retry` directory and
copy only its `cases.json` and `circuit.json` from the planned source. Verify
both copied SHA-256 identities against the values above, repeat the guarded
plan on the run directory, and invoke `qd_platform.py submit` once with the same caps and
the actual quoted authorization above. Preserve the submit checkpoint before
reconciliation; an ambiguous POST response permits read-only reconciliation,
never a blind second POST. Collect through `qd_platform.py collect`, preserve
raw bytes, and integrate the actual acquisition into the research registry
with its receipt and observed debit.

A repeated instrument error or zero-sample result ends the authorization.
The authorization covers one attempt with the frozen order pilot. Different
families, simulator jobs, QRNG reads, bookings, notebooks and rerun endpoints
require their own approval. The active Belenos acquisition remains owned by
its independent collector throughout the wait.

## Temporary observer retention

The local observer's temporary script and JSON-lines log implement repeated
read-only calls to `qd_platform.get(qd_platform.job_route(JOB, "status"))`
and `qd_platform.availability()`, with a 55-second poll interval. Each row
records UTC time, job identity, status, shots, progress, occupancy and a
terminal-plus-idle boolean. The retained bounded observation preserves the
decision-bearing fields. Host-specific launcher paths, repeated unchanged
rows and interpreter caches remain local runtime material. The observer
continues in its existing terminal session until the admission condition
changes; the planned record supplies neither a submission receipt nor a
fabricated job identity for the retry.
