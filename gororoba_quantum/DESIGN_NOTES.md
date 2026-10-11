# Cayley-Dickson quantum circuits

Quantum circuits whose structure comes from the open_gororoba Cayley-Dickson
algebra kernel. Left multiplication L_{e_m} by a basis unit is a signed
permutation of the 2^k basis states (e_p * e_q = cd_sign(dim,p,q) e_{p XOR q}),
so it is unitary on k qubits. The designs turn two algebraic defects that the
kernel measures classically -- the octonion associator and sedenion zero
divisors -- into hardware observables on the 156-qubit Heron backends, and
extend each into a family: the associator into a Walsh spectrum along the
doubling ladder (design C), the zero divisor into a phase-resolved fringe
(design D).

Run `$PYTHON cd_core.py` for the classical structure, `$PYTHON verify.py` for
the ground-truth checks, `$PYTHON designs.py` for the circuit checks, and
`$PYTHON live_run.py --out ../results/live` to choose a backend and layout per
experiment from live calibration, compile, and noise-simulate (add `--submit`
to run on hardware). `verify.py` and `designs.py` exit nonzero on the first
failed check. predict.py computes every prediction from cd_sign and
cd_multiply; no circuit builder imports it. The "Measured" figures in the
design sections come from results/hw_estimate/ibm_fez_record.json, a fixed
ibm_fez compile at transpiler seed 20261010 under the 10:07 calibration of
2026-10-10, written by the single-backend harness that live_run.py replaces;
`live_run.py --backends ibm_fez --seeds 1` repeats that compile under whatever
calibration is live.

## Verification against the kernel

The sign table is ported from cd_kernel::cayley_dickson::signs::cd_basis_mul_sign_iter
into `cd_core.cd_sign`. `verify.py` reads each kernel CSV only after its sha256
matches every registry record under registry/data/project_csv that pins it.

- Convention pin: all 320 cells of the kernel's data/csv/multiplication_table_8D.csv
  and multiplication_table_16D.csv equal cd_sign by index and sign. This is the
  check that fixes orientation.
- Zero-divisor corpus: `sedenion_zero_divisor_corpus()` equals the kernel's 336
  signed rows of data/csv/reggiani_standard_zero_divisor_pairs.csv. The corpus
  is invariant under the rephasing e_p -> -e_p (p != 0), which flips the sign of
  all 42 octonion and 210 sedenion imaginary-imaginary products, so the corpus
  match is a structural check and carries no orientation evidence. `verify.py`
  runs that rephasing and confirms both facts.
- Octonion norm multiplicativity |x y| = |x| |y| holds on random vectors and the
  sedenion norm fails it on some vectors; both are invariant under the same
  orthogonal rephasing.
- The 42/168 associative/anti-associative split of ordered distinct octonion
  triples comes from the Cayley-Dickson signs. The all-positive XOR-indexed
  table is the group algebra of F_2^3, which is associative and splits 210/0.

## Phase degree along the ladder

Two finite results, checked exhaustively by `verify.py` for dims 8 through 128
and stated as conjectures beyond:

- The sign function f_m(x) = [cd_sign(dim,m,x) = -1] of L_{e_m} has algebraic
  degree log2(dim) - 1 for every m != 0. Octonion left multiplications are
  therefore Clifford (Z and CZ signs plus X), and sedenion ones carry a
  degree-3 sign (CCZ) outside the Clifford group.
- The associator phase omega_ij(x) of W_ij = L_{e_i e_j}^dagger L_{e_i} L_{e_j}
  has degree max(1, bitlen(max(i,j)) - 2): it depends only on the doubling
  level where the pair first appears. The census of unordered pairs by degree
  is 21 of degree 1 at dim 8; then 84 of degree 2, 360 of degree 3, 1488 of
  degree 4, and 6048 of degree 5 are added at dims 16, 32, 64, and 128. A
  sedenion W is quadratic (Clifford) although each of its three sedenion
  factors carries a cubic sign, so the composition cancels the cubic terms; W
  leaves the Clifford group from dim 32 on.

`verify.check_pathion_separator_sign_bridge` establishes an exact cross-level
identity behind the cubic rung. C881's 15 labels index the top-level dim-32
pathion cross-assessor components in PG(3,2); they are distinct from the seven
dim-16 sedenion box-kites. Extend C881's 8/7 heptacross indicator by H(0) = 0.
On all 16 four-bit inputs,

H(S) = [cd_sign(16, 8, S) = -1].

Both functions have ANF masks (1, 2, 3, 4, 5, 6, 7, 8), so direct phase
synthesis emits four Z gates, three CZ gates, and one CCZ. The partial
Reed-Muller solver includes the constant and every linear and quadratic
monomial, rejects degree at most two, and returns that unique cubic witness.
The result rules out a Clifford-only exact diagonal phase oracle in this fixed
binary encoding and shows that one CCZ suffices. The result does not establish
a lower bound for arbitrary classification protocols or circuit depth.

The current `C881_GF2CubicMinDegree.v` theorems check every nonempty linear
combination, six individual quadratic monomials, the cubic witness, and its
degree. Its exhaustive quadratic conclusion appears only in a comment.
open_gororoba's Rust search and the independent solver in `verify.py` establish
the finite lower bound; the Rocq source establishes the cubic upper-bound
witness. The verifier also requires the Rocq source bytes to match the reviewed
sha256 before admitting the copied labels and classes.

## Design A: octonion associator as a Fano Z-string

Source: cd_associator, A(e_i,e_j,e_k) = (e_i e_j) e_k - e_i (e_j e_k).

Finding: W = L_{e_i e_j}^{-1} L_{e_i} L_{e_j}, with L_{e_i e_j} = cd_sign(8,i,j)
L_{e_{i^j}}, is diagonal with eigenvalue +/-1, the associator sign of (e_i, e_j,
e_k). Across the 21 unordered pairs these are exactly the 7 non-identity 3-qubit
Z-strings, three pairs each, one per Fano line by point-line duality in
PG(2,2): W is +1 precisely on the associating subspace {0, i, j, i^j}. For
(i,j)=(1,2) the net operator is Z on qubit 2. The cd_sign(8,i,j) factor is a
global sign in an uncontrolled circuit and a relative phase under coherent
control, so every controlled use of W carries it.

Mechanism: the circuit appends L_{e_j}, L_{e_i}, L_{e_{i^j}} as three separate
gates with barriers, so the hardware composes them and performs the cancellation
down to the net Z-string; numpy never multiplies the operators. The octonions
are alternative, so L_{e_m}^2 = -I and L_{e_{i^j}} = -cd_sign(8,i,j)
L_{e_i e_j}^{-1}: the circuit implements W times a global sign. A
line-completing k0 (associative) and a one-bit-away k1 (anti) get opposite
signs. A Hadamard on the differing qubit, applied before the X gates that load
k0, prepares (|e_{k0}> + |e_{k1}>)/sqrt2 for either value of that bit of k0; W
maps it to the orthogonal minus state, and a second Hadamard makes the measured
bit deterministic. Three qubits, ancilla-free.

Predicted ideal: readout bit 1 with probability 1 for all 21 pairs. Confirmed by
statevector in `designs.py`.

Observable and falsifier: the readout-bit probability; ideal 1.0. A measured
value at or below 0.5 + 3 sigma means the phase did not survive, so either the
associator sign is miscompiled or readout is worse than reported.

Measured (results/hw_estimate/ibm_fez_record.json, calibration
2026-10-10T10:07:12-07:00): the (1,2) ISA circuit on ibm_fez is depth 55 with
16 CZ on physical qubits 131-133, and the same circuit under the backend noise
model gives P1 = 0.9685.

## Design B: sedenion zero-divisor interference witness

Source: find_zero_divisors(16, 1e-10). A sedenion zero divisor is a pair
a = e_i + e_j, b = e_k + s e_l (s = +/-1, disjoint indices) with a*b = 0 though
a, b are nonzero. `cd_core.sedenion_zero_divisors` enumerates the 168 signed pairs
of this family with a's second sign +1.

Mechanism: L_a = L_{e_i} + L_{e_j} is linear in a, so a one-ancilla linear
combination of unitaries applies (L_{e_i} + L_{e_j})/2 to |b> = (|e_k> +
s|e_l>)/sqrt2 and post-selects ancilla = 0. The post-selected data amplitude is
(1/2sqrt2)(e_i + e_j)(e_k + s e_l), so P(ancilla = 0) = |a b|^2 / 8, which is 0
for a zero divisor by perfect destructive interference. Four data qubits, one
ancilla.

Compilation (select_lcu.py): the ancilla-selected pair is one operator,
SELECT|a,x> = cd_sign(16,m_a,x)|a, m_a ^ x> with m_0 = i and m_1 = j. It factors
into one sign diagonal (-1)^g(a,x) over all five qubits, g = f_i ^ a(f_i ^ f_j);
X on the bits of i; and CX from the ancilla onto the bits of i ^ j. The input
|b> is loaded by H on a pivot bit of k ^ l, the sign or phase on that bit, CX
fan-out over the rest of k ^ l, and the X load of k last, so the X layer
relabels branches without touching their relative phase. g has degree 4 for
every pair of distinct nonzero sedenion units. `select_circuit` exposes both
the direct Reed-Muller Z/CZ/CCZ/C3Z route and the DiagonalGate route. Both
operators match all 105 signed-permutation definitions; under the pinned
Qiskit version, basis, optimization level, and seed, DiagonalGate saves 10 to
71 all-to-all CZ gates for every pair and remains the default. The builder
receives (i, j) and the input specification and never the expected outcome.

Checks: `designs.py` compares the SELECT operator against its signed-permutation
definition for both strategies over all 105 pairs (32 x 32, phase included),
the prepared state against its target for all 120 index pairs at 9 phases, and
all 168 dark and 168 bright circuits against |a b|^2 / 8 from cd_multiply. The
sparse-preparation checks require one H, popcount(k XOR l) - 1 CX, the optional
phase gate, exact symbolic-parameter binding, and in-range distinct indices.
Mutating the SELECT sign layer or loading k before the Hadamard fails these
checks.

Predicted ideal: zero-divisor pair (e1+e10)(e4-e15) gives P(anc=0) = 0; the
sign-flipped control (e1+e10)(e4+e15) gives P(anc=0) = 1.

Observable and falsifier: the suppression ratio P_zd / P_control on the same
physical qubits; ideal 0. A ratio not significantly below 1 means the
interference did not form, so the compiled product is wrong or gate error
erased it.

Measured (same record): the structural circuit is 27 CZ all-to-all; the ibm_fez
ISA circuit is depth 130 with 46 CZ on physical qubits 119, 131-134, and the
bright control compiled from the same initial layout is also 46 CZ. The noise
model gives P_zd = 0.0806 and P_control = 0.9021, ratio 0.089; both circuits
measure on qubit 133, and correcting each term with that qubit's
prob_meas1_prep0 and prob_meas0_prep1 gives ratio 0.075 (record field
design_b). The dense compile it replaces (Householder preparation plus two
controlled dense unitaries), transpiled onto the same initial layout under the
08:36 calibration with the same seeds, is 249 CZ with P_zd = 0.314, P_control =
0.677, ratio 0.464, so the comparison holds layout quality fixed. Readout
mitigation such as TREX corrects measurement bias in expectation values and
leaves gate error in place, so the CZ count is the lever it was.

## Design C: associator Walsh spectrum along the ladder

Mechanism: prepare |+>^n, apply L_{e_j}, L_{e_i}, and L_{e_i e_j}^dagger as
separate blocks between barriers, apply H^n, and measure all n qubits. The
adjoint block is built as the transpose X^{i^j} D_{i^j} with cd_sign(dim,i,j)
as a global phase, which holds at every dimension without the octonion identity
L_{e_m}^2 = -I. The net unitary is diag(omega_ij), so

P(y) = | 2^-n sum_x omega_ij(x) (-1)^(x.y) |^2.

Quantum composition stays associative; the circuit measures where the encoding
fails L_{e_i e_j} = L_{e_i} L_{e_j}. A degree-1 phase gives a single outcome
and a degree-2 phase a flat distribution on an affine subspace; the degree-3
exemplar at dim 32 gives a non-flat one.

Predicted ideal (qubit 0 least significant): dim 8 pair (1,4) gives P(2) = 1;
dim 16 pair (1,8) gives P = 1/4 on {0, 2, 4, 6}; dim 32 pair (1,16) gives
P(0) = 9/16 and 1/16 on each of {2, 4, ..., 14}.

`verify.check_associator_walsh_hierarchy` checks the high-bit pair
(1, 2^(n-1)) for n = 3 through 7. Its ANF contains every nonempty monomial over
bits 1 through n-2. The n=3 function is the linear Bernstein-Vazirani
character. The n=4 quadratic has polar symplectic rank 2 and a flat affine
support of size 2^2 = 4. Every rung has zero-frequency weight
(1 - 2^(3-n))^2; each other supported outcome has weight 2^(6-2n). The n=5
case therefore has weight 9/16 at zero and 1/16 at seven nonzero outcomes.
Only the n=3 character carries the standard BV/HSP promise. The higher-degree
forms are phase-oracle benchmarks whose nonuniform Walsh spectra fall outside
standard HSP coset sampling.

Checks: `designs.py` compares the composed unitary against diag(omega) and the
statevector distribution against the Walsh prediction for all 21, 105, and 465
pairs at dims 8, 16, and 32. The operator check is the stronger one: replacing
the adjoint by L itself changes W only by a global sign at dim 8, which leaves
every probability unchanged and fails the operator check by 2.0.

Controls: a sign flip of L_{e_i} at one input (flip) and the omitted adjoint
block (omit), each compiled from the experiment's initial layout. Ideal TVD from
the true distribution: 0.438, 0.328, 0.191 (flip) and 1.0 (omit) at dims 8, 16,
32.

Observable and falsifier: the full measured distribution. The run passes when it
is closer in TVD to the true prediction than to each control prediction by more
than the shot-noise TVD; a single favored outcome is not evidence.

Measured (same record): ibm_fez ISA circuits are 18, 51, and 96 CZ at dims 8,
16, 32. Noisy TVD to the true prediction is 0.065, 0.114, 0.196 against 0.372,
0.257, 0.259 to the flip prediction. Resampling the noisy distributions at 4096
shots gives a shot-noise TVD of 0.006, 0.017, 0.026 (99th percentile 0.011,
0.029, 0.037). The true circuit's histogram is closer to the true prediction
than to the flip prediction by a TVD margin of 0.31 and 0.14 at dims 8 and 16;
at dim 32 the margin is 0.063, a difference of two TVDs under twice the
99th-percentile shot noise of either, which more shots or a lower-error qubit
patch widens.

## Design D: phase-resolved annihilator fringe

Mechanism: Design B's circuit on |b_phi> = (|e_k> + e^{i phi}|e_l>)/sqrt2, using
the complex-linear extension of the real multiplication matrices. With
u = (L_{e_i} + L_{e_j}) e_k, the zero-divisor relation gives (L_{e_i} +
L_{e_j}) e_l = -s u, and |u|^2 = 2 because L_{e_i} e_k and L_{e_j} e_k are
orthogonal basis vectors, so

P(anc=0 | phi) = (1 - s cos phi) / 2.

phi = 0 and pi are the real inputs; intermediate phases are interferometric
probes. Every zero divisor's element a = e_i + t e_j annihilates a
4-dimensional space spanned by its corpus partners, and (L_{e_i} + t L_{e_j})/2
has Gram spectrum {0^4, (1/2)^8, 1^4} for all 84 such a, so P(anc=0) =
<b| B^dagger B |b> probes a positive operator with a 4-dimensional kernel.
`designs.py` checks the closed form for all 168 zero divisors at 9 phases, the
exemplar sweep circuits against it, and the kernel and spectrum for every a.
A dark-to-bright rotation cos(eps)|b_dark> + sin(eps)|b_bright> predicts
P(anc=0) = sin^2(eps); its preparation is not implemented.

Observable and falsifier: fit P0 = o + A cos phi + B sin phi over the 9 phases.
The ideal has offset 1/2, visibility 2 sqrt(A^2 + B^2) = 1, and phase
atan2(B, A) = 0 for s = -1; offset, visibility, and phase separate readout bias,
decoherence, and a miscompiled relative phase, which one suppression ratio
collapses. A cosine fringe shows interference; the support-mismatched bright
control and the operator checks tie it to the sedenion product.

Measured (same record): 46 CZ per point on the dark circuit's qubits; the fit
gives offset 0.491, visibility 0.826, and phase -0.0007 rad.

## Shared engine: the Cayley-Dickson ladder

`cd_core.cd_sign` and the L_{e_m} builders are the synthesis recursion under every
design, emitting L_{e_m} at any dimension 2^k. Doubling sends an upper-half unit
to an X on the new top qubit together with conjugation, a diagonal sign on every
basis state except e_0. This is a compiler recursion: "dimension 2^k maps to k
qubits" is a vector-space identity, and Cayley-Dickson multiplication is not a
tensor product, so the ladder is not a physical tensor-factor correspondence.
The sign tables are exponential in k, so the compiler targets small dimensions.

## Prior art

The octonions are a twisted group algebra of F_2^3: e_p e_q = F(p,q) e_{p+q}
for a 2-cochain F whose coboundary is the associator, a 3-cocycle, and the
higher Cayley-Dickson algebras arise by the same cochain twist (Albuquerque and
Majid, "Quasialgebra structure of the octonions", J. Algebra 220 (1999),
arXiv:math/9802116). The Fano Z-string of design A is a circuit reading of that
associator. The ancilla-controlled sum of unitaries in designs B and D is the
linear combination of unitaries of Childs and Wiebe (arXiv:1202.5822), and
DiagonalGate synthesizes the SELECT sign by Theorem 7 of Shende, Bullock, and
Markov (quant-ph/0406176). The contribution here is the convention-pinned
algebra-to-circuit compile with exact operator checks, the degree results along
the ladder, and falsifiable observables with controls; no literature search
establishes priority for the degree results.

## Reference: Fano plane and the Steane code

The weight-3 codewords of the [7,4,3] Hamming code are the 7 Fano lines that also
index the octonion imaginary units, and the Steane [[7,1,3]] code uses that
incidence while dropping the octonion orientation signs. This connection is real
and standard, not novel; it is a labeled reference point, not a proposed
experiment.

## Appendix (speculative): WarpTriad p-adic ansatz

spectral_core WarpTriad weights a three-wave resonance k + p + q by
padic_triad_weight, a scalar-amplitude weight that discards Fourier phase and
polarization. Mapping a triad to a 3-local ZZZ term with that weight as the
rotation angle gives a QAOA-style ansatz, but with no problem to solve and no
verifiable answer it has no falsifier and stays out of the runnable set. A
Hamiltonian or objective with exact small-instance answers, uniform and permuted
weight controls, and a classical exact-diagonalization comparison of p-adic
versus uniform weights are the prerequisites before any circuit.

## Live calibration and backend selection

`live_run.py` treats calibration as a property of the run. Each invocation
queries the active account for accessible systems unless `--backends` pins
names. The runner refreshes every requested backend, reads its status, queue
depth, configuration, Target, and properties, and records every successful,
ineligible, or failed probe. The audit record under `results/live/<UTC start>/`
stores the requested-system inventory, capability summaries, exclusion reasons,
logical circuit requirements, joint placement, fused execution-PUB manifests,
selection trace, exact fused ISA circuits, and simulated outcomes. The process
never reads a retained calibration record to drive a submission. Current
records use schema 5 and contract `live-target-cross-group-fused-pubs-v1`;
schema 4 and both historical schema-3 families remain retained evidence with
incompatible shapes.

- Eligibility: operational, status_msg "active", and at most 25 pending jobs
  (--max-pending); a long queue lets the calibration drift between compile and
  execution.
- Capability admission: each group derives logical width, direct operations,
  control flow, and static or dynamic kind from circuits built by the current
  process. After routing and replica placement, the runner derives the exact
  logical entry count, maximum classical width, packed layouts, and reference
  requirements. Same-backend, same-kind groups then draw from one placement
  pool before corresponding entries receive stable outer register namespaces
  and share Runtime PUBs. The exact fused circuits go to `isa.qpy`.
  The 10-million-execution Sampler bound applies to each result-complete fused
  job. Runtime 0.50 removed the old backend circuit-limit semantics and its
  `IBMBackend.max_circuits` property returns `None`, so the planner does not
  branch on that deprecated property. Classical width remains recorded evidence
  because BackendV2 exposes no separate classical-bit capacity.
- Exclusion policy (QUALITY in live_run.py): readout error above 0.08, CZ error
  above 0.03, sx error above 0.01, T1 or T2 below 20 us, missing calibration, or
  a faulty flag. Degraded hardware arrives without faulty flags: in the run of
  2026-10-10T16:59:44Z faulty_qubits() and faulty_gates() were empty on all
  three backends while ibm_fez reported CZ error 1.0 on edge 27-28, ibm_marrakesh
  T1 = 6.6 us on qubit 26 and readout error 0.145 on qubit 23, and the policy
  excluded 10, 8, and 27 qubits and 16, 24, and 20 edges on fez, kingston, and
  marrakesh.
- Selection: per experiment group and eligible backend, 8 transpiler seeds for
  the primary circuit; the top 3 by layout score compile their controls onto
  the same initial layout; the highest geometric-mean score across the group
  wins, queue depth breaking ties. The layout score is ESP times exp(-T sum_q
  1/T2_q), T the circuit's estimated duration, so idle dephasing on the chosen
  qubits counts beside gate and readout error. Before compilation, the runner
  copies the fresh Target and removes every instruction placement that touches
  an excluded qubit or CZ edge. The transpiler therefore routes inside the
  admitted hardware graph. Recursive `Target.instruction_supported()` checks,
  including fixed instruction parameters and control-flow blocks, validate each
  finished primary and control against the original fresh Target. Replica
  placement uses the filtered CZ graph. A round-fair backtracking allocation
  keeps replicas of one group one CZ hop apart and keeps fused groups
  physically disjoint. The same recursive validation covers every logical
  entry and fused PUB. A compile, placement, or final validation failure
  rejects that executable plan.
- Shared compile for the zero-divisor group: design B dark, bright, and the
  design D sweep are bindings of one circuit with a phase parameter on the
  input, so every member runs the same routing and reads out on the same
  physical qubit, and the suppression ratio compares one set of qubits.
- Mirror calibration: each single-observable witness (design A, design B dark
  and bright) gets a twin cut from its own compiled circuit -- a prefix of its
  dependency layers, a barrier, and the inverse -- on the same physical qubits,
  placed directly after the witness in the job. The cut is the layer within six
  of the depth midpoint whose twin best matches the witness in both scheduled
  depth and CZ count, so the match is approximate: in the dry run of record
  2026-10-10T193949.352436Z the design B witnesses carry 42 CZs and their twins
  40, and on FakeFez the twins sit within 9 percent of witness depth. The twin
  ideally returns all zeros, and the witness's <Z> divided by the twin's <Z> is
  its rescaled value (ODR, literature note 2507.08088). Design D's sweep points
  share the dark twin. The rescaled values stay unclipped; in that record's
  noise model they overshoot by under 1 percent (design A P1 1.002, fringe
  visibility 1.008). collect reports a replica's own ODR values only from
  runs of at least 16384 shots per replica (--shots). The pooled value is the
  mean over replicas of each replica's witness divided by its own twin, so
  replicas whose attenuations differ each divide by their own; its error over
  R replicas is that of one quotient at R times the shots, and it is reported
  when the replicas hold 16384 shots together. Either requires every witness
  and twin under one calibration, and a withheld view records its reason in
  odr_withheld.
- Nulls: these designs read interference through a final Hadamard layer, so the
  fully dephased and fully depolarized nulls coincide with the uniform
  distribution; every summary reports the TVD to uniform.
- Freshness proof: the Target that ESP and the noise model read agrees with the
  properties cached by the same `backend.refresh()` on every exposed gate error
  and duration and on every qubit's T1 and T2. The runner avoids a second
  property refresh that could cross a calibration boundary without rebuilding
  the Target. Ranking and prediction therefore describe one device state. One
  simulator is built per snapshot. A qubit carrying a faulty single-qubit
  instruction is excluded like a faulty qubit, and a backend without a native
  CZ is skipped as ineligible. A bounded-angle Target is rejected at routing
  admission because Qiskit exposes validation of its parameter bounds but no
  public accessor that can reproduce those bounds in the filtered Target; the
  rejection remains local to that system, so later viable systems still
  compete.
- Staleness: last_update_date advances without value changes (ibm_fez moved
  from 08:27 to 09:38 with all 352 CZ errors and 156 T1 values unchanged), so
  `--submit` rediscovers every requested system before any job leaves the host.
  An explicit `--backends` list probes those names directly and remains usable
  when account-wide backend enumeration fails; the default all-system path
  enumerates the accessible systems first.
  The pre-submission loop reruns deterministic selection across every fresh
  eligible system even while the prior choice remains valid. The comparison
  covers backend, layout, replica maps, entry identities, packed QPY identity,
  capabilities, exclusions, Target support, and used calibration values. It
  therefore reacts to degradation and can identify recovered hardware, a newly
  eligible backend, or a better alternate system. The fingerprint includes
  every routed Target
  instruction's error and duration, qubit coherence, asymmetric readout fields,
  and Target timing constraints. Any replacement is recompiled, re-simulated,
  and rearchived as a revised submit-free plan. The record enters
  `approval_required`, carries the new QPY digest and selection reasons, and
  exits before constructing a Runtime Sampler. A new written case and explicit
  user approval govern a later invocation. An unchanged approved plan refreshes
  the selected system again immediately before every static or dynamic job.
  Drift at that boundary stops the affected and later jobs; the retained ledger
  names each unsent fused PUB and logical component.
- Readout: every group record carries summary (raw) and
  summary_readout_corrected, which inverts each classical bit's readout channel
  with the prob_meas1_prep0 and prob_meas0_prep1 of the qubit that wrote it.
  A raw dark P(0) carries prob_meas0_prep1 as an additive floor even on a
  shared readout qubit. The noise model applies the same asymmetric channel,
  and in results/live/2026-10-10T183325.225102Z the correction moves the
  zero-divisor ratio on ibm_kingston from 0.0436 to 0.0369 and the fringe
  visibility from 0.9065 to 0.9175. With --twirl, collection inverts the
  symmetric mean channel, since measurement twirling averages the two flip
  probabilities. A group with feed-forward circuits records why the correction
  is skipped instead: a misread mid-circuit bit also steers the conditional
  gate, which no per-bit channel inversion models. A group whose shots
  straddle a calibration update keeps only its raw summary at collection.
- Archived definitions: the record stores a sha256 over every module of
  gororoba_quantum/ but verify.py -- the experiment definitions and live_run.py's
  own distribution, readout, and replay code -- and the code commit; --collect
  refuses to summarize a run under a different digest, naming the commit to
  collect from.
- Durable job identities: the complete job ledger, ordered fused-PUB manifest,
  exact QPY archive SHA-256, effective options, and unique recovery tags reach
  `record.json` before a job call. An attempt marker and budget snapshot receive
  another checkpoint immediately before `Sampler.run()`, and every returned
  job id receives a checkpoint before the next job. Collection queries
  `service.jobs()` with
  the exact recovery tags and the live instance whose CRN matches the retained
  12-hex hash when a response-lost attempt lacks an id. One job and one instance
  restore the id; zero or multiple matches stop collection with the ambiguity
  retained. Atomic replacement fsyncs the file and containing directory. An
  instance without a usage limit passes the budget check;
  `usage_limit_reached` stops the run.
- Execution-time replay: --collect reads each circuit's execution window from
  the result's execution spans (result.metadata["execution"]
  ["execution_spans"], the spans whose pub_idxs include it), fetches
  target_history and properties at that window's start, flags a calibration
  update inside the window, checks the two against each other (342 of 352 ibm_fez
  CZ errors differ between 2026-10-09 and 2026-10-10, and the two history APIs
  agree on all of them), and re-simulates under that Target with the shots and
  simulator seed stored in the run's record.

Run of 2026-10-10T16:59:44Z (ibm_kingston skipped at 27 pending jobs):

| group | backend | layout | CZ (primary, controls) | noisy observable |
|---|---|---|---|---|
| design A (1,2) | ibm_marrakesh | 10, 9, 11 | 16 | P1 = 0.968 |
| design B/D fringe | ibm_marrakesh | 89, 88, 78, 90, 87 | 42 each | ratio 0.067; offset 0.485, visibility 0.860, phase -0.002 |
| design C dim 8 | ibm_fez | 145, 146, 144 | 18, 20, 16 | TVD 0.065 true vs 0.372 flip |
| design C dim 16 | ibm_marrakesh | 11, 12, 10, 18 | 49, 54, 28 | TVD 0.114 true vs 0.254 flip |
| design C dim 32 | ibm_marrakesh | 11, 9, 12, 18, 10 | 96, 125, 64 | TVD 0.181 true vs 0.243 flip |

A later run of the same code (2026-10-10T17:18:27Z) found ibm_kingston's queue
at 9 jobs and moved every group to it, on the best medians of the three (T1
242 us, CZ error 1.93e-3): design B/D at 42 CZ reached ratio 0.043 and fringe
visibility 0.905 in the noise model, against 0.067 and 0.860 on ibm_marrakesh
earlier the same hour.

The divergent pre-integration schema-3 dry run at
`results/live/2026-10-10T220438.712726Z/` discovers all three accessible systems
from source commit `0205a61`. Fez and Kingston pass
eligibility; Marrakesh reports maintenance and remains recorded as ineligible.
Kingston wins all seven groups at 13 pending jobs. The record preserves each
system's capability summary, each group's circuit-derived requirements, every
capability and routing decision, and 31 unreplicated base and mirror ISA
circuits. Its lifecycle state is `planned`, `code_commit.sources_modified` is
false for the `gororoba_quantum/` source scope, and the absent `submission`
object establishes zero QPU jobs. The record predates replica placement,
isolated crosstalk references, variance decomposition, and statistical
admission, so it does not qualify the integrated schema-4 execution path.

The post-review schema-4 dry run at
`results/live/2026-10-10T232219.919322Z/` uses source `584a78d` with
`sources_modified=false`. The default queue gate first rejects Fez at 147
pending jobs and Kingston at 95; Marrakesh reports maintenance. The retained
submit-free rerun uses `--max-pending 250`, records Fez and Kingston as eligible
under that explicit bound, and records Marrakesh as ineligible. Kingston wins
all seven groups. The archive contains 38 unique packed circuits, including
seven isolated references, and its names exactly match both the member records
and final execution requirements. Every group records its effective replica
floor: 0.9 for six groups and 0.8 for hybrid Shor, which places nine replicas.
All three discovered systems reported the historical `max_circuits=null` field;
schema 5 drops that deprecated field and enforces the documented Sampler
execution bound directly. The lifecycle stays `planned` with `submission`
absent. The record therefore qualifies the combined
discovery, capability, routing, Target-validation, replica, variance, and
archive path while recording zero QPU jobs. Approval-gated pre-submission
selection, immediate batch revalidation, and recovery remain credential-free
contract evidence until an approved submission exercises them.

Schema 5 replaces the one-logical-entry-per-PUB execution surface with joint
cross-group placement and exact fused circuits. Credential-free contracts
prove the 29-to-14 static and 9-to-6 dynamic cardinalities, unique nested
register namespaces, static classification after fusion, client-side dynamic
feed-forward execution, QPY component reconstruction, overlap and width
rejection, Sampler execution-bound rejection, and PUB-manifest tamper
detection. The QPY archive and Runtime submission now contain the same fused
circuits; logical entries remain the decoding and statistical units.

Submission partitions each backend into static and dynamic result-complete
clusters. Row zero fuses all packed primaries, row one fuses the groups'
replica-0 primary references, and later rows align remaining members and
mirrors. The longest static group therefore determines 14 PUBs and the longest
dynamic group determines 6. Each cluster stays in one client-side Sampler job
under the 10-million-execution job bound. The complete planned-job ledger,
ordered logical member names, PUB-to-component manifests, exact QPY archive
SHA-256, calibration stamps, effective options, and recovery tags reach the
record before the first job. Recovery tags hash the complete PUB manifest. Each
accepted job adds its job id and budget snapshot. `usage()` runs before every
job against the instance selected for that backend. A fresh job snapshot must
preserve status, capabilities, admitted qubits and CZ edges,
routed instruction support, calibration fingerprints, and sampler options.
Sampler then receives that exact refreshed backend object. The record stores
the instance only as a hash. The
client-side Sampler comes from
`qiskit_ibm_runtime.executor_sampler`, the destination the
migrate-qiskit-ibm-runtime skill sets for qiskit-ibm-runtime 0.50.
--twirl enables gate and measurement twirling and --dd sets a
dynamical-decoupling sequence (XX, XpXm, XY4); both act on hardware and are
absent from the Aer noise model, so a hardware-versus-model gap with them on
measures their effect. Circuits with mid-circuit measurement, reset, or
feed-forward go in a separate job per backend with dynamical decoupling and
twirling off: IBM's Sampler rejects dynamical decoupling on dynamic circuits,
and in runtime 0.50 the client-side Sampler's twirling boxes circuits through
samplomatic, which rejects if_else (found by the migrate-qiskit-ibm-runtime
skill's local verification). The static twirling path fixes 32 randomizations
explicitly and requires at least 2048 shots divisible by 32. That contract
keeps Runtime 0.50's minimum of 64 shots per randomization from rounding the
recorded request upward. The
10-minute monthly budget is quantum execution time, so the samples each shot
yields set what a second of it buys; packed replicas, below, multiply them.

## Packed replicas and variance decomposition

Every group runs on several disjoint copies of its compiled layout at once
(packing.py). The chosen compile's pattern -- the physical qubits its circuits
touch, mirror twins included, and the CZ edges between them -- is embedded in
the backend's CZ coupling graph by subgraph isomorphism (rustworkx
vf2_mapping). An embedding is admissible when every moved operation exists in
the live Target and avoids the excluded qubits and edges of that run's
snapshot; admissible embeddings rank by the layout score of the moved primary
circuit. The joint allocator takes them in backtracked rounds, one qubit apart
within a group and physically disjoint across groups that share a PUB, until
the remaining groups cannot advance together or --max-replicas is reached. An
explicit --replica-floor sets the
floor for every group; otherwise a group's declared floor applies (hybrid
Shor declares 0.8) and the rest use 0.9. A replica is the identical gate
sequence on other qubits, so replica-to-replica differences are hardware
differences. Each member and twin first forms one packed component, every
replica's gates ahead of every replica's terminal measurements so a static
circuit stays static. Corresponding cross-group components then receive outer
register namespaces (g0_, g1_, ...) and share a fused PUB; the fusion again
places every static body ahead of every terminal measurement. Inner registers
(r0_, r1_, ...) preserve replica identity, so joining one namespaced replica's
registers recovers its distribution.
Simulation, readout correction, and replay run on each replica alone, since
the Aer model carries no crosstalk and a packed width of 21 replicas is beyond
dense simulation. Each group's primary also runs on replica 0's qubits in one
shared reference PUB. Its difference from packed replica 0 compares the global
packed workload with the global replica-0 workload. The result can reveal a
packing cost, but it cannot attribute crosstalk to one group; the noise model
sets the difference to zero.

variance.py scores each shot by the ideal-weighted w(x) = q(x)/max q, or by a
member's own outcome weights (hybrid Shor scores whether an outcome decodes to
a verified factor, since every outcome of its pruned circuit lies in the
ideal's support). Per member, the between-replica variance of the mean score
minus the shot variance is the layout variance, a chi-squared test asks
whether the replicas agree within shot noise, and a replica more than three
shot standard deviations from the median is flagged
(literature/notes/2507.08088.md, action item 3). Folded QPE's four
eigenstates are equal-cost instances, so a two-way decomposition separates
instance, layout, and interaction variance (literature/notes/2509.18259.md,
action item 4). Every pooled summary value is the mean of that value computed
on each replica alone, so a ratio, fringe fit, or TVD and its interval share
one estimand. Every pooled value gets a Student t interval over its replicas. A
value the group declares a per-shot rate also gets a Wilson interval over the
pooled shots, and its reported interval is the union of that and the replicate
interval, so replicas that agree exactly keep their shot uncertainty. Each
member, twin, and shared-reference component belongs to an aligned fused PUB.
Every group summary, global packing comparison, and admission view combines
multiple PUBs, so when those PUBs do not all run under one calibration with no
update inside their shots, collect publishes only each entry's own replica
variance beside the raw distributions and records the reason in
`comparisons_withheld`.

The dry run of record 2026-10-10T222132.627032Z (code 02a5b4b) placed every
group on ibm_kingston, whose snapshot excluded 7 qubits and 24 edges:

| group | replicas | qubits per shot | score best -> last | predicted layout variance (primary) |
|---|---:|---:|---|---:|
| design A (1,2) | 21 | 63 | 0.932 -> 0.851 | 2.3e-5 |
| zero-divisor fringe | 6 | 30 | 0.803 -> 0.731 | 1.6e-4 (dark) |
| design C dim 8 | 18 | 54 | 0.899 -> 0.846 | 2.5e-4 |
| design C dim 16 | 8 | 32 | 0.755 -> 0.681 | 2.1e-4 |
| design C dim 32 | 4 | 20 | 0.593 -> 0.541 | 3.7e-4 |
| folded QPE mod 15 | 3 | 15 | 0.670 -> 0.604 | 2.7e-4 (s1) |
| hybrid Shor N = 15 (floor 0.8) | 7 | 35 | 0.691 -> 0.569 | 3.1e-5, within shot noise (p 0.17) |

The predicted layout variances come from the per-qubit calibration the noise
model reads; a measured layout variance above them, or a crosstalk difference
beyond shot noise, is hardware structure the model omits. In that record the
folded-QPE decomposition predicts instance variance 9.5e-5 against layout
variance 3.3e-4, so the patch a circuit runs on moves its success rate more
than which eigenstate it reads.
