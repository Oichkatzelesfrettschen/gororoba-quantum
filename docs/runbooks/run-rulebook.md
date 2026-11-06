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
