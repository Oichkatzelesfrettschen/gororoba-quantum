# blockswap

Class: scratch (a failed, terminated or superseded run kept as the record of the attempt).

Question: Singular standard-basis timing logs for 32 five-letter sign patterns (`m`/`p`) and two local-order baselines of E8-bar -> N-; the Singular inputs are listed in the large-file manifest and the batch purpose is not recorded beyond the file names.

Generator and command: command not recorded.

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-04 to 2026-11-05.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.log` | 33 | 1378 | `local-e8-nm-----.log`, `local-e8-nm-++++.log` |
| `*.sh` | 1 | 440 | `run-e8.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
