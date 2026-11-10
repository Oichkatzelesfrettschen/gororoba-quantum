# Iso -> N- support certificate (task 56): trace of the failed chart saturations and the cheapest decisive route

Question. Does the fiber E0 = Proj F(I)_red of the blowup of I = (G_1..G_17) on V(J) over the origin equal V(K2) for
Iso -> N- (K2 prime, degree 23, projective dimension 4)? Equivalent forms: analytic spread l(I) = 5; F(I) = k[y]/K2 in
every degree. Marks: proved, computed (run or recomputed for this review), measured (a retained log or transcript), hypothesis.
Paths are relative to `docs/evidence/a5-exceptional-fibers/` (EF) and `structure/arcs-iso-w8/` (AI). Scratch
computations of this review (labeled "scratch") are not retained and use non-QRNG points; they scope, never certify.

## 1. The 8-hour limit

- [measured] The limit is the argument `timeout 28800` in `AI/chart-runs/azure/jobs.sh:12`; the table row "Timeout |
  8 h per process | owner-approved cost bound (8 h x $0.547/h)" is `AI/chart-runs/azure/flags.md:19`; the run rulebook
  restates it with "auto-shutdown start + 9 h (past the 8 h job limit)" (`docs/runbooks/run-rulebook.md:41,46`).
- [measured] `git log -S'28800'`: first in git is 2e4689b74 (2026-11-05 18:23 -0800, rulebook), then 102d92acd /
  cc40016cc (2026-11-06 01:45, outcome record) and 9243e9c24 / 21001701d (01:48, `jobs.sh` and `flags.md` retained).
  The run started 2026-11-06T01:40:12Z (first `mem.log` line) = 17:40 -0800, so the commit carrying the rulebook text
  post-dates the launch by 43 minutes and the scripts reached git after the run ended (09:40Z). Author eirikr in all.
- [measured] Who decided and when: the quantum session transcript
  (`~/.claude/projects/-home-eirikr-Projects-gororoba-workspace-gororoba-quantum/8591a309-47e6-4168-bc23-a3a08c784490.jsonl`,
  lines 59840-59841). At 2026-11-06T01:10:38Z the operator put an AskUserQuestion case: FX4mds_v2 in westus3, both
  primes in parallel, "8 h timeout (<= ~$4.40)", option "Approve FX4, <= 8 h (Recommended)"; the same text records
  "p=32029 died at 5 GB after 57 min, p=32009 is at 6 GB and climbing". At 01:33:51Z the owner answered "Approve FX4"
  and asked for a Singular flag audit, saved results on a crash, and a shutdown instead of a teardown. The operator
  wrote `jobs.sh` at 01:37:11Z. The 8 h figure is the operator's own proposal, priced at 8 x $0.547/h = $4.38, and the
  case contains no runtime model for the saturation: it is a cost cap the owner approved, not a measured need.
- [measured] It was not a physical constraint. The sat processes held 15.8 and 15.1 GB of 84 GB at the stop
  (`azure/chart-iso-p32009-sat.err`: max RSS 15,807,608 KB; p32029: 15,148,544 KB) and kept growing; the same family of
  runs went to 21 h 41 min one day later (`fx4-w8p2/iso.sh:10`, `timeout 79200`, plus a 24 h guard,
  `fx4-w8p2/guard.sh:6`) and ended only at the VM's daily DevTest Labs shutdown, 2026-11-07T20:59:54Z
  (`fx4-w8p2/rss.txt` last line; `AI/README.md:74`).
- [measured] The "52 GB watchdog" is a shared-pool rule, not a limit of the elimination: `jobs.sh:20` kills the largest
  Singular when MemAvailable < 4,000,000 kB. At the p32009 stop (09:09:26Z, `azure/events`) the two sat processes held
  13.8 + 14.0 GB (`mem.log`, 09:10 row), so the elimination had about 84 - 27.8 - 4 = 52 GB. At the p32029 stop
  (05:01:21Z) the largest process was the p32029 elimination at 29.7 GB beside 28.6 GB (p32009 elimination) and 21 GB
  (two sat). [hypothesis] With the siblings gone the p32009 elimination could have run to roughly 78 GB; whether it
  finishes is unknown.
- Owner rulings since: the 3-hour cap (2026-11-09 morning) was superseded the same day by "well-scoped long runs are
  approved; Kaggle under 12 h is free; paid cloud keeps its written-case rule" (workspace memory
  `feedback-long-runs-approved`). The 8 h bound therefore binds nothing now; a paid-cloud rerun needs a written case.

## 2. How far each run got

Every run died inside the first standard basis of the chart ideal C = (J, a0 z_i - G_i, l0(z) - 1), before any
saturation quotient or elimination step ended. Evidence: each log opens with a single `[65535:7]` prot header (one std
stage), contains no RESULT line, and `write` calls for `chart-sat-*`, `chart-std-*`, `chart-fiber-*` sit after the std
(`chart-iso-p32009-sat.sing`); [measured] none of those files exists in the repository or in the retention commit
21001701d (20 files, logs only), and `find` to depth 4 under the laptop home finds none.

Reading the prot trace. [computed] The number in parentheses after `s` is the length of the pair list, not the basis
size: `option(prot); std` on a 3-generator test ideal printed a maximum of (6) for a 12-element basis. The ledger and
README wording "standard bases of 20,000-37,000 elements" (ledger.tsv:71, `AI/README.md:78`, run-rulebook.md:61,
compute-flags.md:284) should
read "pair lists of 20,000-38,000 entries". Degree markers: sat reached degree 16 (19,296 pairs at the marker).

| Run (host, formulation, prime) | Wall at stop | Peak RSS | Last trace | Ended by |
|---|---|---|---|---|
| FX4, dense chart, sat, 32009 | 8:00:00 | 15.81 GB | degree 16, 20,508 pairs | `timeout` (exit 124) |
| FX4, dense chart, sat, 32029 | 8:00:00 | 15.15 GB | degree 16, 20,103 pairs | `timeout` (exit 124) |
| FX4, dense chart, Rabinowitsch eliminate, 32009 | 7:29:21 | 52.06 GB | 37,422 pairs | watchdog, 09:09Z |
| FX4, dense chart, Rabinowitsch eliminate, 32029 | 3:21:15 | 29.73 GB | 26,755 pairs | watchdog, 05:01Z |
| FX4, sliced chart (4 extra z-forms), std(C), 32009 | 21:41 to shutdown at 23.5 h | 25.7 GB | degree 23, 38,251 pairs | VM auto-shutdown 2026-11-07T21:00Z |
| lab-a1, dense chart, sat, 32029 | 57:20 | 5.22 GB | no trace line | `prlimit --as` 5 GB |
| lab-a1, dense chart, sat, 32009 | 3:25:48 | 10.47 GB | no trace line | `prlimit --as` 10 GB |
| lab-a1, sliced and slice-junk chart, 32009 | 3:14 and 3:16 | 9.42 GB | 18,425 pairs | `prlimit --as` |
| lab-a1, coordinate chart a0 = G_16 / G_2, 32009 | 34:05 / 34:19 | 5.22 GB | 20,568 / 20,371 pairs | `prlimit --as` 5 GB |

- lab-a1 stops are address-space caps set by the operators (A5-070 says so; resident need on 11.6 GiB untested), not
  hardware limits. Sat at 3.5 h on the FX4 (10.6 GB) matches lab-a1's 10.5 GB at 3.4 h: same growth, so the caps only
  moved the stop.
- [measured] RSS against time, sat p32009: 6.1 GB at 1 h, 15.8 GB at 8 h, about 0.4 GB/h at the end (a sub-linear
  curve); the sliced chart reached 11.2, 15.6, 17.8, 20.0, 22.4 GB at 4, 8, 12, 16, 20 h (`fx4-w8p2/rss.txt`). The sat is
  time-bound, the elimination memory-bound; no run shows a plateau, so no run supports a completion forecast.
- Pulled partial results (the only mathematics the runs returned), `fx4-w8p2/chart.log` and `lab-a1/*slice*.log`:
  K2 plus the four z-forms and the origin gives dimension 0, vdim 23, eliminant of z(2) of degree 23 with factors
  1+2+3+5+12 (a Frobenius cycle type of the 23 points at p = 32009, consistent with A5-060); V(J+G) has 11 minimal
  primes, 5 saturating factors. `AI/l0-iso-p32009.log`: G vanishes on L0 = {t2 = 0, t4 = t6, t5 = t7}; the prime of
  V(J+G) through 0 is L0 (dimension 3); the degree-2 parts cut the tangent cone in L0 doubled.
- Lost: the in-memory pair sets and bases at each kill (Singular has no checkpoint inside std), the sat exponent, and
  the sat/std/fiber files, none of which was ever written. Nothing retrievable was dropped when the resource group
  went: `mem.log` (3,052 lines), `events`, the `.err` timing files, all logs and scripts are in the repo.
- Laptop `~/a5/iso-chart` is a different test: the reduced charts y_1, y_2, y_3 = 1 of K2 (A5-058: chart 2 and 3
  radical true in 0.7 s at 29 MB; chart 1 printed its dimension 5 and no radical line), not the blowup chart.
- Record defects. Infrastructure `hosts/azure-vms.md` reads "No VM remains" as of 2026-11-01 and lists neither the
  westus3 VM of this run nor the one that carried the sliced chart. `AI/README.md:64` and the A5-067 text still read
  "a relation of L outside K2 in some degree of at least 6", stale since h_6 is certified at both primes (read: >= 7).

## 3. What the pulled results establish about V(K2), E0 and the support question

- [proved, F_32009 and F_32029] E0 is contained in V(K2) because K2 lies in L (degree-2 receipts), and K2 is radical,
  Cohen-Macaulay, geometrically prime (A5-058 to A5-060). The Hilbert series of k[y]/K2 has h-vector (1, 12, 10), so
  HF(k[y]/K2, d) = 1, 17, 85, 265, 640, 1316, 2422 and 4110 at d = 7 (computed here from the record). F(I) matches it
  through degree 6 at both primes (A5-114..A5-125), so any relation of L outside K2 sits in degree >= 7.
- [proved] Generic-direction arcs reach rank 4 of 5, hence dim E0 >= 3 (a projective 3-fold); arcs tangent to L0 reach
  rank 2 (`AI/README.md` table). These families cannot reach rank 5 (A5-067).
- [measured] The chart saturations decide nothing: no dim A/(t) was produced. They fix a cost only: the first std of the
  dense chart ideal exceeds 8 h at 16 GB (sat) and 7.5 h at 52 GB (elimination), and sparser charts (41 and 49 terms)
  grow the pair list no more slowly (20,5xx pairs in 34 min against 20,5xx at 8 h).
- [measured, F_p only] The six-variable slice ladder replaced the chart: k = 4 reads "on" in all eight preregistered rows
  at both primes (486 s, 304 MB each for `t2h`), k = 5 "off", k = 3 "on", 17 controls as predicted
  (`AI/tslice/README.md:167`; logs `AI/tslice/logs/iso-pP-k4*`). Meaning: the origin lies on the closure of the slice, so
  E0 meets four random codimension-4 spaces. This is consistent with dim E0 >= 4 and is not a proof of it.
- [hypothesis] Confidence of that reading. If dim E0 = 3 with degree e, the codimension-4 spaces meeting E0 form the
  Chow hypersurface of multidegree (e,e,e,e) in the four forms' coefficients, so a uniform form set hits it with
  probability <= 4e/p (Schwartz-Zippel). Refined Bezout on the graph closure in P^6 x P^16 (bidegrees <= 2 * 7^k, G of
  degree <= 7) gives e <= 2 * (7^6 - 1)/6 = 39,216 (hypothesis: the bidegree bound is unchecked against a source).
  At p = 32009 the bound 4e/p exceeds 1, which is why the record says "no numerical confidence". At a 31-bit prime
  (p near 2^31) it is <= 7.3e-5 per form set.
- Not established: dim E0 = 4 as a theorem at any prime; any characteristic-0 statement (A5-067 says so; tasks 42, 75,
  122 carry the transfer).
- Not established either way by the degree-6 data: the "degree-6 membership upper bound" excludes relations only up to
  degree 6 and is already met (A5-119, A5-125). No finite degree bound for L is on record, so any membership route can
  refute (find a relation) but never prove.

## 4. First principles: what decides E0 = V(K2)

Since F(I) = A/(L/K2) for the domain A = k[y]/K2 of dimension 5, F(I) = A exactly when dim E0 = 4, i.e. when a
4-dimensional irreducible subset of E0 exists (then it is V(K2), K2 being prime). Everything reduces to one of:

| Route | What it computes | Proves / refutes | Falsifier |
|---|---|---|---|
| A. Point-blowup fiber-cone plane family (task 56, model: W8 C30, A5-066/A5-236) | at p in P(L0) on the point-blowup exceptional divisor, the fiber cone of I' = I/s^2 and its plane Pi_p; the cone over the union of the planes, by the rank of [M(p) \| dM/db Y0 \| dM/dc Y0] | proves E0 = V(K2) (rank 5) at that prime, deterministic given the exact steps of the W8 certificate | rank < 5: no refutation, route silent; fiber cone not a polynomial ring in 3 variables; I'\|B_3 != (x, v2 s, v2^2); Newton or (v4,v5) determinant zero; a plane failing a K2 generator (would refute the setup) |
| B. Slice ladder k = 4 at a large prime | origin on closure of the codim-4 slice, QRNG forms | probabilistic proof of dim E0 >= 4 over F_p, error <= 4e/p | an "off" at k = 4 with two independent form sets (refutes at that prime: a relation of degree >= 7) |
| C. Chart saturation, dim A/(t) | the same fact in 23 variables | proves 4, refutes <= 3 | none reachable: no run passed the first std |
| D. Degree-7 rank at N = 22 (3d+1 law) | r_22 against HF(k[y]/K2, 7) = 4110 | refutes only | r_22 < 4110 (relation of degree 7); r_22 = 4110 is silent about higher degrees |

Route A in detail (the W8 model, `structure/c30-bounded/README.md`). Steps carried over: chart t3 = s, t_k = s u_k
gives J = s^2 J'(u) (J' = u2^2+u4^2-u5^2-u6^2+u7^2, free of s), and every G_j divides by s^2 exactly. [computed, scratch,
p = 32009, b = 17, c = 29] All 17 G_j divide by s^2; the minimal degrees of the G_j are 2 or 3; at the point
u = (0, b, c, b, c) of P(L0) (u2 = 0, u4 = u6 = b, u5 = u7 = c) G' and J' vanish, dG' has rank 2 in the 6-variable chart
and rank 1 on the 5-dimensional tangent space of {J' = 0}. W8 had two independent linear parts (G'_2, G'_11); Iso has one
(G'_9 on the slice v6 = v7 = 0: (J', G'_9) is a smooth surface, local multiplicity 1; G'_6 is a decoy whose slice linear
part is proportional to that of J', determinant 34*1774 - 58*9870 = 0 mod 32009).
- [hypothesis, untested here] Slice B_3 (dimension 3, transversal to P(L0)): I'\|B_3 = (x, v2 s, v2^2) in coordinates
  (x = G'_9, s, v2), because every G_j vanishes on L0 (so G'_j\|S is divisible by v2 on S = {x = 0}) and the quotients
  have linear parts spanning (s, v2)/m^2. Then F(I'\|B_3) = k[Z1, Z2, Z3], planes P^2, and the union over the two
  parameters (b, c) of P(L0) has cone dimension 3 + 2 = 5 = dim A. The count fits exactly; W8's 4 + 2 = 6 fit the same
  way. The divisibility by v2 and the Nakayama step are open: the W8 certificate establishes them by Newton iteration to
  order 10 over truncated series in (s, v2) and reads the exact 1-jets of G'_j\|S / v2 (`c30-bounded/templates/dual.sing`,
  35 s), and the Iso version is that template adapted to three slice variables with G'_9 as the smooth generator. A
  scratch `reduce` of each G'_j by std(N), N = (J', G'_9, v2 s, v2^2), in a `ds` ring did not return in 150 s; that
  attempt is not run to completion and says nothing about the step. std(N) itself took 0 s.
- Why arcs failed but planes can succeed: W8's arcs tangent to L0 stopped at rank 4 of 6 while the plane family gave 6
  (A5-066); Iso's tangent arcs stop at rank 2 of 5, the same pattern, because Rees valuations at the origin need not be
  monomial in the coordinates the arc families use (`AI/README.md`, "A failed search does not bound the analytic spread").
- Note the vertex: Sing V(J) is the whole t3-axis, so B is singular along u = 0; the points p in P(L0) with (b, c) != 0
  avoid it.

Route B at a large prime. Needs a header over F_p for a prime p = 1 (mod 4) near 2^31 (the Gaussian unit I), the same
`t2h` script, and 17 x 4 coefficients from a fresh QRNG draw recorded in `qrng_seeds/allocations.json` (uint16 draws
must be paired into 32-bit values by the existing rejection rule; extend `tslice_gen.py`). It changes the statement from
"consistent" to "error <= 7.3e-5 under the unverified degree bound of section 3".

Route D and the missing-bound caveat. HF(R, d) for R = k[t]/J gives D(N) = sum_{d<N} HF(R,d): D(18) = 46,683,
D(19) = 59,983, D(22) = 118,910 (computed). The two measured cells (N = 18: 1,173 s, 16.13 GiB; N = 19: 1,901 s,
19.6 GiB; `iso-d6-n19-laptop/README.md`) fit time ~ D^1.92 and memory ~ D^0.96, so N = 22 extrapolates to about 38 GiB and
2.0 h (hypothesis: two points, engine v11 closure growth may bend; W8 shows the engine can need 129-223 GiB).

## 5. Placement

Hosts as given: laptop 32 threads, 52.5 GB budget; build host 12 threads, 38.6 GiB; lab-a1 2 OCPU, 9.5 GiB; Kaggle CPU
4 cores, 30 GB (budget 0.82 x 30 = 24.6 GB), 12 h; FX4mds_v2 4 vCPU 84 GB, Singular 1.6x slower than the laptop, credit
lapses 2026-11-23, $0.547/h; GCP 12 vCPU, 300 USD.

| Route | Cores | RAM | Runtime, from a measured rate | Best host | Notes |
|---|---|---|---|---|---|
| A. plane family, 2 primes x 3 points | 1 | < 0.1 GB | W8 plane: 34.6 s and 24.8 MB at 32009 point 1 (`c30-bounded/logs/c30-plane-p32009-pt1.time`), 45-52 s per ledger; Iso slice has 3 unknowns instead of 4: about 6 x 1 min + setup, under 10 min | build host or laptop for the first run (the scope doc names lab-a1 at 9.5 GiB; fits at 100 MB, but aarch64 speed is unmeasured, hypothesis a few times slower) | no spend case; adapt `c30_gen.py` templates `dual.sing`, `plane-tests.sing`; first verify the slice structure with the Newton-series template (section 4) |
| B. k = 4 third family, both primes | 1 per job | 0.3 GB | 486 s (`t2h`), 2,130 s (twin `t2`) at 304-320 MB on the build host; four jobs in parallel | Kaggle CPU session (4 cores, 4 jobs) or build host | large-prime variant: cost assumed equal (hypothesis; falsified if the std is more than 3x slower) |
| C. chart saturation, any variant | 1 | unbounded: 15.8 GB at 8 h (sat), 25.7 GB at 21.7 h (sliced), 52 GB at 7.5 h (elimination) | no forecast: no run left the first std | none | do not rerun in this formulation |
| D. degree-7 rank, N = 22, one prime | 1 Singular + linear algebra | about 38 GiB (hypothesis) | about 2 h (hypothesis) | laptop (52.5 GB budget); Kaggle (24.6 GB) and the build host (38.6 GiB) are too small | refutation only; run after A and B if they stay silent |

Which run needs more than 52 GB and so justifies Azure? Only the dense Rabinowitsch elimination (52.1 GB at 7.5 h,
still climbing, no forecast); it is not worth a spend case, since the formulation has no completion estimate and routes A
and B decide the question at under 1 GB. Route D at N = 22 is the one candidate that could exceed 52.5 GB if the
extrapolation bends (W8's order-19 need was 129-223 GiB), and then an FX4 with 84 GB at $0.547/h for 5 h (about $3) fits
the credit before 2026-11-23; run it on the laptop first and move only on a measured peak above 45 GB. GCP and Kaggle
add nothing here that the laptop and the build host lack.

Ranked by information per core-hour: A (a deciding proof in minutes once the slice structure
I'\|B_3 = (x, v2 s, v2^2) is verified) > B at a large prime (bounded error in 8 minutes if the degree bound e <= 39,216
holds) > B at the current primes (the third family the preregistration already allows) > D (refutation only) > C.
Recommended next action: build the Iso plane pilot from the W8 templates, run it at 32009 on the build host, and report
rank 5, rank < 5 or a failed Nakayama step; then repeat at 32029 and, for the all-degree statement over Z, hand the
result to the char-0 transfer tasks (42, 75, 122).
