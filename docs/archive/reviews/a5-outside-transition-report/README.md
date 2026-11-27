# Review of an outside report on A_5 and arXiv 2611.34924: what survives

An outside assistant's report, in three sections, (1) presents arXiv 2611.34924 as a benchmark for the A_5 work,
(2) lists candidate geometries around the A_5 zero-divisor variety, and (3) gives explicit paths between the
annihilator dimensions with limiting-kernel and first-order claims. This record checks each claim against the
repository's records, an exact recomputation and the paper's pages, and keeps the statements that hold in their
corrected form. Read at commit `aaae364a5`. The reviewed text is not retained here.

Evidence classes: **recomputed** means [the transition record](../../../evidence/a5-nullity-transitions/README.md)
reproduces the value (`scripts/a5_nullity_transitions.py --check`); **record** means a tracked file already holds it;
**page** means the PDF page of arXiv 2611.34924v1 was read; **elementary** means a one-line consequence of a recorded
identity. `A5-NNN` is a row of [the A_5 claim ledger](../../../evidence/a5-exceptional-fibers/ledger.tsv). An
independent implementation, written from the doubling formula alone with no repository import, reproduced the nine
recomputed claims (paths, real roots, limiting planes, Pfaffian, overlap law, commutant, Gram identity).

## Statements that survive

### The paper

- The acknowledgements state that several calculations and proofs were developed with GPT-6 Astra over many months,
  about 400 M tokens, on compute OpenAI provided (page 54).
- The abstract lists the results the report tabulates: a reduced phase space on intersecting null cones, a
  Hilbert-space representation whose algebra generates a type I factor, a finite graviton-pair amplitude, the
  Bekenstein-Hawking entropy with Sen's logarithmic coefficient, and the semiclassical Einstein equations to one
  loop (page 1). The abstract's verb is "we propose"; the theory covers vacuum gravity in four dimensions.
- The relation of the paper to A_5 is already decided (record): the paper holds no Cayley-Dickson, Clifford or
  zero-divisor structure and one abelian boost generator (A5-628, boundary); the bracket-preserving map of A5-620 is
  superseded; the same author's JT paper has an abelian boost group (A5-646); the Lorentzian cone with a fourfold
  kernel does not single out A_5 (A5-621, refuted).

### Paths and junctions (recomputed, A5-650 to A5-653)

- The three paths hold for every real parameter, with exceptional sets {0}, {1} and {-1, 1}.
- The junctions are e_1 + e_10 in W8, e_3 + e_20 in VB, and the nullity-16 ends in N- (s = 1) and N+ (s = -1).
- The two nullity-4 lines into e_1 + e_10 have constant kernel projectors on their punctured branches, orthogonal
  limiting 4-planes, and the sum of the planes is the kernel.
- The first-order compression has rank 4 at every junction.

### Identities

- Embedded doubling of the annihilator: A5-261, proved in Rocq for every level (record).
- V(Q) u V(G) with G = Q^2 - 4 Delta: A5-357; the section Q = a^2 + b^2 - 1, G = ((a + b)^2 - 1)((a - b)^2 - 1)
  holds (recomputed) on the complex point mu = i.
- m_n = 2^n - 4n + 4 and the table values 16, 44, 104, 228, 480: Biss, Dugger and Isaksen, Theorem 9.8 and
  Theorems 10.1 and 10.2, as [the source note](../../../notes/cayley_dickson_annihilator_sources.md) records.
- L_(a,t)^T L_(a,t) = L_(a,0)^T L_(a,0) + t^2 I: holds at levels 16, 32 and 64 (recomputed, A5-658); elementary from
  A5-622. Its consequence, that no element with a component on the doubling unit is a zero divisor, is the doubly
  pure statement of A5-356.
- The three-form <u, y v> is alternating at every level checked (recomputed, A5-658); elementary from
  <xy, z> = <y, conj(x) z>. The identity d omega = -3 phi is the exterior derivative of a constant-coefficient
  three-form restricted to the sphere, with a sign that depends on the orientation.
- Re Q(p + i q) = |p|^2 - |q|^2 has signature (15, 15): elementary from the definition of Q in A5-357.

## Statements corrected

| Report statement | Finding |
|---|---|
| gamma_3 reaches nullity 16 at s = 1 | also at s = -1, in the other orbit N+ (A5-651) |
| "two exact 4D sectors" at e_1 + e_10, with the direct projection between them zero, as an obstruction | the two planes are one antipodal pair of a family: limiting planes depend on the normal u x v of the direction, with trace(P P') = 2 (1 + cos angle); six planes come from two-term directions alone, and pairs at a right angle of normals overlap with trace 2 (A5-655) |
| each junction "identifies four additional annihilator directions" | the rank-4 compression identifies the four kernel directions that leave; the step 4 at W8 has a mechanism: the compression commutes with a quaternion algebra on the kernel (A5-654) |
| the section of Q and G is "an exact section" of the real variety | it is a section at the complex point mu = i; the real zero divisors of that plane need mu real |
| the paper has "essentially solved" quantum gravity | a preprint that proposes a quantization of vacuum gravity; no independent verification is on record |

## Statements with no support in the records

- A correspondence between the quadratic branch V(Q) and relativistic null geometry of the paper. The real slice of
  A5-612 carries a Lorentzian form; no map to the paper's null cones exists (A5-628).
- "Left and right annihilators coincide" is cited to a mirror site; the dimension statement follows from
  conj(xy) = conj(y) conj(x) on pure elements and A5-356, and no record here needs more.
- The geometry atlas (Carrollian, Krein, derived, tropical, diffeological and the rest) states no A_5 theorem. The
  items with a checkable A_5 statement are carried by
  [the transition program](../../../design/a5-nullity-transitions-program.md); the others are analogies.

## New in this review (recomputed; first recorded here)

At e_1 + e_10 the compression forms span a seven-dimensional pencil with a four-dimensional commutant and a
ten-dimensional Lie closure, and the Pfaffian of the pencil is 16 (Q^2 - 4 Delta) on (u, m, v) in R^3 + R + R^3
(A5-654). The real rank-4 directions are the cone over V_2(R^3), and limiting planes obey the overlap law on ten
rational directions (A5-655). The reading as a 2-sphere of quaternionic lines is a hypothesis (A5-656), and the
pencils at VB and N+- are open (A5-657). The prior-art search of
[the annihilator-variety note](../../../notes/topics/cd-annihilator-varieties-prior-art.md) found no work on limits
of annihilators or closures of strata in a Grassmannian; that bound is the scope of the novelty claim.
