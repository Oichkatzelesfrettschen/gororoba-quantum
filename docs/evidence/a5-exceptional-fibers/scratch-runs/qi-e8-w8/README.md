# qi-e8-w8

Class: scratch (a failed, terminated or superseded run kept as the record of the attempt).

Question: Terminal markers and logs of three Q(i) driver runs: W8 -> N- ended with `blocked_resource` (Singular status 137).

Generator and command: command not recorded.

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-10 to 2026-11-11.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*.done` | 3 | 15 | `qi-e8-nm.done`, `qi-e8-vb.done` |
| `*.log` | 1 | 56 | `qi-w8-nm.log` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
