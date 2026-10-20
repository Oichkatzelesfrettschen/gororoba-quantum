# Singular sectors of two-term Cayley-Dickson elements and the dynamics they fix

A two-term element `a = e_i + t e_j` (distinct imaginary basis units, `t = +-1`)
of any Cayley-Dickson algebra splits the algebra into three sectors on which
`L_a` acts with singular value 0, `sqrt2` or 2. One diagonal sign,
`(L_i L_j)^2`, decides the split. The sectors fix every dynamical response the
repository can build from `L_a`: the Hermitian dilation's frequencies, the
exactness of a product-formula step, and the frozen response of amplitude
amplification on Design B's block encoding. Together they answer the
measurement-foundations review recorded in
[qpu_vacuum_cd_review_reconciliation.md](topics/qpu_vacuum_cd_review_reconciliation.md):
the algebra decomposes into computable sectors, and those sectors predict which
hardware response carries new information.

[scripts/singular_sector_dynamics.py](../../scripts/singular_sector_dynamics.py)
recomputes every statement below from `cd_core.cd_sign`; gate core-240
runs it. Gate core-242 replays the
retained [FakeFez record](../evidence/singular_sector_dynamics/fakefez_amplification.json).
Labels follow [prior_work_synthesis.md](prior_work_synthesis.md): known theorem
reproduced, new proof or formalization, new implementation or measurement,
candidate new result.

## Sector split in every dimension

`L_m = L_{e_m}` is a signed permutation, and `L_m^T = L_{conj(e_m)} = -L_m`
([BCDI](0905.2987.md) Lemma 2.3), so `L_m^2 = -L_m^T L_m = -I`. Put
`P = L_i L_j` and `m = i XOR j`. Then `P e_k = s_k e_(k XOR m)` with
`s_k = cd_sign(j, k) cd_sign(i, j XOR k)`, and `P^2 e_k = s_k s_(k XOR m) e_k`
is a diagonal sign. Its `+1` and `-1` coordinates span `S+` and `S-`.

- `P^T = L_j L_i = P^(-1)`, so `{L_i, L_j} = P + P^(-1)` and
  `[L_i, L_j] = P - P^(-1)`. On `S+`, `P^(-1) = P` and the two units commute;
  on `S-`, `P^(-1) = -P` and they anticommute.
- `L_i` commutes with `{L_i, L_j}` by expansion, and
  `(P + P^(-1))^2 = 2I + 2P^2` because `P^4 = I`. So `P^2` is a polynomial in
  the anticommutator, and `L_i`, `L_j` preserve both sectors.
- `L_a^T L_a = -(L_i + t L_j)^2 = 2I - t{L_i, L_j}`. On `S-` this is `2I`.
  On `S+` it is `2I - 2tP` with `tP` an involution: the dark sector `tP = 1`
  has `L_a = 0`, the bright sector `tP = -1` has `L_a^T L_a = 4I`, and `P`
  pairs `k` with `k XOR m`, so each has dimension `|S+|/2`.

Every two-term element therefore has `L_a^T L_a` spectrum in `{0, 2, 4}`
(`M_a = L_a^T L_a / |a|^2` in `{0, 1, 2}`) and nullity `|S+|/2`. At D = 16 the
spectrum is [BCDI](0905.2987.md) Proposition 7.4 (known theorem reproduced).
The sign-driven split and its commutation structure in every dimension carry
the label new proof or formalization, pending one check: whether de Marrais's
higher-dimensional box-kite papers already state the split. The checker
verifies every idempotent, invariance, kernel and Gram identity on integer
matrices for all 1182 signed pairs through D = 32. A sign table with one
flipped entry moves the D = 16 sector total, which the checker rejects.

## Census link and closed forms

`{L_i, L_j} e_k = -[(e_i, e_j, e_k) + (e_j, e_i, e_k)]` for distinct imaginary
units, since `e_i e_j + e_j e_i = 0`. A dependent basis triple associates in
every dimension: with `L_m^2 = R_m^2 = -I` (both are skew signed
permutations), `(e_a e_a) e_b = e_a(e_a e_b) = -e_b`,
`(e_a e_b) e_b = e_a(e_b e_b) = -e_a`, and for `e_c = s e_a e_b`, `s = +-1`,
both `(e_a e_c) e_b` and `e_a(e_c e_b)` equal `s`. So the four indices of
`span(i, j)` always lie in `S-`. Expanding both associators through the
basis signs gives `k in S+` exactly when `omega(i, j, k) != omega(j, i, k)`,
where `omega` is the associator sign of the
[defect census](topics/cd_associator_defect_census.md). Census Theorem 3 gives
`omega = -(-1)^l_W(a XOR c)` on a quasi-octonion plane `W` and `omega = -1` on
an octonion plane. So `k` lies in `S+` exactly when the plane
`W = span(i, j, k)` is quasi-octonion and `l_W(i XOR j) = 1`. A quasi-octonion
plane has four `x` with `l_W(x) = 1`, three pairs `{i, i XOR x}` for each, and
four `k` per pair:

```
sum over pairs of |S+| = 48 Q(D) = (D-2)(D-4)(D-8)/4.
```

Label: new proof, derived from census Theorem 3; the checker confirms the
omega criterion pair by pair through D = 32 and the total through D = 512.

The anticommuting pairs, those with `S+` empty and `L_a^T L_a = 2I` for both
signs, number

```
c(D) = (3/2) D log2(D) - (9/4) D + 3          (D >= 8),
```

the solution of `c(D) = 2 c(D/2) + 3(D/2 - 1)` with `c(8) = 21`. The proof runs
through the doubling `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))` of
`cd_core`, with `h = D/2`, `e_x = (e_x, 0)` and `e_(h+x) = (0, e_x)`. Then
`L_(a,0) = diag(L_a, R_a)` and `L_(0,b)` maps `(c, d)` to
`(-R_b C d, L_b C c)`, where `C` is conjugation and `R_a = C L_conj(a) C`.

- Low pair `(a, 0), (b, 0)`: the anticommutator is
  `diag({L_a, L_b}, {R_a, R_b})` and `{R_a, R_b} = C {L_a, L_b} C`, so `|S+|`
  doubles from `A_(n-1)`.
- High pair `(0, a), (0, b)`: the anticommutator is
  `diag({R_a, R_b}, {L_a, L_b})` for imaginary `a, b`, so `|S+|` doubles; it
  vanishes for `a = 1`, so every pair through `e_h` anticommutes.
- Mixed pair `(a, 0), (0, x)`: the anticommutator is off-diagonal, built from
  `[L_a, R_x]` and `[R_a, L_x]`. The column of `[L_a, R_x]` at `e_c` is
  nonzero exactly when `omega(a, c, x) = -1`, which never happens for the
  four dependent `c` in `span(a, x)` by the lemma above, and by census Theorem 3
  `omega(a, c, x) = +1` for `c` outside `span(a, x)` exactly when `c` lies in
  `S+(a, x)` of `A_(n-1)`. So `|S+| = 2(h - 4 - |S+(a, x)|)` for `x` outside
  `{0, a}`, and 0 for `x = 0` (the unit) or `x = a` (flexibility).

Induction from the octonions, where `|S+| = 0`, gives `|S+| <= D - 8`, with
equality on mixed pairs over anticommuting lower pairs. A mixed pair therefore
anticommutes only for `x` in `{0, a}`, which yields the recurrence, and the
largest two-term nullity is `D/2 - 4`; the retained census records 4, 12, 28,
60 and 124 at D = 16 to 256. Elements reaching `2^(n-1) - 4` are
[BDI II](math-0702075.md) Proposition 8.2 (known); the upper bound for every
two-term element is this recursion, and its relation to BDI II Theorem 8.1 is
unchecked. At D = 16 the count 63 is Levratti's Remark 5.4
([note](levratti-2026-fano-css.md)), and the Gram identity
`L_a^T L_a = 2I - t {L_i, L_j}` with the 63/42 split is already gated in
[octonion_structure_checks.md](topics/octonion_structure_checks.md); its annihilator
of `e1 + e10`, `span{e4 - e15, e5 + e14, e6 - e13, e7 + e12}`, is this note's
dark sector. Label: new proof, derived from census Theorem 3 and the doubling
formula; a comparison with de Marrais's higher-dimensional counts remains
open. The checker verifies the recursion at every pair and the bound at every
dimension through D = 512.

| D | Anticommuting pairs c(D) | Two-term zero-divisor index pairs | Sum of \|S+\| |
| ---: | ---: | ---: | ---: |
| 8 | 21 | 0 | 0 |
| 16 | 63 | 42 | 336 |
| 32 | 171 | 294 | 5040 |
| 64 | 435 | 1518 | 52080 |
| 128 | 1059 | 6942 | 468720 |
| 256 | 2499 | 29886 | 3968496 |
| 512 | 5763 | 124542 | 32644080 |

The repository's two-term annihilator census,
[annihilator_strata.json](../../results/hw_estimate/annihilator_strata.json),
computes each rank independently through exact `2x2` blocks. Its rank-nullity
histogram at every retained dimension, 8 through 256, equals twice the `|S+|`
distribution with nullity `|S+|/2`; at D = 32 both give 342, 168, 168 and 252
signed elements at nullity 0, 4, 8 and 12. The checker reads the retained file
and fails on any difference. The sign `(L_i L_j)^2` alone thus explains the
whole two-term stratum census.

## Hermitian dilation and its frequencies

Imaginary `a` has `L_a^T = -L_a`, so the dilation used in the review and in
[Kang and Su](2510.06316.md),

```
H_a = |0><1| (x) L_a + |1><0| (x) L_a^T = (iY) (x) L_a,    H_a^2 = I (x) L_a^T L_a,
```

conserves the block qubit's Y eigenvalue, and on each Y eigenspace evolves the
algebra register by the real rotation `exp(+-s L_a)`. From `|1>|v>` under
`H_a / alpha`, the block flips with probability

```
P(s) = ||Pi_bright v||^2 sin^2(2s/alpha) + ||Pi_S- v||^2 sin^2(sqrt2 s/alpha),
```

and the dark component never leaves. For the review's example
`a = e1 + e10` and `alpha = 2`, the dark input `v_- = (e4 - e15)/sqrt2` gives
`P(s) = 0` and the bright input `v_+ = (e4 + e15)/sqrt2` gives
`P(s) = sin^2(s)`: the review's sedenion claim holds in this repository's
convention.
The two lines have incommensurate frequencies, so a mixed response is
quasi-periodic. From the maximally mixed register each oscillating sector
averages to one half, and the long-time mean is `rank(L_a) / (2D)`: 3/8 for
every sedenion corpus element. Labels: the dilation is standard prior work
(cited in Kang and Su); the flip law and the rank meter are a new formalization
for these operators.

In composition algebras (D <= 8) `L_a^T L_a = |a|^2 I` for every `a`, so the
dilation response is a single line; the second and third lines appear first
at D = 16, exactly on the pairs where `{L_i, L_j}` fails to vanish, which are
the pairs where the linearized left-alternative law fails.

## One product-formula step reproduces Design B

Write `H_a = H_i + H_j` with `H_i = (iY) (x) L_i` and `H_j = (iY) (x) t L_j`.
Because the units commute on `S+`, one step
`exp(-i theta H_i) exp(-i theta H_j)` equals `exp(-i theta H_a)` on dark and
bright for every `theta`. On `S-` the two terms anticommute and square to the
identity, so they act as a spin-1/2 pair: one step flips the block with
probability `sin^2(2 theta)/2`. Summed over sectors, a single step flips

```
sin^2(2 theta) <v| B^T B |v> / |v|^2,    B = L_a / 2,
```

which is Design B's success probability times a known factor. A one-step
circuit therefore carries no information beyond Design B. Repeated steps on
`S-` follow `sin^2(n phi) 2 cos^2(theta) / (1 + cos^2(theta))` with
`cos(phi) = cos^2(theta)`, which tends to the dilation's `sqrt2` line as
`theta` shrinks. The `sqrt2` line, the only frequency that distinguishes the
dilation from Design B, needs several steps or an exact synthesis of the
`S-` rotation. The checker verifies the exactness on `S+`, its failure on
`S-`, the one-step identity and six Floquet steps on all 84 sedenion corpus
elements. Label: new proof or formalization.

## Amplitude amplification of Design B is frozen

Design B's one-ancilla LCU `U` block-encodes `B = L_a/2`, with singular values
0, `1/sqrt2` and 1 on the three sectors. Rounds `U (Z U^dagger Z U)^k`, with
`Z` on the ancilla, give `P(anc = 0) = sin^2((2k+1) theta_sigma)`,
`sin(theta_sigma) = sigma`, so the sector angles 0, `pi/4` and `pi/2` leave
the probabilities at 0, 1/2 and 1 for every `k`. Each sector restricts `B` to
a multiple of an isometry, which is the hypothesis of
[BCCKS](1312.1414.md) Lemma 3.6; the general singular-value form is
[QSVT](1806.01838.md). The ideal walk has no depth dynamics.

A PREP rotation `beta = pi/4 + eps` encodes `cos^2(beta) L_i + t sin^2(beta) L_j`.
Its dark singular value is `|cos(2 beta)|`, so dark leakage is
`sin^2(2(2k+1) eps)`; bright stays 1; `S-` moves only at second order, with
`sin(theta) = sqrt(cos^4(beta) + sin^4(beta))`. The checker verifies all three
laws, through `k = 3`, on all 84 corpus elements (label: new proof or
formalization).

The reflection `Z` on the single ancilla is a virtual frame change on IBM
processors ([McKay et al.](1612.00858.md)). The echo arm `U U^dagger U`, built
with the same barriers and without the two `Z` gates, compiles to the same
non-virtual gates and the same scheduled duration as the amplified arm; the
record checks both. It returns the round-0 probability whenever the compiled
inverse undoes the error in `U`, as for a PREP angle, and then
`P(U Z U^dagger Z U) - P(U U^dagger U)` is ideally
`sin^2(6 eps) - sin^2(2 eps)`, about `32 eps^2`. CZ is self-inverse, so a
conditional phase after every CZ enters `U` and `U^dagger` with the same sign
and survives the echo instead.

The retained FakeFez record (qiskit 2.5.2, qiskit-aer 0.17.2,
qiskit-ibm-runtime 0.50.0, optimization level 3, transpiler seed 7, simulator
seed 11) prices the dark probe of `e1 + e10` and measures both contrasts under
the backend's noise model:

| Rounds k | CZ gates | Depth | P(anc = 0), ideal 0 | `ln(1 - 2P) / CZ` |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 42 | 142 | 0.0886 | -0.00464 |
| 1 | 131 | 398 | 0.22185 | -0.00448 |
| 2 | 220 | 656 | 0.30695 | -0.00433 |

The contrast `1 - 2P` falls by a nearly constant factor per CZ, the
signature of incoherent contraction. A purely coherent leakage with the
round-0 value would give 0.620 and 0.997 at `k = 1, 2`.

| Injected PREP error (rad) | CZ per arm | Amplified | Echo | Difference | Ideal difference | Difference / (1 - 2 P_echo) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 141 | 0.236025 | 0.23475 | 0.001275 | 0 | 0.002403 |
| 0.03 | 141 | 0.254925 | 0.2371 | 0.017825 | 0.028456 | 0.033901 |
| 0.06 | 141 | 0.30765 | 0.244425 | 0.063225 | 0.109766 | 0.123692 |
| 0.10 | 141 | 0.42215 | 0.2604 | 0.16175 | 0.279352 | 0.337542 |

At 40000 shots per arm the difference has standard deviation about 0.003, so
the zero-error row is a null and the injected rows are detections. Dividing
by the echo contrast lands within about 20 percent of the ideal law; the
record does not attribute the remainder.

A conditional phase `delta` composed onto every compiled CZ, alone and on top
of the FakeFez errors, moves the arms the other way:

| CZ phase (rad) | Coherent only: amplified | Echo | Difference | FakeFez: amplified | Echo | Difference |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.02 | 0.011525 | 0.087475 | -0.07595 | 0.24155 | 0.2795 | -0.03795 |
| 0.05 | 0.05885 | 0.348275 | -0.289425 | 0.2653 | 0.41865 | -0.15335 |
| 0.10 | 0.1765 | 0.5184 | -0.3419 | 0.3253 | 0.510925 | -0.185625 |

In this compilation the echo arm accumulates more of the CZ phase than the
amplified arm. The sign of the
difference therefore separates the two coherent classes, and incoherent
noise alone leaves it near zero; a mixture of the classes can cancel, so a
null difference certifies neither. Labels: new implementation or measurement
(simulation only); the matched pair is a design for a future case, not a
hardware result.

## Consequences for the hardware program

- The review's Hamiltonian ripple adds no cheap new observable: one step
  reproduces Design B, and the frozen Grover walk carries no ideal depth
  dependence. The `sqrt2` line needs a multi-step or exact `S-` synthesis whose
  cost the repository has not yet priced.
- The frozen walk becomes useful as a coherent-error discriminator. The
  amplified/echo pair at 141 CZ costs two circuits per probe and needs no
  model of the incoherent channel beyond its equality across the arms. Its
  difference has opposite signs for inverse-undone rotations and for CZ
  conditional phases, so a case needs an independent CZ-phase reference
  (for example a conditional-phase calibration on the same pairs) and would
  be priced against the allowance left after the branch-signed coherence
  case. Under the retained Fez, Kingston and Marrakesh calibrations
  ([echo_dilation_noise](../evidence/echo_dilation_noise/README.md)), SX
  over-rotation and CZ local phase move the difference negative like the
  conditional phase, so no physical rotation error lands in the
  inverse-undone class. The pair detects coherent error together with
  changes in the incoherent floor; a per-edge 2m-CZ Ramsey reference bounds
  the conditional share, jointly across edges because their phases add
  inside the shift, and the residual needs an incoherent control.
- The dark sector here is an algebraic kernel of one operator. It carries no
  electromagnetic coupling and supports no dark-matter interpretation; a
  dark-photon claim needs a calibrated sensor response such as
  [Kang et al.](2503.18315.md).

## Population flow and the operator boundary

For Hermitian `H` and `rho`, `dp_x/dt = 2 sum_y Im(H_xy rho_yx)`; for one
unitary step, `p'_x = sum_{y,z} U_xy rho_yz conj(U_xz)`, whose `y != z` terms
are the interference absent from a population-only description. The four-qubit
ripple walk has `|U_xy|^2 = 1/16`, so its incoherent part is uniform at every
depth and its depth-two departure from uniform, up to 1/2 in one outcome, is
entirely interference. A rendered probability flow is therefore a model-dependent
inference from coherences and a stated `H`, not an observed path.

Matrix composition stays associative: `(L_a L_b - L_ab) c = -(a, b, c)` with
`(a, b, c) = (ab)c - a(bc)`, checked on 40 seeded integer sedenion triples.
A faithful representation turning the product into operator composition
would force every associator to vanish; the repository encodes the two
bracketings as separate procedures and compares their outputs.
