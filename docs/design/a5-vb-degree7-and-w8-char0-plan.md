# E8-bar -> VB degree 7 and W8 -> N- in characteristic 0: decomposition and sizing

Two items from the A_5 exceptional-fiber program run past the owner's 3-hour run cap: the degree-7 test of the
E8-bar -> VB ladder laws (ledger A5-260, A5-269, stalled as A5-279) and the transfer of the W8 -> N- Hilbert function to
characteristic 0 over Q(i). This document splits each into pieces that fit under the cap and pieces that need a sized
case. For every piece it states the conjecture, the falsifier, the measured cost behind the estimate and the decision
the piece feeds. The ledger (`docs/evidence/a5-exceptional-fibers/ledger.tsv`) records statuses, and this document
holds the plan.

## E8-bar -> VB degree 7

### Preregistered predictions

The rows below are written before any degree-7 cell runs, from A5-260 (closing order 3d + 1) and A5-269 (last jump
2d + 1 on character blocks 0 and 1, block 0 taking d and block 1 taking d + 1 at odd d):

- the target is HF(k[y]/K2, 7) = 624 (A5-279);
- r_22 = 624, so the ladder closes at N = 22;
- r_21 = 609, so the last jump is 15 = 2 * 7 + 1;
- the r_21 -> r_22 block split is 7 / 8 / 0 / 0, with blocks 2 and 3 already at their K2 counts at N = 21.

Each prediction has its own falsifier. r_21 = 624 refutes closure at exactly 22. r_21 other than 609 refutes the jump
law. A split other than 7 / 8 / 0 / 0 refutes the parity rule. r_22 below 624 refutes closure at 3d + 1. N = 21 alone
can falsify the first three predictions, and it costs less than N = 22.

### Where the time goes (measured)

The engine-v11 records of degrees 5 and 6 (`docs/evidence/a5-exceptional-fibers/vb-d6-laptop/*.json`, field
`export.computed_seconds`) put the cost of a cell into one Singular call, `std(J + maxideal(N))` (the `STD_SCRIPT` of
`replay/engine/fiber_rank_v11.py`). The multiplication tables and the generator reduction take under 63 s at every N:

| N | std(J + m^N), p = 32009 | std, p = 32029 | tables and generators |
|---|---|---|---|
| 15 | 420.5 s | 426.7 s | 7 to 11 s |
| 16 | 676.4 s | (not run) | 11 s |
| 18 | 2,527.1 s | 2,655.5 s | 23 to 25 s |
| 19 | 7,313.3 s | 7,095.9 s | 35 s |
| 20 | 10,619.8 s | 10,493.3 s | 59 to 63 s |

The step ratios are 1.61 (15 to 16), 1.93 per step on average (16 to 18), 2.90 (18 to 19) and 1.45 (19 to 20). They
support no clean fit. Bracketing each step from N = 20 by the smallest and largest observed ratio puts std at N = 21
in 15,400 to 30,800 s and at N = 22 in 22,300 to 89,300 s (6 to 25 h). This range is an extrapolation, not a
measurement. A measured N = 21 cell narrows it. Peak memory stays small: 1.71 GiB at N = 20.

The standard basis of J alone in dp has 17 elements and takes under 1 ms (`vb-export-levers/vb-n15-incremental.log`).
The whole cost therefore sits in adding m^N. In dp the leading term of each element of J is its highest-degree term,
so truncation at degree N releases the lower-order parts as new elements, and the work tracks the local structure at
the origin.

### Levers (each a global-ordering computation, per `docs/runbooks/computer-algebra.md`)

The probes in `docs/evidence/a5-exceptional-fibers/vb-export-levers/` time one variant of the std call at a time
against the baseline, at N = 15 and 16, p = 32009. Each variant's kbase must equal the baseline's. The engine's export
identity pins the dp standard monomials, so an admitted lever changes no record. A lever that changes the Singular
script still lands as a successor engine, never as an edit to v11, because the v11 digest binds the retained records.

The probes ran on the build host on 2026-11-09, five Singular processes at once, so the baseline (562 s) runs slower
than the engine record (420 s); the ratios compare runs under the same load.

| variant | N = 15 | N = 16 | kbase equal |
|---|---|---|---|
| baseline `std`, redSB | 562.2 s | running | reference (sha256 6c1172203b181a95...) |
| `std` without tail reduction | 762.8 s (refuted: slower) | running | equal |
| `slimgb` | 301.0 s (1.87x) | running | equal |
| `std(std(J), maxideal(N))` | running | running | pending |

Fitting N = 22 under the cap means std at most about 10,000 s, against the 22,300 to 89,300 s range. A lever must
therefore be at least 2.2 to 9 times faster at N = 18, where it is testable in under an hour.

Further levers, not yet run:

- **Weighted ordering (A5-258, task 115).** The weights come from the exact torus in the Klein centralizer, which is
  not yet computed. Falsifier: J is not weight-homogeneous for any positive weight in the slice.
- **Linear algebra on k[t]/m^N.** (J + m^N)/m^N is the span of t^a f_i truncated below degree N. Its row echelon
  form over F_p gives the quotient and the multiplication tables without a Buchberger run. At N = 22 there are
  C(29, 8) = 4,292,145 columns, so the cost depends on fill-in of a sparse elimination that is unmeasured. Cheapest
  test: N = 15 against the 420 s baseline, comparing the quotient dimension and the table ranks.
- **Local ordering with a Noether bound** (`ds` with highcorner m^N). This is the natural algorithm for an Artinian
  local quotient, but the repository canon admits only global orderings for exact replays, so it needs the owner's
  exception.

### Decision for the owner

Two options:

- **One N = 21 cell at p = 32009.** Estimated 15,400 to 30,800 s at about 2 GiB, one core. It tests three of the four
  predictions.
- **Wait for a lever.** A lever that wins by 2.2 to 9 times at N = 18 brings N = 22 under the cap.

Both N = 22 cells (one per prime) without a lever take 6 to 25 h each and need a sized case.

## W8 -> N- in characteristic 0

### What the transfer needs

The proposition in `docs/notes/topics/a5-char0-and-kernel-limits.md` transfers one certified h_d to Q(i) under
three checks. For W8 -> N- the certified degrees are d = 1 to 5 at both primes (A5-138 to A5-142, A5-144 to A5-148):

| check | W8 -> N- status |
|---|---|
| 1. good reduction of J and G | survives (A5-247; J has one generator, G has 24) |
| 3. good reduction of J + m^N at N = 3d + 1 | survives at N = 4, 7, 10, 13 (A5-277); N = 16 (d = 5) @W16@ |
| 2. degree-2 relations over Q(i), reducing onto K2 | not run; 300 products, 144 relations (h_2 = 156) |

Radicality of K2 does not enter the per-degree proposition. The 24,548 s global radical test belongs only to the
all-degree statement (h_6 = 8,624 and beyond: A5-143, A5-149, proved modulo p by A5-066, which uses A5-061 radical,
A5-062 components and A5-010 Cohen-Macaulay).

### Check 2: the cofactor route, piloted on X- -> N-

The direct Q(i) computation stalled at the 3-hour cap on X- (A5-248), and W8's modular degree-2 receipt alone took
5,619 s at 6.7 GB, so W8 check 2 runs only after the X- pilot finishes end to end. The pilot has three stages:

1. **Lift modulo two split primes** (`docs/evidence/a5-char0-transfer/cofactors/`). At p = 32009 the lift took
   1,565 s at 16.5 GB with 51,611 cofactor terms (A5-248). At 32029: @L2@.
2. **Canonicality.** Reconstruction needs the two primes' cofactor matrices to have the same support. If they
   differ, lift's output is not the image of one Q(i) computation, and the route switches to a degree-bounded linear
   system whose reduced row echelon solution is canonical and reconstructs by the Chinese remainder theorem.
   Result: @CAN@.
3. **Identity over Q(i).** Check q(G) = sum a_k J_k + sum b x P term by term. The single matrix product timed out
   modulo p at 30 minutes, so the check runs per relation (69 for X-) through `parallel.py`. Alternatively the
   identity is checked modulo enough further split primes for their product to exceed twice the coefficient bound of
   the identity polynomial. That check is exact, because an integer of absolute value below B that vanishes modulo a
   modulus above 2B is zero.

### The all-degree statement (hypothesis)

The all-degree statement over Q(i) may avoid a second radical test. Suppose the reduced Gröbner basis of the Q(i)
relation ideal K2 (from check 2) is p-integral and reduces to that of K2 mod p. Then k[y]/K2 is flat over the local
ring R of the proposition, and Proj k[y]/K2 is proper over it. Geometric reducedness and the Cohen-Macaulay property
of fibers are open on the base for a proper flat morphism (EGA IV_3, 12.2.4 and 12.1.6), so both pass from the
special fiber, where A5-061 and A5-010 prove them, to the generic fiber. The irreducible components of the generic
fiber specialize to effective cycles whose degrees sum to 50. The only splittings are therefore one component of
degree 50 or components of degrees 20 and 30.

Status: hypothesis, confidence medium. It rests on the cited openness theorems applying to this family, which an
audit should check against the source. Falsifier: the Q(i) Gröbner basis of K2 has a p in a denominator or a
different leading ideal. Separately, the A5-066 fiber-containment argument (a blowup-chart computation modulo p) needs
its own transfer, which no record yet sizes.

### W8 decision for the owner

W8 per-degree transfer for d = 1 to 5 needs check 2 only, once the X- pilot shows the cofactor route works. Its cost
is sized from the pilot's per-prime lift time scaled by the W8 receipt ratio (5,619 s against X-'s 18 s mod-p
relation step). The all-degree statement needs the flatness check above and a sized transfer of A5-066.

## Placement and concurrency

`docs/runbooks/classical-compute-pool.md` holds each substrate's limits, and the infrastructure chart's job memory
budgets (0.84 x GPU memory + 0.82 x RAM per machine) bound concurrent jobs. Every Kaggle session and every paid VM
needs an approved written case, and every job stops at 3 h unless the owner approves a sized case. The table
assigns each open computation by its measured bottleneck:

| computation | bottleneck (measured) | placement | runs beside |
|---|---|---|---|
| VB std(J + m^N) lever probes at N = 15, 16, 18 | one single-threaded Singular std, under 1 GiB | build host (38.6 GiB budget) or the RTX 4090 laptop (52.5 GB) | everything below; four probes at once |
| VB N = 21 cell, one prime | std 15,400 to 30,800 s, about 2 GiB, one core | the RTX 4090 laptop, past the cap only by owner case; or a Kaggle CPU session (12 h limit, 30 GB, passagemath Singular 4.4.1) | the other prime's cell on a second Kaggle CPU session (5 at once) |
| VB N = 22 cells, both primes | std 22,300 to 89,300 s (extrapolated) | Kaggle CPU only if under 12 h; otherwise an Azure FX4mds_v2 (84 GB, Singular slower than the laptop by 1.6x per the placement memory) under a case | the two primes on two sessions or VMs |
| GPU work for VB | none: tables, products and closure are under 63 s | none; the GPU (engine v12) pays only where closure dominates | |
| X- cofactor lift, per prime | lift 1,565 s at 16.5 GB | build host, one prime at a time (two at once exceed 38.6 GiB) | the probes and the W8 truncation check |
| X- identity check over Q(i), per relation | polynomial products, unmeasured | build host through `parallel.py`; Kaggle CPU if one relation exceeds the cap | |
| W8 check 3 at N = 16 | Q(i) std, 114 s at N = 13 | build host | everything |
| W8 check 2 (cofactors) | scale of the X- pilot times the W8 receipt ratio, unmeasured | sized after the X- pilot | |
| W8 degree 6 at N = 19 (task 113, not needed for F(I) by A5-066) | closure 14 to 19 h CPU, L = 103 GiB dense under v11 | GPU: engine v12 on the RTX 4090 laptop once L streams by degree (efficiency lever 1 and the streaming idea), Kaggle T4 x2 with CPU fallback for the export; an Azure VM otherwise | |
| Exact torus and weighted std (task 115) | symbolic linear algebra, small | build host | everything |

The Singular std behind the VB ladder runs on one core and has no GPU form, so GPU instances buy nothing for VB
degree 7. They pay for the dense closure of W8 and Iso at degree 6 and above. Google Cloud has no row in the compute
pool, and AWS's free plan offers 8 GiB machines, below every heavy job here.
