# Quantum (quantum-journal.org) -- guidelines for referees and editorial policies

## Source copy and license

Web pages, not documents. Two retrieval receipts in [SOURCES.json](../../SOURCES.json) bind the inspected response
bytes; no copy is redistributed and the site's reuse terms were not inspected:

| Page | Retrieved | SHA-256 | Bytes |
|---|---|---|---|
| https://quantum-journal.org/instructions/referees/ | 2026-10-27T01:26:27Z | `b4278186d6b273a0b1be250e56660b83e410a77d9b00990ee46d85e99c01a74c` | 74137 |
| https://quantum-journal.org/editorial-policies/ | 2026-10-27T01:26:28Z | `fd5231305654e0f4b74b5fb18afc442f343a5793c8df4ced9b2f5b5fbe633f7e` | 81475 |

The pages are mutable; the hashes identify the inspected bytes. The APS Physical Review referee guidance
(https://journals.aps.org/authors/referee-guidelines) answered HTTP 403 to automated retrieval and is not admitted.

Tag convention: [P] marks page statements; [I] marks repository interpretation.

## Reading scope

The main text of both pages as rendered, without the site navigation. The referee page was read in full including the
reviewer form preview; the editorial-policies page was read to the section "Review process" (referee assignment,
deadlines, minimal number of reports) and not beyond.

## Referee questions (instructions/referees)

- [P] Peer review "should work towards improving papers"; referees answer specific questions in an online form. The
  journal is "highly selective": correct but incremental work is below threshold, and a very significant technical or
  conceptual contribution is necessary.
- [P] Original research must significantly advance the sub-field, contain a very significant technical or conceptual
  contribution, and "provide evidence that the employed methods or obtained results go significantly beyond the state of
  the art". Reviews must fill a gap and cover the literature comprehensively. Software showcases must show capabilities
  beyond the state of the art.
- [P] Private feedback to editors: overall rating (1 to 5 stars); recommendation (accept as is, revise and resubmit,
  reject); comments for the editor; willingness to referee an updated version.
- [P] Open-response questions, visible to authors:
  1. Summary: the main questions of the manuscript and how it answers them.
  2. Assessment of the paper; a recommendation to accept makes the case that the work is a significant contribution.
  3. "To what extent have you checked the technical correctness of the paper?"
  4. Presentation: well written, main results clear, "assumptions and limitations" described, literature review adequate.
  5. "If the submission includes numerical or physical experiments, does it provide sufficient details such that they
     could be reproduced by readers? This includes for example source code, documentation, experimental data,
     experimental setup specifications, etc."
  6. Suggested changes, corrections and general comments.
- [P] Referees declare conflicts of interest: close collaboration, personal relations, concurrent competitive research,
  same institution, financial co-dependence; the policies page adds a guideline of no joint papers with the submitting
  authors in the previous two years for referees.

## Editorial policies relevant to review

- [P] Single-blind review under an editor; submissions need an arXiv posting in quant-ph; at least two independent
  reports where possible; editorial rejection without external review is possible on formal or scientific grounds.
- [P] "The expected impact ... and the perceived seniority of the authors are not acceptance criteria."
- [P] No strict deadlines; the first referral asks for a report within about 30 days.

## Mapping to this repository

Relevance: (a) none, (b) none, (c) none; the source grounds [critical peer review of hardware results](../../runbooks/critical-peer-review.md).

- [I] Question 3 forces the reviewer to state the extent of the technical check; the runbook report format records which
  items were rerun and which were read only.
- [I] Question 5 sets the reproducibility bar for hardware results: source code, experimental data and setup
  specifications. In this repository that bar is the run record with its raw shot lists, the Target snapshot and the
  analysis digest.
- [I] Question 4 requires assumptions and limitations stated by the authors; the runbook turns it into the claim-wording
  and boundary items.
