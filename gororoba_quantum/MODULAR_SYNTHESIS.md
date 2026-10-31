# Exact N=21 synthesis and the boundary of impossibility

The N=21 modular multiplier is inexpensive enough to challenge the quoted
48,895-CZ ANF and 63,818-CZ cycle implementations. The exact Boolean target-flip
network uses 5,492 CZ at the same ten-round precision and reference FakeFez
seed. The finite counterexample changes the compiler frontier. Physical
usefulness still requires fresh calibration, noise simulation, measured
dynamic latency, and a positive decoder margin.

## Separate the three claims

The identity-padded multiplier fixes zero and every invalid data value. For
N=21, multipliers 2, 4, and 16 have respectively 12, 14, and 14 fixed points
among 32 register states. Their occupied XOR-displacement counts are 16, 14,
and 14. Multiplier 2 therefore has substantial dispersion rather than maximal
dispersion: multipliers 10 and 19 modulo 21 have 19 occupied fibers, and a
five-bit permutation can occupy all 32.

Words in Cayley-Dickson basis left multiplications remain signed translations
of the form `|x> -> sign(x)|x XOR t>`. A nonidentity translation moves every
index. That restricted dictionary cannot express the nontrivial modular
permutation as one word. Its exact scaled LCU also obeys the established
`lambda/|beta| >= T` floor; T=16 bounds its raw good-branch probability by
1/256. These conclusions constrain the dictionary and its postselection
construction. They supply neither a general CZ lower bound nor a physical
impossibility theorem.

A state-conditioned target flip instead implements
`x -> x XOR (predicate(x_without_target) << target)`. The predicate creates
fixed points and enlarges the available permutation group. The target-flip
counterexample leaves the signed-translation obstruction intact. Adding only
diagonal signs would preserve the restricted permutation action.

An invertible affine map over GF(2) has either zero or a power-of-two number
of fixed points. The 12/14/14 fixed-point census rules out a purely affine
network, even after arbitrary bijective relabeling. A CRT 3-by-7 register
offers another cheap N=21 demonstration, but its encoder consumes known
factors. The implemented compiler derives its complete permutation from
public N and multiplier alone; the compiler consumes neither factors,
reference orders, nor orbit labels.

## Factor predicates before expanding basis transpositions

`target_flip.py` pairs inputs and outputs along a chosen target bit. Each
permutation entry forms an edge between its input pair and output pair. Every
vertex has degree two, so each bipartite cycle admits alternating edge colors.
The first target switch sends the input bit to its edge color; the last switch
sends that color to the output bit. The middle permutation preserves the bit
and splits into two smaller permutations. Recursion joins the branch
predicates and yields at most `2*n-1` target layers.

Every layer predicate excludes its target. Its cube flips commute and combine
by XOR parity, so predicate expansion preserves reversibility. The compiler
searches all 120 bit orders and the reversed networks of inverse permutations
at width five. Component color orientation minimizes a switch-count heuristic;
the search establishes a bounded family, rather than globally optimal circuits.

Each four-variable predicate has 65,536 possible truth tables and an 81-cube
dictionary. A graph vertex is a truth table; an edge XORs one cube into the
table. Edge weights 1, 6, 12, 18, and 24 count the exact phase-controlled
CX-equivalent synthesis cost for zero through four data controls. Dijkstra
computes the minimum cost for every vertex. The verifier checks every graph
edge's distance inequality and every nonzero vertex's descending equality
witness. Canonical reconstruction chooses the first cube satisfying that
equality and validates the full predicate again. The bound requires at most
five data qubits: a six-bit network would expose five-variable predicates and
a graph of 2^32 truth tables.

`modular_arithmetic.py` emits one exact controlled cube at a time, using
explicit one-clean MCX synthesis when needed. The default selects target
flips for measured N=21 multipliers 2, 4, and 16. Other generic defaults keep
the existing one-clean cycle path. The ANF coefficient census remains a
property of the original multiplier truth table; the new target-flip count
and control-arity histogram describe the emitted circuit.

## Exact witnesses and compiled cost

All three multiplier networks contain 17 controlled cubes. The ten-round
schedule has 170 cubes, with control arities 2/3/4/5 occurring 20/87/20/43
times. Explicit synthesis produces 512 RCCX and 170 CCX gates, equivalent
to 2,556 CX before routing. The prior cycle has 2,694 RCCX and 449 CCX gates,
equivalent to 10,776 CX. Open-control X gates restore their input state even
on the disabled phase branch.

`proofs/TargetFlipN21.v` independently evaluates the integer gate word and
the modular formula. Rocq proves all 64 packed phase/data inputs for each
multiplier, including padding states 21 through 31 and the disabled control.
The exporter binds the proof's witness lists to the compiler's actual output.
Fresh compilation and kernel checking succeed, and the theorem assumption
reports are closed under the global context. Deleting a required gate makes
both exporter freshness and actual Rocq compilation fail.

The Boolean certificate excludes quantum gate phases and workspace behavior.
The independent Qiskit Operator checks inspect all 32 data inputs and both
control branches with clean workspace, requiring the expected amplitude +1
and restored workspace at tolerance 1e-12. Operator linearity extends those
basis-column checks to coherent superpositions within the clean-workspace
input subspace. Native-gate lowering to Aer is required before local sampling;
the CLI now transpiles explicit RCCX synthesis to Aer-supported instructions.

| Circuit | Logical qubits | Reference CZ / depth | Eight-seed CZ range | Eight-seed depth range |
|---|---:|---:|---:|---:|
| Ten-bit one-clean cycle control | 7 | 17,736 / 47,354 | 17,736-18,773 | 47,354-49,688 |
| Ten-bit exact target flips | 7 | 5,492 / 13,355 | 5,394-5,623 | 13,355-13,790 |
| Five-bit exact target flips | 7 | 2,762 / 6,646 | 2,713-2,804 | 6,646-6,935 |

The reference seed is 20261010; the bounded seed set ends at 20261017. At
equal ten-bit precision the target flips reduce CZ by 69.0 percent and depth
by 71.8 percent against the cycle control, and CZ by 88.8 percent and 91.4
percent against the quoted ANF and scratch-free cycle respectively. The
captures retain source hashes, versions, full topology, pass-level resources,
and physical layouts. Historical controls remain in their original capture.

Precision is a separate admission axis. The existing exact decoder gives
five-bit ideal factor yield 0.2295125182 and uniform-null yield 0.0625, for
margin 0.1670125182. Ten-bit values are 0.3309426044, 0.14453125, and
0.1864113544. Smaller precision reduces dynamic feedback branches from 45
to 10 and measurements from ten to five while changing the phase law.
Ideal simulation recovers factors 3 and 7; the identity null returns zero.
The ten-bit default remains the faithful baseline. Five-bit precision is an
explicit finite benchmark choice, rather than a general Shor precision claim.

## Affine-residual challenger

`affine_residual.py` reads the degree-zero vector b and the degree-one matrix
A over GF(2) from the output-bit ANFs, so `f(x) = A x XOR b XOR q(x)` with q
of degree two and higher. The constant term of every output bit is a bit of
f(0), and modular multiplication fixes zero, so b = 0 for every unit modulo
21. When A has full rank, `r(x) = A^-1 (f(x) XOR b)` is a register
permutation whose own affine part is the identity, and `f = A o r`: the
circuit applies the target-flip network of r first and the linear network of
A second. `target_flip_network` synthesizes r unchanged. Swap-free
Gauss-Jordan elimination synthesizes A in place with 10, 11, and 12 CNOTs for
multipliers 2, 4, and 16; bidirectional search over GL(5,2) gives minima of
10, 9, and 9.

The linear part is singular for most units. Multipliers 2, 4, and 16 have
rank 5; the other eight units, 5, 8, 10, 11, 13, 17, 19, and 20, have rank 4.
A rank-deficient A has no in-place reversible realization, so the method is
inapplicable there and `multiplier_profile` raises ValueError naming the
rank. Multiplier 11, the inverse of 2, is the singular fixture in
`modular_arithmetic._verify`.

Each in-place CNOT from bit c to bit t is a target-flip cube with predicate
`x_c`, and a constant X is a cube with the empty predicate. Phase-control
emission adds the outer control to every cube, so a CNOT becomes a CCX and an
X becomes a CX. Order finding requires the identity on the disabled branch;
an uncontrolled CNOT network applies A there, and the verifier's mutation with
uncontrolled linear CNOTs moves 30 of the 32 disabled-branch states for each
multiplier. The argument binds the direct composition: a conjugated form,
uncontrolled `A^-1`, then controlled `r o A`, then uncontrolled A, keeps the
CNOTs uncontrolled but synthesizes the different residual `r o A`. Sharing
one conjugator across all rounds removes its boundary cost; the
[linear work-register encoding](#linear-work-register-encoding) searches
that family.

The exhaustive checks cover all 32 register states for each of 2, 4, and 16:
r is a bijection with identity affine part, `A o r` equals f, the reversed
order `r o A` differs from f, and deleting any single linear CNOT breaks A.
`_verify_multiplier` checks the phase-controlled circuit on both control
branches with clean workspace, requiring amplitude +1 and restored workspace
at tolerance 1e-12.

The residual alone costs 2,346 phase-controlled CX equivalents over the ten
rounds, 210 below the 2,556 target-flip baseline. The promoted linear
Toffolis add 678 for a 3,024 total. Minimum-CNOT linear networks bound the
direct composition at 2,892, so no in-place CNOT synthesis of A recovers the
baseline surrogate.

`affine_residual_challenger.py` builds both ten-round circuits through
`compile_evidence` and compiles them with the same preset pass manager on the
captured FakeFez target over transpiler seeds 0 through 7. Scheduled duration
is `estimate_duration` over the true-branch gate-time view of `live_run`, in
units of dt = 4 ns. That view omits classical feed-forward latency; both
circuits carry the same 20 H, 45 if_else, 10 measure, and 9 reset operations,
so the omitted latency is common to them.

| Seed | Baseline CZ | Challenger CZ | Baseline depth | Challenger depth | Baseline dt | Challenger dt |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 5,385 | 6,099 | 13,681 | 15,529 | 132,000 | 145,173 |
| 1 | 5,419 | 6,105 | 13,651 | 15,565 | 131,586 | 145,707 |
| 2 | 5,454 | 6,285 | 13,298 | 15,887 | 125,442 | 150,666 |
| 3 | 5,404 | 6,105 | 13,673 | 15,536 | 132,177 | 145,053 |
| 4 | 5,425 | 6,171 | 13,492 | 15,961 | 126,978 | 150,723 |
| 5 | 5,588 | 6,153 | 13,715 | 15,971 | 132,588 | 150,483 |
| 6 | 5,384 | 6,148 | 13,706 | 15,898 | 132,246 | 150,102 |
| 7 | 5,482 | 6,113 | 13,290 | 15,533 | 125,547 | 145,065 |
| Median | 5,422 | 6,130.5 | 13,662 | 15,726 | 131,793 | 147,904.5 |

Both candidates use seven logical qubits, and every seed routes onto seven
physical qubits. The admission rule requires passing logical-equivalence and
workspace checks, no logical-qubit increase, every seed no worse in routed CZ,
depth, and scheduled duration, and a strictly lower median routed CZ. The
checks pass and the qubit count holds, but every seed regresses on all three
metrics, by at least 565 CZ, 1,848 depth, and 12,876 dt, and the median routed
CZ rises 13.1 percent. The verdict is rejection. The default remains
`target_flip_1_clean`; `compile_evidence.py` compiles the challenger only when
`--candidate affine_residual_target_flip` names it. The script evaluates the
rule and writes `results/hw_estimate/n21_affine_residual_challenger.json`
with tool versions, source hashes, the rank census, per-multiplier networks
and checks, the surrogate totals, and every per-seed record.

## Linear work-register encoding

One uncontrolled B in GL(5,2) for every round turns round k into
`B C(g_k) B^-1` with `g_k = B^-1 f_k B`. The operations between rounds act
on the control qubit alone, so each `B^-1 B` pair between rounds cancels.
The first `B^-1` meets the work register in `|1>` and becomes the basis-state
preparation `B^-1 |1>`. The last B acts on a work register order finding
never measures. The encoded circuit therefore carries only the controlled
target-flip networks of the conjugates, and its phase register has the
unencoded circuit's law exactly. `factor_order_finding(work_columns=B)`
builds it, with the default of None leaving every existing circuit unchanged.

The search is exact over its family. `target_flip_network` minimizes over every
bit ordering, so B and `B P` cost the same for a permutation matrix P. That
leaves 83,328 cosets `B S_5`, each named by the unordered set of its columns.
16 is the inverse of 4 modulo 21, and the synthesis minimizes over reversed
inverse networks, so `s(B^-1 f_16 B) = s(B^-1 f_4 B)` (checked on 1,000
sampled cosets). The ten-round schedule [4, 16, 4, 16, 4, 16, 4, 16, 4, 2]
therefore costs `9 s(4) + s(2)`, 2,556 at B = I.

`scripts/linear_conjugation_search.py` evaluated every coset on five Kaggle
CPU kernels (two of them on T4 hosts' CPUs), in 785 to 1,094 s each.
- **Ten-round optimum.** It is unique: the columns (1, 2, 5, 13, 25) give
  s(4) = 186 and s(2) = 222, for a total of 1,896, 25.8 percent below the
  baseline.
- **Distribution.** Only 2,750 cosets (3.3 percent) beat B = I.
- **Two-round diagnostic.** Its multipliers are 16 and 4, so it ranks cosets
  by s(4) alone, and the same coset leads.

The surrogate ranks candidates; it doesn't admit them.
`linear_conjugation_challenger.py` compiles the eight best cosets of each
problem on FakeFez over transpiler seeds 0 to 7. It applies the affine
challenger's rule on every arm: no seed worse in routed CZ, depth or
duration, and a strictly lower median routed CZ. Before admission, each
encoded circuit passes three checks:
- the conjugation holds exhaustively;
- each controlled network maps `|c, x, 0>` to `|c, g^c(x), 0>` with amplitude
  +1 on both branches;
- a seeded Aer sample of the complete circuit reproduces the baseline's phase
  counts (total variation 0).

All sixteen cosets are admitted.

| Problem | Circuit | Median routed CZ | Median depth | Median duration (dt) |
|---|---|---:|---:|---:|
| ten-round | baseline | 5,422 | 13,662 | 131,793 |
| ten-round | coset 15241, columns (2, 4, 5, 8, 25) | 3,933 | 9,847 | 96,196.5 |
| two-round, both arms | baseline | 1,107 | 2,688 / 2,684 | 25,734 |
| two-round, both arms | coset 15265, columns (2, 4, 5, 10, 17) | 739 | 1,839 / 1,838 | 17,607 |

Coset 15241 cuts the ten-round routed CZ by 27.5 percent; coset 15265 cuts
the two-round CZ by 33.2 percent. Neither is the surrogate optimum:
coset 281 compiles to 3,980.5 and 810 CZ. Its surrogate counts only cubes,
while routing also pays for each cube's control pattern on the heavy-hex
coupling map.

The family stays linear by design. An arbitrary permutation B would reduce
to choosing a relabeling of f's cycle structure, which is a choice made from
the order itself, the compiled-answer construction of Smolin, Smith and Vargo
([1301.7007](../docs/notes/papers/1301.7007.md)). A linear B keeps the work
register a linear re-encoding of the residue bits, and both the search and
the synthesis read the complete truth table, exactly as the unencoded
compiler does. The replay gates and the retained records are listed in
[docs/evidence/linear_conjugation/](../docs/evidence/linear_conjugation/README.md).

## Transfer from the dimension ladder and Rocq corpus

The useful transfer from gororoba-open is structural compilation and proof
reflection. Its sign kernel preserves operand swaps and zero predicates
through recursion. Flattening those predicates prematurely into ANF obscures
sharing, just as flattening a modular permutation into isolated basis swaps
obscures reversible switch structure. Cayley-Dickson nonassociativity remains
an algebraic observable; ordinary circuit matrix composition remains
associative.

The fresh source audit pins gororoba-open at
`127816214c3f96cc1777bd4bd9ba1b286ccc5917`. The source-hash and theorem-assumption
record is `results/hw_estimate/n21_cross_project_proof_audit.json`.

| Dimension surface | Index qubits | Evidence and boundary |
|---|---:|---|
| 4, 8, 16, 32, 64 | 2-6 | Prior fold gate simulation is exhaustive; dimension-generic one-step sign lemmas are closed under the global context. |
| 128, 256, 512, 1024, 2048 | 7-11 | Prior recursive sign/table comparison extends through n=11; that comparison is separate from an end-to-end circuit theorem. |
| 4096 | 12 | Associator first-slot scalar homogeneity is kernel-checkable; alternator counts and ignored GPU tests carry distinct execution scope. |
| 65536 | 16 | The named higher-CD theorem again proves first-slot scalar homogeneity, with standard classical-real axioms. |

At dimension 4096 the derived joint basis-product fold has logical counts
132 CSWAP, 34 phase gates, and 12 CNOT across two 12-qubit index registers.
Those counts supply a synthesis hypothesis; physical native cost, routed
duration, and a circuit theorem require their own evidence.

The audit compiled selected source closures afresh with Rocq 9.1.1 and OCaml
5.4.0 because retained object files require a different OCaml build. The four
`CDSignHalfStep.v` lemmas are dimension-generic recurrence statements. The
Cariow dimension-16 theorem concerns 122 real scalar multiplications, rather
than quantum gate counts. The 4096/65536 theorems in
`C1471_HigherCDTrilinearity.v` prove only the first slot's scalar homogeneity.
`C958_ZDGraphTopology.v` requires theorem-specific assumptions: its graph
component proposition uses a project axiom about hard-coded sizes, whereas
its formula and finite numeric evaluations have separate arithmetic scope.
Each statement transfers a proof technique or mathematical invariant; the
new modular network earns its own finite certificate.

## Replay and remaining admission

From the repository root, use the pinned runtime:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" gororoba_quantum/target_flip.py
"$PYTHON" gororoba_quantum/target_flip_certificate.py --check
"$PYTHON" gororoba_quantum/compile_evidence.py \
  --candidate target_flip_one_clean \
  --out results/hw_estimate/n21_target_flip_compilation.json
"$PYTHON" gororoba_quantum/compile_evidence.py \
  --candidate target_flip_one_clean --phase-bits 5 \
  --out results/hw_estimate/n21_target_flip_precision5.json
"$PYTHON" gororoba_quantum/hybrid_shor.py simulate 21 \
  --phase-bits 5 --shots 4096 --seed 7
"$PYTHON" gororoba_quantum/affine_residual.py
"$PYTHON" gororoba_quantum/affine_residual_challenger.py \
  --out results/hw_estimate/n21_affine_residual_challenger.json
```

The fresh Rocq replay command is in ci/AGENTS.md. The open set consists of
fresh live Target compilation, degraded-edge filtering, a noisy primary lower
bound above the exact uniform decoder null, an identity-null upper bound below
the primary, and dynamic-duration accounting that includes classical latency.
QPU submission then requires a written measurement case, estimated seconds,
and immediate owner approval. Every capture here executes zero QPU jobs.

The foreign-source warning gate has a separate open dependency. A strict
`-w +all` replay on both installed Rocq 9.1.1 and 9.2 rejects Prelude's
transitive `Stdlib.ZArith.ZArith_base` import as deprecated. The retained
selected-source compilation and kernel checks used default diagnostic
severity; their proof terms remain checked, while the all-warning gate stays
open. `scripts/open_gororoba_proof_audit.sh` reproduces the strict failure
with a checked 16-source hash manifest. Repairing that installed Stdlib
dependency belongs to the toolchain owner. The new modular certificate uses
an arithmetic-only import closure and passes the strict Rocq 9.2 gate.
