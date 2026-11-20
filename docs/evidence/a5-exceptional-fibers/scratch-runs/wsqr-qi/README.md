# wsqr-qi

Class: scratch (a failed, terminated or superseded run kept as the record of the attempt).

Question: Diagnostics of the X- -> N- Cohen-Macaulay step over Q(i) in `weight_slice_quadric_rings`: stage timings, greedy regular-sequence picks (including a Singular type error), radical and CM records of five model schemes (`steps/`).

Generator and command: `run-full.sh`, `run-small.sh`, `run-v4.sh`, `diag/run*.sh` (included).

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-15 to 2026-11-15.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.done` | 1 | 7 | `small.done` |
| `*.json` | 1 | 5457 | `v3-small.json` |
| `*.load` | 2 | 148 | `full.load`, `small.load` |
| `*.log` | 1 | 3255 | `small.log` |
| `*.sh` | 3 | 1028 | `run-full.sh`, `run-small.sh` |
| `diag/*(none)` | 3 | 90 | `done`, `done3` |
| `diag/*.log` | 6 | 5030 | `chart.log`, `greedy.log` |
| `diag/*.n` | 2 | 4 | `cell.n`, `xm-N-.n` |
| `diag/*.py` | 2 | 1570 | `diag.py`, `diag2.py` |
| `diag/*.sh` | 3 | 1279 | `run.sh`, `run2.sh` |
| `diag/*.txt` | 2 | 8776 | `cell.polys.txt`, `xm-N-.polys.txt` |
| `steps-full/*.json` | 16 | 5778 | `double_plane.cm.json`, `double_plane.radical.json` |
| `steps-v3/*.json` | 24 | 9954 | `double_plane.cm.json`, `double_plane.radical.json` |
| `steps/*.json` | 7 | 1729 | `double_plane.cm.json`, `double_plane.radical.json` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
