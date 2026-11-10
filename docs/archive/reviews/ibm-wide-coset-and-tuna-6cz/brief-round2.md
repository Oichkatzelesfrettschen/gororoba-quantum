# Brief: second adversarial review of the wide-coset and six-CZ write-up

Read first: docs/local/briefs/workspace-AGENTS.md, then AGENTS.md at the root of this checkout (branch
integration/gororoba-quantum-ultrareview). Spawn no subagents. Never commit, push, stash, submit to a provider or
start a cloud resource; change no repository file except your report. You may run git and `python3` (with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`) on the retained records, one light computation at a time under
4 GiB in /tmp. This host is the owner's workstation: run nothing heavy.

The first review (docs/archive/reviews/ibm-wide-coset-and-tuna-6cz/review-codex.md) found no claim falsifier. This
round attacks the write-up written after it, which that review never read:
- docs/archive/reviews/ibm-wide-coset-and-tuna-6cz/analysis-claude.md: the ibm_fez qubit-90 calibration finding and
  the setting comparison;
- docs/archive/reviews/ibm-wide-coset-and-tuna-6cz/README.md: the reconciliation;
- docs/archive/reviews/ibm-wide-coset-and-tuna-6cz/literature-drift-systematics.md: the literature report;
- the 64D/128D subsection of docs/evidence/pathion-kernel-map/README.md.

Claims to justify or falsify:
1. ibm_fez's execution-time calibration in `results/live/2026-11-07T153325.440007Z/collect.json` gives qubit 90
   prob_meas0_prep1 = 0.835, the collector inverted that channel (`gororoba_quantum/live_run.py` corrected_summary),
   and the raw marginal 0.919 contradicts it. Recompute the raw marginal of that bit from the raw counts yourself.
2. Placement 2 contributes -0.113 and -0.068 to the n64 and n128 null totals, so the fez null failures stand without
   it, and no verdict changes.
3. Kingston's per-block null offset of about -0.03 recurs between the parallel and wide runs. The tensor-product
   readout residual hypothesis has a falsifier that can fire.
4. Each literature citation points at a document and page that says what the report claims. Open at least three of
   the five strongest sources and check them.
5. The reconciliation's verdicts match review-codex.md, and nothing in it overstates.

Rank by consequence and mark each finding proved, computed, measured or hypothesis with its file:line or command
output. Write the report to docs/archive/reviews/ibm-wide-coset-and-tuna-6cz/review-codex-round2.md, under 200 lines.
