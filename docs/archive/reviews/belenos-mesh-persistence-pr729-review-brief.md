# Adversarial review brief: Belenos mesh-persistence pull request (#729)

Review read-only: change no file, run no provider, network or job command, spawn no subagent. The subject is the
commit `5deb80f95` (branch `analysis/belenos-mesh-persistence` with `main` merged in) against `origin/main`. Read the
change with `git diff origin/main...5deb80f95` and each file with `git show 5deb80f95:PATH`, because the working
tree is being edited while this review runs. Read the repository's `AGENTS.md` and `ci/AGENTS.md` first.

Try to falsify the work. Report only defects verified against the files, most severe first, each with path and
line, what is wrong, the evidence, and the concrete fix, in under 800 words. Name the checks that found nothing.

## Checks

1. Statistics of `scripts/belenos_mesh_persistence.py`: the centered statistic T, the exact within-block relabeling
   p-value (`relabeled_values`, `exact_upper_p`, its tolerance and tie handling), the regression slope through the
   origin, its residual degrees of freedom and one-sided upper bound, the drift statistic and its degrees of
   freedom, and the secondary restrictions. Check each against the definition in `preregistered()` and in
   `docs/design/belenos-mesh-persistence-case.md`.
2. The power simulation: its generative model, the clipping of true shares, seed spawning, the use of the retained
   counts, and whether `results/quandela/belenos-mesh-persistence-power.json` follows from the code and the cited
   seed draw.
3. `gororoba_quantum/mesh_selection.py` (`sign_flip_cross_product` and the other functions the change touches)
   and `scripts/belenos_best_mesh_first_principles.py`: correctness of the label-invariant test, and whether the
   corrected numbers in `docs/design/belenos-best-mesh-design-investigation.md` and
   `docs/design/belenos-herald-leak-analysis.md` follow from `results/quandela/belenos-best-mesh-first-principles.json`.
4. Repository rules: retained records keep their bytes and a correction lands as a new field or successor; every
   new seed has a QRNG ledger entry in `docs/evidence/qrng_seeds/allocations.json`; reusable analysis lives in
   `gororoba_quantum/` with explicit inputs; independent CPU-bound loops run through `parallel.py`; a new document
   has a map row or inbound link; no mock outcome enters analysis.
5. The written hardware case: its duration bound, credit ceiling, `max_shots`, iteration count and the identity
   check; whether the case as frozen in `results/quandela/cases/belenos_mesh_persistence/job-00/cases.json` matches
   the design document; whether any step would submit without the owner's approval.
6. Tests: whether `tests/scripts/test_belenos_mesh_persistence.py` and
   `tests/gororoba_quantum/test_mesh_selection.py` would fail if the statistic, the reading thresholds or the block
   matching were wrong (mutation thinking), and what is untested.

Two findings of the hosted Codex review are already being fixed and need no report: the persistence analysis
functions move from the script into `gororoba_quantum/`, and the per-iteration histogram reductions in `analyze`
run through `parallel.ordered_map`.
