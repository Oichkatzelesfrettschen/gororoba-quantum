# Quantum linear algebra and the A5 fiber computations

Status: workload and falsification scope reconciled on 2026-11-11. Here A5 is the 32-dimensional
Cayley-Dickson algebra. The original 2026-11-05 survey remains in Git history; its statements that no future
fault-tolerant machine could help, that singularity excludes every QSVT use, and that a Pauli decomposition
sets a universal encoding cost were stronger than its evidence. The current conclusion is narrower:
**the audited proposals and retained experiments establish no end-to-end quantum speedup for these exact
modular fiber computations.** This is a statement about the supplied reductions, costs and records.

Companion records are the [finite-field proposal and its falsification](finite-field-qlsa-alternatives.md),
[corrected HHL/QSVT interpretation](../../evidence/hhl-qsvt-falsify/README.md), and
[executable exact counterexamples and filters](../../evidence/a5-quantum-contracts/README.md).

## What a speedup claim must specify

The problem includes its field, representation, access model, promise, output and error criterion. An explicit
matrix, an entry oracle, a reversible matrix-vector oracle and a block encoding have different costs. A quantum
state proportional to a complex solution, a classical modular kernel basis, a rank, an ideal-membership bit and
a certificate are different outputs. A useful comparison includes preprocessing, coherent access, arithmetic,
preparation, repetitions, verification and readout under comparable assumptions. Wall time on a classical
statevector simulator is not a quantum running-time measurement.

| Result or mechanism | What the result establishes | Boundary for the fiber workload |
| --- | --- | --- |
| [Buhrman and Spalek, quant-ph/0409035](https://arxiv.org/abs/quant-ph/0409035) | Bounded-error matrix-product verification over any field in O(n^(5/3)) worst-case time in its access/cost model, against classical quadratic verification | A counterexample to a blanket claim that finite-field linear algebra has no quantum speedups. It verifies a proposed product; it does not construct the quotient, rank or standard basis needed here. Coherent access remains part of an implementation |
| [Childs, Hung and Li, 2102.11349](https://arxiv.org/abs/2102.11349) | No asymptotic query advantage for several rank, determinant and solve tasks in the stated matrix-vector oracle model; exponential advantages for some other matrix properties | A model-specific lower bound, not a lower bound for every representation, structured promise or gate algorithm |
| [Wocjan, Jordan, Ahmadi and Brennan, 0908.0022](../papers/0908.0022.md) | Additive basis representations and ideal operations, including membership, for finite black-box rings in time polynomial in log of ring size | Finite black-box rings differ from a polynomial ideal supplied by generators. The algorithm presupposes ring access; the cost of constructing the finite quotient and its arithmetic cannot disappear from the fiber comparison. The paper describes classical hardness as apparent, not an unconditional separation for every explicit finite algebra |
| [Gilyen, Su, Low and Wiebe, 1806.01838](https://arxiv.org/abs/1806.01838) | Singular-value transformations, including thresholded pseudoinverses and spectral filtering under block-encoding and spectral promises | Singularity prevents ordinary inversion; it does not prevent these operations. Exact modular rank requires an additional valid reduction |
| Reversible finite-field elimination | Exact finite-field arithmetic can be embedded in a quantum circuit | Reversibility alone does not reduce the arithmetic count or establish a speedup |
| Quantum polynomial-system solvers and Grover-style search | Particular solution-finding or search tasks under their specified promises | A solution point does not recover the nilpotents, relations, ideal powers or Hilbert function of a local quotient |

The earlier bibliography remains in [paper notes](../papers/) and [SOURCES.json](../../SOURCES.json).
The table does not claim an exhaustive negative literature theorem.

## The current algebraic task

For a local chart with ideal J and generators G of I, the finite jet algebra is

```
R_N = F_p[t] / (J + m^N).
```

It is an associative commutative quotient algebra used to study the Cayley-Dickson geometry; it is not A5 itself.
The truncation is zero-dimensional and supported at the origin. It can still have a large vector-space dimension
and nontrivial nilpotents. For example, the retained [W8 N=16 run](../../evidence/a5-exceptional-fibers/w8-n16-azure/README.md)
has quotient dimension 93,024. Its geometric support is one point. Sampling that point supplies none of the
multiplication or ideal-power information represented by those 93,024 coordinates.

For an explicitly represented finite F_p-algebra of dimension D, log2(|R|) = D log2(p).
Thus a bound polynomial in log(|R|) is polynomial in D, not automatically polylogarithmic in the coordinate
count. Building reduction rules or multiplication oracles remains chargeable. Once explicit multiplication is
available, classical linear closure is already a polynomial-time baseline for finite-algebra ideal membership.
None of this proves that every structured quantum route must fail.

| Fiber question | Current retained status | Remaining computational meaning |
| --- | --- | --- |
| E8 degree five | h5 = 952 at p=32009 and p=32029, with the N=18 certificates in the [claim ledger](../../evidence/a5-exceptional-fibers/ledger.tsv) | Positive control for a successor algorithm; no longer an open degree-five target |
| Iso, W8 and E8-to-VB full fiber equality | Established at both retained primes in the ledger | Characteristic-zero transfer is separate; finite-prime completion does not imply it automatically |
| E8 degree six | 1526 <= h6 <= 1666 (A5-251) | The unresolved quotient has 140 target directions; deciding them can improve or close the bound |
| Kernel-plane limits along arcs | Exact small left-action and Laurent-series calculations | A 32 by 32 operator experiment does not replace the large fiber calculation |

### Restrict the target space and preserve the full ideal closure

Write K2 for the retained quadratic relation ideal in S=F_p[y], and L for the full fiber relation ideal.
The established inclusions are K2 subset L subset radical(K2). Define

```
T_d = (radical(K2) / K2)_d,
phi_d : T_d -> I^d / m I^d,  f -> f(G).
```

The exact identity is

```
h_d = dim (S/radical(K2))_d + rank(phi_d).
```

In degree five, the two dimensions are 861 and 91; in degree six they are 1526 and 140.
The finite-jet version phi_(d,N) satisfies rank(phi_(d,N)) <= rank(phi_d), so it yields a lower bound.
The target forms are a basis of T_d. The denominator must still be the entire image of m I^d in R_N,
constructed from every ideal generator and the full maximal-ideal basis. Restricting the denominator to those
91 or 140 targets changes the quotient and can invent independence.

A lower bound equal to the K2 upper bound certifies h_d. A zero image at finite N, or a plateau over several
N values, does not certify exact membership in the untruncated local ideal. Adding 861 or 1526 to the full
truncated fiber rank r_N would also double count; the additive term belongs only beside the restricted target rank.
The implementation and measured bounds belong with the existing
[monomial-ladder work](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/5a8b151c5edeafbd9e6f17fa38610ed5467497b3/docs/evidence/a5-exceptional-fibers/monomial-ladder/README.md), developed in
[PR 818](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/818).

## The inexpensive operator constructions that survive

For nonzero real rational a = sum_i a_i e_i, each U_i = L_ei is an exactly checkable signed permutation. Therefore

```
L_a = sum_i a_i U_i,    alpha = sum_i |a_i|,
1 <= alpha / ||L_a||_2 <= sqrt(s),    s = |support(a)|.
```

The upper bound follows from L_a e0 = a and Cauchy-Schwarz; the lower bound follows from the triangle
inequality for the unitary summands. The natural LCU has at most 32 terms and five selector qubits in A5,
and two terms need one selector qubit. These are algebraic resource counts; PREP, SELECT, precision,
workspace and target compilation still need an implementation budget.

For a=e1+/-e10 and a=e25+/-e8, B=L_a^T L_a has spectrum supported on {0,2,4}. The exact projector

```
P_ker = (B - 2I)(B - 4I) / 8
```

satisfies P^T=P, P^2=P and L_a P=0, and equals identity on ker(L_a). The
[successor replay](../../evidence/a5-quantum-contracts/README.md) certifies complete projectors rather than
checking only selected dark vectors. It also rejects omitted or incorrect spectral roots. A polynomial
identity for these witnesses is not a universal spectrum theorem for all A5 elements or a compiled QSVT circuit.

Over an odd field every pure left action is skew-symmetric, so v^T L_a v is identically zero even when L_a is
invertible. The proposed scalar kernel predicate therefore fails before any resource estimate matters. A
correct predicate L_a v=0 combined with uniform search has the p^(rank/2) search scale; that scale concerns this
algorithm. Conversely, the rational rank of an integer lift can exceed its modular rank, as the exact determinant
-p witnesses in the successor record show.

In characteristic two, reducing signs erases the sign distinction used by these particular probes. Equal ranks
in a selected list of examples do not establish equal kernels, nor do they show that every possible F2
experiment is uninformative. A different field is a different algebraic problem and needs a separate mutation test.

## What the photonic slice establishes

The retained Ascella kernel slice uses a=e1+e10 and inputs e4+/-e15. Its selected outputs are e5,e6,e13,e14;
all coordinates lie in the embedded A4. The exact A4 and A5 restrictions agree. The
[scope and event-accounting replay](../../evidence/a5-photonic-crosschecks/README.md) checks every selected
input column against the declared operator, binds the retained optical requests, and distinguishes eligible
branch probability from success per returned event. A check of only the prepared first column cannot establish
correctness of a fixed operator on the whole two-dimensional input space.

This experiment tests the programmed kernel/bright contrast and a sign mutation on that slice. It establishes
neither full A5 nullity, an A5-specific discriminator, physical nonassociativity nor a computational speedup.
Its classical construction already computes the selected action and expected probabilities. Provider runtime
and simulator runtime are acquisition facts, not a complete comparison against exact classical algebra.
