# fpm

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: First batch of fiber-to-Plucker-map fits (`fiber_plucker_map.py`) per family (x, x-same, iso, w8, e8) and prime, 320 fit and 40 held-out samples.

Generator and command: `run-fpm.sh` (included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.json` | 9 | 6482 | `fiber-plucker-map-e8-p32009.json`, `fiber-plucker-map-iso-p32009.json` |
| `*.log` | 9 | 13954 | `fiber-plucker-map-e8-p32009.log`, `fiber-plucker-map-iso-p32009.log` |
| `*.sh` | 1 | 608 | `run-fpm.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
