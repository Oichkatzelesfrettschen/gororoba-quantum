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
| `distribute/` | the Kaggle distribution brief, its peer review, the kernel generator and watcher |
| `azure-cases/` | the written cases under which cloud VMs ran |
| `exports/w8nm-n16-rcpt/` | manifest of the Singular export of W8 -> N- at N = 16, p = 32009 (`export.json`, producing scripts, `qG.txt`, full sha256 of each table); the 235 MB tables are regenerated from it ([w8-n16-azure](w8-n16-azure/README.md)) |
| [`azure-results/`](working/azure-results/README.md) | the complete work trees of Azure VMs `gororoba-a5-fiber`, `gororoba-a5-fiber-2` and `gororoba-a5-fiber-4`: archive hashes, restore command and the outputs they hold |
| `*-brief.md`, `greater-picture-*.md`, `final-review-*.md`, `review-*.md` | consultant briefs and answers |

The registry and its checks sit beside `working/` and read only from it:

| File | Content |
|---|---|
| [ledger.py](ledger.py) | [ledger.tsv](ledger.tsv): the claim ledger of the program, one row per equation, structural statement, method or operational finding with its status after falsification, basis, evidence paths and falsifier; `--check`, `--summary`, `--open` |
| [build_registry.py](build_registry.py) | builds [claims.json](claims.json), [certificates.jsonl](certificates.jsonl) and [unbound.jsonl](unbound.jsonl) from the retained records; `--check` rebuilds in memory. Scan roots, run from this directory in this order (the first root holding a record names its source): `d5-p2 degree-one n15-laptop n16-laptop n18-laptop d4-p2 ../../local/a5-failed-runs iso-d6-n19-laptop`; any other list rewrites the registry without `--check` |
| [witnesses.py](witnesses.py) | [witnesses.jsonl](witnesses.jsonl): header-pair identities, sign isomorphisms between paired fibers, and k2-span identities between each degree-2 receipt and each K2 source |
| [k2_hilbert.py](k2_hilbert.py) | [k2-hilbert.jsonl](k2-hilbert.jsonl): HF(k[y]/K2, d) for d = 1 to 6 from the 14 retained K2 sources |
| [k2_cm.py](k2_cm.py) | [k2-cm.jsonl](k2-cm.jsonl): Cohen-Macaulay test of each k[y]/K2 by a general linear system of parameters, and the linearly joined structure of E8-bar -> VB |
| [degree-one/](degree-one/) | fresh degree-1 truncated ranks (N = 5) on the canonical headers |
| [n15-laptop/](n15-laptop/) | E8-bar -> N- at N = 15 on the workstation: engine v9 d = 4 at both primes (r 495, blocks 158, 137, 100, 100; certifies h_4 = 495, and h_4 of E8-bar -> N+ by the sign isomorphism), the engine v11 d = 4 control at p = 32009 (same blocks), and v11 d = 5 at both primes (r 742, blocks 168, 148, 213, 213, a lower bound against HF 952) |
| [n16-laptop/](n16-laptop/) | E8-bar -> N- at N = 16 and p = 32009 on the workstation with engine v11 (`replay/engine/fiber_rank_v11.py`): degree 5 gives r_16 = 742 with blocks 168, 148, 213, 213, equal to r_15 and below the K2 count 952 and the arc lower bound 861 of [arcs/](arcs/README.md), so it is a lower bound only; degree 4 gives r_16 = 495 with blocks 158, 137, 100, 100, equal to the K2 count 495 and to r_15; the registry scan roots do not include this directory, so [claims.json](claims.json) does not bind these two records |
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
| [x-opposite-ladder/](x-opposite-ladder/README.md) | engine v11 truncated ranks r_N = 21, 28, 36, 45, 55 = C(d+2, 2) for d = 5 to 9 at N = 20 on the X+ -> N- and X- -> N+ headers (both incidences at p = 32009, X+ -> N- at p = 32029), corroborating the P^2 fiber of [arcs-x/](arcs-x/README.md); the degree-10 truncation to 0 and the measured Hilbert-Samuel ladder |
| [structure/](structure/README.md) | exact structure checks: the doubling automorphism (a, b) -> (a, -b) of A_5 exchanges X+ and X-, N+ and N- and proves the sign-pair fiber identities in every characteristic; E8-bar cut by mu' = 0 splits along N+- into a smooth and a multiplicity-2 sheet (the same-sign / opposite-sign difference); the kernel-map base locus is the B9 slice with residual the VB curve or the origin, at p = 32009, p = 32029 and over Q(i) |
| [w8-n16-azure/](w8-n16-azure/README.md) | W8 -> N- degree 5 at N = 16 and p = 32009 with engine v11 on two Azure VMs: the receipt-bound run (4,116 standard representatives) and the unreceipted run (98,280 products) both give r_16 = 4116 with blocks 1017, 1005, 1047, 1047 = HF(k[y]/K2, 5), identical closure ranks and Singular exports with matching 64-bit SHA-256 prefixes, so h_5 = 4116 there |
| [hardware-orbits/](hardware-orbits/README.md) | the H-orbit of every A_5 operand that a hardware case measured (cd_core nullity, split coordinates, closure memberships, H-generator rank): six orbits carry a measured operand (W8, E8-bar, B9, V, VB, N-), no nullity mismatch; the four-term arcs e1 + e10 -> A16 (W8 -> N-) and e1 + e18 -> C8 (E8-bar -> VB) between measured operands, the six-term chord A16 -> C8, and the ledger rows A5-206 to A5-213 |
