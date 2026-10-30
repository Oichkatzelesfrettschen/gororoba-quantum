# Reduced QX destination conformance case

This case is **unapproved and unadmitted**. It proposes a reduced QX conformance run
for the [Tuna sequential destination case](tuna-destination-sequential-evidence-case.md).
QX cannot run the 17-qubit Tuna sources: its observed limit is ten qubits. QX also
returns its per-qubit last-measurement register rather than the cQASM classical-bit
history. Consequently the reduced case checks QX parsing, provider submission and
terminal-result plumbing only. It cannot validate Tuna's early labels, served schedule,
physical measurements, discrimination or acquisition-to-bit reconstruction.

The repository describes a QX dry run as validating a hardware case end to end. The
three-qubit reduction cannot meet that statement for the 17-qubit source and its early
classical history. Whether the reduced run plus independent local checks is an
acceptable explicitly approved procedure remains a decision for the case owner;
this draft does not silently treat the reduced run as full QX conformance.

## Exact sources and expected results

The three sources use `qubit[3]`, `bit[6]`, a first readout into auxiliary bits and a
terminal readout into bits 0–2. The logical qubits 0, 1, 2 correspond respectively
to the three measured roles q4, q11, q6 in the Tuna source; the reduced circuits are
not the same physical workload. The two zero-preparation sources preserve the baseline
and rotated destination patterns. The third inserts `X q[0]` as an asymmetric terminal
ordering control.

| Source | SHA-256 | Expected QX width-3 output on every shot |
|---|---|---|
| [Baseline](../../results/quantum_inspire/proposals/tuna-destination-qx-conformance/baseline.cq) | `004667f94872f372eab01eb75dfbc6e5fb25e0b16534d3c20da6b1c7f5dc91af` | `000` |
| [Rotated](../../results/quantum_inspire/proposals/tuna-destination-qx-conformance/rotated.cq) | `39454ac0e32f0bebfd687d5def41666ee7e35b3af5d61430c2f0b084d355e584` | `000` |
| [Asymmetric control](../../results/quantum_inspire/proposals/tuna-destination-qx-conformance/asymmetric.cq) | `dc9de0253a6d544bf76ba215a3fca2cf253dda549364f899064f927c1d7f0ecd` | `001` |

The deterministic prediction follows from `init`, the sole `X q[0]` in the third
source, and QX's documented last-measurement-per-qubit result with q0 rightmost.
The [local parse observation](../../results/quantum_inspire/proposals/tuna-destination-qx-conformance/local-parse-observation.json)
records zero cQASM parser errors for all three, equality of the first two physical
instruction streams, and the single added `X q[0]` in the third. Local parsing is
not a simulator execution or a server submission. A separate [local QX observation](../../results/quantum_inspire/proposals/tuna-destination-qx-conformance/local-qx-output-observation.json)
records one simulator shot per source with the three expected strings; it is a local
output-shape check, not a statistical or hardware result. The result contract and its
limits are documented in [QX runs](../notes/quantum_inspire/qx-runs.md).
The separate [local replay](../../results/quantum_inspire/proposals/tuna-destination-qx-conformance/local-replay.json)
records its [producer](../../scripts/qi_tuna_qx_local_replay.py), command, interpreter,
package versions, source hashes and timestamps. The replay reproduces the parser and
one-shot checks; it does not authenticate the earlier observations or establish provider behavior.

The [source-bound proposal manifest](../../results/quantum_inspire/proposals/tuna-destination-qx-conformance/cases.json)
is generated and checked by [the offline QX case producer](../../scripts/qi_tuna_qx_destination.py).
The manifest carries no provider execution authority.

The manifest's `provider_execution_authorized=false` field is descriptive: the generic
`qi_platform.py submit` does not enforce that field or prove that free-form approval
text names this case. A separate reviewed guard must bind explicit user approval,
manifest digest, admission, limits and consumed state before any submission.

After an authorized batch is collected, the same offline producer can validate its
source-bound collection with `--collection RUN --analysis-out FILE`. The analyzer
checks receipts, job identities, exact shot lists, histograms, execution time and
transaction rows before evaluating the deterministic terminal outputs. A failed output
is retained as a failed analysis and returns nonzero. The analyzer verifies receipt
consistency; it does not establish that a user approved the run, that admission was
fresh, or that Tuna early history was correctly reconstructed. The report distinguishes
`terminal_screen_passed` from `provider_conformance_admitted`, which remains false until
a separate approval, admission and provenance decision is implemented and reviewed.

Before collection analysis, `--capture-readback RUN --readback-out FILE` is intended
to read the provider batch, jobs and their stored files through the QI API and bind
backend type, job-to-file IDs and stored source hashes. The capture validates the local
manifest before constructing the API client. The client may refresh and atomically
rewrite its local OAuth token store; the API operations are read-only. The retained
readback is a local observation, not a cryptographically authenticated provider receipt.
An empty collection transaction list is likewise a time-bounded observation; account-wide
ledger reconciliation and the possibility of later charges remain separate requirements.
No live readback for this unsubmitted case has been made.

The capture reserves its output exclusively before loading credentials and records an
incomplete marker before requesting data. A failed capture leaves that marker; an
interruption during final publication can leave a partial or empty file, which the
analyzer refuses. Preserve the incomplete artifact and use a new output path for
read-only recovery. The capture also hashes each full provider
result object including its ordered raw shots; the analyzer reconstructs that object
from retained metadata and shots before accepting the screen.

Provider `created_on`, `queued_at` and `finished_at` are checked against one another
and compared with their readback values. Local submission, collection and readback
capture timestamps form a separate ordered sequence. The analyzer does not compare
provider completion time to local collection time as though the two clocks were
synchronized or the local timestamp had subsecond precision. A readback timestamp
is not fresh admission evidence.

## Proposed provider envelope and screen

Use QX backend type 1 with **three jobs of 2048 shots**, at most one batch containing
three circuits, and **6144 shots** total. The historical QX limit is 2048 shots and
3600 execution seconds per job; the resulting ceilings are **3600 s per job** and
**10,800 s total**. Queue and service overhead are excluded, and the case makes no
execution-time forecast. Expected and allowed
credits are **zero**, subject to fresh account, pricing and terms checks. No API
spending cap is asserted; an unexpected observed charge stops subsequent work.

Each completed job must retain 2048 ordered width-3 binary strings, a matching histogram
and job, source and batch identities. The screen passes only when every shot for each
source equals its listed deterministic output. A wrong width or output fails the QX
conformance screen; missing, partial, malformed, charged or misbound results make the
case inadmissible. Retain dispatched job identities and raw results before analysis.
Do not retry, replace, upload, or enqueue again under the same approval after ambiguity
or failure; reconcile an ambiguous submission read-only.

The exact case still needs a generated source-bound manifest, a frozen conformance
analyzer, local parser replay, negative and mutation tests, independent review, fresh
read-only backend/queue/policy admission and **explicit user approval of this QX case**.
The old QX geometry result does not authorize this batch. A passing QX result does not
itself approve the separate Tuna case. No remote simulator job or upload has occurred
for these sources.
