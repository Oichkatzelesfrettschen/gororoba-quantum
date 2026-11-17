# Brief: pull request 886, the measurement-chain gaps of five backends

Reviewers: agy on gemini-4-hydrogen-high in its regular mode, and the Advisor. Head read by both: 12d384238.

Scope. The pull request adds `docs/notes/topics/backend-measurement-chain-gaps.md`, a map of the measurement chain of Tuna-17, QX, Ry, Ascella and Belenos (17 surviving gaps in table (a), 22 refuted or narrowed candidates in (b), the verification of the mined inventories in (c)) against the code, cases and retained records of this repository.

Inputs. The note, the repository at the head, the retained run directories and catalogue records, the note of pull request 940 (`docs/notes/quantum_inspire/tuna17-characterization-2026-11-16.md`) and the successor case of pull request 881.

Questions.

1. Does each statement of the note follow from the source it cites at this head?
2. Which claims are stated for all, every, none or a wildcard, and does a full scan of their population hold them?
3. Does any table row repeat what the repository already implements or documents?
4. Does each statement of live provider behavior carry the marker hypothesis and the check that decides it?
5. Do the labels, paths and wording of the note follow the repository's text rules?

Output. One row per finding, keyed by the row text of the note: the claim, the check against the source, the disposition (survives, refuted, bounded) and the commit.
