# replay

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Per-cell replay logs of the engine cells named in `replay-ids.txt` (raw and quotient modes at degree 1 to 5, orders 5 to 19, W8, Iso, X, E8 and E8-VB), each a JSON line with exit status and seconds.

Generator and command: command not recorded; `replay-ids.txt` lists the cells.

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-04 to 2026-11-05.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.sh` | 2 | 1769 | `run-e8n15-p1.sh`, `run-replay.sh` |
| `*.txt` | 33 | 4718 | `replay-ids.txt`, `log-E8-N--32009-d1-N5-raw.txt` |
| `out/E8-N--32009-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-N--32009-d2-N8-quotient/*.json` | 1 | 208 | `summary.json` |
| `out/E8-N--32009-d3-N11-quotient/*.json` | 1 | 210 | `summary.json` |
| `out/E8-N--32009-d4-N15-quotient/*.json` | 1 | 248 | `summary.json` |
| `out/E8-N--32029-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-N--32029-d3-N11-quotient/*.json` | 1 | 205 | `summary.json` |
| `out/E8-Np-32009-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-Np-32009-d3-N11-quotient/*.json` | 1 | 205 | `summary.json` |
| `out/E8-Np-32029-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-Np-32029-d3-N11-quotient/*.json` | 1 | 210 | `summary.json` |
| `out/E8-VB-32009-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-VB-32009-d5-N16-quotient/*.json` | 1 | 210 | `summary.json` |
| `out/E8-VB-32029-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-VB-32029-d5-N16-quotient/*.json` | 1 | 210 | `summary.json` |
| `out/Iso-32009-d1-N5-raw/*.json` | 1 | 190 | `summary.json` |
| `out/Iso-32009-d3-N10-quotient/*.json` | 1 | 207 | `summary.json` |
| `out/Iso-32009-d4-N13-raw/*.json` | 1 | 193 | `summary.json` |
| `out/Iso-32009-d5-N16-raw/*.json` | 1 | 194 | `summary.json` |
| `out/Iso-32029-d1-N5-raw/*.json` | 1 | 190 | `summary.json` |
| `out/Iso-32029-d4-N13-raw/*.json` | 1 | 193 | `summary.json` |
| `out/Iso-32029-d5-N16-raw/*.json` | 1 | 194 | `summary.json` |
| `out/W8-N--32009-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/W8-N--32009-d3-N10-quotient/*.json` | 1 | 209 | `summary.json` |
| `out/W8-N--32009-d4-N13-raw/*.json` | 1 | 196 | `summary.json` |
| `out/W8-N--32029-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/W8-N--32029-d3-N10-quotient/*.json` | 1 | 209 | `summary.json` |
| `out/W8-N--32029-d4-N13-raw/*.json` | 1 | 196 | `summary.json` |
| `out/X--32009-d1-N5-raw/*.json` | 1 | 189 | `summary.json` |
| `out/X--32009-d5-N19-quotient/*.json` | 1 | 207 | `summary.json` |
| `out/X--32029-d1-N5-raw/*.json` | 1 | 189 | `summary.json` |
| `out/X--32029-d5-N19-quotient/*.json` | 1 | 207 | `summary.json` |
| `out/Xp-32029-d1-N5-raw/*.json` | 1 | 189 | `summary.json` |
| `out/e8n15-p1/*.json` | 1 | 768 | `out.json` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
