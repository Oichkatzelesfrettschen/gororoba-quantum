# Gauss map of the kernel bundle at the stratum V: four objects and a proposed order of work (draft)

Status: draft idea, written by a working session and landed unreviewed. Checked against the tree: the orbit
representative of V is the entry `"V": split_point({1: 3}, 4, {1: 5})` of
[strata_regularity.py](../../evidence/a5-strata-regularity/strata_regularity.py), and the derivation span is
computed in [rederive_strata_equations.py](../../evidence/a5-rank-strata-equations/rederive_strata_equations.py).
hypothesis: every other formula below (the eight quadrics and their zero set, the split-coordinate form of C_z, the
stabilizer and its eigenspaces) is unverified here; the Rocq file it names lives in the gororoba-open repository and
is not in this tree. The proposed first step is the limit-set computation from nullity 8 to nullity 12 of
[a5-kernel-attachments-program.md](../../design/a5-kernel-attachments-program.md); the nullity-4 Gauss map is retained in
[a5-kernel-bundles-residuals](../../evidence/a5-kernel-bundles-residuals/README.md).

## 1. Eight Quadratic Generators q₁, …, q₈

The Rocq file `NullityTwelveQuadraticLocus.v` (gororoba-open) defines eight quadratic polynomials in affine coordinates (z₅, z₆, z₁₃, z₁₆, z₁₇, z₁₈, z₁₉, z₂₀) ∈ ℝ⁸ with 13 free affine coordinates:

q₁ = z₆² - z₁₆²
q₂ = z₅ z₆ - z₁₃ z₁₆
q₃ = z₁₃ z₆ + z₁₆ z₅
q₄ = z₁₇ z₅ - z₁₃ z₂₀ + z₁₆ z₁₇ + z₂₀ z₆
q₅ = z₁₃ z₁₉ + z₁₈ z₅ + z₁₆ z₁₈ - z₁₉ z₆
q₆ = z₁₉ z₅ - z₁₃ z₁₈ + z₁₆ z₁₉ + z₁₈ z₆
q₇ = z₁₃ z₁₇ + z₂₀ z₅ + z₁₆ z₂₀ - z₁₇ z₆
q₈ = z₁₆ z₆

The certified zero set is:
𝒱(q₁, …, q₈) = {z₆ = z₁₆ = z₁₇ = z₁₈ = z₁₉ = z₂₀ = 0} ∪ {z₆ = z₁₆ = z₅ = z₁₃ = 0}

---

## 2. The 16 × 16 Complex Matrix C_z

For z ∈ ℂ¹⁶ ≅ 𝔸₄ ⊗ ℂ, C_z is the imaginary block of left multiplication by z in the sedenion algebra 𝔸₄. Entries for row a ∈ {0, …, 15} and column b ∈ {0, …, 15}:

(C_z)_{a,b} = cd_sign(16, a ⊕ b, b) · z_{a⊕b}

where ⊕ denotes bitwise exclusive-OR, and cd_sign(16, p, q) ∈ {-1, +1} is the Cayley-Dickson structural sign table on standard basis elements eₚ · e_q = cd_sign(16, p, q) e_{p⊕q}.

In split coordinates z'_k (k = 0, …, 15, with z_k = i^{popcount(k)} z'_k):
(C'_z')_{a, b} = (-1)^{popcount(a & b)} · cd_sign(16, a ⊕ b, b) · z'_{a ⊕ b}

C_z is skew-Hermitian on the pure imaginary subspace Re(z) = 0.

---

## 3. Orbit Representative of V in Split Coordinates

Extracted from `strata_regularity.py` (entry `V` of the orbit representatives):
z'_V = (u'_V, μ'_V, v'_V) ∈ ℂ⁷ × ℂ × ℂ⁷

Explicit component vector in ℂ¹⁵:
u'_V = 3 e'_1 = (3, 0, 0, 0, 0, 0, 0)
μ'_V = 4
v'_V = 5 e'_1 = (5, 0, 0, 0, 0, 0, 0)

Invariant metric evaluation on ℂ⁷ with signature η = diag(-1, -1, +1, -1, +1, +1, -1):
η(u'_V) = -9
η(v'_V) = -25
η(u'_V, v'_V) = -15

s = u'_V + v'_V = 8 e'_1
d = u'_V - v'_V = -2 e'_1
η(s, d) = η(8 e'_1, -2 e'_1) = (-16) · η(e'_1) = (-16)(-1) = 16

Quadratic hypersurface equation:
Q(z'_V) = η(s, d) - (μ'_V)² = 16 - 4² = 0
rank[u'_V; v'_V] = rank(3 e'_1, 5 e'_1) = 1

---

## 4. Action of H_V = SU(2) × U(1) on (u', μ', v')

### 4.1 Ambient Tangent Generators of H = G₂(ℂ) × SO(2, ℂ) × ℂ^*

The Lie algebra 𝔤₂(ℂ) acts via 14 derivations D ∈ Der(𝕆') diagonally on u' and v':
D(u', μ', v') = (D u', 0, D v')

subject to the metric-skew condition: η(D x, y) + η(x, D y) = 0.

The hyperbolic boost generator 𝔰𝔬(2, ℂ) acts as:
B(u', μ', v') = (v', 0, u')

The scaling ℂ^* acts as:
S(u', μ', v') = (u', μ', v')

### 4.2 Stabilizer 𝔥_V at z'_V

The vectors u'_V and v'_V lie entirely along the line spanned by e'_1. The sub-algebra of 𝔤₂(ℂ) fixing e'_1 is isomorphic to 𝔰𝔩(3, ℂ) (compact form 𝔰𝔲(3)). Under e'_1, the orthogonal space (e'_1)^⊥ ⊂ ℂ⁷ splits into two 3-dimensional eigenspaces V₊ and V₋ of the cross product operator e'_1 × ·:

V₊ = span{e'_2 + e'_3, e'_4 + e'_6, e'_5 + e'_7}
V₋ = span{e'_2 - e'_3, e'_4 - e'_6, e'_5 - e'_7}

The normal null directions n_± satisfying e'_1 × n_± = ± n_± and η(n_±) = 0 lie in V_±. The SU(2) subgroup of the stabilizer SU(3) preserves the chosen null pair, rotating the normal slice via its standard spin representation. On μ', the SU(2) action is trivial (μ' is an SU(2)-singlet).

---

## Sequence Selection

Execute Bottleneck 2 (Gauss Map Classification in Gr_ℂ(4, 6)) first.

### Rationale

1. Bottleneck 2 decides whether the kernel bundle attaching map over V is topologically rigid or transitive under the stabilizer SU(2), providing the closed topological classification of the boundary singularity.
2. The computation requires only exact rational linear algebra on the 16 × 16 matrix C_z(t) and its Jordan chain leading terms, with no large-scale polynomial elimination dependencies.

---

## Verification Status

The derivation definitions in `rederive_strata_equations.py` and its retained result state:

- The 14 split octonion derivations span the Lie algebra 𝔤₂.
- All inner derivations D_{x,y} = [Lₓ, L_y] + [Lₓ, R_y] + [Rₓ, R_y] lie in this span.
- Not run: the Plücker coordinates of the Jordan chain leading subspace 𝒦_∞(n_±) and the Jacobian rank of the Gauss map into Gr_ℂ(4, 6).