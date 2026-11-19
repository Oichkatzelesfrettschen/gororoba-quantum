# closure-windows

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: E8 closure certificate of E8-bar -> N- and N+ run on the Windows compute workstation from export commit 666b0a074: a bounded calibration, then write and check stages per sign with systemd admission, unit status and receipts, and mutation checks (a mutated cofactor and a mutated generator) that the checker rejects.

Generator and command: `closure-windows-orchestrate.sh`, `closure-windows-calibration.sh`, `closure-windows-service.sh`, `closure-windows-stage.py` (included); orchestrator log `windows-full-orchestrator.log`.

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-12 to 2026-11-12.

Content:

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.json` | 5 | 613683 | `windows-full-e8-nm-check-receipt.json`, `windows-full-e8-nm-write-receipt.json` |
| `*.log` | 6 | 5059 | `windows-closure-calibration.log`, `windows-full-e8-nm-check.log` |
| `*.py` | 2 | 11196 | `closure-windows-calibration.py`, `closure-windows-stage.py` |
| `*.sh` | 3 | 4809 | `closure-windows-calibration.sh`, `closure-windows-orchestrate.sh` |
| `*.txt` | 11 | 3735 | `windows-closure-calibration-admission.txt`, `windows-closure-calibration-budget.txt` |
| `e8-closure-certificate/checks/e8-nm-2282857-698476266474906/logs/*.log` | 2 | 1347 | `e8-closure-verify-e8-nm-mutate-cofactor.log`, `e8-closure-verify-e8-nm-mutate-generator.log` |
| `e8-closure-certificate/checks/e8-np-2283751-699212034113237/logs/*.log` | 2 | 1347 | `e8-closure-verify-e8-np-mutate-cofactor.log`, `e8-closure-verify-e8-np-mutate-generator.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
