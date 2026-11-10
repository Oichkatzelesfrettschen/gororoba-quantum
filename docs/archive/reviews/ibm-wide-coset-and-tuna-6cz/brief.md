# Brief: adversarial review of branch claims/ibm-wide-coset-and-tuna-6cz

Read first: docs/local/briefs/workspace-AGENTS.md (a copy of the workspace guide), then AGENTS.md at the root of this
checkout. Spawn no subagents. Never commit, push, stash, submit to a provider, start a Kaggle session or create a
cloud resource. Change no repository file except your report. You may run git, `python3` (with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`), `python3 scripts/research_state.py --check`,
`python3 scripts/results_index.py claim ID`, and the analysis modules on the retained records, in a scratch directory
under /tmp, one computation at a time under 8 GiB.

Material: `git diff origin/main...HEAD` (three files: docs/state/research_state.json, docs/evidence/pathion-kernel-map/
README.md and its nhat-bias/README.md, docs/notes/topics/a5-hardware-algebra-synthesis.md), the claims
`hw-ibm-pathion-wide-coset` and `hw-tuna17-pathion-six-cz-null-blocks`, and every record they pin by sha256:
- results/live/pathion_wide_coset_analysis.json and the two collect.json runs;
- docs/evidence/pathion-kernel-map/census-wide.json and nhat-bias/result_wide.json;
- the Tuna-17 and QX analysis JSONs and the case's prediction.json.

Read the records as the authority.

## Claims under review (justify or falsify each)

1. Every number in both claims equals its record: readings, null controls, mutations, rule counts, placements, shots,
   billing, chi-squares and pooled values. Falsifier: one number that differs.
2. ibm_kingston passes 23 of 23 rules and 6 of 6 device-agreement rules, and ibm_fez fails exactly the eight rules
   named. Falsifier: a rule evaluated differently from the analysis code's definition.
3. The fez null-referenced difference failures restate its null-control failures, because each difference equals
   target minus null. Falsifier: a difference computed another way.
4. The Tuna claim establishes only the preregistered endpoint `unresolved_batch`, and nothing about coin-conditioned
   dropout. Falsifier: a preregistered rule that admits more.
5. The 64D/128D implications are each in the right evidence class:
   - nullities 0, 4, ..., D/2 - 4 at D = 32, 64 and 128, computed;
   - the maximum recurrence n -> 2n + 4, computed with a paper proof;
   - half-fold doubling, proved in CdHalfFold.v;
   - the runs touch no A_5 stratum.

   Falsifier: a computation that disagrees, or a "proved" label without a proof artifact.
6. The registry passes `research_state.py --check`, and the only unclaimed acquisition left is the Ascella replay.

Report also:
- systematic effects the analysis may not separate: calibration drift between batches, readout correlation,
  crosstalk across placements, TLS defects;
- a setting-by-setting comparison of the wide pair (fez, kingston) against the retained parallel-coset pair;
- conjectures the records suggest, each with its falsifier.

Rank by consequence, and mark each finding proved, computed, measured or hypothesis with its file:line or command
output. Write the report to the path on your command line, under 300 lines.
