# qimod

Class: scratch (a failed, terminated or superseded run kept as the record of the attempt).

Question: Modular-image Singular drivers of the Q(i) E8-bar -> N- and W8 -> N- rings; the done markers record `rc=143` (terminated).

Generator and command: command not recorded.

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-11 to 2026-11-11.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.c12` | 1 | 7 | `e8-nm.done.c12` |
| `*.done` | 3 | 19 | `e8-nm.done`, `iso.done` |
| `*.log` | 4 | 489651 | `e8-nm-driver.log`, `e8-nm-singular.c12.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
