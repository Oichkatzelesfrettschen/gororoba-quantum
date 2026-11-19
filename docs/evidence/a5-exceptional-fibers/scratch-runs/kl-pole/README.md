# kl-pole

Class: result (an output of a recorded run; no row of the findings ledger cites these files yet).

Question: Rerun of the VB pole arcs (`vb_pole_arcs.py`) and its log.

Generator and command: command not recorded.

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-10 to 2026-11-10.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 1 | 5 | `done` |
| `*.done` | 1 | 5 | `rerun.done` |
| `*.log` | 2 | 70735 | `pole.log`, `rerun.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
