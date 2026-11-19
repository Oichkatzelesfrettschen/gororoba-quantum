# rcpt

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Degree-3 membership-receipt cost probe for E8-bar -> N- at p = 32009: normal forms of the 225 K2-standard cubic products modulo std(J + mS) and their exact rank (225 expected, zero relations). `out-d3.failed-127*` are failed attempts kept as the record of the failure.

Generator and command: `run-rcpt.sh` (included), which calls `docs/evidence/a5-kernel-attachments/fiber_cone_driver.py` (copy included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-04 to 2026-11-04.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.log` | 1 | 1028 | `driver-d3.log` |
| `*.sh` | 1 | 956 | `run-rcpt.sh` |
| `docs/evidence/a5-kernel-attachments/*.py` | 1 | 19948 | `fiber_cone_driver.py` |
| `out-d3.failed-127/*.log` | 1 | 407 | `d3-products.log` |
| `out-d3.failed-127b/*.log` | 1 | 408 | `d3-products.log` |
| `out-d3/*.log` | 1 | 365 | `d3-products.log` |
| `out-d3/*.txt` | 1 | 3382 | `targets.txt` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
