# Factoring and the Cayley-Dickson ladder

Cayley-Dickson structure does not carry Shor's algorithm for RSA-2048 on these
devices, and no folding of zero-divisor chunks changes that. Two independent
reasons:

- The resource floor is 5,755 times the hardware's physical qubit count and
  about seven orders of magnitude above the gate volume these devices run, before
  any error-correction overhead.
- Products of basis left multiplications form a 2-group of exponent 4, while
  order finding needs an operator of order ord_N(a), which is on the scale of N
  for an RSA modulus.

The algebra connects to the hidden-subgroup family over F_2^n, where design C
at dim 8 already is Bernstein-Vazirani, and to certified non-Clifford benchmarks of the
gate class that dominates factoring cost. The checks behind each claim are
named inline; literature notes live under literature/notes/.

## Resource floor

Gidney 2025 (arXiv:2505.15917, note literature/notes/2505.15917.md) is the
reference construction. At n = 2048 with 0.1% uniform gate error, a 1 us
surface-code cycle and a 10 us reaction time, it needs:

| quantity | RSA-2048 (Gidney 2025, Table 5, Sec. 3.2) | one Heron r2 backend |
|---|---|---|
| logical qubits | 1399 (1280 of them the exponent register) | none; no error correction |
| physical qubits | 897,864 | 156 |
| Toffoli gates | 6.5e9 per factoring, about 7.1e8 per shot | -- |
| two-qubit gate error | 1e-3 assumed | median CZ 1.9e-3 to 2.7e-3 (live_run.py, 2026-10-10) |
| runtime | 12.07 h per shot, 4.96 days expected | -- |

The circuits in this repository give the practical scale. The dim-32 associator
spectrum (96 CZ on 5 qubits, joint ESP 0.77 on the best patch of three
backends) is already near the noise floor: its noisy histogram separates from
the sign-flip control by 0.062 TVD (design C). A computation of 7.1e8 Toffolis per shot is about seven orders of magnitude
past that, before any error-correction overhead.

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

**Statement.**
- G_n = <L_{e_m}> at dim 2^n has order 2^(n + 2^(n-1)) for n >= 3 (128 for the
  octonions, 4096 for the sedenions, 2^38 at dim 64), and 8 (Q8) at n = 2.
- Every element has order 1, 2, or 4.

**Proof.**
1. Every L_{e_m} maps |x> to +/-|m XOR x>. Products keep that form, so every
   g in G_n is a signed XOR translation D P_a.
2. The translation part maps G_n onto F_2^n with kernel H, the +/-1 diagonals
   in G_n.
3. Schreier's lemma with transversal {L_{e_a}} generates H by the diagonals
   L_{e_{a^b}}^{-1} L_{e_a} L_{e_b}. These are the associator phases of design
   C. H is abelian, so log2 |H| is the F_2 rank of their sign vectors: 1 at
   n = 2 and 2^(n-1) from n = 3, each vector of algebraic degree at most n - 2.
4. (D P_a)^2 = D D^(a) is diagonal and squares to the identity, so g^4 = 1.
5. Enumeration of the whole group confirms the order and the exponent through
   dim 16.

**Consequence for order finding.**
- Phase estimation on x -> a x mod N needs a unitary of order r = ord_N(a).
- No element of G_n has order beyond 4, at any dimension, 2048 and 4096
  included.
- A multiplier x -> a x mod N fixes 0, and a signed XOR translation D P_t sends
  |0> to +/-|t>. So the only translation among multipliers is t = 0, which is
  the identity, a = 1. No single element of G_n is a nontrivial multiplier.

**Linear combinations.** "Folding zero-divisor chunks" means a linear
combination of unitaries over G_n. A zero divisor's L_a = L_{e_i} + L_{e_j} is
one such combination with two terms.
- The real span of G_n is every matrix: H's diagonals have full real rank 2^n at
  n = 3, 4, 5. So an LCU can represent a modular multiplier in principle.
- The cost is exponential, and provably so:
  1. The XOR translations are linearly independent blocks, so writing a
     permutation pi as a combination of G_n elements fixes its translation-t
     part D_t = [x : pi(x) XOR x = t], a 0/1 diagonal.
  2. |sum c_g D_g(x)| <= sum |c_g| bounds the LCU normalization below by
     lambda >= T, the number of distinct displacements pi(x) XOR x.
  3. The post-selection success is ||pi b||^2 / lambda^2 <= 1/T^2.
- For small multipliers T is a large fraction of 2^n: 8 of 16 for 2x mod 15, 7
  for 7x mod 15, 16 of 32 for 2x mod 21, 30 of 64 for 2x mod 35. If that
  fraction persists, the route costs 2^(n-1) amplitude-amplification rounds at
  n bits, which is exponential. The persistence is an inference from these four
  moduli and has no proof here.

## What the algebra does connect to

**Bernstein-Vazirani over F_2^3.**
- The octonion associator phase is the linear character (-1)^(n_ij . x) of the
  Fano-line normal n_ij.
- H^3 W H^3 |0> therefore returns n_ij deterministically. That is design C at
  dim 8, and for pair (1,4) it returns n = 2. It is Bernstein-Vazirani: one
  oracle query recovers the hidden string, where design A reads one bit of the
  same character.
- Shor's algorithm is the abelian hidden-subgroup algorithm over Z_N, and
  Simon's and Bernstein-Vazirani's are its F_2^n relatives. Cayley-Dickson
  signs live natively in the F_2^n family.

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
