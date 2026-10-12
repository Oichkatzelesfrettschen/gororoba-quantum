# Correction-policy preparation and renewal

The [current campaign preparation](CAMPAIGN_PREPARATION.md) renews correction,
ripple and rank-sector at source `f1b9830`. The
[fresh correction case](../live/2026-10-12T163354.247043Z/UNAPPROVED_CASE.md)
passes independent planning checks: four 8,192-shot Fez PUBs, 11.519211264
nominal seconds, 14.474571264 stress seconds and a 30-second ceiling. The
three-family plan has five job ceilings totaling 170 seconds. Correction runs
first under the user's conditional authority; clean current-head Copilot
review, passing checks, merge and fresh source/calibration/quota/approval
bindings remain execution gates. Returned schedules gate the matched inference.

## Historical preparation at source fb13b06

The [retained written case](../live/2026-10-12T153635.004894Z/UNAPPROVED_CASE.md)
retains a successful submit-free preparation at source
`fb13b0675530c3eb9a4d8c0225bf37cacd8b5923`. All three systems supplied six
admitted candidates. Fez seed 20261014 won the finite calibrated-quality
ranking with layout `[24, 23, 16, 22, 3]` and weakest-arm proxy 0.588331.
The four ordered dynamic PUBs are F(s1), U(s1), U(s3), F(s3), each at 8,192
shots. The active qubits are 3, 16, 22, 23 and 24; each PUB contains 68 CZ gates.
Both arms retain measurement, reset and classical dispatch.

Subsequent runtime shot-allocation edits changed the working experiment
source. The retained case has current state `historical_renewal_required`;
current admission and physical execution authorization for that older record
are false. The current campaign case above qualifies the revised source.

The nominal charge estimate is 11.519211264 seconds. The controller-stress
scenario estimates 14.474571264 seconds under a proposed 30-second service
ceiling. Nominal assumptions use 2.3 seconds overhead and 20 microseconds per
classical stage; stress assumptions use 4.6 seconds and 40 microseconds.
Those estimates exclude queue and local preparation time and carry scenario
scope rather than billing confidence coverage.

The user capped the new correction-plus-atlas campaign at 180 seconds. The
30-second pilot leaves at most 150 seconds for renewed atlas cases. The old
270-second combined proposal is historical; its two atlas ceilings alone
sum to 240 seconds and exceed the new allowance. The
[coordination ledger](../live/qpu-coordination.json) records the cap and
separate 60-second account reserve. Local per-invocation ceilings and the
cooperative ledger do not create an account-wide atomic reservation. The
execution owner must reconcile accepted attempts, settled charges, remaining
campaign allowance and fresh account quota before each submission.

The user conditionally authorized execution after reviewed and merged code,
a current digest-bound case and a combined plan within that 180-second cap.
Those execution gates remain pending. The planner-generated
`UNAPPROVED_CASE.md` retains its original text; the ledger records the
subsequent conditional instruction separately. Preparation submitted zero
physical or mock primitive jobs and recorded zero job identifiers.

The frozen 32,768-shot-per-member model predicts U-minus-F gains of
0.1068115 and 0.5889893 percentage points for s1 and s3. Both fall below the
one-percentage-point decision margin. The hypothetical four-point planning
gain gives joint-power lower bound 0.8806007844 and remains a separate
sensitivity scenario. Actual raw counts, archived-pair conformance, common
calibration and returned schedules must qualify before both labels can pass
`lower_U - upper_F > 0.01` under the four directional bounds. Failed evidence
gates withhold the decision; a failed gain decision retains F.

## Retained artifact identities

- [Record](../live/2026-10-12T153635.004894Z/record.json):
  `315bac0dd8fa61ed2ee0c91506d58b2f6efc76cab534b37fa5f0d0181f8c0207`.
- [Executable QPY](../live/2026-10-12T153635.004894Z/isa.qpy):
  `51db305d47a0cff4664e1135390ee1cd807bde2cc105439669ea795108bd83b4`.
- Experiment digest:
  `6944868a3886e3bdee33e1babfb145f6b234497bdc642baf0d434dbea0bc8881`.
- [Checksums](../live/2026-10-12T153635.004894Z/SHA256SUMS) bind the original record,
  QPY and written case.
- [Independent validation receipt](correction-current-source-validation.json)
  binds source equivalence across merge `ea8eae17005d2226afa981cadad889241d415c47`, all 41
  runtime sources and seven dependency versions at those commits, candidate
  ranking, QPY/PUB identity, case replay and cost arithmetic. Later working-source
  changes require renewal. The receipt preserves historical validation references
  at their own commits.

Submission re-prepares all three systems and compares the fresh source,
dependency, calibration, selection, layout and QPY evidence with the retained
case. Changed bound inputs require renewal. Queueing separates calibration
checks from execution; the preparation establishes no atomic observation of
future hardware state. The [protocol](../../gororoba_quantum/MODEL_DISCRIMINATION.md)
retains the statistical and schedule boundaries.

## Historical renewal rejection

The earlier scoring-repair renewal stopped when Fez exceeded the 25-job queue
limit and Marrakesh reported maintenance. Kingston alone failed the required
three-system snapshot condition. The
[rejection evidence](correction-renewal-rejection.json) retains those bounded
observations. The [account snapshot](correction-renewal-account.json) records
551 of 600 seconds available and an empty pending-account-job list at its
stated time. The successful retained preparation superseded that eligibility
rejection before the later runtime edits; the prior evidence stays unchanged. The
[scoring validation receipt](scoring-repair-validation.json) retains its
software-check scope.

## Historical case at source revision 67106bd1

The retained record below remains immutable. Its 11.515410176-second nominal
estimate, 14.470770176-second stress scenario and proposed 30-second ceiling
apply to that historical preparation. The changed shared source digest and
fresh calibration require a renewed case before execution.

The complete four-PUB comparison selects Fez from 18 routed candidates using
fresh Target/properties snapshots: six transpiler seeds for each of Fez,
Kingston and Marrakesh. Every candidate passed the finite admission checks.
The selection maximizes the weakest calibrated arm score, then minimizes the
Target-plus-repetition charge with zero added controller latency, total CZ
count, seed and backend name. The nominal estimate separately includes the
declared 20-microsecond per-stage controller latency. The
score is a calibration proxy, separate from measured fidelity.

| Best candidate per system | Weakest-arm proxy | Nominal QPU seconds | CZ gates per PUB |
| --- | ---: | ---: | ---: |
| Fez | 0.585064 | 11.515410176 | 70 |
| Kingston | 0.555297 | 11.588024064 | 70 |
| Marrakesh | 0.379618 | 11.648317184 | 70 |

The [unapproved written case](../live/2026-10-12T074042.840320Z/UNAPPROVED_CASE.md)
prices one dynamic job: F(s1), U(s1), U(s3), F(s3), each at 8,192 shots.
The five active physical qubits are 16, 21, 22, 23 and 24. Both arms retain
measurement, reset and classical dispatch; their prescribed false-branch
phase differs. The proposed service ceiling is 30 seconds with a shared
60-second reserve. The fresh account observation records 49 of 600 seconds
used, 551 remaining and an empty pending-account-job list.

The nominal estimate is 11.515410176 seconds. The explicit controller-stress
scenario raises assumed job overhead from 2.3 to 4.6 seconds and per-stage
classical latency from 20 to 40 microseconds, giving 14.470770176 seconds.
Those scenarios are assumptions, not confidence bounds. Queue time and local
preparation are outside QPU time. Actual returned schedules and final usage
provide the execution evidence.

The frozen calibration model uses 32,768 simulation shots per member. It
predicts U-minus-F gains of 0.0823975 and 0.640869 percentage points for s1 and
s3, below the one-percentage-point decision threshold. The hypothetical
four-point improvement used to calculate planning power remains a separate
sensitivity scenario. The pilot tests whether the measured unconditional
gains pass both simultaneous directional bounds. Model discrepancies remain
descriptive. A failed decision retains F and establishes neither
equivalence nor a specific noise mechanism.

Collection preserves integer histograms and complete shot order, checks those
two representations against each other, and qualifies the archived circuit
pairs, common calibration and actual returned schedules before evaluating
the four one-sided Clopper-Pearson bounds. Missing or unmatched schedule
evidence withholds the optimizer decision while preserving the raw data.
The [protocol](../../gororoba_quantum/MODEL_DISCRIMINATION.md) records the
sampling and numerical assumptions.

## Historical reproduction and identity

The [production validation](CORRECTION_VALIDATION.md) records the passing full
repository gates, local Runtime checks and independent concrete-case audit.

- [Record](../live/2026-10-12T074042.840320Z/record.json):
  `eff6beaf2c25c7c8ac4b243edf08f13d6467797399fb6714453935e16cd7da69`.
- [Executable QPY](../live/2026-10-12T074042.840320Z/isa.qpy):
  `2fcb598592888b8a48669df83401979692bb07900e81c07e090fa36ccdaf9aad`.
- Source commit: `67106bd1d11397f0dcacb0c48f509a2e0d02fb89`.
- Experiment digest:
  `e29428189eac0bad0aae4e9fb0d787addd3f118b6ec1e7d10833557cce8c60b8`.
- [Source closure](../live/2026-10-12T074042.840320Z/source-closure.json):
  41 declared source files and seven dependency versions match.
- [Account observation](../live/2026-10-12T074042.840320Z/account-inventory.json):
  read-only quota, pending jobs and the settled 29/11-second prior charges.

The historical written case retains its exact replay and submission commands.
Current execution requires a renewed case and the conditional gates above.
Submission preflight refreshes and reranks all three systems;
the selected backend is refreshed again immediately before its batch. Queueing
separates those checks from physical execution, so the comparison is not an
atomic observation at execution time. Changed selection, calibration or QPY
returns `approval_required` before submission. Preparation sent zero physical
or mock primitive jobs. The
default seven-group dry run separately rejected placement after its bounded
256-combination search; that result establishes rejection, rather than
admission, of the broad default workload.

The held [ripple and rank cases](PREPARATION.md) retain their original records
and separate approval requirements. The
[integrated campaign directive](../../gororoba_quantum/RIPPLE_CAMPAIGN.md)
preserves the complete visual, algebraic and research scope.
