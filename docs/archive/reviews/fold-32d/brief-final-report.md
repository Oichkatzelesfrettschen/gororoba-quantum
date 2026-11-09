# Brief: final report on the twisted-double conjecture and the folding program

Same rules as docs/local/briefs/fold-deep-dive.md (read-only except your report; no commits, pushes, provider jobs or
cloud resources; no subagents; computations under 15 minutes in a scratch directory; seeds from
docs/evidence/anu_qrng/draw-2026-11-08T170257Z.json at indices you name, not 0-1, and not ones your first pass used).

Read first your own first-pass report docs/local/reviews/fold-deep-dive-codex.md, then the section "Folding: what it
reaches and what it does not (2026-11-08)" of docs/notes/topics/a5-hardware-algebra-synthesis.md (commit d6d31472b),
ledger rows A5-222 onward in docs/evidence/a5-exceptional-fibers/ledger.tsv, and docs/evidence/a5-w8-twisted-product/
if it exists.

## Conjecture under test

"The W8 closure is the i-twisted double of the sedenion zero-divisor cone", with the strengthening stated in the
synthesis: on W8 the 32-dimensional nullity is a function of the pair (n_16(z), n_16(z')).

1. Justify or falsify each part against the open items: A5-218 (the W8 and E8-bar -> VB same-dimension components),
   task "W8 arc families into V(P) and every component of V(K2 : P)", the h_d ladder of W8 (h_4 = 1725, h_5 = 4116,
   N = 3d + 1 law), characteristic 0 (the change of variables is defined over Z[i, 1/2]: does that make the twisted
   product a characteristic-0 statement outright?), and the block-swap proposition (blocks 2 and 3 equal): is the
   block swap the involution z <-> z' or something else? Test on data, not by analogy.
2. Test the nullity-pair law on W8 off the basis: seeded random points of V(J) x V(J) over F_32009, and points on
   special sub-loci (z = z', z' = conj-type images, one factor on a deeper sedenion stratum if J has one). Report the
   joint table (n_32, n_16(z), n_16(z')) and whether n_32 is a function of the pair on W8.
3. Check the synthesis's Macaulay argument (no tensor split of k[y]/K2 into two 12-generator halves) for an error, and
   say whether any other split (unequal, or along the z/z' grading of the fiber generators) survives.
4. N = 19 cost: name every fold, symmetry or product identity that could reduce the W8 degree-6 export or closure
   (block swap, the twist, the receipt), with the expected factor and the evidence; say plainly if none does.
5. Rocq: the exact statements to prove for (a) unconditional doubling over the reals (non-pure operand has nullity 0,
   reusing gororoba-open RecursiveCDTower.v and CDPureDoublingKernel.v), (b) the twisted-product identity as a
   polynomial lemma, (c) the mixed rule, each with the lemmas it reuses (file:line).

## Final report

Write docs/local/reviews/fold-final-report-codex.md, under 300 lines: first a table of every claim in the synthesis
section and your first pass with its final status (survives, refuted, open) and the decisive evidence (command and
output, file:line, or theorem); then what survives of the conjecture, in one paragraph; then the next computations
and proofs in order of value, each with cost, host and falsifier.
