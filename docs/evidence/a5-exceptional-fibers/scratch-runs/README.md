# scratch-runs

Run families that the compute workstation held in an untracked scratch directory (runs of 2026-11-02 to 2026-11-15) and that no file of this repository recorded: the files here are those whose content equals no tracked file and that sit below 1.5 MB. Families that repeat a tracked file, copies of `gororoba_quantum/` modules and of other evidence directories, `.pyc` files and a 23 GB export tree are not imported. The files above the limit, with their sha256, are in [large-files-manifest.tsv](large-files-manifest.tsv); the sha256 of each imported file before the rewrite of home-directory paths to `~` is in [SOURCE-DIGESTS.tsv](SOURCE-DIGESTS.tsv).

Not imported: files above 1.5 MB and the derived Singular inputs and tables, which [large-files-manifest.tsv](large-files-manifest.tsv) lists with their sha256 (a `.pyc` file is neither imported nor listed).

Class: result (an output that a finding rests on) or scratch (a failed, terminated or superseded run kept as the record of the attempt). Each family directory holds a README (question, generator command as recorded, dates) and `SHA256SUMS` (`sha256sum -c SHA256SUMS` from the directory). `kernel-limits-variants/` holds the scripts that produced the `kl`, `fpm` and `vb-special` outputs.

| Directory | Class | Files | Bytes |
|---|---|---|---|
| [band-mesh-out](band-mesh-out/README.md) | result | 5 | 10316 |
| [blocks](blocks/README.md) | result | 2 | 2672 |
| [blockswap](blockswap/README.md) | scratch | 34 | 1818 |
| [clo](clo/README.md) | result | 6 | 429677 |
| [closure-windows](closure-windows/README.md) | result | 31 | 641176 |
| [codex-final](codex-final/README.md) | result | 24 | 143113 |
| [e8close](e8close/README.md) | result | 7 | 8839 |
| [e8cone](e8cone/README.md) | result | 9 | 2825 |
| [engine](engine/README.md) | result | 166 | 132622 |
| [export-rescue](export-rescue/README.md) | result | 1 | 983 |
| [fast](fast/README.md) | result | 12 | 18378 |
| [fpm](fpm/README.md) | result | 20 | 21349 |
| [fpm-line](fpm-line/README.md) | result | 8 | 5284 |
| [fpm2](fpm2/README.md) | result | 24 | 40515 |
| [fpm3](fpm3/README.md) | scratch | 5 | 2894 |
| [fpm4](fpm4/README.md) | scratch | 5 | 2894 |
| [iso-chart](iso-chart/README.md) | result | 8 | 32354 |
| [kl](kl/README.md) | result | 8 | 1136989 |
| [kl-iso](kl-iso/README.md) | result | 1 | 2959 |
| [kl-out](kl-out/README.md) | result | 6 | 72006 |
| [kl-pole](kl-pole/README.md) | result | 4 | 70745 |
| [kl-w8](kl-w8/README.md) | result | 5 | 733987 |
| [kl-xs](kl-xs/README.md) | result | 4 | 5934 |
| [mono](mono/README.md) | result | 23 | 62924 |
| [mprobe](mprobe/README.md) | result | 8 | 1964 |
| [probes](probes/README.md) | result | 86 | 34754 |
| [q5](q5/README.md) | result | 13 | 1402 |
| [qi-e8-w8](qi-e8-w8/README.md) | scratch | 4 | 71 |
| [qimod](qimod/README.md) | scratch | 8 | 489677 |
| [rcpt](rcpt/README.md) | result | 9 | 26785 |
| [replay](replay/README.md) | result | 167 | 58219 |
| [replay818](replay818/README.md) | result | 8 | 14650 |
| [replay818b](replay818b/README.md) | result | 5 | 3919 |
| [trash-2026-11-09](trash-2026-11-09/README.md) | scratch | 10 | 594 |
| [trunc](trunc/README.md) | result | 3 | 2111 |
| [vb-special](vb-special/README.md) | result | 3 | 18455 |
| [wsqr-qi](wsqr-qi/README.md) | scratch | 73 | 44105 |
| [xpm](xpm/README.md) | result | 24 | 28285 |
| [kernel-limits-variants](kernel-limits-variants/README.md) | code copy | 4 | 55188 |
