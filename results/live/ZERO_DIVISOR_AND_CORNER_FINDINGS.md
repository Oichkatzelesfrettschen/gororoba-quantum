# Zero-divisor fringe and the Kingston corner baseline (2026-10-15)

The owner approved two bounded runs after the rank-sector endpoint
decomposition (`QPU_PROGRAM_CASES.md`, "Rank-sector estimation endpoints"):
the Design B zero-divisor annihilation with the Design D fringe, with the
low-index corner qubits excluded, and a readout, relaxation and Ramsey
baseline of that corner. Both ran at source `6bb8f57` (experiment digest
`957001f8a996`) on ibm_kingston and settled 14 s.

| Case | Approved dry run | Collected run | Job (settled s) |
|---|---|---|---|
| zero-divisor fringe | [2026-10-15T070828.397109Z](2026-10-15T070828.397109Z/CASE.md) | [2026-10-15T070853.550532Z](2026-10-15T070853.550532Z/collect.json) | db87o8or1c5c738lu910 (10) |
| corner baseline | [2026-10-15T070828.127101Z](2026-10-15T070828.127101Z/CASE.md) | [2026-10-15T070847.644554Z](2026-10-15T070847.644554Z/collect.json) | db87o48r1c5c738lu8jg (4) |

Each `CASE.md` states the preregistered readout and decision rule before the
data; `--exclude-qubits` withheld ibm_kingston 0-4 and 16 and ibm_fez 2-4 and
16 from the fringe placement, and confined the baseline to ibm_kingston 0-4
and 16. ibm_fez had left maintenance with 100 qubits above the readout-error
threshold, and the planner skipped it.

## Corner baseline: a readout fault the calibration does not report

Execution calibration 2026-10-15 00:03:15 PDT; 1024 shots per circuit.

| Qubit | P(1 \| 0) | P(0 \| 1) | Reported readout error | Excited retained after 50 us (model) | Reported T1 (us) | Ramsey visibility 2 us / 10 us |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.388 | 0.144 | 0.0088 | 0.863 (0.831) | 262 | 0.393 / 0.420 |
| 1 | 0.274 | 0.123 | 0.0066 | 0.867 (0.809) | 232 | 0.456 / 0.415 |
| 2 | 0.002 | 0.010 | 0.0093 | 0.727 (0.858) | 350 | 0.972 / 0.850 |
| 3 | 0.000 | 0.014 | 0.0090 | 0.491 (0.718) | 147 | 0.955 / 0.833 |
| 4 | 0.014 | 0.012 | 0.0105 | 0.856 (0.842) | 305 | 0.933 / 0.829 |
| 16 | 0.008 | 0.004 | 0.0115 | 0.728 (0.879) | 348 | 0.944 / 0.929 |

- Qubits 0 and 1 misassign the ground state 39 and 27 percent of the time and
  the excited state 14 and 12 percent, against reported readout errors below
  1 percent. Their Ramsey visibilities, about 0.4 at both idles, match the
  readout factor 1 - P(1|0) - P(0|1) (0.47 and 0.60) rather than a
  decoherence that grows with the idle.
- Qubits 3, 2 and 16 relax faster than their reported T1 implies: 0.49
  retained after 50 us on qubit 3 against 0.72 modeled.
- Rank sector 4 sat on qubits 0 to 3 and ripple lane 6 on 1 to 4 and 16, so
  a readout fault of this size on qubits 0 and 1 accounts for the loss the
  decomposition located there, which the block-homogeneity test resolved no
  change in during the 03:10Z rank job. That the fault already held at 03:10Z
  is an inference from those losses; this 07:10Z run measures it directly.
  Readout crosstalk between the simultaneously measured neighbors 0 and 1 is
  not separated from an intrinsic fault by this run, and the tile and
  template were chosen after seeing the data, so attributing the loss to the
  tile rather than the circuit family needs a prospective crossed design.

## Zero-divisor fringe: the excess floor is incoherent

Eight replicas off the corner, 2048 shots each. The preregistered rule
writes the dark value of the fit P0(phi) = o + A cos phi + B sin phi as
(1 - V)/2 + (o - 1/2) + (V/2)(1 - cos phi0).

| | Dark P(s=0) | Bright | Offset o | Visibility V | phi0 | (1 - V)/2 | o - 1/2 | (V/2)(1 - cos phi0) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Measured, pooled | 0.182 [0.146, 0.217] | 0.828 | 0.502 | 0.678 [0.598, 0.759] | +0.197 | 0.161 | +0.002 | 0.007 |
| Noise model | 0.081 | 0.930 | 0.504 | 0.856 | -0.006 | 0.072 | +0.004 | 0.000 |

- The measured floor is 2.2 times the modeled one, the same excess the rank
  family's ideal-zero endpoints showed (1.9 times on Kingston). In the
  pooled fit and in every replica, the incoherent contraction (1 - V)/2
  carries the floor; the offset and the coherent phase term are at most
  0.041 in any replica. One replica (qubits 138 and 149 to 152) is
  much weaker (V = 0.447).
- The mirror twins, on the same qubits and with the same two-qubit content
  but no algebra, attenuate <Z> to 0.64 against a modeled 0.86, more than the
  witness itself, so dividing by them over-corrects (dark -0.08, V 1.21).
  The excess is device noise on those qubits that the calibrated model
  underestimates, not a feature of the algebra.
- The ideal zero divisor stays dark relative to its bright control
  (0.182 against 0.828) on every replica.
