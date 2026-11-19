# mprobe

Class: result (an output that a finding of the A_5 fiber track rests on).

Question: Monomial-span probe of the same-sign X slice: verdict `monomial_span` with the ranks of I and m_R I (973 and 958 at order 12 over F_32009).

Generator and command: `run-probe.sh` (included): `monomial_probe.py --slug SLUG --prime P --order N`, two cases at a time under a 16 GiB cap..

Host role: the compute workstation. Dates (file modification times, UTC date): 2026-11-10 to 2026-11-10.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 2 | 185 | `done`, `summary` |
| `*.log` | 5 | 1119 | `monomial-probe-xm-nm-p32009-n12.log`, `monomial-probe-xm-nm-p32009-n14.log` |
| `*.sh` | 1 | 660 | `run-probe.sh` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite is in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise; the files carry no claim row in [../../ledger.tsv](../../ledger.tsv).
