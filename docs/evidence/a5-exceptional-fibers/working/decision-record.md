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
- 2026-10-29 TPU submission research (kaggle-tpu/submission-research.md, haiku, read-only): capacity wait ~60 %, stale one-slot TPU session ~20 %, verification ~15 %; use machine_shape TpuV5E8 alone (enable_tpu undocumented), no docker_image pin. Read-only check at ~23:40 UTC: the cancelled a5-e8vb-msolve-tpu still reports KernelWorkerStatus.CANCEL_ACKNOWLEDGED (not a terminal state), so it may still hold the account's single TPU batch slot that a5-fiber-tpu-smoke (QUEUED since 15:10 UTC) waits on. This raises the stale-slot hypothesis; confirming it needs the stuck session cleared.
- 2026-10-29 23:25 UTC: cancel re-sent for stuck session 363262467 (a5-e8vb-msolve-tpu; still CANCEL_ACKNOWLEDGED after it). Re-push of a5-fiber-tpu-smoke with machine_shape TpuV5E8 only was refused: 'Maximum batch TPU session count of 1 reached'. The queued smoke version has no session id in ListKernelVersions, so neither the MCP cancel nor kaggle_sessions.py cancel-running reaches it; only the web UI can stop it. The one-slot limit is confirmed held.
- 2026-10-29 evil-opencode red team (local qwen3.8-9b-distill via ollama; final-review-evil-opencode-redteam.md). Triage: refuted (claims contradicted by the bundle) - X- 72 GB cap, VB 155 = 54x12, 'segments claimed as certificates', 'method B best route', 'second-prime harness unimplemented'. Valid but already scoped - F_p vs characteristic zero (multimodular lift needed), QRNG dependence of a random sampler (deterministic symbolic family avoids it), components without a degree-d generator (why V(K2) is an upper bound and certification is per component). No new defect. A 9B local model over a ~40k-token bundle confabulates; use it for adversarial prompts, not as a referee.

## 10. Final plan (reconciled from five consultants and the local findings, 2026-10-30 UTC)

Inputs: greater-picture-gpt-daybreak-blue-latest.md, greater-picture-gpt-6.1-terra.md (Codex), final-review-grok.md
(grok-4.7 high), final-review-agy.md (Gemini 4 Argon high), final-review-evil-opencode-redteam.md (local 9B; no new
defect). opencode on Groq gpt-oss-120b was refused: the tier allows 8,000 tokens/min and the bundle is ~59,600.

Agreed by all five: method A segments certify only their degrees; pivot saturation, std(L), full-graph msolve,
local ds, minAssGTZ-first and RLIMIT_AS stay stopped; quantum backends, QRNG, GPUs, TPU devices and LLM text are
not evidence for exact algebra over F_p (TPU VM is a large CPU host only).

New and adopted (each with the check that confirms it):
- Linear forms in sqrt(K2) (agy). Observed: X- radical h1 = 12 vs 15, `prime 1 3 12 linear_gens 3`
  (runs/k2struct/xm.log); E8bar->N+ radical h1 = 16 vs 21. The reduced fiber sits in P^11 (X-) and P^15 (N+);
  3 and 5 degree-1 directions are nilpotent. Arc certificates see reduced support only; the nilpotent part needs
  the scheme route or direct kernel limits.
- Newton-Hensel formal arcs (agy, refining grok's "jets are not arcs"): blow up t = s*t~, pick a smooth point of
  the strict transform with an invertible Jacobian M on the dependent coordinates; Hensel then guarantees a unique
  formal arc in F_p(u)[[s]], so a finite jet determines the leading G-vector exactly. Falsifier: det M = 0 on
  every chart.
- Base-locus components (agy): order-1 arcs sweep only the strict transform of P(C_0(Y)); a component over the
  base locus of in(G) needs order-2 normal parameters. VB's second prime may be such a component.
- Geometric irreducibility screen (grok): factor the minimal polynomial of a primitive element of each prime's
  function field (absFactorize) before claiming a geometric component; arithmetic primes over F_p may split.
- Direct kernel-plane limits along arcs (agy): evaluate L_y on y(t(s,u)) from cd_core over F_p(u)[[s]]/(s^3),
  normalize kernel vectors by s-valuation, set s = 0; yields the limiting 8-planes, the item-6 attaching datum,
  including on the nilpotent part. Falsifier: generic nullity over F_p(u)((s)) differs from 8.
- Group arcs (grok): one-parameter subgroups of H through orbit points give algebraic arcs on Y without solving
  J = 0; a construction plan pending explicit Lie-algebra matrices.
- Deferred, not adopted now: Rabinowitsch affine-chart msolve (agy P8; repeats the eliminated graph family),
  AWS EC2 (needs aws login and a case), Rocq verification of finite identities (after a certificate exists).

Ordered steps (host unless stated; cgroup MemoryMax, MemorySwapMax=0, MALLOC_ARENA_MAX=2, one thread):
1. VB h4 vs 155 (running, 8 GiB, 1 h). h4 < 155: reduce the new relation mod each VB prime and the radical.
2. VB arc certificate: Hensel arcs at order 1 and order 2, both primes; containment, 3x3 minor (rank at a
   specialization point bounds the generic rank from below), absFactorize screen. 4-8 GiB, 30 min each.
3. Kernel-plane limits along the step-2 arcs from cd_core. 4 GiB, 30 min.
4. X-: same as 2-3 inside P^11; one prime, degree 12. 8 GiB, 2 h.
5. Radical and minAssChar in projective charts for E8bar->N-, Iso, W8. 8 GiB, 45 min per pair.
6. Arcs and kernel limits for E8bar->N+-, Iso, W8 over the step-5 primes.
7. Second-prime replay (p = 32029, r = 9115, producer-regenerated) of steps 2-6 receipts.
8. Scheme route only if the nilpotent structure is still required after 3: VB syzygy hypothesis probe.
- 2026-10-29 Correction: the Kaggle weekly reset 2026-10-31T00:00Z is Fri 2026-10-30 17:00 PDT, not Thursday as stated in replies; lab-map.md section 14 lists every reset in Pacific and UTC.
- 2026-10-29 23:38 UTC (16:38 PDT): TPU slot freed. The web UI showed a5-e8vb-msolve-tpu version 1 as canceled after 7,390.1 s (TPU v5e-8, latest container image, 19.07 output), so its API status CANCEL_ACKNOWLEDGED was stale, not a slot holder. The user deleted the queued a5-fiber-tpu-smoke kernel in the web UI (the API could not reach its queued version); the re-push with machine_shape TpuV5E8 only (no enable_tpu) was then accepted and queued. Procedure that cleared it: delete the stuck queued kernel in the web UI, then push. The watcher bfjno3z10 tracks the new version.
- 2026-10-30T00:55Z: VB degree-4 product stage hit its 1 h stage cap (exit 124) at 2.4 GB peak and 55 min of CPU, so it is CPU-bound, not memory-bound. Rerun with a 4 h stage cap under a 9 GiB scope (log build/logs/mine/vb4.log).
- 2026-10-30T00:55Z: Record regeneration regen6 hit the 3000 s outer cap with an empty log. The ten blocked rows at 300 s each, run serially, already fill that cap, so the cap was too short and the run tells us nothing about the RLIMIT_AS fix. Rerun as regen7 with a 7200 s cap.
- Scope cut: holomorphic_gauss_fibers.py, path_supported_basepoints.py, nakayama_rees_fibers.py, first_order_normal_cones.py and nullity16_basepoints.py still launch Singular under prlimit --as. Their records are bound and they are outside this branch's change; replacing prlimit there needs its own regeneration and ledger update.
- 2026-10-30T01:30Z X- full fiber s2 (pivot saturation): 12 h cap, exit 124, 11 h 14 min CPU, 9.4 GB peak, no output after "pivot 11 terms 64". This is the third X- stall after the pivot, so pivot saturation stays stopped for X-.
- 2026-10-30 Distribution round (distribute/brief.md; peer review distribute/review-daybreak.md, gpt-daybreak-blue-latest low). Adopted from the review:
  - A single global minAssChar run with an 11 h cap is the minAss-first approach on a longer timer, so it was replaced with chart-by-chart jobs (y_i = 1, radical, minAssChar, each prime written out, 2700 s per chart).
  - A second-prime h that differs from the first prime falsifies two-prime stability for that degree; on its own it does not identify which prime, the producer or the driver is at fault.
  - qBraid Lab takes nothing this round (about 1.8 vCPU, needs a case). GitHub Actions is overflow only, for jobs that fit 16 GB and 6 h.
- Shim test on the host: VB degree 2 at p=32029 through the systemd-run shim gives h=34 and 21 relations, degree-certified, agreeing with p=32009.
- Iso chart y1=1 on the host (180 s probe): dimension 5 and radical on that chart; minAssChar did not finish within 180 s.
- Kaggle kernels pushed and running at 2026-10-30T01:25Z (watcher distribute/watch.sh, outputs under distribute/out/):
  - a5-chart-iso (CPU): 17 charts, 4 at a time.
  - a5-chart-w8nm (CPU): 24 charts, 4 at a time.
  - a5-p2-small (CPU): VB, X- and X+ at p=32029, degrees 2-3.
  - a5-p2-iso (CPU): Iso at p=32029, degrees 2-3.
  - a5-p2-w8 (GPU session used as a 4-core host): W8 at p=32029, degrees 2-3.
  - a5-e8-d2 (GPU session used as a 4-core host): E8bar->N+ and N- at p=32029 degree 2, plus E8bar->N- at p=32009 degree 2, which supplies the K2 relations that N- has lacked for chart work.
  - The TPU smoke kernel is still queued.
- 2026-10-30 VB arc certificate (agent report build/arc/arc-report.md; scripts and logs beside it; not yet re-run by the orchestrator):
  - The order-1 Hensel ansatz fails: det M = 0, because the strict transform has Jacobian rank 3 over P(L) and the tangent cone is non-reduced (dim 4, degree 2, support L).
  - Arcs built on the normalization (two smooth branches, a node) with nu = 2. F(u) was interpolated from 48 points per branch and checked on 8 fresh points per branch.
  - P2 (dim 3, degree 4): support-certified over F_32009. All 9 generators vanish on F(u), and the generic rank is 3.
  - P1 (dim 3, degree 3): never reached. All 7 generators are nonzero on both branches and on every numeric arc in charts t1=1 and t3=1. Not yet tried: charts t5=1 and t7=1, the locus k^2+3=0, and the singular points of the normalization.
  - Both primes are geometrically irreducible by explicit rational parametrization; absPrimdecGTZ refuses characteristic p.
  - Open question: is P1 in the fiber at all? K2 only bounds the fiber from above. VB degree 4 (h4 vs 155) is the direct test.
- 2026-10-30 E8-bar -> VB degree 4 (build/logs/mine/vb4/receipt-d4.json): h4 = 155 with 0 new relations, degree-certified. Products std took 5,184 s; peak 2.4 GB; matrix 155 x 20,339. F(I) = k[y]/K2 holds through degree 4. Tension with the arc data: no arc reaches the degree-3 component, yet no relation cutting it out appears through degree 4. A fiber equal to the degree-4 component alone needs new relations in some degree of 5 or more.
