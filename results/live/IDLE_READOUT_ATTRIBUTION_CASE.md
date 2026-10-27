# Readout attribution on ibm_kingston: written case

Status: approved by the owner on 2026-10-27 and submitted that day as job `dbgfiu1j4t8s73ac91f0` on the backup
account; the run awaits collection. The design, its two reviews and the validation evidence are in [heron-idle-readout-attribution.md](../../docs/design/heron-idle-readout-attribution.md).

## Question

The idle-penalty probe ([findings](IDLE_PENALTY_PROBE_FINDINGS.md)) found idling qubits pulled by a negative phase
rate while readout trains played (pair mean -2.72 kHz, up to -21.5 kHz on one probe). Every pair's partner read at
once, so the run cannot say whether the pull comes from the probe's own partner reading, from readers within three
CZ hops, or from readout anywhere on the chip. This run splits the shift per probe into an own-partner term a_p, a
within-three-hop excess c_p and a chip baseline b, by playing the trains on complementary halves of the pairs.

## Why a simulation cannot answer it

Aer carries no readout crosstalk: the dry run's predictions read b = +0.037 kHz with an interval [-0.169, 0.211]
that contains zero, an additive model and an unresolved attribution, which is the null every measured value is
read against. The shift exists only on the device.

## Design

- Campaign `idle_readout` (`gororoba_quantum/idle_readout.py`): 55 PUBs in one dynamic job. 23 members kept from the
  probe carry the all-read shift, its short-window unwrap and its quiet references; 32 patterned members play the
  trains on class A or class B partners under two class partitions, long and short windows, both quadratures and
  both probe roles. Quiet replicas run the reading body with the partner's train replaced by an idle.
- Placement: the stability repeat's 30 ordered pairs, pinned (the pin string of
  [IDLE_PENALTY_REPEAT_CASE.md](IDLE_PENALTY_REPEAT_CASE.md) after its amendment of 2026-10-27, which drops
  (155,154)); the class strings index those paths in pin order.
- Validation (not binding): a dry run under the 2026-10-27T07:53:14-07:00 calibration admitted all 30 paths; a
  local ALAP schedule of every patterned PUB put each replica's probe window at 561 to 10561 dt and every reading
  train inside every quiet window (7168 pairs); the predictions passed the self-check.

## Backend, account, shots and seconds

- Backend: ibm_kingston (Heron r2), pinned.
- Account: `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` for the dry run, submit and collect. The backup held
  229 s at 2026-10-26 20:04 PDT; the focal jobs' ceilings (50 s) come first, and this run needs its 30 s ceiling plus
  the 60 s reserve after them (`--reserve-seconds 60`).
- Shots: 4096 per PUB, 55 PUBs, twirling off, dynamical decoupling none, isolated reference off, 20 us repetition
  delay.
- Expected charge: 20 s by count scaling from the probe's 16 s for 44 PUBs; the binding dry run's estimate governs.
  Ceiling 30 s.
- Expected credits: none beyond the plan's QPU seconds.
- Seeds: `--seed-transpiler` and `--seed-simulator` from a fresh ANU draw; the bootstrap seeds from
  `docs/evidence/anu_qrng/draw-2026-10-27T034547Z.json`, index 2 for the dry run's self-check and index 3 for the
  measured analysis.
- No 50 us fallback: a zero-execution service error stops the run and goes to the owner.

## Preregistered decisions

The design's "Preregistered decisions" section holds them, computed by `scripts/idle_readout_attribution.py` on the
collected run after its exposure gate: per-probe labels (descriptive), the far-field baseline b with its
class-agreement diagnostic, additivity, attribution (own-partner, within-three-hop, baseline, mixed, opposed,
withdrawn or unresolved) and the replication of the probe's shift by a t-only rule.

## Binding record

Filled from the binding dry run that `scripts/approved_run.sh` made and submitted in one invocation; if the
calibration had moved before the submit, the submit would have written `approval_required` and the runner would have
planned again with identical flags under the same approval.

| Field | Value |
|---|---|
| Seeds | `--seed-transpiler qrng:docs/evidence/anu_qrng/draw-2026-10-27T191741Z.json#0`, `--seed-simulator ...#1` |
| Binding dry run | `results/live/2026-10-27T191809.705421Z` |
| record.json sha256 | `d4778defcfd6e4451c858a3317cf74abdd6af09013fbf71aa1d0ead60c58b8e4` |
| Calibration | 2026-10-27T12:00:41-07:00, fingerprint `4c64033641083258a2b7c977f31b582493a4c7cc86528f7ea07887a10b60b179` |
| Self-check | b -0.162 kHz [-0.333, 0.017], class agreement, additive, attribution unresolved: passes |
| Submitted run | `results/live/2026-10-27T191953.122214Z`, job `dbgfiu1j4t8s73ac91f0`, `submission.complete` true |
| Backup remaining at plan | 197 s |

## Commands

From `gororoba_quantum/`, with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `PYTHON` exported,
`GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform`, `PIN` the pin string and `D` the new ANU draw:

```sh
"$PYTHON" live_run.py --groups idle_readout --backends ibm_kingston --max-pending 300 --shots 4096 \
  --rep-delay 0.00002 --no-isolated-reference --max-execution-seconds 30 --max-total-execution-seconds 30 \
  --reserve-seconds 60 --pin-layout "$PIN" --max-replicas 30 \
  --seed-transpiler "qrng:$D#0" --seed-simulator "qrng:$D#1" --out ../results/live
"$PYTHON" ../scripts/idle_readout_attribution.py RUN --self-check \
  --seed "qrng:docs/evidence/anu_qrng/draw-2026-10-27T034547Z.json#2"
"$PYTHON" live_run.py ... (the same flags) --submit --approved-record RUN --approved-record-sha256 SHA
"$PYTHON" live_run.py --collect RUN_SUBMITTED
"$PYTHON" ../scripts/idle_readout_attribution.py RUN_SUBMITTED \
  --seed "qrng:docs/evidence/anu_qrng/draw-2026-10-27T034547Z.json#3" --out RUN_SUBMITTED/idle-readout-attribution.json
```
