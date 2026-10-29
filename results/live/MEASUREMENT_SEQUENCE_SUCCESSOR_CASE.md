# Case: the measurement-sequence successor on ibm_kingston, width 24

Status: written, not approved. Plan record
[measurement-sequence-pinching-device](../../docs/state/plans/measurement-sequence-pinching-device.json), step
`successor-case`. Design v4.0:
[measurement-sequence-envelope-successor.md](../../docs/design/measurement-sequence-envelope-successor.md), under the
envelope contract of [measurement-sequence-adaptive-envelope.md](../../docs/design/measurement-sequence-adaptive-envelope.md).

## What it measures and why simulation cannot answer it

The run measures the per-measurement departure from ideal pinching on Heron r2: N steps of RX(8 pi / 9 / N), each
followed by a mid-circuit measurement whose outcome is discarded, read against the ideal P0 = (1 + cos(theta / N)^N) / 2,
a unitary N = 16 arm, a duration-matched delay arm and a settle-gap arm. The quantity is the extra transition a real
readout drives per measurement (residual resonator photons, measurement-induced state transitions, leakage), which no
calibration field reports. The Aer noise model applies each measurement as an ideal projector plus the reported
assignment error and idle relaxation, so it predicts zero departure by construction; only the device answers.

The width-32 envelope run of 2026-10-27 (job `dbg08t9j4t8s73abaghg`, billed 38 s) returned no device verdict: its
reset screen withheld all 32 qubits
([findings](MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)). Its raw shot-ordered bits then showed that the screen
guarded a bias the device does not have: carryover through the terminal reset, the 20 us repetition delay and
`init_qubits` is +0.00020 +- 0.00006, and the analysis's (T1, q) fit, not the device, produced half the +0.0185 N = 16
residual ([raw diagnostics](../../docs/evidence/measurement_sequence/envelope-run-raw-diagnostics.json)). The
successor reads relaxation through a gamma-rate fit at q = 1, measures q with a 400 us equilibrium row, bounds
carryover with twelve in-circuit readers, and vetoes q inconsistency with the settle gap.

## What the run can detect

At the rehearsal layout's 24 contexts and the registered 0.018784 scatter floor, the pooled departure z reaches -3 at
a per-step loss of 0.00458, an N = 16 P0 departure of -0.0509 (per-qubit 0.00473 to 0.00846, median 0.00504; mean
departure standard error 0.0179), computed by `measurement_sequence_analysis.minimum_detectable` on the planning row.
The eight-qubit figure was -0.0520 at 0.00467: the per-qubit gate-model systematic enters `pooled_z` as a shared term,
so width buys about 2 %. The expected outcome is `consistent` unless the measurement-induced loss exceeds about 0.005
per step; a run that reads `consistent` bounds it there.

## What the null establishes, and the two readings it leaves

The null ([successor-null.json](../../docs/evidence/measurement_sequence/successor-null.json), sha256
`3c704f7db2fe4dd8...`) ran every arm on the rehearsal dry run `2026-10-28T163139.827337Z` (planning snapshot
`e185caea...`) with 0 false fires and every target met; the design's table lists each arm. Two arms describe the
device this run may meet:

- gamma (healthy relaxation, q = 1, gamma-distributed rates): 396 of 400 replicates issue a device verdict (99 %),
  mean 23.8 of 24 qubits selected.
- plateau-retained (each qubit draws a (T1, q) pair of the retained width-32 run, q from 0.28 to 1.02): 299 of
  15,710 replicates issue a verdict (1.9 %); the equilibrium screen withholds 84 % and the common settle veto 16 %.

If the device is the gamma device, the run issues a departure verdict. If it is the device the retained (T1, q) fit
described, the equilibrium row and the settle veto withhold it, and the run reports per-qubit q_hat, the settle gaps
and the carryover bounds instead. Both outcomes answer whether q = 1 holds on Kingston, which the retained run could
not; neither can fire a false departure at more than 0.01.

## Assumptions the case states

- Carryover readers ([design](../../docs/design/measurement-sequence-envelope-successor.md#carryover-readers)): the
  qubit's evolution from the terminal reset to the next shot is Markovian; the executor's repetition delay starts
  after the terminal reset completes, so the in-circuit 20 us idle is a prefix of the cross-shot sequence; excitation
  and leakage do not cancel between predecessor classes (the reader reads |2> as 1). `pattern_crosscheck` reads the
  cross-shot carryover under the submitted order and can only refute these.
- One-sign carryover: the vertex allocation bounds every allocation whose carryover keeps one sign across predecessor
  classes; a sign that differs between classes can reach 1.6 to 1.8 times the bound.
- Coverage: the binding run executes inside the calibration domain the null sampled (below).

## Coverage of the null

PENDING: fresh dry run layout overlap and the per-quantity ratio table.

## Records

PENDING: the planning dry run, its sha256, experiment digest, planner charge and sizes.

## Cost and account

PENDING.

## Owner decisions

PENDING.

## Commands

PENDING.
