# q5

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Truncated method A cost probe: r = vdim std(J + m^N + mS) - vdim std(J + m^N + mS + S) for the K2-standard degree-d products S, over F_32009.

Generator and command: `probe.sh P D N` (included); outputs in `out/`.

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-04 to 2026-11-04.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.sh` | 1 | 1183 | `probe.sh` |
| `out/*.log` | 6 | 153 | `q32009-d2-n8.log`, `q32009-d3-n11.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
