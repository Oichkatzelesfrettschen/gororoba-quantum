# replay

Class: result (an output of a recorded run; no row of the findings ledger cites these files yet).

Question: Per-cell replay logs of the engine cells named in `replay-ids.txt` (raw and quotient modes at degree 1 to 5, orders 5 to 19, W8, Iso, X, E8 and E8-VB), each a JSON line with exit status and seconds.

Generator and command: command not recorded; `replay-ids.txt` lists the cells.

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-04 to 2026-11-05.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 1 | 1583 | `events` |
| `*.sh` | 2 | 1769 | `run-e8n15-p1.sh`, `run-replay.sh` |
| `*.txt` | 33 | 4718 | `log-E8-N--32009-d1-N5-raw.txt`, `log-E8-N--32009-d2-N8-quotient.txt` |
| `out/E8-N--32009-d1-N5-raw/*.err` | 1 | 0 | `E8-N--32009-d1-N5-raw.err` |
| `out/E8-N--32009-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-N--32009-d1-N5-raw/*.jsonl` | 1 | 674 | `replay.jsonl` |
| `out/E8-N--32009-d1-N5-raw/*.out` | 1 | 674 | `E8-N--32009-d1-N5-raw.out` |
| `out/E8-N--32009-d2-N8-quotient/*.err` | 1 | 0 | `E8-N--32009-d2-N8-quotient.err` |
| `out/E8-N--32009-d2-N8-quotient/*.json` | 1 | 208 | `summary.json` |
| `out/E8-N--32009-d2-N8-quotient/*.jsonl` | 1 | 737 | `replay.jsonl` |
| `out/E8-N--32009-d2-N8-quotient/*.out` | 1 | 737 | `E8-N--32009-d2-N8-quotient.out` |
| `out/E8-N--32009-d3-N11-quotient/*.err` | 1 | 0 | `E8-N--32009-d3-N11-quotient.err` |
| `out/E8-N--32009-d3-N11-quotient/*.json` | 1 | 210 | `summary.json` |
| `out/E8-N--32009-d3-N11-quotient/*.jsonl` | 1 | 751 | `replay.jsonl` |
| `out/E8-N--32009-d3-N11-quotient/*.out` | 1 | 751 | `E8-N--32009-d3-N11-quotient.out` |
| `out/E8-N--32009-d4-N15-quotient/*.err` | 1 | 0 | `E8-N--32009-d4-N15-quotient.err` |
| `out/E8-N--32009-d4-N15-quotient/*.json` | 1 | 248 | `summary.json` |
| `out/E8-N--32009-d4-N15-quotient/*.out` | 1 | 0 | `E8-N--32009-d4-N15-quotient.out` |
| `out/E8-N--32029-d1-N5-raw/*.err` | 1 | 0 | `E8-N--32029-d1-N5-raw.err` |
| `out/E8-N--32029-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-N--32029-d1-N5-raw/*.jsonl` | 1 | 674 | `replay.jsonl` |
| `out/E8-N--32029-d1-N5-raw/*.out` | 1 | 674 | `E8-N--32029-d1-N5-raw.out` |
| `out/E8-N--32029-d3-N11-quotient/*.err` | 1 | 0 | `E8-N--32029-d3-N11-quotient.err` |
| `out/E8-N--32029-d3-N11-quotient/*.json` | 1 | 205 | `summary.json` |
| `out/E8-N--32029-d3-N11-quotient/*.jsonl` | 1 | 751 | `replay.jsonl` |
| `out/E8-N--32029-d3-N11-quotient/*.out` | 1 | 751 | `E8-N--32029-d3-N11-quotient.out` |
| `out/E8-Np-32009-d1-N5-raw/*.err` | 1 | 0 | `E8-Np-32009-d1-N5-raw.err` |
| `out/E8-Np-32009-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-Np-32009-d1-N5-raw/*.jsonl` | 1 | 674 | `replay.jsonl` |
| `out/E8-Np-32009-d1-N5-raw/*.out` | 1 | 674 | `E8-Np-32009-d1-N5-raw.out` |
| `out/E8-Np-32009-d3-N11-quotient/*.err` | 1 | 0 | `E8-Np-32009-d3-N11-quotient.err` |
| `out/E8-Np-32009-d3-N11-quotient/*.json` | 1 | 205 | `summary.json` |
| `out/E8-Np-32009-d3-N11-quotient/*.jsonl` | 1 | 751 | `replay.jsonl` |
| `out/E8-Np-32009-d3-N11-quotient/*.out` | 1 | 751 | `E8-Np-32009-d3-N11-quotient.out` |
| `out/E8-Np-32029-d1-N5-raw/*.err` | 1 | 0 | `E8-Np-32029-d1-N5-raw.err` |
| `out/E8-Np-32029-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-Np-32029-d1-N5-raw/*.jsonl` | 1 | 674 | `replay.jsonl` |
| `out/E8-Np-32029-d1-N5-raw/*.out` | 1 | 674 | `E8-Np-32029-d1-N5-raw.out` |
| `out/E8-Np-32029-d3-N11-quotient/*.err` | 1 | 0 | `E8-Np-32029-d3-N11-quotient.err` |
| `out/E8-Np-32029-d3-N11-quotient/*.json` | 1 | 210 | `summary.json` |
| `out/E8-Np-32029-d3-N11-quotient/*.jsonl` | 1 | 751 | `replay.jsonl` |
| `out/E8-Np-32029-d3-N11-quotient/*.out` | 1 | 751 | `E8-Np-32029-d3-N11-quotient.out` |
| `out/E8-VB-32009-d1-N5-raw/*.err` | 1 | 0 | `E8-VB-32009-d1-N5-raw.err` |
| `out/E8-VB-32009-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-VB-32009-d1-N5-raw/*.jsonl` | 1 | 668 | `replay.jsonl` |
| `out/E8-VB-32009-d1-N5-raw/*.out` | 1 | 668 | `E8-VB-32009-d1-N5-raw.out` |
| `out/E8-VB-32009-d5-N16-quotient/*.err` | 1 | 0 | `E8-VB-32009-d5-N16-quotient.err` |
| `out/E8-VB-32009-d5-N16-quotient/*.json` | 1 | 210 | `summary.json` |
| `out/E8-VB-32009-d5-N16-quotient/*.jsonl` | 1 | 745 | `replay.jsonl` |
| `out/E8-VB-32009-d5-N16-quotient/*.out` | 1 | 745 | `E8-VB-32009-d5-N16-quotient.out` |
| `out/E8-VB-32029-d1-N5-raw/*.err` | 1 | 0 | `E8-VB-32029-d1-N5-raw.err` |
| `out/E8-VB-32029-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/E8-VB-32029-d1-N5-raw/*.jsonl` | 1 | 668 | `replay.jsonl` |
| `out/E8-VB-32029-d1-N5-raw/*.out` | 1 | 668 | `E8-VB-32029-d1-N5-raw.out` |
| `out/E8-VB-32029-d5-N16-quotient/*.err` | 1 | 0 | `E8-VB-32029-d5-N16-quotient.err` |
| `out/E8-VB-32029-d5-N16-quotient/*.json` | 1 | 210 | `summary.json` |
| `out/E8-VB-32029-d5-N16-quotient/*.jsonl` | 1 | 745 | `replay.jsonl` |
| `out/E8-VB-32029-d5-N16-quotient/*.out` | 1 | 745 | `E8-VB-32029-d5-N16-quotient.out` |
| `out/Iso-32009-d1-N5-raw/*.err` | 1 | 0 | `Iso-32009-d1-N5-raw.err` |
| `out/Iso-32009-d1-N5-raw/*.json` | 1 | 190 | `summary.json` |
| `out/Iso-32009-d1-N5-raw/*.jsonl` | 1 | 636 | `replay.jsonl` |
| `out/Iso-32009-d1-N5-raw/*.out` | 1 | 636 | `Iso-32009-d1-N5-raw.out` |
| `out/Iso-32009-d3-N10-quotient/*.err` | 1 | 0 | `Iso-32009-d3-N10-quotient.err` |
| `out/Iso-32009-d3-N10-quotient/*.json` | 1 | 207 | `summary.json` |
| `out/Iso-32009-d3-N10-quotient/*.jsonl` | 1 | 709 | `replay.jsonl` |
| `out/Iso-32009-d3-N10-quotient/*.out` | 1 | 709 | `Iso-32009-d3-N10-quotient.out` |
| `out/Iso-32009-d4-N13-raw/*.err` | 1 | 0 | `Iso-32009-d4-N13-raw.err` |
| `out/Iso-32009-d4-N13-raw/*.json` | 1 | 193 | `summary.json` |
| `out/Iso-32009-d4-N13-raw/*.jsonl` | 1 | 671 | `replay.jsonl` |
| `out/Iso-32009-d4-N13-raw/*.out` | 1 | 671 | `Iso-32009-d4-N13-raw.out` |
| `out/Iso-32009-d5-N16-raw/*.err` | 1 | 0 | `Iso-32009-d5-N16-raw.err` |
| `out/Iso-32009-d5-N16-raw/*.json` | 1 | 194 | `summary.json` |
| `out/Iso-32009-d5-N16-raw/*.jsonl` | 1 | 682 | `replay.jsonl` |
| `out/Iso-32009-d5-N16-raw/*.out` | 1 | 682 | `Iso-32009-d5-N16-raw.out` |
| `out/Iso-32029-d1-N5-raw/*.err` | 1 | 0 | `Iso-32029-d1-N5-raw.err` |
| `out/Iso-32029-d1-N5-raw/*.json` | 1 | 190 | `summary.json` |
| `out/Iso-32029-d1-N5-raw/*.jsonl` | 1 | 636 | `replay.jsonl` |
| `out/Iso-32029-d1-N5-raw/*.out` | 1 | 636 | `Iso-32029-d1-N5-raw.out` |
| `out/Iso-32029-d4-N13-raw/*.err` | 1 | 0 | `Iso-32029-d4-N13-raw.err` |
| `out/Iso-32029-d4-N13-raw/*.json` | 1 | 193 | `summary.json` |
| `out/Iso-32029-d4-N13-raw/*.jsonl` | 1 | 670 | `replay.jsonl` |
| `out/Iso-32029-d4-N13-raw/*.out` | 1 | 670 | `Iso-32029-d4-N13-raw.out` |
| `out/Iso-32029-d5-N16-raw/*.err` | 1 | 0 | `Iso-32029-d5-N16-raw.err` |
| `out/Iso-32029-d5-N16-raw/*.json` | 1 | 194 | `summary.json` |
| `out/Iso-32029-d5-N16-raw/*.jsonl` | 1 | 682 | `replay.jsonl` |
| `out/Iso-32029-d5-N16-raw/*.out` | 1 | 682 | `Iso-32029-d5-N16-raw.out` |
| `out/W8-N--32009-d1-N5-raw/*.err` | 1 | 0 | `W8-N--32009-d1-N5-raw.err` |
| `out/W8-N--32009-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/W8-N--32009-d1-N5-raw/*.jsonl` | 1 | 642 | `replay.jsonl` |
| `out/W8-N--32009-d1-N5-raw/*.out` | 1 | 642 | `W8-N--32009-d1-N5-raw.out` |
| `out/W8-N--32009-d3-N10-quotient/*.err` | 1 | 0 | `W8-N--32009-d3-N10-quotient.err` |
| `out/W8-N--32009-d3-N10-quotient/*.json` | 1 | 209 | `summary.json` |
| `out/W8-N--32009-d3-N10-quotient/*.jsonl` | 1 | 732 | `replay.jsonl` |
| `out/W8-N--32009-d3-N10-quotient/*.out` | 1 | 732 | `W8-N--32009-d3-N10-quotient.out` |
| `out/W8-N--32009-d4-N13-raw/*.err` | 1 | 0 | `W8-N--32009-d4-N13-raw.err` |
| `out/W8-N--32009-d4-N13-raw/*.json` | 1 | 196 | `summary.json` |
| `out/W8-N--32009-d4-N13-raw/*.jsonl` | 1 | 688 | `replay.jsonl` |
| `out/W8-N--32009-d4-N13-raw/*.out` | 1 | 688 | `W8-N--32009-d4-N13-raw.out` |
| `out/W8-N--32029-d1-N5-raw/*.err` | 1 | 0 | `W8-N--32029-d1-N5-raw.err` |
| `out/W8-N--32029-d1-N5-raw/*.json` | 1 | 192 | `summary.json` |
| `out/W8-N--32029-d1-N5-raw/*.jsonl` | 1 | 642 | `replay.jsonl` |
| `out/W8-N--32029-d1-N5-raw/*.out` | 1 | 642 | `W8-N--32029-d1-N5-raw.out` |
| `out/W8-N--32029-d3-N10-quotient/*.err` | 1 | 0 | `W8-N--32029-d3-N10-quotient.err` |
| `out/W8-N--32029-d3-N10-quotient/*.json` | 1 | 209 | `summary.json` |
| `out/W8-N--32029-d3-N10-quotient/*.jsonl` | 1 | 732 | `replay.jsonl` |
| `out/W8-N--32029-d3-N10-quotient/*.out` | 1 | 732 | `W8-N--32029-d3-N10-quotient.out` |
| `out/W8-N--32029-d4-N13-raw/*.err` | 1 | 0 | `W8-N--32029-d4-N13-raw.err` |
| `out/W8-N--32029-d4-N13-raw/*.json` | 1 | 196 | `summary.json` |
| `out/W8-N--32029-d4-N13-raw/*.jsonl` | 1 | 687 | `replay.jsonl` |
| `out/W8-N--32029-d4-N13-raw/*.out` | 1 | 687 | `W8-N--32029-d4-N13-raw.out` |
| `out/X--32009-d1-N5-raw/*.err` | 1 | 0 | `X--32009-d1-N5-raw.err` |
| `out/X--32009-d1-N5-raw/*.json` | 1 | 189 | `summary.json` |
| `out/X--32009-d1-N5-raw/*.jsonl` | 1 | 642 | `replay.jsonl` |
| `out/X--32009-d1-N5-raw/*.out` | 1 | 642 | `X--32009-d1-N5-raw.out` |
| `out/X--32009-d5-N19-quotient/*.err` | 1 | 0 | `X--32009-d5-N19-quotient.err` |
| `out/X--32009-d5-N19-quotient/*.json` | 1 | 207 | `summary.json` |
| `out/X--32009-d5-N19-quotient/*.jsonl` | 1 | 737 | `replay.jsonl` |
| `out/X--32009-d5-N19-quotient/*.out` | 1 | 737 | `X--32009-d5-N19-quotient.out` |
| `out/X--32029-d1-N5-raw/*.err` | 1 | 0 | `X--32029-d1-N5-raw.err` |
| `out/X--32029-d1-N5-raw/*.json` | 1 | 189 | `summary.json` |
| `out/X--32029-d1-N5-raw/*.jsonl` | 1 | 642 | `replay.jsonl` |
| `out/X--32029-d1-N5-raw/*.out` | 1 | 642 | `X--32029-d1-N5-raw.out` |
| `out/X--32029-d5-N19-quotient/*.err` | 1 | 0 | `X--32029-d5-N19-quotient.err` |
| `out/X--32029-d5-N19-quotient/*.json` | 1 | 207 | `summary.json` |
| `out/X--32029-d5-N19-quotient/*.jsonl` | 1 | 737 | `replay.jsonl` |
| `out/X--32029-d5-N19-quotient/*.out` | 1 | 737 | `X--32029-d5-N19-quotient.out` |
| `out/Xp-32029-d1-N5-raw/*.err` | 1 | 0 | `Xp-32029-d1-N5-raw.err` |
| `out/Xp-32029-d1-N5-raw/*.json` | 1 | 189 | `summary.json` |
| `out/Xp-32029-d1-N5-raw/*.jsonl` | 1 | 642 | `replay.jsonl` |
| `out/Xp-32029-d1-N5-raw/*.out` | 1 | 642 | `Xp-32029-d1-N5-raw.out` |
| `out/e8n15-p1/*(none)` | 3 | 43 | `err`, `exit` |
| `out/e8n15-p1/*.json` | 1 | 768 | `out.json` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
