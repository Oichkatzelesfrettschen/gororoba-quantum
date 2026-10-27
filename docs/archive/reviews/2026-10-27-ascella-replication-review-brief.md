# Critical peer review: Ascella replication of the element-offset reading

You are an independent referee. Review the scientific result below as a referee for a physics journal would, with the statistical and hardware skepticism of `docs/runbooks/critical-peer-review.md` (read it first, and the source notes it cites). The review is read-only: change no tracked file, run no provider job, send nothing over the network except reading public documentation, and touch no credential or file under `~/.codex/auth*`, `~/.config/*/`, `~/.quantuminspire/`, `~/.qiskit/` or any token file. Python runs as `python3` with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`; scripts that use `parallel.ordered_map` need an `if __name__ == "__main__":` guard because the pool spawns. Put any scratch script under `docs/local/replication-review/scratch-REVIEWER/`.

## The result under review

Working tree: this repository, branch `quandela/ascella-replication-meshes` (pull request #569). Ascella (`qpu:ascella`, Quandela's 12-mode photonic processor) compiles one logical setting into a different physical mesh for each `compilation_seed`, and each served mesh shows a fixed error in the analyzer statistic X. A model of static per-heater and per-coupler offsets on the returned `computed_circuit` was fitted on earlier meshes, frozen, and scored on meshes served at fresh seeds.

- Claim under review: `ascella-signed-coherence-replication-offsets` in `docs/state/research_state.json`, and its predecessor `ascella-signed-coherence-new-seed-offsets`.
- Design and outcome: `docs/design/ascella-signed-coherence-conformance.md`, sections "New-seed meshes case (job-04 and job-05)" and "Replication case (job-06 and job-07)".
- Plans: `docs/state/plans/ascella-new-seed-meshes-case.json`, `docs/state/plans/ascella-replication-meshes-case.json`.
- Code: `scripts/ascella_new_mesh_score.py` (the score contract), `scripts/ascella_replication_score.py`, `scripts/ascella_replication_offsets.py`, `scripts/ascella_new_mesh_offsets.py`, `scripts/ascella_fixed_mesh_error.py`, `scripts/ascella_physical_models.py` (`static_light`, `static_mode`), `scripts/ascella_compilation_reading.py`, `scripts/ascella_coherence_request.py` (seeds, `compilation_seeds`).
- Records: `docs/evidence/ascella-order-coefficients/replication-score.json`, `replication-offsets.json`, `replication-push-order.json`, `new-seed-score.json`, `new-mesh-offsets.json`, `fixed-mesh-confirmation.json`, `seed-repeat-reading.json`; runs under `results/quandela/runs/*job-0[4-7]*`.
- Earlier context: the same design document's sections from "Perturbed-compilation case (job-02)" onward, and the Quandela issues Perceval#798 and #799, copied to `docs/local/replication-review/perceval-798.txt` and `perceval-799.txt`.

## What to deliver

Write your report to `docs/local/replication-review/report-REVIEWER.md` (REVIEWER is your tool name: codex, grok or agy). Structure it as a referee report:

1. Summary of the claim in your own words, and your overall recommendation (accept as stated, accept with revisions, or reject), with the decisive reasons.
2. Major issues, each with: the claim or code line it concerns (file:line), the defect, the evidence you obtained (a command you ran and its output, or a quoted line), its effect on the stated numbers or wording, and the revision you require.
3. Minor issues, in the same form.
4. Checks you ran that came out sound, so the authors know what was verified.
5. What an honest one-paragraph statement of the result would say, and what the follow-up text to Perceval issue #799 may and may not claim.

Consider at least: whether the preregistration and the push-before-draw ordering hold; whether the t-test's independence and distributional assumptions hold for these 168 meshes, and what a null that keeps the mesh structure would give; whether the returned circuit alone, without offsets, already predicts X; whether the "positive-direction share" is the right estimand for the wording "carries X % of the error", given the affine slope and the raw (unrescaled) predictive accuracy; overfitting of 258 free offsets on 86 or 233 training meshes; influence and heavy tails; the R-C versus R-B comparison and its confounds; multiplicity across the program's earlier tested families; calibration drift and the anchor control; and whether any number in the claims, design, PR body or `docs/local/perceval-799-followup.md` misstates the records. Verify every number you cite against the records; label inference apart from observation.

Finish the report with the line `DONE`.
