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
| [`azure-results/`](working/azure-results/README.md) | the complete work trees of Azure VMs `gororoba-a5-fiber` and `gororoba-a5-fiber-2`: archive hashes, restore command and the outputs they hold |
| `*-brief.md`, `greater-picture-*.md`, `final-review-*.md`, `review-*.md` | consultant briefs and answers |

The registry and its checks sit beside `working/` and read only from it:

| File | Content |
|---|---|
| [build_registry.py](build_registry.py) | builds [claims.json](claims.json), [certificates.jsonl](certificates.jsonl) and [unbound.jsonl](unbound.jsonl) from the retained records; `--check` rebuilds in memory |
| [witnesses.py](witnesses.py) | [witnesses.jsonl](witnesses.jsonl): header-pair identities, sign isomorphisms between paired fibers, and k2-span identities between each degree-2 receipt and each K2 source |
| [k2_hilbert.py](k2_hilbert.py) | [k2-hilbert.jsonl](k2-hilbert.jsonl): HF(k[y]/K2, d) for d = 1 to 6 from the 14 retained K2 sources |
| [k2_cm.py](k2_cm.py) | [k2-cm.jsonl](k2-cm.jsonl): Cohen-Macaulay test of each k[y]/K2 by a general linear system of parameters, and the linearly joined structure of E8-bar -> VB |
| [degree-one/](degree-one/) | fresh degree-1 truncated ranks (N = 5) on the canonical headers |
| [replay/](replay/) | the replay manifest of the certifying truncated-rank runs and its memory-scheduled runner |

