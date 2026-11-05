# W8 -> N- degree 5, N = 16, p = 32009: receipt-bound and unreceipted runs compared

Records: `receipt-bound/w8d5-n16-rcpt.out` (westus3 FX4mds_v2, `--k2-receipt`, 2 workers) and
`unreceipted/w8d5-n16.out` (westus2 FX8mds_v2, no receipt, 4 workers). Both ran engine v11 sha256 `7849cbc7...` on
header sha256 `585a946d...` with passagemath Singular 4.4.1; the westus2 copies of the engine and the input were
re-hashed after the verified copy (`unreceipted/teardown.log`).

| Quantity | Receipt-bound | Unreceipted |
|---|---|---|
| products ranked | 4,116 (standard monomials of k[y]/K2) + 265 nonstandard checks | 98,280 |
| r_16 | 4116 | 4116 |
| per block r_N | 1017 / 1005 / 1047 / 1047 | 1017 / 1005 / 1047 / 1047 |
| per block rank_W | 15364 / 15264 / 15315 / 15315 | 15364 / 15264 / 15315 / 15315 |
| per block cols | 23376 / 23136 / 23256 / 23256 | same |
| dim quotient, closure rounds, tables | 93024, 5, sparse | 93024, 5, sparse |
| Singular export, sha256/16 of all 10 files | s.txt 47e95f5c..., qG c2d5f4d6..., qM1-7, qB | identical, file by file |
| seconds: Singular / products / closure / total | 752 / 2,201 / 4,751 / 7,841 | 688 / 2,473 / 9,264 / 13,429 |
| wall, peak RSS, preflight | 2:10:41, 24.9 GiB, 58.9 GiB | 3:43:48, 45.7 GiB, 97.8 GiB |
| VM cost (wall x hourly rate) | 2.18 h x $0.547 = $1.19 | 3.73 h x $1.094 = $4.08 |

Findings.

- h_5(F(W8)) = 4116 = HF(k[y]/K2, 5) at p = 32009, reached by two product sets (the 4,116 standard representatives
  and all 98,280 products) with the same per-block ranks of the closure space W, so the receipt path is confirmed on
  this instance: the 94,164 products the receipt drops add no rank, as its 265 sampled nonstandard checks showed.
- The Singular stage is deterministic across hosts and worker counts: all ten export files agree byte for byte, so
  the export kept on westus3 ([`working/exports/w8nm-n16-rcpt/`](../working/exports/w8nm-n16-rcpt/export.json), 235 MB; `qM7.txt` is split into 45 MB parts listed in `split.txt`, every data file matches its `.sha256`, and the scripts carry `~` for the VM home) is the export of either run.
- The receipt halves the closure (1.95x) and the peak memory (0.54x) on half the VM; the products stage drops only
  1.12x for 24x fewer products, so most of that stage's cost is independent of the product count. Inference, not
  profiled: the per-generator multiplication tables dominate it, so a further speedup lies there rather than in
  pruning more products; a py-spy profile of the products stage decides it.
- Blocks 2 and 3 are equal in both runs, as the block-swap proposition (block-swap proposition, findings note) requires.

Not tested: p = 32029; characteristic 0 (the char-0 rank is at least the F_p rank, while the upper bound needs the K2
Hilbert function over Q). The stack dump in `unreceipted/snapshot.txt` was taken seconds before the engine exited
(closure total already 9,263.5 s), not 30-40 min before, as first estimated.
