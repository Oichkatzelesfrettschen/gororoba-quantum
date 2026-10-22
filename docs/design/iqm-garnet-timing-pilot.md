# IQM Garnet timing pilot

The pilot measures what IQM Resonance bills for a circuit job on Garnet: the
fixed cost of a job, the cost of one shot, the cost of one more circuit at
equal total shots, and the change when active reset replaces the calibrated
passive reset. Every later IQM case is priced from these four numbers, and
the account's 30.00 credits (60 s on Garnet at 0.50 credits/s) expire
2026-11-01.

## Why it needs the service

Billing is a property of IQM Server, not of the circuit: a job is charged its
runtime rounded up to whole seconds times the price per second
([README](../notes/iqm/README.md#cost)), and the runtime includes whatever the
control stack spends between shots and circuits. No simulator models that.
The calibration set gives the prior: `reset_wait` lasts 298 us on Garnet,
the end delay 2 us and the readout 480 ns
([calibration set](../evidence/iqm/qc/garnet/calibration/set.json)), so
passive reset bounds a shot at about 0.3 ms and 3300 shots per billed second.

## Case

`scripts/iqm_jobs.py build results/iqm/cases/timing-pilot` writes the case;
gate `core-635` regenerates it byte for byte. Every circuit is `prx(angle=pi,
phase=0)` on QB1 followed by `measure` with key `m`, ideal P(1) = 1, with
`heralding_mode` `none`.

| job | circuits x shots | reset | prior seconds | ceiling at 0.50/s |
|---|---|---|---|---|
| `j1-1x1000-passive` | 1 x 1000 | passive | 0.3 | 0.50 |
| `j2-1x4000-passive` | 1 x 4000 | passive | 1.2 | 1.00 |
| `j3-20x200-passive` | 20 x 200 | passive | 1.2 | 1.00 |
| `j4-1x4000-active1` | 1 x 4000 | `active_reset_cycles` 1 | 1.2 | 1.00 |

The four `garnet:mock` jobs run first at 0.00 credits/s. They prove the
request format, return the compiler's
`execution_runtime_estimate_seconds`, and show whether the server accepts
`active_reset_cycles`; a mock refusal of j4 drops j4 from the hardware run.
The Garnet jobs then run in order j1 to j4. The ceiling column is the prior
rounded up; the service bills the measured runtime, so the case approves at
most 1.50 credits per job and 6.00 for the four, and the pilot stops after
any job whose charge exceeds its 1.50.

## Readout

From each completed job's `metrics` (`execution_seconds`, `runtime_seconds`,
`billed_seconds`) and the credit read before and after it:

- per shot: (j2 - j1) / 3000 shots, against the 0.3 ms prior;
- per job: j1 minus 1000 times the per-shot cost;
- per circuit: (j3 - j2) / 19 extra circuits;
- active reset: j4 - j2, and whether the server ran it;
- the compiler estimate against the measured runtime for every job.

P(1) of every circuit checks that the job ran the circuit sent; a value far
from Garnet's QB1 readout (error_1_to_0 0.0174 in the 2026-10-22 metrics)
flags the job. The pilot asks no physics question; its numbers enter the
next IQM case as its pricing source.

## Commands

```sh
export PYTHON="${PYTHON:-python3}" IQM_TOKENS_FILE=TOKENS.json
CASE=results/iqm/cases/timing-pilot
HEX=$(sha256sum "$CASE/cases.json" | cut -d' ' -f1)
"$PYTHON" scripts/iqm_jobs.py submit "$CASE" j1-1x1000-passive --qc garnet:mock \
  --approval "QUOTE" --approved-cases-sha256 "$HEX" --max-credits 1.5 --dry
"$PYTHON" scripts/iqm_jobs.py submit "$CASE" j1-1x1000-passive --qc garnet:mock \
  --approval "QUOTE" --approved-cases-sha256 "$HEX" --max-credits 1.5
"$PYTHON" scripts/iqm_jobs.py collect results/iqm/runs/STAMP-garnet_mock-timing-pilot-j1-1x1000-passive
```

`submit` refuses a job whose quantum computer, case and job already have a
run directory, writes `submission-state.json` before it posts, and records
the quoted approval; `collect` keeps the job record and the measurements and
counts artifacts byte for byte under `raw/`.
