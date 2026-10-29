# Tuna nominal-one destination-response admission

Three additional approved Tuna-17 jobs complete a nominal-one baseline/rotation/baseline comparison
as a separate acquisition case. The [deadline-limited acquisition](../evidence/tuna-projector-geometry/ordered-response-acquisition.md)
retains three nominal-zero jobs and its unavailable six-job primary endpoint. The new case measures
the nominal-one response under an independently frozen 12-cell decision. Combining the cases later
provides retrospective diagnostics with a several-hour separation, rather than the original
prospective six-job endpoint.

## Question and fixed intervention

The case asks whether inverse-decoded early/final binary response cells differ by more than 0.10
between a destination-rotated job and its bracketing baseline jobs, with baseline endpoint agreement
within 0.10. The [uncertainty contract](../evidence/tuna-projector-geometry/destination-one-response-uncertainty.md)
defines the realized predictable target, arbitrary adapted dependence, simultaneous 99% error bound,
separation guarantees and causal limits. A simulator cannot determine the physical acquisition
response or the served Tuna reconstruction chain.

Each job nominally prepares all 17 qubits in one, measures physical q4,q11,q6 early, then measures
all 17 qubits terminally. Each circuit has 20 classical destinations and zero explicit settling gap.
The three batches execute baseline-before, rotated-destinations, baseline-after. Each batch contains
one 4096-shot job; the total is 12,288 shots. The baseline sources are byte-identical. The rotation
changes only early destinations 17,18,19 to 19,17,18. Terminal destinations 0 through 16 remain fixed.
The decoder restores physical-qubit order. The [campaign](../../results/quantum_inspire/proposals/tuna-readout-destination-one/campaign.json)
binds the unchanged nominal-one manifests from the earlier proposal, local compiler replay, successor
runner and analyzer, and every imported approval or submission helper.

Local physical-instruction equality establishes the source-level intervention. Served analog
schedule equality remains an upstream evidence obligation. The labels are binary responses;
an independently calibrated excited-state interpretation remains unavailable.

## Measured waits and bounded operational allowance

The three retained nominal-zero jobs had created_on-to-queued_at intervals of 1025.678760,
987.075253 and 1677.501464 seconds. Those timestamps measure the provider's named records;
queued_at remains distinct from a verified pulse-execution start. Their reported execution times
were 5.176820,4.710931,4.469031 seconds. The old 3600-second request horizon expired before the
third collection and left the nominal-one controls unsubmitted.

The prior global queue snapshot reported a 1680-second maximum wait. The
[fresh read-only observation](../evidence/tuna-projector-geometry/destination-one-queue-observation.json)
at 22:51:54 UTC on 2026-10-27 reported 26 queued entries, 310 seconds average and 598 seconds maximum,
with Tuna enabled, executing and a recent heartbeat. The case conservatively budgets the larger
observed 1680-second queue interval for each of three jobs: 5040 seconds, plus the 900-second
aggregate provider execution ceiling and two 30-second mandatory pauses, totaling 6000 seconds.
A 7200-second request-initiation horizon leaves 1200 seconds for admission, preparation and
collection overhead. The horizon is an operator allowance derived from measured waits, rather
than a guarantee of future queue service or a hard wall-clock execution bound.

The expected reported execution time is 14.688660 seconds, three times the retained original
nominal-one control's 4.896220 seconds. Each job has a 300-second provider execution ceiling;
the aggregate ceiling is 900 seconds. Expected and allowed credits equal zero. Reviewed free-use
terms support that expectation, and account ledger reads check charges before each successor.
The API provides no spending-cap parameter. A delayed charge can stop remaining dispatches;
an already submitted job retains its identity.

## Dispatch and stopping rules

The runner collects and validates each sole completed job before initiating its successor.
The successor's provider creation timestamp must follow the preceding recorded completion by
at least 30 seconds. Timestamp checks assume coherent provider and local record clocks and documented field
meanings; they measure the returned chronology, rather than analog settling independently.

Every dispatch freshly verifies unchanged public policy text, enabled backend, structural
configuration, a heartbeat at most 120 seconds old, the account hardware queue and the account-wide
30-second pause. The oldest admission read must precede provider job creation by at most
60 seconds, including the account-lock wait. The
[successor submission helper](../../scripts/qi_platform_submission_deadline.py) carries that deadline
through backend and queue reads, resource creation, file upload, job creation and batch enqueue.
The guarded submission binds the exact single-job manifest digest. The FAQ permits at most three queued hardware jobs; the runner admits one sole
account hardware job at a time and collects it before the next batch.

The 7200-second horizon bounds initiation of campaign requests and automatic collection requests.
A request already in flight may return later. A dispatched job that outlives the horizon keeps
its identity and receives read-only reconciliation and collection. The executor refuses an existing
run root; automatic resume, replacement jobs, retries and statistical early stopping are prohibited.
The operational guard stops on ambiguity, failed/partial acquisitions, charge or structural drift.
Cancellation requires separate job-specific authority. Raising the 30-second pause to a ladder
level of 60,90,120 seconds requires a successor case; the ladder grants no retry authority.
Authentication handling keeps the shared SDK's token-rotation lock. OAuth refresh calls can start
or finish after the deadline, including after a rejected in-flight compute request. Each subsequent
compute API request checks the deadline immediately before transport and remains refused after
expiry. Token refresh and a remote request already in flight remain outside a hard wall-clock
termination guarantee.

## Primary outcomes and approval

The frozen analyzer evaluates 12 early/final cells across q4,q11,q6 and 12 endpoint contrasts.
All baseline intervals must lie inside [-0.10,0.10]. Then all response intervals inside establish
objective established within scope; any response interval strictly outside supports the specified
alternative. Endpoint uncertainty or response overlap gives inconclusive within budget. Absent
required artifacts give implementation route unavailable. Changed bindings, failed or partial jobs,
malformed shots, invalid identities, charges, structural drift or ordering violations give protocol
inadmissible. Every outcome leaves causal attribution unresolved and requires a new written case
and approval before further hardware.

The [decision record](../evidence/tuna-projector-geometry/destination-one-decision.json) binds this
written case, the campaign, ceilings and all five outcomes. The owner authorized three further
jobs in the instruction recorded by the [approval receipt](../evidence/tuna-projector-geometry/destination-one-owner-approval.json).
Fresh admission remains mandatory at each dispatch. After collection, the read-only investigation
will inspect per-job acquisition mapping, thresholds, served schedules and retained IQ. The
[upstream report](../notes/quantum_inspire/upstream-readout-report.md) owns verified contact routes
and unsent requests. Sending a support message requires separate authorization.
