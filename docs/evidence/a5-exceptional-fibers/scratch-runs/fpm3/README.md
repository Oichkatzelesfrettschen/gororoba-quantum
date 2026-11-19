# fpm3

Class: scratch (a failed, terminated or superseded run kept as the record of the attempt).

Question: Reruns of two `fpm2` cells; the files equal those of `fpm4` in size and are repeated runs.

Generator and command: `run-fpm3.sh` (included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 2 | 88 | `done`, `summary` |
| `*.log` | 2 | 2127 | `fiber-plucker-map-e8-p32029.log`, `fiber-plucker-map-x-same-p32009.log` |
| `*.sh` | 1 | 679 | `run-fpm3.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
