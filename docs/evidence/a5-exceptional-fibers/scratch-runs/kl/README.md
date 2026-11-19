# kl

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Kernel-limit reruns with the patched scripts: `plucker_limits.py` for e8 and x, `vb_limit_span.py`, compared with the retained records of `../kernel-limits/`.

Generator and command: `run.sh` and `vb.sh` (included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-09 to 2026-11-09.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.json` | 1 | 1065419 | `x-result.json` |
| `*.log` | 3 | 70840 | `e8.log`, `vb.log` |
| `*.sh` | 2 | 698 | `run.sh`, `vb.sh` |
| `*.txt` | 2 | 32 | `done.txt`, `vb-done.txt` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
