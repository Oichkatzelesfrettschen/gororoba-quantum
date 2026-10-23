# Algebra hardware probes: first principles

This note derives the design principles that the sedenion-kernel runs on IQM
Garnet established or forced, each from a
finding with its evidence, the conjecture it tested and the outcome. The
binding rules that follow from them are stated in
[algebra_circuit_rules.md](../algebra_circuit_rules.md#hardware-probes); this
note carries the derivations. Device facts (billing, reset, readout) live in
the [IQM guide](../iqm/README.md#what-the-garnet-runs-measured) and the
[Tuna-17 notes](../quantum_inspire/tuna-17.md).

## Findings

### F1. The signed overlap does not depend on the kernel (exact)

- **Conjecture tested.** The signed probe Re<L_e2 u|B(t)|u> =
  t/(2 + |t|) tests that u = (e4 - e15)/sqrt2 is a zero divisor of
  L(e1 + e10) (`proposed-signed-kernel-probe`).
- **Outcome: falsified as a test of the kernel.** L_e2 is orthogonal and
  L_e2^T L_e1 and L_e2^T L_e10 are antisymmetric, so <L_e2 u, L_e1 u> =
  <L_e2 u, L_e10 u> = 0 for every real u and the overlap equals t/(2 + |t|)
  for every unit vector. All 1000 seeded replacement sign tables on {e4, e15}
  leave it unchanged.
- **Evidence.** `signed-overlap-kernel-independence`,
  [audit](../../../results/iqm/signed_kernel_probe_audit.json) (gate
  `core-640`).
- **Principle P1.** An observable tests an algebraic property only if a
  mutation that removes the property changes the observable: run the
  sign-table and input-vector mutations before a case reaches hardware.

### F2. The zero divisor is an eigenvalue, and a five-qubit circuit reads it (exact)

- **Statement.** (L_e1 + L_e10) u = 0 holds exactly when K = L_e1^T L_e10
  maps u to -u. K swaps e4 and e15; the kernel vector is its -1
  eigenvector, the bright vector (e4 + e15)/sqrt2 its +1 eigenvector, and the
  -1 eigenspace is four-dimensional. A Hadamard test with an L_e1 reference
  branch and selector cos(theta)|e1> + sin(theta)|e10> reads cos(2 theta)
  for the kernel and 1 for the bright vector. One flipped L_e10 sign at e4
  or e15, or 755 of 1000 random sign tables, moves the zero at theta = pi/4.
- **Reduction.** u lives on {e4, e15}; both multipliers leave index bit 2
  at 1 and flip bit 1 alike, so data bits 0 and 3 carry the reachable span
  as a Bell pair, and the probe runs on five qubits.
- **Evidence.** [kernel_cancellation.py](../../../gororoba_quantum/kernel_cancellation.py)
  `--check`, gate `core-641`.
- **Principle P2.** Write an algebraic property as an eigenvalue of an
  operator built from the algebra's left multiplications, and read it with
  a Hadamard test whose two branches differ only by that operator; restrict
  the register to the property's reachable span.

### F3. Garnet carries the zero-divisor sign (hardware, preregistered)

- **Outcome: established, nothing falsified.** On set `68b0f1d0` (37 CZ,
  1.50 credits) the kernel odd part read -0.0695 +- 0.0087 at phi = 0.1
  (z -8.0) and -0.178 +- 0.009 at phi = 0.3 (z -20.1); the bright odd part
  read -0.016 +- 0.009, within a standard error of its modeled -0.008; the
  sine-law contrast read z 0.74 and the even-part decomposition z 0.37.
  Visibility 0.36 +- 0.05 against the model's 0.48.
- **Evidence.** `iqm-garnet-kernel-cancellation`,
  [analysis](../../../results/iqm/kernel_cancellation_probe_analysis.json).
- **Boundary.** cd_core already settles the property exactly; the run shows
  the device realizes the compiled sign table at first order.

### F4. Batch order confounds a blocked contrast (hardware)

- **Conjecture tested.** The original signed probe resolved the sign of t
  at |t| = 0.25 (+0.022 +- 0.0067, z 3.29).
- **Outcome: the confound is real.** That job listed +t before -t, and a
  device with no signed response and a -0.044 shift on the second circuit
  reproduces the reading exactly.
- **Principle P3.** Interleave the arms of every contrast +, -, -, + within
  one calibration, so drift that is linear along the job's circuit list
  cancels in the odd part.

### F5. The noise model has a null offset; subtracting it restores the linear law (model)

- **Statement.** The exact calibration model gives the signed probe an odd
  part of +0.0136 at t = 0, where the ideal is zero and every first-order
  coherent error leaves it zero: the +0 and -0 circuits differ in their
  rotation angles, so incoherent noise acts on them differently. The
  difference D(t) = odd(t) - odd(0) reads +0.0021 at |t| = 0.05 and +0.0095
  at |t| = 0.25, ratio 0.221 against the linear law's 0.222.
- **Outcome: withdrawn.** The earlier reading that the simulator departs
  from the linear law at small |t| was this additive offset.
- **Evidence.** [null-controlled cases](../../design/iqm-garnet-signed-kernel-probe.md#null-controlled-follow-up),
  [prediction](../../../results/iqm/cases/signed-kernel-null-retest/prediction.json).
- **Principle P4.** Give every odd-part contrast a null arm at the
  parameter value where the ideal odd part vanishes, and decide on the
  difference.

### F6. The |t| = 0.25 sign does not survive the null control (hardware, preregistered)

- **Outcome: the original claim is superseded.** On set `68b0f1d0`, in
  balanced order with a t = 0 arm (5.50 credits): odd(0.25) = +0.0090 +-
  0.0031, odd(0) = +0.0025 +- 0.0031, D(0.25) = +0.0065 +- 0.0045 (z 1.46),
  unresolved. The visibility after subtraction, 0.058, sits inside the
  model's 0.05 to 0.09; the original run implied 0.206.
- **Evidence.** `iqm-garnet-signed-null-retest`, which supersedes
  `iqm-garnet-signed-kernel-probe`;
  [analysis](../../../results/iqm/signed_kernel_null_retest_analysis.json).

### F7. Garnet's negative even offsets lie outside the stationary coherent model (open)

- **Observation.** The signed probe's even part reads -0.022 and -0.012
  (set `9069c4ef`) and -0.0195 and -0.0175 (set `68b0f1d0`), against
  +0.029 from the calibration model and +0.031 from readout alone: the
  circuit pushes the reading about 0.045 toward |1>.
- **Attributions withdrawn.** A 0.6 % and then a 2.7 % QB11 over-rotation
  were proposed from noiseless derivatives. Through the noise model every
  stationary coherent response shrinks to 5 to 10 % of its noiseless size,
  unevenly (QB11 over-rotation -0.43 against -8.02 per unit), so QB11 alone
  would need 10.5 %, three times the 3.5 % its RB infidelity allows, and all
  29 terms aligned at that bound reach 0.032. The cancellation run measured
  QB11 at +0.15 +- 0.07 %.
- **Open.** Leakage read as 1, crosstalk, time-dependent error and readout
  under heralding are untested.
- **Principles.** P5: compute a coherent-error response through the
  device's noise model, not the noiseless circuit, before scaling it to a
  measured offset. P6: a depolarizing model built from RB fidelities keeps an
  error's infidelity and drops its signed first-order effect; a case that
  reads a first-order observable measures the coherent parameters it
  depends on in the same job (error-amplifying trains with their own
  readout calibration).

### F8. An observable can be immune to coherent error at first order (model)

- **Statement.** In the signed probe every stationary coherent error adds a
  term proportional to sqrt(|t|/(2 + |t|)) to the odd part, so a coherent
  error fakes a signed response. In the cancellation compile every such
  error except the theta qubit's over-rotation has zero first-order
  response in both parts, and that one scales the odd part.
- **Evidence.** `iqm-garnet-signed-probe-coherent-response`; the
  cancellation case's `response` in its prediction.
- **Principle P7.** Prefer an observable whose odd part takes no additive
  first-order term from any coherent error of the compile.

### F9. The Cayley-Dickson sign has joint degree max(2, n) (exact, n <= 6)

- **Statement.** f(p, q) in e_p e_q = (-1)^f e_(p xor q) has algebraic
  normal form degree max(2, n) over the 2n index bits in dimension 2^n,
  with C(n, 2) + n quadratic monomials and (2^(k - 1) - 1) C(n, k) of
  degree k >= 3. Its degree at a fixed left factor, n - 1, is Theorem 1 of
  [cd_phase_degree.md](../cd_phase_degree.md), which proves it for every n.
- **Evidence.** `cd-sign-cocycle-degree`, gate `core-640`. The joint count
  is checked to n = 6 and unproved beyond.
- **Consequence.** Octonion left multiplication is a quadratic phase (CZ
  and Z gates); sedenion left multiplication reaches degree 3 (CCZ).

### F10. Engineering invariants the runs forced (tooling)

- A free mock twin refuses a job pinned to the QPU's calibration set
  ("Calibration set not found"), so a case pins its set per quantum
  computer.
- The analysis decides against the prediction the approval covered:
  cases.json records the prediction's digest, and an analysis refuses mock
  runs, other case bytes, other calibration sets, repeated runs and failed
  jobs.
- An approved credit limit lives in cases.json, and IQM bills ceil(runtime)
  with no job-side cap, so the limit bounds a predicted bill
  ([issue #376](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/376)).

## Principles, in order of use

1. P1 mutation test: the observable must change when the property is removed.
2. P2 eigen-observable: read the property as an operator eigenvalue on its
   reachable span.
3. P7 first-order immunity: no additive coherent term in the odd part.
4. P3 interleaving: +, -, -, + within one calibration.
5. P4 null arm: decide on odd(t) - odd(0).
6. P5 and P6 coherent parameters: response through the noise model, and the
   parameters it depends on measured in the same job.
