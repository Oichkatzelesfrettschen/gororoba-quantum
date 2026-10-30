# IBM full-register descriptive acquisition review

Status: reviewed with a budget admission hold; owner approval remains pending.
The [packet](packet.json) binds the exact case, source closure, sparse analyzer
identities, independent inspection findings and fresh read-only admission.
The review covers one 24-PUB attempt retaining 73,728 full 156-bit shots,
with reporters 0 and 1, actor 2, and 30/50/250-microsecond repetition delays.
The measured error tables and paired-score variances inform a separately
approved confirmation case. Delay and acquisition period remain associated.

## Findings and accounting

An independent read-only agent inspects source head `a7b58d9`, verifies all
three written record/QPY/case digests, and executes the offline actor-case
validator successfully. The inspection covers the relevant planning,
submission, approval, collection and adjudication interfaces; it supplies
neither a hosted review nor physical timing evidence.

The [prepared case](../../../results/live/2026-10-29T002839.028671Z/UNAPPROVED_CASE.md)
requests three six-second job ceilings, totaling 18 seconds. Its configured
aggregate ceiling is 20 seconds and its retained reserve is 48 seconds.
The modeled 10.995612672 seconds remains an estimate.

**Serious operational risk:** `readout_actor_family.py:603-615` requires
remaining quota of at least 66 seconds before every job, even after earlier
charges appear. Starting at 68 seconds leaves two seconds before a later
check refuses. The modeled first job alone costs 3.128005632 seconds. An
attempt can therefore submit one job, consume its approval and stop before
collecting every delay. The check conservatively protects the reserve;
it does not establish complete-program feasibility at 66 or 68 seconds.
A 78-second start covers two earlier six-second ceilings against those repeated
checks, conditional on provider accounting and other activity. A changed
calibration or other admission failure can still cause partial acquisition.
Production budget reconciliation remains unchanged by this review.

**Documentation correction:** the planning function performs zero quota reads.
The design now separates backend/compilation checks from the independently
retained [usage observation](admission.json). The observation at
2026-10-29 00:47:21 UTC reports 68 seconds on the default primary instance.
The review withholds an approval request under the conservative 78-second
start rule. Quotas from distinct instances remain separate.

The [fresh submit-free case](../../../results/live/2026-10-29T004725.208468Z/UNAPPROVED_CASE.md)
passes comparison with the reviewed record: all approved-record mismatch
checks return an empty list. Kingston reports active with 66 pending jobs,
below the case's queue ceiling of 100. All 24 compiled measurement starts
remain tick 8. The refresh submits zero jobs. Backend scheduling, physical
shot alignment, initialization and carryover remain separate unknowns.

## Digest custody and one-attempt boundary

The committed packet sits outside every analyzed run directory. A write-once
copy of its digest and reviewed/fresh record anchors also resides under
`~/.local/state/gororoba-quantum/acquisition-approvals/`, with owner-only file
permissions. The custody entry identifies its origin as the review process
and records authorization as pending. Local creation establishes an independent
storage boundary, rather than owner approval or physical provenance.

After an admitted, explicitly approved attempt, the operator records the final
submitted record digest and provider job identities in a new custody entry
before passing that expected digest to `--collect --actor-record-sha256`.
A recovery that changes the submission record requires a new reviewed custody
entry; the operator retains the original anchor. The operator records the
collection receipt digest in another external entry before passing it to
`adjudicate.py --actor-collection-sha256`. Expected digests come from those
custody entries, rather than being recomputed from the files under analysis.
The resulting acquisition-index, raw PUB, QPY, preparation and projection chain
supports recorded-byte consistency under that custody boundary.

One approval covers one attempted program. The generated binding command uses
`approved_run.sh`; the approval review additionally limits that wrapper to
`--attempts 1`. A consumed approval or partial/uncertain submission ends the
attempt. The operator retains completed jobs and missing allocation identities
and requests a separately reviewed case for any later acquisition.

The case remains descriptive. The analyzer's hardware verdict stays null.
The packet grants zero parity-superiority, equivalence, causal activity,
initialization, carryover or chip-wide protection decisions. IQM's separate
provider-enforced credit gate remains intact.
