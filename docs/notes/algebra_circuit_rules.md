# Algebra circuit design rules

These rules bind every circuit, case, analysis and note that encodes
Cayley-Dickson arithmetic on a qubit register. The root AGENTS.md carries a
digest of the binding rules; this note is the full text.
`docs/evidence/reviewer_associator_audit/` replays the numeric claims below
(gate sources-240), and `scripts/algebra_circuit_fixtures.py`
(gate core-251) runs the zero-product, Hadamard-basis and
workspace fixtures on the circuit builders of `designs.py`.

## Algebra arithmetic contract

`cd_core` evaluates the real Cayley-Dickson algebra with ordered basis
`e_0, ..., e_(D-1)`, `e_0=1`, and the doubling
`(a,b)(c,d)=(ac-conj(d)b, da+b conj(c))`. Conjugation fixes coordinate zero
and negates every imaginary coordinate, recursively
`conj(a,b)=(conj(a),-b)`. Both halves use the same ordered basis.
The level-zero algebra has dimension one and ordinary real multiplication.

Every dimension is a positive power of two. Every basis index lies in
`0..D-1`; integer-index objects are normalized through `operator.index`.
Every coefficient vector has exactly `D` entries. `fano_completion` accepts
two distinct imaginary octonion indices in `1..7`, and
`left_mult_matrix_check` accepts all octonion basis indices in `0..7`.
Invalid dimensions, indices, lengths and exact scalar types raise `ValueError`.

`cd_multiply` and `left_mult_matrix` provide numerical binary64 evaluation.
The numerical product's scale-sensitive forward-error bound is documented in
`cd_core.cd_multiply`; overflow, underflow and nonfinite arithmetic lie outside
that bound. A computed numerical zero alone supplies no exact zero-product
certificate. `cd_multiply_exact`, `left_mult_matrix_exact` and
`left_mult_determinant_exact` accept only `int` and `Fraction` coordinates,
reject Boolean and floating coordinates, and return `Fraction` values.
A decimal spelling may be parsed into `Fraction` when that spelling defines
the intended rational; measured inputs retain their measurement uncertainty.

The left-action matrix has column `q` equal to `v e_q`. The core exposes
left action; separate research modules define and check any right-action
construction. Algebra vectors have unrestricted norm; circuit statevectors
carry the normalization and success scaling of their encoding.

The [sign recurrence and derivation](left_mult_sign_rank.md) and
[phase-degree inductions](cd_phase_degree.md) carry the all-stage written
arguments. The independent `verify.py` comparison checks 320 orientation
cells in the pinned dimension-8/16 tables and 336 ordered signed zero-product
rows. Those rows cover disjoint signed two-support imaginary factors.
The [sparse count ledger](topics/cayley_dickson_sparse_census.md) distinguishes
84 first operands, 84 table pairs, 168 first-relative-sign-positive rows and
336 ordered signed rows.

The [associator census](topics/cd_associator_defect_census.md) counts 168
nonassociating triples among 210 ordered distinct imaginary octonion triples,
or among 512 all-basis triples when scalar and repeated indices are included.
The sedenion all-basis count is 1848 among 4096 ordered triples. Every reported
count names its denominator.

## Sedenion determinant and membership

Write `v=(x_0+u,x_8+w)`, with imaginary octonions `u,w`, and set
`s=x_0^2+x_8^2`, `A=||u||^2`, `B=||w||^2`, `gamma=<u,w>`.
Then `D1=s+A+B`, `D2=s^2+2s(A+B)+(A-B)^2+4 gamma^2`, and
`det L_v=D1^4 D2^2`. The factorization comes from
[Koebisu's version-2 preprint](papers/2512.13002.md); the real nonzero
membership and annihilator results have the
[Biss-Dugger-Isaksen foundation](math-0511691.md). Nonzero membership requires
all three conditions `s=0`, `A=B` and `gamma=0`.

`rank_polynomials.evaluate_sedenion_determinant` evaluates those factors
and an exact left-matrix determinant on precisely 16 rational coordinates.
Gate `core-044` compares both determinants on 300 seeded integer and 100
seeded rational vectors plus the two determinant-256 controls `e0+e9` and
`e1+e9` and the zero divisor `e1+e10`. Removing `4 gamma^2` fails the
orthogonality control `e1+e9`. The replay is a bounded implementation check;
the written source arguments supply the all-real identity.

The [research registry](../state/RESEARCH_STATE.md) records publication
provenance, repository-written proofs, exact finite certificates, Rocq proofs
and open questions separately. Sparse dimension-32 rank counts describe their
coefficient family; a global continuous-locus classification remains open.

**Encoding and representation.**
- The map `a -> L_a` is a linear encoding, not an algebra homomorphism.
  Associative matrix composition represents a non-associative product through
  `(L_a L_b - L_ab) c = -(a, b, c)` with `(a, b, c) = (ab)c - a(bc)`: two
  wirings compared by an observable, never a claim that matrix products
  fail to associate. A faithful associative representation of a
  non-associative product does not exist.
- A sedenion-coefficient encoding states its coefficient domain (real or
  complex), normalization, basis convention (`cd_core.cd_sign`, doubling
  `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`) and scale. The basis
  state `|0>` is `e_0 = 1`, the multiplicative identity, never the zero
  vector. A unitary cannot output the zero vector: an algebraic zero product
  is a heralded branch of zero probability while the full state keeps norm 1.
- Algebra index bit `b` sits on register qubit `b` (`designs.left_mult_gate`),
  so qubit 0 carries the least significant bit, matching Qiskit's
  little-endian outcome strings; a register drawn or read in another order
  states its map.
- A product sign carried as the global phase of a block is unobservable on
  its own. A Hadamard test sees it only when the sign is set on the block
  before it is controlled, so the controlled block applies it as a relative
  phase on the control (`scripts/algebra_circuit_fixtures.py`).
- Norm multiplicativity `|ab| = |a||b|` holds for real coefficients in
  dimensions 1, 2, 4 and 8 only (Hurwitz). The real sedenions already have
  zero divisors, `(e1 + e10)(e4 - e15) = 0`, and the complex-linear extension
  has them even on associative subalgebras: `(e_0 + i e_1)(e_0 - i e_1) = 0`.

**Zero-product witnesses.**
- Certify every claimed zero-divisor pair with `cd_core` before circuit work.
  Four product terms that land on four distinct XOR labels cannot cancel:
  `(e1 + e10)(e2 - e13) = e3 + e7 + e8 - e12`, which is the repository's
  negative regression fixture (fixed-operand LCU `P(s = 0) = 1/2`). The
  corpus pair `(e1 + e10)(e4 - e15) = 0` is the dark witness, and
  `(e1 + e10)(e4 + e15)` is its bright control (`P(s = 0) = 1`).
- Read the selector's success outcome, not "output label unequal to zero".
  The fixed-operand LCU of Design B gives `P(s = 0) = ||x y||^2 / 2` for
  normalized `x = (e_i + t e_j)/sqrt2`, `t = +-1`, and normalized `y`;
  `designs.lcu_witness` builds `t = +1`, and `t = -1` adds a Z on the
  selector after its first H. The
  universal coefficient contraction of the D-dimensional algebra (D = 16 for
  the sedenions), `M|i, j> = sigma(i, j)|i xor j>`, has `M M^dagger = D I`,
  so its success Kraus operator is `M / sqrt(D)` and `P = ||x y||^2 / D`. Reports
  give success counts, attempts, the bright reference, the uncertainty and
  the implemented normalization; the dark floor carries preparation, coherent
  control, incoherent, readout and sampling contributions together.

**Signs, workspace and measurement basis.**
- A sign register prepared in `|0>` records the sign as a which-path label;
  phase kickback needs the register in `|->`, where `X|-> = -|->`. Every
  retained input or workspace register that differs between branches
  suppresses their interference and enters the overlap.
- Before two computation branches recombine, return every temporary register
  to a common state (undo branch-specific XORs), and include all registers in
  the overlap calculation.
- In a Hadamard test, `<X_c>` before the final H, or `<Z_c>` after it, equals
  `Re<psi_L|psi_R>`; `X_c` measured after the final H reads the pre-H `Z_c`,
  which is 0 for balanced branches.
- A uniform superposition over all `16^3` sedenion basis triples gives
  witness expectation `1 - 2(1848/4096) = 25/256` and `P(c = 1) = 231/512`;
  the deterministic `-1` belongs to a single non-associating triple or to
  input supported inside that sign sector.

**Observables and claims.**
- Associator-sign measurement, zero-product success and state-coherence
  reconstruction are three observables. The fixed-pair witness
  `W_ij = L_(e_i e_j)^dagger L_(e_i) L_(e_j)` is diagonal, so its expectation
  `sum_k rho_kk omega(i, j, k)` reconstructs no coherence of the data
  register. A selected coherence `<x|rho|y>` needs the `2^w` settings with X
  or Y on the `w` bits where `x` and `y` differ and Z on the rest, with the
  register order fixed: four settings (XX, XY, YX, YY) for a two-qubit pair,
  and at most 16 for a sedenion register.
- Logical register counts: fixed-pair associator test, 4 data qubits plus 1
  control; fixed sparse operand zero-product LCU, 4 data qubits plus 1
  selector; two-input signed lookup, 8 input qubits plus 1 sign qubit; three
  independent input registers with coherent branch control, 12 input qubits
  plus 1 control plus workspace. Routed gate costs are measured separately.
- Name the interferometer an associator-sign interference witness; a
  holonomy claim needs a parameter space, transport rule and closed-loop
  observable. Non-Abelian braiding is noncommutative and associative and
  supports no non-associativity claim. A circuit construction establishes
  ideal implementability, hardware data establish performance under a stated
  implementation, and a priority claim needs a separate literature
  comparison.
- IBM removed pulse-level control on 3 February 2025; designs use the gate
  set, fractional gates and dynamic circuits.

**Cayley-Dickson, quaternion and Clifford packages.**
`gororoba_quantum/cd_core.py` is the specification. A package result enters
evidence only through a declared map onto it, identity or a signed
relabeling checked on every basis pair; majority agreement is never the
criterion. `scripts/algebra_package_tables.py` binds each installed package
to its pinned release and retains its tables in
`docs/evidence/algebra_packages/tables.json` (CI rechecks them without
importing any package), and `docs/notes/packages/` holds one note per
package. Each package is an Arch package; a broken or missing one is rebuilt
and reinstalled from its PKGBUILD in `~/Github/PKGBUILDs` (`makepkg -si
--nocheck` in the package directory), never patched in place, and the note's
pinned digest is checked again after the rebuild. A Kaggle kernel builds the
same seventeen packages from the same pinned archives (`--fetch` and
`--install` apply the PKGBUILD recipes) and runs its entry only after
`--extract` regenerates `tables.json` byte for byte; SageMath stays on the
build host (`docs/notes/kaggle/hypercomplex-stack.md`). A Clifford algebra
is associative, so clifford, kingdon and galgebra reach cd_core only through
Cl(0,1) and Cl(0,2) (the complex numbers and quaternions); an octonion or
sedenion statement never rests on them.

| Arch package | Import | Version | Relation to cd_core | Use it for | Trap |
|---|---|---|---|---|---|
| sagemath | `sage`, `OctonionAlgebra(QQ)` | 10.10 | opposite algebra in natural order; sign flip on e3, e5, e6 is an isomorphism | exact octonion reference, quadratic forms, G2 | ported code reverses every product unless mapped |
| python-hypercomplex | `hypercomplex` | 0.3.4 | identical table (D = 8, 16 exhaustive; 32, 64 sampled) | exact certificates with `cayley_dickson_algebra(n, fractions.Fraction)` | a basis product costs about 4x more per doubling; `inverse()` exists for zero divisors |
| python-hypercomplex-engine | `hypercomplex_engine` | 0.5.0 | identical (standard); its split variant shares every associator sign | fast basis-sign oracle at D = 4096 and beyond | takes and returns `(sign, index)` tuples; `dim` changes which doubling is split |
| python-hypercomplex-algebra | `hypercomplex_algebra` | 0.2.0.2 | identical; wraps the engine | parsing and formatting expressions | not an independent witness; `multiply_many_expressions` folds left |
| python-cayley-calculator | `Cayley_Calculator`, then `sedenion` and the other level modules | 1.3.1 | identical table at D = 16 (gamma = -1) | elementary functions (exp, log, trigonometric) through D = 128 | coerces every coefficient to float64; `from octonion import *` loads python-octonion |
| python-cayley-dickson | `cayley_dickson` | commit abf96e7 | identical table at D = 8, 16 | reading and cross-checking only; the source carries no license | installs a top-level `src` package, so `import src` resolves to it; its pandas table reads transposed |
| python-octonion | `octonion` | 0.1.0 | signed relabeling from a Fano labeling, `pi = (0, 1, 2, 4, 3, 6, 7, 5)` with a flip on e6 | batched octonion tensors in PyTorch | index i is not cd_core e_i; its tensors are float64 while torch defaults to float32; owns the `octonion` module name; AGPL |
| python-splitoct | `SplitOct` | 0.16 (commit e29e72f) | split octonions: the same 512 associator signs, signature (4, 4) | negative control for associator-only tests; SymPy symbolics | not the octonions; isotropic elements have no inverse; GPL |
| python-mathdunders | `mathdunders` | 0.4.2 | none | operator plumbing for python-hypercomplex | contributes no algebra evidence |
| python-pyoctonion | `pyoctonion` | 3.12 | identical table at D = 8 (doubling over pyquaternion) | a further independent octonion check | `cal_multiply` prints every product, use `*`; imports the undeclared pyquaternion; no license |
| python-octonion-sedenion | `Octonion_Sedenion` | 1.0.0 (wheel only) | identical tables at D = 8, 16 | a fourth independent sedenion table | `sedenion.py` imports the top-level `octonion`, which python-octonion owns, and fails as installed; no license |
| python-numpy-quaternion | `quaternion` | 2024.0.13 | identical table at D = 4 | quaternion arrays as a compiled numpy dtype | compiled: Kaggle takes the pinned wheel |
| python-quaternionic | `quaternionic` | 1.0.18 | identical table at D = 4 | numba quaternion arrays, rotations | `q[1]` on one quaternion raises; read `q.ndarray` |
| python-pyquaternion | `pyquaternion` | 0.9.9 | identical table at D = 4 | scalar rotation quaternions | the PyPI sdist lacks the VERSION.txt its setup.py reads; the recipe writes it |
| python-clifford | `clifford` | 1.5.1 | Cl(0,2) on (1, e1, e2, e12) identical at D = 4 | numerical geometric algebra: rotors, spinors, conformal GA | associative; `Cl(p, q)` puts the p positive squares first; numba compiles on first use |
| python-kingdon | `kingdon` | 3.0.0 | Cl(0,2) identical at D = 4 | geometric algebra on numpy, sympy or torch from one code path | product `keys()` are blade bitmasks; imports anywidget |
| python-galgebra | `galgebra` | 0.6.0 | Cl(0,2) identical at D = 4 | symbolic geometric algebra and calculus | a one-generator algebra needs coordinates; a scalar needs `sympy.S.One` |
| python-hyprat | `hyprat` | 0.2.0 (GitHub tag) | identical at D = 8, 16 (measured to 32) at mu = -1; signs (-1, -1, +1) give the split octonions | exact rational Cayley-Dickson algebras with a doubling parameter, Hurwitz quaternions | `Hy.from_array(coeffs, signs=...)` names the algebra, lowest level first |

## Hardware probes

These rules bind every case that reads an algebraic property on hardware;
[algebra-hardware-probe-principles.md](topics/algebra-hardware-probe-principles.md)
derives each one from the run that forced it.

- Run the mutation test before a case reaches hardware: replace the
  property's input (the kernel vector by its bright partner, the sign table
  by flipped or random signs) and require the ideal observable to change.
  The signed overlap Re<L_e2 u|B(t)|u> = t/(2 + |t|) survives every such
  mutation, because L_e2^T L_e1 and L_e2^T L_e10 are antisymmetric, so it
  never tested the sedenion zero divisor.
- Read a zero-product property as an eigenvalue: (L_e1 + L_e10) u = 0 is
  the eigenvalue -1 of L_e1^T L_e10 on u, which a Hadamard test with an
  L_e1 reference branch reads as cos(2 theta) against 1 for the bright
  vector (`gororoba_quantum/kernel_cancellation.py`).
- Choose an observable whose odd part takes no additive first-order term
  from a coherent error of the compile; check it with the first-order
  response of every coherent error (`scripts/iqm_probe_audit.py`).
- Preregister the decision on the double difference kernel minus control,
  running the control (the bright vector) at every parameter value the
  kernel runs: on Tuna-17 the bright vector carried a signed response of
  -0.017 (z -4.3) and the kernel's difference from it was z -1.0, while
  Garnet's was z -4.3.
- Read the executed order of a contrast's arms from the provider's
  timestamps where the platform runs each circuit as its own job (Quantum
  Inspire), and decide only on contrasts whose executed order holds the
  design: Tuna-17 ran one listed +, -, -, + contrast as +, -, +, -.
- Set every continuous parameter on the target's angle grid (Tuna: pi/36)
  and refuse an emitted rotation off it; compile at a setting that keeps
  Clifford+T phases exact (`scripts/qi_cancellation_cases.py`).
- List the arms of a +- contrast +, -, -, + within one calibration, and give
  it a null arm where the ideal odd part vanishes: decide on
  odd(t) - odd(0). Where a batch holds fewer circuits than the contrast
  (Quantum Inspire's three), the balance spans batches and the case declares
  the assumption that each batch carries the same position effect. A blocked order and a missing null arm let a position
  effect and an incoherent offset pass for a signed response.
- Derive a coherent-error response through the device's noise model before
  scaling it to a measured offset; the noiseless derivative overstates it by
  ten to twenty times on a 199-CZ compile. A depolarizing model built from
  randomized-benchmarking fidelities drops an error's signed first-order
  effect, so a case that reads a first-order observable measures the
  coherent parameters it depends on in the same job, each through its own
  readout calibration.
- Bind the prediction an analysis decides against into the approved case
  (its digest in cases.json), and exclude mock runs, other case bytes and
  other calibration sets from the analysis.
