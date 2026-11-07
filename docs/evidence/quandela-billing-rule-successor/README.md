# Quandela iterated-job billing rule: successor for pinned records

`qd_platform.job_billing` and `qd_platform.charged` bill an iterated Quandela job 1 credit plus 1e-6 per shot of
the smaller of the shots it used and its largest iteration's `max_shots`. An iterated job whose result reports no
shots-used figure bills the cap in full. The [credit optimization runbook](../../runbooks/quandela-credit-optimization.md),
"The billing rule", carries the measured charges behind the rule: run
`2026-10-30T190300Z-qpu_ascella-a5-kernel-slice` used 60,000 shots under a 100,000 cap and was charged 1.06 credits.

The records below state the charge as the largest iteration's `max_shots` in full. Each is pinned, either by its
sha256 in a run manifest or record, or by its producer's `--check`, which compares the record byte for byte against
a fresh build, so each keeps its bytes. This record supersedes only the named field. In each, the cap figure is the
job's credit ceiling, and the charge equals that ceiling only where the job used at least its cap; every other
field keeps its meaning. A reader that cites one of these fields as the billing rule reads the rule above.

| Record | sha256 | Field | Pinned by |
|---|---|---|---|
| `docs/evidence/bdsc/qualification_case.json` | `5d308a9b17b86007a1a371f1b4e47089451a5802a4820ba19a28782ecf0c5681` | `/resources/billing_rule` | `results/quandela/cases/bdsc_qualification/*/cases.json`, `docs/evidence/bdsc/forensics/forensics.json` |
| `docs/evidence/bdsc-principal-angle-svd/qualification_case.json` | same bytes as above | `/resources/billing_rule` | same digest |
| `docs/evidence/bdsc/planning.json` | `867bb625a84b5339c7ba638c8fd57d10e9eff902c8c51fc6e929a8fa34195bbd` | `/resources_historical/rates/credits` | output of `scripts/bdsc_certificate.py`, itself digest-pinned |
| `docs/evidence/bdsc-principal-angle-svd/planning.json` | same bytes as above | `/resources_historical/rates/credits` | same producer |
| `docs/evidence/bdsc/diagnostic/case.json` | `9f5a2cea55c250e370388e91ca4ff4c32a280b3f4b44915eb8928ceb36be158c` | `/resources/billing_rule` | `results/quandela/cases/bdsc_diagnostic/*/cases.json`, `scripts/bdsc_diagnostic.py --check` |
| `docs/evidence/bdsc/stationarity/case.json` | `5c159593897259ab768d9590d6e68de479047adabe94e92302bfecd15cc5cc4b` | `/resources/billing_rule` | `results/quandela/cases/bdsc_stationarity/*/cases.json`, `scripts/bdsc_stationarity.py --check` |
| `results/quandela/cases/ascella_predecessor/job-00/cases.json` | `9778e3a35512bcbf80b79d2c36d2530d13057b313926333921a61bb9c940a2b9` | `/preregistered/credit_basis` | `docs/evidence/ascella-predecessor-admission/running-plan.json` and two acquisition-review records |
| `results/quandela/cases/ascella_predecessor/reviewed-submission/cases.json` | `0e58c0b22c4f8650ae893c5a7dcae5daeb1e25e87012c1aa3be8318085c17c13` | `/preregistered/credit_basis` | `docs/evidence/ascella-predecessor-admission/reviewed-submission-*.json`, `docs/state/plans/ascella-predecessor-intervention.json` |
| `results/quandela/cases/ascella_predecessor/source-compatible/cases.json` | `dd7757e087f5dff36efb78bc903ae7c5d1c6b5c24ea88537ee3b4e92e5357fce` | `/preregistered/credit_basis` | `docs/design/ascella-predecessor-intervention.md`, `docs/state/plans/ascella-predecessor-intervention.json` |
| `results/quandela/runs/2026-10-30T010726Z-sim_ascella-ascella_predecessor-source-compatible/cases.json` | `3a8c4a11f1390cdc35c426566657ef2f2a498a7083cd983234077dea6fcaad9e` | `/preregistered/credit_basis` | `docs/evidence/ascella-predecessor-admission/simulator-qualification.json`, the run's `submission.json` |
| `results/quandela/runs/2026-10-30T165953Z-qpu_ascella-ascella_predecessor-current-schema/cases.json` | `f7dca476ad6ffe4232d69c8ffd2d64488f2faaa528d711b70c47829ed31bcc49` | `/preregistered/credit_basis` | `docs/evidence/ascella-predecessor-admission/current-source-qpu.json`, the run's `submission.json` |

The producers emit the same wording and keep it, because a changed string changes every record above:
`scripts/bdsc_certificate.py` (sha256 `5dbcd027eb24a303ba5757e00b0123e846bc3c86dab70a24dc1ae1f98b197753`, the
`billing_rule` and `credits` strings and the job-model comments), `scripts/ascella_predecessor_case.py` (sha256
`2310aa98d1c0c68812d7edcbd30fd6a0713ca5fb6ab1e1b8c3c96e3d845b197b`, `charge` and `credit_basis`), and the
`billing_rule` strings of `scripts/bdsc_diagnostic.py` and `scripts/bdsc_stationarity.py`.

A new record of either family comes from a versioned successor, which rebuilds the original's records in memory and
replaces only the fields in the table above with the rule text in
[`scripts/billing_rule_v2.py`](../../../scripts/billing_rule_v2.py); each refuses a build whose original no longer
emits the superseded wording. [`scripts/bdsc_certificate_v2.py`](../../../scripts/bdsc_certificate_v2.py) succeeds
`bdsc_certificate.py`; [`scripts/bdsc_case_records_v2.py`](../../../scripts/bdsc_case_records_v2.py) succeeds the
diagnostic and stationarity builders and re-binds each job manifest's `diagnostic_case_sha256` or
`stationarity_case_sha256` to the successor case record; and
[`scripts/ascella_predecessor_case_v2.py`](../../../scripts/ascella_predecessor_case_v2.py) succeeds
`ascella_predecessor_case.py`, adds its own digest to `analysis_sources` and names the original's `charge` figure
`credit_ceiling`. Every credit number keeps its value as the ceiling at the frozen `max_shots`. No successor record
is retained; [`tests/scripts/test_billing_rule_v2.py`](../../../tests/scripts/test_billing_rule_v2.py) holds each
successor's difference from its original to exactly those JSON pointers.

Three pinned documents carry the same rule in prose and have full successors:
[`hypercomplex-operator-cases-v2.md`](../../runbooks/hypercomplex-operator-cases-v2.md),
[`provider-counter-audit/README-v2.md`](../provider-counter-audit/README-v2.md) and
[`ascella-cancellation-transition-acquisition/README-v2.md`](../ascella-cancellation-transition-acquisition/README-v2.md).

## Census boundary

A `git grep` of every tracked file for a billing, charge, credit, cost, tariff or price term within 120 characters
of `max_shots`, a shot cap, a shot limit or the largest iteration finds 169 lines. Outside the records above, the
three successors and the unpinned documents and comments corrected in place, each hit falls in one of these
classes, and none states the wrong rule as current guidance:

- Ceilings. A credit ceiling of 1 + 1e-6 x `max_shots` is the most the rule can bill and stays correct: the
  `credit ceiling under matching preflight tariff` statement in 23 associator and two-photon case and run
  manifests, the plan ceilings, the runbook and the `qd_platform` comments.
- Content-addressed snapshots and history. The 21 files under `docs/evidence/plan-reconciliation/sources/` are
  named by the sha256 of their bytes, and the 6 under `docs/archive/` are review and handoff transcripts.
- Measured or preregistered single records. A `docs/notes/quandela/strategy.md` job row reports what one job was
  billed, a strategy paragraph prices both billing hypotheses, the `belenos_mesh` dwell preregistration names
  both outcomes, and the `bdsc_qualification` submissions quote an approved estimate.
- Readers of the original runbook that are themselves pinned or are run records:
  `docs/design/tuna-order-pilot-adversarial-admission.md`, `docs/evidence/hypercomplex-operators/README.md`,
  `results/quandela/runs/ascella-mosaiq-update-order-retry/README.md`, the closed-plan receipts under
  `docs/state/plans/` and the claim evidence lists in `docs/state/research_state.json`.
