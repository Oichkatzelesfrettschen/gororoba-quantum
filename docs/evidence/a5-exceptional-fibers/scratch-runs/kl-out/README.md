# kl-out

Class: result (an output of a recorded run; no row of the findings ledger cites these files yet).

Question: Rerun of the three kernel-limit records (x opposite, e8, vb limit span) with a byte comparison against the retained records in `summary.txt`. `summary.txt` records that `e8-result` and `vb-limit-span-result` equaled the retained records of the rerun checkout and `x-opposite-result` differed; the cause of that difference is not recorded, and the rerun's `x-opposite-result.json` is not imported.

Generator and command: `kl-rerun.sh` (included).

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-09 to 2026-11-09.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 1 | 0 | `done` |
| `*.log` | 3 | 70840 | `e8.log`, `vb.log` |
| `*.sh` | 1 | 993 | `kl-rerun.sh` |
| `*.txt` | 1 | 173 | `summary.txt` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
