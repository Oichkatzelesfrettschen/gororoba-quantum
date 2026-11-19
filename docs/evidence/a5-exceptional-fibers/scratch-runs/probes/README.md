# probes

Class: result (an output of a recorded run; no row of the findings ledger cites these files yet).

Question: E8-bar -> VB standard-basis lever experiments (slimgb versus std ladder, local order, a laptop batch with a 10,800 s cap); the Singular inputs and k-bases are in the large-file manifest.

Generator and command: `vb-levers/ladder/run-ladder.sh`, `vb-levers/local-order/run-ds.sh`, `vb-levers/run-laptop.sh` (included).

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-09 to 2026-11-09.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `vb-levers/*.out` | 1 | 19 | `run.out` |
| `vb-levers/*.sh` | 1 | 517 | `run-laptop.sh` |
| `vb-levers/*.time` | 4 | 3424 | `laptop-vb-n18-base.time`, `laptop-vb-n18-slimgb.time` |
| `vb-levers/ladder/*.out` | 1 | 12 | `run.out` |
| `vb-levers/ladder/*.sh` | 1 | 522 | `run-ladder.sh` |
| `vb-levers/ladder/*.status` | 34 | 68 | `ladder-n1-slimgb.status`, `ladder-n1-std.status` |
| `vb-levers/ladder/*.time` | 34 | 27930 | `ladder-n1-slimgb.time`, `ladder-n1-std.time` |
| `vb-levers/local-order/*.out` | 1 | 0 | `run.out` |
| `vb-levers/local-order/*.sh` | 1 | 582 | `run-ds.sh` |
| `vb-levers/local-order/*.status` | 4 | 12 | `ds-n15.status`, `ds-n16.status` |
| `vb-levers/local-order/*.time` | 4 | 1668 | `ds-n15.time`, `ds-n16.time` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
