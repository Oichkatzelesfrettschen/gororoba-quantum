# Review and audit reports

Orchestrator-side reviews of pull requests and read-only audits of main. Each
report records the commit it read; the pull request threads and the merge
commits that followed hold the resolution of every finding. Paths are
repository-relative; a branch name stands for its worktree.

| Report | Subject |
|---|---|
| [tuna-sequential-sensitivity-review.md](tuna-sequential-sensitivity-review.md) | Exact constant-response sensitivity and its model-specific interpretation |
| [tuna-capture-prefix-retention-review.md](tuna-capture-prefix-retention-review.md) | Retention-order review, historical receipt interpretation and unresolved quarantine |
| [tuna-capture-prefix-budget-review.md](tuna-capture-prefix-budget-review.md) | Prefix validation order, fixed-overhead bound and recovery limitations |
| [tuna-journaled-collection-followup-review.md](tuna-journaled-collection-followup-review.md) | Identifier repair, response metadata mismatch and remaining fault coverage |
| [tuna-journaled-collection-review.md](tuna-journaled-collection-review.md) | Collector and commitment composition, locator bounds and failure-coverage review |
| [tuna-identity-continuity-followup-review.md](tuna-identity-continuity-followup-review.md) | Identity comparison repairs and remaining authenticated, concurrent and restart boundaries |
| [tuna-capture-bounds-review.md](tuna-capture-bounds-review.md) | Capture metadata bounds review and subsequent repair targets |
| [tuna-qx-destination-initial-review.md](tuna-qx-destination-initial-review.md) | Initial independent review of the reduced QX destination verifier and case |
| [tuna-qx-destination-followup-review.md](tuna-qx-destination-followup-review.md) | Follow-up review of QX destination verifier repairs and remaining pagination and provenance findings |
| [tuna-qx-destination-repair-review.md](tuna-qx-destination-repair-review.md) | Review of pagination and provenance repairs, with remaining backend-capability findings |
| [tuna-qx-destination-capacity-review.md](tuna-qx-destination-capacity-review.md) | Review of backend-capability checks and residual regression coverage |
| [tuna-qx-destination-mutation-review.md](tuna-qx-destination-mutation-review.md) | Focused review of backend-capability type and gate mutation coverage |
| [tuna-sequential-score-review.md](tuna-sequential-score-review.md) | Independent review of the prospective Tuna sequential score and its regression gaps |
| [tuna-sequential-score-followup-review.md](tuna-sequential-score-followup-review.md) | Follow-up review of scoring mutation tests and statistical-design bindings |
| [tuna-destination-slot-alternatives-review.md](tuna-destination-slot-alternatives-review.md) | Independent review of Tuna slot alternatives, allocation custody and submission boundaries |
| [tuna-destination-slot-alternatives-followup-review.md](tuna-destination-slot-alternatives-followup-review.md) | Review of slot tree hard-link checks and assignment custody requirements |
| [tuna-assignment-commitment-review.md](tuna-assignment-commitment-review.md) | Independent review of the prospective assignment commitment and raw ANU validation |
| [tuna-assignment-commitment-followup-review.md](tuna-assignment-commitment-followup-review.md) | Follow-up review of raw ANU validation and remaining mutation coverage |
| [tuna-assignment-commitment-final-review.md](tuna-assignment-commitment-final-review.md) | Focused review of commitment parser regression-mutation repairs |
| [tuna-qx-exact-dispatch-guard-review.md](tuna-qx-exact-dispatch-guard-review.md) | Independent review of the prospective QX dispatch transaction and its unresolved requirements |
| [tuna-qx-exact-dispatch-guard-followup-review.md](tuna-qx-exact-dispatch-guard-followup-review.md) | Follow-up review of dispatch authority, billing, lock, clock and provider observation requirements |
| [tuna-dispatch-clock-review.md](tuna-dispatch-clock-review.md) | Independent review of the offline dispatch clock and its integration boundaries |
| [tuna-dispatch-clock-followup-review.md](tuna-dispatch-clock-followup-review.md) | Follow-up review of clock input validation, state protection and integration limits |
| [tuna-dispatch-clock-final-review.md](tuna-dispatch-clock-final-review.md) | Byte-bound review of clock fixes and remaining adapter requirements |
| [tuna-source-association-review.md](tuna-source-association-review.md) | Independent review of source, job, batch and result association checks |
| [tuna-source-association-followup-review.md](tuna-source-association-followup-review.md) | Follow-up review of result-page and provider-association predicates |
| [tuna-slot-associated-decoder-review.md](tuna-slot-associated-decoder-review.md) | Review of slot-bound source association and complete-result decoding |
| [tuna-receipt-aware-collection-review.md](tuna-receipt-aware-collection-review.md) | Review of receipt collection and remaining authenticated adjudication boundaries |
| [tuna-private-readbacks-review.md](tuna-private-readbacks-review.md) | Review of private capture durability, replay and admission boundaries |
| [tuna-readback-expiry-review.md](tuna-readback-expiry-review.md) | Review of receipt retention across the post-response expiry boundary |
| [tuna-capture-commitment-review.md](tuna-capture-commitment-review.md) | Review of capture commitment encoding, substitution and admission boundaries |
| [tuna-capture-commitment-followup-review.md](tuna-capture-commitment-followup-review.md) | Follow-up on coherent capture substitutions and scoring separation |
| [tuna-attempt-transport-review.md](tuna-attempt-transport-review.md) | Review of attempt retention, failure paths and admission boundaries |
| [tuna-private-attempt-journal-review.md](tuna-private-attempt-journal-review.md) | Review of attempt journal replay, lifecycle and persistence boundaries |
| [tuna-attempt-retention-followup-review.md](tuna-attempt-retention-followup-review.md) | Follow-up on attempt transport and journal repairs |
| [tuna-subject-binding-review.md](tuna-subject-binding-review.md) | Review of subject, user, member and team binding boundaries |
| [tuna-subject-binding-followup-review.md](tuna-subject-binding-followup-review.md) | Follow-up on coherent identity transitions and subject encoding |
| [tuna-identity-continuity-review.md](tuna-identity-continuity-review.md) | Review of process-local identity comparison and refusal latch |
| [tuna-lock-decoder-repair-review.md](tuna-lock-decoder-repair-review.md) | Review of local lock timing and source-associated decoder repairs |
| [tuna-consumption-marker-review.md](tuna-consumption-marker-review.md) | Review of local approval-consumption identity, durability and descriptor ownership |
| [tuna-consumption-marker-followup-review.md](tuna-consumption-marker-followup-review.md) | Follow-up review of marker descriptor ownership and remaining adapter limits |
| [tuna-byte-snapshot-decoder-review.md](tuna-byte-snapshot-decoder-review.md) | Review of byte-preserving source and result validation |
| [tuna-byte-snapshot-followup-review.md](tuna-byte-snapshot-followup-review.md) | Follow-up review of byte parsing and destination metadata |
| [tuna-account-binding-review.md](tuna-account-binding-review.md) | Review of team namespace derivation and authorization boundaries |
| [tuna-account-binding-followup-review.md](tuna-account-binding-followup-review.md) | Follow-up review of member schema and team-namespace boundaries |
| [tuna-readback-transport-review.md](tuna-readback-transport-review.md) | Review of byte-preserving readback and source-result association |
| [seed-provenance-owned-draw-scan-profile.md](seed-provenance-owned-draw-scan-profile.md) | Profile of the repeated seed-ownership claim scan and timing-budget failure |
| [pr-147-ghost-error-scale.md](pr-147-ghost-error-scale.md) | PR #147, ghost-error-scale Kaggle shards and gates |
| [pr-148-substrate-routing-libraries.md](pr-148-substrate-routing-libraries.md) | PR #148, Kaggle substrate routing and library captures |
| [pr-149-jax-bridge-and-atlas-fringe.md](pr-149-jax-bridge-and-atlas-fringe.md) | PR #149 jax bridge sweep, and the atlas fringe amplitudes branch (PR #158) |
| [audit-kaggle-aer-runner.md](audit-kaggle-aer-runner.md) | tools/kaggle-aer-runner against main and the substrate-routing branch |
| [audit-dangling-docs-references.md](audit-dangling-docs-references.md) | dangling references under docs/ on main |
| [open-issue-triage.md](open-issue-triage.md) | open issues checked against the named files |
| [quantum-inspire-branch-pair-map.md](quantum-inspire-branch-pair-map.md) | the two Quantum Inspire branches and their merge order |
| [open-gororoba-anf-degree-issue-draft.md](open-gororoba-anf-degree-issue-draft.md) | draft upstream issue for open_gororoba (ANF degree closed forms); not filed |
| [docs-audit.md](docs-audit.md) | documentation inventory, bindings and restructure options |
| [tuna17-bdsc-pauli-pilot-review.md](tuna17-bdsc-pauli-pilot-review.md) | adversarial, stability and literature review of the Tuna-17 BDSC Pauli pilot (PR #349) |
| [quantum-recovery-proposal-audit.md](quantum-recovery-proposal-audit.md) | external nonlocal-transport and quantum-recovery proposal checked against cd_core, retained runs and its Zenodo dataset; two experiment candidates |
| [docs-move-plan.json](docs-move-plan.json) | per-file move plan with bindings and reference-edit counts, companion of docs-audit.md |
| [2026-10-25-das-mergus-algebra-review.md](2026-10-25-das-mergus-algebra-review.md) | adversarial claim review of the DAS MERGUS monograph, algebra and geometry chapters, with its [claim ledger](2026-10-25-das-mergus-algebra-claims.json) |
| [2026-10-25-das-mergus-data-review.md](2026-10-25-das-mergus-data-review.md) | adversarial claim review of the DAS MERGUS monograph, data and statistics chapters and the pasted Ascella claims, with its [claim ledger](2026-10-25-das-mergus-data-claims.json) |
| [das-mergus-checks/README.md](das-mergus-checks/README.md) | the independent probes and reruns both DAS MERGUS ledgers cite |
| [2026-10-25-results-catalog-opposition.md](2026-10-25-results-catalog-opposition.md) | opposition review of the results catalog and storage proposals, with ranked alternatives |
| [2026-10-26-a5-rank-strata-equations-review.md](2026-10-26-a5-rank-strata-equations-review.md) | adversarial opus review of the A_5 rank-strata equations record: no refutation, seven robustness and wording findings and their disposition |
| [2026-10-26-a5-strata-regularity-critical.md](2026-10-26-a5-strata-regularity-critical.md) | critical opus review of the A_5 strata-regularity record: no fatal finding, two serious gaps (irreducibility of X_+- and a `pass` flag that did not guard the germ table) and their disposition |
| [2026-10-26-a5-kernel-bundles-critical.md](2026-10-26-a5-kernel-bundles-critical.md) | critical opus review of the A_5 kernel-bundle record (roadmap item 5): no fatal finding; three serious evidence defects (a self-certifying classifier, hand-typed inputs labeled observed, a serial loop) and three sloppy citation and argument gaps, fixed in program round 2 |
| [2026-10-27-a5-kernel-bundles-nullity8-critical.md](2026-10-27-a5-kernel-bundles-nullity8-critical.md) | critical opus review of the A_5 nullity-8 kernel-bundle record: no fatal finding and every class confirmed; a missed W8 stabilizer component, ungated replays, a liftless canonicity argument and serial baseline loops, fixed in program round 2 |
| [primorial-coherence-case-2-review.md](primorial-coherence-case-2-review.md) | adversarial review of the second primorial coherence case against the run-economy rules; drove its 23-path, short-delay redesign |
| [primorial-coherence-case-2-codex-review.md](primorial-coherence-case-2-codex-review.md) | Codex (gpt-daybreak-blue-latest, high) review of the second primorial coherence case with each finding's disposition |
| [2026-10-26-belenos-teleportation-rehearsal-review-goal.md](2026-10-26-belenos-teleportation-rehearsal-review-goal.md) | standing brief of the Codex (gpt-daybreak-blue-latest, high) deep peer review of the Belenos teleportation rehearsal, job-00 evidence and the job-01 case of #560 |
| [2026-10-26-belenos-teleportation-rehearsal-review.md](2026-10-26-belenos-teleportation-rehearsal-review.md) | Codex (gpt-daybreak-blue-latest, high) deep peer review of the Belenos teleportation rehearsal and job-01: fourteen findings, the fixes in #560 and the questions left to the owner |
| [2026-10-26-belenos-job-01-redesign-consult.md](2026-10-26-belenos-job-01-redesign-consult.md) | Codex (gpt-daybreak-blue-latest, high, web search) research consult on the job-01 redesign, with its [brief](2026-10-26-belenos-job-01-redesign-consult-goal.md) |
| [2026-10-26-belenos-job-01-redesign-operator-research.md](2026-10-26-belenos-job-01-redesign-operator-research.md) | operator's parallel reading of the same questions, superseded in part |
| [2026-10-26-belenos-job-01-redesign-disposition.md](2026-10-26-belenos-job-01-redesign-disposition.md) | how the consult, the operator reading and the source notes became the descriptive job-01 design |
| [2026-10-27-ascella-replication-review-audit.md](2026-10-27-ascella-replication-review-audit.md) | audit of four critical peer reviews of the Ascella replication (PR #569) under the [critical-review runbook](../../runbooks/critical-peer-review.md): twenty-two findings and their disposition |
| [2026-10-27-ascella-replication-review-codex.md](2026-10-27-ascella-replication-review-codex.md) | Codex (gpt-daybreak-blue-latest, high) referee report on the replication, with its [brief](2026-10-27-ascella-replication-review-brief.md) |
| [2026-10-27-ascella-replication-review-grok.md](2026-10-27-ascella-replication-review-grok.md) | Grok (grok-4.7, high) referee report on the replication |
| [2026-10-27-ascella-replication-review-agy.md](2026-10-27-ascella-replication-review-agy.md) | agy (Gemini 3.8 Flash, high) referee report on the replication |
| [2026-10-27-ascella-replication-review-orchestrator.md](2026-10-27-ascella-replication-review-orchestrator.md) | orchestrator's referee report on the replication, corrected by the audit |

The [Tuna projector campaign review](tuna-projector-campaign-review.md) and its
[model provenance](tuna-projector-campaign-review.json) separate QX conformance, bounded hardware qualification and causal successors.

The [Tuna admission follow-up](tuna-projector-admission-review.md) verifies the compiler,
qualification analyzer, structural checks and digest-bound submission path.

The [ordered-response evidence-boundary review](tuna-ordered-response-evidence-boundary-review.md)
accepts the martingale derivation and serial dispatch design while requiring stricter
operational receipt and numeric validation before successor approval.
The [repair review](tuna-ordered-response-admission-review.md) accepts the exact
hash-bound descriptive case after those repairs; causal inference remains unadmitted.
The [model provenance](tuna-ordered-response-review-provenance.json) binds both reports.
The correct frozen policy receipt passes the exact case; explicit terms-schema
validation before future packet reuse remains a nonblocking follow-up in the work plan.

The [acquired destination-data review](tuna-destination-acquired-data-review.md)
independently verifies the three nominal-zero jobs, deadline stop, raw counts and
causal limits, and requests stronger automated recovery/source-receipt validation.
The [recovery-validation review](tuna-destination-recovery-validation-review.md)
identifies the remaining chronology edge; the
[focused correction review](tuna-destination-recovery-order-review.md) confirms
that correction and numerical invariance. The
[review provenance](tuna-destination-acquired-review-provenance.json) binds all three reports.

The [nominal-one deadline review](tuna-destination-one-deadline-review.md) accepts the separate
three-job statistical contract and holds execution because later resource writes omit the
admission deadline. Its [provenance](tuna-destination-one-deadline-review.json) binds the reviewed packet.
The [locked-admission consumer review](tuna-destination-one-locked-admission-review.md) confirms
the timing repair and requires the under-lock receipt in completion and analysis;
its [provenance](tuna-destination-one-locked-admission-review.json) identifies the second packet.
The [final nominal-one admission review](tuna-destination-one-admission-review.md) closes both
findings and passes the exact three-job case; its
[provenance](tuna-destination-one-admission-review.json) binds the final packet and requested model.
The [acquired-data review](tuna-destination-one-acquired-review.md) passes the primary result and
encoding reconciliation while identifying an ancillary API-provenance gap; its
[provenance](tuna-destination-one-acquired-review.json) records the requested model.
The [lossless projection replay](../../evidence/tuna-projector-geometry/destination-final-result-projection-replay.md)
adds retained response metadata and checked reconstruction against the original API hashes.
The [projection closure review](tuna-destination-final-result-projection-review.md) independently
reconstructs all six responses and closes the provenance finding within the API-capture trust boundary;
its [provenance](tuna-destination-final-result-projection-review.json) records the requested model and effort.
The [joint-response review](tuna-joint-response-analysis-review.md) independently reconstructs the
six acquired distributions and identifies a regression-coverage finding; its
[provenance](tuna-joint-response-analysis-review.json) binds the reviewed candidate and model.
The [coverage review](tuna-joint-response-coverage-review.md) closes that finding after the
independent parity, uncertainty and exact-byte checks; its
[provenance](tuna-joint-response-coverage-review.json) records the reviewed inputs and test limit.

The [Tuna joint-algebra package review](tuna-joint-algebra-package-review.md) and its
[model provenance](tuna-joint-algebra-package-review.json) verify retained-data arithmetic,
package bindings, descriptive distances and their physical interpretation limits.

The [Quantum Inspire metadata-route issue draft](quantum-inspire-metadata-route-issue-draft.md)
separates the public SDK/deployment question from the unsent private acquisition-trace request.

The [Tuna randomized-block feasibility review](tuna-randomized-block-feasibility-review.md)
records early builder feedback, disposition and the separate final-review requirement.

The [Tuna early-label map review](tuna-early-label-map-review.md), its
[coverage follow-up](tuna-early-label-map-followup-review.md) and
[model provenance](tuna-early-label-map-review.json) bind the exhaustive-map check.
