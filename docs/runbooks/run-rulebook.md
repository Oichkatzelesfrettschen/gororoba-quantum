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
  52.1 GB after 7 h 29 min (32009). sat: 8 h limit at 15.1 and 15.8 GB. The `prot` traces show standard bases of
  20,000-37,000 elements still growing. The dense a0 = l0(G) makes every a0 z_i a polynomial with hundreds of terms;
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
  orphaned extension) to degree 15 with 37,018 elements and 25.7 GB resident, still growing, and ended when the VM's
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
