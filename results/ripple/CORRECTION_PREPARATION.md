# Live-calibrated correction-policy preparation

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

## Reproduction and identity

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

The written case contains the exact replay and submission commands. Physical
execution requires explicit approval of that case and fresh calibration
revalidation. Submission preflight refreshes and reranks all three systems;
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
