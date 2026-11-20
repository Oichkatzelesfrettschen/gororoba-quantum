# Reconciliation: local review of PR 956 (anu_qrng: retain the crossing-benchmark seed draw)

Head read: 19521300013d23d6bafe9f66556fe1ac1453b838 (the branch had this one commit over main). Reviewer: the local codex round (gpt-daybreak-blue, read-only, exit 0), chosen by the owner on 2026-11-19; the Advisor last. Every finding below carries its disposition; a fixing commit is named by its full hash after its diff was read.

| # | Finding | Source | Check | Verdict |
|---|---|---|---|---|
| F1 | SERIOUS: commit 195213000 states the crossing benchmark takes its six seeds from this draw; no tracked file references the draw and the allocation query returns [] | codex | git grep finds no reference outside the draw; docs/evidence/qrng_seeds/allocations.json has no row (AGENTS.md rule: each consumed index cited once) | Fixed in bd326bd1865429935f78edafa77a25e25277f697 (owned allocation row for indices 0 to 11 and docs/notes/qrng/external-consumers.md with the seed mapping) and 1e1139595cc4438802075ab77f3065f19442569e (README link); both diffs read |
| C1 | Claim 1: raw_sha256 and values match the raw bytes | codex | independent decode: sha_match, values_match, length 12, all uint16; scripts/anu_qrng.py check admits 95 draws | Passes |
| C2 | Claim 2: the record names no secret | codex | adapter puts the key in the request header only; bounded secret scan found no marker | Passes |
| C3 | Claim 3: an index of draws and consumers exists; update required only if consumed | codex | ci/seed_provenance.py --check passed with 443 literals accounted yet the draw had no consumer row | Fixed in the same two commits: the ledger row and the consumer note are the binding |
| A1 | Advisor (parent) | Advisor | read after the fixes | Passes after the PR body carries the owned ledger row and the consumer note (body updated) |
