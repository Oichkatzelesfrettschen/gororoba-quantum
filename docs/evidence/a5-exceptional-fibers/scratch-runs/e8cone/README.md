# e8cone

Class: result (an output of a recorded run; no row of the findings ledger cites these files yet).

Question: Fiber-cone check on E8-bar -> N-/N+: whether J is nonzero on the parametrization (`RESULT J nonzero on the parametrization 0`), over F_32009 and F_32029.

Generator and command: command not recorded; the Singular inputs are in the large-file manifest.

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-10 to 2026-11-11.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 1 | 7 | `done` |
| `*.done` | 2 | 14 | `e8-fiber-cone-e8-nm-p32029.done`, `e8-fiber-cone-e8-np-p32009.done` |
| `*.err` | 3 | 2678 | `e8-fiber-cone-e8-nm-p32029.err`, `e8-fiber-cone-e8-np-p32009.err` |
| `*.log` | 3 | 126 | `e8-fiber-cone-e8-nm-p32009.log`, `e8-fiber-cone-e8-nm-p32029.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
