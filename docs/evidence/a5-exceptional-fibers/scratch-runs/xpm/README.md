# xpm

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Emission of the xp-nm and xm-np weight-slice headers at p = 32009 (root 10754) and p = 32029 (root 9115), with receipts and the surviving relation sets.

Generator and command: `run-emit.sh` (included): `fiber_inputs.py emit --prime P --root R --slug xp-nm --slug xm-np`.

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-04 to 2026-11-04.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 1 | 31 | `events` |
| `*.log` | 2 | 120 | `emit-32009.log`, `emit-32029.log` |
| `*.sh` | 1 | 513 | `run-emit.sh` |
| `.git/*(none)` | 3 | 188 | `HEAD`, `config` |
| `.git/hooks/*.sample` | 14 | 25827 | `applypatch-msg.sample`, `commit-msg.sample` |
| `.git/info/*(none)` | 1 | 240 | `exclude` |
| `out/survivors/*.json` | 2 | 1366 | `X--N+.json`, `X+-N-.json` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
