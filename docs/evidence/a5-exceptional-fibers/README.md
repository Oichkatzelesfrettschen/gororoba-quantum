# A_5 exceptional fibers: working record

This directory retains the working record of the exceptional-fiber computations on the A_5 nullity-8 closures:
input scripts, run logs, relation and receipt files, consultant briefs and answers, the formal-arc certificate and
the Kaggle distribution scripts. The A_5 exceptional-fiber findings note states the results, the hypotheses tested
against them and what survives; this directory is the data it rests on. Results
here are diagnostic working data over F_32009 (and F_32029 where named) and enter the tracked claim record only
through the kernel-attachments ledger.

Every file of the working directory is retained, with home paths written `~`, the session scratch directory
`SCRATCH`, session identifiers `SESSION` or `UUID`, and the build host's name and owner handles replaced. Files
above 50 MB are split into 45 MB parts named `FILE.part00`, `FILE.part01`, ...; `cat FILE.part* > FILE` restores
the original bytes. The split files are listed in [split.txt](split.txt).

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
| `*-brief.md`, `greater-picture-*.md`, `final-review-*.md`, `review-*.md` | consultant briefs and answers |
