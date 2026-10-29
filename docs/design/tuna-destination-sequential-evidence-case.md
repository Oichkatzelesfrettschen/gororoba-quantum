# Tuna sequential destination response: working acquisition case

This case is **unapproved and unadmitted**. It proposes a prospective check of the
nominal-zero early and terminal q6 responses whose retrospective differences motivated
the [joint replay](../evidence/tuna-projector-geometry/joint-response-analysis.md) and
[early-label map analysis](../evidence/tuna-projector-geometry/early-label-map-analysis.md).
Neither old result becomes a new endpoint. The case can test an end-to-end response
null under explicit randomization assumptions; it cannot identify reconstruction,
discriminator behavior, physical state or a Cayley–Dickson property. Job-bound provider
association traces, thresholds, schedule and IQ remain separate evidence requirements.

## Intervention and observation

Use Tuna-17 (backend type 7), the two nominal-zero cQASM sources below, and one circuit
per serial batch. Each completed job requests 4096 shots. Source hashes name the exact
retained bytes:

| Source | SHA-256 | Early destinations for q4, q11, q6 |
|---|---|---|
| [Baseline](../../results/quantum_inspire/proposals/tuna-readout-destination-sequential/prepared-zero-baseline-before/baseline-before.cq) | `3ab15a468b5eaa4811a2a06f297754269976f6901dde12370cf3d5fad593f267` | 17, 18, 19 |
| [Rotated](../../results/quantum_inspire/proposals/tuna-readout-destination-sequential/prepared-zero-rotated-destinations/rotated-destinations.cq) | `3084eef16a0d32a23d7b3fa41c92f27fa3ce4f3d84791d128a10246728ad6d5d` | 19, 17, 18 |

Both declare 17 qubits and 20 classical bits, prepare nominal zero, measure q4/q11/q6,
then measure all 17 qubits terminally. Terminal q6 always uses bit 6. Decode early q6
from bit 19 for baseline and bit 18 for rotated; bit 0 is the rightmost character.
The retained [compiler receipt](../../results/quantum_inspire/proposals/tuna-readout-destination-sequential/compiler-admission.json)
has SHA-256 `c61eb8717a017243361e11b4f3179fcf6b3f9beb5b639aa1962b5dc05380ce8d`.
It does not establish the served schedule. Fresh compilation, structural checks and
source bindings must be verified for the eventual case and provider state.

Use two prespecified observables: early-q6 and terminal-q6 one fractions. The treatment
is the source assignment, including any resulting compilation, queue, physical or
reconstruction changes. The two source streams match locally after removing early
classical destinations; the served analog operation is unknown. Each of the two
responses has two directional hypotheses, for four tests in total.

## Required QX conformance before hardware

The [provider procedure](../notes/quantum_inspire/README.md) requires a QX dry run
before a hardware series. QX has a ten-qubit limit and returns the last measurement
per qubit rather than Tuna's classical-bit history, so QX cannot execute the 17-qubit
source or validate the early-q6 decoder. The older QX conformance batch is relevant
background but is not automatically a dry run of this case.

The [separate reduced QX case](tuna-destination-qx-conformance.md) specifies two
three-qubit destination patterns and an asymmetric terminal-order control. Its
expected QX outputs are `000`, `000` and `001`. A successful result can check supported
parsing, submission and terminal-output plumbing for those reduced sources. It cannot qualify Tuna's 17-qubit
physical stream, retained early labels, schedule, thresholds or IQ. Any remote QX job
or circuit upload requires the user's explicit approval of that exact written QX case;
this draft grants none. A local or historical simulator observation does not silently
replace the documented QX-first requirement.

## Sequential test and limitations

For each assigned position `t`, use `Z[t]=+1` for rotated and `-1` for baseline. For
one response let `Y[t]` be its fraction in `[0,1]`, and define
`X[t]=2 Z[t] (Y[t]-1/2)`. The predictable contrast `tau[t]` and required conditional
fairness, consistency and potential-outcome assumptions are stated in the
[sequential uncertainty design](tuna-sequential-destination-uncertainty.md). Past job
history, temporal drift and within-job shot dependence may be arbitrary. The current
assignment must be conditionally independent of the two current potential outcomes
given that history. Random-source provenance and future-assignment concealment require
separate evidence; a quantum source alone does not prove conditional fairness.

For each response and direction `d` in `(+1,-1)`, define the nonnegative process

    E[d,n] = (9/10) product_{t=1..n}(1 + d X[t])
             + (1/10) product_{t=1..n}(1 + d X[t]/2).

The product starts at 1. The smaller-stake component stays positive even if a full-stake
factor becomes zero. Under the directional null `d*tau[t] <= 0` at every visited
history, each component is a nonnegative supermartingale. A threshold of 400 per
response/direction allocates `0.0025` to each test; Ville's inequality and a union bound
control the probability of rejecting any true member of the four directional nulls at
at most 0.01, without independence between responses. Record the first crossing and the
running maximum, not only the final product. Record both directions if both cross at
different times; the directions are not mutually exclusive under changing effects.
Use exact rational arithmetic for all updates and threshold comparisons.

The [local scoring core](../../scripts/qi_tuna_sequential_score.py) implements the
four rational processes, destination-bit decoding for complete shots and shared stop
rules on already classified inputs. The core is a working implementation: it does
not validate job identity, allocation commitments, source bytes, admission, costs,
timestamps or the evidence supporting a neutral classification. It cannot admit a
campaign or establish the conditional randomization assumptions. A separate
source-bound collection and adjudication layer must verify those inputs before the
case can be frozen.

### Provider source-to-result association

The retained [Quantum Inspire API schema](../notes/quantum_inspire/api/openapi.json)
defines `Job.file_id`, `Job.batch_job_id`, `File.content`, `File.commit_id`,
`BatchJob.job_ids`, `BatchJob.backend_type_id` and `Result.job_id`. For every
slot, the future collector must retain the creation checkpoints and independently
read back the job, batch, file and result. It must match the checkpointed IDs,
the one-job batch membership, backend type, requested shots and raw-data flag;
compare the provider's stored source text under an approved canonical UTF-8
contract with the assigned source; and match the result to the same job before
decoding. Reject missing, duplicate, Boolean, malformed or conflicting identities.
The stored file must also match the admitted cQASM language ID, the `none`
compile stage and empty compile properties. A synthetic language ID in a test
is not a live provider identity; fresh admission must bind the actual ID.
The existing deadline-aware collector checks job and batch identities and result
membership, but does not check `Job.file_id` against the checkpoint or fetch the
stored file content. A schema declaration and local checkpoints do not prove that
the live service provides matching readback or that the served analog schedule
matches the source. Fresh admission and integration tests must establish the
available readback surface; unavailable or inconsistent association makes the
prospective score inadmissible.

The offline [association verifier](../../scripts/qi_tuna_source_association.py)
checks the one-job identity chain, a positive checkpointed result ID, one
internally consistent result page, and exact UTF-8 source text against supplied
checkpoint and readback records. Its slot-association entry point also checks
the supplied slot and arm against the digest-bound catalogue and selected
manifest, then requires the same source in the provider association. The caller
must authenticate the catalogue digest and assignment release; the entry point
does not establish commitment opening, assignment custody or fairness. The
complete-result decoder additionally checks the job status, requested and
completed shot counts, ordered binary shots and their histogram before it
constructs a score row. Each histogram key must be a width-20 binary string;
valid zero-count bins are allowed. The decoder compares its counts with an
independent calculation from the selected manifest's destination metadata.
The final packet must bind both decoder producers and their reviewed bytes.
The decoder does not establish when the result became available
or whether a complete observation is admissible for the sequential inference.
The byte-oriented decoder parses each supplied checkpoint and provider response
with duplicate-key and non-finite-number rejection into privately owned local
objects before applying the same checks. The caller must authenticate, retain
and bind the exact bytes and request locators; the byte parser does not do so.
The existing [platform client](../../scripts/qi_platform.py) returns
`response.json()` and therefore cannot retain duplicate-key evidence from the
response body. The collection transport needs a reviewed byte-preserving path
before JSON decoding. It must specify whether retained bytes are the HTTP
library's decoded response body or wire bytes, bind the request locator and
response metadata, and enforce the approved deadline on each request and retry.
The offline [readback transport](../../scripts/qi_tuna_readback_transport.py)
restricts GET locators, disables redirects, bounds response size and returns
the HTTP library's decoded body bytes before JSON parsing. It checks a supplied
clock around refresh, requests and body reads; the caller owns authentication,
the clock, bounded callbacks and receipt retention. Preemption between a clock
check and the request call remains possible, and the transport is not yet an
admission or dispatch guard. Fake-session tests do not establish provider
behavior or a live authentication boundary. Response bodies can contain account
identifiers; any retained exact bytes require private storage and an approved
sanitization boundary before repository publication.
The offline [readback collector](../../scripts/qi_tuna_readback_collection.py)
requests the checkpointed job, batch page, file and result page in decoder
order. It presents the checkpoint and each response to caller-supplied
retention callbacks before proceeding. A callback's return does not prove
durability or authenticity; an independently reviewed storage adapter must
establish those properties before the captured bytes enter scoring.
The collector presents a successfully returned receipt to retention before its
next clock check, so expiry at that boundary stops the collection without
discarding the receipt. The test covers all four response positions. The
transport still discards some failed or partial attempts before it returns a receipt.
The [expiry review](../archive/reviews/tuna-readback-expiry-review.md) confirms
the narrow ordering repair and holds inference on the missing attempt journal,
deadline adjudication, account binding and charge evidence.
The offline [private readback store](../../scripts/qi_tuna_private_readbacks.py)
creates non-overwriting owner-only files, syncs each file and directory, and
reloads only a complete set with matching response digests. The store assumes
one serialized owner, a trusted private directory outside the checkout, and a
filesystem with the required sync semantics. It cannot authenticate the
provider, isolate other processes with the same user identity, or establish
that a failed sync survives a crash. Failure requires external quarantine;
reload by itself does not admit a score or prove its observation time.
The [private-store review](../archive/reviews/tuna-private-readbacks-review.md)
identifies a late sync failure that can leave every expected file readable:
successful reload therefore cannot establish successful persistence. The review
also requires an external authenticated capture commitment and a durable
failure-quarantine authority across restart before using a reloaded capture.
The [recovery boundary tests](../../tests/scripts/test_qi_tuna_private_recovery_boundaries.py)
reproduce final file- and directory-sync errors with readable complete-looking
captures, and check rejection of selected file substitutions. The injected
errors do not establish behavior after a real filesystem crash. A separate
fixture shows that retaining the final receipt after expiry also produces a
reloadable capture: reload cannot decide whether the receipt was on time.

#### Recovery authority required for a readback attempt

The following is a proposed recovery contract, not an implemented authority.
An independently durable authority must record a pending attempt, keyed by
the authenticated account, approved case, slot, request and attempt, before
the first provider-facing action. An absent or unauthenticated pending record
prohibits that action. The authority's storage and access boundary must remain
independent of the capture directory and of the process whose persistence can
fail. The record must contain no bearer token or unredacted account identifier.

| Recovery observation | Permitted treatment |
|---|---|
| Pending record with missing intent, partial files or unknown request outcome | Quarantine the attempt; reconcile the provider identity and request outcome before any further request. |
| Pending record and readable complete local files after a reported or possible sync failure | Keep the attempt quarantined; readable files alone do not establish durability, origin or timing. |
| Pending record and a complete response observed after the approved boundary | Retain the response for reconciliation; classify the score under the separately reviewed deadline rule. |
| Pending record and authenticated, timely evidence whose bytes and successful persistence are independently attested | The adjudicator may evaluate source association, account identity, charge and assignment evidence; the record does not by itself admit a score. |
| Missing, conflicting, stale or unauthenticated authority state | Refuse further dispatch and scoring until independent reconciliation establishes the state. |

The release decision must bind the pending attempt and the exact authenticated
capture, timing, source, assignment and charge evidence, and its publication
must itself survive restart. A success marker written to the same filesystem
after a failed sync does not establish whether that marker or the capture
survives a crash. A new process must not infer release from a missing quarantine
file, a parseable capture, or a self-computed digest. An operator or separate
durable service may resolve an ambiguous attempt only through an authenticated,
auditable decision under the approved case; the protocol and failure-domain
assumptions require independent review before acquisition.
The offline [capture commitment](../../scripts/qi_tuna_capture_commitment.py)
binds a checkpoint and four ordered response envelopes and body digests to a
caller-supplied expected hash. A comparison rejects changed bytes or ordering
only when that expected hash is independently authenticated. The commitment
does not establish a valid source association, provider truth, observation
time, durable storage or a score decision; the producer needs integration into
the eventual adjudication path.
The [independent commitment review](../archive/reviews/tuna-capture-commitment-review.md)
accepts its encoding within that boundary and identifies the direct scoring
path and missing coherent-substitution tests. The revised local integration
stops after source association; an adjudicator remains necessary before scoring.
The revised commitment bounds locator length, query arity, query integer bit
length and escaped metadata before hashing. The
[bounds review](../archive/reviews/tuna-capture-bounds-review.md) identifies
allocation and integer conversion gaps in the earlier staged version; the
repair requires independent review. Those bounds do not validate source or
provider association; the stricter transport and association checks remain
separate obligations.
The [follow-up review](../archive/reviews/tuna-capture-commitment-followup-review.md)
confirms the coherent substitutions and separation of scoring, and requests a
pre-existing literal commitment for the mutation test. The mutation test uses a
fixed literal, while a separate canonical encoding vector has an OpenSSL hash;
neither authenticates a provider capture.
The [receipt-aware collection review](../archive/reviews/tuna-receipt-aware-collection-review.md)
requires an authenticated effective-request record and retention of failed
attempts. A separate adjudication record must bind each decision to the
source, provider receipts, producer digests, deadline and charge evidence;
the statistical scorer accepts count rows and cannot establish that binding.
The existing platform client's constructor records `member_id` after its first
OAuth refresh, while later refreshes reload the SDK configuration and update the
session's bearer token without reassigning that field. An adapter must verify the
effective authenticated subject and member after every credential reload, bind
the resulting team to the approval namespace, and stop on an identity change.
The cached member field alone cannot establish that the current bearer token
belongs to the approved member. An offline mock of this transition cannot prove
the provider's subject-to-member mapping; that mapping needs a supported,
authenticated provider observation before admission.
The installed `quantuminspire` 4.1.0 SDK's `AuthManager.refresh_tokens` calls
`_store_tokens`, which calls `_get_team_member_id`. The latter queries the
members API and prompts on standard input when the returned page has multiple
members. The inspected `auth_manager.py` has SHA-256
`2c0f1d9b32671a021e813f98664270309c9d3813a936dabbed0aa2977b233b50`;
the installed `qi-compute-api-client` is 0.63.0. That implementation introduces
additional network activity and a potentially unbounded interactive prompt
inside refresh. A guarded adapter must account for the actual refresh path,
its timeouts and identity selection before it can claim to journal or bound
all requests. The captured API schema exposes member `user_id` and user
`oidc_sub`, but the schema alone does not establish the live authorization
rules, pagination completeness, or an authenticated token-to-user match.
One candidate identity chain is the validated access-token subject, a unique
authorized `/users` result with the same `oidc_sub`, and a selected active
`/members` record whose `user_id` equals that user and whose `team_id` defines
the shared namespace. The retained schema permits those fields and filters;
it does not promise that access tokens expose that subject or that list
permissions and pagination make the match complete. Fresh read-only admission
must establish those contracts, or the adapter must use another documented
provider identity endpoint. A missing, ambiguous or inconsistent link refuses
admission. Account identifiers and token claims belong only in protected local
evidence; public records use an approved keyed digest.
The installed SDK decodes the token without signature verification solely to
read `iat`. That operation is not subject authentication. A candidate verifier
must validate the token under a trusted, current issuer and key set, approved
algorithms, intended audience and validity times before using any claim; it must
also bound key discovery and handle key rotation. The local QI environment has
PyJWT 2.15.1 and cryptography 50.0.2, but installed libraries alone establish
neither the served token contract nor a verified identity.
The retained [public discovery observation](../evidence/quantum_inspire/oauth-public-discovery/observation.json)
binds the public configuration, OpenID document and key-set response bytes.
At that observation the issuer was `https://auth.quantum-inspire.com/` and
the key set contained two RSA signing keys declaring `RS256`. The discovery
document's ID-token algorithm list is not an access-token validation contract.
Key rotation and provider policy require fresh authenticated checks; the
retained key set must not drive a later submission.
The retained OpenID discovery document also advertises a `userinfo_endpoint`.
That endpoint is a candidate source for the subject, but the discovery document
does not establish that the compute-audience access token has the required scope
or is accepted there. A bounded, authenticated read-only observation must check
the endpoint and its response contract without publishing token or subject
values; an error, unexpected audience, or ambiguous subject leaves the
subject-to-member link unresolved. The observation must not replace access-token
validation or proof that the member and team belong to the approved account.
The offline [subject-binding check](../../scripts/qi_tuna_subject_binding.py)
compares a caller-verified subject with supplied user and member records and
derives separate keyed subject, user, member-and-role and team identities. It rejects inconsistent
identities, inactive records, boolean identifier aliases and ambiguous JSON.
It neither verifies a token nor authenticates or fetches the records, proves
uniqueness or pagination, or establishes when they were observed. The adapter
must supply those properties and compare the bound identities after every reload.
The [subject-binding review](../archive/reviews/tuna-subject-binding-review.md)
identified a coherent user, member or role transition that preserved the earlier
subject-and-team-only output. The revised check supplies separate keyed user and
member-and-role identities and tests those transitions. It remains stateless:
the future adapter must compare the approved identity, issuer and audience with
fresh authenticated evidence before another request.
The [subject-binding follow-up](../archive/reviews/tuna-subject-binding-followup-review.md)
accepts the four-domain encoding while leaving authentication and refresh-time
enforcement to the adapter. Additional tests check field-by-field transition
invariants and keep differently normalized opaque subjects distinct.
The offline [identity continuity guard](../../scripts/qi_tuna_identity_guard.py)
compares all four keyed identities to a caller-supplied approved binding and
latches refusal after a mismatch or malformed observation in one serialized process.
It does not authenticate either binding, verify issuer or audience, persist
the refusal across restart, coordinate other account users, or prevent another
code path from sending requests. The future adapter must supply those controls;
the guard and its integration need independent review.
The [identity guard review](../archive/reviews/tuna-identity-continuity-review.md)
identified an aliased approved binding and a malformed-object path that bypassed
the latch. The revision snapshots each digest and normalizes missing fields into
a latched refusal. It assumes serialized calls and needs a follow-up review.
The SDK's `OauthDeviceSession` constructor also fetches OAuth discovery on
every construction, including when the stored access token has not expired;
its `requests.get` supplies no timeout. Its refresh-token `requests.post` also
supplies no timeout. The inspected `authentication.py` has SHA-256
`fb7111b784ce5f82e22d4c4033386b5151f6f1a15638cb08bf686180535b5b19`.
An outer clock check cannot bound either blocking request or the member prompt.
A replacement or controlled integration must preserve the provider's OAuth
and token-rotation semantics while bounding every operation; an interrupted
refresh needs reconciliation before another process uses the shared token.
In the installed SDK, `_store_tokens` also calls `UserSettings.save`, whose
inherited implementation writes JSON through `Path.write_text`. This write
occurs inside `AuthManager.refresh_tokens`, before the repository client's
subsequent atomic publication for a rotated token; an interruption during the
SDK write can leave the shared token file incomplete. The inspected
`base_settings.py` has SHA-256
`60cff1637561fa36ae7b4d5b3424b83d0d5f0377ca086f86961ce90b808c5141`.
The guarded integration needs a reviewed publication and rotation-recovery
contract covering that earlier write, including the case where a refresh token
was spent but its replacement could not be durably retained.

The attempt journal for the future transport needs a durable, ordered intent
before each request and a terminal observation before any retry. The intent
binds the slot, request ordinal, attempt ordinal, account namespace, method,
canonical authority, path and query, and the case and clock evidence digests.
It must exclude bearer tokens and other secret headers. The terminal observation
binds the effective request and available response envelope, completion or
failure classification, clock observations, and a digest and length of the
retained decoded body or prefix. A digest identifies retained bytes; it does not
authenticate the provider or prove when those bytes were observed.

An incomplete intent after a crash represents an ambiguous attempt, including
the possibility that a request reached the provider. A partial stream retains
its prefix and the fact that the body is incomplete; the prefix cannot enter the
result decoder. A complete body received after the observation boundary remains
available for recovery but cannot become an on-time observation. Failure to
persist or sync an intent, body, or terminal observation prohibits further
requests and requires a separately durable quarantine that survives restart.
The next attempt may start only after the preceding terminal observation is
durably retained and the clock and authenticated account are checked again.
The journal must reconcile the effective prepared request and response URL with
the intended locator and reject redirects or mismatches. These requirements
remain unimplemented in the present transport and private store.
The separate offline [attempt transport](../../scripts/qi_tuna_attempt_transport.py)
presents an intent before a readback request and an outcome before retry,
including a bounded observed body prefix and stream completion or error types.
Synthetic tests cover a 401 retry, partial or oversized bodies, expiration,
request and close exceptions, and callback failures. The `request_called` flag
records a local call attempt, not a provider receipt or physical send time.
The callbacks do not prove durability, authenticate the session, bind the
effective URL, record trusted observation times or include refresh operations.
The existing collector does not use this transport; independent review and the
remaining journal and dispatcher integration are required before admission.
The [attempt-transport review](../archive/reviews/tuna-attempt-transport-review.md)
identified ordinary receipt reuse and masked simultaneous retention failures.
The revised transport returns an explicitly unadmitted wrapper and chains
underlying stream and close errors when outcome retention also fails. A caller
can still deliberately unwrap the receipt, and exception chaining does not
provide durable failure evidence or replace quarantine. The revised bytes need
follow-up review.
The local [private attempt journal](../../scripts/qi_tuna_attempt_journal.py)
stores intent, nonempty body and outcome files with exclusive creation and
file-before-directory sync. It replays complete pairs in order and accepts a
second attempt only after a complete, error-free 401 for the same locator. A
lone retryable 401 is reported as `retry_pending`, not a terminal operation.
Incomplete sets refuse replay and remain available for separate recovery.
The journal requires a trusted private filesystem and one serialized owner;
callback return or a successful reload does not prove provider authentication,
the observation boundary, or survival after a failed sync. An independent
cross-restart quarantine and authenticated context remain required. The
journal and transport are connected only in synthetic tests and require
independent review before integration into the case.
The separate [journaled collector](../../scripts/qi_tuna_journaled_collection.py)
composes four caller-supplied journals with the attempt transport and capture
retention, returning an explicitly unadmitted wrapper. Synthetic tests exercise
complete readbacks, a partial second response, checkpoint and readback retention
failures, and expiry after retaining a readback. The collector has no
authenticated session, effective-request check, trusted observation clock,
durable quarantine or dispatcher binding; no production acquisition path
uses it. The wrapper can be deliberately unwrapped and is not an admission
control. Independent review and the remaining integration stay required.
The [collector review](../archive/reviews/tuna-journaled-collection-review.md)
found that an oversized batch identifier could pass collection but fail the
capture commitment. The revised collector validates all checkpoint identifiers
against the commitment's bound and validates every locator before any clock,
retention or request callback. Boundary tests exercise the maximum identifier
and rejection above it. The revision and the broader failure matrix require
independent review; the collector still cannot establish admission.
The [follow-up review](../archive/reviews/tuna-journaled-collection-followup-review.md)
confirms the identifier repair and identifies response metadata that can exceed
the commitment's aggregate limit. The revised collector retains each attempt in
its journal, then checks the shared commitment budget before storing the response
in the private capture or issuing the next request. Callback and expiry failures
can still leave a complete-looking capture, as the recovery tests show. Reload
therefore cannot replace durable quarantine or independent adjudication; the
revision requires review. The [prefix-budget review](../archive/reviews/tuna-capture-prefix-budget-review.md)
found the prior ordering stored the response before checking the budget and
independently bounded fixed encoding overhead at 822 bytes, below the 2048-byte
reserve. The revised ordering retains attempt evidence first and rejects an
oversized capture prefix before the private capture write.
The [retention-order review](../archive/reviews/tuna-capture-prefix-retention-review.md)
confirms that ordering and the bounded metadata accounting. Its first two
findings compare the preceding review's historical hashes and findings with the
revised index: the preceding report identifies the earlier bytes it reviewed and
does not certify later revisions. The preceding report remains unchanged; the
later review and its own hashes record the revised evidence. The later review
also identifies source association as a caller-owned boundary and reiterates that
expiry and persistence failures require external quarantine.
The [journal review](../archive/reviews/tuna-private-attempt-journal-review.md)
identified contradictory outcomes, retry-pending ambiguity, oversized metadata
and cross-restart quarantine as distinct issues. The revised local validation
rejects contradictory outcomes and bounds encoded metadata before writing the
body. Reload checks parsed metadata and current body digests; it does not
authenticate historical metadata bytes or a same-user replacement. The revised
code requires follow-up review, and cross-restart quarantine remains external.
The [attempt-retention follow-up review](../archive/reviews/tuna-attempt-retention-followup-review.md)
accepts the local repairs and identifies remaining integration and adversarial
coverage gaps. Additional tests exercise boolean/integer aliases, malformed
success states and exact request and refresh ordering; they do not establish
provider behavior or independently prove the outcome-retention callbacks durable.
The collection layer must retain the request
locator, response envelope and result identity before scoring. A single page
reporting one result does not provide an atomic provider snapshot or prevent
another result from appearing later. The batch mapping is a caller-selected
projection in the lower-level predicate; the slot-association entry point also
checks a one-batch page and its checkpointed ID. The collection layer must
authenticate and retain the batch query and response, and the page does not
establish an atomic provider snapshot. The verifier does
not authenticate those records, prove their association with an approved
assignment, validate timestamps, or contact the service. The collection layer and an
independent review must establish those remaining boundaries before use.

The three retained nominal-one `submission-state.json` records under
[the nominal-one run](../../results/quantum_inspire/runs/20261027T232908Z-tuna-destination-one-response/)
each contain one creation checkpoint whose job and file IDs agree with the job
in the corresponding `results.json`. The three nominal-zero submission-state
records under [the nominal-zero run](../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/)
do not contain `created_resources`; that particular checkpoint comparison is
unavailable for those records. The six inspected `results.json` records contain
neither a stored-file content readback nor a batch readback. Those observations
describe the named retained files and do not establish what the provider served
or whether another source can supply the missing readbacks.

A crossing challenges the corresponding uniform pathwise conditional-mean null. It
does not prove a persistent effect, an average effect, a calibrated population, or an
identified fault. A non-crossing does not establish equivalence. The e-process does not
provide a confidence interval for an average effect; any such interval needs a separate
reviewed method. The 0.10 comparison from the old case is not the null margin here.

The 24-job limit also constrains sensitivity in a centered, zero-score-variance
point alternative. Suppose both observables have the same constant rotated and
baseline fractions, `(1 + d)/2` and `(1 - d)/2`, at every position, and both
potential jobs complete. Each assignment then
contributes the same positive score `d`, so the positive evidence value after
`n` positions is `0.9 (1 + d)^n + 0.1 (1 + d/2)^n`. For `d = 0.25` the value
after 24 positions is about 192.27, below 400. For `d = 0.5` the value is about
396.95 after 15 positions and 594.71 after 16. The
[exact-arithmetic test](../../tests/scripts/test_qi_tuna_sequential_score.py)
reproduces both trajectories with attainable 4096-shot counts. Under the stated
point alternative the crossing probability is zero by 24 positions for `d = 0.25`
and one by position 16 for `d = 0.5`, for either assignment sequence. Those
model-specific probabilities give neither an upper nor a lower power bound for
other alternatives with the same contrast. The example does not represent queue
failures or drift, or claim that the retained nominal-zero response will recur.
The 4096 shots provide outcome granularity; each job supplies one intervention
assignment, and the analysis permits within-job dependence. A non-crossing
remains inconclusive, including when a moderate effect is present.
The [independent review](../archive/reviews/tuna-sequential-sensitivity-review.md)
verified the arithmetic and requested the model-specific interpretation and
prefix-level coverage above. The revised text and test require follow-up review.

Stop further dispatch when both observables have crossed at least one directional
threshold, at 24 assigned positions, at the request deadline, or upon any acquisition,
admission, cost or identity failure. A crossing for only one observable is reported as
such; the other remains inconclusive. Stop on the first invalid or incomplete job and
preserve every dispatched identity. To define the statistical observation even when a
source would fail, the proposed augmented outcome assigns `Y=1/2` to a confirmed failure,
well-formed partial result or unavailable result at its prespecified observation boundary. The neutral
score is a deadline-based analysis value, not a claim that a running job has failed.
Such a score has factor 1 and the executor then stops; it changes the estimand to include
availability. A rejection can therefore reflect source-dependent success or timing,
even when the underlying physical response does not differ. The final implementation
must define both counterfactual augmented outcomes and score each assignment once.
An ambiguous submission remains unresolved until read-only reconciliation establishes
its identity; do not call a still-running job permanently failed or resubmit it.

The test's unconditional error bound covers the specified attempted-campaign process.
Conditioning the guarantee on favorable completion requires an additional argument.
Malformed records, violated source or decoder identities, an unavailable assignment
record, or a demonstrated fairness/ordering violation make inference inadmissible. All
raw shots and diagnostic histograms are retained separately; scoring failures does not
rewrite or substitute them. More assumptions and a separate analysis are needed for
physical attribution, equivalence, or an average causal effect.

### Slot observation boundary

For the working case, start a suspend-aware slot clock immediately before the first
submission request for an assigned slot. Its observation boundary is the earlier of
3600 s after that start and the 64,800 s campaign request deadline. The runner must
persist the slot number, assigned arm, intent, boot identity, UTC observation and
boot-time boundaries before the request. Linux `CLOCK_BOOTTIME` includes suspended
time; a persisted monotonic value alone cannot establish the boundary after reboot.
The clock implementation, sampling uncertainty, clock-disagreement tolerance and
restart rules require review and inclusion in the approved case. A changed boot
identity, unadjudicated clock discontinuity, or loss of trusted boundary evidence
stops dispatch and makes the affected inferential score inadmissible; a restarted
process cannot silently start a new slot interval. Network calls receive bounded
timeouts and cannot be started after the applicable boundary; an in-flight call may
return later.
The current transport does not enforce the request-start requirement: a
[deterministic preemption fixture](../../tests/scripts/test_qi_tuna_request_start_boundary.py)
advances the clock after the last successful check and observes a request call
after the boundary. The fixture models the scheduling gap; it does not measure
kernel or provider timing. An admitted dispatcher must resolve the gap with an
independently reviewable request-start mechanism or a revised case that
explicitly incorporates the uncertainty before approval.

A trusted clock observation after a complete authenticated response causally
bound to the request can supply an upper bound on request initiation: the
request must have started before its response completed. If the observation and
its uncertainty lie wholly before the boundary, the request started before that boundary under the authenticated
transport and clock assumptions. A response observed after the boundary cannot
by itself establish whether initiation was early or late. This retrospective
implication can qualify a timely result; it cannot prevent a late submission or undo a
provider action. The request-start policy therefore still needs an enforcement
or an independently reviewed revision with an explicit late-action risk and
owner approval. The current clock callbacks do not authenticate this evidence.

Score a validated complete result only when its identity, source, 4096 ordered
width-20 bits, counts and zero-charge checks are available by the boundary. A
provider-confirmed terminal failure without usable shots, a well-formed partial result,
or a confirmed submitted job whose complete result is unavailable at the boundary gets
one neutral `Y=1/2` score for each observable and stops the campaign. A pending job's
neutral score records analysis-time unavailability, not physical failure or cancellation.
An unconfirmed submission identity, conflicting identity or source, malformed result,
missing assignment, invalid timestamps, structural drift or charge makes inference
inadmissible and stops the campaign. These rules are prospective and require tests
against the provider's actual response and recovery schemas.

The runner retains the score decision and its observation time immutably. Later
read-only reconciliation and collection preserve the eventual raw record and can support
a separate descriptive analysis, but must not replace a neutral inferential score or
resume the campaign. A result that arrives after the boundary does not retroactively
become available by the boundary. No retry, replacement or selective removal of a slot
is authorized.

## Assignment concealment and binding

Construct both arm-specific source and manifest alternatives for each of the 24 slots;
a public sequence of arm-specific filenames or manifests would disclose future orders.
A commitment to an unsalted 24-bit sequence is also enumerable. Before dispatch, bind
the exact source pair, assignment algorithm, random draw receipt and a cryptographically
salted commitment to the whole allocation. Store the salt and unrevealed values outside
the repository in an access-controlled location; disclose only the current bit after the
pre-assignment admission state is fixed under the account lock. Preserve a private audit
record and publish the opening material only after the campaign can no longer be affected
by future assignments. Unused allocated values remain reserved and are never reused.

The commitment protocol needs an independently reviewed entropy source, precise
canonical encoding, access model and deterministic verifier. The runner must not read or
log future values, and the provider receives only the current source. Concealment and
commitment make premature disclosure harder; they do not establish that the underlying
bits are conditionally fair, that every actor lacks future information, or that the
provider uses an identical served schedule. A violation or unavailable allocation
record makes inference inadmissible.
The [private-assignment design](tuna-destination-private-assignment.md) specifies the
custody boundary and the additional implementation and review required before a draw.
The [slot-alternatives catalogue](../../results/quantum_inspire/proposals/tuna-destination-slot-alternatives/catalogue.json)
binds both one-circuit choices for each of the 24 positions to the historical source and
compiler evidence. The catalogue contains no selected assignments and grants no
submission authority. The local source comparison does not establish a served schedule.
The generic Quantum Inspire submit command does not enforce the catalogue's
`provider_execution_authorized=false` field. A separately reviewed guard must bind
the exact approval, allocation, current slot and admission before dispatch.

## Workload and queue envelope

The working envelope allows at most **24 jobs**, **98,304 shots** and **18 hours**
(64,800 s) for initiating campaign requests. Each request is one job in one batch;
collect and reconcile the preceding job, observe the account-wide 30 s hardware pause,
and refresh queue, backend, pricing, terms and heartbeat checks before the next. The
working thresholds are a 120 s maximum heartbeat age and a 60 s maximum age for the
oldest admission read, including time spent acquiring the account lock. The pause starts
at 30 s and the repository escalation rule applies after a platform failure; that failure
stops this case rather than authorizing a retry.
The FAQ's three-queued-job limit and the repository's stricter one-queued-batch rule
both apply. No automatic retries, job substitution or cancellation of other workers'
jobs are authorized. A request already in flight can finish after the deadline;
dispatched work is retained and recovered read-only by its recorded identity.

The three retained nominal-zero executions reported 14.356782 s in total. Their mean
scaled to 24 jobs gives a workload estimate of **114.854256 execution seconds**,
excluding queue, pause and service overhead; the estimate is not a guarantee. The
historical provider ceiling is 300 s per job, or **7200 s** for 24 jobs. The
working case expects and permits **zero credits**. Fresh terms and a zero ledger
do not guarantee the cost of future requests; a hard zero-credit ceiling requires
an authoritative exact-request provider guarantee, or a separately written case
and explicit approval of a bounded charge risk. The retained API exposes no
spending-cap parameter, so a delayed charge cannot be reversed; an observed
charge stops further dispatch.

A stress scenario uses the observed maximum creation-to-`queued_at` interval of
1936.258985 s for each job, 23 pauses of 30 s and 24 execution ceilings of 300 s:
**54,360.215640 s**, about 15 h 6 min before other overhead. That arithmetic does not
predict a completion probability or bound future waits. An 18-hour horizon therefore
admits a substantial risk of an incomplete case; no stationary queue model is asserted.
The horizon, zero-credit rule and workload need explicit user approval after the case
is fully implemented and independently reviewed.

## Illustrative sensitivity, not Tuna power

For a deliberately unrealistic model, suppose every baseline job returns exactly the
old baseline-average fractions and every rotated job exactly the old rotated fractions,
with fair independent assignments and complete jobs. The retained early counts are
1442/4096, 3419/4096, 1449/4096; the terminal counts are 938/4096, 2525/4096,
969/4096. The two positive e-process factors are then deterministic functions of
assignment, and each component increases on every job. Exact binomial enumeration
under this toy model gives:

| Assigned positions | Probability both positive processes have crossed 400 |
|---:|---:|
| 16 | `0/65536 = 0` |
| 20 | `783275/1048576 = 0.7469892501831055` |
| 24 | `16764265/16777216 = 0.9992280602455139` |

At 16 positions the early process needs at least eight rotated assignments while the
terminal process needs at most three, so both cannot cross in this model. The table
assumes exact stable fractions, no failures and independent fair assignments. The
three historical jobs cannot justify those assumptions, a future assignment law or a
probability of campaign completion. The table is not a power or queue forecast.

## Required work before an approval request

1. Prepare and obtain separate approval for the required reduced QX dry-run case, with
   explicit recognition of its output and width limits.
2. Freeze and independently verify the four e-processes, exact arithmetic, threshold
   boundaries, shared stopping rule, neutral failure definition and full potential-outcome
   interpretation. Test zero factors, later recovery, non-crossings, invalid records and
   assignment-dependent failures against independent reference calculations.
3. Construct distinct single-job manifests and compiled source receipts for all slots;
   validate source mapping, physical-stream equality, terminal bits and mutation tests.
4. Specify and review a quantum-random allocation, conditional-law assumptions, private
   future-value handling and exact assignment-to-job binding. Do not draw, select or
   disclose future assignments as part of this draft.
5. Implement and test the 18-hour request deadline, serial account lock, one-batch queue,
   pause, live admission, no-retry and late-recovery rules. The older six-job executor is
   frozen to a different case and cannot authorize this one unchanged.
6. Obtain the requested independent high-effort case review, resolve findings, perform
   fresh read-only provider admission and present the exact bound case for explicit user
   approval. Availability of the provider association traces could change the case.

No provider job, remote simulation, upload, booking or upstream message is authorized by
this draft. A completed response test alone does not admit a Cayley–Dickson hardware claim.
