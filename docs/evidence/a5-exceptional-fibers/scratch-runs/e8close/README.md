# e8close

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: E8-bar -> N- ladder: the truncation order at which degree 3 reaches rank 225 and degree 4 reaches 495, over F_32009.

Generator and command: `run-e8close.sh` (included): `mono/fast_ladder2.py --slug e8-nm --prime 32009 --degree D --order N --threads 28` for (D,N) in (3,14) (3,16) (3,18) (4,18) (4,20) (3,20) (4,22), under a 44 GiB cap; only the first three cells have retained outputs..

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 1 | 50 | `summary` |
| `*.json` | 2 | 1457 | `e8-nm-p32009-d3-n14.json`, `e8-nm-p32009-d3-n16.json` |
| `*.log` | 3 | 6647 | `e8-nm-p32009-d3-n14.log`, `e8-nm-p32009-d3-n16.log` |
| `*.sh` | 1 | 685 | `run-e8close.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
