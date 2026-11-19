# mono

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Monomial-ladder variants (`fast_ladder.py`, `fast_ladder2.py`, `e8_monomial_probe.py`, `monomial_probe.py`, `grading_probe.py`) with E8-bar -> N- ladder records at degree 2 to 4 over F_32009.

Generator and command: `run-e8.sh` (included): `monomial-ladder` scripts for (D,N) in (2,10) (2,12) (3,12) (3,14) (4,14) (4,16) under a 30 GiB cap..

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.log` | 11 | 15085 | `e8-nm-p32009-d2-n10.log`, `e8-nm-p32009-d2-n12.log` |
| `*.py` | 6 | 32596 | `e8_monomial_probe.py`, `fast_ladder.py` |
| `*.sh` | 3 | 2003 | `run-e8.sh`, `run-fast.sh` |
| `clean/*.py` | 1 | 12965 | `fast_ladder.py` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
