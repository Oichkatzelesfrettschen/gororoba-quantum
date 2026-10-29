# Tuna ordered readout-response admission

The [destination-invariance draft](tuna-readout-destination-invariance.md) identified a
cheap intervention: cycle three classical destinations while preserving the physical
instruction stream. Its two three-job batches left execution order uncontrolled and
its IID illustration left dependence unqualified. The successor uses six serial
single-job batches and a finite-sample bound for the acquired response sequence.
The earlier draft, qualification refusal and raw observations retain their bytes.

## Question and claim boundary

The primary question is whether inverse-decoded early/final response cells differ by
more than 0.10 between the rotated job and its two baseline jobs, while the two
baselines agree within 0.10. The target is the average conditional response along
the acquired history. The target differs from a stationary device parameter, a
repeated-run mean, a prepared-state population and a causal destination effect.

The [uncertainty derivation](../evidence/tuna-projector-geometry/destination-response-uncertainty.md)
defines the filtration, deterministic weights, simultaneous error control and
separation guarantees. Arbitrary shot dependence is allowed. A coincident transient
at the rotated job remains confounded with destination naming. Passing the baseline
screen establishes its stated endpoint comparison; it cannot bound an unobserved
intermediate excursion. Every terminal report keeps causal attribution unresolved.

## Fixed acquisition and ordering

The zero-preparation control executes baseline-before, rotated destinations,
baseline-after. The one-preparation control executes the same sequence afterward.
Each of the six jobs has its own batch and requests 4096 shots, for 24,576 total.
Each baseline pair has identical source bytes. The rotated source changes only the
early destinations for physical qubits 4, 11 and 6 from 17, 18 and 19 to 19, 17 and 18.
The decoder restores physical-qubit order. All terminal destinations stay unchanged.

The operator collects a completed job and preserves its raw results before preparing
the next dispatch. The account-wide pause and queue checks precede every dispatch.
The guarded path checks the exact single-job manifest digest. The next job's
provider creation timestamp must follow the previous job's completion and required
pause. The API's `queued_at` field is retained under its own name, rather than
treated as a documented pulse-start timestamp. Serial
dispatch prevents within-batch reordering; the future timestamps still require
verification. Local compiler equality establishes the source-level intervention;
served pulse and acquisition schedule equality remains unavailable.
Chronology relies on the provider-reported timestamps sharing a coherent clock
and the documented creation/completion meanings. The check measures those records;
it does not independently measure an analog settling interval.

The workload estimate is 29.533215 seconds from the measured original controls,
excluding queue and mandatory pauses. The provider ceiling is 300 seconds per job,
1800 seconds total. Expected and allowed credits are zero. The pause ladder starts
at 30 seconds and has 60, 90 and 120 second levels for separately admitted recovery.
A failure stops this case; a higher pause level grants neither a retry nor another
acquisition. The six-job case includes at least five intervening pauses, so its
elapsed duration exceeds the execution estimate even with an empty service queue.
Zero cost is supported by the reviewed free-use terms and checked against the
account ledger. The API exposes no spending-cap parameter for this case. A delayed
or unexpected charge can stop subsequent dispatch but cannot undo a submitted job.
The case fixes the pause at 30 seconds, the heartbeat freshness limit at 120 seconds
and the deadline for initiating campaign requests at 3600 seconds. Those are operator
admission policies. A deadline stops further dispatch; an already dispatched job retains its
identity and requires collection or explicit job-specific cancellation authority.
The automatic collector also stops initiating requests at that deadline. The
operator then uses read-only reconciliation and collection for the preserved job
identity; the campaign executor refuses automatic resume or replacement jobs.
An in-flight request can finish after the deadline; the guard does not promise a
hard wall-clock termination of network calls or provider execution.
The oldest read in each admission observation has a 60-second freshness limit;
the submission deadline carries that limit through waiting for the account lock.

## Decision discipline

The frozen analyzer evaluates 24 joint cells: two preparations, three ancillas and
four early/final binary outcomes. It uses a simultaneous 99% bound for those 24
rotated-minus-baseline contrasts and 24 baseline-after-minus-before contrasts.
The response margin and baseline tolerance are both 0.10, fixed before acquisition.

The baseline intervals must all lie within the tolerance before the response
comparison can establish its descriptive endpoint. All response intervals inside
the margin establish bounded response equivalence; any interval wholly outside
the margin supports response departure. Remaining valid complete records are
inconclusive within budget. The mathematical note specifies boundary conventions.
Neither endpoint certifies universal register invariance or a physical mechanism.
The 24 selected cells cover each ancilla's early/final pair separately. They do
not certify the full joint distribution across all three ancillas and data qubits.

Absent required acquisition artifacts make the implementation route unavailable.
Missing required fields in a returned artifact, changed manifests, invalid identities, malformed or partial raw shots,
failed jobs, overlapping or reversed execution, structural drift and charges make
the protocol inadmissible. Preserve every dispatched identity and failure. An
ambiguous submission is reconciled by its recorded identity before any action.
Automatic retries and favorable postselection are prohibited. Statistical decisions
use the full six-job case; intermediate outcomes do not select continuation.

## Discriminating successors

An upstream reconstruction replay using stored acquisition indices and raw IQ can
test the classical association without another quantum execution. A destination
permutation is a useful metamorphic test: physical instructions stay fixed while
the expected classical output permutes exactly. The same test can run separately
against the local compiler and each simulator's documented output contract.

If the ordered response case finds departure, independently randomized or
counterbalanced treatment blocks can separate systematic naming dependence from
some temporal confounding. The experimental unit is the assigned job or block;
increasing shots within one job does not add treatment assignments. Randomization
requires a new QRNG-backed schedule and a separately qualified acquisition case.
Randomization alone cannot eliminate treatment carryover through apparatus memory.

If the response case finds equivalence, a common reconstruction defect and physical
readout-context effects remain possible. Isolating qubit 11, fixing spectator states,
and crossing first-only, late-only and repeated readout at verified timing separates
different alternatives. Vary readout multiplexing separately from spectator
excitation. Matching omitted pulses requires the provider's served operation
duration, rather than assuming the public 300 ns notice specifies integration time.

A terminal-only emulator control tests shared circuit mathematics and terminal
decoding. Testing early history requires a backend that documents that history in
its output. Copying the early result into a spare qubit is a distinct physical
experiment with additional gates and cannot silently replace the failed protocol.

## Approval boundary

The exact manifests, compiler receipt, analyzer digest, acquisition-decision record,
focused verification and fresh admission observation form the approval packet.
The [sequential campaign](../../results/quantum_inspire/proposals/tuna-readout-destination-sequential/campaign.json)
binds all six manifests, the analyzer, mathematical note, execution guard and compiler
receipt. The [decision record](../evidence/tuna-projector-geometry/readout-ordered-response-decision.json)
binds the campaign and this written case. The
[upstream report](../notes/quantum_inspire/upstream-readout-report.md) owns contact
routes, unsent reproduction drafts and the preliminary readiness observations.
Approval covers those identities, six jobs, 24,576 shots, the zero-credit ceiling
and the stated descriptive objective. Structural and account checks run again at
dispatch because an admission observation expires as provider state changes.
The prior hardware approval covers the completed qualification only.
