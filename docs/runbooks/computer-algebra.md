# Computer algebra foundations: formulation, orderings and local invariants

These rules hold for every Singular, msolve or Macaulay2 computation in the repository. They decide how a question is
posed before any flag is chosen; [compute-flags.md](compute-flags.md) then reviews the launch line, and the
[run rulebook](run-rulebook.md) records each long run's own choices and the reason for every departure from these
foundations.

## Orderings and local invariants

Exact replays compute in global monomial orderings (`dp`, `lp`). A local
invariant at a point p, such as a tangent cone, multiplicity or singularity
type, comes from the deformation to the normal cone: translate p to 0,
substitute t -> h t, take `sat(I, h)` (an ideal in Singular 4.4, not a list)
and set h = 0. The reduced germ at p is the intersection of the `minAssGTZ`
primes through p, with no prior `radical()`. Local orderings (`ds`,
`tangentcone`) on the A_5 strata ran past an hour at tens of GiB on the shared
host, while the global route takes seconds
([a5-strata-regularity](../evidence/a5-strata-regularity/README.md)).

## Pose the cheapest question that decides the claim

A whole-ideal decomposition is the most expensive way to learn a structural fact, and often the only one that stalls.
Before launching `radical`, `minAssChar`, `minAssGTZ`, `facstd` or a global saturation, ask whether a cheaper
computation decides the same claim:

| Claim | Decisive cheap computation | Measured gain |
|---|---|---|
| a homogeneous ideal K is radical | K : y_i = K for a coordinate y_i plus one reduced chart K + (y_i - 1) (k[y]/K embeds in a Laurent ring over the chart) | Iso K2: 1-5 s against a global `radical` stopped after 13.85 h |
| k[y]/K is Cohen-Macaulay | length of k[y]/(K + a general linear forms) equal to the degree | seconds; no resolution |
| K radical and equidimensional, its F_p-components and their degrees | general linear sections cut to deg K points (vdim = deg, squarefree eliminant of a separating form); Frobenius orbits refine the component degrees; common subset sums across sections bound them | Iso and W8 K2: under 2 s per section against `minAssChar` past 41,000 s |
| a component is geometrically irreducible | a section-point orbit of size 1 on it (or an orbit size prime to the count of conjugates) | free once the sections exist |
| a variety lies in a fiber or a closure | an explicit family (arcs, a parametrization) with symbolic membership and a Jacobian rank at a point | the W8 V(P) certificate in seconds |
| the dimension of a blowup fiber | one affine chart of the blowup, saturated, then cut by the base point | the Iso chart test; a decomposition of the Rees algebra stalled |

Each cheap route states its premise (Cohen-Macaulay, equidimensional, a perfect field) and a log line showing that a
generic choice was generic (vdim equal to the degree, a squarefree eliminant). Random linear forms take their
coefficients from the ANU QRNG with the draw file and index of every coefficient recorded, so a section regenerates
byte for byte from its ledger.

## Symbolic or numeric

A symbolic computation whose parameters multiply (power series with many coefficient variables, expansions to high
order) can grow by orders of magnitude between neighbouring sizes: the symbolic L0-arc families ran in seconds at one
order and reached 17 GB at the next. Search numerically first (exact arithmetic over F_p with dual numbers for
Jacobians, in Python with numpy or python-flint), then certify the one family that matters symbolically with the
fewest parameters. A rank at one point bounds the generic rank from below, and the symbolic run certifies that the
lower coefficients vanish identically.

## Saturation and elimination

- Add every relation the saturation implies before saturating: in a blowup chart a0 z_i = G_i with a0 = l0(G), the
  relation l0(z) - 1 lies in the saturation, and adding it up front removes a variable without changing the result.
- `sat(I, f)` (iterated quotients) and the Rabinowitsch elimination `eliminate(I + (1 - w f), w)` reach the same
  ideal by different algorithms; on a long run launch both as a portfolio, let the first to finish decide and the
  second confirm.
- Slice only after saturating. Linear forms in the original coordinates added before a saturation compute a strict
  transform and lose the exceptional fiber.

## Singular pitfalls that cost a run

- `ord(p)` under a global ordering returns the leading degree, not the lowest one; find the lowest degree with a loop
  over `jet(p, k)`.
- `homog(I)` tests each generator on its own.
- `product` needs `general.lib`, `concat` needs `matrix.lib`, `sat` and `eliminate` need `elim.lib`; a missing library
  aborts the statement and every later line that uses its result.
- `sat` returns an ideal in 4.4 and a list in older versions; accept both
  (`def SS = sat(...); if (typeof(SS) == "list") { ... }`).
- A K2 relation file uses the generator order of the run that wrote it; compare that list with the header's G before
  evaluating K2 at G (the Iso runs differ from the header by the sign of G_6..G_15).
- Singular reads standard input whenever it is not a terminal; start it with `< /dev/null`
  ([compute-flags.md](compute-flags.md#why-the-review-exists)).

## Records

Write each result the moment it exists, to a file named by fiber, prime and method, so that concurrent runs never
share an output name and a timeout keeps everything before the stall. Retain every log a README cites: the global
gitignore excludes `*.log` and `*.out`, so a new evidence directory is staged with `git add -f` after
`git ls-files --others --ignored --exclude-standard DIR` lists what was held back.
