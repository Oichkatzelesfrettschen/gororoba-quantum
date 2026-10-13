# Complex skew coordinates for Cayley-Dickson rank geometry

Multiplication in dimension 32 admits a 16-by-16 complex skew representation.
The representation reduces the size of exact classical rank and kernel
calculations. It retains complex conjugation and supplies no physical qubit
reduction. The construction below holds at every stage n >= 2 and for every
real doubly-pure coefficient vector, including zero.

[Zhilina, Section 6, Lemmas 6.6-6.10](2608.26893.md) supplies the prior
conjugate-linear structure. [Biss-Dugger-Isaksen](math-0511691.md) supplies the
real annihilator framework and rank divisibility. The coordinate formulas,
executable API and convention controls below instantiate those results.
Pfaffian rank conditions and Schur charts are standard linear algebra.
The repository claims an implementation certificate, rather than priority for
these structural theorems. [Koebisu Discussion Q4](2608.08232.md) motivates
the remaining rank geometry; the equations below do not solve its components.

## All-stage coordinate proof

Write A_n=A_(n-1) x A_(n-1), m=2^(n-1), with the repository product

    (a,b)(c,d) = (ac - conjugate(d)b, da + b conjugate(c)).

Take pure a,b. Let C=diag(1,-1,...,-1) be conjugation on A_(n-1), and define

    Phi(c,d) = c + i C d,
    Phi_inverse(u+i v) = (u,C v),
    K_x = L_a - i R_b.

Conjugation reverses products at every Cayley-Dickson stage. Therefore

    Phi(xy) = ac - conjugate(d)b - i(a conjugate(d) + cb)
            = K_x conjugate(Phi(y)).

The displayed computation uses binary products only; it introduces no
associative rearrangement. Conjugation reversal follows by induction from
the doubling product. The real inner-product adjoint identities
L_a^T=L_conjugate(a), R_b^T=R_conjugate(b) follow from the same recursion
(or Zhilina Lemma 2.12(2)). Purity gives K_x^T=-K_x. Phi preserves the
Euclidean norm because C is orthogonal.

In real coordinates, D=diag(I,C) satisfies

    D L_x D = [[L_a,-R_b],[-R_b,-L_a]]
            = realify(K_x) diag(I,-I).

Phi and complex conjugation are invertible real maps. Thus

    rank_R(L_x) = 2 rank_C(K_x),
    ker_R(L_x) = Phi_inverse(conjugate(ker_C(K_x))).

Every complex skew matrix has even rank: a nonzero off-diagonal entry gives
an invertible two-coordinate skew pivot, and Schur elimination continues by
induction. Hence the real rank is divisible by four. These arguments prove
the representation at every stage, independently of the finite controls.
For a nonzero coefficient vector outside the doubly-pure subspace, the
positive-definite real Cayley-Dickson zero-divisor theorem gives an invertible
multiplication operator (Zhilina Lemma 5.1). The zero vector has full kernel.
Those alternatives complete the domain reduction for arbitrary real inputs;
they do not classify the singular loci inside the doubly-pure subspace.

## Exhaustive real rank predicates

Let r be a multiple of four with 0 <= r < 2m. Then rank_R(L_x) <= r iff
all principal Pfaffians of K_x of order r/2+2 vanish. Exact rank r also
requires at least one principal Pfaffian of order r/2 to be nonzero.
The order-zero Pfaffian equals one. The full-rank upper bound is automatic.
Real and imaginary parts give real polynomial equations; a nonzero complex
Pfaffian p is the real inequality Re(p)^2+Im(p)^2>0.

To justify completeness, eliminate any nonzero skew entry by congruence.
An invertible principal pivot and an invertible principal pivot of its Schur
residual combine into an invertible principal pivot of the original matrix.
Induction produces principal nonsingular minors of every even size up to
rank. Their determinants equal the squares of their Pfaffians. Thus vanishing
of the next Pfaffian order supplies an upper bound, and the selected nonzero
Pfaffian supplies the matching lower bound. This argument concerns all real
coefficients, including specializations where a generic pivot vanishes.

`principal_pfaffians` enumerates every index set of a requested order.
`real_rank_equations` splits the resulting polynomials into their real and
imaginary parts. The division-free matching recurrence remains valid at every
specialization. Full symbolic expansions grow combinatorially; enumeration is
lazy and no sampled or generic rank substitutes for an equation. Gaussian-rational point Pfaffians use exact skew elimination with verified
nonzero pivots; polynomial inputs use the division-free recurrence. Point
certificates use exact elimination and one nonzero principal Pfaffian instead
of expanding the entire symbolic ideal.

## Connection to the Newton determinant factor

For n>=2, m is even, so real conjugation on C^m has determinant +1.
The intertwiner and det(K)=Pf(K)^2 give

    det_R(L_x) = |det_C(K_x)|^2 = |Pf(K_x)|^4.

The established Newton formula gives det_R(L_x)=N^2 E_last^2, where
N=||x||^2 and E_last is the final reduced elementary spectral coefficient.
Both |Pf(K_x)|^2 and N E_last are nonnegative on real coefficient space.
Taking the nonnegative square root therefore gives the exact identity

    Re(Pf(K_x))^2 + Im(Pf(K_x))^2 = N E_last.

In dimension 32, E_last=E7 is Koebisu's degree-14 determinant factor.
This deduction connects the two existing representations: one complex
Pfaffian gives a sum-of-two-squares expression for N E7 on the doubly-pure
subspace. The replay compares the Pfaffian with the independent trace/Newton
implementation at every retained point, including a dense invertible point.
The identity supplies another exact determinant-factor evaluator, while
lower-rank distinctions still require the smaller Pfaffians or other E_j.
The identity alone establishes neither new components nor topology.

## A finite cover with quadratic residual numerators

For j=1,...,m-1, define q_j=K[0,j]=-a_j+i b_j. The domains

    U_j = {a_j^2+b_j^2>0}

cover every nonzero doubly-pure coefficient vector. Dimension 32 has fifteen
such domains. In the ordered pivot/free coordinates (0,j; remaining indices),
write K=[[A,B],[-B^T,D]], where A=[[0,q],[-q,0]], and let u,v be the rows
of B. Exact congruence gives

    S = D+B^T A^(-1)B,
    q S = q D-u^T v+v^T u,
    rank_R(L_x) = 4+2 rank_C(S).

Each upper-triangular entry of qS equals the order-four principal Pfaffian on
(0,j,k,l), with that ordering. The replay verifies all 15*91=1365 identities
symbolically in dimension 32. These quadratic numerators retain arbitrary real
coefficients. Multiplication by q preserves residual rank only on U_j;
substitution at q=0 creates spurious solutions and falls outside that chart.

This cover gives a smaller starting point for the remaining local branch
analysis at e1+e18. Further principal elimination at that point gives complex
rank ten and a six-coordinate residual, in place of a twelve-coordinate real
residual. Solving its real equations, radicals, branches and links remains
an explicit research obligation.

## Kernel bundles and overlap maps

On a principal pivot of complex order k, require det(A)!=0 and S=0.
With free coordinates z, let F have pivot rows -A^(-1)B and free rows I.
Then K F=0. The invertible k-minor supplies rank >= k, while the m-k
independent columns of F supply rank <= k. Thus F is the complete kernel.
Independent columns of a skew matrix form a nonsingular principal minor:
write the rank factorization K=X J X^T with J invertible skew; independence
of the selected columns makes the corresponding square row restriction of
X invertible. Exact elimination therefore selects a valid maximal pivot.

The real annihilator frame is E(z)=Phi_inverse(conjugate(F z)). For F=P+i Q
and z=s+i t, the matrix on (s,t) is

    E = [[P,-Q],[-C Q,-C P]].

The Hermitian metric H=F^*F is positive definite. Its realification is E^T E;
the unit-partner fiber is the ellipsoid z^*H z=1 in these coordinates.
The frame does not assert that transition matrices are unitary.

On two charts at the same coefficient point, let pi_beta select the target
free rows. Then T_beta_alpha=pi_beta F_alpha and F_beta T_beta_alpha=F_alpha.
Uniqueness of free coordinates proves inverse and cocycle identities.
The metrics satisfy T^* H_beta T=H_alpha, and real frames satisfy
E_beta realify(T)=E_alpha. These rational identities define kernel bundles
on fixed-rank loci. A rank locus can be singular; smooth stratification and
frontier attachments require additional analysis.

## Implementation, evidence and boundaries

[complex_skew.py](../../gororoba_quantum/complex_skew.py) accepts exact rational
coefficient points through dimension 256 and creates independent real symbols
for its polynomial interface. The mathematical proof above covers all stages.
[The replay](../evidence/complex_skew/README.md) checks all coefficient
operators through dimension 64, all five nonzero dimension-32 nullities,
the origin, a dense rational invertible point, inverse/cocycle/metric
identities, generic Pfaffian determinants and deliberate corruptions.
The [proof obligations](../evidence/complex_skew/proof_obligations.json)
retain the statements for later Rocq implementation.

The existing [real principal atlas](principal_skew_atlas.md) remains available
as an independent reference. The [cone attachment model](annihilator_kernel_limits.md)
retains its named restricted scope. Neither an implicit polynomial cover nor
finite rational checks supply unrestricted connected components, a smooth
stratification, local links, a global finite model, or its cohomology ring.
QPU frequencies supply experimental evidence independently of these proofs.
