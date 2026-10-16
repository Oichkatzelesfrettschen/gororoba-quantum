# Algebraic degree of Cayley-Dickson sign rows and associator phases

## Result

Let A_n be the Cayley-Dickson algebra of dimension 2^n with basis products
e_a e_b = psi_n(a, b) e_{a^b}, psi_n = cd_sign(2^n, ., .) from
gororoba_quantum/cd_core.py, and phi_n(a, b) = [psi_n(a, b) = -1] in F_2.
Degrees are algebraic (ANF) degrees of Boolean functions on F_2^n, and
bitlen(m) is the bit length of m (bitlen(0) = 0).

**Theorem 1 (sign rows).** For n >= 2 and every m != 0 the sign row
f_m = phi_n(m, .) of L_{e_m} has degree exactly n - 1.

**Theorem 2 (associator phases).** Let

    g_ij(x) = phi_n(j, x) + phi_n(i, j^x) + phi_n(i^j, x) + phi_n(i, j),

so that W_ij = L_{e_i e_j}^dagger L_{e_i} L_{e_j} = diag((-1)^(g_ij(x)))
(predict.associator_phase). For n >= 3 and distinct nonzero i, j < 2^n,

    deg g_ij = max(1, bitlen(max(i, j)) - 2),

independent of n: the degree is fixed at the doubling level where the pair
first appears. In A_2 (the quaternions) every g_ij vanishes. The pairs with
bitlen(max(i, j)) = b >= 3 number 3 2^(b-2) (2^(b-1) - 1) unordered pairs,
so the census of unordered pairs by degree adds 84, 360, 1488, 6048 and
24384 pairs of degree 2 to 6 at dims 16 to 256, above the 21 pairs of degree
1 at dim 8 (3 quaternion pairs and 18 new ones).

Consequences already recorded in gororoba_quantum/DESIGN_NOTES.md: octonion
left multiplications are Clifford, sedenion ones carry a cubic sign, and W
leaves the Clifford group from dim 32 on.

Status. Both theorems carried the label "candidate new result" in
[prior_work_synthesis.md](prior_work_synthesis.md): Bales 2016 states no ANF
degree ([1602.02843.md](1602.02843.md)), and Albuquerque-Majid's Corollary
4.3, Proposition 4.2 and Proposition 4.5 state the cochain recursions with
no degree ([math-9802116.md](math-9802116.md)). The proofs below are this
note's (new proof or formalization). They are written proofs;
scripts/cd_phase_degree.py checks every identity they use, cell by cell
against cd_sign, and both statements on every pair through n = 8 (gates
listed under Replay); no proof assistant has checked them.

Upper bound only, as a cross-check: g_ij = s_{i,j} + phi_n(i, j) with
s_{i,j} the Schreier sign vector of
[left_mult_sign_rank.md](left_mult_sign_rank.md), whose Theorem puts every
element of V_n at degree at most n - 2 for n >= 3. Theorem 2 adds that the
bound is attained by every pair with an index in the top half and that a
pair's degree stays fixed as n grows.

## Conventions

Index bit n-1 is the last doubling. Write a = (a', alpha) with a' the low
n-1 bits and alpha bit n-1, likewise i = (i', alpha), j = (j', beta),
k' = i' ^ j', and x = (y, xi). Functions of y live on F_2^(n-1). Let
N(y) = [y != 0], delta_p(y) = [y = p], phi^(0)(a, b) = phi(a, b) and
phi^(1)(a, b) = phi(b, a). Primes on phi and g mean level n - 1:
g' = g^(n-1)_{i'j'}.

From [left_mult_sign_rank.md](left_mult_sign_rank.md):

- **(R)** phi_n((a', alpha), (y, xi)) = phi'^(xi)(a', y) + alpha (N(y) + xi),
  the four branches of the cd_sign loop read at its first iteration.
- **Lemma 0.** phi_n(0, x) = phi_n(x, 0) = 0.
- **Lemma 1.** C_n(c, y) := phi_n(c, y) + phi_n(y, c) = N(c) + delta_0(y) +
  delta_c(y). Substituting y -> c' ^ y gives C(c, c' ^ y) = N(c) +
  delta_{c'}(y) + delta_{c ^ c'}(y).

## Lemmas

**Lemma A (involution).** phi_n(a, x) + phi_n(a, a^x) = N(a) for every a, x.
With x = 0 and Lemma 0, phi_n(a, a) = N(a).

*Proof.* Induction on n; level 0 has only a = x = 0. Apply (R) to both
terms with a ^ x = (a' ^ y, alpha + xi). Write S(y) = phi'(a', y) +
phi'(a', a' ^ y), which equals N(a') by induction, and use Lemma 1 to turn
each phi'(b, a') into phi'(a', b) + C(a', b).

- alpha = 0, xi = 0: the sum is S(y) = N(a') = N(a).
- alpha = 0, xi = 1: phi'(y, a') + phi'(a' ^ y, a') = S(y) + C(a', y) +
  C(a', a' ^ y) = N(a') + (N(a') + delta_0 + delta_{a'}) + (N(a') +
  delta_{a'} + delta_0) = N(a'). Here a = (a', 0), so N(a) = N(a').
- alpha = 1, xi = 0: phi'(a', y) + N(y) + phi'(a' ^ y, a') + N(a' ^ y) + 1
  = S(y) + C(a', a' ^ y) + N(y) + N(a' ^ y) + 1 = N(a') + (N(a') +
  delta_{a'} + delta_0) + (1 + delta_0) + (1 + delta_{a'}) + 1 = 1 = N(a).
- alpha = 1, xi = 1: phi'(y, a') + N(y) + 1 + phi'(a', a' ^ y) + N(a' ^ y)
  = S(y) + C(a', y) + N(y) + N(a' ^ y) + 1, which reduces the same way
  to 1.

**Lemma B (two points).** For k >= 1 and p != q in F_2^k, delta_p + delta_q
has degree exactly k - 1, and N has degree exactly k.

*Proof.* delta_p(y) = prod_t (y_t + p_t + 1), whose ANF coefficient on the
monomial y^S is [supp p within S]. The coefficient on the full monomial is 1
for every p, so deg delta_p = k and deg N = deg(1 + delta_0) = k. In
delta_p + delta_q the full coefficients cancel, and for S the complement of
a bit t where p and q differ the coefficient is [p_t = 0] + [q_t = 0] = 1.
For k >= 2 adding a constant leaves degree k - 1 unchanged.

**Lemma C (degenerate pairs).** g_0j = g_i0 = g_ii = 0, and g_ij(0) = 0 for
every i, j.

*Proof.* Lemma 0 kills g_0j and g_i0 term by term. g_ii = phi(i, x) +
phi(i, i^x) + phi(0, x) + phi(i, i) = N(i) + 0 + N(i) by Lemma A. At x = 0
the second and fourth terms coincide and Lemma 0 kills the others: W fixes
e_0.

**Lemma D (slices).** For n >= 1 and every i, j:

    (D0)  g_ij(y, 0) = g'(y) + beta (C(i', j' ^ y) + C(i', j'))
                             + alpha (N(y) + N(y ^ j') + N(j'))
    (D1)  g_ij(y, 1) + g_ij(y, 0) = N(i') + N(j') + N(k').

*Proof.* (R) at xi = 0 gives the four terms phi'(j', y) + beta N(y);
phi'^(beta)(i', j' ^ y) + alpha (N(j' ^ y) + beta); phi'(k', y) +
(alpha + beta) N(y); and phi'^(beta)(i', j') + alpha (N(j') + beta). The
N(y) coefficients add to beta + alpha + beta = alpha, the two alpha beta
terms cancel, and phi'^(1)(a, b) = phi'(a, b) + C(a, b) turns the two
beta-dependent terms into g' plus beta (C(i', j' ^ y) + C(i', j')).

At xi = 1 each term changes as follows. phi'(j', y) becomes phi'(y, j'),
which adds C(j', y), and beta N(y) gains beta. phi'^(beta)(i', j' ^ y)
becomes phi'^(beta+1), which adds C(i', j' ^ y), and the alpha term gains
alpha. phi'(k', y) becomes phi'(y, k'), which adds C(k', y), and the third
term gains alpha + beta. The constants sum to beta + alpha + alpha + beta
= 0. Lemma 1 gives C(j', y) + C(i', j' ^ y) + C(k', y) = (N(j') + delta_0 +
delta_{j'}) + (N(i') + delta_{j'} + delta_{k'}) + (N(k') + delta_0 +
delta_{k'}), and every delta cancels.

So every phase splits as g_ij(y, xi) = A(y) + c xi with c = N(i') + N(j') +
N(k'), a constant. For distinct nonzero i, j:

- **Lower pair** (alpha = beta = 0). i', j' are distinct and nonzero, so k'
  is nonzero and c = 1, giving **g_ij = g' + xi**.
- **Upper pair** (alpha or beta is 1). Expanding (D0) with Lemma 1 gives
  **A = g' + delta_u + delta_v + const**, with u != v:
  - (alpha, beta) = (0, 1): {u, v} = {j', k'}, distinct because i' != 0
    (i = i' is nonzero);
  - (1, 0): {u, v} = {0, j'}, distinct because j = j' is nonzero;
  - (1, 1): {u, v} = {0, k'}, distinct because i != j forces i' != j'.

  When one of i', j', k' is zero, Lemma C gives g' = 0 and c = 0, and A
  reduces to 1 + delta_0 + delta_p = [y not in {0, p}] for the nonzero p
  among them; the constant is 1 because g_ij(0) = 0.

## Proof of Theorem 1

(R) with a = m = (m', mu) and Lemma 1 give

    f_m(y, xi) = f_{m'}(y) + xi (N(m') + delta_0 + delta_{m'}) + mu (N(y) + xi),

which splits into three cases:

- (a) mu = 0, m' != 0: f_m = f_{m'}(y) + xi (1 + delta_0 + delta_{m'});
- (b) mu = 1, m' != 0: f_m = f_{m'}(y) + N(y) + xi (delta_0 + delta_{m'});
- (c) m = (0, 1): f_m = N(y) + xi.

These are the identities of [math-9802116.md](math-9802116.md) in
cd_core's order of arguments.

**Base n = 2.** f_1 at level 1 is y (e_1 e_1 = -1). Case (a) gives f_1 = y,
case (b) gives f_3 = y + y + xi = xi, and case (c) gives f_2 = y + xi. Each
has degree 1.

**Step n >= 3.** Here k = n - 1 >= 2, and deg f_{m'} = n - 2 by induction.

- (a) By Lemma B, xi (1 + delta_0 + delta_{m'}) has degree 1 + (n - 2). Its
  monomials contain xi and those of f_{m'} do not, so the degree is n - 1.
- (b) N(y) carries the full low monomial y_0 ... y_{n-2}, of degree n - 1.
  f_{m'} has degree n - 2 and the xi term's monomials contain xi, so
  neither cancels it.
- (c) N(y) has degree n - 1 and xi has degree 1.

## Proof of Theorem 2

**n = 2.** No lower pair exists: two distinct nonzero i', j' in F_2^1 is
impossible. For an upper pair, i', j' and k' in F_2^1 cannot all be nonzero,
so c = 0 and Lemma C gives g' = 0. That leaves A = delta_u + delta_v +
const with u != v in F_2^1, which is the constant 1 + const. Lemma C's
g_ij(0) = 0 then sets that constant to zero, so every g_ij vanishes.

**Induction for n >= 3.** The induction runs over the statement for all
pairs at level n - 1, with Lemma C covering the degenerate ones.

- **Lower pair.** g_ij = g' + xi, and xi is a variable absent from g'.
  Hence deg g_ij = max(deg g', 1).
  - At n = 3, g' = 0 and the degree is 1 = max(1, b - 2) for b = bitlen <= 2.
  - At n >= 4, induction gives deg g' = max(1, b - 2) >= 1.
- **Upper pair.** max(i, j) has bitlen n, and A = g' + delta_u + delta_v +
  const with u != v. Lemma B, with k = n - 1, gives delta_u + delta_v
  degree exactly n - 2 >= 1. Nothing else in g = A + c xi cancels its
  monomials of degree n - 2:
  - the constant has degree 0;
  - c xi contains the variable xi, which no y-monomial does;
  - g' either vanishes (degenerate i', j' by Lemma C, or n = 3 by the n = 2
    case) or, at n >= 4, has degree max(1, bitlen(max(i', j')) - 2) <=
    max(1, n - 3) < n - 2.

  Hence deg g_ij = n - 2 = bitlen(max(i, j)) - 2.

At n = 3 the c xi term and the two-point term both have degree 1. The
argument still holds there because xi is a separate variable and g' = 0
(quaternion associativity). From n = 4 on the strict inequality deg g' <
n - 2 does the work.

**Census.** A pair with bitlen(max(i, j)) = b has j in [2^(b-1), 2^b) and
i < j, i != 0, so the count is sum_j (j - 1) = 3 2^(b-2) (2^(b-1) - 1).

## Formalization statement

A Rocq statement for open_gororoba, against its `cd_sign_fuel` (the
function the [Stiefel witness](../evidence/stiefel_witness/README.md) uses)
with fuel at least n, and an ANF degree on `nat -> bool` truth tables of
2^n entries:

    Theorem sign_row_degree : forall n m,
      2 <= n -> 0 < m < 2 ^ n -> anf_degree n (phi n m) = n - 1.

    Theorem associator_phase_degree : forall n i j,
      3 <= n -> 0 < i < 2 ^ n -> 0 < j < 2 ^ n -> i <> j ->
      anf_degree n (assoc_phase n i j) = Nat.max 1 (Nat.log2 (Nat.max i j) - 1).

Nat.log2 m - 1 equals bitlen(m) - 2 for m > 0, with truncated subtraction
giving 0 below bitlen 2. Lemmas A to D are finite identities at each level
and suit `vm_compute` per level. The induction itself needs (R) as a lemma
about `cd_sign_fuel` and the ANF coefficient formula of Lemma B. The
statement is filed upstream as
[open_gororoba issue #217](https://github.com/Oichkatzelesfrettschen/open_gororoba/issues/217).

## Replay

`"$PYTHON" scripts/cd_phase_degree.py --max-n 8` checks, at every level up
to n = 8:

- (R), Lemmas 0, 1, A and C;
- Lemma B for k <= 8;
- cases (a) to (c) cell by cell;
- (D0) and (D1) on all 4^n ordered pairs, degenerate ones included;
- the upper-pair closed form;
- both theorems on every ordered pair;
- the census.

It runs in under a second. `--mutate high-low-unconditional` and `--mutate
high-high-no-early-return` each replace one cd_sign branch, and the run
exits 0 only when a check catches the change. gororoba_quantum/verify.py
keeps its pure-Python degree checks at dims 8 to 128.

| n | dim | sign-row degree | new unordered pairs | their degree |
| --- | --- | --- | --- | --- |
| 3 | 8 | 2 | 18 | 1 |
| 4 | 16 | 3 | 84 | 2 |
| 5 | 32 | 4 | 360 | 3 |
| 6 | 64 | 5 | 1488 | 4 |
| 7 | 128 | 6 | 6048 | 5 |
| 8 | 256 | 7 | 24384 | 6 |
