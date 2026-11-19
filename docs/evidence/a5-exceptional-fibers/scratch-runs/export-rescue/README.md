# export-rescue

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Helper that copies each finished file of a Singular quotient export out of the engine temporary directory and writes SHA256SUMS of the copies.

Generator and command: `rescue.sh SRC DST` (included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-02 to 2026-11-02.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.sh` | 1 | 983 | `rescue.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
