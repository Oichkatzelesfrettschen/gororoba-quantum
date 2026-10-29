# Private assignment for the Tuna destination case

The [sequential destination case](tuna-destination-sequential-evidence-case.md)
requires a fair, conditionally independent assignment at every job. This working
design identifies the custody and publication requirements. It does not allocate
random values, establish fairness or authorize a provider request.

The [ANU adapter](../../scripts/anu_qrng.py) writes the raw response and parsed
values into its output file. A published draw from which the case derives future
assignments would reveal those assignments. A case must keep the whole draw and
its derivation private until future assignments can no longer affect acquisition.
The adapter accepts an output directory, but its file creation inherits the
process umask; a caller must establish and verify private directory and file
permissions before relying on that path. A process running under the same user
identity can generally read those files, even when other users cannot. Filesystem
mode alone therefore does not establish concealment from other local processes.

## Candidate custody boundary

1. Before any draw, freeze and review the value-to-arm rule, source, number and
   order of allocated indices, commitment encoding, threat model and release
   conditions. The draw must use the repository's admitted source and retain the
   raw response for later audit. Unused values remain reserved to this case.
2. A trusted allocation custodian retains the complete draw, index list and
   secret commitment salt in a private location outside the checkout. Access
   must be limited to the custodian by an independently justified isolation
   boundary or a documented trust assumption covering every process with access.
   The executor must receive only the current assignment after its
   pre-assignment history and admission observation are fixed. The executor,
   provider and logs must not receive future assignments or opening material.
3. The public pre-dispatch commitment must bind the exact draw bytes, index order,
   allocation rule, source pair and entire assignment sequence using an
   unambiguous canonical encoding and a sufficiently unpredictable secret salt.
   The commitment must not expose a separately enumerable unsalted digest of the
   24-bit sequence. A verifier must reject an altered opening, index reuse,
   missing allocation, changed source identity or inconsistent current-slot
   release. The precise encoding, salt source and custody mechanism require
   implementation and independent review before the case is frozen.
4. The custodian releases the draw, salt and allocation opening only after the
   campaign has permanently stopped and later assignments cannot influence an
   acquisition. A verifier then checks the source adapter's retained-response
   contract, the commitment and every released assignment. A missing opening
   or evidence of early disclosure makes the randomized inference inadmissible;
   raw physical observations remain available for bounded description.

## Provenance and selective timing remain unresolved

The ANU adapter's offline `admit` check validates the response's internal
structure, value range and recorded hash. Those checks do not authenticate the
server as the author of the retained bytes, establish which request was first,
or prove that the custodian did not discard unfavorable draws. The eventual
protocol needs an authenticated or independently witnessed acquisition record,
or an explicit trust assumption that covers fabrication and selection. It must
fix the first eligible request and a no-discard rule before obtaining values,
retain every request attempt, failure and retry decision, and bind a witnessed
commitment time before dispatch. A failed or ambiguous acquisition must not be
silently replaced by a more favorable sequence.

The protocol must also fix each assignment request time and response deadline
before disclosing the arm, and must prevent or account for a custodian's
arm-dependent release delay. A release after the boundary, a missing response,
or evidence of selective timing stops the case and makes randomized inference
inadmissible. A claimed timestamp in an unauthenticated local file is not an
independent witness. A complete threat model must specify who can observe future
values, control request timing or modify logs, and how those actions are detected
or covered by trust. The public alternatives reveal the arm from a selected
directory, source hash or manifest hash, so access logs and selected identifiers
must stay private until that slot becomes current.

For example, the least significant bit of a uniformly distributed 16-bit value
splits the 65,536 possible values equally. That arithmetic does not establish
that an actual service's outputs are uniform, independent across indices, hidden
from relevant actors, or conditionally independent of potential job outcomes.
Those properties remain assumptions to justify for the exact implementation.
Neither a salted commitment nor a quantum source proves the assumptions.

The [ANU adapter](../../scripts/anu_qrng.py) has no documented mechanism for
atomic private publication of an allocation, secret salt handling, one-slot
release or post-campaign commitment verification. A future implementation must
test interruption, permissions, duplicate release, altered openings and leakage
before any allocation is used. This document does not replace the source adapter's
draw receipt or the repository's allocation ledger.

## Working commitment encoding

The [offline commitment implementation](../../scripts/qi_tuna_assignment_commitment.py)
accepts one exact ANU record containing 24 `uint16` values, ordered by indices
0 through 23. The low bit at index `t-1` maps zero to baseline and one to
rotated at slot `t`. The input record must name the 24-value ANU request and
pass the adapter's consistency check; the implementation rejects duplicate JSON
keys. The origin and requested order are labels checked for consistency, not
authenticated facts. A source-order or retry policy must be approved and
enforced separately.

The historical ANU adapter can accept a raw boolean `false` or `true` where
the separately stored parsed value is integer `0` or `1`: Python compares
those values equal. The commitment validator independently requires each raw
data value to be an actual integer in the `uint16` range before invoking that
adapter. A non-object raw response also receives a controlled rejection. The
historical adapter remains unchanged because retained submission records bind
its producer bytes; its broader consumers still need a separately reviewed
repair and evidence migration.

The candidate commitment is SHA-256 over the ASCII bytes
`gororoba-qi-tuna-assignment-v1` followed by a zero byte, a 32-byte secret salt,
the 32 raw bytes of the exact slot-catalogue SHA-256, the 8-byte big-endian
length of the draw record, and the exact draw-record bytes. The fixed domain
names the index and arm rule; a different rule needs a different domain. The
caller supplies the salt and catalogue digest. The function does not generate
the salt, check its entropy, read a catalogue, record a witness time or protect
the input from other local processes. Hiding the small assignment space depends
on an unpredictable secret salt and the commitment's cryptographic assumptions.

An opening verifies the digest and a contiguous released slot prefix against
the committed values, returning no future sequence. The function does not
enforce post-stop invocation, check release or submission timestamps, prove
that releases were concealed before their slots, or bind them to actual jobs.
The caller must supply a digest independently computed from the approved exact
catalogue and retain the release evidence through a separately reviewed guard.
Synthetic test vectors exercise the encoding; no assignment draw or salt has
been created for the proposed case.
