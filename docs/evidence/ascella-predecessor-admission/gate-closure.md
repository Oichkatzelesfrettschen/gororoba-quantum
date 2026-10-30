# Ascella reviewed-submission gate closure

The [exact approval packet](reviewed-submission-approval.json) binds the unchanged
scientific eight-iteration target-slot diagnostic to a revised execution route.
The source-compatible request lives under
[reviewed-submission](../../../results/quandela/cases/ascella_predecessor/reviewed-submission/cases.json).
The old `job-00` request, source-bound admission observations and review findings
retain their recorded paths and bytes. Exact owner approval remains pending.

## Closed implementation gates

The documented `qd_platform.py submit` route requires an externally anchored
review packet whenever the registered family, design path or analyzer identity
names the diagnostic. The token-locked path compares the fresh case digest
with the pre-lock gate snapshot, verifies all six registered constructor/analyzer
dependencies, checks policy and package identities, and compares the complete
body with the reviewed candidate. The final verification follows the usage read
and precedes any consumed marker or POST checkpoint.

The [transport source probe](transport-process-identity.json) records that
Perceval 1.3.1's `runtime/payload_generator.py` creates a module-level UUID for
`process_id` and places that transport metadata beside `payload`. The binding
pins the reviewed UUID instead of silently excluding it from the comparison.
The JSON transport uses sorted-key UTF-8 encoding, matching the retained body
SHA-256. Every other body field remains equal to the reviewed body. The
transport UUID is an identifier, rather than a scientific seed or intervention.

The write-once marker resides under the selected token-store directory's
`reviewed-acquisition-attempts/`, outside every run directory. A token lock
serializes competing submissions; atomic exclusive publication and directory
fsync persist the exact case digest before checkpoint or POST. A lost response,
local interruption or copied run directory grants zero renewed attempt.
The guard covers byte-identical frozen cases in that shared token-store
directory. A changed case requires a new external review and approval.
Other hosts or token-store paths require independent coordination.

The reviewed source checkout remains quiescent during execution. The final
source recheck catches drift across provider reads; it is not an atomic lock
against arbitrary external filesystem writers. The source-bound analyzer
continues to require the frozen source revision for later analysis.

The regressions cover missing anchors, changed source/circuit/case/policy/body
and packages, omitted dependencies, case swaps during planning, source drift
during usage reads, public CLI enforcement, canonical wire bytes, simultaneous
copied directories and uncertain POST outcomes. Independent review reproduces
the original defects and verifies their repairs under these explicit boundaries.

Provider-wide verification passes 427 tests, including audit checks, and mypy
passes 653 files. The shared transport change also requires a
[source-compatible matched-mesh bundle](../ascella-transition-day-repeat-reviewed-transport/README.md)
for the local day-repeat launcher. That bundle preserves the existing science,
seeds, original timing window and earlier retained bytes. The update arms zero
timers or hosted schedules and grants zero acquisition authority to that case.

## Read-only admission and custody

The [cross-process validation](reviewed-submission-validation.json) performs a
fresh plan in a separate process, observes a different SDK process UUID, and
verifies the complete body after pinning the reviewed identifier. Its canonical
wire digest equals the approval packet's body digest. The observation records
zero submissions and an unconsumed attempt. Explorer reports `running`, the
processor reports `available`, and the estimate remains 262,144 shots and
1.032768 credits under the written tariff inputs. Fresh admission checks still
run during actual submission.

A separate owner-only write-once custody entry retains the packet, case,
source and body anchors under
`~/.local/state/gororoba-quantum/acquisition-approvals/`. That entry records
pending authorization. Explicit approval later enters a new custody record
and the actual submission receipt; the frozen packet stays byte-identical.
The operator records the final submission and result anchors independently
before invoking the source-bound analyzer.

The current approval scope is descriptive. Conditional uncertainty retains its
separate sampling-contract gate, and physical predecessor attribution remains
unavailable. The causal successor retains its separate chronology, randomized
assignment and carryover obligations. The [operator procedure](../../design/ascella-predecessor-intervention.md#successor-admission-procedure)
contains the bound command and full one-attempt limits.
