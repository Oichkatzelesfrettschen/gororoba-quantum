# Tuna-17 zero-divisor matched-response case

The retained [Tuna-17 experiment](../notes/quantum_inspire/experiments.md) rejects its preregistered
shared symmetric-contraction response. Sequential jobs and different routed depths leave drift,
readout and control mechanisms coupled. The proposed comparison tests a narrower common-affine
response with matched emitted gate shapes. The case authorizes local generation and validation;
provider execution requires separate user approval after refreshed admission checks.

## Witnesses and matching

The fixed left operand is `(e1+e10)/sqrt(2)`. The dark and bright right operands are
`(e4-e15)/sqrt(2)` and `(e4+e15)/sqrt(2)`. The quadrature fixture is
`(e4-i e15)/sqrt(2)` in the complex-linear extension of the real multiplication operator.
The fixture changes the relative phase on the same support; the fixture does not assert a new
real zero divisor. Exact split-real products certify ideal selector-zero probabilities 0, 1 and 1/2.

One symbolic five-qubit circuit is routed once per region. Binding changes one nonzero native
`Rz` angle after a fixed `S`: dark `pi/2`, bright `-pi/2`, fixture `pi`.
The regions are `(1,2,4,8,12)` and `(10,11,13,14,16)`. Each case retains its region's complete
gate locations and order, including 81 and 105 controlled-Z gates respectively and 28 T-family
gates per region. Different regions remain different routed circuits. Local OpenSquirrel
serialization rounds rotation angles; the checker bounds each change by `5e-8` radians and
reports the observed maximum. Equal emitted shapes establish a software property, while the
provider's physical scheduling and angle-dependent implementation remain admission questions.

## Primary estimand and falsifier

The ordered witness assignments are `(dark R1, bright R2)`, `(bright R1, fixture R2)`,
and `(fixture R1, dark R2)`, each accompanied by all-zero and all-one readout controls.
For the six readout-corrected selector estimates in that order, the primary weights are
`(0,0,-1,1,1,-1)`. The residual is `F_R2-B_R1+F_R1-D_R2`.
Under `p=batch_offset+region_offset+visibility*ideal`, the residual vanishes:
each participating batch contributes one positive and one negative term; each region does too.
A pooled half-spacing alone fails to cancel arbitrary batch offsets and is secondary only.

Use the full six-by-six covariance, including shared shots and shared readout-calibration
uncertainty. Readout inversion may produce estimates outside `[0,1]`. Require positive contrast
variance and reject the common-affine response at `abs(residual/standard_error)>=3`.
The local helper validates covariance symmetry and positive semidefiniteness. The acquisition
analysis must retain its covariance construction, calibration conditioning and uncertainty method
before execution approval. A significant residual rejects the specified response; a residual alone
identifies neither drift, crosstalk nor a particular control-error channel. A compatible residual
also leaves region-dependent visibility and time-dependent region offsets unresolved.

## Budget, replay and admission

The [proposal](../../results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response/proposal.json)
contains nine unsubmitted jobs on `tuna_17`: three witness jobs and six readout-control jobs,
each with 16384 shots, totaling 147456 shots. The provisional budget is 101.55168 device seconds,
using the [retained timing model](../notes/quantum_inspire/README.md) of 2.6 seconds fixed overhead
plus 0.53 ms per shot per job, at zero metered credits under the recorded
service terms. Two interbatch pauses of at least 120 seconds require at least 240 seconds total.
Refresh availability, terms, queue limits and duration before presenting an execution approval.

The generator binds the retained catalogue digest and its own source digest. Replay locally:

```sh
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON
"$PYTHON" scripts/qi_matched_zero_divisor.py --check results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response
"$PYTHON" scripts/qi_matched_zero_divisor.py --check-toolchain results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response
```

The first command uses the pinned Qiskit replay runtime. The second checks the
[current compiler receipt](../evidence/quantum_inspire/matched-zero-divisor-toolchain-pause-ladder.json)
against the producer and its compiler/admission/adapter/pool sources, catalogue, locked toolchain
and all nine circuit hashes. The [first receipt](../evidence/quantum_inspire/matched-zero-divisor-toolchain.json)
retains its original bytes and top-level-only source binding. The
[intermediate receipt](../evidence/quantum_inspire/matched-zero-divisor-toolchain-source-closure.json)
preserves the compiler closure before the backend batch-admission source was included, and the
[admission-closed receipt](../evidence/quantum_inspire/matched-zero-divisor-toolchain-admission-closure.json)
the closure before `scripts/qi_platform.py` gained the hardware pause ladder; every compiled row is
identical across the last two. With `QI_PYTHON`
set, the second command also repeats local parsing and compilation through the repository's
`qi_stack` adapter and compares every receipt field. Gate `core-633` requires that live path
in the Quantum Inspire CI stack; the ordinary stack checks the retained receipt explicitly.
Neither command contacts a provider.
Before submission, freeze analysis, inspect emitted and served scheduling, refresh the catalogue
and budget, and obtain the user's approval of the exact circuit digests, backend, shots, seconds
and credits. Preserve each acquired batch and its calibration and timing records separately.
