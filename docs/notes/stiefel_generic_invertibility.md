# Generic invertibility of normalized A_6 Stiefel elements

Moreno (math/0512517, Section 5; note [math-0512517.md](math-0512517.md))
asks whether every Stiefel element of `A_(n+1)` is a zero divisor. The
retained integer witness answers no at `A_6`, and with it the invertible
Stiefel elements form an open, dense, full-measure set. This note gives the
proof and marks which steps are machine-checked, which are executable
certificates, and which rest on cited theorems.

## Conventions

- `A_n` is the Cayley-Dickson algebra of dimension `2^n` in the `cd_core`
  convention: `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`, with index
  `2^(n-1) + k` the second half.
- A Stiefel element of `A_6` is `v = (a, b)` with `a`, `b` pure in `A_5`
  (zero real part), `a . b = 0` and `|a| = |b| != 0`.
- `V` is the normalized family, `|a| = |b| = 1`. It is the real Stiefel
  manifold `V_2(R^31)` of orthonormal 2-frames in `Im A_5 = R^31`.
- `L_v` is left multiplication by `v`, a real `64 x 64` matrix with entries
  linear in `v`.

## Theorem

The set `{(a, b) in V : L_(a,b) invertible}` is open and dense in `V` and
has full measure. Its complement, the zero-divisor Stiefel elements of
`V`, is a closed semialgebraic subset of measure zero and dimension at most
58.

## Proof

1. **`F = det L_v` is a polynomial in the 64 coordinates of `v`** (written).
   The entries of `L_v` are `sigma(i xor j, j) v(i xor j)`, linear in `v`, and
   the determinant is a polynomial in the entries. Restricted to `V`, `F` is
   real-analytic, since `V` is a real-analytic submanifold of `R^62`.
2. **`V` is a connected real-analytic manifold of dimension 59** (written,
   standard). `V_2(R^31) = SO(31) / SO(29)` is a homogeneous space of the
   connected group `SO(31)`, so it is connected. Its dimension is
   `62 - 3 = 59`: 62 coordinates minus the three equations `|a|^2 = 1`,
   `|b|^2 = 1` and `a . b = 0`, whose gradients are independent on `V`.
3. **`F` does not vanish identically on `V`** (machine-checked).
   - The integer witness `w` has pure, orthogonal halves of squared norm
     62. Rocq checks these Stiefel conditions in `witness_is_stiefel`.
   - Rocq also checks `N L_w = d I` with `d != 0` (`Lv_left_inverse`) and
     a trivial integer kernel (`Lv_integer_kernel_trivial`). Hence `L_w` is
     invertible over Q, and `det L_w != 0`.
   - `F` is homogeneous of degree 64, so `F(w / sqrt 62) = 62^-32 F(w)`,
     which is nonzero. The point `w / sqrt 62` lies in `V`.

   The evidence is the bundle in [stiefel_witness](../evidence/stiefel_witness/README.md):
   `L_w` is built from open_gororoba's `cd_sign_fuel`, it agrees with
   `cd_core` (forced by the identity) and with python-hypercomplex (zero
   mismatched entries), and `nullity.json` retains the determinant residues
   modulo `2^61 - 1` and `10^9 + 7` (gate core-267).
4. **The zero set is closed, nowhere dense and of measure zero** (cited).
   A real-analytic function that is not identically zero on a connected
   real-analytic manifold vanishes on a closed set with empty interior and
   Lebesgue measure zero in every chart (Mityagin, arXiv:1512.07276, for
   the Euclidean case, applied in analytic charts). With steps 1 to 3, this
   makes `Z = {F = 0} intersected with V` closed, nowhere dense and null.
   Its complement is therefore open, dense and of full measure.
5. **`dim Z <= 58`** (cited). `Z` is semialgebraic, since `V` is algebraic
   and `F` is a polynomial. A semialgebraic subset of a 59-dimensional
   semialgebraic manifold has dimension 59 only if it has nonempty interior
   (Bochnak, Coste and Roy, *Real Algebraic Geometry*, Section 2.8, on the
   dimension of semialgebraic sets). Step 4 rules that out.

## Evidence classes of the steps

| Step | Status |
| --- | --- |
| 1, polynomial determinant | written; standard |
| 2, connected 59-manifold | written; standard homogeneous-space argument |
| 3, `F(w) != 0` | machine-checked in Rocq 9.2, closed under the global context; Python and modular certificates agree |
| 4, analytic zero set | cited theorem (Mityagin); not formalized, since the Rocq environment has no real-analysis library for it |
| 5, dimension bound | cited theorem (semialgebraic dimension); not formalized |

## Not established

- The components, conditioning and attachment geometry of `Z`. Its
  dimension is exactly 57: `Z` is the set of complex points of V(Q, f_6)
  for an irreducible f_6 not divisible by Q (claim
  `a6-a8-stiefel-zero-divisor-cone`,
  [the higher Pfaffian evidence](../evidence/stiefel-pfaffian-higher/README.md)).
- Which points `Z` contains beyond the Proposition 4.3 zero divisors of
  `nullity.json`. Those are Stiefel elements of nullity 28, so `Z` is
  nonempty.
- The universal `A_5` question, where 32 exact points have nullity 4 and no
  proof exists.
- Statements at other doubling levels, which need their own embedding and
  witness.

Because `Z` has measure zero, unguided random sampling of `V` almost surely
misses it. Its structure needs targeted families: exact rank minors,
continuation along certified loci and explicit kernel constructions.
