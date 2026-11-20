# trash-2026-11-09

Class: scratch (a failed, terminated or superseded run kept as the record of the attempt).

Question: Export manifests of two E8-bar -> VB v11 exports at N = 22 that were moved aside.

Generator and command: command not recorded.

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-09 to 2026-11-09.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.err` | 2 | 0 | `e8vb_d7_n22_p32009.err`, `e8vb_d7_n22_p32029.err` |
| `*.time` | 2 | 0 | `e8vb_d7_n22_p32009.time`, `e8vb_d7_n22_p32029.time` |
| `e8-vb-p32009-n22-v11/*.json` | 1 | 271 | `export.json` |
| `e8-vb-p32009-n22-v11/*.lock` | 1 | 0 | `.lock` |
| `e8-vb-p32009-n22-v11/*.owner` | 1 | 26 | `.owner` |
| `e8-vb-p32029-n22-v11/*.json` | 1 | 271 | `export.json` |
| `e8-vb-p32029-n22-v11/*.lock` | 1 | 0 | `.lock` |
| `e8-vb-p32029-n22-v11/*.owner` | 1 | 26 | `.owner` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
