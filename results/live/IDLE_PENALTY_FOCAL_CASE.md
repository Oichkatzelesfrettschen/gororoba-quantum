# Idle-penalty focal placement on ibm_kingston: written case

Status: approved by the owner on 2026-10-26 ("design and execute the plan to continue forward logically to burn
through this"), in reply to an enumeration that stated this envelope: two jobs of about 16 s each on the backup
account, placing qubits 79, 92 and 93. The approval covers the rule and bounds below; the binding records are the
dry runs made right after the stability repeat's dry run, under its calibration.

## Question

Retained Kingston runs `2026-10-12T055624.091217Z` and `2026-10-13T020454.599853Z` charged idle qubits a multiplier
near 3 over the region 73, 79, 92, 93, 94 and 95. The idle-penalty probe ([findings](IDLE_PENALTY_PROBE_FINDINGS.md))
placed 73, 94 and 95 and read 73 and 94 nominal on every endpoint; its quality-ranked placement never chose 79, 92
or 93. This case places those three under one calibration with a full cohort beside them, and reads whether any of
them carries the excess today.

The same jobs place the five N=21 qubits the probe never reached (104, 106, 124, 125 and 126), so the replay of the
retained N=21 runs with measured idle and readout parameters has measured values on all eight of its qubits
(104-107, 117, 124-126) instead of three.

## Why a simulation cannot answer it

Aer draws from the reported T1, the echo T2 and the assignment errors, and reads kappa near 1 on every qubit by
construction (the dry-run self-check). Whether a named qubit relaxes or dephases faster than its reported values is
a property of the device.

## Design

The campaign, members, ladders, shots and analyzer are those of the stability repeat
([IDLE_PENALTY_REPEAT_CASE.md](IDLE_PENALTY_REPEAT_CASE.md)): 44 two-qubit members, 4096 shots, 20 us repetition
delay, no twirling, no dynamical decoupling, no isolated reference, one dynamic job each. Each job pins the repeat's
31 ordered pairs, except where a new pair would sit within one CZ hop of a cohort pair; that cohort pair gives its
slot to the new pair. Path 0 stays (150,149), so replica 0 and the campaign digest are the first run's.

93 neighbors both 79 and 92 on the coupler graph (`docs/evidence/heron_platform/targets.json`), and
`pinned_replicas` keeps paths one CZ hop apart, so the three need two jobs. The first-listed qubit of each pair is
the target:

| Job | New ordered pairs | Cohort pairs replaced | Paths |
|---|---|---|---|
| X | 79,73 / 92,91 / 104,103 / 106,107 / 126,125 | 105,117 / 90,89 / 74,73 / 97,107 / 96,103 | 31 |
| Y | 93,94 / 124,123 | 94,95 | 32 |

```text
X ibm_kingston:150,149/21,36/141,140/79,73/16,3/94,95/57,47/1,0/44,45/14,13/82,81/33,32/92,91/104,103/49,50/77,65/144,145/71,70/109,110/132,133/61,62/59,55/19,35/155,154/27,28/106,107/6,7/11,18/101,100/130,129/126,125
Y ibm_kingston:150,149/21,36/141,140/105,117/16,3/93,94/57,47/1,0/44,45/14,13/82,81/33,32/90,89/74,73/49,50/77,65/144,145/71,70/109,110/132,133/61,62/59,55/19,35/155,154/27,28/97,107/6,7/11,18/101,100/130,129/96,103/124,123
```

A pinned path with an excluded qubit or edge refuses the plan. The job then runs without substitution at the next
calibration that admits it, and the case reports which focal qubit the calibration excluded.

## Backend, account, shots and seconds

- Backend: ibm_kingston (Heron r2), pinned.
- Account: `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` for each job's dry run, submit and collect. The primary
  account's remaining seconds after the repeat fall below its 60 s reserve plus these ceilings; the backup holds
  its own rolling window: 229 s remaining at the validation dry runs (2026-10-26 20:04 PDT), against the same
  60 s reserve, read again before the binding dry runs and before each submit.
- Shots: 4096 per PUB, 44 PUBs per job.
- Expected charge: 16 s per job, the probe's billed seconds for the identical job shape; 32 s for both. Ceiling 25 s
  per job, 50 s in total.
- Expected credits: none beyond the plan's QPU seconds.
- Seeds: one ANU draw at binding time serves the repeat (indices 0 and 1), job X (2 and 3) and job Y (4 and 5).
- Order: the stability repeat submits first, then X, then Y, all from dry runs made under one calibration. No 50 us
  fallback; a zero-execution service error stops the remaining jobs and goes to the owner.

## Preregistered decisions

Fixed before these jobs' data. `scripts/idle_penalty_focal_decisions.py` computes every decision from the jobs'
`idle-penalty-report.json` files:

```sh
"$PYTHON" ../scripts/idle_penalty_focal_decisions.py X/idle-penalty-report.json Y/idle-penalty-report.json \
  REPEAT/idle-penalty-report.json --focal 79,92,93 --context 104,106,124,125,126 \
  --region 73,79,92,93,94,95 --out X/idle-penalty-focal-decisions.json
```

1. **Per focal qubit and multiplier** (descriptive): kappa_1, kappa_2* and kappa_2e with their standard errors,
   a reading against fixed thresholds ("elevated" when the value less 1.96 standard errors exceeds 1.5, "nominal"
   when the value plus or minus 1.96 standard errors lies inside [0.67, 1.5], otherwise "unresolved"), and the
   value's rank in its own run's cohort. These readings decide nothing: the cohort's tail is heavy, and on the
   probe run 25 of 62 qubits read elevated on kappa_1 or kappa_2*, so three random qubits would show at least one
   elevated reading with probability 0.79.
2. **Historical reading**, over the region the retained runs fitted one kappa near 3 on (73, 79, 92, 93, 94 and
   95): the six qubits against the rest of the pooled cohort, each qubit once from the first report that holds it
   (repeat, then X, then Y), by a one-sided exact Mann-Whitney test on kappa_1 and on kappa_2*. "Supported" when
   either p falls below 0.025, a false-positive rate of at most 0.05 for six exchangeable qubits; "weakened" when
   the region's median lies at or below the rest's median on both multipliers; otherwise "unresolved". Supported
   places a present-day excess on the region; weakened leaves drift over two weeks or the retained runs' own gates
   and measurements as the accounts of kappa near 3. Neither reconstructs the two-week-old rates.
3. **Same window**: the repeat, X and Y report one execution calibration stamp. A split reports each job against
   its own cohort and states the split.
4. **Test-retest floor** (descriptive): over qubits that keep role and partner between any two of the three runs,
   Pearson r and the median-ratio band, the statistics `--compare` reads across calibrations, here under one
   calibration. They calibrate how much of a cross-calibration difference is run-to-run noise.

The context qubits 104, 106, 124, 125 and 126 carry no decision here; their values enter the N=21 replay.

Validation dry runs under the 2026-10-26T19:09:26-07:00 calibration (not retained) admitted all 31 paths of X
and all 32 of Y, passed `--self-check` and `--check-placement` against a live export, and carried campaign digest
`bf6be296...`.

## Binding records

Filled from the dry runs made right after the repeat's dry run:

| Job | Run directory | record.json sha256 | Calibration |
|---|---|---|---|
| X | pending | pending | pending |
| Y | pending | pending | pending |

Each job's campaign digest must equal `bf6be296...`, the first run's. If the calibration values move before a
submit, that submit writes `approval_required` and sends nothing; its dry run is remade with the identical flags
and submitted under this approval.

## Commands

From `gororoba_quantum/`, with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `PYTHON` exported,
`GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform`, `PIN` the job's pin string and `N` its path count (31 or 32):

```sh
"$PYTHON" live_run.py --groups idle_penalty --backends ibm_kingston --max-pending 300 --shots 4096 \
  --rep-delay 0.00002 --no-isolated-reference --max-execution-seconds 25 --max-total-execution-seconds 25 \
  --reserve-seconds 60 --pin-layout "$PIN" --max-replicas "$N" \
  --seed-transpiler "qrng:$D#I" --seed-simulator "qrng:$D#J" --out ../results/live
"$PYTHON" ../scripts/idle_penalty_report.py RUN --self-check --check-placement --snapshot SNAPSHOT
"$PYTHON" live_run.py ... (the same flags) --submit --approved-record RUN --approved-record-sha256 SHA
"$PYTHON" live_run.py --collect RUN_SUBMITTED
"$PYTHON" ../scripts/idle_penalty_report.py RUN_SUBMITTED --out RUN_SUBMITTED/idle-penalty-report.json
```
