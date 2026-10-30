

===== FILE: final-plan-brief.md =====

# Final-plan consult: A_5 exceptional fibers, with every result and the whole lab

You are one of several independent reviewers (Grok, agy/Gemini, opencode on Groq). This bundle is the whole
evidence. Read it in full; then write your answer. Do not run anything.

Bundle order after this brief: purpose.md, decision-record.md (the authority, every success and failure),
lab-map.md (every machine, service, quantum provider, QRNG, cloud compute, LLM API and policy gate),
greater-picture-gpt-daybreak-blue-latest.md and greater-picture-gpt-6.1-terra.md (two earlier Codex consults),
docs/PYTHON.md and docs/runbooks/compute-flags.md.

## Resolved local findings to build on (each verified in the decision record)

1. Degree-by-degree method A is exact and has succeeded on every pair: X+- h=15,51,122; Iso 17,85,265;
   E8bar->N+ and N- 21,83; W8 24,156; E8bar->VB 10,34,80 (reproduced by the new driver). Nullity-16: eight fibers
   complete (B9: P^2; V: conic; VB, Va: points).
2. Every full-fiber completion (pivot saturation, candidate-ideal std(L)) stalled after the pivot: X- 3 h and 12 h,
   Iso 6 h, VB 2 h, E8bar->N+- 10 h at 72 GB, VB std(L) 3 GB. W8 was cut off by a VM outage (not a stall).
3. The 2.5 GB "no more memory" exits of the nullity-16 producer came from an inherited RLIMIT_AS of 4 GiB set by
   a Python helper, not from the configured cap; cgroup MemoryMax is the only permitted limit.
4. Kaggle TPU v5e-8 queue: 6+ h without assignment for a small smoke kernel.
5. The Codex consults converge on exact arc families with a Jacobian density certificate (VB, then X-), a
   syzygy/Jacobian-dual probe, and VB h4 vs 155 as a diagnostic (running now).

## Questions

1. Attack the converged plan. Where is the arc-family certificate wrong, incomplete, or harder than it looks
   (positive characteristic, inseparability, arithmetic vs geometric primes, nonreduced K2, components missed)?
2. Give one concrete construction of an arc family for E8bar->VB or X- from the data in the bundle (which
   coordinates to parametrize, how to solve J=0 along the arc, what degree in s to expect), as Singular, M2 or
   Sage code a reviewer can run on the host in under 8 GiB.
3. Name any route the two Codex consults missed, using any capability in lab-map.md, including quantum backends,
   QRNG, cloud LLM APIs, Kaggle, Azure, GitHub Actions or local GPU. Say plainly when a capability does not
   apply to this classical algebra problem.
4. Produce a stepwise plan: ordered steps, each with resource, memory cap, time limit, the result it yields, and
   the falsifier that stops it. Mark each claim observed (cite the bundle section) or inferred.

Keep the answer under 200 lines.


===== FILE: purpose.md =====

# What the fiber computations measure, and why

**Programme.** The open claim `dimension32-global-topology` asks for the global topology of the zero-divisor set of
the 32-dimensional Cayley-Dickson algebra A_5, stratified by nullity. Its roadmap is the table "Route to the global
classification" in `docs/notes/rank_locus_two_dimension_gap.md:323-341`. Items 3-5 are discharged: components and
closed equations of every rank stratum, a Whitney stratification by orbits of H = G_2(C) x SO(2,C) x C^*
(`docs/evidence/a5-strata-regularity/README.md`), and kernel bundles on every stratum
(`docs/design/a5-kernel-bundles-nullity8-program.md`). Item 6, **attachments**, is open: how the partner spheres
(kernel fibers) of a stratum specialize across each closure incidence, that is, the attaching maps a finite global
model (item 7) is glued from.

**Where the runs enter.** Each run takes a nullity-8 orbit closure Y (W8, E8-bar, Iso, X_+, X_-) and a smaller orbit
Z in its closure (N_+, N_-, VB, ...), with I the ideal of Z on Y (generators G, ambient relation J). The fiber cone
F(I) = sum_d I^d / m I^d (the special fiber of the Rees algebra at a point of Z, after the normal-cone translation)
is the coordinate ring of the exceptional fiber of the blow-up of Y along Z over that point: the set of limiting
directions by which Y approaches Z. Its Hilbert function h_d, its degree and its relation degrees (for example the
K2 relations of degree 23 on Iso) describe that limit set. Item 6 needs exactly this set: the program doc (gap N3,
lines 38-40) says a nullity-12 boundary orbit carries the nullity-8 kernel representation plus two extra dimensions
and that "the shape of that specialization is the attaching data", and the nullity-8 record finds boundary limits
path-dependent, so the attaching datum is the whole limit set, not one inclusion. The fiber cone is its algebraic
certificate.

**What a result must deliver.** For each (Y, Z): the dimension and degree of the exceptional fiber, enough of its
Hilbert function to fix it (or its Hilbert series), and ideally its defining ideal or its decomposition into
components. Any reformulation that computes the same limit set is acceptable, for example: the exceptional fiber via
implicitization of limits of a parametrized family of curves into Z; the fiber over one point only, since H acts
transitively on Z and the point stabilizer acts on the fiber (equivariant decomposition by that representation);
the kernel-map limits directly (limits of ker L_y as y -> Z), which is the attaching datum itself. An option that
yields only h_d up to some d is weaker than one that yields the fiber's components; state which each option yields.


===== FILE: decision-record.md =====

# Decision record: the four failed A_5 fiber runs

Inputs: `purpose.md` (target object), `first-principles-plan.md` (Claude sonnet consultant, "CP"),
`codex-consult-v2.md` (Codex gpt-6.1-sol high, read-only, "CX"). Times UTC. Every step states its falsifier before it
runs; results are appended under each step with log paths.

## 1. Target

Proj F(I), F(I) = sum_d I^d / m I^d, for I = (G) the kernel-coordinate ideal on the nullity-8 closure Y at a point of
the boundary orbit Z. Deliverable per pair: dimension, degree, Hilbert series, components. A finite segment h_1..h_d is
partial. CX qualification adopted: I = (G) is the Pfaffian kernel-coordinate ideal; its identification with the ideal
of Z is not assumed, and the fiber of (G) is what the attachment needs (the kernel limit set), so (G) is the right
center. Computations over F_32009 certify that reduction only; characteristic-zero claims need a second prime and a
specialization argument (CX).

## 2. Reconciliation of the two consultants

| Point | CP | CX | Decision and reason |
|---|---|---|---|
| Local `ds` syzygy is the cost driver; replace by global membership in J + m P_d ("A") | yes, measured 17 s vs 25,459 s at X- d=2 | yes, same proof (quotient killed by m) | **Adopt.** Two independent derivations; measured. |
| Nakayama normal-monomial reduction (680 -> 122 X, 969 -> 265 Iso) | yes | yes, local justification suffices | **Adopt.** |
| X+ and X- related by t9 -> -t9 with sign vectors on J and G | not seen | checked coefficient-wise | **Adopt after S0 verifies it in Singular.** Halves the X work. |
| Full fiber by pivot saturation H : g^inf, F = k[t,y]/((H:g^inf)+(t)) ("B") | not proposed | proposed, M2 ReesAlgebra uses the same mechanism | **Adopt as the completion certificate.** It is the only route giving the whole ideal, hence the Hilbert series and components without a completeness gap. |
| Regularity of k[y]/K2 bounds missing relations (CP R7) | proposed | refuted: regularity of K2 says nothing about relations of the unknown F(I) | **Reject.** CX is right; a new relation can appear in any degree. |
| Radical first + `minAssChar` for X- V(K2): one prime, degree 12 | measured 1 s | agrees; arithmetic irreducibility over F_p only | **Adopt, with the F_p qualifier.** V(K2) is only an upper bound for the fiber until B or a complete A closes it. |
| msolve on the 31-variable a-graph | "not the tool" | low priority, not refuted universally | **Deprioritize, do not run.** B removes the a-graph entirely; a 64 GiB msolve replay buys a comparison, not the object. |
| Generic linear section / Frobenius orbits for Iso components (CP R4) | proposed | diagnostic only | **Reject as evidence; keep as a sanity check if cheap.** |
| Torus multigrading makes decomposition cheap (CP R5) | proposed | grading splits blocks, does not force toric components | **Defer.** Use only if Iso chart decomposition stalls. |
| Projective-chart decomposition for Iso K2 / fiber | not proposed | proposed | **Adopt for Iso** after B gives the fiber ideal. |
| One-point transport by H-transitivity | assumed | the split boost has no kernel lift (program doc line 23) | **Reject the assumption.** Each pair is computed at its recorded point; no transport claim. |
| Fiber dim bounds | "at most 3" universally | 3 X, 4 Iso and E8-bar, 5 W8 from germ dimensions | **Adopt CX bounds** as falsifiers. |
| W8 product count | 325 | 300 | **300** (24*25/2). |
| Sparse Macaulay linear algebra with upper/lower sandwich | Wiedemann idea | gives a certified stop rule | **Hold in reserve** for a degree where A's std blows up. |
| GPU/TPU rank infrastructure | listed | lowest priority until a matrix problem is measured | **Reject for now.** No measured matrix bottleneck. |
| New packages (Normaliz, 4ti2, CoCoA, OSCAR, msolve master) | not needed | same | **Build none now.** Installed Singular 4.4.1 and Macaulay2 cover A and B. |
| Resource limits | cgroup `MemoryMax`, never `prlimit --as` | same, with `MALLOC_ARENA_MAX=2`, one thread | **Adopt.** Both prior killers (xp_np, msolve solo, probe H) were address-space caps. |

## 3. Falsification of the whole plan

The plan fails if any of these holds; each is checked by a step below.
- F1. The sign symmetry fails on any generator: X+ must be computed separately.
- F2. Method A at d=2 does not reproduce h2 = 51 (X) / 85 (Iso): A is wrong or the inputs differ.
- F3. A at d=3 gives h3 > 122 (X) or > 265 (Iso): the Nakayama reduction or the code is wrong.
- F4. B's Hilbert function disagrees with A in any degree A completed: one of the two is wrong; neither result stands.
- F5. B's fiber dimension exceeds the germ bound (3 X, 4 Iso/E8-bar, 5 W8).
- F6. B fails at the chosen pivot because g is a zero divisor mod J: choose another pivot; if none, B is unavailable.
- F7. The fiber is not contained in V(K2) (B's degree-2 part differs from K2): input or code error.

## 4. Steps (cheapest decisive first)

| Step | Pair | Method | Substrate, limits | Decides |
|---|---|---|---|---|
| S0 | X+ vs X- | substitute t9 -> -t9 and compare J, G up to sign | host, seconds | F1 |
| S1 | X- | A at d=3 on 122 normal cubics, products reduced mod J factor by factor | host cgroup 8G, 1 h | F3, h3 |
| S2 | X- | B, pivot saturation | host cgroup 16G, 3 h | F4-F7, full fiber |
| S3 | Iso | A at d=3 on 265 cubics | host cgroup 12G, 2 h | F3 |
| S4 | Iso | B | host or Azure | full fiber |
| S5 | E8-bar->N+, W8->N- | h1 then A at d=2 | host 16G / Azure VM 2 if larger | F2-style counts, first measurement |
| S6 | E8-bar, W8 | B | Azure VM 2 (westus2, 84 GB), one job at a time | full fiber |
| S7 | all completed | repeat at a second prime p = 1 mod 4 | Kaggle CPU | char-0 support |

Azure use follows the case in `azure-cases/vm2-fiber-b.md`, written before VM 2 starts.

## 5. Results

(appended per step)

- **S0, 2026-10-29 ~10:10.** `runs/s0/s0.log`: under t9 -> -t9, J- = eps * J+ with eps = (+ - - - - - - - + + + +)
  and G- = delta * G+ with delta = (+ + + + + + - - - - - - - - -), 0 failures. F1 passes; X+ results follow from
  X- by y_j -> delta_j y_j. CX's coefficient check is confirmed independently.
- **h1, E8-bar and W8.** `runs/e8_a2/nf1.txt`, `runs/w8_a2/nf1.txt`, F_p rank by `probes/rank_nf.py`: h1 = 21 and 24,
  equal to the generator counts; both G are minimal, no generator drops.
- **S1 launched** (host, 8G cgroup, 3 h): the 122 cubic products built in 4 s once each factor is reduced mod J as it
  is multiplied (probe H died at the eager `phi(kb)` expansion under a 2 GiB address-space cap, at 333 MB allocated).
- **S2 launched** (host, 16G, 3 h): pivot G_11 (64 terms) is a nonzerodivisor mod J. F6 passes.
- **E8-bar, W8 method A degree 2 launched** (host, 6G each, 1 h): 231 and 300 products.
- **VM 2 restarted** under `azure-cases/vm2-fiber-b.md`: method B on E8-bar then W8, 78G cgroup each, 10 h each;
  watcher copies results to `runs/<job>/vm2/` and deallocates by 2026-10-30 08:00 UTC.
- **S1 result.** `runs/s1/out.log`, `runs/s1/s1_nf3.txt`: std(J + m P3) in 587 s, 598 s total, exit 0; F_p rank of
  the 122 normal forms = 122, so **h3 = 122** for X- (and X+ by S0). F3 passes. No cubic relation lies outside K2:
  F(I) agrees with k[y]/K2 through degree 3 (h = 15, 51, 122). This is a finite segment; S2 decides all degrees.
- **S3 launched** (host, 10G, 3 h): Iso, 265 normal cubics built in 1 s.
- **S3 result.** `runs/s3/out.log`, `runs/s3/s3_nf3.txt`: std in 1010 s, 1054 s total, exit 0; rank 265, so
  **h3 = 265** for Iso. F3 passes; Iso F(I) agrees with k[y]/K2 through degree 3 (h = 17, 85, 265). The local-syzygy
  cross-check `iso-h3-reduced` computed the same quantity by the slow route and was stopped to free 16G for S4.
- **S4 launched** (host, 16G, 6 h): Iso method B, pivot G_16 (41 terms) is a nonzerodivisor mod J. F6 passes.
- **W8 method A degree 2, 6G attempt.** `runs/w8_a2/try6g/`: exit 137 after the 300 products, killed by the kernel
  OOM killer inside its own 6G scope (journal: "The kernel OOM killer killed some processes in this unit"). Host
  memory was not exhausted. Relaunched at 12G, 2 h; VM 2's method-B job on W8 stays the primary route.
- **E8-bar method A degree 2, 1 h attempt.** `runs/e8_a2/try1h/`: exit 124 (timeout) inside std(J + m P2), memory peak 4.6G; time-bound. Relaunched at 10G, 8 h.
- **W8 method A degree 2, 12G.** `runs/w8_a2/`: std(J + m P2) in 5551 s, 5619 s total, exit 0, memory peak 6.7G
  (the original local syzygy reached 83 GB before h2). F_p rank 156 of 300 products: **h2 = 156**, 144 quadric
  relations (`runs/w8_a2/w8_k2.rel`, extracted by `probes/relations_nf.py`).
- **Relation extractor check.** `probes/relations_nf.py` on the X- degree-2 normal forms returns 69 relations whose
  ideal equals the retained `xm_nm_fiber.rel` (`runs/s0/k2cmp.sing`: same ideal, h = 15, 51, 122).
- **W8 V(K2).** `runs/w8_a2/k2hf.sing`: projective dimension 5 (equal to the germ bound, F5 consistent), degree 50,
  h = 24, 156, 600, 1725. V(K2) is an upper bound for the fiber until degree 3 or method B closes it.
- **W8 degree 3 queued** (`runs/w8_a3/queue.sh`): 600 normal cubics, host 16G, 12 h, starts when S2 or S4 frees
  its memory. VM 2's E8-bar job sits at 33.8 GB of its 78G cap, so sharing VM 2 would risk a global OOM.
- **E8-bar method A degree 2, 8 h attempt.** `runs/e8_a2/`: std(J + m P2) in 6003 s, 6029 s total, exit 0. F_p rank
  83 of 231 products: **h2 = 83**, 148 quadric relations (`runs/e8_a2/e8_k2.rel`). V(K2): projective dimension 4
  (germ bound 4, F5 consistent), degree 11, h = 21, 83, 225, 495 (`runs/e8_a2/k2hf.sing`). The msolve a-graph
  elimination never produced any fiber count.
- **E8-bar degree 3 launched** (`runs/e8_a3/`, host 12G, 12 h): 225 normal cubics.

## 6. What failed, what works (summary as of 2026-10-29 20:40 UTC)

| Run | Old route and failure | Mechanism | New route | Result |
|---|---|---|---|---|
| X+ -> N+ | local `ds` syzygy of U_d (961 columns); killed in degree 3 | `prlimit --as` 12 GiB address-space cap, not RAM (RSS 6.7 GiB, 22 GiB free) | method A in `dp` + Nakayama cubics; X+ = X- by t9 -> -t9 (S0) | h = 15, 51, 122 |
| X- -> N- | degree-2 K2, then `minAssGTZ`; timeout | GTZ's generic coordinate change densifies the input | radical first + `minAssChar` (1 s); method A degree 3 | V(K2) one prime over F_p, proj dim 3, degree 12; h3 = 122 |
| Iso K2 | `minAssGTZ` 40,000 s; timeout | same | method A degree 3; method B running | h = 17, 85, 265 |
| E8-bar -> N+ | msolve elimination of a in the 31-variable Rees graph; hash table to 2^28, memory | degree-7 F4 step selects 407,116 pairs | method A degree 2 (100 min), degree 3 running; method B on VM 2 | h = 21, 83; V(K2) proj dim 4, degree 11 |
| W8 -> N- | local syzygy, 2,401 module generators; 83 GB before h2 | Schreyer module growth in `ds` | method A degree 2 (94 min, 6.7 GB); degree 3 queued; B on VM 2 | h = 24, 156; V(K2) proj dim 5, degree 50 |

Working strategy: global ordering, membership in J + m P_d (exact, since the quotient is killed by m), products reduced
mod J factor by factor, Nakayama normal cubics from the certified K_{d-1}, exact F_p rank and left kernel with FLINT
(`probes/rank_nf.py`, `probes/relations_nf.py`), every job in a `systemd-run --scope -p MemoryMax=... -p
MemorySwapMax=0` cgroup with `MALLOC_ARENA_MAX=2`. Completion comes only from method B (pivot saturation); a finite h_d
segment is reported as partial. Errors met in this program: a 2 GiB address-space cap killed probe H at 333 MB
allocated (eager `phi(kb)` expansion); W8 degree 2 died in its own 6G cgroup (exit 137) and passed at 12G; E8-bar
degree 2 timed out at 1 h (4.6G peak) and passed with 8 h; a launch with a wrong relative input path ran nothing and
was relaunched.

## 7. Host memory incident, 2026-10-29 09:45:53 UTC

systemd-oomd (`journalctl`, unit systemd-oomd[984]) killed the Konsole tab scope
`app-org.kde.konsole-2020.scope/tab(3888226).scope` "due to memory used (63965974528) / total (67305283584)" with
27G of swap in that scope; the tab's own processes are not named in the log. Load at that moment: the cu13 Aer wheel
podman build (6 nvcc jobs), the full gate run (4 workers), the 16G-capped iso-h3 scope, the uncapped E8-bar->VB
Singular job (PID 426469, which still runs inside another Konsole tab scope with a FLOOR_KB watchdog instead of a
cgroup cap), and the Codex consult. The kernel OOM killer acted once more, at 11:07:40 UTC, only inside the 6G W8
scope (CONSTRAINT_MEMCG). NVRM "Out of memory" lines at 09:17 and 09:22 UTC are GPU allocations during the cu13
gpu-check. Rule adopted: every heavy job runs in its own cgroup scope with MemoryMax, the caps actually reachable at
once stay below physical RAM, and no container build runs beside fiber jobs; queued jobs (W8 degree 3) start only when
a capped job frees its memory.
- **S2 X- method B, 3 h attempt.** `runs/s2/try3h/`: exit 124 inside sat(H, g), 6.9G peak; time-bound. Relaunched at 10G, 12 h. W8 degree 3 started from its queue at 13:11 UTC (600 normal cubics).
- **W8 N+ symmetry.** `runs/s0b/w8.sing`: under t9 -> -t9 the W8->N+ input equals the W8->N- input up to sign
  (J +, G: 22 minus, 2 plus), 0 failures. The W8->N+ fiber follows from W8->N- by y_j -> +-y_j; no run needed.
- **E8-bar N- is distinct.** `runs/s0b/e8.sing`: J matches up to sign, G does not; `runs/s0b/e8span.sing` +
  `probes/rank_nf.py`: rank 21, 21 and 41 for the substituted N+ generators, the N- generators and both together,
  so the spans share one dimension and E8-bar->N- needs its own run.
- **VM 1 swap, ~13:45 UTC.** VM 1 ran the old local-syzygy `e8_nm_fiber` (17 h, 33.3 GB RSS under a 32 GiB
  `prlimit --as` cap, the X+ failure mode) and would rerun `w8_np_fiber` (exit 137) the same way. Both stopped by
  PID; `supervise-a.sh` now runs E8-bar->N- method A (degree 2) and method B side by side, 38G cgroup each, 6 h,
  inside the existing VM 1 deadline (deallocation by 20:00 UTC).
- **E8-bar->VB homogenized run (host, old route)** ended exit 137 at its watchdog after about 24 h in `std_graph`.
- **Review round.** The executed plan and results went to two reviewers: Codex gpt-6.1-sol high (read-only,
  `review-codex.md`) and a Claude opus agent (`review-claude.md`), brief `review-brief.md`.
- **Old E8-bar->VB run, post-mortem.** `e8vb-old/` (copied from the session scratchpad): Rees graph in 20 variables
  (a, t1..t8, y1..y10, homogenizing h), `eliminate(R, a)`; only `RESULT eliminated 0` and `STAGE homogenized`
  printed, pair count peaked near 61,609 and was ~49,000 at the end, RSS 2-4 GB; no fiber result. Both kill paths
  were disabled by our own `extend-timeout.sh`: it sends SIGSTOP to the run's `timeout` (PID 426466) to hold the
  deadline, so the 12 h limit never fired and the memory-floor signal (`floor_fired` at 13:25 UTC) went to the
  stopped `timeout`; the run ended only by a manual kill (exit 137). Rule: a deadline extension restarts a new
  timer around the running PID or relies on a cgroup, never SIGSTOPs the supervisor.
- **E8-bar->VB by method A** (`runs/e8vb_a2/`, host 3G): degree 2 in 7 s. h1 = 10, h2 = 34, 21 quadric relations;
  V(K2) proj dim 3, degree 7, h = 10, 34, 80, 155. Degree 3 (`runs/e8vb_a3/`, 80 cubics) and method B
  (`runs/e8vb_b/`, pivot G_3 with 9 terms) run on the host at 4G each; the problem is small enough that a cloud VM
  is unnecessary.
- **Full-picture analysis** requested from Codex gpt-6.1-sol high (`picture-brief.md` -> `picture-codex.md`).

## 8. Review round outcome (Codex `review-codex.md`, Claude opus `review-claude.md`, Codex `picture-codex.md`)

Both reviewers replayed the counts and found methods A and B correct as coded (products from `kbase` exponents,
global membership equals the local graded piece, left kernel orientation, pivot test J : g = J, global t = 0 equals
the local fiber). Corrections adopted, superseding earlier wording in this record:
- A finite segment certifies only those degrees. "No cubic relations beyond K2" means K_3 = (K2)_3; V(K2) stays an
  upper bound for every pair until a completion certificate closes it. Iso's 23 is the degree of the quadratic
  scheme. Logged "std seconds" are cumulative from product construction.
- Span rank 41 shows only that the diagonal-sign transport fails for E8-bar N+ vs N-; the review's membership check
  (`review-checks/claude/idealeq.log`) shows the global ideals differ, which still leaves local equivalence and
  fiber isomorphism untested. E8-bar->N- keeps its own computation.
- Method B is one completion route, not the only one. Alternatives: a certified candidate L with
  H in L in ker(y -> aG) and L : g = L; reduced-support equality by a dense family of genuine limits; an independently
  bounded Hilbert function; an unmixed candidate with equal dimension and multiplicity.
- Second-prime runs must regenerate J and G from the Q(i) producer at the new split prime; rewriting 32009 in the
  specialized inputs changes the input.
- The S2 6.9G peak comes from the systemd journal ("memory peak"), not from `try3h/out.log`.

**K2 structure and J check** (`runs/k2struct/*.log`, 3G cap, 600 s):
| Pair | J radical, one prime through 0 | K2 radical | Minimal primes of K2 (proj dim, degree) |
|---|---|---|---|
| X- | yes | no (radical h = 12, 45, 112, 225) | one: (3, 12) |
| E8-bar->N+ | yes | no (radical h = 16, 69, 195, 440) | two: (4, 11), (3, 4) |
| E8-bar->VB | yes | yes | two: (3, 3), (3, 4) |
| Iso, W8->N- | yes | not finished in 600 s | not finished |
J being prime through the origin closes the reviewers' unstated method-B assumption. E8-bar->VB's V(K2) is reducible,
which rules out the irreducible 2 x 7 scroll hypothesis in `picture-codex.md`.

**E8-bar->VB degree 3** (`runs/e8vb_a3/`, 406 s): rank 80 of 80, h3 = 80; h = 10, 34, 80 agree with k[y]/K2.

**Host load, ~21:30 UTC.** Available memory fell to 6 GB with five Singular jobs (W8 degree 3 at 14 GB) and two
foreign 4 GB Python workers. W8 degree 3 was stopped by PID (its `rc` reads 0 because the wrapper caught the
signal); both reviewers rank it lowest value. Host admission target from here: about 24 GiB of reachable caps for
this program.

**Revised order** (both reviewers' rankings merged):
1. E8-bar->VB as the first complete receipt: method B running (pivot G_3, 9 terms); decompose the fiber; then
   the second prime from the producer.
2. X- completion: S2 method B 12 h rerun continues; next try M2 `reesIdeal` or the certified-candidate L route.
3. Iso method B continues (bounded at 6 h).
4. E8-bar->N- on VM 1 (A degree 2, B), E8-bar then W8 method B on VM 2 continue as cased.
5. E8-bar degree 3 continues on the host; W8 degree 3 moves to a cloud substrate only after items 1-3 report.
6. Build the degree-by-degree driver with receipts (input hashes, ordered monomials, normal forms, rank witness,
   timings, peaks), and the producer-based second-prime harness.

## 9. Tooling build (owner request 2026-10-29)

Advisor review before building (summary): settle input provenance first (the X/Iso/E8/W8 inputs come from producer
phase-one emits plus a scratchpad converter, and the E8-bar->VB input from a hand edit with a `+((10754))*(0)`
artifact), so the second-prime harness regenerates from the Q(i) producer and is falsified by regeneration at
p=32009, r=10754 against the files actually computed; keep validation within about 3G while long jobs run; the
certificate layer reports separate statuses (degree-certified, support-equal, scheme-equal), and the bounded-Hilbert
route is a scope cut because no relation-type bound exists in the tree. Versions: Singular 4.4.1.p5, FLINT 3.6.0,
msolve 0.11.0 equal the packaged latest (`paru -Si`); Macaulay2 1.26.06 is a local build; python-flint 0.9.0. No
upgrade while jobs run on these versions. E8-bar degree 3 was stopped by PID to free 12G (both reviews rank it low).
Build split: Part A (`build/part-a-inputs.md`, provenance and harness, `fiber_inputs.py`) and Part B
(`build/part-b-driver.md`, `fiber_cone_driver.py`, `fiber_certificates.py`), sonnet agents in the
a5-kernel-attachments worktree; review by Codex read-only and the orchestrator before any commit.
- **Kaggle TPU msolve kernel `a5-e8vb-msolve-tpu`** (E8-bar->VB, msolve route): CANCEL_ACKNOWLEDGED at 15:03 UTC after ~2 h running (watch log `kaggle-watch3.log`). Not rerun: the msolve route is deprioritized (section 2) and method A/B cover this pair on the host.
- **Kaggle TPU analysis, ~15:30 UTC.** Quota (MCP): TPU 7,390 s of 72,000 s per week used, GPU 11,920 s of
  108,000 s; refresh 2026-10-31T00:00Z. The cancelled `a5-e8vb-msolve-tpu` kernel (source and outputs in
  `kaggle-tpu/src`, `kaggle-tpu/out`) ran msolve on the E8-bar->VB Rees graph on a TpuV5E8 VM: degree 16 matrix
  86,010,243 x 87,648,606, RSS up to ~51 GB of ~390 GB available, its own solver timeout 31,500 s; it ended
  CANCEL_ACKNOWLEDGED after ~7,380 s with no cancel issued from this machine, so the cancel came from Kaggle's side
  (cause under review). The TPU VM is a 96-core, ~330 GB CPU host (docs/notes/kaggle/tpu-research.md), the largest
  substrate available to this program, limited to one batch session, 9 h per session and 20 h per week. Smoke
  kernel `a5-fiber-tpu-smoke` pushed with a 3600 s timeout (`kaggle-tpu/test/`): passagemath-singular install plus
  E8-bar->VB degrees 2-3 and X- degree 2 in parallel, expected h = 10, 34, 80 and 15, 51. Codex reviews the TPU
  question (`kaggle-tpu/review-brief.md` -> `review-codex.md`).
- **TPU review (Codex, `kaggle-tpu/review-codex.md`) corrections.** The msolve kernel's sampled RSS peaked at
  203,942,860 KiB (~209 GB) at 7,166 s, not ~51 GB; `os.cpu_count()` returned 224 logical CPUs and msolve averaged
  ~23 effective cores (CPU/wall), ~31 in degree 16. The cancel initiator is unresolved: a push-time session timeout
  and Kaggle policy remain plausible, and the local search rules out only this machine. Extrapolating the 1.63x
  round growth puts degree 19 near 9.2 h, so full elimination does not fit a session. Smoke acceptance must compute
  exact ranks from the job outputs (done locally from the downloaded normal-form files). Next: a 4 h (14,400 s)
  parallel method-B pilot (VB 8 GiB, X- 16, Iso 24, E8-bar N+/N- 48 each, W8 64, E8-bar N- degree 2 24; 296 GiB
  admission, 1 s RSS sampling, per-job TERM/KILL, streaming receipts), only after the smoke test passes. Kaggle
  guides to update (substrates.md, tpu-research.md, workflow.md, interfaces.md, README.md) in a docs PR.

- 2026-10-29 Part A (input provenance, second-prime harness) complete; report build/part-a-report.md. fiber_inputs.py regenerates all nine inputs from the Q(i) producer. At p=32009, i=10754: six inputs byte-identical; Iso equal up to term print order (and order/sign for N-); E8bar->VB has the same J and coordinates, G equal modulo J but not byte-reproducible (the computed file carries a `+((10754))*(0)` artifact), so prior VB results stand on an equivalent presentation. Second embedding r=21255 and second prime p=32029 (r=9115) headers emitted for all nine, selected counts unchanged. Open: nullity16-rees-fibers-result.json still records prime 32003 against producer 32009; regenerate with its digest before commit.
- 2026-10-29 Part B (degree driver, certificates) complete; report build/part-b-report.md. Orchestrator rerun reproduces E8bar->VB h=10,34,80 (21 quadrics at d2, none new at d3) and X- h=15,51 with 69 relations; 5 unit tests pass; ruff/mypy clean. Candidate-ideal certificate on VB: std(L) in 18 variables timed out at 500 s and hit 3G after 14 min -> candidate-not-verified; post-std checks untested. Dense-family arc sampler unbuilt (needs QRNG draws + ledger rows).
- 2026-10-29 e8vb_b (VB method B, 2 h cap) exit 124 after pivot G_3: second VB completion route to stall in elimination, with X- method B (3 h). Finding: the Rees saturation and std(L) both blow up on the same rings; the next completion attempt must change formulation (e.g. degree-bounded std with a Hilbert-driven stop, or the dense-family route), not raise caps.
- 2026-10-29 Defect fixed in nullity16_rees_fibers._run_singular: an outer `timeout` shorter than the inner one killed Python before killpg, orphaning Singular (start_new_session); two orphans from Part A ran 30-45 min. Fix: SIGTERM->SystemExit plus finally-killpg, and cgroup MemoryMax scope replacing `prlimit --as`. Falsifier run (8 s outer timeout over a spinning Singular) left no process.
- 2026-10-29 iso_b (Iso method B, 6 h, 16G) exit 124 after pivot G_16 at ~10G RSS: fourth method-B/candidate stall; confirms the formulation finding above.
- 2026-10-29 VM 1 deallocated. e8nm_a2 (E8bar->N- method A d1-2, 2.2 h, std_Q 7838 s) gives h = 21, 83 (rank_nf on downloaded nf files), the same counts as E8bar->N+ although the global ideals differ (span rank 41). e8nm_b (method B) stopped after pivot G_19, no fiber: fifth method-B stall. Results in runs/e8nm_a2/.
- 2026-10-29 Producer regeneration blocked: under the cgroup cap, E8bar->N+/- and W8->N+/- modular_rees_fiber stages exit status 14 (Singular allocation failure) at 2.5 GB peak, 83-227 s, where the self-test permits only blocked_timeout. A/B run with the prior prlimit cap is in progress to decide whether this predates the runner change.
- 2026-10-29 A/B: the prior prlimit runner reproduces the same status-14 exits (E8bar->N+/- 220 s, W8->N+/- 83 s, 2.5 GB peak, identical RSS under both caps), so the runner change is not the cause; the self-test's timeout-only allowance predates the 32003->32009 prime switch. Capturing Singular's output on those exits next.
- 2026-10-29 Root cause of the status-14 exits: the 4 GiB per-Singular cap. Singular reports 'no more memory' at 2.5 GB resident (allocator reservations exceed the cap under both prlimit and cgroup); with a 16 GiB cap all ten permitted pairs reach the 300 s timeout as the self-test expects. Producer cap set to 16 GiB (jobs run serially, GOROROBA_WORKERS=1); record regenerating.
- 2026-10-29 TPU smoke kernel a5-fiber-tpu-smoke (TpuV5E8) queued 15:10 UTC, still QUEUED at 21:10 UTC; TPU quota unchanged at 7,390 s of 72,000 s, 0 reserved: v5e-8 capacity was not assigned for 6 h. Queue wait is a measured TPU-route cost; left queued under a 12 h watcher.
- 2026-10-29 VM 2 results, fetched after the watcher deallocated it on six failed ssh polls (restart under azure-cases/vm2-fiber-b.md, deallocated again). e8_b (E8bar->N+ method B, 78G cap, 36,000 s) exit 124 after pivot G_19 at 72 GB RSS: sixth method-B stall, and the largest memory seen. w8_b (W8->N- method B) started 20:15 UTC, reached 13 GB with ~71 GB available at its last sample (1,501 s), then the VM stopped answering ssh at ~20:38 UTC. Memory did not cause the outage (growth ~0.5 GB/min, 58 GB headroom); the cause is unidentified (previous-boot kernel log held no OOM entry). w8_b is incomplete, not a stall.
- 2026-10-29 Corrected root cause of the status-14 exits: _analyze_row calls basepoints.schur._cap_worker_memory(), which sets RLIMIT_AS soft and hard to 4 GiB on the calling process; every Singular child inherits it, so the per-call cap (prlimit or cgroup, 4 or 16 GiB) never governed. The earlier '16 GiB fixes it' reading was wrong: that run's pass is unexplained by the cap. Fix: the row analysis no longer sets RLIMIT_AS; the cgroup MemoryMax of _run_singular bounds each call, and the whole producer runs under an outer 20G scope. Regeneration in progress.
- 2026-10-29 Greater-picture consult (brief greater-picture-brief.md; answers greater-picture-gpt-daybreak-blue-latest.md and greater-picture-gpt-6.1-terra.md, both read-only, medium). Both converge: (1) exact arc families x(s,u) on Y through the base point, leading G-vector F(u), exact containment in each minimal prime of sqrt(K2) and a nonzero dim-sized Jacobian minor certify reduced support per component without saturation; VB (two dim-3 primes) and X- (one dim-3 prime) first. (2) Syzygy/Jacobian-dual presentation probe on VB as a scheme route only with verified hypotheses. (3) VB h4 vs 155 (quadratic-model value) as a diagnostic: h4<155 exhibits a new relation; equality closes nothing. (4) Stop unchanged pivot saturation, std(L), full-graph msolve, local ds, minAssGTZ-first, RLIMIT_AS. Neither claims any current measurement decides support for any pair. VB h4 launched (8 GiB, 1 h).


===== FILE: lab-map.md =====

# Lab map: every machine, service and API available to the repository (2026-10-29 UTC)

Evidence tags: **M** = measured by a command run on 2026-10-29 for this map; **M0** = measured on 2026-10-29 and
carried over from the previous version of this file (not rerun); **D** = documented in the cited file, whose own
date governs. Paths are relative to the primary checkout (~/Projects/IBMQuantum) unless they begin with `~`.
Credential files are named by environment variable or path pattern only. Policy authorities: AGENTS.md (approval
rules), docs/runbooks/compute-flags.md (flag review, memory rule), docs/PYTHON.md (interpreters),
docs/notes/kaggle/ (Kaggle). Live provider pages outrank every D row.

Standing rules that bind every layer below (AGENTS.md "Hardware services", "QPU time and calibration", "Seeds"):

| Rule | Statement | Tag | Source |
| --- | --- | --- | --- |
| Job approval | every job (QPU, emulator, simulator, mock), upload, provider QRNG read, timeslot booking and notebook session on any provider waits for the user's approval of a written case | D | AGENTS.md |
| Routing | simulation of 14 qubits or fewer runs on Kaggle; 15 qubits is decision-gated; IBM hardware serves 16 or more qubits or a device-itself question | D | AGENTS.md |
| Seeds | every new random seed comes from a QRNG draw (ANU first) | D | AGENTS.md "Seeds" |
| Flag review | every costly command passes docs/runbooks/compute-flags.md first | D | AGENTS.md |
| Read-only | status, calibration, catalogue and balance reads need no approval | D | AGENTS.md; docs/notes/ibm_quantum/account-access.md |

## 1. Local hardware (build host)

| Resource | Value | Tag | Source |
| --- | --- | --- | --- |
| CPU | AMD Ryzen 5 5600X3D, 6 cores / 12 threads, 96 MiB L3 | M | `lscpu` |
| RAM | 62 GiB total; 32 GiB used and 30 GiB available at read time; swap is not headroom | M | `free -g` |
| GPU | NVIDIA GeForce RTX 4070 Ti, 12,282 MiB, driver 615.78.08, SM 89 (Aer, cuStateVec; no GPU path for Groebner or rank) | M | `nvidia-smi`; docs/PYTHON.md |
| CUDA stack | CUDA 13.4.3, cuQuantum 26.09.0.8 (libcustatevec.so.1, libcutensornet.so.2), cutensor 2.8.1.0 | D | docs/PYTHON.md |
| Disk, root | 3.6 TB NVMe, 3.2 TB used, 394 GB free (90 % full) | M | `df -h /` |
| Disk, /tmp | 125 GB, 58 GB free, separate device | M | `df -h /tmp` |
| OS | CachyOS (Arch), Linux 7.2.11-1-cachyos | M | environment |
| Simulator ceilings | GPU density matrix 14 qubits, statevector 29; CPU density matrix 15 (17 s), statevector 31 (74 s); never CPU widths above 56 GiB (DM 16, SV 32) | D | memory note build-host-substrate.md (2026-10-16); docs/notes/kaggle/substrates.md |
| Memory rule | every heavy job in a `systemd-run --user --scope -p MemoryMax=NG -p MemorySwapMax=0` scope; systemd-oomd kills the session tab above about 90 % RAM+swap (incident 09:45 UTC 2026-10-29); never `prlimit --as` | M0 | docs/runbooks/compute-flags.md |
| Timers | user unit `gororoba-credits.timer` (daily 14:00 UTC provider-credit snapshot) is active | M | `systemctl --user is-active` |
| Container runtime | podman builds the runner-image replay (`ci/runner_image.sh`) | D | ci/AGENTS.md |
| Cleanup classes | scratch / rebuildable / retained / credential; deletion through `trash-put` | D | docs/runbooks/cache-locations.md |
| Cache root | `${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum` (`$GQ`); CI venv `ci-py3.14.7-qiskit261` | M0 | docs/runbooks/cache-locations.md |
| Credential store | `~/.qiskit/qiskit-ibm.json`, `~/.config/<provider>/...` mode 600, `~/.quantuminspire/config.json`, `~/.aws/config` | D | AGENTS.md "Records"; provider guides |

## 2. Local software stacks and interpreters

| Environment | Interpreter variable and location | Contents | Tag | Source |
| --- | --- | --- | --- | --- |
| Build host system | `$PYTHON` (Python 3.14, system) | qiskit 2.6.1, qiskit-aer-cuda 0.18.2-3 (cuStateVec), qiskit-ibm-runtime 0.51.0, samplomatic 0.21.0, Perceval 1.3.1, numpy, scipy, sympy, python-flint, cvxpy, mcp | D | docs/PYTHON.md; docs/notes/build_host/python-stack.md |
| CI / PR | Python 3.14.7, `ci/pinned_tool.py` | ruff 0.17.1, mypy 2.4.0 via uv; `ci/requirements-ci.txt` | D | docs/PYTHON.md |
| Browser checks | `ci/requirements-browser.txt` | playwright 1.64.0 | D | docs/PYTHON.md |
| Replay runtime | `REPLAY_PYTHON` | Qiskit 2.5.2, pydantic 2.13.5, ibm-quantum-schemas 0.12.20260921, samplomatic 0.21.0; gates marked runtime `qiskit-2.5` | D | docs/PYTHON.md; ci/requirements-replay.txt |
| Quantum Inspire | `QI_PYTHON`, `QI_ENV=~/.local/share/quantuminspire/venv` (Python 3.13) | quantuminspire 4.1.0, qxelarator, libqasm, opensquirrel, qiskit-quantuminspire (Qiskit < 2.4) | D | docs/notes/quantum_inspire/README.md |
| Open Quantum | `OQ_PYTHON`, `OQ_ENV=~/.local/share/openquantum/venv` (Python 3.14) | openquantum-sdk 1.0.0, openquantum-mcp 0.2.0, openquantum-sdk-qiskit 1.0.0, qiskit 2.5.2 | D | docs/notes/open_quantum/README.md |
| Quandela | system `$PYTHON` for Perceval; `QD_PYTHON` for the MCP server | perceval-quandela 1.3.1, exqalibur 1.4.2, scmver, mcp 1.29.0 | D | docs/notes/quandela/README.md |
| IQM Resonance | `iqm-python`, `/opt/iqm-resonance-stack` (Python 3.13, IQM OS 4.7) | iqm-client 36.0.0, qiskit 2.1.2, cirq-core, qrisp, iqm-pulla 15, iqm-pulse 15 | D | docs/notes/iqm/README.md |
| IonQ | `IONQ_PYTHON=/usr/bin/ionq-python` (`/opt/ionq-stack`, Python 3.13) or `~/.local/share/ionq/venv` | qiskit-ionq 1.1.1, Qiskit 2.6.1 | D | docs/notes/ionq/README.md |
| BlueQubit | `BQ_PYTHON=/usr/bin/bluequbit-python` (`/opt/bluequbit-stack`) | bluequbit 0.19.0b1 | D | docs/notes/bluequbit/README.md |
| Quafu | `QF_PYTHON=/usr/bin/quafu-python` (`/opt/quafu-stack`, Python 3.11) | pyquafu 0.4.5, numpy 1.26.4 | D | docs/notes/quafu/README.md |
| Origin Quantum | `OG_PYTHON=/usr/bin/originquantum-python` (`/opt/originquantum-stack`) | pyqpanda3 0.5.0 | D | docs/notes/originquantum/README.md |
| qBraid | `QB_PYTHON=/usr/bin/qbraid-python` (`/opt/qbraid-stack`); license keeps it on this machine | qbraid 0.13.0, qbraid-core 0.6.36 | D | docs/notes/qbraid/README.md |
| Planck | `PL_PYTHON=/usr/bin/planck-python`; account deleted 2026-10-25, package uninstalled, PKGBUILD kept | planck_sdk 1.0.0 | D | docs/notes/planck/README.md |
| Kaggle client | `kaggle` CLI 2.2.4, kagglesdk 0.1.37, kagglehub 1.0.2 as Arch packages | CLI, SDK, MCP at the Kaggle web host | D | docs/notes/kaggle/interfaces.md; libraries.md |
| AWS client | aws-cli v2 2.37.9 (Arch `extra`), profile `gororoba` | CLI, `uvx` proxy for `aws-mcp` | D | docs/notes/aws/README.md |
| Azure client | azure-cli 2.90.0 with `quantum` extension 1.0.0b30 | CLI | D | docs/notes/azure/README.md |
| Packaging | paru at /usr/bin/paru; `makepkg -si` in each PKGBUILD directory | local Arch packages | M | `which paru`; docs/notes/quandela/README.md |
| Package tree | 100 directories holding a PKGBUILD in ~/Github/PKGBUILDs | see section 3 | M | `ls -d */PKGBUILD` |
| Wheel packaging | `packaging/qiskit-aer-cuda/` (build==1.6.0, scikit-build==0.19.1, pybind11==3.1.0) | custom CUDA 13 Aer wheel | D | docs/PYTHON.md |
| Library register | 362 distributions with role and importing files | gate core-630 | D | docs/state/hypercomplex-libraries/libraries.md |
| Required environment | `export PYTHON="${PYTHON:-python3}"` and `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` | an unexported `PYTHON` makes every gate exit 127 | D | AGENTS.md |

## 3. Algebra and symbolic tools

| Tool | Version | Role | Tag | Source |
| --- | --- | --- | --- | --- |
| Singular | 4.4.1 (x86_64, built 2026-06-30) | Groebner, `minAssGTZ`, `sat`; global orderings (`dp`, `lp`) only for exact replays | M | `Singular --version`; AGENTS.md "Computer algebra" |
| msolve | 0.11.0 | F4 elimination; flags in compute-flags.md (`-e`, `-g`, `-t`, `-s`, `-u`, `-l`) | M | `msolve -V`; docs/runbooks/compute-flags.md |
| Macaulay2 | 1.26.06-3 (makepkg build, dirty tree) | computer algebra | M | `M2 --version` |
| SageMath | 10.10 | exact algebraic geometry, rotation-composite audits | M | `sage --version` |
| PARI/GP | 2.19.0 | number theory | M | `gp --version-short` |
| giac | installed (`giac --version` printed no version line) | CAS | M | `giac --version` |
| python-flint | 0.9.0 (`nmod_mat` rank and nullspace) | modular rank, rational null spaces | M | `python3 -c "import flint"` |
| GAP, Maxima | on PATH (versions not read) | group theory, CAS | M | `which gap maxima` |
| Absent | Magma, Maple, Julia/OSCAR, CoCoA5 | none available | M | `which` |
| Rocq (opam) | pinned in `ci/rocq_toolchain.pin`; 9.3 with `-w @all` | formal certificates under proofs/ | D | ci/AGENTS.md; memory open-gororoba-rocq-reuse |
| Algebra reference packages | 17 hypercomplex packages (octonion, splitoct, clifford, galgebra, ...) checked against `cd_core` | tables in docs/evidence/algebra_packages/tables.json | D | docs/PYTHON.md |
| Exact arithmetic | `pyadic` (finite-field and p-adic valuations) | no Cayley-Dickson table | D | docs/PYTHON.md |
| Notable local PKGBUILDs | python-flint, python-qiskit-aer(-cuda), python-qiskit-ibm-runtime, python-qiskit-experiments, python-qiskit-serverless, python-qiskit-addon-{slc,utils}, python-perceval-quandela, python-perceval-interop, cuquantum, python-cuquantum, quantuminspire-qiskit-stack, iqm-resonance-stack, qbraid-stack, ionq-stack, bluequbit-stack, quafu-stack, originquantum-stack, planck-stack, kaggle-benchmarks-stack, kaggle-environments-stack, quantum-pipeline-stack | M | `ls -d */` in ~/Github/PKGBUILDs |
| Singular on remote VMs | from sage wheels (`~/tools/sage_wheels/bin/Singular`) plus msolve | Azure VM tools | M0 | prior lab-map |
| Flag authority | memory and time limits, threads, environment checked per tool against `--help` before every run | | D | docs/runbooks/compute-flags.md |
| Cost levers | planner stages, ghost replay, noise-model serialization reuse | | D | docs/runbooks/simulation-cost-levers.md |

## 4. Quantum providers

Common facts: every submit, upload, timeslot booking and QRNG read needs an approved case. "Read" means a
read-only call that spends nothing.

### 4.1 IBM Quantum (Heron r2)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Devices | ibm_fez, ibm_kingston, ibm_marrakesh: Heron r2, 156 qubits, heavy-hex, 352 coupling pairs, dt 4 ns | D | AGENTS.md; docs/notes/ibm_heron_platform.md |
| Basis | cz, id, rz, sx, x, xslow; fractional rx and rzz; measure_2, reset_2, dynamic circuits; `rep_delay_range` [0, 0.002] s | D | docs/notes/ibm_quantum/account-access.md; fractional-gates.md |
| Pulse access | removed by IBM on 2025-02-03 | D | AGENTS.md |
| Access route | qiskit-ibm-runtime 0.51 under `$PYTHON`; `gororoba_quantum/ibm_account.py open_service`; no IBM MCP server | D | docs/notes/ibm_quantum/account-access.md |
| Accounts | two saved accounts in `~/.qiskit/qiskit-ibm.json`: default (primary) and `backup-ibm-quantum-platform`; `GOROROBA_IBM_ACCOUNT` selects; quotas never pool | D | AGENTS.md; account-access.md |
| Quota | 600 s of quantum time per account on a rolling 28-day window; no reset date; the backup serves when primary remaining minus reserve falls below the case's summed ceilings | D | AGENTS.md "QPU time"; docs/notes/ibm_quantum/qpu-submission.md |
| Read surfaces | `service.usage()`, `backends()`, `backend.status()`, `.target`, `.properties()`, `.configuration()`, `service.jobs()`, `job.metrics()`, `job.result()` | D | account-access.md |
| Billing | per sub-job QPU lock time; failed jobs bill lock time consumed (2 to 5 s on four 2026-10-18 jobs) | D | account-access.md; ibm_heron_platform.md |
| Approval | every `--submit` waits for a written case; `sh scripts/approved_run.sh --check CMD -- FLAGS` binds dry run and submit; `--approved-record(-sha256)`, `--max-execution-seconds` | D | AGENTS.md |
| Calibration | fetched afresh by `live_run.py` in the deciding process; cadence 30 to 40 min; `scripts/wait_calibration.sh` chains a start | D | AGENTS.md; memory ibm-calibration-reads |
| Controls | `--exclude-qubits`, `approved_backend_scope`, calibration fingerprints, prediction reuse | D | docs/notes/ibm_quantum/qpu-submission.md; hardware-controls.md |
| Dynamic-circuit split | mid-circuit measurement, reset or feed-forward circuits go in their own job with twirling and DD off | D | AGENTS.md "Qiskit skills" |
| Reference docs | 18 transcribed guides (processor types, transpiler stages, timing, repetition rate, calibration jobs, run-time estimate) | D | docs/notes/ibm_quantum/README.md |
| Live data | `docs/evidence/heron_platform/targets.json` snapshots all 156 qubits and 352 pairs | D | AGENTS.md |

### 4.2 Quantum Inspire (QuTech)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Backends | QX emulator (10 qubits per API), Ry emulator (9 qubits, neutral-atom model), Tuna-5 (5 transmons, offline), Tuna-9 (9 transmons, offline), Tuna-17 (17 transmons, 24 couplers, online) | D | docs/notes/quantum_inspire/backends.md |
| Shots and run limit | 1024 to 2048 on emulators; 8192 default and 131072 maximum on Tuna; 300 s on Tuna, 3600 s on emulators | D | backends.md |
| Account | one free account type with access to every listed backend; transaction ledger shows no metered charge after 42 jobs (2026-10-16) | D | docs/notes/quantum_inspire/usage.md |
| Access routes | `qi` CLI (4.1.0), REST, SDK, Qiskit, PennyLane; login `qi login`; tokens in `~/.quantuminspire/config.json` | D | setup.md; AGENTS.md |
| MCP | `quantum-inspire`: qi_backends, qi_backend, qi_compile, qi_submit, qi_submit_case, qi_run_local, qi_job(s), qi_results, qi_usage, qi_hardware_status, qi_performance_dashboard, qi_performance_query | D | docs/notes/quantum_inspire/mcp.md; MCP tool list |
| Exposes | submit, compile, local qxelarator run, job and result reads, usage ledger, public Grafana status and calibration | D | mcp.md |
| Limits | Tuna-9 Q8 carries a two-level-system message; Tuna-17 q9 idle P1 about 0.27 (design without q9); 30 s pause between batches, ladder to 120 s on failure, 3 circuits | D | tuna-9.md; memory tuna17-q9-readout-shift |
| Result order | qubit-0-leftmost on Ry; see `qx-runs.md` for the measurement-register root cause | D | ry-emulator.md; qx-runs.md |

### 4.3 Open Quantum (broker)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Backends | aqt:ibex-q1 (12 trapped-ion), ionq:forte-1 and ionq:forte-ent (36 trapped-ion), iqm:emerald (54), iqm:garnet (20), rigetti:cepheus-1-108q (108, 107 per job) | D | docs/notes/open_quantum/README.md facts table |
| Credits | Spark 25 granted at signup and every 90 days (claimed by hand), Public plan only, expire after 90 days; Full credits purchased, expire after 12 months; refund on failure or cancel | D | open_quantum/README.md "Accounts, credits and public runs" |
| Cost rule | credits = ceil(per_task + shots x per_shot), per_task 0.18 USD-equivalent; Private plan twice Public; Priority +2 credits; minimum 1 credit per job | D | open_quantum/README.md |
| Privacy | Public Compute makes every circuit and result public; unpublished methods stay off it | D | AGENTS.md |
| Access | SDK 1.0.0 (`OpenQuantumClient`, `SchedulerClient`), SDK CLI, Qiskit plugin (`OQBackend`, `OQSampler`, `OQEstimator`), portal; key file named by `OPENQUANTUM_SDK_KEY` (path `~/.config/openquantum/sdk-key.json`) | D | open_quantum/README.md |
| MCP | `openquantum`, 13 tools: list_organizations, get_credits, list_backends, get_backend, list_job_categories, prepare_job, submit_job, wait_for_job, get_job, list_jobs, get_job_results, get_job_calibration, cancel_job; `OPENQUANTUM_MCP_MAX_CREDITS` 1 here; `confirm_spend` gates Full credit spend | D | open_quantum/README.md; MCP server instructions |
| Read-only snapshot | `scripts/oq_platform.py snapshot` (organizations, credits, backends, constraint documents, categories) | D | open_quantum/README.md |

### 4.4 Quandela Cloud (photonic)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| QPUs | qpu:ascella (1..12 modes, 1..6 photons), qpu:belenos (1..24 modes, 1..12 photons); threshold detectors; 300 s per job | D | docs/notes/quandela/README.md platform table |
| Simulators | sim:ascella (Arcturus), sim:belenos, sim:slos, sim:sampling, sim:gpu:small, sim:gpu:medium (decommissioned) | D | same |
| Credits | Explorer offer: 200 free credits per calendar month (UTC reset, no carry-over); QPU 1.0 base credit per job plus 1e-06 per shot; simulators bill fractional per-shot credit | D | quandela/README.md "Explorer plan"; legal ToS 13.3 |
| Access | REST https://api.cloud.quandela.com; Perceval 1.3.1 (system Python); `scripts/qd_platform.py`; token file named by `QUANDELA_TOKEN_FILE`; Jupyter, Quantum Toolbox, Usage Explorer on the portal | D | quandela/README.md |
| MCP | `quandela` (repository-owned, `scripts/qd_mcp_server.py`, `QD_PYTHON`): qd_platforms, qd_platform, qd_availability, qd_plan, qd_simulate_local, qd_job_status, qd_job_result, qd_job_billing, qd_cancel_job, qd_usage; verb-specific Bash denies guard the token | D | quandela/README.md; memory quandela-token-deny-rules |
| Local simulation | `qd_simulate_local` (SLOS, Naive; at most 24 modes, 1,000,000 output states) | D | quandela/README.md |
| Schedules | GitHub Actions `quandela-schedule.yml` and `quandela-record-watch.yml` | D | docs/runbooks/quandela-scheduled-runs.md; .github/workflows |
| Caution | shared token: other sessions can cancel our jobs | D | memory quandela-shared-token-cancels |

### 4.5 IQM Resonance (superconducting)

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Emerald | 54 qubits, 90 couplings, 20000 shots, 100 circuits, 0.75 credits/s, timeslot 2400 per hour | D | docs/notes/iqm/README.md facts table |
| Garnet | 20 qubits, 30 couplings, 20000 shots, 100 circuits, 0.50 credits/s, timeslot 1800 per hour | D | same |
| Sirius | 16 qubits plus COMPR1 resonator, 24 couplings, `move` gate, 0.30 credits/s, timeslot 1080 per hour | D | same |
| Mocks | emerald:mock (54), garnet:mock (20), sirius:mock (24); free | D | same |
| Account | PERSONAL; 30.00 credits expiring 2026-11-01 (monthly grant, up to 30 credits per month); 2.50 left on 2026-10-26 | D | iqm/README.md; memory iqm-billing-and-reset-facts |
| Gates | cc_prx, cz, measure, measure_012, prx, prx_12, reset_wait; cc_prx needs passive reset and same-probe-line pairs | D | iqm/README.md; memory |
| Access | IQM Server API v1 https://resonance.iqm.tech; iqm-client 36.0.0; token pair file named by `IQM_TOKENS_FILE` | D | iqm/README.md |
| MCP | `iqm`: iqm_quantum_computers, iqm_quantum_computer, iqm_architecture, iqm_metrics, iqm_queue_availability, iqm_timeslots, iqm_job, iqm_job_artifact, iqm_cancel_job, iqm_credit, iqm_tokens, iqm_artifact | D | MCP tool list; iqm/README.md |
| Exposes | submit circuit, run (protobuf) and sweep; calibration sets and dynamic architecture; queue availability; timeslot book and cancel; GraphQL credit | D | iqm/README.md API table |
| Billing | ceil(runtime in seconds) x rate; mocks free | D | memory iqm-billing-and-reset-facts |

### 4.6 Other providers

| Provider | Devices | Quota and cost | Access | Status | Tag | Source |
| --- | --- | --- | --- | --- | --- | --- |
| IonQ | simulator (29 qubits, noise models ideal, aria-1, aria-2, forte-1, forte-enterprise-1); qpu.forte-1 (36, all-to-all) | simulator free; QPU needs organization credit (0.249 credits per compute second); 1,000,000 shots, 5000 circuits per job | REST api.ionq.co/v0.4; key at `~/.config/ionq/api-key`; `GET /jobs/estimate` creates nothing | simulator-only key; no adapter yet | D | docs/notes/ionq/README.md |
| BlueQubit | cpu (34 qubits statevector), mps.cpu (96), pauli-path (192), GPU variants, quantum (108) | Free: cpu 50,000 jobs per day, 60 min per job; others credit-only; balance read by `GET /balance` | REST app.bluequbit.io/api/v1; key at `~/.config/bluequbit/api-key`; `bq.estimate()` counts as a submission | Free plan inferred; no adapter yet | D | docs/notes/bluequbit/README.md |
| Quafu (BAQIS) | ScQ-Sim10, ScQ-P5 (5, queue about 1750), Baihua (119) online; others offline or obsolete | no quota route; browser only | pyquafu 0.4.5; token at `~/.config/quafu/api-token` | open access; no adapter yet | D | docs/notes/quafu/README.md |
| Origin Quantum | WK_C180 (166 usable of 180), WK_C180_2 (17), WK_C180_3 (30), PQPUMESH8 (3); simulators 35 / 68 / 200 | 60 s Wukong grant at registration; usage = 0.3 s overhead x multiplier + runtime | pyqpanda3 0.5.0; key at `~/.config/originquantum/api-key`; HTTPS URL passed explicitly | no adapter yet | D | docs/notes/originquantum/README.md |
| qBraid | 38-device catalogue (broker to Braket, Azure, IonQ, IQM, Rigetti, Open Quantum); own CPU and GPU simulators; Lab | Free tier: 100 jobs per simulator per UTC day; 25 GPU circuits per day; 100 Lab CPU hours (renews 2026-11-10); AI allowance 5 USD; 0 credits; 1000 requests per 15 min | REST api-v2.qbraid.com/api/v1; key at `~/.config/qbraid/api-key` | Free; read-only catalogue plus simulators | D | docs/notes/qbraid/README.md |
| Planck | digital twin (returns random bits) | none | account deleted 2026-10-25 | closed; source audit only | D | docs/notes/planck/README.md |
| Azure Quantum | quantinuum.sim.h2-1sc (syntax checker), h2-1e (emulator), pasqal.sim.emu-free, rigetti.sim.qvm; no hardware | 1,000 eHQC one-time on H2 emulator (HQC = 5 + C(N1q + 10 N2q + 5 Nm)/5000); Pasqal 5 emulator hours per month | `az quantum` extension; workspace `gororoba-quantum`, eastus | free plans only; trial spending limit on | D | docs/notes/azure/README.md |
| AWS Braket | not available to the project (managed SCP denies every Braket call) | n/a | n/a | excluded | D | docs/notes/aws/README.md |

## 5. QRNG sources (seed draws)

| Order | Source | Quota | Credential | Approval | Tag | Source |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ANU Quantum Numbers (keyed), `scripts/anu_qrng.py draw` | 100 requests per calendar month, 1 per second, up to 1024 uint16 values per request | key file under `~/.config/anu-qrng/` (mode 600) | none | D | docs/notes/qrng/README.md |
| 2 | ANU legacy (keyless), `draw --source legacy` | 1 request per minute; to be retired | none | none | D | same |
| 3 | Cisco Outshift QRNG, `scripts/outshift_qrng.py draw` | 100000 bits per month; 1 to 10000 bits per block, 1 to 1000 blocks per request | key file under `~/.config/outshift-qrng/` | none | D | same |
| 4 | Quandela Cloud QRNG, `scripts/quandela_qrng.py draw --approved-case FILE` | priced per byte through the account offer; CHSH must exceed 2 and stay at most 2 sqrt 2 | Quandela token | approved case required | D | same |
| pending | QCi uQRNG | free to 1 Gbit per month | token pending | n/a | D | same |

Each draw writes `docs/evidence/<source>/draw-<UTC>.json` with raw bytes and sha256; `ci/seed_provenance.py`
requires every integer seed literal to be a row of `ci/reproduction_seeds.json` or an allocation in
`docs/evidence/qrng_seeds/allocations.json`; runtime seeds go through `qrng_seeds.add_seed_argument`
(`qrng:<draw>#<index>`, the flag default, or `repro:<integer>`) (D, AGENTS.md "Seeds").

## 6. Cloud compute

| Platform | Resource | Value | Tag | Source |
| --- | --- | --- | --- | --- |
| Azure VM | size | Standard_FX4mds_v2: 4 vCPU, about 82 GiB RAM, retail about 0.547 USD/h | M0 | prior lab-map |
| Azure VM | quota | 4 regional vCPUs in eastus and 4 in westus2: one FX4mds_v2 per region at a time | M0 | prior lab-map |
| Azure VM | instances | gororoba-a5-fiber (eastus) and gororoba-a5-fiber-2 (westus2), both deallocated, disks retained; a case file is required per VM start (approved: azure-cases/vm2-fiber-b.md) | M0 | prior lab-map |
| Azure VM | failures | address-space cap at 32 GiB stopped e8_nm_fiber at 17 h; VM 2 lost ssh at about 20:38 UTC with 58 GB headroom (cause unidentified) | M0 | prior lab-map |
| Azure subscription | offer | FreeTrial_2014-09-01, 200 USD credit for 30 days, spending limit on; upgrade is the owner's decision | D | docs/notes/azure/README.md |
| Kaggle TPU | v5e-8 VM | 224 logical CPUs (`os.cpu_count`), about 390 to 400 GB available RAM; 9 h session cap, 20 h per week | M0 | prior lab-map; docs/notes/kaggle/README.md |
| Kaggle TPU | quota | 7,390 s used of 72,000 s; refresh 2026-10-31T00:00Z | M0 | prior lab-map |
| Kaggle GPU | T4 x2 or P100 | 11,920 s used of 108,000 s; at most two GPU batch sessions per account; 29 to 30 GB host RAM, 4 cores, 12 h | M0 / D | prior lab-map; substrates.md |
| Kaggle CPU | session | 4 cores, about 30 GB, 12 h; no accelerator quota; 20 GB saved output | M0 / D | prior lab-map; docs/notes/kaggle/README.md |
| Kaggle observed | msolve E8bar to VB | degree-16 matrix 86M x 88M, peak about 209 GB, about 23 effective cores, cancelled near 7,380 s (initiator unresolved) | M0 | prior lab-map |
| Kaggle observed | TPU smoke kernel | a5-fiber-tpu-smoke queued 6+ h with no v5e-8 assignment; earlier TPU pushes ran on 4-core CPU machines | M0 / D | prior lab-map; tpu-research.md |
| Kaggle accelerators | IDs (Sept 2026) | NvidiaTeslaT4 (2 x T4), NvidiaTeslaA100, NvidiaL4, NvidiaL4X1, NvidiaH100, NvidiaRtxPro6000, TpuV5E8, TpuV6E8; push with `--accelerator` | D | docs/notes/kaggle/README.md |
| Kaggle interfaces | CLI 2.2.4, kagglesdk 0.1.37, kagglehub 1.0.2, MCP https://www.kaggle.com/mcp (76 tools: notebooks sessions, datasets, models, competitions, quota, benchmarks) | D | docs/notes/kaggle/interfaces.md; MCP tool list |
| Kaggle workflow | `scripts/kaggle_run.py push/status/collect`; `scripts/kaggle_sessions.py quota`; every GPU push needs `--timeout`; collect reads per-version output through kagglesdk | D | docs/notes/kaggle/workflow.md; interfaces.md |
| Kaggle capacity | T4 density matrix 14, statevector 29; T4 x2 cache blocking DM 15, SV 30; TPU host RAM 34/35 qubit SV (unreached) | D | docs/notes/kaggle/substrates.md |
| AWS | project on the free plan, Region us-east-2 (other regions denied), 100.00 USD credit (99.91 on 2026-10-28), plan end 2027-04-24; Braket excluded; no instances running | D | docs/notes/aws/README.md; free-plan-usage.md |
| AWS | tooling | `aws-mcp` server (proxy `mcp-proxy-for-aws==1.7.0`, profile `gororoba`), 24 installed skills, 115 remote skills (2026-10-24); sessions renew via `aws login`; 2026-10-29 re-read stopped on an expired session | D | docs/notes/aws/README.md |
| AWS | EC2 | ordinary On-Demand `RunInstances` allowed in us-east-2; host tenancy, instance-store root, spot denied | D | aws/README.md |
| GitHub Actions | hosted runners | `ubuntu-26.04` (jobs in pr.yml, ci.yml, null-shards.yml, quandela workflows), `ubuntu-24.04` (one ci.yml job), `ubuntu-latest` (pr-agent.yml); about 4 logical CPUs and 16 GB; standing approval for slow classical jobs and nulls | M / D | `grep runs-on .github/workflows`; docs/runbooks/ci-runtime.md |
| Provider credits | daily snapshot of IBM, Kaggle, IQM, Open Quantum, Quandela, Quantum Inspire, qBraid, BlueQubit, AWS, Azure, ANU; IonQ, Quafu, Origin Quantum read `not readable` | D | docs/runbooks/provider-credits.md |

## 7. Cloud LLM and APIs

| Service | Models and credit | Access | Tag | Source |
| --- | --- | --- | --- | --- |
| AWS Bedrock | ordinary inference is priced and draws the 100 USD plan credits; cross-region Bedrock invoke meters sit outside the region policy; the Bedrock-playground activity pays a 20 USD reward on completion (status NOT_STARTED); model list not captured in the repository | `aws bedrock-runtime` through profile `gororoba`; `aws-mcp`; skill `amazon-bedrock` | D | docs/notes/aws/free-plan-usage.md |
| AWS SageMaker, Rekognition, Lex, Polly | credit-metered; SageMaker free meter is a short trial and not active | AWS CLI | D | free-plan-usage.md |
| Azure AI services | none attached to the subscription; the only Azure resource is the Quantum workspace and its storage account | `az` | D | docs/notes/azure/README.md |
| Anthropic (Claude) | Claude Code session model; subagents capped at 2 at once (haiku lookup, sonnet build, opus review); usage-limited | Claude Code `Agent` tool | D | memory no-background-agents-except-haiku |
| OpenAI (through Codex CLI) | see section 8 | Codex CLI 0.165.0 | M | `codex --version` |
| Google Gemini API (through opencode) | 35 `google/` models, including gemini-2.5 and 3.x flash and pro, gemini-3.8-flash, gemini-4-argon, gemma-4 (26b, 31b), deep-research, image and Lyria models, embeddings | `opencode` 2.1.2 | M | `opencode models` |
| Google Antigravity (through opencode) | `google/antigravity-claude-opus-4-6-thinking`, `-claude-sonnet-4-6`, `-gemini-3-flash`, `-gemini-3-pro`, `-gemini-3.1-pro` | `opencode`; also `agy` CLI | M | `opencode models` |
| Groq (through opencode) | 7 models: allam-2-7b, llama-prompt-guard-2 (22m, 86m), gpt-oss-120b, gpt-oss-20b, gpt-oss-safeguard-20b, qwen3.8-27b | `opencode` | M | `opencode models` |
| OpenAI API (through opencode) | 83 `openai/` models | `opencode` | M | `opencode models` |
| Qwen (through opencode) | `qwen/coder-model` | `opencode` | M | `opencode models` |
| Gemini CLI 0.46.0 | installed, but refused: the client is retired for the individual tier | `gemini` | M / D | `gemini --version`; prior lab-map |

## 8. Local LLMs and review CLIs

| Tool | Version | Capability | Tag | Source |
| --- | --- | --- | --- | --- |
| Codex CLI | 0.165.0 | `codex exec -m MODEL -c model_reasoning_effort=EFFORT -s workspace-write -C DIR -o OUT`; models in models_cache.json: gpt-6.1-sol, gpt-6.1-terra (500k context), gpt-6-sol, gpt-6-astra, gpt-6-luna, gpt-5.6-sol, -terra, -luna, gpt-daybreak-blue-latest (272k to 500k context, efforts low to ultra); gpt-6-sol at low effort is the cheap delegate, gpt-6-astra costs more than a Claude frontier model and is never the delegate; hidden entries gpt-reserve and codex-auto-review | M | `codex --version`; ~/.codex/models_cache.json; ~/AGENTS.md |
| Codex review roles | reviews and diagnoses read-only (tmux TUI, gpt-daybreak-blue-latest LOW by default); Claude implements every change; hosted `@codex review` on pull requests is the only hosted reviewer | D | memory codex-cli-reviews-in-tmux; AGENTS.md "Reviews and merges" |
| opencode | 2.1.2 | multi-provider agent CLI: providers google (35), ollama (28), groq (7), openai (83), qwen (1) | M | `opencode models` |
| grok CLI | 1.0.70 (stable) | Grok Build TUI; flags `--agent`, `--agents`, `--allow`, `--deny`, `--always-approve`, `--cwd`, `--add-dir`, `--continue`; prior use: referee report docs/archive/reviews/2026-10-27-ascella-replication-review-grok.md | M / D | `grok --help` |
| agy CLI | 1.4.10 | `--print`, `--model`, `--effort low..max`, `--mode accept-edits/auto/plan`, `--output-format json/stream-json`, `--json-schema`, `mcp`, `models`, `plugin`, `--sandbox`; prior use: docs/archive/reviews/2026-10-27-ascella-replication-review-agy.md | M / D | `agy --help` |
| Gemini CLI | 0.46.0 | refused for this account tier | M | `gemini --version` |
| ollama | 0.40.7, local tags (27 listed) | glm-4.7-flash (19 GB; 64k and 128k variants; uncensored variant), qwythos-9b (10 GB; 64k, 128k), qwenseer-2b (1.3 GB), qwen3.8 distill 9b and 4b, qwen3.8-27b IQ2_XXS (8.2 GB; 64k, 128k), qwen3.5-4b, gemma-4-26b (17 GB; 256k), whiterabbitneo-2.5-coder-7b, foundation-sec-8b-instruct, rwkv7-g1k (7.9 GB) | M | `ollama list` |
| Local-LLM limit | 12 GiB VRAM; models above it spill to RAM; text outputs are never evidence | D | docs/notes/kaggle/substrates.md ("Gemma inference ... never evidence") |
| Claude subagents | max 2 at once; check usage before launching; two sonnet launches once consumed 94 % of the budget | D | memory agent-launch-usage-budget |
| MCP servers (repository) | `quantum-inspire`, `openquantum`, `quandela`, `iqm`, `kaggle`, plus `aws-mcp` (Claude, Codex, Gemini CLI, OpenCode, Windsurf, Grok, Agy) | D | AGENTS.md; docs/notes/aws/README.md; MCP tool list |
| Skills | migrate-qiskit-ibm-runtime (pinned upstream a5499c7c); 24 AWS skills; Codex skills under ../.codex/skills | D | AGENTS.md "Qiskit skills" |
| Review runbook | critical peer review criteria (12 items) | D | docs/runbooks/critical-peer-review.md |

## 9. CI

| Item | Value | Tag | Source |
| --- | --- | --- | --- |
| Workflows | ci.yml (nightly audit, 8 jobs), pr.yml (lint, types, tests, gates), null-shards.yml (2 jobs), pr-agent.yml, quandela-schedule.yml, quandela-record-watch.yml | M | `ls .github/workflows` |
| PR checks | `sh ci/pr_checks.sh lint|types|tests|gates`; branch protection requires all four on the head; gates of at most 15 measured seconds that the diff reaches | D | AGENTS.md |
| Audit | `ci.yml` runs every gate, retained-evidence replays, Rocq replays and the ledger nightly on main; a failing run updates the issue "Nightly audit failing" | D | AGENTS.md |
| Runner profile | about 4 logical CPUs, 16 GB, AMD EPYC 7763 / 9V45 / 9V74; Python 3.14.7; QI lane uses 3.13 | D | docs/runbooks/ci-runtime.md |
| Measured run cost | PR run 674 s wall, 2,678 s runner time; main run 2,885 s wall (1,040 s queue delay) | D | ci-runtime.md |
| Gate machinery | `ci/run_gates.py`, `ci/gates.json`, `ci/gate_ledger.py`, `ci/premerge_gates.py`, `ci/runner_image.sh` (podman replay), `ci/gate_timings.json` | D | ci/AGENTS.md; ci/ listing |
| Shards | null calibrations offloaded to GitHub Actions shards | D | docs/runbooks/null-shards.md |
| Style gates | `"$PYTHON" ci/pinned_tool.py ruff format --target-version py313`, `ruff check`, `mypy` | D | AGENTS.md |
| Review loop | `@codex review` per push; `scripts/codex_review_status.sh`, `scripts/resolve_answered_threads.sh`; merge via `gh api` REST with merge commit | D | AGENTS.md "Reviews and merges" |

## 10. Repo tree

| Path | What lives there | Tag | Source |
| --- | --- | --- | --- |
| gororoba_quantum/ | 169 entries: runtime modules run as scripts (not a package): `cd_core.py` (canonical Cayley-Dickson specification), `live_run.py`, `experiments.py`, `parallel.py`, `ibm_account.py`, `local_compute.py`, `qpu_planning.py` | M | `ls gororoba_quantum`; AGENTS.md |
| scripts/ | 321 entries: provider adapters (`qd_platform.py`, `qi_platform.py`, `oq_platform.py`, `iqm_platform.py`), MCP servers, QRNG draws, `kaggle_run.py`, `approved_run.sh`, `provider_credits.py`, plan tracker, source-registry tools | M | `ls scripts` |
| ci/ | gate runner, gate ledger, pins, replay and Rocq machinery, seed provenance, reproduction seeds | M | `ls ci` |
| tests/ | 27 top-level entries: pytest suites (`tests/scripts/`, gate-contract tests); the `audit` marker holds replays | M | `ls tests` |
| kaggle_kernel/ | `kernel_main.py`, `gpu_env_report.py`: the entry that runs inside Kaggle sessions | M | `ls kaggle_kernel` |
| proofs/ | Rocq certificates (TargetFlipN21, FoldAverageDescent, TerminalChannelSeparation, C881) | D | AGENTS.md |
| packaging/ | `qiskit-aer-cuda` wheel build | M | `ls packaging` |
| plans/ | plan records beside docs/state/plans.md | M | `ls plans` |
| literature/ | link to docs (`literature -> docs` keeps recorded paths) | D | AGENTS.md |
| docs/notes/ | provider guides (ibm_quantum, quantum_inspire, open_quantum, quandela, iqm, ionq, bluequbit, quafu, originquantum, planck, qbraid, aws, azure, kaggle, qrng, build_host), source notes, topic notes | M | `ls docs/notes` |
| docs/evidence/ | 150 replay and evidence directories (account snapshots, heron_platform targets, QRNG draws, ledgers) | M | `ls docs/evidence` |
| docs/runbooks/ | operator procedures (compute-flags, ci-runtime, cache-locations, provider-credits, simulation-cost-levers, null-shards, evidence-closure, plan-tracker) | M | `ls docs/runbooks` |
| docs/state/ | generated registries: research_state.json, plans, hypercomplex-libraries | D | AGENTS.md |
| docs/design, docs/archive, docs/sources, docs/pdf | designs and plans; handoffs and review reports; source ledgers; retained PDFs | M / D | docs/README.md |
| docs/local/ | ignored session scratch (this file, BUILD_HOST.md, plans) | D | AGENTS.md |
| results/ | audit records: hw_estimate, live, quandela, quantum_inspire, open_quantum, iqm, kaggle, local_compute, local-simulation, hypercomplex, ripple | M | `ls results` |
| Worktrees | 15 listed by `git worktree list` (primary checkout, one under `~/worktree`, one `a9e6`-named agent tree, twelve under `~/worktrees/IBMQuantum/<branch>` named for their topic, e.g. a5-kernel-attachments, kaggle-stacks, msq-envelope-backend, pin-baseline) | M | `git worktree list` |
| Current branch | experiment/ascella-21pair-octonion-atlas with uncommitted Ascella character scripts and results | D | gitStatus at session start |

## 11. Policy gates

| Gate | What it blocks | Tag | Source |
| --- | --- | --- | --- |
| Approved written case | any submit, upload, QRNG read, booking, notebook session | D | AGENTS.md |
| Approved record binding | `--submit` runs only after the plan matches the record's digest; a mismatch writes `approval_required` and sends nothing | D | AGENTS.md; qpu-submission.md |
| 15-qubit gate | a 15-qubit run waits for a written case naming the substrate | D | AGENTS.md |
| Public-data gate | Open Quantum Public Compute publishes circuits and results | D | AGENTS.md |
| Flag review | every solver, simulator, pool or launcher command | D | docs/runbooks/compute-flags.md |
| Memory scope | heavy jobs in capped `systemd-run` scopes, one at a time | M0 / D | compute-flags.md; memory oomd-kills-session-tab |
| Azure VM case file | each VM start needs a case file | M0 | prior lab-map |
| Spend policy | AWS credits and Azure trial: upgrade to a paid plan is the owner's decision alone | D | aws/README.md; azure/README.md |
| Seed provenance | integer seed literals must come from QRNG allocations or the reproduction ledger | D | ci/seed_provenance.py |
| Mock outcomes | `--native-dry-run` timing never enters scientific analysis | D | AGENTS.md |
| Retained bytes | files bound by a ledger or digest keep path and bytes | D | AGENTS.md "Documents" |
| Merge gate | pr.yml `lint`, `types`, `tests`, `gates` green plus Codex review loop | D | AGENTS.md |
| Delete | `trash-put`, never `rm -rf` | D | ~/AGENTS.md |
| Secrets | tokens, account ids, CRNs, emails, local absolute paths stay out of commits; an IBM instance is named by a 12-hex sha256 of its CRN | D | AGENTS.md "Records" |

## 12. Gaps (capabilities documented but not confirmed in this pass)

- Live provider state (queues, balances, device status) was not read: no provider call was permitted. Every Quantum
  Inspire, IQM, Quandela, Open Quantum, qBraid and IBM figure is the dated D value, and the credit snapshot
  (`latest.md` under `${XDG_STATE_HOME:-~/.local/state}/gororoba-quantum/credits/`) was not opened.
- Kaggle and Azure rows marked M0 (TPU and GPU quota used, VM state, Kaggle capacity) were not re-measured; the
  Kaggle TPU v5e-8 assignment has never been confirmed in this tree and earlier pushes ran on 4-core CPU machines.
- AWS Bedrock: the model list, regional availability and per-token credit cost are not recorded anywhere in docs/notes/aws;
  the AWS session had expired on 2026-10-29, so no live read was possible.
- Azure AI services (Foundry, OpenAI): no document and no resource; the subscription holds only the Quantum workspace.
- giac, GAP and Maxima versions were not captured; Rocq/opam version on this host was not run.
- IonQ, BlueQubit, Quafu and Origin Quantum have no adapter or MCP server; their guides record probes of 2026-10-24
  only, and Quafu and Origin Quantum quotas are readable only in a browser.
- Grok and agy model catalogues (`grok models`, `agy models`) were not listed; their provider credit and rate limits are
  undocumented in the repository.
- Local-LLM throughput on the RTX 4070 Ti and the ollama GPU offload fraction were not measured.
- QCi uQRNG token is pending; the Quandela QRNG `count` unit (bytes or integers) is unsettled until a first approved draw.
- Heron r3 and Nighthawk appear in docs/notes/ibm_quantum/processor-types.md, but the account reaches Heron r2 only.
- Remote-host CPU/RAM figures for the Azure VMs and Kaggle sessions are per prior measurement; no unified host
  inventory beyond the primary build host exists in the repository.

## 13. Review-model catalogues (measured 2026-10-29)

| CLI | Models | Tag | Source |
| --- | --- | --- | --- |
| grok 1.0.70 | grok-4.7 (default), grok-4.7-build-fast, grok-4.6, grok-4.5 | M | `grok models` |
| agy 1.4.10 | gemini-4-argon low/medium/high, gemini-3.8-flash low/medium/high, claude-opus-5-5 and claude-sonnet-5-5 low/medium/high, gpt-oss-120b medium | M | `agy models` |
| opencode 2.1.2 | groq: gpt-oss-120b, gpt-oss-20b, qwen3.8-27b (fast inference); google incl. antigravity and gemini-3.8-flash; openai; 28 ollama tags | M | `opencode models` |
| AWS Bedrock | session expired at read time; model list not captured | M | `aws` session state |


===== FILE: greater-picture-gpt-daybreak-blue-latest.md =====

`[O]` denotes a repository observation. `[I]` denotes an inference, proposed procedure, budget, or falsifier.

## Executive conclusion

[O] Method A computes an exact, bounded graded piece of the fiber cone over \(\mathbf F_{32009}\). Every completed degree therefore remains valid evidence. Method B and the candidate-ideal route both enter an unbounded mixed-variable standard-basis calculation after the pivot; six method-B attempts and one candidate-ideal attempt produced no complete fiber. [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:243)

[I] The next compute hour should buy either an independent relation-type bound or a dimension-certified family of genuine limits. Another unchanged saturation run only buys a seventh measurement of the same failure.

## 1. Diagnosis

[O] Method A fixes target degree \(d\) before Gröbner work. It forms only the degree-\(d\) target monomials, reduces every product modulo \(J\) factor by factor, computes \(\operatorname{std}(J+\mathfrak mP_d)\) in the source variables, and finishes with exact FLINT rank. [Driver](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_cone_driver.py:227) [Part B report](~/Projects/IBMQuantum/docs/local/a5-failed-runs/build/part-b-report.md:9)

[O] Method B instead computes \((H:g^\infty)\) before setting the source variables to zero. The mixed rings contain:

| Pair | Source variables | Target variables | Mixed variables |
|---|---:|---:|---:|
| E8bar-to-VB | 8 | 10 | 18 |
| X-minus | 7 | 15 | 22 |
| Iso | 6 | 17 | 23 |
| E8bar-to-N-plus/minus | 9 | 21 | 30 |
| W8-to-N-minus | 7 | 24 | 31 |

[O] The saturation must discover relations of unrestricted target degree while multiplying them by source polynomials. E8bar-to-VB proves that pivot size alone is not the cause: its pivot has only 9 terms, yet saturation stalled for 2 hours and `std(L)` stalled in the 18-variable candidate presentation. Iso used a 41-term pivot; X-minus used 64 terms. [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:243) [Part B report](~/Projects/IBMQuantum/docs/local/a5-failed-runs/build/part-b-report.md:31)

[O] Arithmetic occurs over a fixed prime field, so coefficient bit-length does not grow. The observed growth is monomial support, critical pairs, and sparse-matrix fill:

- The old 20-variable E8bar-to-VB graph retained roughly 49,000 pending pairs after peaking near 61,609.
- The msolve graph reached an \(86{,}010{,}243\times87{,}648{,}606\) degree-16 matrix and about 209 GB sampled RSS.
- E8bar-to-N-plus saturation reached 72 GB after 10 hours without passing the pivot stage. [TPU review](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/review-codex.md:26) [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:252)

[O] Global `dp` ordering is still the correct observed choice. Local `ds` created 2,401 Schreyer generators and reached 83 GB before W8 \(h_2\), whereas global method A completed \(h_2\) in 94 minutes at 6.7 GB. [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:106)

[I] The mechanism is therefore unbounded saturation degree plus mixed source-target fill. More RAM changes the failure point; it does not change the asymptotic problem. The logs expose no terminal saturation degree, so assigning one would be fiction.

## 2. Reformulations ranked by expected value

### 1. Genuine arc families with an exact dimension certificate

[I] This route has the highest expected value because it can prove reduced-support equality without computing the Rees ideal.

For each minimal prime \(P_\alpha\) of \(\sqrt{K_2}\):

1. Construct an exact algebraic family \(x(s,u)\) with \(J(x)=0\), \(x(0,u)=0\), and generic \(x(s,u)\) in the intended nullity-8 stratum.
2. Compute
   \[
   \nu=\min_i\operatorname{ord}_sG_i(x),\qquad
   c_i(u)=\left.s^{-\nu}G_i(x(s,u))\right|_{s=0}.
   \]
3. Verify \(c(u)\neq0\) and every generator of \(P_\alpha\) vanishes on \(c(u)\).
4. In a chart \(c_q=1\), exhibit a nonzero \(d_\alpha\times d_\alpha\) minor of
   \(\partial(c_i/c_q)/\partial u_j\), where \(d_\alpha=\dim P_\alpha\).

[I] Irreducibility, containment, and equal image dimension then prove that the image is dense in \(V(P_\alpha)\). One family is required for every component.

[O] The current `dense-family` implementation correctly treats finite points as a support lower bound only. [Certificate code](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:168)

[I] Falsifiers: a nonzero coefficient of \(J(x)\); generic departure from the source-orbit open set; all leading \(G_i\) equal zero; failure of a component equation; or Jacobian rank below \(\dim P_\alpha\).

### 2. Exact curve sections as an arc-discovery instrument

[I] For a germ of dimension \(r\), intersect \(J\) with \(r-1\) reproducible linear forms through the origin, isolate the one-dimensional components through the origin, normalize each curve, and evaluate \(G\) in every DVR branch above the origin:

```singular
LIB "normal.lib";
ring R=32009,(t(1..e)),dp;
ideal C=J,L(1),...,L(r-1);
if (dim(std(C))!=1) { "bad_section"; quit; }
list normalization_data=normal(C);
```

[I] Each normalization branch supplies a uniformizer \(s\) and therefore a genuine limit point. A truncated jet satisfying \(J\bmod s^M\) is insufficient unless a Hensel or implicit-function certificate proves liftability.

[I] Finite sections remain discovery/lower-bound evidence. Replacing numeric section coefficients by parameters and proving the image-rank condition above turns the construction into a support certificate.

[I] Initial budget: X sections at 3–8 GiB and 15 minutes each; one symbolic three-parameter family at 8–16 GiB and 2 hours. Abort the route if normalization reaches the same frontier as saturation or every image rank stays below three.

### 3. Degree-truncated method A, but only after earning a proof bound

[O] A finite sequence \(h_1,\ldots,h_D\) does not bound future relation degrees. Regularity of \(S/K_2\) says nothing about the unknown kernel \(K_F\supseteq K_2\). [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:23)

[I] A proof-producing stop requires one of:

- a theorem, with verified hypotheses, giving relation type \(\operatorname{rt}(I)\le D\);
- an independently certified Hilbert series for \(F(I)\);
- a candidate algebra surjecting onto \(F(I)\) with independently proved equal Hilbert series;
- a verified Cohen–Macaulay/reduction-number theorem yielding \(\operatorname{rt}(I)\le r(I)+1\).

Then run every degree through \(D\), retaining cumulative relation files:

```sh
systemd-run --user --scope \
  -p MemoryMax=8G -p MemorySwapMax=0 \
  "$PYTHON" ~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_cone_driver.py \
  --header HEADER.sing --degree D \
  --previous-relations relations-upto-dPREV.rel \
  --out OUT --prime 32009 --memory-gib 8 --timeout 7200
```

[I] Falsifier: a new relation above the proposed bound, or failure of any theorem hypothesis.

[I] `degBound=D; std(...)` alone is not a saturation certificate. Saturation can require a high power of \(g\) to reveal even a low target-degree relation. A Hilbert-driven stop is circular if the supplied Hilbert series comes from \(K_2\).

### 4. Syzygy and Jacobian-dual presentation

[I] Run the route first on E8bar-to-VB, then X-minus:

```macaulay2
A = (GF(32009)[t_1..t_e])/J;
I = ideal apply(G, g -> sub(g,A));
phi = syz gens I;
degrees source phi
```

[I] Check whether the presentation is linear, whether \(I\) is perfect of the required grade, the \(G_\ell\) Fitting-height conditions, Cohen–Macaulay hypotheses, and the reduction number. Only verified Morey–Ulrich-type hypotheses authorize a Jacobian-dual determinantal presentation.

[I] Without those hypotheses, the syzygy/Jacobian-dual equations define only a candidate \(L\). The candidate must pass the existing checks
\(H\subseteq L\subseteq\ker\phi\), \(L:g=L\), and equality of its special fiber with the proposed \(K\). [Candidate certificate](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:3)

[O] Linear type is already refuted: the measured nonzero quadratic relation ideals contradict a polynomial special fiber.

[I] Falsifiers: nonlinear presentation without an applicable generalized theorem; failed height conditions; failed colon/kernel checks; or syzygy computation reaching the same memory frontier.

### 5. One bounded Macaulay2 implementation comparison

[I] A bounded `ReesAlgebra` pilot is defensible because Macaulay2 begins with the symmetric-algebra presentation:

```macaulay2
needsPackage "ReesAlgebra";
A = (GF(32009)[t_1..t_e])/J;
I = ideal apply(G, g -> sub(g,A));
Rideal = reesIdeal(I,g);
Fideal = specialFiber(I,g);
```

[O] The installed package still saturates the symmetric ideal. Its declared `DegreeLimit`, `PairLimit`, and related options do not limit `reesIdeal`, so the pilot is an implementation/order comparison rather than a new completion theorem.

[I] Budget E8bar-to-VB at 8 GiB/2 hours and X-minus at 16 GiB/4 hours. Acceptance requires agreement with every certified \(h_d\) and \(K_2\). Timeout, memory exhaustion, or comparable basis growth ends the route.

### 6. Generic projective sections

[I] Generic sections can certify component degrees after component containment and coverage have been established:

```singular
ring Y=32009,(y(1..n)),dp;
ideal S=std(Component,L(1),...,L(dimComponent),y(q)-1);
vdim(S);
mult(S);
```

[I] Run the resulting zero-dimensional systems through Singular or msolve and repeat at a correctly regenerated second split prime. Section counts alone cannot establish component coverage; one component can be absent while another carries multiplicity.

### 7. SAGBI or initial-algebra degeneration

[I] Plain SAGBI on \(k[G_1,\ldots,G_n]\) computes relations \(f(G)=0\), whereas the fiber relation is \(f(G)\in J+\mathfrak mI^d\). Plain SAGBI therefore addresses the wrong algebra.

[I] A filtration-aware initial-Rees/SAGBI route becomes valid only after proving a flat degeneration and a finite SAGBI basis. Normaliz or 4ti2 becomes relevant only after that proof produces a semigroup presentation. A truncated SAGBI run remains diagnostic.

### 8. Multimodular reconstruction and Hensel lifting

[O] `fiber_inputs.py` can regenerate the inputs at \(p=32029\), root \(9115\). Replacing `32009` inside a specialized input is invalid. [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:242)

[I] Once any full modular ideal is available:

1. Repeat at several good split primes.
2. Require stable leading monomials and Hilbert series.
3. CRT/rationally reconstruct coefficients in \(\mathbf Q(i)\).
4. Verify all identities by exact substitution and ideal membership over \(\mathbf Q(i)\).

[I] Multimodular work detects bad primes and lifts a completed basis; it does not reduce the per-prime saturation frontier. Classical Hensel lifting offers little for the unresolved positive-dimensional ideal before such a basis exists.

## 3. What \(h_d\) and \(K_2\) decide now

[O] Every row below is certified only over \(\mathbf F_{32009}\). [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:181)

| Pair | Present conclusion | Exact extra fact closing reduced support |
|---|---|---|
| X-plus/minus | \(h=15,51,122\); \(K_2\) is nonradical; \(\sqrt{K_2}\) has one component of dimension 3, degree 12 | Prove \(\dim\operatorname{Proj}F=3\), equivalently construct one dense three-dimensional family of genuine limits. Irreducibility then forces support equality. Scheme equality still needs a relation bound or Rees certificate. |
| E8bar-to-VB | \(h=10,34,80\); \(K_2\) is radical with dimension-3 components of degrees 3 and 4 | Produce a dense rank-3 genuine-limit family in each component. Alternatively prove independently that the reduced fiber is pure dimension 3, contained in \(V(K_2)\), and has total degree 7 with component coverage. |
| E8bar-to-N-plus | \(h=21,83\); nonradical \(K_2\) has components \((4,11)\) and \((3,4)\) | Produce dense families of dimensions 4 and 3 in the respective components, or prove \(\sqrt{K_F}=\sqrt{K_2}\) directly. A dimension-4 witness alone says nothing about the lower-dimensional component. |
| E8bar-to-N-minus | Same measured \(h_1,h_2\), but a distinct input ideal | Same component analysis must be performed independently until an actual local/fiber isomorphism is proved. |
| Iso, W8 | Certified Hilbert segments, but radical/minimal-prime calculations did not finish in 600 seconds | First decompose \(\sqrt{K_2}\); then certify a dense genuine-limit family in every minimal component, or compute \(\sqrt{K_F}\) directly. |

[I] None of the present Hilbert segments decides reduced support by itself.

## 4. Arc-sampler receipt required for `support-equal`

[I] Extend the certificate format to bind:

- source-header SHA256 and field;
- exact section or explicit arc equations;
- branch prime and normalization/DVR map;
- proof that the branch lies in \(Y\), approaches the origin, and generically leaves the center;
- common valuation \(\nu\) and leading target coordinates;
- component-prime SHA256 and exact containment;
- parameter-space irreducibility;
- nonzero Jacobian minor or exact generic-fiber dimension;
- second-prime replay and separability check in positive characteristic.

[I] `fiber_certificates.py` may report `support-equal` only after every candidate component has such a receipt. Numeric samples alone must continue to report `support lower bound`.

## 5. Compute plan

| Rank | Substrate and work | Cap and deadline | Falsifier |
|---:|---|---|---|
| 1 | Host: finish radical/minimal-prime structure for \(K_2\); X arc-family discovery and dimension certificate | One job, 3–8 GiB initially; 15–60 min probes, at most 16 GiB/2 h for a symbolic family | Decomposition or family reaches the saturation-like frontier; image rank \(<3\) |
| 2 | Host: conditional relation-bound and syzygy/Jacobian-dual checks on VB, then X | 8 GiB/1 h VB; 16 GiB/2 h X | Required theorem hypotheses fail or syzygies show no smaller presentation |
| 3 | Host: one M2 symmetric-presentation pilot | 8 GiB/2 h VB; 16 GiB/4 h X | Same basis growth, timeout, or disagreement with certified degrees |
| 4 | Host or GitHub Actions: producer-regenerated second-prime method-A degrees and exact receipt verification | GitHub Actions 8–12 GiB, 30 min–2 h; host within the 24 GiB aggregate admission target | Any regenerated \(h_d\), relation dimension, or membership check differs |
| 5 | Kaggle CPU: one measured method-A degree, normalization batch, or zero-dimensional section | 24 GiB working budget; 10 h solver deadline within 12 h | Queue/setup/export cost loses to host, memory exceeds 30 GB, or outputs are not recoverable |
| 6 | Azure FX4mds_v2: only a reformulated computation whose host measurement requires more than 24 GiB | One 60–72 GiB job per VM, 6–10 h, zero swap, independent deallocation deadline | New formulation reproduces the post-pivot curve of the failed saturation |
| 7 | Kaggle TPU VM used as a large CPU host: several independent, receipt-producing reformulations only after smoke allocation | Keep aggregate RSS below roughly 296 GiB; 4 h pilot inside the 9 h session | Queue starvation, missing intermediate receipts, or another batch of unchanged timeouts |
| 8 | GitHub Actions: deterministic checks only | 16 GB runner ceiling | Any discovery job approaches the runner ceiling or ordinary pull-request latency |

[O] All host and Azure jobs require cgroup `MemoryMax`, `MemorySwapMax=0`, a live wall deadline, `MALLOC_ARENA_MAX=2`, and aggregate admission accounting. Kaggle requires a process-tree RSS watchdog. `RLIMIT_AS` is unsuitable. [Compute flags](~/Projects/IBMQuantum/docs/runbooks/compute-flags.md:46)

## 6. Stop doing

- [O] Stop extending unchanged Singular pivot saturation. Six runs ranging from the smallest VB case to E8bar at 72 GB/10 h stopped after the pivot.
- [O] Stop extending unchanged `std(L)` candidate-ideal runs. The 18-variable VB candidate failed before any colon or comparison check ran.
- [O] Stop full Rees-graph msolve elimination. The degree-16 matrix already consumed about 209 GB, while projected degree 19 exceeded the session envelope without a termination bound.
- [O] Stop local-`ds` syzygy routes. Global method A has already dominated them by orders of magnitude.
- [I] Stop W8 degree 3 unless a named finite-degree question needs \(h_3\). The computation cannot close the fiber without an independent bound.
- [O] Stop `minAssGTZ` on the large quadratic ideals. Radical followed by `minAssChar`, preferably in projective charts, is the supported route; GTZ densification remains an inference.
- [O] Stop every `prlimit --as` or inherited `RLIMIT_AS` memory cap.
- [O] Stop deadline extensions implemented by suspending `timeout`; replace the active timer while leaving the supervisor runnable.
- [I] Stop generic-line, finite-arc, or second-prime results from being described as completion evidence. Those procedures supply diagnostics, lower bounds, or arithmetic reproducibility until an explicit equality theorem closes the gap.

The strongest next milestone is a three-dimensional genuine-limit family dense in X’s unique reduced quadratic component. The certificate would settle X’s reduced attachment support at a fraction of the demonstrated saturation cost while preserving the unresolved nilpotent and characteristic-zero questions explicitly.



===== FILE: greater-picture-gpt-6.1-terra.md =====

The best next attempt is to construct **exact families of arcs for E8-bar→VB and X−**, then certify that their images are dense in every component of the quadratic upper bound. That route can establish reduced support without computing the full Rees ideal. It does not establish the fiber scheme, its multiplicities, or the attaching map itself.

The next scheme-level attempt should use independently justified relation bounds or a verified presentation of the Rees algebra. The current finite Hilbert-function measurements do not supply either bound. All computational recommendations below are proposals; this consultation ran no algebra jobs.

**Evidence labels:** “Observed” identifies a result recorded in the named file. “Inferred” identifies a mathematical consequence or a proposed experiment whose outcome remains open. Costs for new procedures are budgets, not measured runtimes.

## 1. Diagnosis

**Observed — [decision record, sections 5–9](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:65):** Method A works one degree at a time. It reduces products modulo the slice ideal \(J\), computes a global standard basis of \(J+\mathfrak m I^d\), and takes an exact finite-field rank. Its measured sizes include:

- X−: 122 normal cubic products; \(h_3=122\) in 598 seconds.
- Iso: 265 normal cubic products; \(h_3=265\) in 1,054 seconds.
- E8-bar→N+: 231 quadratic products; \(h_2=83\) in 6,029 seconds.
- W8→N−: 300 quadratic products; \(h_2=156\) in 5,619 seconds, with 6.7 GB peak.
- E8-bar→VB: 80 normal cubic products; \(h_3=80\) in 406 seconds.

**Observed — [method-B template](~/Projects/IBMQuantum/docs/local/a5-failed-runs/templates/b_body.sing:1) and [decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:181):** Method B forms \(H=J+(g y_j-G_jy_q)\) in the combined slice and target variables and computes \(H:g^\infty\) before setting the slice variables to zero. VB has eight slice and ten target variables; its candidate-ideal computation stalled in 18 variables. The selected pivots contain 64 terms for X−, 41 for Iso, and nine for VB. E8-bar→N+ reached 72 GB during a ten-hour saturation attempt.

**Inferred:** The decisive difference is **all-degree elimination before specialization**. Saturation must resolve relations involving slice variables and target variables, including intermediate relations that disappear when the slice variables are set to zero. Method A discards that all-degree burden and asks only for one finite quotient. The combined variable count and repeated critical-pair reductions provide a concrete mechanism for the growth; the logs do **not** establish the saturation exponent or maximum degree needed for completion.

**Observed — [compute-flags runbook](~/Projects/IBMQuantum/docs/runbooks/compute-flags.md:1):** The older E8-bar→N+ graph elimination reached an F4 matrix of 407,116 by 432,548 at degree seven. The VB TPU-VM graph reached an 86,010,243 by 87,648,606 sparse matrix at degree 16 and approximately 209 GB sampled peak RSS; it returned no basis ([TPU review](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/review-codex.md:1)). Those are graph-elimination measurements, not measurements of the pivot saturation’s hidden degree.

**Inferred:** Coefficient *bit-length* growth is not the explanation for these \(\mathbf F_{32009}\) runs: coefficients remain in a fixed finite field. Polynomial density, monomial count, pair selection and intermediate matrix size can grow enormously. Global `dp` helps the measured degree-wise membership problem; it does not guarantee a cheap saturation. Before attributing a future stall to a particular degree, retain `option(prot)` output or an equivalent solver trace with pair counts, leading degrees, RSS and elapsed time.

## 2. Ranked completion routes

### 1. Exact arc families and component dimensions — support certificate

**Inferred; first target VB, then X−.** For each prime component \(C\) of \(V(K_2)\), construct a rational parameter family of formal or algebraic curves \(t(s,u)\) satisfying
\[
t(0,u)=0,\quad J(t(s,u))=0,\quad
G(t(s,u))=s^e\bigl(F(u)+O(s)\bigr),\quad F(u)\ne0.
\]
The projective point \([F(u)]\) is then a genuine limit. Prove that its image is dense in \(C\). Since the certified quadrics contain the fiber, doing so for **every** minimal component proves equality of reduced projective supports.

A checkable pilot is:

```text
1. Choose polynomial or rational t_i(s,u), with denominators nonzero on a named open set.
2. In F_32009[u,s], reduce every J_i(t(s,u)); require exact zero.
3. Find the common lowest s-order e of the G_i and extract F_i(u).
4. Reduce every generator of C at F(u); require exact zero.
5. On the chart F_q != 0, compute the exact rank of
   d(F_i/F_q)/d(u_j) over F_32009(u).
6. Exhibit a nonzero maximal minor and an open parameter point satisfying
   all denominator and leading-coefficient conditions.
```

A Jacobian rank equal to \(\dim C\) proves image dimension at least \(\dim C\); containment gives the reverse inequality. In characteristic \(p\), a deficient Jacobian can reflect inseparability, so a low rank fails this certificate rather than proving the image too small. An alternative is an exact graph-ideal calculation proving the image dimension.

**Falsifiers:** a nonzero substituted \(J_i\); all leading \(F_i\) zero; a component polynomial nonzero on the family; a zero claimed maximal minor; or an image dimension smaller than the component dimension. A finite list of sampled points cannot establish density.

**Budget:** host, 3–8 GiB and 10–30 minutes per symbolic pilot; increase only after observing the actual polynomial sizes. VB has two known components of dimensions three and degrees three and four; X− has one arithmetic prime of dimension three and degree 12. Those small decompositions make them the best first targets. The dimensions and degrees belong to the **quadratic upper bound**, not yet the fiber ([decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:181)).

### 2. Lifted relations with a certified saturation-free presentation — scheme certificate

**Inferred:** The existing candidate criterion is sound if its checks finish. Construct a candidate \(L\) containing \(H\), verify by substitution that \(L\subseteq\ker(y_j\mapsto aG_j)\), and prove \(L:g=L\). Then \(L\) is the Rees ideal. Specialize \(t=0\) and compare the resulting ideal with the proposed fiber ideal. The implementation and exact checks are in [fiber_certificates.py](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:1).

The productive change is to seek a **structured presentation**, rather than immediately repeat `std(L)`: compute low-degree syzygies of \(G\), inspect their coefficient matrices, and test whether a Jacobian-dual or determinantal presentation has a theorem whose hypotheses can be checked for the actual quotient ring and ideal. Verify all hypotheses—including grade, dimension and torsion conditions—before invoking such a theorem. A Jacobian dual or linear-type claim does not follow from the measured \(h_d\).

**Falsifiers:** a proposed generator survives substitution, a required grade or depth hypothesis fails, `quotient(L,g)` contains an element outside \(L\), or the specialized ideal disagrees with a certified method-A degree.

**Budget:** VB first on the host, 3–8 GiB and 30–60 minutes for syzygy and hypothesis probes; only promote a presentation with a substantially smaller verified intermediate problem. **Observed:** the existing 18-variable `std(L)` timed out at 500 seconds and reached its 3 GiB cap after 14 minutes ([decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:243)).

### 3. Bounded degree calculations — scheme certificate only with an independent bound

**Inferred:** Let \(K\) be a candidate homogeneous fiber ideal. If an independent theorem or certificate proves that the actual kernel is generated in degrees at most \(D\), then method A through \(D\), together with equality \(K_d=\ker_d\) for every \(d\le D\), proves \(K=\ker\). A certified regularity bound for the **unknown kernel**, or another valid relation-type bound, can supply \(D\). Regularity of \(K_2\) alone cannot.

A practical experiment is to compute VB degree four using the driver, retaining the ordered monomials, exact normal forms, rank and relation witnesses. Compare its rank with 155, the recorded degree-four Hilbert value of the quadratic model. A smaller rank exhibits a new relation; equality supplies one further degree only.

**Falsifier:** \(h_4<155\) refutes the assertion that VB’s quadrics generate its relations through degree four. A result \(h_4=155\) does not prove an all-degree stop. A degree-truncated standard basis is similarly a proof only after a separately verified bound covers every potentially necessary relation and every reduction needed by the claimed certificate.

**Budget:** host, 4–8 GiB, initial 1-hour wall limit; the preceding cubic took 406 seconds. Escalate only with stage and memory measurements.

### 4. Initial algebra or SAGBI — conditional, potentially decisive

**Inferred:** Work with the subalgebra generated by \(G_i z\) in \((k[t]/J)[z]\), using an explicitly specified compatible valuation or term order. If a finite SAGBI basis is produced **and all subduction tests terminate at zero**, its initial algebra gives a presentation and Hilbert series of the Rees algebra. Deriving the special fiber additionally requires proving that the degeneration and specialization commute, for example through an appropriate flatness or filtered-module certificate.

**Falsifiers:** a nonzero unreduced subduction, an unverified infinite completion, or a specialization/Hilbert mismatch with method A. Matching leading monomials in a finite prefix is not a SAGBI certificate.

**Budget:** VB host, 3–8 GiB and 30 minutes for a feasibility probe. Defer larger pairs until a finite basis and specialization argument exist.

### 5. Linear sections, lines, alternate solvers and multiple primes — supporting tools

- **Inferred:** A generic projective linear section can help measure a candidate component’s dimension or degree. A certified section needs an exact genericity condition and must meet every relevant component; it does not by itself prove that an unknown fiber fills that component. A generic line in the **slice** may miss exceptional directions that require nonlinear or higher-order arcs.
- **Inferred:** M2 or msolve is useful if it implements a materially different presentation or an exact bounded linear-algebra problem. Changing the solver on the same full graph is a comparison experiment, with weak expected value given the retained failures.
- **Observed — [decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:174):** A second split prime requires regenerating \(J,G\) from the Gaussian-rational producer, rather than changing the prime in specialized input text. The input harness emitted \(p=32029\), root \(9115\), as well as the second root at \(32009\).
- **Inferred:** Matching primes is a valuable diagnostic, but neither two matching primes nor Hensel lifting alone proves the characteristic-zero answer. A characteristic-zero certificate needs exact lifted identities and a justified specialization/flatness argument, including excluded denominators and bad primes.

## 3. What the quadratic models already decide

**Observed — [decision record, quadratic structure table](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:181):**

| Pair at the recorded point | Certified data over \(\mathbf F_{32009}\) | What closes reduced-support equality |
|---|---|---|
| X−, and X+ by the checked sign change | \(h_1,h_2,h_3=15,51,122\); \(V(K_2)\) has one arithmetic prime, dimension 3, degree 12; \(K_2\) is nonradical | A genuine limit family whose closure has dimension 3 inside that prime, or another proof that the fiber has dimension 3. |
| E8-bar→VB | \(10,34,80\); \(K_2\) is radical with two primes, both dimension 3, degrees 3 and 4 | A dense genuine limit family in **each** component, or an equivalent containment certificate for each. Dimension 3 alone could select only one component. |
| E8-bar→N+ | \(21,83\); \(K_2\) has primes of dimensions 4 and 3, degrees 11 and 4; \(K_2\) is nonradical | Dense genuine limits in both components. A dimension-4 family alone leaves the separate dimension-3 component unresolved. |
| E8-bar→N− | \(21,83\) | Compute and certify its own \(K_2\) decomposition, then cover each component. Matching \(h_1,h_2\) does not identify its ideal with N+. |
| W8→N−, and N+ by the checked sign change | \(24,156\); quadratic model dimension 5, degree 50; decomposition unfinished | Certified minimal primes plus a dense limit family in every component. |
| Iso | \(17,85,265\); decomposition unfinished; quadratic-scheme degree 23 | Certified minimal primes plus a dense limit family in every component. |

**Inferred:** The measurements alone decide reduced support for **none** of these nullity-8 pairs. In X−, irreducibility of the quadratic upper bound makes a dimension-three lower bound especially valuable. Arithmetic primality over \(\mathbf F_{32009}\) is not a claim of geometric irreducibility over its algebraic closure; base-field and geometric support must be named separately.

## 4. Arc sampler and certificate interface

**Observed:** The current [dense-family implementation](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:168) tests supplied points against component equations and returns a lower-bound status. It does not verify that supplied points came from arcs or compute image dimension. The earlier [build review](~/Projects/IBMQuantum/docs/local/a5-failed-runs/build/codex-review.md:1) identified a metadata-only equality defect; the inspected function now documents and implements the lower-bound restriction.

**Inferred — proposed contract:**

1. Store the exact input hash, prime and root, ordered \(J,G\), component ideals, parameter ring, arc formulas, denominators and open conditions.
2. Verify \(J(t(s,u))=0\) exactly. A truncated numerical or formal solution alone needs a separate exact lifting/existence proof.
3. Verify a common leading order and nonzero leading vector, then retain \(F(u)\) and the projective chart.
4. Verify component containment and an exact dimension witness: a nonzero Jacobian minor of the required size, or a certified image ideal and dimension.
5. Verify that the component list is complete and consists of the certified minimal primes of the upper bound. Require one valid dense-family witness per component.
6. Only after those checks return `support-equal`; otherwise return `support-lower-bound`, `refuted`, or `unverified`, with the failed check identified.

Random parameter values can discover candidate families or supply sanity checks; they cannot prove density. A deterministic symbolic family avoids a new random seed. If randomized exploration is later used, the repository’s QRNG provenance and provider-approval rules apply.

**Falsifier for the checker:** an empty point list, fabricated dimension metadata, a family with \(J(t)\ne0\), a vanishing claimed minor, an omitted upper-bound component, or a changed input digest must never return `support-equal`.

## 5. Compute assignment and stop rules

**Observed:** The host has 62 GiB RAM and had a memory-pressure incident; the program adopted approximately 24 GiB of reachable concurrent caps. Azure has one approximately 82 GiB FX4mds_v2 VM per listed region. Kaggle CPU has about 30 GB; the TPU VM supplied a much larger CPU-memory surface but had a queue exceeding six hours. These are recorded observations, not current availability ([lab map](~/Projects/IBMQuantum/docs/local/a5-failed-runs/lab-map.md:1)).

| Rank | Work and resource | Initial limit and decision |
|---|---|---|
| 1 | Host: VB/X exact arc and component probes | 3–8 GiB, 10–30 min each; serialize against other admitted caps. Continue only when an exact family or a useful dimension witness emerges. |
| 2 | Host: VB structured syzygy/presentation probe and degree four | 4–8 GiB, 1 h each; retain separate results. Degree four is diagnostic unless an independent bound emerges. |
| 3 | GitHub Actions: small deterministic certificate checks | 4 vCPU/16 GB runner; use only inputs and tests that fit its permitted classical-work scope. Recheck current runner limits and authorization before dispatch. |
| 4 | Azure: a new, demonstrably smaller structured computation or component decomposition | One job per VM, up to 70 GiB and 4 h initially, subject to a written case and current approval. The N+ saturation already consumed 10 h and 72 GB without completion. |
| 5 | Kaggle CPU: independent second-prime degree receipts | Per-session RSS watchdog below the approximately 30 GB limit, 4 h initial solver ceiling; retain each result promptly. A notebook session requires its written case and approval. |
| 6 | Kaggle TPU VM: only a redesigned, independently useful batch | A bounded four-hour session after exact smoke validation, explicit case and approval; sampled RSS thresholds, process-group deadlines and streamed receipts. Include queue time and setup in the comparison. Its TPU device does not accelerate Singular merely because the VM has a TPU. |

For each launch, review the actual binary’s flags and the [compute-flags checklist](~/Projects/IBMQuantum/docs/runbooks/compute-flags.md:179). Use cgroup `MemoryMax` and `MemorySwapMax=0` where available, `timeout` and recorded thread counts; avoid inherited `RLIMIT_AS`. The decision record’s last correction identifies an inherited 4 GiB hard address-space limit as the cause under investigation, and explicitly withdraws its earlier 16 GiB explanation.

## 6. Stop doing

- **Observed; stop repeating unchanged:** pivot saturations with larger caps as the main strategy. X−, Iso, VB and E8-bar→N+ have substantial failed attempts; W8’s VM outage left its run **incomplete**, so it does not establish a saturation stall.
- **Observed; stop repeating unchanged:** local `ds` syzygy and full Rees graph elimination. W8’s local route reached 83 GB before \(h_2\); VB’s TPU graph produced a huge degree-16 matrix without a basis.
- **Inferred:** Do not infer that any solver can *never* converge affordably. The evidence rejects these unchanged runs as a good next investment; a smaller presentation, verified theorem or measured algorithmic improvement changes the experiment.
- **Observed:** Do not repeat `minAssGTZ` as the first decomposition step on the recorded X−/Iso quadratic models; the record attributes its failure to generic-coordinate densification. Radical-first decomposition succeeded quickly for X−.
- **Inferred:** Stop treating additional matching \(h_d\), a generic line, finite samples, two primes, or regularity of \(K_2\) as a completion certificate. Each remains useful when it answers a stated finite or diagnostic question.

The recorded finite-field fibers are steps toward the kernel-limit problem. Even a completed exceptional-fiber support certificate still needs the appropriate map from those directions to limiting kernel planes before it supplies the full attaching data described in [purpose.md](~/Projects/IBMQuantum/docs/local/a5-failed-runs/purpose.md:1).



===== FILE: PYTHON.md =====

# Python in this repository: multi-environment audit and governance

This document is the central governance and routing authority for Python libraries,
environments, dependency manifests and interpreters across the repository.
Versions live in the locked manifests and machine-audited inventories, never in
prose:
- [requirements.txt](../requirements.txt) (tested core runtime);
- [ci/requirements-ci.txt](../ci/requirements-ci.txt) (gate tools and testing);
- [ci/requirements-browser.txt](../ci/requirements-browser.txt) (browser validation of the measured explorer);
- [ci/requirements-replay.txt](../ci/requirements-replay.txt) (historical Qiskit 2.5.2 replays);
- [packaging/qiskit-aer-cuda/build-requirements.txt](../packaging/qiskit-aer-cuda/build-requirements.txt) (qiskit-aer CUDA wheel packaging);
- the build host's Arch packages in [python-stack.md](notes/build_host/python-stack.md), and the Qiskit-adjacent packages and `/opt` stacks beyond the core in [qiskit-packages/README.md](notes/qiskit-packages/README.md);
- the isolated provider environments: [Quantum Inspire](notes/quantum_inspire/README.md), [Open Quantum](notes/open_quantum/README.md), [Quandela](notes/quandela/README.md) ([quandela/python-stack.md](notes/quandela/python-stack.md)), [IQM](notes/iqm/README.md) ([iqm/python-stack-versions.json](notes/iqm/python-stack-versions.json)), and [Kaggle](notes/kaggle/README.md) ([kaggle_kernel/AGENTS.md](../kaggle_kernel/AGENTS.md)).

The central [library register](state/hypercomplex-libraries/libraries.md) lists every
distribution (362 distributions across all source surfaces) with its role, and its sibling
[libraries.json](state/hypercomplex-libraries/libraries.json) records each
tracked file that imports it (`imported_by`); gate
core-630 (`scripts/hypercomplex_libraries.py --out docs/state/hypercomplex-libraries --check`)
compares it with a fresh AST scan of `gororoba_quantum/`, `scripts/`, `ci/` and
`kaggle_kernel/`, so a new import in those trees enters the register in the same change.


## Multi-environment architecture

The repository segregates Python execution across six distinct runtime environments
to prevent dependency conflicts, preserve bit-for-bit historical replay, and respect
platform boundaries:

1. **Build Host (Arch Linux / CachyOS System Environment, `$PYTHON`)**
   - Python 3.14 (system interpreter).
   - Package management: Arch system packages (`pacman`, `paru`) and custom PKGBUILDs
     in `~/Github/PKGBUILDs`, all linking the system OpenBLAS (`blas-openblas`) as BLAS and LAPACK.
   - Hardware acceleration: NVIDIA RTX 4070 Ti (SM 89), CUDA 13.4.3, cuQuantum 26.09.0.8
     (libcustatevec.so.1 and libcutensornet.so.2), and cutensor 2.8.1.0.
   - Locally compiled packages: `python-qiskit` (2.6.1), `python-qiskit-aer-cuda` (0.18.2-3 with cuStateVec support and unique provider names),
     `python-samplomatic` (0.21.0), and `python-qiskit-ibm-runtime` (0.51.0); the library wiring
     is in [python-stack.md](notes/build_host/python-stack.md).
   - Computer algebra: System `sagemath` (10.10) for exact algebraic geometry and
     rotation-composite audits.
   - Local hypercomplex verification stack: 17 packages extracted and validated against
     `gororoba_quantum/cd_core.py` by `scripts/algebra_package_tables.py`.

2. **Hosted CI / Pull-Request Verification (`ci/`)**
   - Python 3.14.7 container environment.
   - Strictly locked dependencies from `requirements.txt` and `ci/requirements-ci.txt`.
   - Tool pinning: `ci/pinned_tool.py` runs pinned `ruff==0.17.1` and `mypy==2.4.0` via uv.
   - Browser checks: `ci/requirements-browser.txt` installs `playwright==1.64.0` for
     headless validation of rendered explorer artifacts.

3. **Historical / Replay Runtime (`REPLAY_PYTHON`)**
   - Interpreter satisfying `ci/requirements-replay.txt`: Qiskit 2.5.2, pydantic 2.13.5,
     ibm-quantum-schemas 0.12.20260921, and samplomatic 0.21.0.
   - Gates marked `"runtime": "qiskit-2.5"` execute under this runtime to verify
     bit-for-bit equivalence of retained historical evidence, circuit routing, and receipts.

4. **Isolated Provider Virtual Environments**
   - **Quantum Inspire (`QI_PYTHON`, Python 3.13)**: Located in `~/.local/share/quantum_inspire/`
     or `QI_ENV`. Isolates `quantuminspire`, `qxelarator`, `libqasm`, `opensquirrel`, and
     `qiskit-quantuminspire` from main Qiskit versions.
   - **Open Quantum (`OQ_PYTHON`, `OQ_ENV`)**: Located in `~/.local/share/open_quantum/`. Runs
     `openquantum-sdk`, `openquantum-sdk-qiskit`, and `openquantum-mcp`.
   - **Quandela (`QD_PYTHON`)**: Dedicated environment in `~/.local/share/quandela/` for the
     Quandela MCP server (`scripts/qd_mcp_server.py`). Perceval itself runs on `$PYTHON`.
   - **IQM Resonance (`iqm-python`)**: Independent Python 3.13 environment under
     `/opt/iqm-resonance-stack` running IQM OS 4.7 (`iqm-client`, `qiskit 2.1.2`, `cirq-core`,
     `qrisp`, `iqm-pulla`, `iqm-pulse`).
   - **Other Providers**: Pinned venvs under `~/.local/share/<provider>/venv` for IonQ,
     BlueQubit, Quafu, and Origin Quantum.

5. **Kaggle Kernel Multi-Substrate Execution (`kaggle_kernel/`, `scripts/kaggle_run.py`)**
   - **CPU Kernels**: Kaggle Python 3.13 container, image numpy/scipy/sympy/torch,
     pip `--no-deps` hypercomplex stack from pinned archives (`hypercomplex.json`),
     and optional `quantum-tools` group (`PIN_GROUPS`).
   - **GPU Kernels (Tesla T4)**: `qiskit-aer-gpu-cu11` 0.17.2, `cuquantum-cu11` 24.8.0,
     `cutensor-cu11` 2.2.0, or custom CUDA 13 Aer wheel (`qiskit-aer-gpu-cu13`).
   - **TPU Kernels (`TpuV5E8`, `TpuV6E8`)**: JAX differentiable array sweeps only;
     Aer has no TPU backend.

6. **Native Packaging and Wheel Building (`packaging/`)**
   - Locked build-system dependencies in `packaging/qiskit-aer-cuda/build-requirements.txt`
     (`build==1.6.0`, `scikit-build==0.19.1`, `pybind11==3.1.0`, `setuptools==84.0.0`, `wheel==0.48.0`).


## Locally installed vs. otherwise used libraries

The repository audit recognizes four operational statuses across all Python distributions:

1. **Locally Installed and Directly Imported on Build Host**
   - *Core runtime*: `numpy`, `scipy`, `sympy`, `python-flint`, `rustworkx`, `qiskit`,
     `qiskit-aer`, `qiskit-ibm-runtime`, `pydantic`, `qiskit-mitigation`, `samplomatic`,
     `ibm-quantum-schemas`.
   - *CI and verification*: `mypy`, `ruff`, `matplotlib`, `pytest`, `pytest-xdist`,
     `threadpoolctl`, `perceval-quandela`, `exqalibur`, `cvxpy`, `clarabel`, `mcp`,
     `playwright`.
   - *Local computer algebra*: `sagemath`.
   - *In-tree specifications*: `gororoba_quantum/cd_core.py` (canonical Cayley-Dickson multiplication),
     `gororoba_quantum/parallel.py` (order-preserving spawn process pool).

2. **Locally Installed for Hardware Acceleration, Probes and Negative Controls**
   - *Host CUDA/BLAS support*: `cuquantum` (libcustatevec, libcutensornet), `cutensor`,
     `cuda`, OpenBLAS (`blas-openblas`) as the BLAS and LAPACK provider.
   - *Algebra reference packages*: Installed as Arch packages and bound by SHA256 digests in
     `docs/evidence/algebra_packages/tables.json` to verify `cd_core`:
     `hypercomplex`, `hypercomplex-engine`, `hypercomplex-algebra`, `cayley-calculator`,
     `cayley-dickson`, `octonion`, `splitoct` (split-signature negative control), `mathdunders`,
     `numpy-quaternion`, `quaternionic`, `pyquaternion`, `clifford`, `kingdon`, `galgebra`,
     `pyoctonion`, `octonion-sedenion`, `hyprat`.
   - *Exact arithmetic backends*: `python-flint` (modular rank, rational null spaces) and
     `pyadic` (finite-field and p-adic valuations), which define no Cayley-Dickson table.

3. **Otherwise Used in Isolated Virtual Environments or Containers**
   - Distributions that would create conflicting requirements if installed into the main host
     environment:
     - Quantum Inspire: `quantuminspire`, `qxelarator`, `libqasm`, `opensquirrel`, `qiskit-quantuminspire`
       (requires isolated Python 3.13 venv).
     - IQM Resonance: `iqm-client 36.0.0`, `qiskit 2.1.2`, `cirq-core 1.7.0`, `qrisp 0.9.10`
       (pinned in `/opt/iqm-resonance-stack`).
     - Open Quantum: `openquantum-sdk`, `openquantum-sdk-qiskit`, `openquantum-mcp`.
     - Kaggle GPU simulation: `qiskit-aer-gpu-cu11`, `cuquantum-cu11`, `cutensor-cu11`
       (containerized T4 runtime).

4. **Documented Ecosystem Candidates and Evaluated Alternatives**
   - Distributions evaluated during architectural surveys and cataloged in
     [docs/notes/packages/candidates.md](notes/packages/candidates.md) and
     [docs/notes/qiskit-ecosystem.md](notes/qiskit-ecosystem.md).
   - Each carries a recorded status:
     - *Declined or not required*: `qiskit-addon-mpf` (declined multiproduct workflow; CVXPY presence does
       not establish admission), `qiskit-dynamics` (archived upstream), `benchpress` (unqualified oracle),
       `mapomatic` (unqualified against live Target), `pennylane`, `qutip`.
     - *Machine register tracking*: All 362 evaluated distributions are tracked with their
       retained roles, host presence, and citation records in
       [docs/state/hypercomplex-libraries/libraries.md](state/hypercomplex-libraries/libraries.md).


## Interpreters

| Interpreter | Runs | Authority |
| --- | --- | --- |
| `$PYTHON`, exported | default-stack scripts, gates and dry runs; a provider-dependent script or gate half runs under its provider interpreter below | [AGENTS.md](../AGENTS.md) "Layout and gates" |
| `--replay-python` or `REPLAY_PYTHON` | gates marked `"runtime": "qiskit-2.5"`; with neither, the running interpreter serves when it holds every replay pin, and an unresolved runtime exits 127 | [ci/AGENTS.md](../ci/AGENTS.md) |
| `QI_PYTHON` (Python 3.13) | Quantum Inspire SDK, qxelarator, cQASM, OpenSquirrel | [quantum_inspire/README.md](notes/quantum_inspire/README.md) |
| `OQ_PYTHON` | Open Quantum SDK | [open_quantum/README.md](notes/open_quantum/README.md) |
| `QD_PYTHON` | the Quandela MCP server; Perceval itself runs on `$PYTHON` | [quandela/README.md](notes/quandela/README.md) |
| `iqm-python` | IQM Resonance client stack | [iqm/README.md](notes/iqm/README.md) |
| `qi-stack-python`, `qi-stack` (Python 3.13) | the hash-locked Quantum Inspire stack: SDK, Qiskit provider and PennyLane plugin on qiskit 2.3.0 | [quantum-inspire-family.md](notes/qiskit-packages/quantum-inspire-family.md) |
| `qiskit-debugger-python` (Python 3.11) | qiskit-debugger on its pinned Qiskit 0.43.2 | [qiskit-debugger.md](notes/qiskit-packages/qiskit-debugger.md) |
| `quantum-pipeline-python`, `quantum-pipeline` (Python 3.13) | quantum-pipeline VQE runs on Aer 0.17.2 | [quantum-pipeline.md](notes/qiskit-packages/quantum-pipeline.md) |
| `QB_PYTHON` (Python 3.13) | qBraid SDK (`qbraid`, `qbraid-core`). The guide's venv is the portable default; the build host sets `QB_PYTHON` to `qbraid-python` from the `qbraid-stack` package | [qbraid/README.md](notes/qbraid/README.md) |
| Kaggle kernel | simulations of 14 qubits or fewer | [kaggle/README.md](notes/kaggle/README.md) |

Every interpreter starts with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, which the Qiskit Rust
and Aer OpenMP extensions need. Each gate's flags are the ones its command
in [ci/gates.json](../ci/gates.json) spells out; most pass `-B -W error` and
many also run under `-O`, so a check raises explicitly instead of using
`assert`.


## Dependency manifests and inventory verification

| Manifest / Register | Scope and purpose | Verification gate |
| --- | --- | --- |
| [requirements.txt](../requirements.txt) | Primary runtime dependencies (Qiskit 2.6.0, runtime 0.50.0, FLINT, SymPy, SciPy, NumPy) | `sh ci/pr_checks.sh tests` |
| [ci/requirements-ci.txt](../ci/requirements-ci.txt) | CI gate tools, testing plugins, Quandela adapters, CVXPY/Clarabel solvers, MCP | `sh ci/pr_checks.sh lint\|types\|tests` |
| [ci/requirements-browser.txt](../ci/requirements-browser.txt) | Headless Playwright browser automation for measured explorer verification | `scripts/validate_measured_explorer.py` |
| [ci/requirements-replay.txt](../ci/requirements-replay.txt) | Pinned Qiskit 2.5.2 compiler stack for bit-for-bit historical replay | `ci/run_gates.py --replay-python` |
| [packaging/qiskit-aer-cuda/build-requirements.txt](../packaging/qiskit-aer-cuda/build-requirements.txt) | Build tools (`build`, `scikit-build`, `pybind11`, `wheel`) for native Aer CUDA package | [notes/build_host/custatevec.md](notes/build_host/custatevec.md) |
| [state/hypercomplex-libraries/libraries.md](state/hypercomplex-libraries/libraries.md) | Exhaustive 362-distribution register of roles, host presence, and citations | `python3 scripts/hypercomplex_libraries.py --out docs/state/hypercomplex-libraries --check` |
| [state/hypercomplex-libraries/libraries.json](state/hypercomplex-libraries/libraries.json) | Machine-readable AST import scan, declared pins, and unresolved roots | `test_retained_inventory_*` in behavioral suite |


## Libraries by job

| Job | Library | Use it when | Rule and evidence |
| --- | --- | --- | --- |
| Cayley-Dickson products and signs | `cd_core` (in tree) | always: it is the specification | [algebra_circuit_rules.md](notes/algebra_circuit_rules.md) |
| Arrays, batched linear algebra | numpy | any float work; vectorize before pooling | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Least squares, decompositions, statistics, sparse | scipy | `lstsq` or pivoted QR, never normal equations; `scipy.sparse` for structured systems | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Exact rank modulo p, rational null spaces | python-flint through `scripts/exact_rank.py` | every rank or nullity certificate | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Symbolic algebra, exact matrices | sympy, as `DomainMatrix` for integer products; its ground types are FLINT on the pinned stack | polynomial identities and charts | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Arbitrary precision | mpmath; python-flint `arb_mat` and `acb_mat` for ball arithmetic | refining a float estimate past float64 rounding. FLINT's `eig` returns rigorous enclosures, and a cluster of near-equal eigenvalues widens its balls | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| p-adic and finite-field arithmetic | pyadic, galois | rational reconstruction, F_p linear algebra beyond FLINT, exact Hensel lifts whose valuation reads the order of an obstruction ([pyadic.md](notes/packages/manual/pyadic.md#hensel-lifting)) | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Gate-model circuits and transpilation | qiskit | IBM and other Qiskit-compatible circuits; the live Target is the timing authority. Provider-native circuits (Perceval, cQASM) follow their provider guides | [ibm_heron_platform.md](notes/ibm_heron_platform.md) |
| Noise simulation | qiskit-aer, CPU or the host's CUDA build | 14 qubits or fewer on Kaggle; 15 qubits only through an approved case naming the substrate; 16 or more go to IBM hardware through an approved case | [AGENTS.md](../AGENTS.md) "QPU time and calibration", [substrates.md](notes/kaggle/substrates.md) |
| IBM hardware | qiskit-ibm-runtime, client-side `executor_sampler` | `--submit` only after an approved case; `--collect`, `--preserve-raw`, calibration reads and transpilation need no approval | [qpu-submission.md](notes/ibm_quantum/qpu-submission.md) |
| Convex modeling and tomography SDPs | cvxpy, clarabel, scs, osqp | PSD-constrained state/process tomography and classical teleportation benchmarks; inspect residuals and solver status | [quandela/python-stack.md](notes/quandela/python-stack.md), [solver-role-grounding.json](state/hypercomplex-libraries/solver-role-grounding.json) |
| Layout and graph search | rustworkx | replica placement (`vf2_mapping`) | `gororoba_quantum/` |
| Batched density-matrix sweeps | jax | error-scale sweeps in `jax_bridge` on CPU | [jax-bridge-structure-report.md](notes/kaggle/jax-bridge-structure-report.md) |
| Tensor networks, contraction order | quimb, cotengra, opt_einsum | networks beyond a few tensors | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Photonic circuits | perceval, exqalibur | Quandela runs and their simulations | [quandela/README.md](notes/quandela/README.md) |
| qBraid sessions and device calls | qbraid, qbraid-core | a call through the qBraid SDK. The credit snapshot uses the default interpreter's HTTP client and does not import these packages. Pins stay in the qBraid requirements file; the library register marks both distributions separate | [qbraid/README.md](notes/qbraid/README.md), [requirements-qbraid.txt](notes/qbraid/requirements-qbraid.txt), [libraries.md](state/hypercomplex-libraries/libraries.md) |
| Cayley-Dickson cross-checks | hypercomplex (recursive products, `Fraction` witnesses); hyprat (exact rational coefficients, annihilators, regular representations); hypercomplex-engine (fast basis signs above dimension 16; hypercomplex-algebra wraps it and is not independent); cayley-dickson (recursive products), cayley-calculator, octonion-sedenion, pyoctonion, octonion (PyTorch batches) | an independent witness for a `cd_core` result, through a declared map checked on every basis pair; splitoct serves as the split-signature negative control | [packages/README.md](notes/packages/README.md), `scripts/algebra_package_tables.py` |
| Quaternions | numpy-quaternion (vectorized fields), quaternionic (Numba arrays), pyquaternion (scalar rotations) | quaternion subalgebra checks and rotation bookkeeping | [packages/README.md](notes/packages/README.md) |
| Clifford and geometric algebra | clifford, galgebra (symbolic), kingdon (generated operators) | associative envelopes and rotor controls; they never supply an octonion or sedenion product | [packages/README.md](notes/packages/README.md) |
| Audits that need SageMath | sage | build-host audits whose retained output a pinned gate checks | [rank_locus_rotation_composite](evidence/rank_locus_rotation_composite/README.md#symmetry) |
| Plots | matplotlib | measured figures, and exact or prospective model figures labeled as such; mock outcomes never enter either | [AGENTS.md](../AGENTS.md) "Layout and gates" |
| Tests | pytest, pytest-xdist | the behavioral suite | [ci/AGENTS.md](../ci/AGENTS.md) |
| Thread accounting | threadpoolctl | recording the BLAS and OpenMP runtimes a gate used | [numerics_best_practice.md](notes/topics/numerics_best_practice.md) |
| Provider MCP servers | mcp | `scripts/*_mcp_server.py` | provider guides |
| Kaggle control, browser checks | kaggle, kagglesdk, requests; playwright, selenium | kernel push and status; rendered-viewer and session checks | [kaggle/README.md](notes/kaggle/README.md), [ci/requirements-browser.txt](../ci/requirements-browser.txt) |
| Process pools | `gororoba_quantum/parallel.py` | every CPU-bound loop over independent items; dask and joblib stay unused | below |

A gate that needs a library outside the pin files retains its output with
`--out` and checks that output with the pinned stack, as core-489 does for
pyadic.


## Qiskit-adjacent packages and stacks

The build host carries these distributions beyond the pinned core of
requirements.txt, each built from a PKGBUILD in `~/Github/PKGBUILDs`. This
table registers them. Each linked note in
[notes/qiskit-packages/](notes/qiskit-packages/README.md) gives the package's
usage, commands, flags, hazards and connections, and that directory's README
maps how the packages connect. `"$PYTHON"
docs/notes/qiskit-packages/probe_packages.py --stacks` reruns the offline
probes after any upgrade.

| Surface | Interpreter | Core it carries | Packages |
|---|---|---|---|
| system, `$PYTHON` | Python 3.14 | qiskit 2.6.1, runtime 0.51.0, Aer 0.18.2 (CUDA build) | [qiskit-aer](notes/qiskit-packages/qiskit-aer.md), [ibm-quantum-schemas](notes/qiskit-packages/ibm-quantum-schemas.md), [qiskit-noise-learning](notes/qiskit-packages/qiskit-noise-learning.md), [pauli-prop and qiskit-addon-slc](notes/qiskit-packages/qiskit-addon-slc.md), [qiskit-serverless and qiskit-ibm-catalog](notes/qiskit-packages/qiskit-functions.md), [qiskit-connector](notes/qiskit-packages/qiskit-connector.md), [qiskit-resume](notes/qiskit-packages/qiskit-resume.md), [qiskit-waveform-sim](notes/qiskit-packages/qiskit-waveform-sim.md), [qcog](notes/qiskit-packages/qcog.md), [qubasic](notes/qiskit-packages/qubasic.md), [eigenkit](notes/qiskit-packages/eigenkit.md), [quantum-al](notes/qiskit-packages/quantum-al.md), [perceval-quandela and perceval-interop](notes/qiskit-packages/perceval-interop.md) |
| `quantuminspire-qiskit-stack` | `qi-stack-python`, Python 3.13 | qiskit 2.3.0, Aer 0.17.2 | [quantuminspire, qiskit-quantuminspire, pennylane-quantuminspire](notes/qiskit-packages/quantum-inspire-family.md) |
| `qiskit-debugger-stack` | `qiskit-debugger-python`, Python 3.11 | qiskit 0.43.2 (terra 0.24.1), Aer 0.12.1 | [qiskit-debugger](notes/qiskit-packages/qiskit-debugger.md) |
| `quantum-pipeline-stack` | `quantum-pipeline-python`, Python 3.13 | qiskit 2.6.1, runtime 0.51.0, Aer 0.17.2 | [quantum-pipeline](notes/qiskit-packages/quantum-pipeline.md) |

Each package's placement follows from one requirement:

- The Quantum Inspire family requires Python below 3.14, and pennylane-qiskit
  caps qiskit at 2.3.0.
- qiskit-debugger pins `qiskit==0.43.2` and imports `qiskit.Aer` and
  `qiskit.execute`, both of which Qiskit 1.0 removed.
- quantum-pipeline caps qiskit-aer below 0.18.
- qiskit-serverless caps qiskit-ibm-runtime below 0.51, and its system
  package relaxes that cap.

Four packages carry host hazards that their notes spell out:
- qiskit-connector loads `.env` files on import and overwrites the default
  IBM account.
- qiskit-resume unpickles checkpoint files.
- qubasic's `SHELL` statement runs shell commands.
- qiskit-waveform-sim takes only timing from the Target; its pulse shapes
  and amplitudes are placeholders.

The environments, caches and build trees that these surfaces leave on the
host, and the rules for cleaning them, are in
[runbooks/cache-locations.md](runbooks/cache-locations.md).


## Optimization ladder

Climb in this order and stop at the first rung that meets the budget.

1. **Measure.** `py-spy record` for Python stacks, `perf` for native code,
   `hyperfine` for whole commands. A long run writes its full log to a file.
2. **Vectorize.** Broadcasting, batched `@` and stacked `np.linalg` replace
   Python loops over elements; preallocate and keep dtypes concrete.
3. **Batch replicates.** A null calibration or bootstrap runs across
   replicates as arrays, with a gate proving the batched path returns the
   scalar reference's bits ([vectorized-fits.md](runbooks/vectorized-fits.md)).
4. **Pool independent items.** `parallel.ordered_map(function, items)` with a
   module-level `function` and picklable items. Items that share a seeded
   generator draw every input first, in the generator's order, and then map,
   so pooled and serial runs write the same bytes. The pool spawns, so an
   entry script calls it only under `if __name__ == "__main__":` and runs
   from a file rather than stdin. The pool sets each unset BLAS and OpenMP
   thread variable to one for its workers and keeps a value the caller
   exported, which can oversubscribe native threads.
5. **Move exact work to FLINT.** `scripts/exact_rank.py` gives
   `rank_mod` (FLINT `nmod_mat`, a rank modulo a word-size prime, which
   bounds the rational rank from below) and `rational_kernel` (FLINT
   `fmpq_mat` reduced row echelon form, a rational null space). A finite-field
   null space certifies nothing over the rationals; the certifying caller,
   such as `d_locus_nullity.nullity`, checks each rational kernel vector in
   Python integers.
6. **Use an accelerator only where a run qualified it.** The host's CUDA Aer
   build and Kaggle GPUs serve the circuits their notes measured; small
   dynamic circuits stay on CPU ([substrates.md](notes/kaggle/substrates.md)).
7. **Shard.** A pooled, batched run that still exceeds one host's budget
   shards to Kaggle CPU sessions by item range, once the user has approved
   the written case every simulator job and notebook session needs
   ([AGENTS.md](../AGENTS.md) "Hardware services"). The successor null also
   shards to the public repository's hosted runners
   ([null-shards.md](runbooks/null-shards.md)).


## Emulating another CPU with Intel SDE

numpy's dispatched loops, OpenBLAS's `DYNAMIC_ARCH` kernel choice and glibc's
libm ifuncs all pick their code path from CPUID, so one float64 computation can
round differently on an AVX-512 runner than on the build host, an AMD Ryzen 5
5600X3D (Zen 3, AVX2, no AVX-512). The Intel Software Development Emulator
runs an unmodified process under a chosen Intel CPU's CPUID and instruction
set, AVX-512 included, so the host reproduces an AVX-512 machine's natural code
path without capping the dispatch (`OPENBLAS_CORETYPE`,
`NPY_DISABLE_CPU_FEATURES`; [ci/AGENTS.md](../ci/AGENTS.md)).

The host carries `intel-sde` 10.13.1 (chaotic-aur), installed at
`/opt/intel-sde/sde64`. A run names the chip and passes the command after `--`:

```sh
/opt/intel-sde/sde64 -icx -- "$PYTHON" -B scripts/n21_dose_decisions.py RUN_DIR --out OUT.json
```

- `-icx` is an Ice Lake server and `-skx` a Skylake server; `-clx`, `-cpx`,
  `-spr` and `-gnr` name other AVX-512 server chips, `-hsw` an AVX2-only
  Haswell, and `/opt/intel-sde/sde64 -help` lists every chip. Emulate the
  model the runner reports: `ci/run_gates.py` prints a `numeric stack:` line
  with the CPU model, numpy's enabled dispatch targets and each loaded
  OpenBLAS core before the first gate. SDE emulates Intel chips only, so an
  AMD runner has no emulated counterpart.
- The process sees the emulated CPUID, so numpy reports `AVX512F` and
  `X86_V4` and dispatches its AVX-512 loops, and OpenBLAS selects its kernel
  for that chip. Exported caps still apply, so one emulated run can take the
  capped path and another the uncapped one.
- The emulator executes each instruction with the hardware's IEEE semantics,
  so the bits match a real chip of that generation wherever the result
  depends only on the instruction path. Cache sizes, core counts and timing
  are the host's, so a library that sizes its blocking from the cache or
  threads by core count can still diverge from real hardware. Pin
  `OPENBLAS_NUM_THREADS=1` and compare against a real run before treating an
  emulated replay as that chip's result.
- Cost: importing numpy and threadpoolctl took 12.8 s, and the n21 dose
  decisions run (about 5 s native) took 147 s, about 30 times native.

Measured on the n21 dose-decisions record
`results/live/2026-10-27T014354.701394Z/dose-decisions.json` (written in the
runner image, `scripts/n21_dose_decisions.py`, whose replica covariance is
`psi.T @ psi`, an OpenBLAS product):

| Emulated chip | `OPENBLAS_CORETYPE=Haswell` | numpy cap | Fields that differ from the record |
|---|---|---|---|
| `-icx` | set | set | 0 |
| `-icx` | set | unset | 0 |
| `-icx` | unset | set | 85 |
| `-icx` | unset | unset | 85 |
| `-skx` | unset | unset | 85 |

OpenBLAS's AVX-512 kernel alone moves the record under emulation, and
numpy's dispatch leaves it unchanged. On the hosted runners of audit run
40824932629, every shard reports numpy dispatching `X86_V3` and both
OpenBLAS copies on the `Haswell` core, so both pins apply. The Intel Xeon
Platinum 8573C shard (AVX-512) replays the record exactly. The AMD EPYC 9V74
and 9V45 shards (Zen 4 and Zen 5, AVX-512) differ in 95 fields. Their
`.arms.n21_orbit_window_dose_d7000_feedback_contrast.sigma` equals the
emulated value of the unpinned Intel AVX-512 kernel, and their d10500 arm's
sigma moves in no emulated run. So on those AMD CPUs a CPU-dependent path
outside the reported numpy dispatch and OpenBLAS core still changes the
rounding, and SDE cannot reproduce it. A record that depends on BLAS rounding
replays on the host under emulation only after a real-hardware comparison
has shown the two agree.

## Correctness rules

- Seed every generator and record the seed. Byte replay also needs the
  pinned generator algorithm and dependency versions and a gate that
  compares bytes: NumPy's seeded `Generator.binomial` changed between
  releases (`scripts/atlas_fringe_amplitudes.py`).
- float64 suffices wherever sampling sets the error. An exact claim uses
  exact arithmetic, and extended precision only refines a float estimate.
  A ball enclosure that excludes zero proves a minor nonzero and so bounds a
  rank from below; no precision proves a value zero, so rank deficiency and
  membership in a rank locus need exact arithmetic.
- Float tolerances decide nothing about rank, nullity or local dimension.
  A floating projection stops once a residual falls under its tolerance, so
  a direction along which the residual vanishes to high order passes
  uncorrected; such a test needs a scale where that order exceeds the
  tolerance, or extended precision.
- Run ruff and mypy through `ci/pinned_tool.py` on every touched Python file, and mypy over gate core-039's scope when a change alters a signature another module imports.
- Record the versions a result depends on inside the result.
- Mock outcomes (`--native-dry-run`) never enter an analysis or a figure.


===== FILE: compute-flags.md =====

# Compute flags: memory caps, threads and solver options

This runbook is the flag review that precedes every command whose cost or
correctness depends on its options: computer algebra (Singular, msolve,
Macaulay2), simulators (Aer, cuStateVec), Python pools, compilers, CI tools,
cloud launchers and resource limiters, on the build host, Azure VMs, Kaggle
kernels or any other substrate. The tool sections below cover the tools
measured so far; a tool without a section gets one the first time it runs long. An agent or operator fills in the
checklist at the end before the run starts and records the filled checklist
beside the run's log. A run launched without it gets stopped and relaunched.

[library-flags.md](library-flags.md) is the per-library companion: the environment
variables, API options and build facts of every package the repository imports.

## Why the review exists

Every msolve run on the A_5 Rees-fiber eliminations died with exit 139 under a
`prlimit --as` cap while its resident set sat far below that cap:

| Cap | msolve flags | Death | Peak resident set |
|---|---|---|---|
| `prlimit --as` 80 GiB | `-t 4 -e 1 -g 2` | degree 7, "Allocating memory for hash-column lookup table failed" | 33.6 GB |
| `prlimit --as` 28 GiB | `-t 3 -m 200000 -s 24 -l 1 -e 1 -g 2` | degree 6, "Enlarging exponent vector for hash table failed for esz = 268435456" | 28.0 GB |
| `prlimit --as` 28 GiB | `-t 3 -s 24 -u 2 -e 1 -g 2` | same point, same message | 18.1 GB |

`RLIMIT_AS`, which `prlimit --as` and Python's
`resource.setrlimit(RLIMIT_AS, ...)` set, limits reserved virtual address
space, not resident memory. The msolve 0.10.1 source names the two failing
allocations: `enlarge_hash_table` in `src/neogb/hash.c` reallocates the whole
exponent block at each doubling (`esz * evl * sizeof(exp_t)` bytes, with the
old block still mapped until `realloc` returns), and `src/neogb/convert.c`
reallocates the hash-to-column map (`(esld - 1) * sizeof(hi_t)` bytes) once per
matrix. glibc also reserves one malloc arena per OpenMP thread. The address
space therefore runs far ahead of the resident set, and the cap refuses an
allocation that physical memory could serve, so the failure looked like a
fixed internal limit. Several debugging rounds, including a consultation of
five frontier models, went into msolve internals before reading the cap
itself. The confirming run under a cgroup memory cap with the address-space
limit lifted is recorded in the A_5 attachment evidence once it ends; until
then the address-space explanation is the leading one, not a measured fact.

The general rule: a resource limit, a default thread count, or an unexamined
solver default can masquerade as a property of the mathematics. Read every
flag of the launch line before blaming the algorithm.

## Memory caps

Every mechanism below is available; the review picks one memory limit and one
time limit per run from what the substrate supports and records why.

| Mechanism | What it limits | When it fits | Caveat |
|---|---|---|---|
| cgroup v2 `MemoryMax` (`systemd-run --user --scope -p MemoryMax=NG -p MemorySwapMax=0 CMD`) | resident memory plus page cache charged to the job; the kernel OOM-kills the job alone at the limit | default on the build host and Azure VMs | needs the `memory` controller delegated to the user manager (`cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/cgroup.controllers`) and lingering (`loginctl enable-linger USER`) so the scope survives logout |
| cgroup v2 `MemoryHigh` (same command, `-p MemoryHigh=NG`) | soft limit: the kernel reclaims and throttles above it instead of killing | pairing with `MemoryMax` to slow a job before it dies | throttling can stretch wall time severalfold |
| container limit (`docker run --memory`, Kaggle's own 32 GB) | the container's cgroup | runs that already sit in a container | the whole container dies, every job in it included |
| RSS watchdog (sample `VmRSS` of the job and its children, kill above N) | resident memory, at sample granularity | Kaggle kernels and other containers without a delegated cgroup; the multi-job template already samples every 30 s | a fast spike between samples escapes it |
| `prlimit --as=BYTES CMD`, `ulimit -v`, `resource.setrlimit(RLIMIT_AS, ...)` | virtual address space reserved by the process | single-threaded programs whose virtual-to-resident ratio was measured small | refuses allocations far below physical memory for msolve, OpenMP programs, JIT runtimes and anything that reserves before touching |
| `prlimit --rss`, `RLIMIT_RSS` | nothing on Linux since 2.6 | never | accepted and ignored by the kernel |
| `prlimit --data`, `RLIMIT_DATA` | heap and private anonymous mappings | rarely; counts reservations like `--as` | same caveat as `--as` |
| `timeout -k 10 SECONDS CMD` | wall time | every run, beside one memory limit | |
| `systemd-run -p RuntimeMaxSec=` | wall time of the scope or service | runs already under `systemd-run` | |

Set `MALLOC_ARENA_MAX=2` in the environment of every multithreaded C program
so glibc keeps two arenas instead of one per thread; this shrinks address-space
growth and fragmentation at no measured cost to these workloads.

## msolve

Authority: `msolve -h` of the binary in use. The passagemath wheel 10.8.13
ships msolve 0.10.1 linked to libgomp, FLINT and GMP; the build host's
system package is 0.11.0, so a measured row names its binary and holds only
for that version.

| Flag | Meaning | Setting for Rees eliminations |
|---|---|---|
| `-f FILE`, `-o FILE` | input, output | required |
| `-e N` | two-block DRL elimination order, first N variables eliminated | number of eliminated variables (`-e 1` for the variable `a`) |
| `-g 0/1/2` | print nothing / leading ideal / full reduced basis for the first prime | `-g 2` when the basis is the result |
| `-t N` | OpenMP threads | physical cores free for the job (2 on a Standard_FX4mds_v2 alone, 1 beside another job); hyperthreads add contention |
| `-s N` | initial hash table size 2^N (default 17) | `-s 24` skips early doublings |
| `-u N` | rebuild the hash table every N steps, dropping stale monomials (default 0, never) | `-u 2` when the monomial table drives memory |
| `-m N` | maximum pairs per matrix (default unlimited) | leave unlimited: it splits matrices without shrinking the monomial table |
| `-l 1/2/42/44` | exact sparse-dense / exact sparse (default) / probabilistic variants | `-l 2`; the probabilistic modes stay out of cited results |
| `-r 0/1` | reduce the final basis (default 1) | default |
| `-q 0/1` | signature-based F4 | experiment only |
| `-v 0/1/2` | verbosity; 2 prints per-step degree and matrix sizes | `-v 2`, the only progress trace |
| `-c`, `-d` | genericity handling for zero-dimensional solving | irrelevant to elimination |

There is no `-l 0`, no column-split option, and `-s` takes an exponent, not a
count.

Environment: `OMP_PLACES=cores OMP_PROC_BIND=close MALLOC_ARENA_MAX=2`.

Build: the wheel's F4 library (`libneogb`) carries no AVX-512 code and almost no
AVX2; its AVX2 and AVX-512 routines serve FGLM only. A Standard_FX4mds_v2
(Xeon Platinum 8573C) offers AVX-512 F/VL/BW/IFMA/VNNI. A native build
(`-O3 -march=native` on the target host) vectorizes the row reductions; the
expected speedup per step is unmeasured, and memory does not change.

Accuracy: computations over a prime field with `-l 1` or `-l 2` are exact and
deterministic.

Version pin. The build host runs the distribution package and each Azure VM a
native build of the same upstream release, so both sit on upstream's latest
tag. Read the tag with
`gh api repos/algebraic-solving/msolve/releases/latest -q .tag_name` and the
host's version with `msolve -V`; when they differ, update the host package and
rebuild on each VM:

```sh
sudo apt-get install -y build-essential autoconf automake libtool pkg-config libgmp-dev libmpfr-dev libflint-dev git
git clone --depth 1 --branch "$TAG" https://github.com/algebraic-solving/msolve.git "msolve-src-$TAG"
cd "msolve-src-$TAG" && ./autogen.sh
CFLAGS="-O3 -march=native -mtune=native -fopenmp -funroll-loops" ./configure --prefix="$HOME/msolve-$TAG"
nice -n 19 make -j2 && make install
"$HOME/msolve-$TAG/bin/msolve" -V
objdump -d "$HOME/msolve-$TAG/lib/libneogb.so" | grep -c zmm   # nonzero: AVX-512 kernels present
```

A launch line names the binary by its versioned prefix, never the wheel's
`sage_wheels/bin/msolve`. The v0.11.0 native build on a Standard_FX4mds_v2
carries 199 AVX-512 instructions in `libneogb`; the passagemath wheel carries
none.

## Singular 4.4

Singular's `std`, `slimgb`, `syz`, `eliminate` and `minAssGTZ` run on one
thread. `Singular --help` lists `--cpus`, `--threads` and `--flint-threads`;
they bound the parallel libraries (`parallel.lib`, `tasks.lib`) and FLINT or NTL
calls, not a single standard-basis computation. Parallelism for these
eliminations comes from separate processes through `parallel.py` or separate
hosts.

| Setting | Meaning |
|---|---|
| `option(redSB)` | reduced standard bases; set before the first `std` |
| `option(prot)` | prints progress only; no memory effect |
| `option(notWarnSB)` | silences warnings on non-standard-basis inputs |
| ordering | global (`dp`, `lp`, block orders) per the repository canon; local orderings (`ds`) run far slower on the A_5 strata |
| `GOROROBA_WORKERS` | worker count for the repository's process pools |

Cap: cgroup `MemoryMax` or the RSS watchdog. Singular's allocator reserves
little beyond its resident set, so an address-space cap usually works, but the
cgroup cap is the uniform rule.

## Substrate table

| Substrate | Cores | Memory cap | Notes |
|---|---|---|---|
| Build host | 6 cores, 12 threads | `systemd-run --user --scope -p MemoryMax` | the owner keeps it mostly idle |
| Azure Standard_FX4mds_v2 | 2 cores, 4 threads | `systemd-run --user --scope -p MemoryMax`, lingering on | 84 GB; two jobs share 2 physical cores |
| Kaggle CPU kernel | 4 vCPU (treated as 2 cores) | RSS watchdog in the kernel script | 32 GB, kernel death above about 31 GB |

## Measured combinations

Each row is a hypothesis: the best flag set found so far for one tool version,
host and workload, with the measurement behind it and the result that would
dethrone it. A new run that beats a row on the same workload replaces it in
the same change, and the old row moves to `superseded` with its measurement
kept, so the table records every combination tried and why it lost.

| Tool and version | Host | Workload | Flags and environment | Measured | Falsifier | Status |
|---|---|---|---|---|---|---|
| msolve 0.10.1 (passagemath 10.8.13) | Azure FX4mds_v2, beside one Singular job | A_5 E8bar->N+ Rees elimination | `-t 4 -e 1 -g 2`, `prlimit --as` 80 GiB | exit 139 in degree 7, resident 33.6 GB | | superseded: address-space cap |
| same | same | same | `-t 3 -m 200000 -s 24 -l 1 -e 1 -g 2`, `prlimit --as` 28 GiB | exit 139 in degree 6, resident 28.0 GB | | superseded: `-m` leaves the monomial table unchanged |
| same | same | same | `-t 3 -s 24 -u 2 -e 1 -g 2`, `prlimit --as` 28 GiB | exit 139 in degree 6, resident 18.1 GB; `-u 2` lowered the resident set by 10 GB at the same point | | superseded: address-space cap |
| same | same | same | `-t 3 -s 24 -u 2 -e 1 -g 2`, cgroup `MemoryMax` 30 GiB, address space 1 TiB | passed every point where the address-space-capped runs died; memory-cgroup OOM kill entering degree 7 at 31.4 GB resident, 36.2 GB virtual | | superseded: the 30 GiB cap itself; confirms the address-space diagnosis |
| msolve 0.11.0, native `-O3 -march=native` | same | same | `-t 2 -s 24 -u 2 -e 1 -g 2`, cgroup `MemoryMax` 38 GiB, `choom -n 1000`, `MALLOC_ARENA_MAX=2 OMP_PLACES=cores OMP_PROC_BIND=close` | memory-cgroup OOM kill entering degree 7 (first matrix 407116 x 432548), sampled peak 33.3 GB; reached degree 7 in 901 s against 841 s for the wheel at `-t 3`, both beside a Singular job | a run reaching degree 7 faster on the same thread count alone on the VM | superseded: degree 7 needs more than 38 GiB; the native build shows no measured speedup yet |
| OpenBLAS 0.3.34 (`blas-openblas`), numpy 2.5.4 | build host, Ryzen 5 5600X3D | 3000 x 3000 float64: matmul, `scipy.linalg.lu_factor`, `numpy.linalg.eigh` | `OPENBLAS_NUM_THREADS=6` | matmul 0.234 s, LU 0.341 s, eigh 4.24 s | a thread count or library beating all three | current best |
| same | same | same | `OPENBLAS_NUM_THREADS=1` | matmul 0.883 s, LU 0.358 s, eigh 3.17 s | | eigh is faster single-threaded at this size |
| AOCL-BLAS 5.3.0 (BLIS), numpy 2.5.4 | same | same | `BLIS_NUM_THREADS=6` | matmul 0.215 s, LU 0.715 s, eigh 7.60 s; checksum equal to OpenBLAS to ten digits | | superseded: removed from the host; LAPACK slower when threaded |
| same | same | same | `BLIS_NUM_THREADS=1` | matmul 0.856 s, LU 0.330 s, eigh 3.03 s | | superseded |
| qiskit 2.5.2 `transpile` | build host, offline Heron r2 Targets (ibm_fez, ibm_kingston, ibm_marrakesh) | 7 families of `experiments.experiment_groups()` at 3-5 qubits, two dynamic; 8 ANU QRNG seeds per setting | `optimization_level=3`, default layout and routing (the `live_run.OPT_LEVEL` setting) | median routed cz equal to level 2 in every family (for example 98 against 291, 163, 98 at levels 0, 1, 2 on `design_c_32_1_16`); level 2 within 1-3 depth; `layout_method="dense"` worse by 1-53 cz; `routing_method="sabre"` identical to the default; seed spread up to 27 cz exceeds every level-2-versus-3 difference | a level, layout or routing setting with a lower median cz on these families, or a family above 5 qubits where level 3 and level 2 differ | current best; seed selection is the remaining lever |

A row records the tool version, the host, the workload, the full launch line
with environment, wall time, peak resident set, the furthest stage reached,
and the log path in the evidence directory that holds the run.

## Pre-run checklist

Record answers beside the run log:

1. Memory cap mechanism and value; for a multithreaded program, confirm it is
   not an address-space cap.
2. Wall-time cap.
3. Thread count against free physical cores on the host, other jobs included.
4. Every solver flag on the launch line, each checked against the binary's
   own `-h` or manual, with the reason for every non-default value.
5. Environment variables (`MALLOC_ARENA_MAX`, `OMP_*`, `GOROROBA_WORKERS`,
   `GLIBC_TUNABLES`).
6. Exactness: deterministic and exact, or probabilistic with the reason.
7. Progress trace (verbosity, RSS sampling) and where the log lands.
8. The falsifier: what the log shows if the run fails for the cap rather than
   the mathematics.
9. The measured-combinations row this run starts from, or a note that none
   exists; after the run, the row it adds, replaces or supersedes.
