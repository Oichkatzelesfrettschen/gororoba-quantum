# Associator observables on the A_5 rank strata

The rank of the left alternative associator operator `L_y^2 - L_(y^2)` is not an invariant of a rank stratum on six of
the twelve strata (W8, Ehat, Iso, X+, X-, B9); on the other six (V, VB, Va+, Va-, N+, N-) it equals 24 at all 1,367 distinct exact
points sampled there. The nullity of `L_y` is the stratum invariant, and the factored spectrum of `-L_y^2 / N` varies on every
stratum except N+ and N-. `associator_observables.py` computes every observable in exact arithmetic over Q and writes
`associator-observables.json`, bound to the script by its sha256.

## Setting

For a doubly pure element `y` of the 32-dimensional Cayley-Dickson algebra A_5 (the doubling of the sedenions A_4, products
from `gororoba_quantum/cd_core.py`; doubly pure means the `e_0` and `e_16` coordinates vanish) the left and right
multiplications `L_y` and `R_y` are 32 x 32 rational matrices, `y^2 = -N e_0` with `N` the sum of the squared coordinates,
and the observables are

- the nullity of `L_y` and of `R_y`;
- the rank of `L_y^2 + N I = L_y^2 - L_(y^2)` (the associators `(y, y, w)`) and of `R_y^2 + N I` (the associators `(w, y, y)`);
- the spectrum: the factorization over Q of the characteristic polynomial of `-L_y^2 / N`, whose roots are the squared
  singular values of `L_y` in units of `N`, and its multiplicity pattern, the multiset of pairs (degree of an
  irreducible factor, multiplicity);
- in the controls, the unnormalized characteristic polynomial of `-L_y^2` and `N`.

The twelve strata are the orbits of `H = G_2(C) x SO(2, C) x C^*` of the [strata regularity record](../a5-strata-regularity/README.md),
which tabulates their closures and representatives. `R_8`, the locus of nullity at least 8 of `L_y`, is, minus the origin, the
disjoint union of twelve orbits with distinct closure-membership patterns. A point of the script lies in a stratum when the
exact nullity of `L_y` equals the stratum's nullity and its membership pattern equals the pattern of the stratum's
representative. The names are the strata script's: W8, Ehat (the verifier's E8-bar), Iso, X+, X-, B9, V, VB, Va+, Va-, N+,
N-. The split coordinates are `z' = (u', mu', v')` in `C^15`, with `u'` and `v'` in the 7-dimensional module of the split
octonions, related to `y` by `z_k = i^popcount(k) z'_k` and `z_k = y_k + i y_(16+k)`; `eta` is the invariant form of the
record, `Q = eta(u') - eta(v') - mu'^2` and `Delta = eta(u', v')^2 - eta(u') eta(v')`. In H the factor `C^*` is the complex scaling of `z`,
so the real scalings and the phase `z -> (c + i s) z` with `c^2 + s^2 = 1` are elements of H.

## Result

Each row counts distinct rational split coordinates within one stratum. The enumeration evaluates 3,596 labeled
rows at 3,044 distinct points: stabilizing movements and overlaps between families repeat some coordinates. The
summary deduplicates coordinates before counting ranks or spectra, rejects conflicting observables at repeated
coordinates, and retains evaluation counts separately. The point table keeps every labeled evaluation for replay.

| Stratum | Nullity | Evaluations | Distinct points | Ranks of `L_y^2 + N I` (distinct-point count) | Distinct spectra | Distinct multiplicity patterns | Rank on the sample |
|---|---|---|---|---|---|---|---|
| W8 | 8 | 307 | 276 | 16 (7), 20 (7), 24 (138), 28 (124) | 99 | 9 | varies |
| Ehat | 8 | 307 | 271 | 24 (40), 28 (231) | 124 | 4 | varies |
| Iso | 8 | 307 | 300 | 20 (6), 24 (73), 28 (221) | 171 | 8 | varies |
| X+ | 8 | 307 | 270 | 20 (6), 24 (38), 28 (226) | 109 | 6 | varies |
| X- | 8 | 307 | 270 | 20 (5), 24 (42), 28 (223) | 110 | 6 | varies |
| B9 | 12 | 307 | 290 | 20 (15), 24 (14), 28 (261) | 85 | 5 | varies |
| V | 12 | 307 | 232 | 24 (232) | 28 | 3 | constant 24 |
| VB | 12 | 307 | 257 | 24 (257) | 4 | 2 | constant 24 |
| Va+ | 12 | 307 | 229 | 24 (229) | 26 | 3 | constant 24 |
| Va- | 12 | 307 | 229 | 24 (229) | 26 | 3 | constant 24 |
| N+ | 16 | 262 | 211 | 24 (211) | 1 | 1 | constant 24 |
| N- | 16 | 264 | 209 | 24 (209) | 1 | 1 | constant 24 |

The ranks at the retained representatives reproduce the exploratory probe: 16 (W8), 24 (Ehat, Iso), 20 (X+, X-), 28 (B9),
24 (V, VB, Va+, Va-, N+, N-). The representative is the lowest-rank point of the sample on W8, Ehat, X+ and X-, and the
highest on B9, so the rank at one representative reads a special locus of the orbit and fixes no stratum invariant. The
record keeps, per stratum, the rank values by family, one witness per rank value with its split coordinates, and one witness
per multiplicity pattern.

### Proved

1. **Rank bound.** For a doubly pure `y = (a, b)` (the doubling `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))` with `a`, `b`
   pure imaginary in A_4, and `e = e_16 = (0, 1)`), `y^2 = -N e_0`, `ye = (-b, a)` and `y(ye) = (0, -N) = -N e`. Hence
   `L_y^2 + N I` kills `e_0`, `y`, `e` and `ye`; these four vectors are independent for `y != 0` (`y` and `ye` are orthogonal of
   equal norm and both lie in the span of the basis vectors other than `e_0` and `e_16`). The rank is at most 28, and a rank
   below 28 counts the eigenvalue pair `+- i sqrt(N)` of the skew matrix `L_y` beyond the four forced ones. The script verifies
   that `cd_multiply_exact` at dimension 32 is this doubling of dimension 16 on all 1,024 basis pairs and checks the four
   annihilation identities at every point.
2. **The right analog adds nothing.** The conjugation `c` is an involution with `c(xy) = c(y) c(x)` and `c(y) = -y`, so
   `R_y = -c L_y c`. The ranks, nullities, spectra and unnormalized characteristic polynomials of the left and right operators
   agree at every point, as the script confirms.
3. **Automorphisms preserve every observable.** An algebra automorphism `T` satisfies `L_(Ty) = T L_y T^(-1)`.
4. **The movements of H are not automorphisms of A_5.** The real 32 x 32 maps induced on `y` by a unipotent of `G_2(C)`, by the
   boost with `c = 5/4`, `s = 3/4`, by the scaling 2 and by `mu' -> -mu'` break between 168 and 900 of the 1,024 basis products
   (`map_verification` in the record). They preserve the nullity of `L_y` and the stratum, but `N` depends on `conj(z)`, so they
   move the associator observables.
5. **Non-invariance of the rank on W8, Ehat, Iso, X+, X- and B9.** Two exact points of one stratum with different ranks
   decide it; the record keeps one witness per rank value with its split coordinates (`witnesses`). W8 holds 16 at the
   representative and 28 at `u2:1`, the unipotent image `exp(N_2)` of the representative. The rank is lower semicontinuous
   in `y`, and B9 lies in the closure of W8, Ehat, Iso, X+ and X- (closure order of the regularity record), so rank 28
   holds on a non-empty open subset of each of those five orbits, and 28 is their generic value by the bound above.

### Observed on the finite sample

- On V, VB, Va+ and Va- the rank is 24 at 232, 257, 229 and 229 distinct points, and on N+ and N- at 211 and 209 distinct points, while the spectra
  take 28, 4, 26, 26, 1 and 1 distinct values. **Conjecture**, unproved for V, VB, Va+ and Va-: a certified
  point with another rank is the falsifier, and each point count above is the number tried.
- N+ and N- have one spectrum over all their points. **Inferred** from a standard fact: in original coordinates a point of
  N+ (N-) is `u = a + i b`, `v = +i u` (`v = -i u`) with `a`, `b` orthogonal of equal norm in R^7, and the compact `G_2` acts
  on `y` through the same action on the four octonion blocks, so transitivity of `G_2` on orthonormal pairs of `R^7`
  (`G_2 / SU(2) = V_2(R^7)`) makes N+ and N- each one orbit of the compact automorphisms and the scalings. The script does
  not verify transitivity; the constant spectrum over 420 distinct points (526 evaluations) agrees with it.
- The spectrum and its multiplicity pattern are not stratum invariants on any stratum but N+ and N-. On V the rational roots of
  the spectrum of the representative are 0, 1 and 2 with multiplicities 12, 8 and 12; other points of V add roots such as
  `338/769` and `2738/769`, so neither the multiplicity pattern nor the spectrum identifies the orbit of the compact group
  inside V.
- The movement families alone would have reported B9 as constant: the 180 unipotent, 6 boost-scale-reflect and 20 composite
  images of the B9 representative all have rank 28, and only the grid points reach 20 and 24 (`rank_values_by_family` in the
  record). Movements from one representative therefore under-sample the moduli, and the constancy claims on V, VB, Va+, Va-,
  N+ and N- hold for the grid points of those strata as well (100 each, 55 and 57 on N+ and N-).
- The phase `z -> (c + i s) z`, an element of the `C^*` factor of H, is not an automorphism (840 of 1,024 basis products fail
  for `(3/5, 4/5)`), and all 48 phase images (two angles, two base points, twelve strata) leave every observable, the
  unnormalized characteristic polynomial included, unchanged. The cause is unproved: conjugacy of `L_y` and `L_(y')` by
  `cI +- s L_e` or `cI +- s R_e` fails at three tested points. The sample is consistent with the observables being functions
  on the quotient of a stratum by the compact group `G_2 x U(1)` (the group of the
  [compact orbit ranks](../a5-kernel-bundles-nullity8/compact_orbit_ranks.py)) and the real scalings, with the unipotents and
  boosts of H as the moduli directions.
- The outer reflection `(a, b) -> (a, -b)` is an automorphism and exchanges X+ with X-, Va+ with Va- and N+ with N-
  (`controls.automorphism_images.reflection_image_strata`).

## Points and enumeration

Every point comes from the deterministic enumeration in the script; no random draw enters.

- `representative`: the retained representative of each stratum (the strata script and the regularity verifier agree on
  the twelve points).
- `unipotent`: `exp(t N_i)` for the 60 nilpotent derivations `N_i` of the split octonions listed by
  `verify_regularity_independent.nilpotent_derivations()`, `t` in `1, 1/2, -2`; each of the 180 matrices is checked to be an
  automorphism of the split octonion table.
- `boost-scale-reflect`: boosts `(c, s)` = `(5/4, 3/4)`, `(13/12, 5/12)`, `(5/3, 4/3)`, scalings 2 and 1/3, and `mu' -> -mu'`.
- `composite`: for `j` in `0..19`, the unipotent `exp(t_1 N_((3j+1) mod 60))`, the boost number `j mod 3`, and the unipotent
  `exp(t_2 N_((7j+4) mod 60))`, with `t_1`, `t_2` cycling through fixed rational values.
- `grid`: the points of `{-1, 0, 1}^15` in split coordinates that satisfy a necessary equation of `R_8` (`mu' = 0`,
  `eta(u') = -eta(v')`, `eta(u', v') = 0`; or `Q = 0` and `Delta = 0`), every 11th such point classified by its
  membership pattern, and per stratum 100 evenly spaced members (all members when fewer). The record lists the member counts.
  Independent 524,288-index candidate chunks run through `parallel.ordered_map`; their ascending outputs concatenate
  before the stride selection, so worker count preserves the selected coordinates and their order.

Each point is certified in its stratum by the exact nullity of `L_y` and its membership pattern, evaluated on the Gaussian
rational split coordinates of `y`; all 3,596 sample evaluations (3,044 distinct points) and all 336 control-image evaluations pass.

## Controls

| Control | Outcome |
|---|---|
| Compact automorphisms `rot-a`, `rot-b`, `rot-c`, `rot-d` (products of rotations `exp(theta D) = I + sin(theta) D + (1 - cos(theta)) D^2`, `D^3 = -D`, Pythagorean `(cos, sin)`, lifted to the four octonion blocks), `reflect` and `rot-c*reflect` | each preserves all 1,024 basis products against `cd_multiply_exact` |
| Their 288 images (6 maps, 4 base points per stratum, 12 strata) | every observable identical to the base point, the unnormalized characteristic polynomial and `N` included; every image in the stratum predicted by the reflection exchange |
| Mutation: the rotation with `cos = sin = 4/5` | 256 basis products fail, and the observables at the W8 representative change |
| H movements | 168 to 900 basis products fail per map; the observables change inside a stratum, as the table shows |
| Structural identities at every point | `y^2 = -N e_0`, four forced kernel vectors of `L_y^2 + N I` and `R_y^2 + N I`, equal left and right spectra and unnormalized characteristic polynomials, rank equal to 32 minus the multiplicity of the root 1, nullity equal to the multiplicity of the root 0 |
| Doubling convention | `cd_multiply_exact` at dimension 32 equals the doubling of dimension 16 on all 1,024 basis pairs |

## Falsifiers

- Each non-invariance claim rests on two exact witnesses; it fails only if a witness lies outside its stratum (a nullity or a
  membership pattern different from the stratum's), which the certification of every point excludes.
- Each constancy claim is overturned by one certified point of that stratum with a rank other than 24. The sample tried
  232, 257, 229 and 229 distinct points on V, VB, Va+ and Va-, and 211 and 209 on N+ and N-.
- The automorphism invariance fails at one basis pair that a map breaks, or one image whose observables differ; none of
  the 288 images and none of the six maps fails.
- The `G_2` transitivity argument for N+ and N- fails at a pair of orthogonal equal-norm vectors in `R^7` that no automorphism
  of A_5 carries to another.

## Open questions

- The rank 24 on V, VB, Va+ and Va- needs a proof or a point of another rank.
- The invariance of every observable under the phase has no explanation.
- The loci of lower rank inside W8, Ehat, Iso, X+, X- and B9 have no equations yet.

## Replay

`"$PYTHON" -B -W error docs/evidence/a5-associator-observables/associator_observables.py --check` recomputes the record in about
20 s on 12 cores and compares it byte for byte (`--write` rewrites it). The record names the sha256 of the script and of
`cd_core.py`, `parallel.py`, the regularity verifier, the strata script and the equations script. Tools: Python 3.14.7,
python-flint 0.9.0, numpy 2.5.4. Evidence: [`associator_observables.py`](associator_observables.py),
[`associator-observables.json`](associator-observables.json),
[`tests/test_a5_associator_observables.py`](../../../tests/test_a5_associator_observables.py).
