# Folded-QPE calibration admission refusal

The owner authorizes the record in `../2026-10-12T054229.702537Z/` and explicitly
permits hardware execution after the account rejects native mock-service access.
The guarded submission command exits 1 before creating a submission ledger,
consuming approval, or accepting a Runtime job.

The live properties update changes calibration from
`2026-10-11T22:25:34-07:00` to `2026-10-11T22:36:25-07:00`. The planner replaces
physical qubit 91 with 73 and changes the shared layout, family configuration,
PUB manifests, and QPY bytes. `record.json` retains all nine mismatch messages
and state `approval_required`. Both admitted plans predict 39.632399872 seconds
nominal and 45.543119872 seconds under the declared stress scenario.

Before submission re-preparation, an independent capture retains the original
planner-produced `planned` record and QPY. The capture records equal bytes on
both sides of the read. After the refusal, its QPY equals the final refreshed
archive and the hash recorded in `renewed_approval`. The original refusal record
remains unchanged. The separate `../2026-10-12T055017.711575Z-prepared/` case
passes the case writer and the 21-source dependency audit; owner approval of
that new record is separate from the earlier approval.

The runner discovers stale approval after candidate simulation, selected-plan
simulation, and a second candidate simulation. Early immutable-record and
calibration comparison can reject stale records before expensive preparation.
A persistent preparation-and-approval flow can reuse same-process predictions
only when all selection inputs, live properties, source/dependency identities,
options, and QPY remain identical. Both repairs preserve the final per-job
refresh, quota reservation, and single-use approval marker.

The refusal supplies evidence of functioning admission guards and inefficient
local rejection ordering. The refusal supplies zero hardware measurements.
