# Primorial coherence case 3: retained evidence

[PRIMORIAL_COHERENCE_CASE_3.md](../../../../results/live/PRIMORIAL_COHERENCE_CASE_3.md) is the case: the split
excitation law on 22 ibm_kingston paths at a 20 us repetition delay, on the backup instance. Every file here
derives from the run records under `results/live/` named below; the decision code is commit 386011f.

## Runs

| run | job | stage | billed | execution calibration |
| --- | --- | --- | ---: | --- |
| `2026-10-27T010741.272123Z` | `dbfvivljm0ks73efhsm0` | prep0 (A) | 3 s | 2026-10-26T17:47:10-07:00 |
| `2026-10-27T010917.104805Z` | `dbfvjktrd2mc73ctl290` | x_history (A) | 3 s | 2026-10-26T17:47:10-07:00 |
| `2026-10-27T011025.944327Z` | `dbfvk5drd2mc73ctl3hg` | x_history (B) | 3 s | 2026-10-26T17:47:10-07:00 |
| `2026-10-27T011140.821404Z` | `dbfvkoljm0ks73efi0jg` | prep0 (B) | 3 s | 2026-10-26T17:47:10-07:00 |
| `2026-10-27T011538.241671Z` | `dbfvntdrd2mc73ctlbo0` | stage 1, probes, 800 shots | 5 s | 2026-10-26T17:47:10-07:00 |
| `2026-10-27T013626.332783Z` | `dbg0118iudkc73e3e100` | stage 2, gap-88, 4000 shots | 16 s | 2026-10-26T19:09:26-07:00 |

The case billed 33 s against its 33 s expectation and 40 s stop. No member's calibration changed during its
shots. Stage 2 waited 76 minutes in the queue.

## Files

- `split.json`: `state_prep_split.py` over the four controls.
- `stage1-snapshot.json`: the calibration at stage 1's execution start (`calibration_snapshot.py --export
  --at`).
- `stage1-decision.json`: `--decide-paths` with the split, `--gap88-cap 4000`, `--positive-paths 147,148,149`.
- `stage2-snapshot-a.json`, `stage2-snapshot-b.json`: the calibration at stage 2's execution start, read at
  02:59Z and again at 03:11Z.
- `stage2-crosstalk.json`, `stage2-falsification.json`: the preregistered checks.
- `lambda-bracket.json`: lambda on 147-148-149 with every hd of the path at the lower and at the upper end of
  its interval, the reporting item the case names.

## Results

- **Controls.** No qubit's pooled prep0 fraction exceeds 0.2. q147 reads excited in 0.08 percent of prep0 and
  4.89 percent of x_history shots, hd 0.0484 in [0.0446, 0.0523]; both replicates of each arm agree (p 0.41 and
  0.45) and the two pairs' raw differences are 0.0475 and 0.0486, so the excess follows the shot history, not the
  job. q58 and q92 read heterogeneous: q58's prep0 differs between its two jobs (p below 1e-4), which widens its hd
  interval to [0, 0.040].
- **Decision.** All 22 paths enter stage 2 at 4000 shots, 21 under the case-2 rule and 147-148-149 as a
  positive-prediction path (p95 max_z 1.65, identification need 6462 shots per reading).
- **Calibration identity.** Kingston published the label 19:09:26 between the decision (17:47:10) and stage 2's
  execution. The channel digest over the 66 stage-2 qubits is `12bc42f7349d711b...` in the decision snapshot
  and in both stage-2 reads, so every value the law reads held; the claim is a device claim.
- **Crosstalk.** The first gap-88 member on 147-148-149 against its isolated reference: chi-square 6.96 on 7
  degrees of freedom, p 0.43, consistent.
- **Bands.** 150 of 154 coefficients lie inside their bands. 58-71-72, 15-19-35 and 100-101-102, outside in
  case 2, lie inside. Four lie outside, all above their bands and within 0.22 half-widths of the edge: 38-49-50
  coefficient 2 (1.08 half-widths from center), 66-67-68 coefficient 1 (1.04), 132-133-134 coefficients 01
  (1.07) and 1 (1.22). By the preregistered rule they falsify the split law with the coherent-error model on
  those three paths. The 01 deviations across the 22 paths lean positive, which points at a shared offset more
  than at three path-specific failures; a pooled offset test is outside the preregistration and not run.
- **Positive prediction.** 147-148-149's coefficient 2, where the probes predicted q149's detuning to survive
  the null subtraction, reads 0.74 half-widths above its center, inside its band.
- **Split against terminal.** On 147-148-149, the only path past the 2-spread floor (3.97 spreads), lambda is
  0.66 +- 0.25; across hd's interval it runs from 0.59 to 0.74. The excess is not absorbed by the in-job
  inversion (lambda 0 excluded at 2.6 standard errors) and sits below its all-|1>-history value (lambda 1 at 1.3),
  as an initial population scaled by how often the previous shot leaves q147 excited would.
