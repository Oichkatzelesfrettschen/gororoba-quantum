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
no degree ([math-9802116.md](math-9802116.md)). Ren and Zhao's closed form
of the sign table ([2205.07986.md](papers/2205.07986.md)) and Morier-Genoud
and Ovsienko's cubic twisted group algebras, which exclude the
Cayley-Dickson series ([1003.0429.md](papers/1003.0429.md)), state none
either. The proofs below are this
note's (new proof or formalization). They are written proofs;
scripts/cd_phase_degree.py checks every identity they use, cell by cell
against cd_sign, and both statements on every pair through n = 8 (gates
listed under Replay). Rocq proves Theorems 1 to 3, Proposition 4 and
the census below for every n ([sign-row ANF bundle](../evidence/cd-sign-row-anf/README.md),
[associator-phase ANF bundle](../evidence/cd-associator-anf/README.md),
[census bundle](../evidence/cd-associator-census/README.md)).

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

## Leading coefficients, right rows and the bilinear layer

**Theorem 3 (leading layer).** For n >= 3 and m != 0, the ANF of f_m has
no degree-n term, and its degree-(n-1) layer is

    [f_m]_(n-1)(x) = sum_j m_j prod_(l != j) x_l,

so the coefficient of the monomial that omits x_j is the index bit m_j.

*Proof.* Write m = (m', mu) and x = (y, xi) as in the proof of Theorem 1,
whose cases combine into f_m = f_{m'}(y) + xi (N(m') + delta_0 + delta_{m'})
+ mu (N(y) + xi). By Theorem 1 at level n - 1 (or f_0 = 0), f_{m'} has
degree at most n - 2 and no xi. Lemma B's coefficient formula puts
[supp p within S] on y^S in delta_p. The full monomial y^all xi would need
the full y-coefficient of delta_0 + delta_{m'}, which is 1 + 1 = 0. The
monomial y^all omits xi = x_(n-1) and gets coefficient mu = m_(n-1) from
N(y) = 1 + delta_0 alone. The monomial xi y^(all - j) gets the coefficient
of y^(all - j) in delta_0 + delta_{m'}, which is 1 + [m'_j = 0] = m_j; the
constant N(m') and the mu xi term have degree below n - 1 because n >= 3.

Modulo functions of degree at most n - 2 the leading layers add as the
indices do, [f_i] + [f_j] = [f_(i^j)]. In g_ij the translate
f_i(j ^ x) keeps f_i's leading layer, so the three sign rows cancel there
and deg g_ij <= n - 2, the upper bound that Theorem 2 sharpens to an exact
value. Theorem 3 at k = 2 fails: the quaternion rows are affine and their
linear coefficients follow a different map. `sign_row_leading` in
[CdSignRowAnf.v](../../proofs/CdSignRowAnf.v) proves Theorem 3 for every
n >= 3, and `sign_row_top` the absent degree-n term for n >= 2, on ANF
coefficients defined as the Moebius transform (`anf_coef`), which
`anf_inversion` and `anf_unique` identify with the ANF.

**Lemma E (right involution).** phi_n(a, m) + phi_n(a^m, m) = N(m) for every
a, m.

*Proof.* Lemma 1 turns phi(a, m) into phi(m, a) + C(m, a) and phi(a^m, m)
into phi(m, a^m) + C(m, a^m). Lemma A gives phi(m, a) + phi(m, a^m) = N(m),
and C(m, a) + C(m, a^m) = (N(m) + delta_0(a) + delta_m(a)) + (N(m) +
delta_m(a) + delta_0(a)) = 0.

So (e_x e_m) e_m = -e_x for m != 0. Pairing a with a ^ m in the Walsh sum
of s_m(a) = (-1)^phi(a, m) cancels every term at z with m . z = 0, so
those coefficients vanish and R_{e_m} = X^m diag(s_m) expands only over
Pauli words X^m Z^z with m . z odd.

**Proposition 4 (right rows).** For n >= 1 and m != 0 the right sign row
h_m = phi_n(., m) has degree 1 when m is a power of two and
max(1, bitlen(m) - 2) otherwise, independent of n.

*Proof.* Induction on n; at n = 1, h_1 = y has degree 1. (R) with the
variable x = (y, xi) in the first argument and m = (m', mu) reads
h_m(y, xi) = phi'^(mu)(y, m') + xi (N(m') + mu), which splits into three
slices:

- mu = 0, m = m' != 0: h_m(y, xi) = h'_m(y) + xi. The term xi adds only the
  monomial x_(n-1), of degree 1, so deg h_m = deg h'_m >= 1, the degree at
  level n - 1.
- m = 2^(n-1): phi'(0, y) = 0 by Lemma 0, so h_m = xi, of degree 1.
- mu = 1, m' != 0: h_m(y, xi) = f'_(m')(y), the left sign row of e_(m') at
  level n - 1, independent of xi. Theorem 1 gives degree n - 2 for n >= 3,
  and at n = 2 the row f'_1 = y has degree 1.

In the last two slices bitlen(m) = n, so the degree is 1 at the power of two
and max(1, n - 2) = max(1, bitlen(m) - 2) otherwise; the first slice carries
that value up unchanged from level bitlen(m). `right_row_degree` in
[CdSignRowAnf.v](../../proofs/CdSignRowAnf.v) proves the proposition for
every n through the same three slices.

**Bilinear layer (Albuquerque-Majid, p. 19).** The paper states without
proof that the cochain of every algebra in the family has the bilinear part
sum_(i <= j) x_i y_j. For f = f_AM(x, y) = phi_n(y, x) on the 2n variables
of (x, y), with paper index i on bit i - 1: the ANF of f has no constant or
linear term, and its degree-2 layer is sum_(i <= j) x_i y_j.

*Proof.* Induction over Corollary 4.3, starting from f = xy. A monomial of
degree at least 3 in (x, y) has two distinct x-variables or two distinct
y-variables, so its restriction to y = x has degree at least 2; f(x, x)
therefore has linear layer sum_i x_i from the diagonal terms x_i y_i and no
constant. In f'((x, x'), (y, y')) = f(x, y)(1 + x') + f(y, x) x' + y' f(x, x)
+ x' y', the degree-2 layer is [f(x, y)]_2 + x' [f(x, y) + f(y, x)]_1 +
y' sum_i x_i + x' y'. The middle term vanishes by induction, and the last
two add exactly the pairs (i, new) with i <= new. No term is constant or
linear.

## Formalization statement

[CdSignRowAnf.v](../../proofs/CdSignRowAnf.v) proves the sign-row
statement in this repository's terms: `sign_row_degree_all` gives degree
max(1, n - 1) for every n against the tower sign sigma, which the
[tower basis-sign bundle](../evidence/cd-tower-basis-sign/README.md) ties to
cd_sign through dim 64 and the
[cd_sign Python-semantics bundle](../evidence/cd-sign-python-semantics/README.md)
for every n, by running cd_sign's syntax tree. [CdAssociatorAnf.v](../../proofs/CdAssociatorAnf.v) proves the
associator statement on the same terms: `assoc_degree_is` gives degree
max(1, Nat.log2 (max p q) - 1) for every k >= 3 and distinct nonzero p, q,
following Lemmas A to D and the induction above; `assoc_sigma` equates the
phase with the four cd_sign factors of predict.associator_phase, and
`assoc_basis` with e_p (e_q e_x) = (-1)^g(x) (e_p e_q) e_x.
[CdAssociatorCensus.v](../../proofs/CdAssociatorCensus.v) proves the
census: with `anf_degree` the largest weight carrying a nonzero ANF
coefficient, `census_degree_one` and `census_degree` count 21 pairs of
degree 1 and 3 2^d (2^(d+1) - 1) of degree d for 2 <= d <= k - 2,
`census_degree_none` excludes every other degree, and `census_total` sums
the counts to C(2^k - 1, 2).

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
- the census;
- Theorem 3's leading layer on every m;
- Lemma E and the Walsh coefficients it forces to zero;
- the three right-row slices of Proposition 4 and its degree on every m;
- the bilinear layer of the 2n-variable cochain;
- Ren and Zhao's Theorem 1 closed form against the table, and its transpose as the control.

It runs in about 2 s. `--mutate high-low-unconditional` and `--mutate
high-high-no-early-return` each replace one cd_sign branch, and the run
exits 0 only when a check catches the change. gororoba_quantum/verify.py
keeps its pure-Python degree checks at dims 8 to 128.
[CdTowerBasisSign.v](../../proofs/CdTowerBasisSign.v) proves Lemma 1 as
`am_altercommutative`, Lemma A as `am_left_involution` and Lemma E as
`sigma_right_involution`, in the paper's argument order, for every n, and
[CdSignRowAnf.v](../../proofs/CdSignRowAnf.v) proves Theorem 1, Theorem 3
and Proposition 4, and [CdAssociatorCensus.v](../../proofs/CdAssociatorCensus.v)
the table's last two columns for every n.

| n | dim | sign-row degree | new unordered pairs | their degree |
| --- | --- | --- | --- | --- |
| 3 | 8 | 2 | 18 | 1 |
| 4 | 16 | 3 | 84 | 2 |
| 5 | 32 | 4 | 360 | 3 |
| 6 | 64 | 5 | 1488 | 4 |
| 7 | 128 | 6 | 6048 | 5 |
| 8 | 256 | 7 | 24384 | 6 |
