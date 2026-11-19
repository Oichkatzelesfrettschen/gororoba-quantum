# trunc

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Truncated fiber-rank ladder for W8 degree 3: the rank of the degree-d targets in k[t]/(J + m P_d + m^N), a lower bound on h_d that is nondecreasing in N.

Generator and command: `ladder2.sh JOBDIR PRIME STEP_TIMEOUT_S N...` (included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-10-31 to 2026-10-31.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.sh` | 1 | 1901 | `ladder2.sh` |
| `w8_d3/*.log` | 2 | 210 | `jout10.log`, `ladder2.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
