# QRNG draws consumed outside this repository

A retained draw here can seed an analysis whose code and registration live in another repository. This file names each
such draw, the indices it gives and the mapping, so the allocation ledger
(`docs/evidence/qrng_seeds/allocations.json`, section `owned`) can mark the whole draw as taken and no case here reuses
an index of it.

| Draw record | Indices | Consumer | Mapping |
|---|---|---|---|
| `docs/evidence/anu_qrng/draw-2026-11-19T164733Z.json` | 0 to 11 (all) | the confirmatory crossing benchmark, a registration in a private repository that cites this record by path, sha256 and commit | seed k = values[2k] * 65536 + values[2k + 1] for k = 0 to 5, six analysis seeds in the registration's listed order |
