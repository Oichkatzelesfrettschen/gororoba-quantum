# Factoring and the Cayley-Dickson ladder

Cayley-Dickson structure does not carry Shor's algorithm for RSA-2048 on these
devices, and no folding of zero-divisor chunks changes that. Two independent
reasons:

- The reference construction (Gidney 2025) needs 5,755 times the hardware's
  physical qubit count and about seven orders of magnitude more gate volume than
  these devices run, before any error-correction overhead. It is the cost of
  one construction, not a proven lower bound, and its author sees no route to
  another order of magnitude in qubits.
- No product of basis left multiplications is a nontrivial modular multiplier,
  at any dimension: every product is a signed XOR translation, and a
  multiplier x -> a x mod N fixes 0, which a nontrivial translation never does.
  The products also form a 2-group of exponent 4, while order finding needs
  ord_N(a), which for a random base modulo an RSA semiprime is on the scale of
  N; the at most 16 bases with ord_N(a) <= 4 are a fraction about 2^-2044 of
  the units.

Cayley-Dickson dimension 2048 = 2^11 is an 11-qubit index register; RSA-2048 is
a 2048-bit modulus. The numbers coincide and the scales do not.

The algebra connects to the hidden-subgroup family over F_2^n, where design C
at dim 8 already is Bernstein-Vazirani, and to certified non-Clifford benchmarks of the
gate class that dominates factoring cost. The checks behind each claim are
named inline; literature notes live under literature/notes/.

## Reference baseline

Gidney 2025 (arXiv:2505.15917, note literature/notes/2505.15917.md) is the
reference construction. It proves no lower bound; its costs are those of one
construction. At n = 2048 with 0.1% uniform gate error, a 1 us surface-code
cycle and a 10 us reaction time, it needs:

| quantity | RSA-2048 (Gidney 2025, Table 5, Sec. 3.2) | one Heron r2 backend |
|---|---|---|
| logical qubits | 1399 (1280 of them the exponent register) | none; no error correction |
| physical qubits | 897,864 | 156 |
| Toffoli gates | 6.5e9 per factoring, about 7.1e8 per shot | -- |
| two-qubit gate error | 1e-3 assumed | median CZ 1.9e-3 to 2.7e-3 (live_run.py, 2026-10-10) |
| runtime | 12.07 h per shot, 4.96 days expected | -- |

The circuits in this repository give the practical scale. The dim-32 associator
spectrum (96 CZ on 5 qubits, joint ESP 0.77 on the best patch of three backends
in the run of 2026-10-10T16:59:44Z) is already near the noise floor: its noisy
histogram is closer to the true prediction than to the sign-flip prediction by
a TVD margin of only 0.062 (0.181 against 0.243), and its TVD to the noisy
sign-flip control histogram is 0.131. A computation of 7.1e8 Toffolis per shot
is about seven orders of magnitude past that, before any error-correction
overhead.

## What decomposes and what does not

Per the Gidney note:

- **Splits:**
  - the s + 1 Ekera-Hastad shots, which are independent and recombined
    classically;
  - the classical precomputation of the prime set and discrete-log tables;
  - the prime-by-prime serialization of the residue arithmetic;
  - the quantum Fourier transform, which is a semiclassical frequency
    measurement of n - 1 adaptive phase gates and is negligible in cost.
- **Does not split:** the quantum core. All m = 1280 exponent qubits stay
  coherent from the first lookup to the final frequency-basis measurement, about
  4.45 million exponent-addressed lookups per shot, and every saving in the
  construction rests on each multiplier g^(2^k) mod N being a classical
  constant.
- **Splitting the exponent into independent chunks** needs a
  quantum-by-quantum modular multiplication to recombine the partial products,
  and that removes the classical-constant property. The note rates this
  moderate, because the paper does not analyze a split.

## Cayley-Dickson multiplications form an exponent-4 2-group

`verify.check_left_mult_group` pins the following for dims 4 through 64.

**Proved for every n.**
- Every element of G_n = <L_{e_m}> is a signed XOR translation D P_a: each
  L_{e_m} maps |x> to +/-|m XOR x>, and products keep that form.
- Every element has order 1, 2, or 4: (D P_a)^2 = D D^(a) is diagonal and
  squares to the identity. G_n is therefore a 2-group of exponent dividing 4.

**Computed for the listed dimensions, unproved beyond them.**
- The translation part maps G_n onto F_2^n with kernel H, the +/-1 diagonals
  in G_n. Schreier's lemma with transversal {L_{e_a}} generates H by the
  diagonals L_{e_{a^b}}^{-1} L_{e_a} L_{e_b}, the associator phases of design
  C, and H is abelian, so log2 |H| is the F_2 rank of their sign vectors.
- That rank is 1 at n = 2 and 2^(n-1) for n = 3 through 6 (check_left_mult_group;
  the survey's sympy computation extends it to n = 8), with every vector of
  algebraic degree at most n - 2. So |G_n| = 2^(n + 2^(n-1)) at those
  dimensions: 128 for the octonions, 4096 for the sedenions, 2^38 at dim 64, and
  8 (Q8) at n = 2.
- Enumeration of the whole group confirms the order and the exponent through
  dim 16. Schreier's lemma names generators of H; the rank formula for every n
  needs a proof this note does not have.

**Consequence for order finding.**
- Phase estimation on x -> a x mod N needs a unitary of order r = ord_N(a).
- No element of G_n has order beyond 4, at any dimension, 2048 and 4096
  included. This rules out random bases, whose order is on the scale of N;
  the obstruction that holds for every base is the next one.
- A multiplier x -> a x mod N fixes 0, and a signed XOR translation D P_t sends
  |0> to +/-|t>. So the only translation among multipliers is t = 0, which is
  the identity, a = 1. No single element of G_n is a nontrivial multiplier.

**Linear combinations.** "Folding zero-divisor chunks" means a linear
combination of unitaries over G_n. A zero divisor's L_a = L_{e_i} + L_{e_j} is
one such combination with two terms.
- The real span of G_n is every matrix at n = 3, 4, 5, where H's diagonals have
  full real rank 2^n, so there an LCU can represent a modular multiplier in
  principle. The span is smaller elsewhere: G_2 = Q8 spans 4 of the 16
  dimensions of 4 x 4 matrices, and dimensions beyond 32 are unchecked.
- The LCU normalization is provably at least T, the number of distinct
  displacements:
  1. The XOR translations are linearly independent blocks, so writing a
     permutation pi as a combination of G_n elements fixes its translation-t
     part D_t = [x : pi(x) XOR x = t], a 0/1 diagonal.
  2. |sum c_g D_g(x)| <= sum |c_g| bounds the LCU normalization below by
     lambda >= T, the number of distinct displacements pi(x) XOR x.
  3. The post-selection success is ||pi b||^2 / lambda^2 <= 1/T^2.
- Exponential cost needs more than that bound: it needs T = 2^Omega(n) for the
  multiplier family. For small multipliers T is a large fraction of 2^n -- 8 of
  16 for 2x mod 15, 7 for 7x mod 15, 16 of 32 for 2x mod 21, 30 of 64 for 2x
  mod 35 -- and if that fraction persists the route costs about 2^(n-1)
  amplitude-amplification rounds at n bits. The persistence is an inference
  from these four moduli; nothing here proves it.

## What the algebra does connect to

**Bernstein-Vazirani over F_2^3.**
- The octonion associator phase is the linear character (-1)^(n_ij . x) of the
  Fano-line normal n_ij.
- H^3 W H^3 |0> therefore returns n_ij deterministically. That is design C at
  dim 8, and for pair (1,4) it returns n = 2. It is Bernstein-Vazirani: one
  oracle query recovers the hidden string, where design A reads one bit of the
  same character.
- Shor's order finding hides the period r of x -> a^x mod N in the exponent
  domain, the integers, approximated by a power-of-two cyclic register; r need
  not divide N. Simon's and Bernstein-Vazirani's problems hide subgroups of
  F_2^n instead. Cayley-Dickson signs live natively in the F_2^n family.

**Hidden quadratic and cubic forms.**
- Design C's Walsh spectrum of omega_ij reads out the phase function. At degree
  2 the distribution is flat on an affine subspace of size 2^rank, where rank is
  that of the quadratic form's symplectic matrix: 4 outcomes for dim 16 pair
  (1,8). The degree-3 and degree-4 exemplars give non-flat distributions.
- The pair (1, 2^(n-1)) has zero-frequency weight (1 - 2^(3-n))^2, checked for
  n = 3 through 7. That gives a closed-form target for every rung of the ladder.

**A certified Toffoli-class benchmark.**
- Toffoli and CCZ gates make up the 6.5e9-gate core of RSA-2048. A degree-3
  phase with pi coefficients is CCZ-class.
- The associator phase has degree max(1, bitlen(max(i,j)) - 2), so the ladder
  supplies phase circuits of chosen non-Clifford degree with exact answers and
  sign-flip and omitted-block controls:

  | dim | phase degree | CZ (FakeFez target) |
  |---|---|---|
  | 8 | 1 | 18 |
  | 16 | 2 | about 50 |
  | 32 | 3 | about 96 |
  | 64 | 4 | 200 to 239 |

  The CZ column is for pair (1, 2^(n-1)).
- Measuring TVD against degree at matched CZ count separates degree-driven error
  from gate-count-driven error. The falsifier: if fidelity tracks CZ count alone,
  algebraic degree carries no information beyond circuit size.
- `live_run.py` already compiles the dims 8 to 32 rungs onto the best calibrated
  patch of the three backends.

**The folded QFT on dynamic circuits.**
- Gidney's QFT is semiclassical: n - 1 adaptively phased gates driven by
  mid-circuit measurement.
- The smallest honest test on Heron is order finding for a = 2 mod 15. Its
  multiplier, a cyclic rotation of the four work bits, is the exact permutation
  on every input rather than a circuit compiled from the known answer (Smolin,
  Smith, and Vargo, Nature 499, 163 (2013)).
- `order_finding.py` implements it with one recycled control qubit, controlled
  rotations by 2 and by 1 built from five Fredkin gates, and one feed-forward
  phase -pi/2 conditioned on the first outcome.
- The input is an eigenstate |u_s> = (1/2) sum_k exp(-2 pi i s k/4) |2^k> of the
  multiplier, prepared as a phased W state. That makes the two-bit readout
  deterministic, equal to s. The textbook |1> input instead reads the four
  phases uniformly, which a decohered device also produces.
- The four eigenstates run identical-cost circuits with distinct outcomes, so
  each controls the others. The identity multiplier is the null and reads 0.
- `$PYTHON order_finding.py` checks the multiplier on residues 1..14, the
  eigenvalues i^s, and the readout exactly. The generic controlled synthesis of
  the rotation costs 248 CZ on the FakeFez target; the Fredkin form costs 67.
- The live dry run of 2026-10-10T17:23:16Z placed the group on ibm_kingston at
  67 CZ. The noise model reads the correct phase with probability 0.91 for each
  s and the null at 0.957. The duration estimate (record field duration_s)
  excludes the classical feed-forward latency, which the Target does not report.
- This tests the dynamic-circuit machinery the factoring QFT needs. It
  demonstrates no factoring capability, since multiplication by 2 mod 15 is a
  known easy case. Monz et al. (Science 351, 1068 (2016)) ran the
  recycled-control form on trapped ions.

## What open_gororoba supplies

A survey of open_gororoba at fe668020 (literature/notes/open_gororoba_survey.md,
with derivations and replay scripts in open_gororoba_survey_deep_notes.md)
separates proven, tested, and asserted content.

**Re-checked here:**
- *The sign recursion as a circuit.* Over GF(2), cd_basis_mul_sign_iter
  unrolls to f_{n+1}(a, b, p', q') = f_n(swap_b(p', q')) + a(1 + b) + a[q' = 0],
  with a and b the top bits of p and q. It agrees with cd_sign on every (p, q)
  through dim 256.
  - The survey turns it into a circuit for the multiplexed product
    sum_p |p><p| (x) L_{e_p}: n(n-1) controlled swaps, 3n - 2 multi-controlled
    Z gates, and n CNOTs. It simulated that circuit at gate level through n = 6.
  - That is polynomial in n, where the DiagonalGate compile of one L_{e_m}
    grows as about 2^n.
  - At the 3 to 6 qubits these devices run, the controlled swaps cost more than
    the diagonal, so the crossover lies beyond this hardware.
  - The multiplexed product is still a family of signed XOR translations, so
    the modular-multiplier obstruction above applies to it unchanged.
- *Defect count.* The ordered basis triples with nonzero associator number
  v(N) = N^3/2 - 14N + 24: 168, 1848, 15960, and 130200 at N = 8, 16, 32, 64,
  checked here by brute force.
  - The survey matches the repository's zero-divisor edge totals at dims 16 to
    256 (84 to 523,404) to E(D) = v(D/2)/2.
  - Its predictions for dims 512 to 4096 (4,192,524 up to 2,147,469,324)
    assume the identity continues; nothing proves that.

**From the survey, not re-run here:**
- *Rocq.* 313 .v files, with no Admitted and no admit. CDSignHalfStep.v holds
  the only dimension-generic sign lemmas.
- *Fast factorization.* The only Rocq-proven one is Cariow 2013 at dim 16:
  Walsh-Hadamard diagonalization plus a 106-term sparse correction, 122
  multiplications. The dim-32 and dim-64 counts are unachieved targets.
- *"512/1024/2048" files.* The Rocq files with those numbers in their names, in
  curated/, model thread capacity and carry no Cayley-Dickson content.
- *Quantum content.* The repository's quantum material is an MPS simulator, a
  Grover search, and hardware profiles. It has no QFT, no modular arithmetic,
  and no Shor; its box-kite QEC, p-adic CD crypto, and sedenion braid compiler
  modules are stubs or analogies.
- *The group order.* The survey's independent sympy computation gives
  2^(n + 2^(n-1)) for n = 3 through 8, matching check_left_mult_group.
