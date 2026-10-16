# scripts agent guide

This file applies to the analysis, checker and rendering scripts under `scripts/`. The repository's root AGENTS.md
carries every other rule and loads first; the section below repeats its
algebra circuit design rules byte for byte so they bind work started here.
Paths are repository-relative.

<!-- algebra-circuit-rules:begin -->
## Algebra circuit design rules

These rules bind every circuit, case, analysis and note that encodes
Cayley-Dickson arithmetic on a qubit register. The root AGENTS.md,
gororoba_quantum/AGENTS.md and scripts/AGENTS.md carry this section with
identical bytes; `ci/check_agents_sections.py` fails on any difference.
`docs/evidence/reviewer_associator_audit/` replays the numeric claims below
(gates sources-240 and sources-241), and `scripts/algebra_circuit_fixtures.py`
(gates core-251 and core-252) runs the zero-product, Hadamard-basis and
workspace fixtures on the circuit builders of `designs.py`.

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
same sixteen packages from the same pinned archives (`--fetch` and
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
<!-- algebra-circuit-rules:end -->
