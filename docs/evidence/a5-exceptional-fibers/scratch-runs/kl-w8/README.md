# kl-w8

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Kernel-limit reruns for W8 at the cap-20 and cap-30 arc families.

Generator and command: command not recorded.

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 2 | 18 | `done`, `summary` |
| `*.json` | 1 | 728799 | `w8-c30-result.json` |
| `*.log` | 2 | 5170 | `w8-c20.log`, `w8-c30.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
