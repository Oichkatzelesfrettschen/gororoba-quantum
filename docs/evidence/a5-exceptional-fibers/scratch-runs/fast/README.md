# fast

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Fast-ladder logs and records at high degree: same-sign X (xm-nm) degree 6 to 8 at orders 26 to 32 and E8-bar -> N- degree 6 at order 18.

Generator and command: command not recorded; the warning path in the logs names `fast_ladder2.py` of the `mono` family.

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 2 | 150 | `done`, `summary` |
| `*.json` | 3 | 3000 | `xm-nm-p32009-d6-n26.json`, `xm-nm-p32009-d7-n29.json` |
| `*.log` | 7 | 15228 | `e8-nm-p32009-d6-n18.log`, `xm-nm-p32009-d6-n26.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
