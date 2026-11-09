# Adversarial review of the C30 placement in the W8 fiber (2026-11-08)

Codex (gpt-daybreak-blue, high, read-only) and Grok read one brief ([brief.md](brief.md)) against commit 6144d16fd of
[structure/c30-bounded](../../../evidence/a5-exceptional-fibers/structure/c30-bounded/README.md):
[review-codex.md](review-codex.md) and [review-grok.md](review-grok.md). Local paths are scrubbed; the text is
otherwise as written.

Reconciliation, checked against the source:

- Step 2 (both): "s^2 is invertible" is false on {s = 0}; the Cartier twist of the Rees algebra replaces it.
- Step 4 (both; Grok: unproved, Codex: repairable): an order-10 jet does not prove divisibility by v2. Codex's repair
  holds: J and every G_j vanish identically on the chart curve of L0 for symbolic (b, c)
  (`structure/c30-bounded/l0/`), so the unique formal solution specializes to that curve and divisibility is exact.
  Grok's non-membership of 22 generators in the global polynomial ideal concerns the global ideal, not the germ.
- Grok's "K2 vanishing on six planes is not an identity": the vanishing is a control; T lies in E0, and E0 in V(K2)
  because K2 lies in L.
- Claim 5 (both): L = K2 follows from the projective Nullstellensatz, K2 radical and saturated; L need not be radical.
- Records (Codex): the degree-6 rows were left open while the text concluded every degree; they now read proved.
- Smaller defects (Grok): `run.sh` exited 0 on failure and expanded a glob through `ls`; README line 132 dropped "at
  least"; the degree-7 value had no retained `kbase` log. All three are fixed.
- QRNG (both): the brief pointed at indices 70 to 99, which `points.json` already assigns to controls, so the
  reviewers' further point reuses draw values; it is a reproduction and not retained as evidence.
