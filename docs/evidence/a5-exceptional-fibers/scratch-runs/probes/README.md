# probes

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: E8-bar -> VB standard-basis lever experiments (slimgb versus std ladder, local order, a laptop batch with a 10,800 s cap); the Singular inputs and k-bases are in the large-file manifest.

Generator and command: `vb-levers/ladder/run-ladder.sh`, `vb-levers/local-order/run-ds.sh`, `vb-levers/run-laptop.sh` (included).

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-09 to 2026-11-09.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `vb-levers/*.sh` | 1 | 517 | `run-laptop.sh` |
| `vb-levers/ladder/*.sh` | 1 | 522 | `run-ladder.sh` |
| `vb-levers/local-order/*.sh` | 1 | 582 | `run-ds.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
