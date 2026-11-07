# Adversarial review brief: Ascella long-horizon seed repeat (job-08)

Review read-only: change no file, run no provider, network or job command, spawn no subagent. First read the
workspace guide `~/Projects/gororoba-workspace/AGENTS.md`, then this repository's `AGENTS.md` and `ci/AGENTS.md`.
The subject is commit `e98d5b324` on branch `quandela/ascella-long-horizon-seed-repeat` against `origin/main`; read
it with `git diff origin/main...e98d5b324` and `git show e98d5b324:PATH`. A 1.03-credit `qpu:ascella` job will be
submitted from this frozen case after this review, so a defect that would waste the job or bias its reading matters
most.

Try to falsify the work. Report only defects verified against the files, most severe first, each with path and
line, what is wrong, the evidence and the concrete fix, in under 800 words. Name the checks that found nothing.

## Checks

1. `gororoba_quantum/mesh_selection.py`: the sampled-relabeling path (`relabelings_of`, `slope_terms`,
   `relabeled_values`, `persistence`). Is a Monte Carlo p-value with the identity in the reference set valid for
   the persistence test, the useful-slope test and the inverted upper bound? Does the bisection stay monotone with
   sampled relabelings? Does the exact path keep its bytes and behavior?
2. `scripts/ascella_long_horizon_reading.py`: the ceiling generalization (counting variance scaled by 8,192 over
   samples), the reliability recorded beside the slope, pairing by setting name, the identity subset, the anchor
   control, the generator order (persistence, P1, P2), the not-read path, and whether the rehearsal record
   `docs/evidence/ascella-order-coefficients/long-horizon-rehearsal-02-03.json` follows from the code and agrees with
   `seed-repeat-reading.json`.
3. The power record `long-horizon-power.json`: its generative model (true error SD s_c, counting noise at 16,384 and
   32,768 samples, fresh error variance s_c^2 (1 - slope^2)), seed spawning from value 57 of the new draw, use of
   `parallel.ordered_map`, and whether the reading rule (alpha 0.01, useful slope 0.5) suits the question.
4. `scripts/ascella_coherence_request.py`: job-08's registration, the order draw and its consumed values 0..55,
   the `repeat_plan` field, and whether every earlier job's retained bytes are unchanged; the frozen
   `results/quandela/cases/ascella_signed_coherence/job-08/` request and body (samples, shots, credit ceiling
   1.032768, expected 205 s, 64 iterations, job-02's seeds by name).
5. The written case in `docs/design/ascella-signed-coherence-conformance.md` (section "Long-horizon seed-repeat case
   (job-08)") and the plan `docs/state/plans/ascella-long-horizon-seed-repeat-case.json`: does the text match the
   code, are the readings fixed before acquisition, is the primary reading single, and does the mesh-identity rule
   handle a compiler update that redraws meshes?
6. Repository rules: QRNG provenance of every new seed, the research-state acquisitions of the two sim runs,
   tests that would fail under a wrong statistic, emoji-free American English, no absolute paths.
