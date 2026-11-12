# A_5 exceptional fibers: working record

This directory retains the working record of the exceptional-fiber computations on the A_5 nullity-8 closures:
input scripts, run logs, relation and receipt files, consultant briefs and answers, the formal-arc certificate and
the Kaggle distribution scripts. The [findings note](../../notes/topics/a5-exceptional-fiber-findings.md) states
the results, the hypotheses tested against them and what survives; this directory is the data it rests on. Results
here are diagnostic working data over F_32009 (and F_32029 where named) and enter the tracked claim record only
through the [kernel-attachments ledger](../a5-kernel-attachments/README.md).

Every file of the working directory is retained except cloud run-control files named `ip` or `known_hosts*`
(public addresses and host keys, kept in the private infrastructure repository), with home paths written `~`, the session scratch directory
`SCRATCH`, session identifiers `SESSION` or `UUID`, and the build host's name and owner handles replaced. Files
above 50 MB are split into 45 MB parts named `FILE.part00`, `FILE.part01`, ...; `cat FILE.part* > FILE` restores
the original bytes. The split files are listed in [split.txt](split.txt). `sh retain_working.sh SOURCE_DIR` applies the same scrub and
split and copies every file whose scrubbed bytes differ from the retained copy (`--dry-run` lists them).

| Path under `working/` | Content |
|---|---|
| `purpose.md` | what the fiber computations measure and why |
| `decision-record.md` | chronological record of every run, failure, review and decision |
| `lab-map.md` | every machine, service, provider and policy gate available to the program |
| `runs/` | one directory per run: Singular input, log, exit code, relations, Hilbert counts |
| `runs/k2struct/` | radical and minimal-prime structure of the quadric ideal per pair |
| `build/` | input-provenance harness and degree driver reports, driver logs, the formal-arc certificate (`build/arc/`) |
| `build/inputs/` | Singular headers regenerated from the Q(i) producer at p = 32009 and p = 32029 |
| `probes/` | FLINT rank and relation extractors and small checks |
| `kaggle-tpu/`, `kaggle-pack-a/` | Kaggle TPU and CPU kernels, their outputs and research |
| `distribute/` | the Kaggle distribution brief, its peer review, the kernel generator and watcher; `distribute/out/` also holds the outputs of the stalled msolve, local-syzygy, normalization and K2 decomposition kernels (A5-328, A5-329, A5-331, A5-332) |
| `kaggle-v7/out/` | the outputs of the three engine v7 export kernels of E8-bar -> N- degree 4 at N = 14, 15 and 16 (A5-330) |
| `reviews/codex-reaudit/`, `arcs-p2/e8np-p32009/` | the producers of the re-audit records of [structure/reaudit](structure/README.md) and of the exact derivative of [arcs-vb](arcs-vb/README.md), and the twist-correspondence producers of [arcs](arcs/README.md), as run |
| `build/arc/n3/`, `build/arc/n5/`, `build/arc/chart.py`, `build/arc/snorm_write_first.sing` | the build host's normalization of charts 3 and 5 of E8-bar -> VB, the 14 order-1 arcs of chart 5, and the arc script and normalization script that produced them (`n5/inputs.sha256` verifies from `build/arc/`) |
| `azure-cases/` | the written cases under which cloud VMs ran |
| `exports/w8nm-n16-rcpt/` | manifest of the Singular export of W8 -> N- at N = 16, p = 32009 (`export.json`, producing scripts, `qG.txt`, full sha256 of each table); the 235 MB tables are regenerated from it ([w8-n16-azure](w8-n16-azure/README.md)) |
| [`azure-results/`](working/azure-results/README.md) | the complete work trees of Azure VMs `gororoba-a5-fiber`, `gororoba-a5-fiber-2` and `gororoba-a5-fiber-4`: archive hashes, restore command and the outputs they hold |
| `*-brief.md`, `greater-picture-*.md`, `final-review-*.md`, `review-*.md` | consultant briefs and answers |

The ignored `docs/local/` trees of the program were compared with every ref in the [retention audit](../../archive/reviews/untracked-records-audit-2026-11-11/README.md),
which sorts their files into result-missing, provenance-gap, scratch and failed-run groups and names the home of each;
the audit keeps no per-file listing, and its counts are its own. The records of `a5-failed-runs/`, `std-ladder/`,
`split-export-test/`, `arcs-vb/`, `arcs/`, `structure/` and the operational ledger rows A5-327 to A5-332 retain its
result-missing and failed-run groups.

The first line of each of the three msolve logs (`working/distribute/out/a5-iso-nm-msolve/msolve.log`,
`a5-iso-np-msolve/msolve.log` and `a5-w8-np-msolve/msolve.log`) reads `Initial seed for pseudo-random number generator
is N`, with N = 1793211011, 1793211033 and 1793211444. The recorded commands pass no seed option, so the value is the
tool's own seed of that retained run; it is kept as an identifier of the run and enters no seed ledger, because the
repository drew no seed for it. Measured: the msolve 0.11.0 help text documents `--random-seed` with the default `-1`,
meaning `time(0)`, and a local run of that build printed a seed equal to the Unix time at its start; the three logged
values read as the Unix times 2026-10-28T18:10:11Z, 18:10:33Z and 18:17:24Z. Hypothesis: the `passagemath-msolve`
10.8.13 wheel of the kernels (msolve version not recorded in the logs) seeds from the clock in the same way, and a
replay with `--random-seed N` reproduces the pseudo-random choices of the run.

The registry and its checks sit beside `working/` and read only from it:

| File | Content |
|---|---|
| [ledger.py](ledger.py) | [ledger.tsv](ledger.tsv): the claim ledger of the program, one row per equation, structural statement, method or operational finding with its status after falsification, basis, evidence paths and falsifier; `--check`, `--summary`, `--open` |
| [build_registry.py](build_registry.py) | builds [claims.json](claims.json), [certificates.jsonl](certificates.jsonl) and [unbound.jsonl](unbound.jsonl) from the retained records; `--check` rebuilds in memory. Scan roots, run from this directory in this order (the first root holding a record names its source): `d5-p2 degree-one n15-laptop n16-laptop n18-laptop d4-p2 xm-lown a5-failed-runs iso-d6-n19-laptop vb-d6-laptop w8-n16-azure vb-d7`; the scan reads `.json`, `.jsonl` and the engine-stdout `.out` records, and any other list rewrites the registry without `--check` |
| [witnesses.py](witnesses.py) | [witnesses.jsonl](witnesses.jsonl): header-pair identities, sign isomorphisms between paired fibers, and k2-span identities between each degree-2 receipt and each K2 source |
| [k2_hilbert.py](k2_hilbert.py) | [k2-hilbert.jsonl](k2-hilbert.jsonl): HF(k[y]/K2, d) for d = 1 to 7 from the 14 retained K2 sources (`k2_hilbert.py k2-hilbert.jsonl 7`) |
| [k2_cm.py](k2_cm.py) | [k2-cm.jsonl](k2-cm.jsonl): Cohen-Macaulay test of each k[y]/K2 by a general linear system of parameters, and the linearly joined structure of E8-bar -> VB |
| [degree-one/](degree-one/) | fresh degree-1 truncated ranks (N = 5) on the canonical headers |
| [n15-laptop/](n15-laptop/) | E8-bar -> N- at N = 15 on the workstation: engine v9 d = 4 at both primes (r 495, blocks 158, 137, 100, 100; certifies h_4 = 495, and h_4 of E8-bar -> N+ by the sign isomorphism), the engine v11 d = 4 control at p = 32009 (same blocks), and v11 d = 5 at both primes (r 742, blocks 168, 148, 213, 213, a lower bound against HF 952) |
| [a5-failed-runs/](a5-failed-runs/README.md) | the 36 run records and four engines (`fiber_rank_v4.py` to `v7.py`) of the ignored `docs/local/a5-failed-runs/` tree that the registry binds or lists as unbound, at their original relative paths, so the scan root of the same name rebuilds `claims.json`, `certificates.jsonl` and `unbound.jsonl` byte for byte from tracked files; ledger rows such as A5-080 cite them by these paths; four of the records, with per-block ranks below the K2 count of E8-bar -> N-, W8 -> N- and X-, bind nothing and enter the ledger as A5-324 |
| [std-ladder/](std-ladder/README.md) | Singular `std(J + m^N)` of E8-bar -> N- at p = 32009 for N = 12, 13 and 14: 627, 1,584 and 4,195 s, quotient lengths 11,595, 16,575 and 23,128, basis sizes 5,125, 6,739 and 8,687 (A5-321) |
| [split-export-test/](split-export-test/README.md) | the split quotient export of engine v9 against the serial export of engine v8 on E8-bar -> N- at p = 32009: 11 files byte-identical at N = 9 and N = 11, 31.3 against 37.3 s and 425.3 against 524.8 s (A5-322) |
| [n16-laptop/](n16-laptop/) | E8-bar -> N- at N = 16 and p = 32009 on the workstation with engine v11 (`replay/engine/fiber_rank_v11.py`): degree 5 gives r_16 = 742 with blocks 168, 148, 213, 213, equal to r_15 and below the K2 count 952 and the arc lower bound 861 of [arcs/](arcs/README.md), so it is a lower bound only; degree 4 gives r_16 = 495 with blocks 158, 137, 100, 100, equal to the K2 count 495 and to r_15; the registry scan roots include this directory, so [claims.json](claims.json) binds the degree-4 record (r_16 = 495, the K2 count) and leaves the degree-5 record, a lower bound below 952, unbound |
| [n18-laptop/](n18-laptop/README.md) | E8-bar -> N- at N = 18, both primes, engine v11: h_5 = 952 (A5-183, A5-220) and the degree-4 controls |
| [iso-d6-n19-laptop/](iso-d6-n19-laptop/README.md) | Iso degree 6 at N = 18 and 19: h_6 = 2,422 at both primes (A5-119, A5-125) |
| [xm-lown/](xm-lown/README.md) | X- ladders at degrees 2 to 4 (p = 32009), the last-jump law A5-244 out of sample, and the preregistered degree-6 split |
| [d4-p2/](d4-p2/README.md) | X- degree 4 at p = 32029: h_4 = 240 (A5-171), X+ by the sign isomorphism (A5-159) |
| [arcs/](arcs/README.md) | exact formal-arc certificates for E8-bar -> N- and E8-bar -> N+ at p = 32009 and p = 32029: two arc families per target with limit vectors dense in both components of V(K2), hence L inside sqrt(K2), a graded surjection F(I) -> k[y]/sqrt(K2) and h_5 >= HF(k[y]/sqrt(K2), 5) = 861 at all four targets; one implementation parameterized by target, the per-target records and a replay command |
| [d5-p2/](d5-p2/) | degree 5 at p = 32029 with engine v8: E8-bar -> VB at N = 16 (r 266) and X- at N = 19 (r 417), each equal to its K2 count; X+ follows by the sign isomorphism |
| [replay/](replay/) | the replay manifest of the certifying truncated-rank runs and its memory-scheduled runner |
| [v10-comparison.jsonl](v10-comparison.jsonl) | fiber-rank engine v10 (`replay/engine/fiber_rank_v10.py --k2-receipt`, products indexed by the standard monomials of k[y]/K2) against engine v9 (all products) on 11 small-N cases of four fibers at both primes: r_N and every block rank equal |
| [v11-comparison.jsonl](v11-comparison.jsonl) | fiber-rank engine v11 (`replay/engine/fiber_rank_v11.py`: per-block generator matrices built once, closure over per-block variable tables) against engine v9 on the v10 grid, the all-products and single-block paths, and E8-bar -> N- d = 4 at N = 15 (r 495, blocks 158, 137, 100, 100) |
| [arcs-x/](arcs-x/README.md) | exact formal-arc certificates for X+ -> N- and X- -> N+ at p = 32009 and p = 32029: linear arcs of the slice leave it with order-2 limit vectors (a1 W^2, a2 W (R + S), a3 W (R - S)) of Jacobian rank 3, so the reduced exceptional fiber is P^2 and F(I) = k[y1,y2,y3]; one implementation parameterized by the header's prime and root of -1, the per-prime logs, Singular scripts and records, and a replay command |
| [arcs-x-same/](arcs-x-same/README.md) | exact arc certificate for the same-sign incidences X- -> N- and X+ -> N+ at p = 32009 and p = 32029: the slice has the parametrization Phi(w, rho, sig, a), and the weighted arcs w = W s^2, rho = R s, sig = S s, a = A s have G of order 5, K2 vanishing identically on the limit and limit rank 4, so the fiber support has dimension 4 and equals V(K2) where V(K2) is irreducible (ledger A5-022); the Cohen-Macaulay conjecture A5-245 is refuted |
| [arcs-vb/](arcs-vb/README.md) | exact arc certificate for E8-bar -> VB at p = 32009 and p = 32029: the slice has the parametrization Phi(w, rho, sig, k), which contracts a line to the origin; arcs through a generic point of the line have limits dense in the degree-4 component of V(K2), and arcs through its point k = -9 with w at order 2 have limits dense in the degree-3 component, so E0 = V(K2) and F(I) = k[y]/K2 in every degree (ledger A5-005, A5-015, A5-016) |
| [arc_rank_check.py](arc_rank_check.py), [arc-rank-check.json](arc-rank-check.json) | recomputation without Singular (it shares the Python series evaluator of `kernel-limits`) of the limit-map ranks of the arc certificates of `blowup-arcs`, `arcs-x-same` and `arcs-vb`: each arc is rewritten from its formula and evaluated over F_p[eps]/(eps^2) by truncated power series, and the rank of [dF, F] equals the rank in the Singular log on all 24 rows (6 families, 2 primes, 2 parameter points), with J vanishing to the truncation order and the same order of G |
| [x-opposite-ladder/](x-opposite-ladder/README.md) | engine v11 truncated ranks r_N = 21, 28, 36, 45, 55 = C(d+2, 2) for d = 5 to 9 at N = 20 on the X+ -> N- and X- -> N+ headers (both incidences at p = 32009, X+ -> N- at p = 32029), corroborating the P^2 fiber of [arcs-x/](arcs-x/README.md); the degree-10 truncation to 0 and the measured Hilbert-Samuel ladder |
| [structure/](structure/README.md) | exact structure checks: the doubling automorphism (a, b) -> (a, -b) of A_5 exchanges X+ and X-, N+ and N- and proves the sign-pair fiber identities in every characteristic; E8-bar cut by mu' = 0 splits along N+- into a smooth and a multiplicity-2 sheet (the same-sign / opposite-sign difference); the kernel-map base locus is the B9 slice with residual the VB curve or the origin, at p = 32009, p = 32029 and over Q(i) |
| [w8-d5-probe/](w8-d5-probe/README.md) | W8 -> N- degree 5 at N = 10, 11, 12 and p = 32009 with engine v11: r_N = 0, 1,911 and 2,596, the cost probe that sized the N = 16 cloud run |
| [w8-n16-azure/](w8-n16-azure/README.md) | W8 -> N- degree 5 at N = 16 and p = 32009 with engine v11 on two Azure VMs: the receipt-bound run (4,116 standard representatives) and the unreceipted run (98,280 products) both give r_16 = 4116 with blocks 1017, 1005, 1047, 1047 = HF(k[y]/K2, 5), identical closure ranks and Singular exports with matching 64-bit SHA-256 prefixes, so h_5 = 4116 there; the second prime (`p32029/`) reads the same r_16 and blocks, and [claims.json](claims.json) binds the `.out` records of both primes through the scan root `w8-n16-azure` |
| [engine-v12/](engine-v12/README.md) | engine v12 (`replay/engine/fiber_rank_v12.py`): the per-block echelon basis on the CUDA device, acceptance runs against engine v11 on W8 degree 4 at N = 13 and Iso degree 6 at N = 19, byte-equal rank fields |
| [memory-bounded/](memory-bounded/README.md) | engine v14 (`replay/engine/fiber_rank_v14.py`) and the cell runner `replay/engine/rank_cell.py`: the W8 degree 5 at N = 16 acceptance summary (r_16 = 4116 with a 5.01 GiB process-group peak, the engine's stdout record, stderr and resource file retained) and the selected-array bound of the W8 degree-6, N = 19 route |
| [../a5-char0-transfer/](../a5-char0-transfer/README.md) | good reduction of the presolved germ ideal J and the generators G of all ten fiber-track pairs at both split primes, the first check of the characteristic-0 transfer (ledger A5-247) |
| [kernel-limits/](kernel-limits/README.md) | exact limits of ker L_a along the arcs, from the 32 x 32 left-multiplication matrix over k[[s]]: on X+ -> N- and X- -> N+ (both primes and Q, A5-272) and on both arc families of E8-bar -> N+- (both primes, A5-275) the kernel has dimension 8 along every arc and one limiting 8-plane per fiber point; on Iso, both components of W8 and the same-sign X incidences (A5-273, A5-274, A5-292), with rational arcs on all but the degree-20 component of W8 |
| [monomial-ladder/](monomial-ladder/README.md) | truncated ranks of the fiber cone without a standard basis, from a slice ring inside a power series ring: the same-sign X incidences reach h_7 = 996 and h_8 = 1,422 at p = 32009 (A5-298, A5-299), E8-bar -> N- reproduces 21, 83, 225 (A5-300), the truncated ideal of the same-sign X slice is a span of monomials at order 12 on both incidences and both primes and at order 14 on X- -> N- at 32009, and an exact certificate gives I = M at all four modular cells and F(I) = k[y]/K2 in every degree at the three cells with a retained K2 (X- -> N- at both primes, X+ -> N+ at 32029; A5-301, A5-304), and a batched float64 echelon returns the python-flint ranks (A5-302) |
| [quadric-census/](quadric-census/README.md) | saturation of the quadric ideals K2 at the irrelevant ideal for E8-bar -> VB, Iso, E8-bar -> N- and W8 -> N- at p = 32009 (all saturated, A5-308), and the radical of the E8-bar -> VB ideal: reduced, two components, Cohen-Macaulay with a linear resolution (A5-307); term supports and the Lie algebra of linear symmetries of the five K2, with a torus-rank bound that excludes a toric K2 on Iso and W8 -> N- (A5-310) |
| [hardware-orbits/](hardware-orbits/README.md) | the H-orbit of every A_5 operand that a hardware case measured (cd_core nullity, split coordinates, closure memberships, H-generator rank): six orbits carry a measured operand (W8, E8-bar, B9, V, VB, N-), no nullity mismatch; the four-term arcs e1 + e10 -> A16 (W8 -> N-) and e1 + e18 -> C8 (E8-bar -> VB) between measured operands, the six-term chord A16 -> C8, and the ledger rows A5-206 to A5-213 |
