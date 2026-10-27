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
- `offset_and_history.py` (run from the repository root) and its output `offset-and-history.json`: the two
  post-hoc analyses below, chosen after the stage-2 results were read. The script's docstring holds the
  predictions written before its first run and labels each item added after it.

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
  those three paths. The post-hoc pooled offset test below finds no single offset behind the four.
- **Positive prediction.** 147-148-149's coefficient 2, where the probes predicted q149's detuning to survive
  the null subtraction, reads 0.74 half-widths above its center, inside its band.
- **Split against terminal.** On 147-148-149, the only path past the 2-spread floor (3.97 spreads), lambda is
  0.66 +- 0.25; across hd's interval it runs from 0.59 to 0.74. The excess is not absorbed by the in-job
  inversion (lambda 0 excluded at 2.6 standard errors) and sits below its all-|1>-history value (lambda 1 at 1.3).
  The post-hoc shot-history analysis below rejects the reading of lambda as a population scaled by how often the
  previous shot leaves q147 excited.

## Post-hoc analyses

Both use the retained records only and are descriptive; neither is part of the preregistration.

**Pooled offset.** Each coefficient's residual is (observed - shift_center) / shift_spread over the 22 paths,
pooled by inverse variance; the excitation envelope stays out of the spread. The scatter chi-square about each
offset reaches 1.7 to 2.7 per degree of freedom on 0, 01, 1 and 2 (21 degrees of freedom), so the spreads
understate the path-to-path scatter, and each offset is judged on a standard error scaled by
sqrt(chi-square / dof) at the Bonferroni level over seven coefficients (alpha 0.05 / 7, |z| 2.69).
- Offsets on 01 (+0.0080, scaled z 2.86), 02 (+0.0107, 5.73) and 2 (+0.0155, 4.86) pass; 1 (+0.0081, 2.15),
  0, 12 and 012 do not. Leaving out 147-148-149, or moving its center to its measured lambda, changes no verdict.
- The four misses, each rechecked against its unchanged band after subtracting the offset fitted on the other 21
  paths: 38-49-50 coefficient 2 returns inside under a significant offset (z 4.65); 66-67-68 coefficient 1 and
  132-133-134 coefficient 01 return inside only under offsets that fail the test (z 1.82 and 2.59);
  132-133-134 coefficient 1 stays outside (1.08 half-widths). No new miss appears.
- The same fit on case 2 (`../case2/`, the same circuits, estimators, paths and delay). Case 2's retained
  centers applied each path's largest excitation to all three qubits, and the excitation term moves 01, 02, 12
  and 012 (case 3's envelope reaches 1.8 spreads on 01) while leaving 0, 1 and 2 within 0.005 spreads, so the
  fit recenters all 21 case-2 paths under the split law from case 2's own two controls, swapping only the
  incoherent shift and keeping every spread; the swapped shifts reproduce the case-2 ablation's split variant on
  its four paths exactly. Case 2 then gives 01 +0.0085 (scaled z 3.45) and 02 +0.0105 (4.66), both significant,
  against case 3's +0.0080 and +0.0107; 1 (+0.0072) and 2 (+0.0082) keep case 3's sign without significance. On
  the retained centers case 2's 01 reads -0.0078, the sign the over-applied excitation predicts.

The positive 01 and 02 offsets are therefore a fixed offset of the shared model, repeated at the same size on
two runs, and 1 and 2 lean the same way; the excitation's own envelope cannot be the cause on 1 and 2. The four
misses are still not one offset: 38-49-50 coefficient 2 is absorbed by the shift on 2; 66-67-68 coefficient 1
and 132-133-134 coefficient 01 return inside only under leave-one-out offsets that fail the test; and
132-133-134 coefficient 1 remains outside.

**q147's shot history.** IBM runs a job column-wise, every circuit of shot s before shot s + 1
([repetition-rate-execution](../../../notes/ibm_quantum/repetition-rate-execution.md)), without a guarantee on
PUB order.
- Execution order. In stage 2, each readout arm that prepares q147 in |1> and reads 0 (about 19 percent of its
  shots) is followed, in submitted order, by a |0>-prepared arm that reads q147 excited more often: 0.095 against
  0.051 (z -4.62), 0.082 against 0.058 (-2.31) and 0.070 against 0.047 (-2.46) for arms 2, 4 and 6. The arm
  that follows each of these in submitted order shows no link (z 0.62, 1.38, 1.13). The link runs forward in
  time only, which supports column-wise execution in submitted order.
- The previous shot's end state does not set the excess. In each x_history job, a shot whose initial read was 1
  ends in |0> after its X, and the next shot still reads q147 excited in 0.039 and 0.036 of shots, against 0.049
  and 0.050 after a shot that ended in |1>. Conditioning on the previous shot removes 21 and 28 percent of the
  excess; a population carried from the previous shot predicts about 98 percent. In stage 2, the sign is the
  same: a |1> arm that fails to read 1 raises the next shot's excess instead of lowering it.
- The in-job excess exceeds the end-state ceiling. `g88_readout_0` prepares all 66 qubits in |0> and measures
  them, the prep0 control's configuration, and reads q147 excited in 0.0675 +- 0.0040 of its 4000 shots. Any law
  that scales the excess with q147's own end-state history tops out at 0.0518 (hd / (1 - x_history fraction) +
  prep0, every earlier shot excited), 3.97 standard errors below at the calibrated |1> read efficiency. The
  stage-2 |1> arms read with efficiency 0.873 once their start-excited shots are removed; at that efficiency in
  the x_history jobs, which neither job measures, the ceiling rises to 0.0587 and the reading sits 2.21 standard
  errors above it. q142, uncoupled to q147, reads 0.085 in the same arm against 0.027 in both of its controls
  (hd 0); the other 64 qubits sit within 0.016 of their prep0 fractions.
- The order-free number. Each circuit has one predecessor, so the mean predecessor end-excited fraction equals
  q147's mean end-excited fraction over the 105 PUBs, 0.399 through the calibration's assignment. Against
  x_history's 0.951 it gives f = 0.42, one standard error below lambda 0.66 +- 0.25, which is consistent, but the
  mechanism f assumes is the one the three items above reject.
- What lambda says. The split center applies hd as an initial X error to every arm, the readout3 arms included
  (`primorial_probe_case.path_budgets`), and the in-job |0> arms read q147 excited in 0.060 of shots, at or above
  x_history's 0.049. A uniformly smaller excess on every arm does not produce lambda 0.66; the excess must differ
  between the readout arms and the gap-88 and null circuits, or act as something other than an X error before the
  circuit.

Inference, low confidence: the link runs only from a circuit to the one after it, so the previous shot acts on
the next one, but through its readout event rather than its end state: a |1> arm read as 0 is followed by more
excitation, and an x_history shot read as 1 and sent to |0> leaves most of the excess in place. The
initialization between circuits failing after particular readout outcomes fits this; a condition stationary
across circuits does not, because it would link a circuit to its successor as strongly. q147's |1> arms read
0.81 to 0.83 against a calibrated e01 of 0.0076, and q142's in-job excess follows no history of its own. A
repeated-measurement arm (measure, measure), cut from case 3's scope, separates a real population from
misassignment after each readout and would raise or lower this reading.
