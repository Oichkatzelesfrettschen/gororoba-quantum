# Measurement-sequence envelope successor: a carryover screen sized from the endpoint

Status: design v1, before review. The width-32 envelope run of 2026-10-27 (`results/live/2026-10-27T014422.881898Z`,
[findings](../../results/live/MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)) executed as planned and billed 38 s, and its
reset screen withheld all 32 qubits, so it returned no device verdict. This successor keeps the envelope contract of
[measurement-sequence-adaptive-envelope.md](measurement-sequence-adaptive-envelope.md) (layout rule, width tiers,
20 us repetition delay with the 50 us fallback, aggregate cap, replan bound) and replaces the two parts that failed:
the reset screen and the settle verdict.

## What the screen has to bound

`measurement_sequence_analysis.corrected` reads every arm through the ro0 and t1-0 brackets, and the in-job T1 fit
carries an initialization excitation. An excitation carried over from the previous shot that is the same on every
member therefore divides out. `scripts/msq_carryover_sensitivity.py` plants an extra initial excitation delta through
the analysis's own device model and reports the largest endpoint shift per unit delta
([carryover-sensitivity.json](../evidence/measurement_sequence/carryover-sensitivity.json)):

| Excitation on | departure | settle gap | contrast |
|---|---|---|---|
| every member | 0.0000 | 0.0000 | 0.086 |
| the measure arm only | 0.760 | 0.729 | 0.760 |
| ro0 only | 0.883 | 0.061 | 0.891 |
| t1-0 (the ro1 bracket) only | 1.111 | 1.703 | 0.891 |
| the unitary arm only | 0.000 | 0.000 | 0.957 |

The endpoint inherits the member-to-member spread of carried-over excitation, at most 1.11 times that spread on the
departure. Execution interleaves a job's circuits and IBM fixes no circuit order, so a member's predecessor is any
member; the spread is bounded by the difference between the excitation an all-|1> previous shot leaves and the one a
near-|0> previous shot leaves.

The run's reset controls (`x; measure; reset; measure` against `measure; reset; measure`) measured something else: the
residual of one measure-and-flip reset read immediately inside the shot, median 0.0123, about 1.7 times the
calibrated P(0|1). The previous shot's end state reaches the next shot through the terminal reset, the 20 us
repetition delay and the service's `init_qubits` initialization; the state-prep controls of 2026-10-18 measured that
chain without the terminal reset (`results/live/2026-10-18T214519.655411Z` x_history and
`2026-10-18T220218.089776Z` prep0, 20 us, 32768 shots) at a median P1 difference of 0.0006 over 148 qubits.

## Carryover controls

Two jobs, each holding one fused PUB over the layout's qubits, measure the spread directly; a job holding a single
circuit fixes every shot's predecessor to the same circuit, so the history holds by construction
(`scripts/state_prep_excess.py` states the argument):

- `hist1`: measure, x, measure, reset: each shot reads the carryover of a previous shot that ended in |1> before its
  terminal reset;
- `hist0`: measure, measure, reset: the same after a previous shot that ended near |0>.

The first measurement of each shot is the reading; the second fixes the end state through the same terminal reset
every family member ends with, so the controls measure the chain the members inherit (terminal reset, delay,
`init_qubits`) instead of the conservative init-only chain of the state-prep family. Each runs at 32768 shots.

Screen: a qubit stays usable when the one-sided upper confidence bound of P1(hist1 first read) minus
P1(hist0 first read), Bonferroni over the W qubits at family alpha 0.05, lies below the margin
`0.25 * 0.0188 / 1.111 = 0.0042`: a quarter of the bound floor carried to the departure at the worst member-class
sensitivity. The margin is fixed before the run from the sensitivity table, not from any run's counts. The
2026-10-18 init-only controls, read the same way, pass 22 of the run's 30 measured layout qubits and 26 of the
current calibration's 31 (failures there: q40 0.0077, q61 0.0134, q71, q79, q154; q62 0.053 on the run's layout), so
the screen admits more than the 8 qubits the verdict needs even before the terminal reset shortens the chain. The
in-job reset controls stay in the family as a reported reset diagnostic and gate nothing.

Cost: two jobs of one PUB at 32768 shots, about 3.1 s of planner charge each plus 2.3 s job overhead, priced with the
measured 9 us per shot residual. Attempt accounting covers three jobs per attempt (the family job and the two
controls); the fallback signature applies to each job, and the aggregate cap adds the control ceilings.

## Settle verdict becomes descriptive

The exploratory reading of the run (`docs/evidence/measurement_sequence/envelope-run-exploratory.json`) has the settle
test reading `reduced_by_gap` on 16 qubits, pooled z 18.7, while the measure arm shows no deficit for a gap to reduce:
the settle arm stands above the model's prediction for its sixteen 2 us gaps, in the direction of the delay arm's
idle-model shortfall (median +0.11 over modeled). A preregistered settle verdict would attribute a model error to a
readout tail. The successor reports the settle gap per qubit and pooled, labeled descriptive, and no device verdict
reads it. The departure and mutation decisions stay preregistered; the exploratory reading found 32 of 32 mutation
tests passing and every departure consistent (pooled z 1.07), so neither fires on the known model error.

## Fewer than 8 kept qubits

`msq_envelope_analysis.collected` reports the per-qubit pinching analysis over the kept qubits whenever any qubit is
kept, and withholds only the device verdict below 8, as the original design stated.

## Null calibration

The null of `msq_envelope_null.py` is rebuilt as the batched estimator of issue #579 (numpy across replicates with a
scalar bit-identity gate) before it runs at the successor's width. Its replicates plant, besides the sx-error residual,
the idle-model error the run shows (the delay arm's +0.11 median excess, realized as a T2 shortfall on the idle
segments) and a carryover spread drawn up to the margin, and it must keep the family-wise false-fire bound below 0.01
on the departure and count-rule verdicts.

## Approval scope

The family stays `measurement-sequence-envelope` and the record's envelope section stays schema `msq-envelope-v1`; the
contract gains the control jobs' ceilings inside the aggregate cap. AGENTS.md ratified the envelope exception for
`msq-envelope-v1` records of this family; the case states whether the three-job attempt stays inside that wording.

## Sequence

1. Reviews of this design: the adversarial review skill, Codex gpt-daybreak-blue in tmux, the advisor.
2. Issue #579: the batched null with its gate.
3. Implementation: the hist controls as a second family job pair, the screen, the descriptive settle, the per-qubit
   report, the three-job attempt accounting; tests and lanes.
4. A sizing replay of every successor screen and verdict over the retained run's counts (the hist screen over the
   2026-10-18 controls), then the null at the chosen width.
5. Dry run on the live calibration, the written case, approval, run.

Falsifiers: the sensitivity probe's every-member row departs from zero beyond 1e-4 per unit; a hist control whose
predecessor is another circuit (a job holding more than one circuit); a margin derived from run counts; a settle
reading that enters a device verdict; a null that does not plant the idle-model error.
