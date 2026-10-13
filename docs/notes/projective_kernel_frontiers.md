# Projective kernel limits and real frontier graphs

The first nonzero coefficient of the complementary-Pfaffian vector recovers
an approaching kernel plane when its unnormalized volume vanishes. The
[implementation](../../gororoba_quantum/projective_kernel_limits.py) computes
that coefficient from a regular polynomial frame and one Pfaffian. It avoids
enumerating every exterior coordinate and avoids a rational Gram inverse
along the path. Exact endpoint Gram matrices remain available for metric
comparisons and unit-partner attachments.

The written arguments cover polynomial skew matrices with arbitrary complex
coefficients at real endpoints, in every finite dimension. The executable
interface uses `Q(i)[t]` and rational endpoints. The final graph construction
applies to every normalized real Cayley-Dickson rank locus. Its real closure
still requires computation before the construction supplies a finite
attachment model or a homology calculation.

## Sources and evidence boundaries

The [determinant-line proof](annihilator_determinant_line.md) supplies the
complementary-Pfaffian identity. The
[complex representation](complex_skew_rank_geometry.md) supplies the
Cayley-Dickson coordinate and metric transport. These arguments apply the
structures attributed to Zhilina and Biss-Dugger-Isaksen in those notes;
the repository claims an exact implementation and a reproducible reduction,
without asserting publication priority for polynomial module saturation or
Grassmannian graph constructions.

[Biss-Dugger-Isaksen, Lemma 9.5](math-0511691.md) places every nonzero zero
divisor in the doubly-pure coefficient space. Their result makes the normalized
base used below cover the complete zero-product pair space.
[Basu-Roy, Theorem 1 and Definitions 1-3](1803.00505.md) supply real
semialgebraic curve selection and its representation boundary. The retained
PDF's first four pages are re-read for this construction; its SHA-256 remains
`184427ee1a8b6e4d770352e278343ef3293ad47975313842135a3e1a2aabe9c5`.
[Coste's existence results](coste-semialgebraic-geometry.md) supply the
triangulation and local-cone framework. Those sources require actual real
closure membership; polynomial identities or complex solutions alone do not
supply that premise. The external-only PDF bytes remain in the local source
cache under the existing source-library rights policy.

## Finite polynomial saturation

Let `K(t)` be an `m x m` skew matrix, polynomial over `C`, and fix a real
endpoint `a`. Write `s=t-a`. Gaussian elimination over `C(t)` supplies the
generic kernel dimension `k` and a rational kernel frame. Clearing each
column's denominator produces a polynomial frame `B(t)` with

```text
K(t) B(t)=0, rank_C(t)(B)=k.
```

Choose any nonzero `k x k` row minor `Delta(t)` of `B`. Its vanishing order
`mu=ord_a(Delta)` is finite. If `B(a)` has dependent columns, choose a
nonzero constant vector `c` in its kernel and an index `p` with `c_p!=0`.
Rescale `c` so `c_p=1`, then replace column `p` by

```text
B(t)c / (t-a).
```

Every entry in the numerator vanishes at `a`, so division is exact in the
polynomial ring. The column operation has determinant `1/(t-a)` over
`C(t)`: the unreplaced columns are standard coordinate columns and the
selected entry of `c` is one. It preserves the generic column span and
multiplies every maximal row minor by `1/(t-a)`. In particular, the retained
minor's order falls by exactly one. The polynomial identity `K B=0`
continues to hold.

The process therefore terminates after at most `mu` divisions. A further
division after the retained minor reaches order zero would contradict the
full rank of that minor at the endpoint. The resulting frame `B_reg(t)`
is polynomial, spans the generic kernel, and satisfies
`rank(B_reg(a))=k`. The recorded divisions provide a replayable witness;
the verifier checks exact divisibility, column coefficients, the termination
bound, kernel identities, and endpoint independence separately.

Every maximal minor receives the same divisor at each iteration. Since one
final minor has order zero, the division count equals the minimum initial
maximal-minor order. Computing that minimum requires neither an enumeration
of the minors nor numerical rank decisions. Its value belongs to the chosen
seed frame; it is not an intrinsic multiplicity of the rank locus.

For `k=0`, the empty frame and empty minor one give zero divisions and the
zero-dimensional limiting plane. The corresponding unit sphere is empty.
The identically zero operator uses the ambient identity frame.

## One dominant Pfaffian determines the entire leading vector

Choose increasing free rows `J` such that
`D(a)=B_reg(a)[J,:]` is invertible, and let `I` be the increasing complement.
The normalized frame

```text
F(t)=B_reg(t) D(t)^(-1), F(t)[J,:]=identity
```

is regular near `a`. Its endpoint `F0` has rank `k`. A skew matrix of
generic rank `r=m-k` has a nonzero principal minor on `I` when these free
rows form a kernel chart. One way to prove that assertion is to identify
`span(e_i : i in I)` with the quotient by the kernel; the induced alternating
form is nondegenerate there. Hence `r` is even and
`p(t)=Pf(K(t)[I,I])` is a nonzero polynomial.

Let `epsilon` be the sign of the permutation `(I,J)`. The determinant-line
identity gives

```text
tau_r(t)=epsilon p(t) wedge(F_1(t),...,F_k(t)).
```

Write `p(a+s)=s^nu (p_nu+O(s))`, with `p_nu!=0`. Since `F` is regular and
its `J` minor equals one, the minimum order among all complementary
Pfaffians is exactly `nu`. The complete leading exterior vector is

```text
w=epsilon p_nu wedge(F0_1,...,F0_k).
```

Its coordinate on any increasing `k`-tuple `Jprime` is
`epsilon p_nu det(F0[Jprime,:])`. The implementation emits those coordinates
lazily after validating the certificate. The vector is nonzero and
decomposable, and its projective class determines the unique limiting
`k`-plane. Every vector in that plane belongs to `ker K(a)` by continuity
of `K B_reg=0`.

The Pfaffian order and the frame's division count measure different things.
The retained four-dimensional fixture has three divisions at constant
operator rank and Pfaffian order zero. Multiplying its operator by
`(1+i)t^2` leaves its punctured kernel unchanged, gives Pfaffian order two,
and retains three divisions. Replacing `t` by `t^2` doubles these orders
without changing the limiting plane. Neither order alone determines a
frontier's topology.

## Exact real interval and partner geometry

The certificate retains the real square-free monic polynomial obtained from

```text
abs(p(t) det D(t))^2.
```

For real `t`, its nonzero locus certifies the rank lower bound from `p` and
the frame rank from `D`. The kernel frame supplies the matching rank upper
bound. Translating to `a`, removing the zero factor, and applying the
coefficient bound in the
[projector proof](annihilator_kernel_limits.md#complete-local-chart-and-an-explicit-radius)
gives an explicit positive rational punctured radius. The verifier recomputes
that polynomial and radius. It establishes the complete kernel throughout
both punctured sides, including arbitrarily close approaches to the endpoint.

The limit is a plane with its inherited Hermitian metric. Its projector is
`F0 (F0^* F0)^(-1) F0^*`. For a Cayley-Dickson path, the existing fixed real
isometry `Phi_inverse(conjugate(z))` transports that plane and its unit
sphere to the real annihilator. The replay compares the resulting real
projector with the independent full real-matrix algorithm.

The dimension-32 controls include four nullity-eight approaches to
`e1+e18`, and three nullity-four approaches with a shared derivative. The
three four-planes are pairwise orthogonal and sum to the twelve-dimensional
endpoint kernel. The dimension-64 control checks an ordinary embedding.
These controls certify their paths; they leave coverage of other approaches
as a separate obligation. Zero-endpoint matrix fixtures test the algebraic
algorithm and carry no normalized-base claim.

## An all-dimensional quotient construction from reachable planes

The following construction identifies the exact global object whose frontier
geometry remains to be computed. It is a written reduction, not a computed
cell complex.

Fix a Cayley-Dickson stage and let `B` be the unit sphere in its doubly-pure
coefficient space. Write `K(x)` for the certified complex skew matrix in
`C^m`. For each even rank `r<m`, let

```text
X_r={x in B : rank K(x)=r}, k=m-r,
G_r={(x,ker K(x)) : x in X_r},
Gamma_r=closure(G_r) in B x Gr_C(k,m).
```

The Grassmannian is compact. Its projector representation consists of
Hermitian matrices `P` with `P^2=P` and `tr(P)=k`. In that representation,
`G_r` has the additional equation `K(x)P=0` and the exact rank conditions
on `x`. Those equations give a unique `P` for every `x in X_r`. Real and
imaginary parts and the Pfaffian rank conditions make the graph
semialgebraic. Its closure remains semialgebraic and compact.

Pull the tautological bundle back to `Gamma_r` and take its unit sphere:

```text
E_r={(x,W,z) : (x,W) in Gamma_r, z in W, ||z||=1}.
```

The bundle exists even when `Gamma_r` has singular points. Define
`q_r(x,W,z)=(x,Phi_inverse(conjugate(z)))`.
Then `q_r(E_r)` is exactly the closure of the normalized pair incidence
whose base lies in `X_r`.

To prove the forward inclusion, choose `x_j in X_r` with
`(x_j,ker K(x_j))->(x,W)`. Orthogonal projectors converge in the Grassmannian.
For a unit `z in W`, projecting `z` onto `ker K(x_j)` and normalizing gives
unit vectors converging to `z`. These vectors produce pairs in the rank-r
incidence. For the reverse inclusion, start with a converging sequence of
pairs. Compactness of the Grassmannian supplies a convergent subsequence of
its kernel planes. The limit plane belongs to `Gamma_r`, and the limiting
unit vector belongs to that plane by continuity of its projector.

Every normalized zero-product pair lies over one of the finitely many
singular rank loci; the full pair space is closed. Thus the map from the
finite disjoint union of the `E_r` onto the full pair space is surjective.
The domain is compact and the pair space is Hausdorff. The induced quotient
is therefore a homeomorphism, with the explicit equivalence relation

```text
(x,W,z) ~ (xprime,Wprime,zprime)
    exactly when x=xprime and z=zprime.
```

Planes and rank labels can differ while representing the same pair. Keeping
that equivalence is essential: separate sphere bundles omit the gluing. The
construction holds at every stage. It proves an exact quotient description;
it supplies neither a classification of the `Gamma_r` nor computable cellular
boundary and cup-product maps by itself.

## Coverage still requires real closure decisions

In projector coordinates, membership of `(x,P)` in `Gamma_r` is the following
real-algebraic closure condition, together with the base and projector domain:

```text
for every epsilon>0 there exist xprime,Pprime such that
  xprime in X_r,
  Pprime=Pprime^*, Pprime^2=Pprime, tr(Pprime)=k,
  K(xprime)Pprime=0,
  ||xprime-x||^2 + ||Pprime-P||_F^2 < epsilon^2.
```

Evaluating only the endpoint equations admits every suitable subplane of the
exceptional kernel, including planes that may be unreachable from `X_r`.
Taking a complex algebraic closure can also introduce real points absent
from the real closure. The quantified condition preserves the needed
inequalities and rank domain.

Basu-Roy curve selection applies after that membership is established. Its
paths can require algebraic functions and a real branch selector; the theorem
does not say that every reachable plane has a path over `Q[t]`. The exact
polynomial API therefore supplies checkable witnesses and leading coordinates,
while arbitrary real coefficient coverage, algebraic-arc representation,
local links, complete quotient identifications, integral invariants and a
Rocq translation remain explicit work. The
[replay and proof obligations](../evidence/projective_kernel_limits/README.md)
retain those distinctions.
