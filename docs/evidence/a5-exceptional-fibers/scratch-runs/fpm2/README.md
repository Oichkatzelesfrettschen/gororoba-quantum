# fpm2

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Fiber-to-Plucker-map fits with the mutation arm and a verdict (`degree_2_fit_validated`), for the N- and N+ headers.

Generator and command: `run-fpm2.sh` (included); `run-fpm-plus.sh` (included) is the N+ batch that waits for the first batch to finish..

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 2 | 726 | `done`, `summary` |
| `*.log` | 20 | 38341 | `fiber-plucker-map-e8-p32009.log`, `fiber-plucker-map-e8-p32029.log` |
| `*.sh` | 2 | 1448 | `run-fpm-plus.sh`, `run-fpm2.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
