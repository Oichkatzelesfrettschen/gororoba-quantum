# replay818b

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Same-sign X degree-8 cell at order 34 after the first replay batch, under a 40 GB cap.

Generator and command: `run-replay-n34.sh` (included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.log` | 1 | 800 | `float64-xm-nm-p32009-d8-n34.log` |
| `*.sh` | 1 | 741 | `run-replay-n34.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
