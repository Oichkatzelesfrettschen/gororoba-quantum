# Determinant lines of annihilator bundles

Every constant-rank complex skew family in a fixed complex vector space has
a trivial kernel determinant line. Applied to the
[Cayley-Dickson complex representation](complex_skew_rank_geometry.md), the
argument supplies an all-stage bundle invariant over each full real rank
locus, including its singular base points. It does not require a smooth
stratification. The statement concerns the top exterior power of the kernel;
it leaves the full kernel bundle, its higher characteristic classes, and the
attachment maps unresolved.

## Sources and scope

[Zhilina, Lemmas 6.6-6.10](2608.26893.md) supplies the prior complex skew
structure, and [Biss-Dugger-Isaksen](math-0511691.md) supplies the annihilator
setting. The coordinate proof and principal-chart coverage already establish
the real-to-complex transport in this repository. The argument below uses
ordinary exterior algebra and proves the determinant-line statement directly.
The repository claims a reproducible application and certificate, rather than
publication priority for the general skew-family theorem.

The author-hosted [Hatcher vector-bundle text](https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf)
is a further reference for characteristic-class terminology. Retrieval on
2026-10-13 UTC times out through curl and Python with a Mozilla user agent,
including the alternate `www.math.cornell.edu` host. The repository records
neither an inspected passage nor PDF bytes for that attempted retrieval.
The proof below does not depend on a claimed reading of that text.

## All-stage determinant-line proof

Let V=C^m with its fixed ordered basis, and let K(x) be a continuous family of
complex skew matrices of constant rank r=2s on a base B. In the application,
m=2^(n-1), n>=2, and B is any subset of one exact real rank locus in the
doubly-pure coefficient space. Principal nonzero r-Pfaffians cover B.
Their complete kernel charts prove that E=ker K is a vector bundle of
complex rank k=m-r, even if B itself has singularities.

The alternating form omega_x(v,w)=v^T K(x)w descends to a nondegenerate form
on Q=V/E. Its top exterior power beta=omega^s/s! is a nowhere-zero section
of det(Q)^*. The fixed ambient covolume Omega and the exact sequence

    0 -> E -> B x V -> Q -> 0

define a nowhere-zero kernel covolume lambda in det(E)^*. Use the ordering
Q then E. For any lifts u_1,...,u_r of a quotient basis and kernel vectors
f_1,...,f_k, define

    lambda(f_1,...,f_k)
        = Omega(u_1,...,u_r,f_1,...,f_k) / beta(u_1,...,u_r).

Changing a lift by a kernel vector leaves the numerator unchanged by
alternation. Changing the quotient basis multiplies numerator and denominator
by the same determinant. Nondegeneracy makes the denominator nonzero.
Thus lambda is independent of the lifts, continuous, and nowhere zero.
Consequently det(E) and det(E)^* are trivial over the entire constant-rank
base. The argument holds for every m, and hence every Cayley-Dickson stage;
finite dimension controls provide executable checks rather than the induction.

## Explicit chart factors and oriented real transport

Let I be the ordered principal pivot indices, J their increasing complement,
A=K[I,I], and F the kernel frame with F[J,:]=identity. Let epsilon_I be the
sign of the permutation (I,J). Choosing the coordinate vectors indexed by I
as quotient lifts gives

    lambda(F) = epsilon_I / Pf(A) = sigma_I.

The block-triangular matrix of the quotient lifts and F has determinant
epsilon_I. The quotient top form evaluates to Pf(A). On an overlap, write
F_source=F_target T_target_source. Alternation then gives

    det(T_target_source) = sigma_source / sigma_target.

For k>0, multiply the first column of F by 1/sigma_I. The resulting frame
has covolume one, so every normalized transition has determinant one. For
k=0, the empty frame cannot absorb a nonunit scalar; the canonical
zero-dimensional bundle is already trivial. The API treats that boundary
separately and rejects an attempted positive-rank normalization.

The real annihilator uses the certified map
Phi_inverse(conjugate(F z)). Both charts use the same conjugation, so its
coordinate transition is realify(T), with

    det_R(realify(T)) = det_C(T) conjugate(det_C(T)) > 0.

The transported complex structure therefore orients the real annihilator
bundle. The first integral Chern class is zero because it equals the first
Chern class of det(E), whose displayed global section trivializes it.
Equivalently, determinant-one transitions have a constant determinant
transition cocycle. This conclusion supplies neither a global frame for E
nor vanishing of its higher Chern classes.

## A polynomial section and the rank-drop boundary

For each increasing k-tuple J, let I be its increasing complement. Define
the k-vector tau_r by its standard exterior coordinates:

    (tau_r)_J = epsilon_I Pf(K[I,I]).

Contraction of omega^s/s! with the fixed ambient volume vector produces
these coefficients. In the quotient-plus-kernel basis the form contains
only quotient directions; the contraction therefore gives

    tau_r = epsilon_I Pf(A) wedge(F_1,...,F_k).

This identity also proves the complementary-minor formula for every J.
The vector is decomposable and nonzero on rank r, belongs to det(E), and
is dual to lambda. At rank below r, every order-r Pfaffian vanishes, so
the same polynomial expression is zero. At rank above r, tau_r does not
serve as a kernel determinant section of that rank and need not be
decomposable. The rank condition remains essential.

The vanishing at lower rank prevents the determinant section alone from
specifying a limiting kernel. For example, the two skew paths
diag(t J2,0_2) and diag(0_2,t J2), with J2=[[0,1],[-1,0]], have the same
zero endpoint and distinct persistent kernel planes. Their determinant
sections both vanish at that endpoint. These general skew paths illustrate
the logical limitation; the repository's
[Cayley-Dickson projector paths](annihilator_kernel_limits.md) supply the
separate algebra-specific frontier analysis.

## Replay and remaining obligations

`kernel_determinant.py` validates complete exact charts before producing
covolumes, certified transition determinants, normalized frames, and lazy
complementary-Pfaffian coordinates. Rational point inputs and dimensions
4 through 256 follow the existing chart API. The written proof covers
arbitrary real coefficients and every stage.

The [retained replay](../evidence/kernel_determinant/README.md) checks zero
and full rank, all four nonzero singular nullities in dimension 32, arbitrary
complex parameters on a symbolic four-dimensional skew chart, signed and
non-real transitions, and complete complementary coordinates on the stated
small fixtures. It rejects damaged certificates, mismatched points, and
empty-frame rescaling. A recorded zero coordinate-count means that the
fixture tests transitions without enumerating its full exterior coordinate
array; it does not assert an empty array.

The remaining work classifies full kernel bundles and smooth rank strata,
determines the limiting planes across every frontier, constructs a global
attachment model, and computes the pair space's integral invariants.
Determinant triviality is one constraint on that program. The proof
obligations retain a Rocq port separately from these exact computations and
written proofs; QPU frequencies do not prove a bundle theorem.
