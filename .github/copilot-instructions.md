# Copilot instructions for gororoba-quantum

## Code review: adversarial and exhaustive by default

Review every pull request as an adversarial referee and an exhaustive reader. The pull-request description is a
claim to test, not a fact to summarize.

- Read the whole diff, then follow each changed symbol, path, digest, claim ID and theorem name through the
  repository: callers, tests, gates, ledgers, registry rows and the documents that cite it. Report a defect outside
  the diff when the change exposes it.
- Check every statement of the pull-request body against the source: each command it says ran, each check it says
  passes, each number. A validation step that no workflow runs on pull requests is a finding unless the body marks
  it `not run` with the reason.
- Mathematics and proofs: confirm that the theorem proved is the one stated (quantifiers, hypotheses, the edge cases
  zero, identity, first and last index), that no `Admitted`, `admit` or new axiom enters, and that each claim's
  status (proved, computed, measured, hypothesis) matches its evidence.
- Evidence: a file whose sha256 appears elsewhere in the tree keeps its bytes; raw records are never rewritten; every
  new random seed cites a QRNG draw file and index.
- Code: hunt unchecked exit statuses, silent fallbacks, off-by-one ranges, unit errors, warnings, tests that cannot
  fail and serial loops over independent items.
- Connections: when the change explains, duplicates or contradicts a result elsewhere in the repository or an open
  claim, name both places.
- Rank findings by consequence. Each cites file and line and states the failing input or the evidence; a finding you
  could not verify is marked as a hypothesis rather than dropped. State plainly what is correct, and list what you
  checked when you report no issues.

Repository rules a review checks here (`AGENTS.md`, `ci/AGENTS.md` and `docs/README.md` hold them in full):

- A merge needs the `pr.yml` checks `lint`, `types`, `tests` and `contracts`; historical replays and digest gates run
  on demand from `ci/gates.json`, never in a workflow.
- Every provider job, notebook session or QPU submission needs the owner's approval of a written case; a change that
  submits without one is a defect.
- Every new seed comes from a QRNG draw cited by file and index, enforced by `ci/seed_provenance.py`.
- Raw records under `raw/<job_id>/` and approval-hashed records keep their bytes; a claim that interprets an
  acquisition lands in a later change than the acquisition.
- Algebra: `gororoba_quantum/cd_core.py` is the specification; `a -> L_a` is a linear encoding, never a homomorphism;
  algebra index bit `b` sits on qubit `b`. Ledgers such as `docs/evidence/a5-exceptional-fibers/ledger.tsv` carry
  each claim's status, evidence and falsifier, and a sentence elsewhere may not claim more than its row.
- Every CPU-bound loop over independent items runs through `gororoba_quantum/parallel.py`.
- Text is American English and emoji-free.
