# Run rulebook: the specifics of each long run, on top of the foundations

The foundations are [computer-algebra.md](computer-algebra.md) (how to pose the question) and
[compute-flags.md](compute-flags.md) (how to review the launch line, which caps and threads, the substrate facts and
the measured-combinations table). This rulebook holds what the foundations cannot: the concrete decisions of one run
and why, written before the run starts and completed when it ends.

## When an entry is due

Every run expected to exceed 30 minutes, every cloud VM, and every run that departs from a foundation rule gets an
entry. Search this file and the measured-combinations table for the same tool, host and workload first; start from
the closest entry and say what changed.

## Entry template

```
### <descriptive title of the question, not an ordinal>
- Question and decisive outcome: what result settles which claim, and what each outcome proves.
- Formulation: the cheapest decisive computation chosen (computer-algebra.md) and the alternatives rejected.
- Host and tool versions: substrate row of compute-flags.md, binary and version.
- Launch line and environment: every flag, with the reason for each non-default value.
- Departures from the foundations: each rule not followed, and why.
- Parallelism: processes against physical cores (hyperthreads counted separately).
- Memory and time limits: mechanism, value, and what the log shows if a limit rather than the mathematics ends it.
- Checkpoints: the files written at each stage and their names.
- End state: copy, verification, and deallocate or delete; the backstop if no watcher is online.
- Outcome: wall time, peak resident set, furthest stage, result; the measured-combinations row added or replaced.
```

## Entries

### Iso -> N- blowup-chart saturation (does the fiber over the origin fill V(K2))

- Question and decisive outcome: dim A/(t) for one chart A of Bl_I V(J), a0 = l0(G) with QRNG l0; 4 means
  F(I) = k[y]/K2 in every degree, at most 3 means the analytic spread is at most 4. The log must first show chart
  dimension 5 and l0(z) = 1 in the chart.
- Formulation: one chart in place of the Rees algebra (K2 prime without linear forms, so one chart meets V(K2)
  densely); arc searches failed to reach rank 5 and decide nothing.
- Host and tool versions: lab-a1 (aarch64, 11 GB, apt Singular 4.4.1) first; then Azure Standard_FX4mds_v2 in
  westus3 (2 cores, 4 threads, 84 GB) with passagemath-singular 10.8.13 (Singular 4.4.1).
- Launch line: `timeout 28800 Singular -q --no-rc chart-iso-pP-METHOD.sing < /dev/null` under `/usr/bin/time -v`;
  inside, `option(noredTail)` and `option(prot)`; l0(z) - 1 added before saturating.
- Departures from the foundations: no cgroup `MemoryMax`; a shared RSS watchdog stops only the largest process when
  MemAvailable falls below 4 GB, so a runaway saturation does not end the other three. `option(noredTail)` replaces
  the `redSB` default of the measured table without a same-workload measurement; this run supplies one.
  Auto-shutdown is kept, set to start + 9 h (past the 8 h job limit), as the deallocation backstop, not disabled.
- Parallelism: four single-threaded processes ({32009, 32029} x {sat, Rabinowitsch elimination}) on 2 physical
  cores and 4 threads, so each shares a core; the portfolio trades per-process speed for two independent
  algorithms per prime.
- Memory and time limits: lab-a1 runs under `prlimit --as` 5 GB and 10 GB stopped with "Singular error: no more
  memory" (p = 32029 at 5.2 GB after 57 min, p = 32009 at 10.5 GB after 3 h 26 min); Azure: none per process,
  8 h each; at 1 h 47 min the p = 32009 processes held 25.5 GB each (about 14 GB/h) and the p = 32029 processes
  7.8 GB each.
- Checkpoints: `chart-sat-iso-pP-METHOD.txt` (saturation), `chart-std-...` (its standard basis), `chart-fiber-...`
  (the fiber ideal), each written as it exists.
- End state: the local watcher waits for `all done`, requires no Singular running, copies a tarball of out/ and the
  checkpoints, compares sha256, unpacks it, then `az vm deallocate` (the disk and its results stay; compute billing
  stops). A guest OS shutdown would leave the VM allocated and billed.
- Outcome: no saturation finished. Elimination: stopped by the watchdog at 29.7 GB after 3 h 21 min (32029) and
  52.1 GB after 7 h 29 min (32009). sat: 8 h limit at 15.1 and 15.8 GB. The `prot` traces show pair lists of
  20,000-37,000 pairs still growing (the number after `s` is the pair count, not the basis size). The dense a0 = l0(G) makes every a0 z_i a polynomial with hundreds of terms;
  the next formulation takes a0 = a single generator G_j (a coordinate chart, equally decisive because K2 contains no
  linear form). Results copied with sha256 verification; VM deallocated, disk kept.

### Point sections of a quadric scheme (radical, components, geometric irreducibility)

- Question and decisive outcome: whether K2 is radical and how V(K2) splits; a squarefree eliminant of degree vdim =
  deg K2 per section, common subset sums of orbit sizes, and a size-1 orbit per component.
- Formulation: QRNG linear sections in place of `radical` and `minAssChar` (which ran past 41,000 s).
- Host: laptop, passagemath Singular 4.4.1, about 2 s per section, no limits needed.
- Departures: none.
- Outcome: Iso K2 geometrically prime of degree 23; W8 K2 = I(C20) cap I(C30), both primes
  (`docs/evidence/a5-exceptional-fibers/structure/iso-k2/sections/`, `structure/w8-kp/`).

### Numeric arc search with symbolic certification

- Question: which arc families reach each component of V(K2) at full rank.
- Formulation: numeric dual-number engine over F_p (`arcs_num.py`) for the search, symbolic Singular only for the
  certified family; the symbolic search reached 17 GB at the second order and was stopped.
- Host: the session host for the numeric search (CPU only, under 1 GB), Singular for certificates in seconds.
- Departures: none.
- Outcome: V(P) certified at both primes; the Iso V(K2) and the W8 C30 not reached
  (`docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/README.md`).

### Iso -> N- coordinate-chart saturation (the sparse chart after the dense chart stalled)

- Question and decisive outcome: as the dense chart above, with a0 = G_j and z_j = 1; fiber dimension 4 means
  F(I) = k[y]/K2, at most 3 means the analytic spread is at most 4. The log must show chart dimension 5.
- Formulation: a coordinate chart decides equally (K2 contains no linear form, so y_j lies outside K2 and a
  4-dimensional E0 meets D+(y_j) densely). G_16 and G_17 have 41 terms and G_2, G_4 49, against 665 for the dense
  a0, so every a0 z_i is about 16 times sparser.
- Host and tool versions: lab-a1 (aarch64, 2 cores, 11 GB), apt Singular 4.4.1; p = 32009 only until a result.
- Launch line: `prlimit --as=5368709120 timeout 21600 nice -n 5 Singular -q --no-rc chart-iso-p32009-coordJ.sing
  < /dev/null` under `/usr/bin/time -v`, j = 16 and j = 2, launched with `setsid nohup`.
- Departures from the foundations: `sat` only, no Rabinowitsch twin (it grew 3.4 times faster in memory on the dense
  chart); an address-space cap of 5 GB per process on the 11 GB host, because Singular's allocator reserves little
  beyond its resident set and two processes share the host.
- Parallelism: two single-threaded processes on two cores.
- Checkpoints: `chart-sat-iso-p32009-coordJ.txt`, `chart-std-...`, `chart-fiber-...`.
- End state: logs copied into `structure/arcs-iso-w8/chart-runs/lab-a1/`; no VM to end.
- Outcome: both runs died with "no more memory" at the 5 GB cap after 34 min (j = 16 and j = 2), inside the
  saturation: faster memory growth than the dense chart on the same host (5.2 GB after 57 min). The sparser a0 does
  not shrink the saturation; the chart's size comes from the blowup itself, not from the density of a0.

### Iso -> N- sliced blowup chart (a finite fiber over the origin)

- Question and decisive outcome: the dense chart of the entries above, with l0(z) - 1 and four QRNG forms l1..l4(z)
  added before saturating. Bl is irreducible of dimension 5 and its exceptional divisor V(a0) is Cartier, so general
  z-forms meet no component of it entirely and (C + Lambda) : a0^inf is Bl cut by Lambda; the fiber over the origin is
  E0 cut by Lambda. All 23 points of V(K2) cut by Lambda means E0 = V(K2); no point means dim E0 <= 3. Points found lie in
  E0 deterministically; the full verdict rests on the genericity of one QRNG slice, so it is recorded as survives (one
  slice) until a second slice and an arc family upgrade it.
- Formulation: the cheapest decisive chart; the K2 cut by the same forms is checked generic first (vdim 23, squarefree
  eliminant of z(2) of degree 23, factors 1, 2, 3, 5, 12).
- Host and tool versions: lab-a1 (aarch64, 2 cores, 11 GB), apt Singular 4.4.1, p = 32009.
- Launch line: `prlimit --as=9663676416 timeout 21600 nice -n 5 Singular -q --no-rc chart-iso-p32009-slice.sing
  < /dev/null` under `/usr/bin/time -v`, one process, `setsid nohup`.
- Departures from the foundations: an address-space cap of 9 GB on the 11 GB host (one process).
- Checkpoints: `chart-sat-iso-p32009-slice.txt`, `chart-fiber-iso-p32009-slice.txt`.
- End state: logs copied into `structure/arcs-iso-w8/chart-runs/lab-a1/`.
- Outcome: "no more memory" at 9.4 GB after 3 h 14 min, inside the saturation; slicing by four z-forms barely
  changed the memory curve, because the saturation's work is removing the junk V(J + G) x (z-space cut by Lambda), of
  dimension 15 over L0, not the curve. The next formulation saturates by one function per component of V(J + G)
  (`chart-iso-p32009-slice-junk.sing`).

- Junk saturation outcome (2026-11-06): the slice-junk run also stopped with "no more memory" at 9.4 GB after
  3 h 16 min inside the saturation, so replacing a0 by one saturating function per component of V(J + G) does not
  bring the sliced chart under the 11 GB lab host; the next attempt needs a host above that ceiling and a written
  case.
- FX4 outcome (2026-11-07): on an FX4mds_v2 under a 55 GB scope the first std(C) ran 23.5 h (22 h limit, then an
  orphaned extension) to degree 15 with a pair list of 37,018 and 25.7 GB resident, still growing, and ended when the VM's
  `az vm auto-shutdown` schedule deallocated it at 21:00Z. That schedule recurs daily and had ended the first attempt
  a day earlier; a run past its first day reads `az resource list -g RG --resource-type
  Microsoft.DevTestLab/schedules` first and moves the schedule past the run's own deadline. Logs:
  `structure/arcs-iso-w8/chart-runs/fx4-w8p2/`. Six chart formulations have now failed; the 23 chart variables and the
  15-dimensional junk over L0 are the cost, so the successor works in the six t-variables (ledger A5-205).

### Iso -> N- t-space slice ladder (does a generic codimension-k slice of the graph of G reach the origin)

- Question and decisive outcome: whether the origin lies on the closure of V(J) minus V(I) cut by k generic linear
  forms l_i(G), read as Q_k : t2^inf with every generator vanishing at 0. Controls first: X+ -> N- and X- -> N+
  (l(I) = 3) must read on at k = 2 and off at k = 3; Iso at k = 5 must read off and at k = 3 on. A control reading the
  other way stops the work. The preregistered Iso k = 4 rows at p = 32009 and 32029 then decide dim E0 >= 4: on keeps
  A5-007 in every degree at that prime, off refutes it for generic forms.
- Formulation: six variables and one saturation in place of the 23-variable chart (A5-205, six failed chart runs);
  the criterion and its reduction are in `docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/README.md`.
  Alternatives kept as twins: `sat_with_exp` against the homogenized standard basis with t2 last; the dense a0
  saturation as the chart-style cross-check.
- Host and tool versions: the build host capsule (10 CPUs visible, 47 GiB), passagemath-singular 10.8.13 (Singular
  4.4.1, 12 October 2026 build), `/usr/bin/time` GNU, `prlimit` util-linux.
- Launch line and environment: `sh run.sh CASE CAP_GIB LIMIT_S`: `prlimit --as=CAP timeout -k 10 LIMIT /usr/bin/time -v
  Singular -q --no-rc sing/CASE.sing < /dev/null`, `MALLOC_ARENA_MAX=2`,
  `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`. `option(prot)` on the Iso scripts for the pair trace; global
  `dp`; no `redSB` or `noredTail` (defaults, no measurement for either on this workload). Caps: 12 GiB (X), 20 GiB
  (Iso k = 5 and the preregistered rows), 8 GiB (a0 cross-checks). Limits: 300 to 900 s (X), 3,600 s (Iso k = 5),
  7,200 s (Iso k = 3 and k = 4).
- Departures from the foundations: no cgroup `MemoryMax`, because `systemd-run --user --scope` fails with "Failed to
  connect to user scope bus" after the capsule start, so `prlimit --as` is the cap (Singular reserves little beyond its
  resident set; the measured peaks sit at 0.45 GiB or below against 8 to 20 GiB). Up to five Singular processes
  ran at once instead of one, each under 0.5 GiB resident, so their sum stays far below the host's oomd threshold.
  The homogenized saturation by t2 replaces `sat_with_exp` as the primary route, with a measurement (the
  measured-combinations table).
- Parallelism: single-thread processes, at most five at once on 10 CPUs.
- Memory and time limits: a "no more memory" line, or `exit 124` in `logs/CASE.result`, means the cap or the limit
  ended the run and no reading exists; `.time` holds the peak resident set and `.rss` the curve.
- Checkpoints: `logs/CASE.result` receives each RESULT line when it exists; no standard basis is written.
- End state: logs retained beside the scripts; nothing to deallocate.
- Outcome: all controls read as predicted (17 readings: X 12, Iso k = 5 off three ways, Iso k = 3 on two ways); the longest was
  `sat_with_exp` at Iso k = 5, 3,022 s at 382 MiB; the homogenized saturation took 272 s. Iso k = 3 cost less than
  k = 5 (16 s). The a0 cross-check at Iso k = 3 was stopped at 786 s and the junk split of that run's slice proper hit
  its 1,800 s limit; neither is a required control. Rows added to the measured-combinations table; the Iso k = 4 rows are preregistered and unrun.

### W8 -> N- degree 6, N = 19: export probe on the laptop (sizes the cloud case)

- Question and decisive outcome: the preflight memory and the Singular standard-basis cost of the W8 degree-6 rank at
  N = 19 (the 3d + 1 law), so the cloud case quotes a measured figure; the probe answers no algebra.
- Formulation: engine v11 quotient mode with the degree-2 receipt; `--max-gb 1` stops it at the preflight gate after
  the standard basis, keeping the degree-independent export for the full run.
- Host and tool versions: the laptop (WSL, 32 threads, 54 GiB), passagemath Singular 4.4.1, the engine's venv.
- Launch line and environment: `run-w8-d6-export.sh` (retained in
  `docs/evidence/a5-exceptional-fibers/w8-d6-n19-probe/`) under `systemd-run --user --unit a5-v11-w8-d6-export -p
  MemoryMax=48G -p MemorySwapMax=0`, `GOROROBA_WORKERS=8`, `MALLOC_ARENA_MAX=2`, timeout 43,200 s.
- Departures from the foundations: none.
- Parallelism: one job on the laptop; export chunks run through the engine's worker pool.
- Memory and time limits: the cgroup cap of 48 GiB; the preflight gate ends the run by design (exit 1).
- Checkpoints: the export directory keeps `s.txt` and `qB.txt` with their hashes.
- End state: export kept on the laptop for the full run; records retained; the runner logs the engine status but
  exits 0 on failure (#793 tracks the fix for new runners).
- Outcome: standard basis and preflight in 2,773.7 s at 486,608 KiB peak; preflight 375.62 GiB (D = 235,543); peak
  forecast about 160 GiB, at most about 195 GiB, from the degree-5 term-by-term reading. Case:
  `docs/evidence/a5-exceptional-fibers/working/azure-cases/w8-d6-n19.md`.

### W8 -> N- degree-30 component C30: fiber-cone planes over the base locus of the point blowup (bounded check)

- Question and decisive outcome: whether C30 = V(K2 : P) lies in the fiber E0 over the origin. A family of limit planes
  of cone dimension 6 inside V(K2 : P) and outside V(P) decides it positively (F(I) = k[y]/K2, the degree-6 rank run
  unnecessary); planes inside V(P), planes outside V(K2), or Jacobian rank below 6 would read the other way.
- Formulation: the local fiber cone of the pullback ideal at a QRNG point of P(L0) in the point blowup, cut by a
  transversal slice, read from a two-variable ideal (docs/evidence/a5-exceptional-fibers/structure/c30-bounded/README.md); rejected: the global t-space slice of codimension 5
  (Bezout bound 131,072 for its degree, no standard basis in 900 s) and the Iso-style one-chart saturation (more than
  23.5 h and 25.7 GiB on W8).
- Host and tool versions: build host capsule (10 CPUs visible, 47 GiB), Singular 4.4.1 (passagemath-singular 10.8.13),
  one thread.
- Launch line and environment: `sh docs/evidence/a5-exceptional-fibers/structure/c30-bounded/run.sh CASE [LIMIT_S]`, which wraps
  `systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 timeout -k 10 LIMIT /usr/bin/time -v Singular -q --no-rc`,
  `MALLOC_ARENA_MAX=2`, `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, stdin from `/dev/null`; local ordering `ds`
  only for the two-variable ideal of step 4, `dp` elsewhere; `option(prot)` on the global slice.
- Departures from the foundations: none; the user scope that earlier entries record as failing after the capsule start
  worked on 2026-11-08, so the cgroup cap is the memory limit here.
- Parallelism: one single-thread process at a time, except the global slice beside the quick cases (under 0.6 GiB each).
- Memory and time limits: 8 GiB cgroup cap; 300 s per plane or control, 900 s for the global slice; `exit 124` in
  `logs/CASE.result` means the limit ended the run, an out-of-memory kill would leave a nonzero exit.
- Checkpoints: `logs/CASE.result` receives each RESULT line when it exists.
- End state: logs retained beside the scripts; nothing to deallocate.
- Outcome: five planes (three at 32009, two at 32029) of 45 to 52 s and 26 MiB each, every one inside V(K2), outside V(P) and
  V(Lambda), inside V(K2 : P) at 32009, Jacobian rank 6; the controls read as predicted; the global slice stalled
  (`A5-237`). Rows added to the measured-combinations table of compute-flags.md.

### Iso -> N- degree 6, N = 19: truncated rank against the K2 count on the laptop

- Question and decisive outcome: whether h_6 of the Iso fiber reaches HF(k[y]/K2, 6) = 2,422 at p = 32009. r_19 = 2,422
  certifies h_6 = 2,422 (A5-119) and extends the N = 3d + 1 law to degree 6; r_19 below 2,422 would leave h_6 open or
  falsify the law at degree 6.
- Formulation: engine v11 quotient mode at N = 3d + 1 = 19 in raw mode, every product, because the Iso degree-2
  receipt has never run; rejected: N = 18 first (the law puts the count at 19, and 18 alone decides nothing).
- Host and tool versions: the laptop WSL host (substrate row in compute-flags.md), passagemath Singular 4.4.1, the
  laptop's pinned Python environment.
- Launch line and environment: `docs/evidence/a5-exceptional-fibers/iso-d6-n19-laptop/run-iso-d6.sh` under a
  `systemd-run --user` unit: `--quotient --export-chunks 5 --dense-tables-gb 0 --max-gb 47`, `MALLOC_ARENA_MAX=2`,
  `GOROROBA_WORKERS=8`, `timeout 43200`.
- Departures from the foundations: none.
- Parallelism: 8 workers on the laptop's physical cores; the laptop carried no other heavy job.
- Memory and time limits: the engine's `--max-gb 47` preflight (49.5 GB raw estimate) and the 12 h timeout; neither
  ended the run.
- Checkpoints: `out/iso6.events` start and exit lines; the json, time and err files at exit.
- End state: the four files and the runner copied into the evidence directory and hash-checked against the laptop; the
  export stays on the laptop.
- Outcome: wall 1,900.6 s, peak RSS 19.6 GiB, r_19 = 2,422 (blocks 632/610/590/590); h_6 certified at p = 32009.
- Follow-on unit `a5-v11-iso-d6-next` (`run-iso-d6-next.sh`, same flags): N = 18 at 32009, to test the predicted last
  jump 169 split 49/42/39/39 (r_18 = 2,253 or the law fails at degree 6), then N = 19 at 32029 to certify A5-125.
  Outcome: r_18 = 2,253 (583/568/551/551) in 1,173.2 s at 15.4 GiB, as predicted; r_19 = 2,422 at 32029
  (632/610/590/590) in 1,905.6 s at 19.6 GiB, h_6 certified there.

### E8-bar -> N+-: the defining ideal of the fiber cone by elimination from S[I T] / (m_R S) S[I T]

- Question and decisive outcome: the kernel L of k[y_1..y_21] -> S[I T] / (m_R S) S[I T] for the E8-bar slice, where
  I = I S is proved (A5-309). L = K2 closes A5-009 and gives h_6 = 1,666; a generator of L above degree 2 gives the
  true h_6 between 1,526 and 1,666. A run that does not finish proves nothing.
- Formulation: one elimination of T from (y_j - T G_j) over the polynomial model of S (variables w, rho, sigma, zeta,
  a, b, u with u (1 + w) = 1 and b^2 = F), then elimination of the seven S variables from the result plus m_R S, in a
  block dp ordering; local at the origin because S / m_R S has colength 2. Rejected: the truncated ladder at degree 6
  (the order-18 degree-3 cell alone held 30 GB) and a degree-bounded standard basis (no bigraded bound is set up).
- Host and tool versions: the laptop WSL host, passagemath Singular 4.4.1 (`~/a5env/bin/Singular`).
- Launch line and environment: `Singular -q --no-warn < records/e8-fiber-cone-e8-nm-p32009.sing` under
  `systemd-run --user --scope -p MemoryMax=24G -p MemorySwapMax=0` and `timeout 43000`, in tmux; the same script at
  p = 32029 and on the N+ header under `MemoryMax=10G` and `timeout 86000`.
- Departures from the foundations: none (global orderings; the localization is carried by the quotient).
- Parallelism: Singular is single-threaded; three independent cases run side by side.
- Memory and time limits: the cgroup caps above; a cap or the timeout ends the run with no result.
- Checkpoints: the log prints one RESULT line when J is checked and one when the Rees ideal is found; nothing between.
- End state: the logs and the generators of L (`e8-fiber-cone-L*.txt`) copied into `monomial-ladder/records/`.
- Outcome: not finished when this entry was written.

### Same-sign X ladder replays with the source-hashing float64 engine

- Question and decisive outcome: whether the committed `fast_ladder.py` reproduces the ranks an earlier version
  gave, so that each retained float64 record names its producer. Equal ranks close the provenance finding of the
  local review; a different rank would be an engine defect.
- Formulation: `fast_ladder.py --slug xm-nm --degree 8 --order 32` and `--order 34` at p = 32009,
  `--degree 7 --order 29` and `--order 31` at p = 32029, `--slug e8-nm --degree 3 --order 14`.
- Host and tool versions: the laptop WSL host, torch 2.15.0+cpu, numpy 2.5.4, scipy 1.18.1, python-flint 0.9.0.
- Launch line and environment: each under `systemd-run --user --scope -p MemoryMax=20G -p MemorySwapMax=0`,
  `--threads 16`, one after another in tmux.
- Departures from the foundations: none.
- Parallelism: torch threads inside one process; the products and maps go through the process pool.
- Memory and time limits: 20 GB per run.
- Checkpoints: one JSON line per degree in the log.
- End state: the records copied into `monomial-ladder/records/`.
- Outcome: order 32 in 1,835 s (ranks 665, 996, 1,133 at degrees 6 to 8); the E8-bar cell in 1,095 s (225); the two
  p = 32029 cells in 890 s and 1,904 s (996); the order-34 cell was killed at the 20 GB cap (exit 137) and again
  under a 40 GB cap with 24 threads after reproducing degrees 3 to 7 (1,590 s for degree 7 at order 31). The
  second kill came from the host's global out-of-memory killer at 24.7 GB resident (kernel log), with the other
  jobs holding the rest of the 54 GB: read the kernel log before blaming a cap. The engine held the echelon buffer
  twice while it grew and the two previous spaces in float64; `fast_ladder_blocks.py` removes both.
  The replay with it on an Azure D8ds_v6 (8 vCPU, 32 GB, westus3; D8ds_v5 has no quota in the subscription) gave
  the retained rows through degree 8 (1,422) at 13.0 GB peak in 3,690 s; the machine and its resource group were
  deleted after the record and logs were copied and their sha256 compared.

### E8-bar -> N- degree-3 products: the full standard basis on an 84 GB cloud VM

- Question and decisive outcome: whether `std(J + m P_3)` for the 225 degree-3 products of the 21 generators G of
  E8-bar -> N- finishes within 36 h; a finished basis would give the degree-3 normal forms and the membership rank
  h_3 (ledger A5-327).
- Formulation: the untruncated standard basis in one process; the jet-truncated rank (A5-031) was the cheaper route
  and decided h_3 = 225 (A5-092).
- Host and tool versions: the fourth Azure VM of the program (84 GB, `hv_balloon` maximum 86,016 MB), Singular from a sage
  wheel, p = 32009.
- Launch line and environment: `cg-run.sh e8nm_d3 78G 129600 Singular -q --no-rc --cpus=1 input.sing` with
  `MALLOC_ARENA_MAX=2`, a transient cgroup scope with `MemoryMax=78G` and `MemorySwapMax=0`, and `timeout -k 30`.
- Departures from the foundations: none.
- Parallelism: one process, one CPU.
- Memory and time limits: 78 GiB cgroup limit without swap, 129,600 s; a timeout shows as `e8nm_d3/exit` = 124.
- Checkpoints: `out.log` (generator count, target count, products time), `samples.tsv` (resident set every 30 s),
  `started`, `exit`, `all.done`.
- End state: the work tree copied and its sha256 verified, then the VM deallocated (`vm4/watch.out`); `vm4/watch.log`
  holds the five-minute poll of the job.
- Outcome: timeout at 129,600 s (exit 124), no standard basis, products built in 1,825 s, peak Singular resident set
  49,760,004 KiB, so the time cap ended the run; no measured-combinations row, since the run produced no result.

### Rees-graph elimination by msolve on a 32 GiB Kaggle kernel (Iso -> N-, Iso -> N+, W8 -> N+)

- Question and decisive outcome: whether msolve eliminates the Rees graph of Iso -> N-, Iso -> N+ and W8 -> N+ in one
  Kaggle session; a Groebner basis of the graph would give the defining ideal of the fiber cone (ledger A5-328;
  E8-bar -> N+ is A5-042).
- Formulation: full elimination `-e 1 -g 2`; a homogenized or Macaulay slice stays untested (A5-042).
- Host and tool versions: Kaggle CPU kernel, 4 cores, 32,869,288 KiB, Python 3.13.15, `passagemath-msolve` 10.8.13,
  p = 32009.
- Launch line and environment: `msolve -v 2 -t 4 -e 1 -g 2 -f input.ms -o gb.out`.
- Departures from the foundations: none.
- Parallelism: 4 threads on 4 cores.
- Memory and time limits: the kernel's 32 GiB; return code -9 at a peak of 31.37 million of 32.87 million KiB reads as
  an out-of-memory kill (hypothesis: the kernel's killer, not recorded in the log).
- Checkpoints: `msolve.log` (one line per F4 step), `samples.tsv` (resident set every 30 s), `result.json`.
- End state: the kernel output pulled and kept under `working/distribute/out/`.
- Outcome: killed at 9,069.4 s (Iso -> N-), 10,910.0 s (Iso -> N+) and 3,839.7 s (W8 -> N+) at 31.37 million KiB, in
  the degree-10 F4 step with 110,419, 110,419 and 52,198 pairs; `gb.out` empty.

### Local-syzygy fiber relations on a Kaggle CPU kernel (W8, E8-bar -> N+, Iso -> N+)

- Question and decisive outcome: whether the local-syzygy computation of the degree-2 fiber relations (degree 3 for
  Iso -> N+) finishes in one Kaggle session; the relations would give the quadric ideal K2 without the global
  products (ledger A5-329; the route is superseded by A5-044).
- Formulation: a local (`ds`) ordering, which the relations need (A5-044); the jet-truncated route replaced it.
- Host and tool versions: Kaggle CPU kernel, 4 cores, 32,869,288 to 32,869,296 KiB, Python 3.13.15, `passagemath-singular` 10.8.13,
  p = 32009.
- Launch line and environment: the Singular script `input.sing` of each kernel in a local (`ds`) ring, with a timeout
  of 41,000 s on the E8-bar -> N+ and Iso -> N+ kernels.
- Departures from the foundations: none.
- Parallelism: one Singular process.
- Memory and time limits: return code -9 at a peak near the kernel's 32 GiB (W8; hypothesis: an out-of-memory kill) and
  return code 124 at the 41,000 s timeout (E8-bar -> N+, Iso -> N+).
- Checkpoints: `singular.log` (generator and variable counts, the `syz` stage on Iso -> N+), `samples.tsv`,
  `result.json`.
- End state: the kernel output pulled and kept under `working/distribute/out/`.
- Outcome: W8 -> N- and W8 -> N+ killed at 5,437.4 and 6,207.5 s at 29.9 GiB; E8-bar -> N+ timed out at 41,047.0 s at
  18.8 GiB; Iso -> N+ degree 3 timed out at 41,051.8 s at 17.4 GiB in the `syz` stage.

### Engine v7 quotient export of E8-bar -> N- degree 4 at N = 14 to 16 in one Kaggle session

- Question and decisive outcome: whether one 41,000 s Kaggle session exports and ranks the quotient for N = 14, 15 and
  16 at degree 4; a rank at N = 15 equal to 495 would close the ladder (ledger A5-330).
- Formulation: engine v7 (`fiber_rank_v7.py`, sha256 prefix `a197799d97287b78`) in quotient mode on the header
  `e8-nm.sing`, one kernel per N.
- Host and tool versions: Kaggle CPU kernel, 4 cores, 32,869,292 KiB, Python 3.13.15, numpy 2.1.3, scipy 1.16.3,
  python-flint 0.9.0, p = 32009.
- Launch line and environment: one kernel per rung (`a5-v7-e8nm-d4-n14`, `-n15`, `-n16`) with the engine's admission
  limit `--max-gb 24.0` and a 41,000 s timeout.
- Departures from the foundations: none.
- Parallelism: not recorded.
- Memory and time limits: `--max-gb 24.0` (a refusal prints `preflight X GiB exceeds --max-gb 24.0`), 41,000 s.
- Checkpoints: `progress.log` (sizes of the export tables every 300 s), `summary.json`, `stderr.log`.
- End state: the kernel output pulled and kept under `working/kaggle-v7/out/`.
- Outcome: N = 14 refused by the admission check at 40,381.7 s (24.59 GiB against 24.0, equal to the preflight of the
  laptop record); N = 15 and 16 timed out at 41,000 s with three tables and none written. The laptop ran N = 15 (A5-324).

### Normalization of the E8-bar -> VB chart ideals on a Kaggle CPU kernel

- Question and decisive outcome: whether Singular `normal` finishes on the strict-transform chart ideals t3, t5 and t7
  of the point blowup of E8-bar -> VB; the normalization would give arcs for the degree-3 component (ledger A5-331,
  A5-016).
- Formulation: `normal` on one chart ideal, with the script writing the normalization out before any further basis
  computation; the build host's run of chart 5 is the counterpart.
- Host and tool versions: Kaggle CPU kernel, 4 cores; `summary.json` records the versions 10.9 and 4.4.1 (Singular
  4.4.1); p = 32009.
- Launch line and environment: kernel `a5-vb-arcs` (charts 3, 5, 7 at 14,400 s each, then the arc search on chart 7)
  and kernel `a5-vb-chart5` (chart 5 at 37,800 s).
- Departures from the foundations: none.
- Parallelism: one Singular process per chart, the three charts of `a5-vb-arcs` at once (14,509.6 s in all).
- Memory and time limits: the per-chart timeouts above (return code 124).
- Checkpoints: `snorm3.log`, `snorm5.log`, `snorm7.log`, `arcs7.jsonl`, `summary.json`.
- End state: the kernel output pulled and kept under `working/distribute/out/`; the build-host chart-5 files under
  `working/build/arc/n5/`.
- Outcome: no chart finished on Kaggle; the arc search on the chart-7 normalization from the build host raised
  `ValueError: min() iterable argument is empty` after 8.5 s; the build host finished chart 5 in 359 s.

### Minimal primes of the Iso -> N- quadric ideal K2 on a Kaggle CPU kernel

- Question and decisive outcome: whether `minAssChar` and `minAssGTZ` of K2 (17 variables, p = 32009) finish in one
  Kaggle session; a result would give the prime decomposition of K2 for Iso -> N- (ledger A5-332).
- Formulation: the whole-ideal decompositions; the chart criterion of
  `structure/iso-k2/chart-colon/README.md` decided that K2 is radical.
- Host and tool versions: Kaggle CPU kernel, 4 cores, 32,869,296 KiB, Singular 4.4.1, Python 3.13.15.
- Launch line and environment: kernel `a5-k2-iso-direct`, the two jobs `iso_k2_minAssChar` and `iso_k2_minAssGTZ`, 41,000 s
  each.
- Departures from the foundations: none.
- Parallelism: the two jobs at once, one process each (41,047.1 s in all).
- Memory and time limits: 41,000 s per job (return code 124).
- Checkpoints: `summary.json`, `a5-k2-iso-direct.log`, an empty `out.log` per job.
- End state: the kernel output pulled and kept under `working/distribute/out/`.
- Outcome: both jobs timed out at 41,000.1 s with no result.

### E8-bar degree-seven fiber-cone ranks from arc jets

- Question and decisive outcome: whether the degree-seven fiber-cone Hilbert function reaches 2,718 on the N- and
  N+ headers over each of F_32009 and F_32029. Arc-jet rank 2,718 and the retained K2 membership establish equality
  over that prime field. A lower plateau supplies a lower bound alone.
- Formulation: reuse the certified arc parametrization and compute exact jet functionals on the 2,718 standard
  monomials of K2. This avoids increasing the whole truncated local ideal. The degree-seven radical image has
  dimension 2,514, leaving 204 nilpotent classes to test.
- Host and tools: build host; Python 3.14.7, python-flint 0.9.0, Singular 4.4.1 for the basis exports. The retained
  degree-six producer keeps its bytes; `jet_rank_v2.py` and `e8_target_basis_v2.py` import the retained arithmetic.
- Launch and environment: `jet_rank_v2.py --target TARGET --degree 7 --arcs 6000 --step 100 --stall-steps 5 --write
  RECORD`, under `systemd-run --user --scope -q -p MemoryMax=12G -p MemorySwapMax=0`, GNU `time -v` and
  `timeout -k 10 3430`. `GOROROBA_WORKERS=4`, `MALLOC_ARENA_MAX=2` and all BLAS/OpenMP thread controls are 1;
  `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`. Four independent header/prime cells run serially, with each
  cell's arcs mapped through `parallel.py`.
- Calibration: four fresh Singular exports and their replays agree in dimension and monomials. The successor
  reproduces a retained degree-six record across 25 fields, reaching rank 1,666 from 1,800 arcs. A 200-arc
  degree-seven slice reaches rank 400 in 26.08 s wall, at 92,944 kB maximum resident set and zero swaps.
- Limits: the 6,000-arc budget extrapolates to 782.4 s before dense-rank growth; four times that estimate plus
  300 s gives the 3,430-second deadline. The multiplier is a scheduling allowance, not a measured complexity
  bound. The 12 GiB cgroup caps resident memory and page cache without constraining virtual address space.
  Exit 124 or a cgroup kill marks execution failure and retains the last checkpoint; neither refutes a
  mathematical equality. Five consecutive 100-arc steps with zero rank gain stop the cell as a lower bound.
- Checkpoints and end state: each 100-arc step rewrites its target-specific JSON under
  `docs/evidence/a5-exceptional-fibers/arc-jets/records/`; every arc carries J and K2 checks. The runner retains
  per-cell resource receipts and terminal markers in local scratch. [The arc-jet evidence](../evidence/a5-exceptional-fibers/arc-jets/README.md)
  carries the terminal ranks and sanitized resource table; provider jobs and uploads are outside this run.
- Outcome: all four cells reach rank 2,718 from 3,000 arcs / 6,000 rows with every J and K2 check passing.
  The terminal wall times and largest-process RSS values are in the linked evidence table; the equality is
  finite-field evidence through degree seven, with characteristic zero and higher degrees open.
