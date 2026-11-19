# wsqr-qi

Class: scratch (a failed, terminated or superseded run kept as the record of the attempt).

Question: Diagnostics of the X- -> N- Cohen-Macaulay step over Q(i) in `weight_slice_quadric_rings`: stage timings, greedy regular-sequence picks (including a Singular type error), radical and CM records of five model schemes (`steps/`).

Generator and command: `run-full.sh`, `run-small.sh`, `run-v4.sh`, `diag/run*.sh` (included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-15 to 2026-11-15.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.done` | 1 | 7 | `small.done` |
| `*.json` | 1 | 5457 | `v3-small.json` |
| `*.log` | 1 | 3255 | `small.log` |
| `*.sh` | 3 | 1028 | `run-full.sh`, `run-small.sh` |
| `diag/*.log` | 6 | 5030 | `chart.log`, `greedy.log` |
| `diag/*.py` | 2 | 1570 | `diag.py`, `diag2.py` |
| `diag/*.sh` | 3 | 1279 | `run.sh`, `run2.sh` |
| `diag/*.txt` | 2 | 8776 | `cell.polys.txt`, `xm-N-.polys.txt` |
| `steps-full/*.json` | 16 | 5778 | `Iso-N+.cm.json`, `Iso-N+.radical.json` |
| `steps-v3/*.json` | 24 | 9954 | `E8bar-N+.cm.json`, `E8bar-N+.radical.json` |
| `steps/*.json` | 7 | 1729 | `double_plane.cm.json`, `double_plane.radical.json` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
