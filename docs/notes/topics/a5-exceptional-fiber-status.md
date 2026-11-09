# A_5 exceptional fibers: goal, status by layer, and what the 2026-11-09 results change

This page walks through what the A_5 fiber program is for, where each layer stands by count of the claim ledger
([`ledger.tsv`](../../evidence/a5-exceptional-fibers/ledger.tsv), 269 rows after the ledger audit and the sweep of session-local findings of [ledger-audit](../../archive/reviews/ledger-audit/README.md)), and
what the results of 2026-11-09 imply. The measurements and methods live in
[a5-exceptional-fiber-findings.md](a5-exceptional-fiber-findings.md); this page counts and interprets them.

## The goal

A_5 here is the 32-dimensional Cayley-Dickson algebra (the pathions), not the alternating group. Its zero divisors
form strata by nullity, the dimension of the kernel of left multiplication. The open registry claim
`dimension32-global-topology` asks how those strata are glued: as a point of a nullity-8 orbit closure Y approaches a
smaller orbit Z, which 8-dimensional kernels arise as limits. The program answers in four layers:

1. **Directions of approach, degree by degree.** The exceptional fiber of the blowup of Y along the kernel-coordinate
   ideal I at a point of Z has coordinate ring F(I); its Hilbert function h_d = dim_k(I^d / m I^d) counts the independent degree-d
   classes of F(I), the degree-d forms modulo the relations among the limiting directions (h_1 is the number of
   independent generators of I). Each h_d is certified when a truncated-rank lower bound meets the upper
   bound HF(k[y]/K2, d) from the quadric relations K2.
2. **Directions of approach, all degrees at once.** F(I) = k[y]/K2 for a fiber says K2 is the whole story in every
   degree; it is proved by a structural argument (the C30 argument for W8), not by more ranks.
3. **Characteristic 0.** Every certificate is a statement over F_32009 or F_32029; the claim over Q(i) needs a
   specialization argument.
4. **The attaching datum itself.** The limiting kernel 8-planes and the real arcs that realize them (ledger A5-029).
   G is the Pfaffian kernel-coordinate ideal, so Proj F(I) is the complex kernel limit set in Pfaffian coordinates
   (`working/decision-record.md`, section 1), given the holomorphic-kernel identification, which the kernel-attachments
   record establishes on its retained samples only (row 2h); layer 4 adds the two-sided real certificate and the
   attaching maps that `dimension32-global-topology` consumes ([a5-char0-and-kernel-limits.md](a5-char0-and-kernel-limits.md)).

## Status by layer (ledger count, 2026-11-09)

Ledger totals: 90 certified, 39 proved, 58 survives, 46 refuted, 9 superseded, 7 rejected, 15 open, 5 boundary.

| Layer | Count | Share | Open items |
|---|---|---|---|
| Per-degree h_d, degrees 1 to 6, sixteen fiber-and-prime rows (X+, X-, Iso, W8 -> N+-, E8-bar -> N+-, E8-bar -> VB at both primes) | 92 of 96 cells certified or proved (W8 degree 6 by C30) | 96 percent | E8-bar -> N+- degree 6 at both primes (A5-083, A5-089, A5-095, A5-101): 1526 <= h_6 <= 1666 |
| All-degree F(I) = k[y]/K2, five fiber classes with a claim (A5-005 VB, A5-006 X+ -> N+ and X- -> N-, A5-007 Iso, A5-008 W8, A5-009 E8-bar -> N+-) | 1 proved (W8, A5-066); 4 survive every measured degree | 20 percent | Iso local route (A5-067); E8-bar membership on sqrt(K2)/K2; the VB degree-3 component (A5-016); X+ -> N+ has no route (its K2 ring is not Cohen-Macaulay, A5-019) |
| Characteristic 0 | the kernel-attachments track proves its completed fibers over Q(i) (14 incidences of nullity 8 to 12 and eight nullity-16 rows); for the ten fiber-track pairs the germ ideal J reduces well at both primes (A5-247); the opposite-sign X fibers are proved over Q(i) in every degree, F(I) = Q(i)[y1, y2, y3] (A5-270); J + m^N reduces well for X- -> N- at N = 4, 8, 11, 15 (A5-249); the degree-2 relations over Q(i) are running (A5-248) | partial | the relations q(G) in J + m I^2 over Q(i) and good reduction of J + m^N; then each certified h_d holds over Q(i) ([a5-char0-and-kernel-limits.md](a5-char0-and-kernel-limits.md)) |
| Attaching datum: kernel-plane limits along the arcs | complex limit sets computed for 14 incidences of nullity 8 to 12 and eight nullity-16 rows (kernel-attachments track) and for W8 -> N+- modulo p (V(K2) = C20 cup C30, A5-066); A5-036 refuted; no two-sided real certificate for any incidence | complex part started; real part not started | the exact Plucker limit along each certified arc family (A5-029) and the real curve-selection certificate |

Ledger row A5-006 named the 3-generator pair X+ -> N-, X- -> N+ while its basis (h_4 = 240) belongs to the
15-generator pair X+ -> N+, X- -> N-; this change corrects the row. The counts replace an earlier estimate of 75 to 85 percent for the first layer, which was low: only E8-bar degree 6
remains there. Reproduce the counts with
`"$PYTHON" -c "import csv,collections; print(collections.Counter(r['status'] for r in csv.DictReader(open('docs/evidence/a5-exceptional-fibers/ledger.tsv'), delimiter='\t')))"`.

## What the 2026-11-09 results change

- **E8-bar -> VB degree 6 certified at both primes** (r_20 = r_19 = 420, blocks 138/98/92/92, so the closing order is at most 19; `vb-d6-laptop/`). VB's first
  layer is complete through degree 6, and A5-005 (VB all-degree) survives one more degree. It does not prove A5-005:
  VB's all-degree question is whether its fiber contains the degree-3 component (A5-016).
- **The t7 = 1 chart and its arcs** (`working/build/arc/`). The chart ideal is prime of dimension 4: it is radical, and `minAssChar` returns one minimal prime equal to it (`chart_t7_primes.sing`, 115 s and 220 MiB on OCI A1). Its normalization is one
  12-variable ring under the default method; 34 order-1
  arcs land in the degree-4 component and none in the degree-3 component, as chart t1 predicted. A5-016 narrows to
  arcs with jet parameters on the plane t1 = 0 and at the apex t1 = t3 = t5 = 0, where G vanishes through s^13.
- **E8-bar degree 6 has one route.** K2 is not radical for E8-bar, so a plane-family proof only reproduces the lower
  bound 1526; h_6 is decided by membership of the 140 forms of sqrt(K2)_6 / K2_6 in the fiber relations, piloted on
  the 91 forms of degree 5, where the answer is known. This is the only open cell of the first layer.
- **The wall is the Singular export on three fibers, the closure on the rest** (A5-246). The export holds 96 to 99
  percent of the wall time of E8-bar degree 5 and VB degree 6 and 80 percent of X- degree 6; the closure holds 53 to 74
  percent on Iso degree 6, W8 degree 5 and E8-bar degree 4. The GPU echelon step (equal to flint on every tested
  shape, 20 to 33 times faster at 4,000 x 20,000) and engine v12 shorten W8 and Iso, whose closure dominates; their use
  for the goal is Iso degree 7 (the A5-007 falsifier) and the membership linear algebra.
- **The Cayley-Dickson tower enters through symmetry, not dimension counts**
  ([cd-tower](../../archive/reviews/cd-tower/report.md), one agent, no outside review). The four character blocks are
  the stabilizer of the base point among the sign automorphisms e_a -> +-e_a; the stabilizer also carries a torus and
  an SL(2) fixing a quaternion subalgebra (hypothesis: floating point on fixed, unregistered seeds whose scripts were
  not retained, pending a seeded, retained replay). An exact torus would allow a weighted standard basis, the
  one lever found against the export wall. Icosahedral, McKay and E8 readings are refuted.

## What moves each layer next

| Layer | Next computation | Host | Decides |
|---|---|---|---|
| 1 | E8-bar membership pilot on sqrt(K2)_5 / K2_5, then the 140 degree-6 forms | laptop | A5-083/089/095/101 |
| 2 | Order-2 arcs on t1 = 0 and at the apex of the VB blowup (a positive result only: a failed search leaves A5-016 open, and a negative decision needs a degree-7 fiber relation outside P1) | build host (Sage), minutes per chart | A5-016, then A5-005 |
| 2 | Iso local route by plane family on the point blowup | OCI A1 or laptop | A5-067, then A5-007 |
| 2 | Exact torus over Q, weighted standard basis of J | laptop CPU, OCI | the export wall for E8-bar and X- degree 7 |
| 3 | Degree-2 K2 over Q(i) by rational reconstruction from both primes, exact membership | laptop | the first characteristic-0 statement |
| 4 | Kernel-plane limits along the certified arc families (W8, Iso, X, E8-bar -> N+-, VB degree-4 component, whose family is an interpolant of numerical Hensel lifts, A5-015) | laptop | A5-029, the attaching datum |

Layer 4's real certificate has had no computation yet, and it is the part the registry claim needs; the arc families it runs along are
already certified for most pairs, so it can start without waiting for layers 2 and 3.
