# Ascella target-slot diagnostic acquisition review

The owner selects the existing eight-iteration diagnostic with causal
attribution explicitly unavailable and requests a separate causal successor.
The [packet](acquisition-review-packet.json) binds the request, circuit,
constructor, analyzer, provider wrapper and current admission observation.
Status: approval request withheld pending mechanical submission bindings.

## Independent findings

An independent read-only agent inspects exact source head `68ecb43`, executes
the byte-exact case replay, checks the analyzer CLI and probes default
descriptive output. The review makes zero provider calls and edits zero files.

**Serious:** `qd_platform.py:1456` refreshes a plan under the token lock and
supports a verification callback, but the documented CLI at line 2919 supplies
zero callback and accepts zero reviewed-plan digest. Planning also leaves
`analysis_sources` unchecked against current files. The documented submission
route therefore does not mechanically bind the externally reviewed body,
case and source/analyzer identities. A separate earlier `--check` does not
close the time between checking and posting. A case-specific verified route
must bind those identities before acquisition approval.

**Boundary:** `qd_platform.py:1454` refuses an existing submission, body or
checkpoint in the same run directory. The checkpoint precedes POST and protects
that directory from retry after an ambiguous response. Copying the case to a
fresh directory bypasses case-wide consumption. The one-attempt approval needs
a case-wide guard, in addition to the directory and token locks.

**Sound:** the default analyzer requires external submission/result digests,
emits descriptive output with physical predecessor attribution unavailable,
and issues zero confidence statements without its externally anchored sampling
contract. Conditional review remains separate from this descriptive scope.
The signed contrast cannot separate predecessor response from curvature.
More observations narrow uncertainty on that mixture rather than identifying
its physical components.

## Fresh read-only admission and custody

The [admission observation](acquisition-review-admission.json) records a passed
read-only plan at 2026-10-29 00:51:39 UTC. Explorer reports `running`, the
processor reports `available`, and the token occupancy checks pass. The plan
estimates 262,144 shots and 1.032768 credits using the retained one-credit
per-job input and live per-shot price. The passed plan does not independently
establish the account's available credit balance or total tariff guarantee.
`running` remains admissible; calibration, maintenance and occupied-token gates
remain enforced.

The fresh body digest differs from the retained running-plan body digest,
while the cases digest, reported package versions and estimated shot count
match. The summaries omit body bytes; the cause remains unestablished.
The observation demonstrates that a stable cases digest alone does not bind
the body. Neither digest difference establishes changed physical compilation.

The committed packet remains outside each analyzed run directory. A separate
write-once entry under
`~/.local/state/gororoba-quantum/acquisition-approvals/` retains its digest and
request/body anchors with owner-only file permissions. The entry records
review-process origin and pending authorization. That storage boundary
establishes custody, rather than owner approval or provider chronology.
After approved execution, independent custody entries must retain the actual
submission and result digests before analyzer invocation. Expected hashes
come from those entries, rather than from rereading the files under analysis.

One attempt covers one eight-iteration job with 32,768 samples and shots per
iteration, 262,144 aggregate shots, expected 40 seconds, a 300-second duration
cap and a 1.032768-credit ceiling. The case grants zero automatic retry.
Owner approval follows closure of the body/source and case-wide attempt gates,
refresh of the complete provider admission and review of the exact packet.

The [causal successor contract](../../design/ascella-predecessor-intervention.md#causal-successor-preparation-contract)
keeps chronology, randomization, carryover, target-sensitive references and
complete block/charge sizing as separate obligations. The existing diagnostic
allocates zero exposure to that successor and grants zero continuation authority.
