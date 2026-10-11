# Sign subgroup of the Cayley-Dickson left-multiplication group

## Result

Let A_n be the Cayley-Dickson algebra of dimension 2^n with basis e_0 ..
e_{2^n - 1} and products e_a e_b = psi_n(a, b) e_{a^b}, psi_n = cd_sign(2^n, ., .)
from gororoba_quantum/cd_core.py. Let G_n = <L_{e_m} : m in F_2^n> and let H_n
be the kernel of the translation map G_n -> F_2^n.

**Theorem.** For n >= 3, H_n is elementary abelian of rank 2^(n-1), so

    |G_n| = 2^(n + 2^(n-1)).

Writing a sign diagonal (-1)^v as the Boolean function v on F_2^n, and
splitting an index as x = (x', xi) with x' the low n-1 bits and xi = bit n-1,

    H_n = { v(x', xi) = g(x') + c xi : g of even weight on F_2^(n-1), c in F_2 }.

Every element of H_n has ANF degree at most n - 2, and degree n - 2 is
attained. For n = 2, H_2 = {+I, -I} and G_2 is the quaternion group Q8 of order
2^3. For n = 1, H_1 = {+I, -I} and |G_1| = 4.

Equivalently, H_n is the monomial code spanned by the monomials x^S with S a
proper subset of {0, ..., n-2}, together with the single monomial x_{n-1}: the
Reed-Muller code RM(n-2, n-1) on the low bits, direct sum the top coordinate.
The two descriptions agree because a function of m variables has even weight
exactly when its ANF omits the full product x_0 ... x_{m-1}.

The proof below is complete for every n >= 3. scripts/left_mult_sign_rank.py
checks every lemma it uses (the closed form of Lemma 3 at n <= 7) and the
statement itself, in both containment
directions, through n = 11.

## Conventions

### The sign function

phi_n(a, b) = [psi_n(a, b) = -1] in F_2. Bit n-1 of an index is the last
Cayley-Dickson doubling: the first iteration of the cd_sign loop compares each
index against half = 2^(n-1), and the remaining iterations are the loop of
cd_sign(2^(n-1), ., .) on the rewritten pair, times the first iteration's
sign. Write a = (a', alpha) for a = a' + alpha 2^(n-1), and similarly
b = (b', beta), x = (x', xi). Reading the four branches of cd_sign at
dimension 2^(n+1):

| alpha | xi | branch of cd_sign | phi_{n+1}((a', alpha), (x', xi)) |
| --- | --- | --- | --- |
| 0 | 0 | both low: no change | phi_n(a', x') |
| 0 | 1 | low, high: (p, q) -> (q - half, p) | phi_n(x', a') |
| 1 | 0 | high, low: negate when q != 0 | phi_n(a', x') + [x' != 0] |
| 1 | 1 | both high: return -1 when q' = 0, else (p, q) -> (q', p') | phi_n(x', a') + [x' = 0] |

The last row's early return gives -1 = -psi_n(0, a') because of Lemma 0. With
N(x') = [x' != 0] = 1 + delta_0(x'), phi^(0)(a', x') = phi_n(a', x'), and
phi^(1)(a', x') = phi_n(x', a'), the table is the single formula

    (R)  phi_{n+1}((a', alpha), (x', xi)) = phi^(xi)(a', x') + alpha (N(x') + xi).

The level-0 algebra is the reals: cd_sign(1, 0, 0) = +1 and phi_0 = 0.

### The group

L_{e_m} sends e_x to psi_n(m, x) e_{m^x}, so every word in the generators is a
signed XOR translation |x> -> (-1)^(v(x)) |x ^ t>, and the translation part is
a homomorphism G_n -> F_2^n. L_{e_m} has translation m, so the map is onto and
|G_n| = 2^n |H_n|. H_n consists of +/-1 diagonals, so H_n is elementary abelian
and v -> (-1)^v identifies it with an F_2-subspace V_n of functions on F_2^n:
|H_n| = 2^(dim V_n).

The set {L_{e_m}} serves both as the generating set of G_n and as a
transversal of the left cosets g H_n: the coset L_{e_m} H_n holds every
element with translation m, L_{e_m} is the representative chosen from it,
and L_{e_0} = I by Lemma 0. Schreier's lemma for left cosets
gives H_n = < rep(s t)^(-1) s t > over generators s and transversal elements t;
with s = L_{e_a} and t = L_{e_b}, rep(L_{e_a} L_{e_b}) = L_{e_{a^b}}. H_n is
normal, so the right-coset form generates the same subgroup. The generator
L_{e_{a^b}}^(-1) L_{e_a} L_{e_b} is diagonal with sign vector

    s_{a,b}(x) = phi_n(b, x) + phi_n(a, b^x) + phi_n(a^b, x),

which is gororoba_quantum/verify.py `_schreier_sign_vector`. Hence V_n is the
F_2-span of {s_{a,b}}.

s_{a,b}(x) = assoc(a, b, x) + phi_n(a, b), where assoc(a, b, x) =
[(e_a e_b) e_x = -e_a (e_b e_x)] is the associator sign: the Schreier sign
vectors are associator rows up to a constant.

The survey (literature/notes/open_gororoba_survey.md) closes <L_{e_p}, -1>;
verify.py closes <L_{e_p}>. The groups coincide: the all-ones vector has even
weight and c = 0 in the theorem's description, so -I lies in H_n. A rephasing
e_p -> -e_p changes every s_{a,b} by a constant and leaves V_n unchanged.

## Lemmas on phi_n

**Lemma 0.** phi_n(0, x) = phi_n(x, 0) = 0 for every n and x.

*Proof.* With q = 0, cd_sign takes only the both-low and high-low branches, and
the high-low branch negates only when q != 0; q stays 0. With p = 0, the
low-high branch rewrites (0, q) to (q - half, 0), after which q = 0. Neither
path negates.

**Lemma 1 (commutator).** C_n(c, y) := phi_n(c, y) + phi_n(y, c) =
N(c) N(y) N(c ^ y): distinct nonzero basis units anticommute and every other
pair commutes. For every c, as a function of y,

    C_n(c, y) = N(c) + delta_0(y) + delta_c(y).

*Proof.* Induction on n; level 0 has only c = y = 0. Apply (R) to both orders
with c = (c', gamma), y = (y', eta):

- gamma = eta = 0: C_{n+1} = C_n(c', y'), and N(c) = N(c'), N(y) = N(y'),
  N(c ^ y) = N(c' ^ y').
- gamma = 0, eta = 1: phi_n(y', c') + (phi_n(y', c') + N(c')) = N(c'), and the
  target is N(c') . 1 . 1.
- gamma = 1, eta = 0: symmetric, N(y').
- gamma = eta = 1: (phi_n(y', c') + N(y') + 1) + (phi_n(c', y') + N(c') + 1)
  = C_n(c', y') + N(c') + N(y'), and the target is N(c' ^ y'). With
  C_n = N(c')N(y')N(c' ^ y') the four cases c' = 0, y' = 0, c' = y' != 0, and
  c', y' distinct nonzero give N(y'), N(c'), 0, and 1, which equal
  N(c' ^ y') in each case.

For the second form: C_n(0, y) = 0 and delta_0 + delta_0 = 0; for c != 0,
[y != 0][y != c] = 1 + delta_0(y) + delta_c(y) because delta_0 and delta_c have
disjoint supports.

**Lemma 2 (parity).** For n >= 2 every row phi_n(c, .) and every column
phi_n(., c) has even weight.

*Proof.* Let w_L and w_R be row and column weights at level n >= 1. By (R),
the row (a', alpha) at level n+1 has weight congruent mod 2 to
w_L(a') + w_R(a') + alpha #{(x', xi) : N(x') + xi = 1}. The count is
(2^n - 1) + 1 = 2^n, and w_L(a') + w_R(a') is congruent mod 2 to
sum over y of C_n(a', y) = N(a') (2^n - 2) by Lemma 1. Both are even. The
column (b', beta) at level n+1 is phi^(beta)(x', b') + xi (N(b') + beta) at
(x', xi), with weight congruent mod 2 to
2 sum_{x'} phi^(beta)(x', b') + 2^n (N(b') + beta), also even.

Level 1 is the exception: phi_1(1, 1) = 1 and phi_1(1, 0) = 0, so row 1 has
weight 1.

**Lemma 3 (closed form).** At level n+1, with P(xi, x') :=
phi^(xi)(b', x') + phi^(xi)(a' ^ b', x') + phi^(beta + xi)(a', b' ^ x'),

    s_{a,b}(x', xi) = P(xi, x') + alpha (delta_0(x') + delta_{b'}(x') + beta).

*Proof.* Expand the three terms of s_{a,b} by (R):

    phi_{n+1}(b, x)       = phi^(xi)(b', x')               + beta (N(x') + xi)
    phi_{n+1}(a, b ^ x)   = phi^(beta + xi)(a', b' ^ x')   + alpha (N(b' ^ x') + beta + xi)
    phi_{n+1}(a ^ b, x)   = phi^(xi)(a' ^ b', x')          + (alpha + beta)(N(x') + xi)

The beta (N(x') + xi) terms cancel, leaving alpha (N(b' ^ x') + N(x') + beta),
and N(b' ^ x') + N(x') = delta_{b'}(x') + delta_0(x').

## Proof of the theorem

Fix n >= 2 and work at level n+1 >= 3. Let U_{n+1} be the space in the theorem:
functions g(x') + c xi with g of even weight on F_2^n. dim U_{n+1} = (2^n - 1) + 1
= 2^n.

**Upper bound, V_{n+1} in U_{n+1}.** A function v lies in U_{n+1} exactly when
(i) v(x', 1) + v(x', 0) is constant in x' and (ii) v(., 0) has even weight. The
alpha term of Lemma 3 does not depend on xi, so for (i) only P matters:

    P(0, x') + P(1, x') = C_n(b', x') + C_n(a' ^ b', x') + C_n(a', b' ^ x'),

for either value of beta, because phi^(beta) + phi^(beta + 1) = C_n. By the
second form of Lemma 1 this is

    N(b') + delta_0 + delta_{b'} + N(a' ^ b') + delta_0 + delta_{a' ^ b'}
          + N(a') + delta_{b'} + delta_{a' ^ b'}   (evaluated at x')
    = N(a') + N(b') + N(a' ^ b'),

a constant. For (ii), the weight of s_{a,b}(., 0) is congruent mod 2 to
w_L(b') + w_L(a' ^ b') + (w_L(a') or w_R(a')) plus the weight of
alpha (delta_0 + delta_{b'} + beta), which is 0, 2, 2^n, or 2^n - 2. Lemma 2 at
level n >= 2 makes the row and column weights even. So every s_{a,b} lies in
U_{n+1}.

**Lower bound, U_{n+1} in V_{n+1}.** Take a = (0, 1) and b = (b', 0). The first
two terms of P cancel and Lemma 0 kills the third, so Lemma 3 gives
s_{a,b} = delta_0(x') + delta_{b'}(x'). For b' != 0 these 2^n - 1 vectors are independent and span the even-weight
functions of x'. Take a' and b' distinct and nonzero, possible because n >= 2,
with alpha = beta = 0 (indices a = 1, b = 2): the constant in (i) is
1 + 1 + 1 = 1, so s_{a,b} = g(x') + xi with g even weight, and xi lies in the
span.

Hence V_{n+1} = U_{n+1}, dim V_{n+1} = 2^n, and |G_{n+1}| = 2^(n+1 + 2^n). In
the theorem's indexing, dim V_n = 2^(n-1) for n >= 3.

**Degree.** A function of n-1 variables has even weight exactly when its ANF
omits x_0 ... x_{n-2}, so g has degree at most n - 2, and xi has degree
1 <= n - 2 for n >= 3. The degree of a sum is at most the larger degree of its
terms, so every element of V_n has degree at most n - 2. x_0 ... x_{n-3}, of
weight 2 on F_2^(n-1), lies in V_n and has degree n - 2.

**Small n.** At level 2 the constant N(a') + N(b') + N(a' ^ b') of (i) is 0
for every a', b' in F_2, so every s_{a,b} depends on x' alone and the xi
generator is absent. Lemma 2 fails at level 1, so the parity (ii) at level 2
rests on direct computation: the 16 vectors s_{a,b} span the constants, and
G_2 = Q8. The dimension therefore goes 1, 4, 8, 16, ...: it quadruples from
level 2 to level 3 and doubles from level 3 onward. V_2 has degree 0 = n - 2,
so the degree bound holds at n = 2 as well.

**Exponent.** verify.py `check_left_mult_group` records the exponent argument:
(D P_a)^2 is diagonal and squares to I, so every element has order dividing 4.

## Computation

`"$PYTHON" scripts/left_mult_sign_rank.py --max-n 10` prints the table and
exits 0; `--timing` adds per-level seconds on stderr. For each n from 2 to
--max-n the script asserts, and exits 1 at the first failure:

- recursion (R) against cd_sign, row by row, from level n-1;
- Lemma 1 and, for n >= 2, Lemma 2;
- Lemma 3 cell by cell against directly computed s_{a,b}, for n <= 7;
- every distinct s_{a,b} lies in U_n (upper bound);
- full Gaussian elimination over F_2 on all distinct s_{a,b}, with vectors as
  Python ints and pivots keyed by leading bit, gives rank 2^(n-1) (1 at n = 2);
  this rank is independent of the explicit description;
- every basis vector of U_n reduces to zero against that elimination (lower
  bound);
- every pivot vector has ANF degree at most n - 2 and some vector reaches it.

Falsifiers stated before the run: a rank other than 2^(n-1), a Schreier vector
outside U_n, a U_n basis vector outside the span, or a span vector of degree
above n - 2. None occurred. `--mutate high-low-unconditional` and `--mutate
high-high-no-early-return` each replace one branch of the sign recursion by a
wrong one; the run then exits 0 only when a check catches the mutation, and
both are caught at n = 2 (the gate runs them at `--max-n 5`).

| n | dim | distinct s_{a,b} | rank | max degree | log2 \|G_n\| | seconds |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 4 | 2 | 1 | 0 | 3 | < 0.01 |
| 3 | 8 | 16 | 4 | 1 | 7 | < 0.01 |
| 4 | 16 | 86 | 8 | 2 | 12 | < 0.01 |
| 5 | 32 | 524 | 16 | 3 | 21 | 0.01 |
| 6 | 64 | 2586 | 32 | 4 | 38 | 0.03 |
| 7 | 128 | 11640 | 64 | 5 | 71 | 0.17 |
| 8 | 256 | 49846 | 128 | 6 | 136 | 0.58 |
| 9 | 512 | 207412 | 256 | 7 | 265 | 4.96 |
| 10 | 1024 | 848690 | 512 | 8 | 522 | 37.22 |
| 11 | 2048 | 3438896 | 1024 | 9 | 1035 | 336.93 |

Seconds are wall time per level for one run under CPython 3.14.7, single
threaded; the closed-form check runs at n <= 7 only. The n = 11 row comes from
`--max-n 11`, which takes about 6.5 minutes in all and peaks near 1.2 GB
resident. The n = 3..8 orders
reproduce the survey's sympy closure, and n = 9 gives the survey's predicted
2^265.
