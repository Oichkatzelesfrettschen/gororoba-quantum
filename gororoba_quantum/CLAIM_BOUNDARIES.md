# Cayley-Dickson circuit evidence and mathematical claim boundaries

The circuits implement finite algebraic calculations with ordinary complex
quantum amplitudes. Their associator spectra, zero-product interference, and
annihilator checks support a reproducible circuit benchmark. Those calculations
do not establish the three claimed solutions in "The Mathematical Triad:
Unsolved Problems Solved by Heron's 156 Qubits".

## Boolean phase sampling and query complexity

Design C prepares a uniform superposition, applies the associator phase, and
measures after a Walsh-Hadamard transform. One execution returns one outcome
with probability

```text
P(y) = |2^(-n) sum_x omega(x) (-1)^(x dot y)|^2.
```

One phase-oracle call produces one sample. Recovering a distribution, learning
its phase function, finding a hidden shift, and identifying hidden polynomial
level sets are different tasks. Each needs an oracle definition, input promise,
output criterion, error tolerance, and resource model. A phase assembled from
known multiplication tables also has synthesis and gate costs; assigning the
whole compiled phase a unit query cost does not remove those costs.

The primary literature already distinguishes solvable hidden nonlinear problems
from unresolved broader families. Childs, Schulman, and Vazirani,
[arXiv:0705.2784](https://arxiv.org/abs/0705.2784), give efficient quantum
algorithms for two hidden nonlinear problems and quantum-query results.
Decker, Draisma, and Wocjan,
[arXiv:0706.1219](https://arxiv.org/abs/0706.1219), give a quantum algorithm for
identifying hidden polynomials at fixed degree and variable count, for all but
finitely many field sizes, alongside a classical lower bound for their black-box
problem. These results do not justify transferring that lower bound to direct
Boolean evaluation or describing every degree-at-least-three problem as open.

The proposal's exponential classical lower bound fails for the stated direct
Boolean evaluation interface. If `f : F_2^n -> F_2` has degree at most `d`, query
all inputs whose Hamming weight is at most `d`. For each monomial support `S`,
its ANF coefficient is

```text
c_S = XOR over T subseteq S of f(1_T).
query count = sum_(k=0)^d binomial(n,k).
```

Every queried subset also has size at most `d`. These queries therefore recover
every coefficient, with polynomial query count for fixed `d`. The identity is
Boolean Moebius inversion, already implemented for truth tables in
[boolean_anf.py](boolean_anf.py). The existing bounded-degree interpolation
routine independently recovers the benchmark coefficients from those samples.
The high-bit cubic and quartic exemplars need 26 and 57 evaluations at widths
five and six, respectively. These are finite checks of the reconstruction
identity, rather than asymptotic quantum advantage measurements.

A directional derivative at an input is `f(x) XOR f(x XOR a)`, requiring two
evaluations. For `n >= d+1`, the parity of a degree-at-most-`d` function over a
`(d+1)`-dimensional affine cube is zero. A uniformly random Boolean function has
odd parity with probability one half on that cube. This gives a
`2^(d+1)`-query, constant-bias distinguisher for the specific polynomial-versus-
uniformly-random promise. Independent disjoint cubes amplify the distinction.
These arguments concern direct value access; an oracle that hides polynomial
level sets behind unknown labels has a different information contract.

Walsh probabilities also discard phase information. The two cubic functions
`f=x0*x1*x2` and `g=(x0 XOR 1)*x1*x2` have ANF masks `(7,)` and `(6,7)`.
They differ on eight of the 32 five-bit inputs, yet have identical squared Walsh
spectra. Translation multiplies each Walsh amplitude by a sign, which measurement
removes. Even complete knowledge of those probabilities fails to identify which
of these two functions generated them.

The implemented high-bit exemplars are especially transparent:
[verify.py](verify.py), `check_associator_walsh_hierarchy`, verifies at widths three through seven
that their Boolean phase is the OR of bits 1 through `n-2`. Let `m=n-2`. Their
supported outcomes have zero outer bits, with

```text
P(0) = (1 - 2^(1-m))^2;
P(y) = 2^(2-2*m) for every other supported y.
```

A classical sampler chooses zero with the first probability and otherwise
chooses a uniform nonzero `m`-bit outcome. The closed form supplies an efficient
sampler for this known family. Increasing ANF degree or adding non-Clifford gates
therefore supplies a compilation benchmark without establishing classical
sampling hardness. The degree rule for distinct imaginary basis pairs is checked
at dimensions 8 through 128; that finite denominator remains the evidence scope.
Bernstein-Vazirani terminology applies to the linear character rung. Simon's
period-finding promise and general hidden-polynomial promises require separate
algorithms and admission criteria.

## Linear-combination witnesses and the Albert algebra

Left multiplication by a Cayley-Dickson basis unit is an orthogonal signed
permutation. The map `a -> L_a` is a faithful linear encoding of multiplication
by a fixed operand because `L_a(1)=a`. Associativity of matrix composition does
not make that map an algebra homomorphism. In the repository's octonion sign
convention,

```text
(e1*e2)*e4 = +e7;
e1*(e2*e4) = -e7;
L_e1 L_e2 != L_(e1*e2).
```

A sedenion witness also refutes square preservation, which a Jordan embedding
would require. For `a=e1+e10` and `b=e4-e15`, the exact sign table gives

```text
a*b = 0;
a*a = -2*e0;
L_a^2 b = 0;
L_(a*a) b = -2*b.
```

This witness applies to the proposed sedenion left-multiplication map. It should
not be generalized to claim failure of the symmetrized octonion left-action
identity: octonion alternativity provides additional identities.

The Albert algebra `J_3(O)` has 27 real dimensions: three real diagonal entries
and three independent octonion off-diagonal entries in a Hermitian matrix. Its
product is the symmetrized matrix product. Designs B and D act on 16-dimensional
sedenion vectors through a five-qubit LCU circuit; the builders implement neither
the Albert product nor an exceptional Jordan state-and-effect model.

The success branch applies `(L_ei + L_ej)/2` to the normalized input, yielding
`P(ancilla=0)=||a*b||^2/8` for the two-term operands. Unitary dilation implements
that linear transformation in an enlarged complex Hilbert space. The dilation
retains the homomorphism obstruction above. Finite matrix arithmetic that
simulates an algebra and a faithful product-preserving representation are
different mathematical constructions. Hardware agreement with the LCU prediction
would validate the compiled interference experiment; it would not demonstrate
exceptional Jordan quantum mechanics or bypass the exceptional-algebra theorem.

The LCU mechanism has prior art described in
[DESIGN_NOTES.md](DESIGN_NOTES.md), including Childs and Wiebe,
[arXiv:1202.5822](https://arxiv.org/abs/1202.5822). A future Albert calculation
needs its own explicit encoding, Jordan-product evaluator, observable contract,
and comparison with ordinary quantum simulation before making physical claims.

## Zero-divisor topology and phase fringes

The square sum-of-squares composition restriction to dimensions 1, 2, 4, and 8
is Hurwitz's theorem. Hurwitz-Radon theory concerns the more general composition
and vector-field constraints. Failure of the square composition identity in
sedenions does not turn an arbitrary graph count into a topological invariant.

Write `Z_n={(x,y) in S^(2^n-1) x S^(2^n-1) : x*y=0}`. With this indexing the
sedenion case is `Z_4`. Its topology already has a classical description.
Reggiani, [The geometry of sedenion zero divisors, Section 2.2,
Theorem 2.2](https://arxiv.org/html/2411.18881v1#S2.SS2), attributes to Moreno the
diffeomorphism of the normalized pair space with `G2`, and identifies the
principal bundle

```text
SU(2) -> G2 -> V_2(R^7).
```

The base is the Stiefel manifold of orthonormal two-frames in seven dimensions;
the fiber is the unit sphere in the four-dimensional annihilator. Reggiani uses
operands of norm `sqrt(2)`. Constant rescaling identifies that pair space with
`Z_4` above. The continuous base is fundamentally different from a finite
assessor graph. The paper studies intrinsic metrics and curvature with explicit
geometric constructions. The repository's finite checks do not reproduce those
geometric proofs or settle topology for higher doubling levels.

[designs.py](designs.py), `_check_design_d`, verifies four-dimensional kernels
and Gram eigenvalue multiplicities `{0:4, 1/2:8, 1:4}` for the 84 standard signed
two-term sedenion elements in the corpus. Those kernels each supply a sphere
`S^3` of normalized partners. A finite list of fibers provides neither transition
maps nor a cell decomposition of the full variety.

The unsigned assessor graph derived from the same corpus has 42 vertices, 84
edges, and seven connected components. Treated as a one-dimensional cell complex,
it has `b0=7`, `b1=84-42+7=49`, and Euler characteristic `42-84=-42`. Adding every
triangle instead gives the seven octahedron boundaries: 56 faces, Euler
characteristic `42-84+56=14`, and a different homology. The shared edge count 84
therefore determines neither even these two finite complexes' Euler
characteristics nor the invariants of the continuous pair variety. The edge
formula in [the retained survey](../literature/notes/open_gororoba_survey.md)
is explicitly a cross-assessor graph count, supported at measured dimensions;
it is not an Euler-characteristic formula for `Z_n`.

Design D varies `b=(e_k+exp(i*phi)*e_l)/sqrt(2)` in the complex-linear extension
of the multiplication matrices. [predict.py](predict.py), `phase_sweep_p0`,
explicitly names that domain. For the witness `(e1+e10)(e4-e15)=0`, the sweep
has `P0=(1+cos(phi))/2`. The phase `phi=pi` is dark, whereas `phi=pi/2` has
`P0=1/2` and a complex operand. The intermediate sweep therefore leaves the real
zero-product variety. The nine listed phases also repeat the endpoint at
`2*pi`; they sample eight distinct phases. Fringe visibility characterizes the
interference signal under compilation and noise. Curvature of a named manifold
requires a metric and geometric observables beyond this cosine fringe.

## Retained predictions and a bounded research program

The quoted ratio 0.043 and visibility 0.860 come from different retained
calibration-based noise simulations:

| Record | Backend | Raw dark/bright ratio | Raw visibility |
| --- | --- | ---: | ---: |
| [2026-10-10T171827+0000](../results/live/2026-10-10T171827+0000/record.json) | ibm_kingston | 0.0431190292 | 0.9053799049 |
| [2026-10-10T165944+0000](../results/live/2026-10-10T165944+0000/record.json) | ibm_marrakesh | 0.0669144981 | 0.8600468775 |

The records carry simulator seeds, `noisy` member distributions, and
`tvd_noisy_to_ideal` comparisons. Their historical schema lacks the newer
submission-state fields and a hardware collection identity. Those numbers support
noise-model predictions for their recorded calibration and compilation choices.
They do not identify measured transmon outcomes. CZ counts, replica counts, and
visibility must retain their backend, calibration, seed, layout, and result
provenance. Disjoint small-register replicas use chip capacity for parallel
benchmarking; the capacity alone establishes neither a 156-qubit entangled
calculation nor quantum advantage.

The defensible program has three measurable targets: verify the algebra-to-
circuit identities, compare equivalent decompositions on fresh backend Targets,
and test whether hardware residuals exceed the calibrated noise predictions.
The third target needs separately approved QPU observations. An ideal circuit
that disagrees with its exact sign-table prediction falsifies the implementation;
a noisy fringe alone cannot falsify a theorem about the underlying algebra.
An advantage claim needs a precise task and the strongest relevant classical
baseline. A topological claim needs a justified chain complex or geometric
construction connecting the sampled surface to the named variety.

The [retained local audit](../results/hw_estimate/cayley_dickson_claim_boundaries.json)
contains the finite witnesses, including the quartic six-qubit Statevector
comparison. Its [verification manifest](../results/hw_estimate/cayley_dickson_claim_boundaries_verification.json)
binds the source hashes, runtime versions, and serial/four-worker equality.
The [fresh IBM dry-run record](../results/live/2026-10-11T200341.410400Z/record.json)
records the separate service-access and calibrated local-simulation evidence.

Run the local executable boundary checks from the repository root:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  cd gororoba_quantum
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" claim_boundaries.py
)
```

The command checks finite mathematical witnesses and Qiskit statevectors locally.
For a fresh service contact, Target fetch, compilation, and noise-model dry run,
use the existing approved-record workflow's planning entry point:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  cd gororoba_quantum
  "$PYTHON" live_run.py --out ../results/live
)
```

Record the resulting state and any admission exclusions. A successful service
contact proves API access; a completed dry run proves the recorded local
compilation and simulation surface. QPU execution requires the user's approval
of a written measurement case and estimated quantum seconds, tied to the retained
dry-run record. Submission must preserve the matching experiment, calibration,
layout, shots, seeds, policy, and QPY identities required by
[AGENTS.md](../AGENTS.md). These replay commands omit `--submit`.
