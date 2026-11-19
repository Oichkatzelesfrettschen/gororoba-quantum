# band-mesh-out

Class: result (an output of a recorded run; no row of the findings ledger cites these files yet).

Question: Does the patched, mapped `mesh_model.py` of the Ascella CZ-tomography band evidence reproduce the committed serial run byte for byte? `summary.txt` records both runs, "outputs identical", and that the serial output differs from the retained record. This is Ascella band evidence, outside the A_5 fiber track; it sat beside the A_5 runs in the scratch directory and is kept here until the owner names a home.

Generator and command: `band-mesh.sh` (included): runs `docs/evidence/ascella-cz-tomography-band/mesh_model.py` serial, then with a patched copy, and compares with `cmp`..

Host role: the compute workstation. Dates (file modification times of the inventory): 2026-11-09 to 2026-11-09.

Content (`.time` files hold the wall time and peak memory of a run, `.done`, `.status` and `.exit` files its terminal marker):

| Path pattern | Files | Bytes | Examples |
|---|---|---|---|
| `*(none)` | 1 | 0 | `done` |
| `*.json` | 2 | 9302 | `mapped.json`, `serial.json` |
| `*.sh` | 1 | 919 | `band-mesh.sh` |
| `*.txt` | 1 | 95 | `summary.txt` |

Each file is listed with its sha256 in `SHA256SUMS` (verify with `sha256sum -c SHA256SUMS` from this directory). Home-directory paths in the files read `~`; the digest of each file before that rewrite, and the tracked path whose bytes a small marker or timing file happens to equal, are in [../SOURCE-DIGESTS.tsv](../SOURCE-DIGESTS.tsv). Scope: diagnostic working data over F_32009 and F_32029 unless a file says otherwise.
