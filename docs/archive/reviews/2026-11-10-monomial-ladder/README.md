# Local review of the monomial ladder (pull request 818)

One reviewer read the first commit of the branch (`b02ae8d34`) on [brief.md](brief.md): the `codex` command-line
agent on gpt-daybreak-blue at high effort, read-only ([review-codex.md](review-codex.md)). The Advisor step of the
review chain did not run: the `advisor` tool was not available in the session. Each finding is checked against the
source below. `A5-NNN` is a row of [the A_5 claim ledger](../../../evidence/a5-exceptional-fibers/ledger.tsv).

| Finding | Verdict | Disposition |
|---|---|---|
| The degree-7 and degree-8 float64 records and the E8-bar degree-3 record come from an earlier version of the engine and carry no source digest, so A5-298 and A5-299 are not certified by them | survives | `fast_ladder.py` writes the SHA-256 of its sources and its library versions; the cells are replayed with the committed source (degrees 1 to 8 at orders 11 to 32, E8-bar degree 3 at order 14, and degree 7 at p = 32029); A5-298 and A5-299 now rest on the exact certificate A5-304, with the ladder as a cross-check. The order-34 cell needs more than 20 GB and three cells of the earlier engine remain, labeled in the README |
| The float64 exactness bound (sums of fewer than 2^17 terms) is promised for inputs the script does not check | survives | the script refuses p >= 2^15 and a space of 2^17 columns or more |
| Generator-times-basis products and multiplication maps run as serial loops over independent items | survives | they run through `parallel.ordered_map`; small cells reproduce the ranks, including the reviewer's own degree-3 cell (361, 239, 122) |
| A5-301 states the monomial span without bounding the order | survives | superseded in substance: A5-304 proves I = M exactly; A5-301 names the orders it computed |
| The README calls P + P b the E8-bar slice ring | survives | the text names R0 + R0 b inside P + P b |
| The "same host" timing comparison is in no record | survives | the sentence is removed; the agreement of dim A, dim B and r stays |
| Truncation cannot make r_N(d) exceed h_d | confirmed by the reviewer (proved) | no change |

The reviewer's three hypotheses: h_8 = 1,422 is proved (A5-299, through A5-304 and HF(k[y]/K2, 8) = 1,422);
h_9 = 1,955 and h_10 = 2,607 follow from the same certificate and `records/x-same-k2-hilbert-d10.jsonl`; h_7 = 996
at p = 32029 holds by the certificate and by two source-hashed ladder records.
