# Review of an external candidate report: what survives

An external report proposed five "algorithmic candidates" drawn from this repository, a foundations text and a
settlement table for the Quandela Ascella processor, a candidate ledger, a list of "critical vulnerabilities", an
alignment of those candidates with the Cohen-Macaulay geometry of the A_5 exceptional fibers, and a monograph on the
twisted Cayley-Dickson tower. This record checks each claim against the repository's records, exact recomputation
and the primary literature, and keeps the statements that hold, in their corrected form. Read at commit `4ac9dc771`.
The reviewed text is not retained here; two files the monograph names as its sources exist nowhere in the workspace.

Evidence classes: **recomputed** means a script in this directory or a tracked test reproduces the value;
**record** means a tracked file holds it; **literature** means a registry lookup (arXiv, Crossref, OpenAlex) on
2026-11-09. `A5-NNN` is a row of
[the A_5 claim ledger](../../../evidence/a5-exceptional-fibers/ledger.tsv).

## Statements that survive

### Circuits for left multiplication by a two-term element

- The SELECT circuit is a sign diagonal, an X layer and a CX fan-out, exact on all 105 index pairs of the sedenions.
  The joint sign function has algebraic normal form degree exactly 4 on every pair and the per-unit sign degree 3
  (recomputed; `tests/gororoba_quantum/test_select_lcu_degree.py` pins both). At dimension 32 the degrees are 5
  and 4 on all 465 pairs, so no degree-4 statement extends to A_5.
- The 105 pairs are all index pairs. Zero divisors occupy 42 of them, with 168 signed rows.
- `DiagonalGate` synthesis of the sign diagonal costs 19 to 30 CZ and is the default; it saves 10 to 71 CZ against
  the direct Reed-Muller route, which is the only comparison the saving refers to.
- The Pauli decomposition has 28 words, 13 of full weight, a commuting cover of 7 settings and 5 CX in total with at
  most 2 per setting (recomputed).
- The ibm_fez figures match `results/hw_estimate/ibm_fez_record.json`, whose `qpu_executed` field is `false`: they
  are a noise-model simulation on that backend's calibration, never a device run.

### Kernel-nullity estimator and probes

- The bias identity of the kernel-map nullity estimator is exact (A5-228). The retained residuals are 0 in exact
  arithmetic and at most 7.1e-15 in double precision.
- The reading 12.65 with interval [11.87, 13.42] is the ibm_fez full-map reading. The sign-fixed share is "3 of 4
  blocks" for e1 + e18 and e17 - e2, 10 of 32 summed over eight operands, and 4 coset blocks per operand; 99.9 % of
  the 12.0151 reading follows from algebra alone.
- Two-term operands have nullity 0, 4, 8 or 12. The retained runs use 16,384 and 8,192 shots.
- Basis-state probes cannot separate the candidates named in the report; sixteen coherent probes do, with the stated
  values (2 against 4, 2 against 0; recomputed). Those sixteen are the aligned XOR pairs of e1 + e10 itself, so the
  probe set presupposes the candidate it identifies.
- The two negative results hold: the finite-field linear-system solver and the zero-divisor code give no advantage.
- The self-calibrating estimator and the probe search the report calls a new algorithm were added in `9ffad367c`
  and removed in `3be1b91c1`, whose message records that the calibration assumes alternating null signs. Calibrating
  the null operand against itself returns 0 by construction.

### Ascella

- The tracked [Ascella foundations document](../../../notes/quandela/ascella-foundations-and-architecture.md)
  already holds the publication values the report's settlement table corrects toward: 80 MHz pump, 92 ps lifetime,
  phonon-assisted excitation, a clear-box physical model, a Swabian time-to-digital converter with a 1 ns window,
  132 couplers and 126 phase shifters.
- `perceval.utils.NoiseModel` (perceval 1.3.1) has seven parameters and none for dark counts. At the retained rates
  a dark click mimics a missing photon at a relative size near 4e-5 (an inference from the retained rates), far
  below source distinguishability and loss.
- The service adapts the input state by adding routing permutations, as the provider guide and the supplement of
  Maring et al. state, so the report's "input permutation vulnerability" has no support.
- The corrections of the next section are the defects the review found in the tracked document itself.

### A_5 exceptional fibers

Every number in the report's Cohen-Macaulay table reproduces (`fibers/num.sing`, `fibers/xm.sing`), for the quadric
ring k[y]/K2. The fiber cone F(I) is a quotient of that ring and equals it only where a ledger row proves so: W8
(A5-008, A5-066); Iso after the review of A5-284; open for E8-bar -> VB (A5-016) and X- (A5-245); refuted as
Cohen-Macaulay for E8-bar -> N± (A5-014).

| Pair | k[y]/K2 at p = 32009 (recomputed) |
|---|---|
| E8-bar -> VB | dimension 4, degree 7, Cohen-Macaulay, numerator 1, 6; linear resolution with Betti numbers 21, 70, 105, 84, 35, 6, new to the record |
| Iso -> N- | dimension 5, degree 23, Cohen-Macaulay, numerator 1, 12, 10, prime |
| W8 -> N- | dimension 6, degree 50, Cohen-Macaulay, numerator 1, 18, 27, 4, radical with components of degree 20 and 30 |
| X- -> N- | dimension 4, degree 12, projective dimension 14, depth 1, numerator 1, 11, -3, 4, -1, non-reduced |
| E8-bar -> N- | dimension 5, degree 11, numerator 1, 16, -12, 10, -5, 1 (the report truncates it), minimal primes of projective dimension 4 and 3 |

- The criterion applied to F(I) is D'Cruz, Raghavan and Verma, "Cohen-Macaulay fiber cones", arXiv:math/0212119,
  Theorem 2.1 (literature).
- F(I) = k[y]/K2 holds exactly when the analytic spread and the multiplicity agree, whenever k[y]/K2 is unmixed;
  Cohen-Macaulayness is sufficient and stronger than needed. For Iso the reduction needs only K2 prime and K2 inside
  the relation ideal.
- The slice ladder ran on Iso and on the X controls. Each reading is consistent with dim E0 >= k for one form set at
  one prime and carries no genericity bound, because the degree of E0 is unbounded in the record. Its timings (486 s
  and 304 MB at k = 4) compare a finished computation with an unfinished one of another formulation.
- **New, recomputed here, awaiting independent review.** On the retained normalization of chart t7 of the point
  blowup of the E8-bar -> VB slice, G(h t) = h^2 G' exactly. On the exceptional divisor D (dimension 3), G'
  satisfies K2 and the degree-4 component's ideal P2 identically and none of the 7 generators of the degree-3
  component's ideal P1 (`fibers/vbpb.sing`, 2 s). At two F_p-points of D the span of G' and its derivatives along D
  has rank 4 (`fibers/vbrank.sing`, 3 s), so D maps dominantly onto the degree-4 component. That places the
  component in E0 at p = 32009 with no interpolation, the certificate the falsifier of A5-015 asks for.
- In that chart the base locus of I' on D is one closed point of degree 2 at the apex. The lengths measured there
  (`fibers/vbapex2.sing`: 6, 12, 20 at truncation 6, lower bounds) read as three generators per geometric point,
  which would leave the apex unable to supply a threefold. Charts t3 and t5 over the line t1 = t7 = 0 are not run,
  so A5-016 stays open.
- For E8-bar -> N-, the module sqrt(K2)/K2 has Hilbert function 5, 14, 30, 55, 91, 140, 204, 285 in degrees 1 to 8
  (sums of squares) and its annihilator has degree 2 with 16 linear forms in its radical (`fibers/m.sing`, 3 s):
  the nilpotents sit on a quadric threefold. This narrows the degree-6 question and does not answer it.

### Twisted tower

Recomputed with `cd_core` in exact arithmetic (`tower/check.py`, output in `tower/check.out`):

- The report's closed form N(D) = (D - 2)(D - 4)(D + 6)/2 satisfies N(2D) = 4 N(D) + 2 (D - 2)(D^2 + 2D + 18),
  an identity of polynomials; the recurrence the report prints beside it disagrees with it at every D checked. This
  record does not re-enumerate the count the closed form stands for beyond the sedenion figures below.
- The sedenions carry 168 ordered (84 unordered) disjoint index-pair pairs with equal XOR and sign character +1, and
  336 signed zero products, 48 in each of the seven XOR classes 9 to 15.
- e1 + e10 has a 4-dimensional left kernel and every kernel shift of conj(x)/2 inverts it on both sides, so it has
  infinitely many two-sided inverses.
- Floating-point addition is non-associative at u = 2^-52: (1 + u/2) + u/2 = 1 and 1 + (u/2 + u/2) = 1 + u.

The remaining tower claims repeat [the twisted-tower verification](../cd-tower/twisted-tower-verification.md).

## Statements that do not survive

| Report statement | Finding |
|---|---|
| Sign degree "exactly 3"; a degree-4 bound on A_5; a 5-qubit circuit for the four-term element | degree 4 on sedenions, 5 at dimension 32; the compiler takes two-term pairs only |
| ibm_fez "physical device" results; "8 to 15 %" contrast; the 249-CZ Householder figure | the record is a simulation; the other two appear in no record |
| "1.40 ± 0.08"; "< 8.9e-16"; nullity 10; [-0.12, +0.12]; 10^5 shots; M = 4096; "16 coset blocks"; "75 % tautology" | no record holds them; the recorded interval is [-0.47, 3.54] with t = 2.11 below 2.776 |
| Klein-group explanation of the sign-fixed blocks | an analogy; the repository's note states no result transfers |
| Ascella: 79 MHz, 150 ps, resonant pi-pulse, neural-network transpilation, FPGA taggers, "88.86 % HOM", Altair as an on-premise 2025-2026 system | absent from the publication and the retained records (retained HOM 87.48 % and 87.74 %) |
| arXiv:2307.03732, arXiv:2201.13328, Nat. Commun. 6, 7372 and 14, 8436 as cited | each resolves to an unrelated paper; the Pont paper is arXiv:2201.13333, the certified-randomness paper is PRX Quantum 5, 020348 |
| "Davis-Robbiano-Valla" criterion | no such criterion in the record; see above |
| "23.5 hours and 25.7 GB exhausted, 37,018 basis elements" | the run ended at a scheduled shutdown inside a 55 GB scope; 37,018 is a pair count (A5-071, A5-205) |
| The slice ladder "computes l(I) = 5 in seconds" and "resolves the fiber ring"; Corollary 3.1 (W8, saturation by m, Hilbert polynomial in 486 s) | 486 s on Iso, one dimension reading per run; the ladder never ran on W8 and computes no Hilbert polynomial |
| QRNG coefficients "certify independence between the primes" | the first form family uses the same integers at both primes; only the second family is independent |
| Orbit dimensions Iso 10, X± 9, V^a± 6 | 11, 10 and 7 ([strata record](../../../evidence/a5-strata-regularity/README.md)) |
| Recurrence 4 N(D) + (D - 2)(D - 4)(3D + 4); the rounding example at u = 2^-53; "24 directed zero products per box-kite" | corrected above |

## Corrections made with this record

- Ascella foundations document: live transmittance 5.25 % (was 5.5 % and 5.52 %); the coupler angle interval
  [1.4223, 1.4465] rad for R = 56.8 ± 0.6 %, stated apart from the live range [1.4204, 1.4739]; dark counts cited
  from the retained 2026-10-20 reading; the Taballione DOI `10.1088/2633-4356/ac168c` (the former one returns 404)
  and the journal reference of the 20-mode paper; Tzitrin et al. for static linear optics; 574 phase elements marked
  as the cloud's compiled circuit; the Barzaghi entry described by its authors' affiliation; the m output phases of
  the mesh decompositions; the 50:50 assumption of the visibility relation.
- A5-205, the arcs README, the run rulebook and the synthesis note: 37,018 is a pair count.
- A5-015 and A5-016: the chart t7 results above, statuses unchanged.

Left unverified in the Ascella document: the company roles, the dates of the on-premise systems, and the name in
"Troyansky, Tichy" (probably Troyansky and Tishby). Each needs a dated primary page.

## Which long computations the record makes unnecessary

The truncated-rank ladder certifies one Hilbert-function value per run, and 97 % of its largest run (E8-bar -> N-
degree 5: 118,427 s, 35.4 GiB) is one standard basis of the truncated slice ring, whose cost grows about 1.36 times
per order. Every all-degree statement in the record came from geometry instead: a Jacobian rank at an explicit
point of the point blowup bounds the fiber dimension from below exactly, in seconds. The decomposition behind it is
that E0 is the closure of the image of the exceptional divisor D off the base locus of I', together with the fiber
cones of I' at the base points; arcs in generic directions reach only the first piece.

| Cell | Decision route | Cost |
|---|---|---|
| W8 -> N-, every degree | proved (A5-066); the degree-6 rank at order 19 would test only the engine | none; withdrawal is the owner's decision |
| Iso -> N-, every degree | review of A5-284; then h_d = C(d+4, 4) + 12 C(d+3, 4) + 10 C(d+2, 4) | reviewer time |
| E8-bar -> VB support | base locus on charts t3 and t5 of the normalized point blowup | chart t7 took 2 s, 3 s and 111 s; the degree-10 rung it replaces extrapolates to about three days per prime |
| X same-sign support | the same decomposition; one rank of 4 on limits satisfying K2 decides | unmeasured, expected minutes |
| E8-bar -> N± degree 6 | membership of the 140 forms of sqrt(K2)/K2 in degree 6; the one cell where an exact rank or membership is the decision | about 230 GiB and two weeks by the ladder; a local chart on the quadric threefold is unmeasured |
| Characteristic-zero transfer | no fiber geometry replaces it | the order-22 check of X- timed out at 20,000 s on 4 cores (A5-290) |

## Replay

```sh
cd docs/archive/reviews/2026-11-10-external-candidates-review/fibers
for n in num m vbpb vbrank vbapex2 xm; do Singular -q < "$n.sing" > "$n.out"; done   # xm: 158 s, 0.5 GB
cd ../../../../.. && "$PYTHON" docs/archive/reviews/2026-11-10-external-candidates-review/tower/check.py
```

Singular 4.4.1, `dp` ordering, p = 32009. Not run: the apex length at truncation 10 (no result in 280 s), the chart
t3 base locus (no result in 290 s), every fiber statement at p = 32029, and a second reader for the chart t7
argument. The circuit, estimator and Ascella checks ran from scratch scripts that are not retained; their retained
anchors are the test, the ledger rows and the records cited above.
