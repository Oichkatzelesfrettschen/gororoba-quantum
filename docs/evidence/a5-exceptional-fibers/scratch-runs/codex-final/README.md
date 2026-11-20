# codex-final

Class: result (an output of a recorded run; no row of the findings ledger cites these files yet).

Question: Singular option comparison at order 13 and 15: groebner, slimgb (baseline, degree bound, no reduced tail, reverse) and std (baseline, length); each log ends with a `RESULT ms` line. The `.s` inputs have the sizes of the `probes/vb-levers/ladder` inputs at n13 and n15 (large-file manifest).

Generator and command: command not recorded.

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-09 to 2026-11-09.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.log` | 8 | 136135 | `groebner-default-n13.log`, `slimgb-baseline-n13.log` |
| `*.status` | 8 | 16 | `groebner-default-n13.status`, `slimgb-baseline-n13.status` |
| `*.time` | 8 | 6962 | `groebner-default-n13.time`, `slimgb-baseline-n13.time` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
