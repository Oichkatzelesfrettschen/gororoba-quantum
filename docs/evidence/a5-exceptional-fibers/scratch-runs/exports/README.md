# exports

Manifests and producing scripts of the 36 Singular quotient exports (`std(J + m^N)`, its k-base and the multiplication tables of the variables) that the compute workstation held in an untracked export tree of 23.6 GB. The tables themselves are not retained: the sha256 of every file is in [../analysis/exports-file-digests.tsv](../analysis/exports-file-digests.tsv), the per-export verification in [../analysis/exports-audit.tsv](../analysis/exports-audit.tsv), and the files with equal bytes across directories in [../analysis/exports-digest-groups.tsv](../analysis/exports-digest-groups.tsv).

Each directory is named `FAMILY-pPRIME-nN-vENGINE`: FAMILY is `e8nm` (E8-bar -> N-), `e8-vb` (E8-bar -> VB), `isonm` (Iso -> N-), `w8nm` (W8 -> N-) or `xmnm` (same-sign X, X- -> N-; one directory is spelled `xm-nm`), PRIME is 32009 or 32029, N is the truncation order and ENGINE the fiber-rank engine (`replay/engine/fiber_rank_v9m.py`, `v11` or `v13`, or the first split export, `v9`). The retained files of a directory:

| File | Content |
|---|---|
| `export.json` | prime, variables, N, sha256 of the header `J` and of `G`, and the sha256 of each table the export wrote (`s.txt`, `qB.txt`, `qG.txt`, `qM1.txt` to `qM9.txt`) |
| `*.sha256` | the sidecar of each table (digest only; the tables are not retained) |
| `std.sing`, `qG.sing` | the Singular scripts that wrote `s.txt` and `qB.txt`, and `qG.txt` |
| `qG.txt` | the generators `G` of the fiber map (at most 127 KB; its sha256 equals `G_sha256` of `export.json` in every directory) |
| `q.sing` | not retained (the directory without `export.json` holds a copy of the `v9` export) |

`kbcheck.sing` and `qm1check.sing` are the scripts of the recomputation check at E8-bar -> N-, p = 32009, N = 15: the recomputed k-base (`kbcheck-n15.txt`) and the recomputed first multiplication table (`qM1-recomputed.txt`, 131.6 MB) have the sha256 of `qB.txt` and `qM1.txt` of `e8nm-p32009-n15-v9m` (rows of the digest groups table).

Home-directory paths in the scripts read `~`, the workstation name reads `build-host` and the login name `USER`; the digest of each file before that rewrite, and the tracked path whose bytes it equals (six `export.json` files and their sidecars equal the records of `../../vb-d7/exports/`, `../../n18-laptop/` and `../../w8-d6-n19-probe/`; `qG.txt` of E8-bar -> VB at p = 32009 equals `working/build/logs/mine/vb1.json/gens.txt`), are in [SOURCE-DIGESTS.tsv](SOURCE-DIGESTS.tsv). `sha256sum -c SHA256SUMS` from this directory verifies the retained files.
