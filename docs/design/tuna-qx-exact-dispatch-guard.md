# Exact dispatch guard for the reduced QX case

The [reduced QX case](tuna-destination-qx-conformance.md) proposes three
2048-shot simulator jobs. Its manifest and analyzer are unapproved working
artifacts. The generic [Quantum Inspire submitter](../../scripts/qi_platform.py)
accepts nonempty approval text and does not enforce the manifest's descriptive
`provider_execution_authorized` field. This design specifies the additional
guard required before asking the owner to approve a provider request. It does
not itself authorize an upload, simulator job or hardware job.

## Exact approval object

Before requesting approval, generate and independently review one packet that
binds exact bytes of the written QX case, `cases.json`, all three source files,
the local-replay and result-analysis producers, the guard and its submission
helper, the decision and stop rules, and the policy baseline used for comparison.
The packet states backend type 1, three jobs, 2048 shots each, 6144 total shots,
3600 execution seconds per job, 10800 total execution seconds and zero expected
credits. The proposed zero-credit ceiling is not yet executable: a historical
zero ledger and policy text do not guarantee that a new job cannot incur a
delayed charge. An authoritative provider quote or reservation must guarantee
zero for the exact requests, or the owner must explicitly approve a separately
written case with a bounded charge risk. The proposed zero-credit envelope does
not supply that second authorization. Its request-initiation horizon and
freshness limits must be explicit in the packet and approved with the rest of
the case. The historical
execution and queue observations are neither a forecast nor a guarantee.

A path-name search of the retained provider API identified transaction reads
but no billing quotation or credit-reservation endpoint. That search does not
establish whether another provider channel offers an exact-request guarantee.

An approval record must bind the exact packet digest and the owner's explicit
case-specific approval. The approval channel must provide a verifiable receipt
or the case must explicitly name the trusted operator and record the exact user
approval and its session provenance. A local JSON string or digest alone cannot
establish who approved it. The canonical consumption key must derive from the
authenticated account and approval event, and the marker must bind the exact
packet. Reusing one approval event for another packet must collide rather than
create a fresh consumption key. A
renewed authorization needs a distinct verifiable approval event; copying or
editing a record cannot create one. The packet must define one account-scoped
marker namespace, the private account-binding mechanism, marker schema,
permissions, owner, durable location and the protection against multiple home
directories or hosts using the same account. If the account cannot be reliably
bound to one consumption namespace, the guard must refuse. No current record
conveys approval for this proposed case.

The retained [provider schema](../notes/quantum_inspire/api/openapi.json) gives
each member an `id`, `team_id` and `is_active`, and each transaction a
`team_id`. A candidate account binding can read the authenticated member by
the client-selected member ID, require the returned ID and active flag to
match, and derive a private namespace key from the verified provider host and
positive team ID. A keyed digest with a protected, shared namespace secret
avoids publishing a directly enumerable hash of the team ID. All participating
processes and hosts would need the same trusted secret and marker namespace;
the adapter must refuse if that binding is unavailable or inconsistent. The
current-user queue remains a separate member-scoped observation. This schema
supports the candidate derivation but does not establish live account identity,
exclusive control of the team, shared filesystem semantics or approval. The
offline [account-binding primitive](../../scripts/qi_tuna_account_binding.py)
derives a keyed team digest from a supplied member record and shared secret;
it does not authenticate the record, generate or protect the secret, or verify
that another host uses the same secret and marker namespace. It validates the
retained member schema's user ID and role fields, but does not bind that user
to the OAuth subject or prove access to team-wide transaction history. Secret custody,
aliases and cross-host behavior still need implementation, tests and an
owner-approved trust boundary.

## Ordered local and provider boundary

1. Validate the packet, approval identity, current source and analyzer hashes,
   exact case envelope, source paths and independent review receipts. Reject an
   existing consumption marker or an unresolved earlier attempt. Reserve an
   exclusive run location and preserve the exact approved inputs. A symbolic or
   hard-link substitution, conflicting attachment, invalid timestamp, missing
   input or changed digest fails closed before provider resource creation.
   Resolve each path beneath a trusted root with descriptor-relative,
   no-follow operations; verify regular-file type, owner, link count and
   inode/device identity on opened descriptors. Publish exact checked copies to
   a trusted run directory without overwriting prior evidence. A fresh isolated
   process must load the packet-bound producer bytes from the verified snapshot,
   bypass cached bytecode, and reject unbound imports on the dispatch path. The
   packet must identify the interpreter and dependencies and the trusted launch
   boundary; hashing a module's pathname after import does not identify the code
   already loaded. An unverified launch or dependency fails closed. The claimed
   exclusivity and fsync guarantees apply only to a reviewed local filesystem
   whose semantics meet those operations.
2. Record a UTC initiation horizon, Linux boot identity and suspend-aware
   elapsed-time boundary before attempting the account submission lock.
   Acquire the lock nonblocking with bounded waiting; each wait checks both
   the approved UTC and boot-time boundaries. Lock wait and all read-only
   admission requests count against freshness and the initiation horizon. A
   changed boot identity, backward wall-clock movement, suspend or clock-domain
   disagreement that cannot be adjudicated makes the attempt inadmissible.
3. Under the lock, fetch current backend type, instance status and heartbeat,
   current-user queue, account transaction information and reviewed public
   policy pages. Compare the backend's identity, simulator status, raw-data
   support, capacity, shots, execution limit, batch and queue limits, gate set
   and compiler configuration against the approved packet. Reject disabled,
   unavailable, stale, malformed, incompatible or charged observations. The
   admission record retains sanitized data and timestamps, not account secrets.
   Page-number pagination and concurrent account activity do not supply an
   atomic ledger snapshot. Use a provider-supported stable snapshot if one is
   verified; otherwise state and approve the residual non-atomic observation
   boundary, test insertions, deletions and queue changes, and refuse any
   inconsistent or incomplete pages. Other hosts can change the queue after a
   local observation. Provider policy and billing may change after observation;
   no local check guarantees a future charge will remain zero.
4. Before the first resource-creation request, atomically create an exclusive
   account-scoped marker that binds the approval identity, packet, manifest and
   attempt. Flush the marker and its containing directory. A pre-existing,
   truncated, unreadable or malformed marker is consumed or ambiguous, never
   reusable. Any crash after marker creation spends the approval even when the
   outcome cannot be established; reconcile read-only and obtain a new case and
   approval for any later attempt. Do not infer that no request was sent from
   an absent or incomplete local result record.
5. Use a new, case-specific lock-owning adapter around the deadline-aware
   helper's private `_submit()` entry point, with the exact approved manifest
   digest and a case-specific admission callback. The adapter alone acquires,
   verifies and releases the lock and invokes `_submit()` inside that lexical
   boundary. The packet binds the exact helper bytes and the adapter's tests
   exercise the private interface. The helper's public `submit()` acquires the
   lock itself and must not be called while the guard holds it: a second open
   and `flock` blocks. This design chooses the adapter and does not claim that
   the existing helper has a public lock-aware API.
   The callback must run after the helper's fresh backend and queue reads and
   before resource creation, and refuse stale or changed observations. The
   helper reads each source into memory after checking its hash, decodes UTF-8,
   and sends text in JSON. Require canonical UTF-8 and confirm stored source
   bytes through provider readback; the request does not transmit the original
   byte blob directly. A fresh check of a pathname by itself does not prevent
   later replacement. The existing helper uses a monotonic deadline and cannot
   by itself guarantee the suspend-aware boundary, especially across an
   authenticated retry. The guard needs a reviewed transport that checks the
   approved clock boundary before every request and retry, or fails closed
   without retry. An in-flight request can complete after its initiation
   deadline. Authentication refresh has its own documented boundary. The
   inherited client returns parsed `response.json()` values; a reviewed
   readback transport must retain response-body bytes and request metadata
   before decoding if duplicate-key evidence is required. It must distinguish
   decoded HTTP response bodies from original wire bytes.
6. Retain the checkpointed resource identities, submission, ordered raw shots,
   result metadata, source and batch readback and transactions before evaluating
   the frozen terminal screen. Missing, incomplete, charged or inconsistent
   evidence stops the case. A failed or ambiguous request is never retried or
   replaced under the same approval. A lost response during project, batch,
   algorithm, commit, file or job creation can leave the resource identity
   unknown: the attempt remains blocked unless the provider supplies a sound
   idempotency or exact read-only discovery mechanism. Existing reconciliation
   can recover a fully checkpointed batch after an ambiguous enqueue; it does
   not recover every earlier lost creation response. Account-wide ledger
   reconciliation and late charges require separate checks after collection.

The account lock coordinates compliant local processes; it cannot prevent an
independent client or another host from using the account. Filesystem mode and
exclusive creation do not establish safety against a malicious process with the
same user identity. The guard's threat model must name those trust boundaries.
The generic CLI remains callable, so policy and operator discipline must also
prohibit bypassing the guard for this case.

The offline [consumption-marker primitive](../../scripts/qi_tuna_consumption_marker.py)
creates an exclusive local marker keyed by supplied account and approval-event
digests, binds the packet digest in its content, and syncs the file and parent
directory. The primitive duplicates the supplied descriptor and checks that it
names a directory; the caller must keep the borrowed descriptor stable until
duplication and establish directory identity, ownership and filesystem
semantics. The primitive does not authenticate the digests, coordinate other
hosts, or grant approval. On any write or sync failure the caller must quarantine the attempt
across restart: a failed sync cannot prove the marker will survive a crash.

The offline [bounded-lock primitive](../../scripts/qi_tuna_bounded_lock.py)
uses a caller-supplied unlocked file descriptor, nonblocking local `flock`, a
`CLOCK_BOOTTIME` wait limit and a caller-supplied clock check before and after
acquisition. The caller must establish descriptor identity, lock ordering,
namespace and filesystem semantics, and must check the approved boundary at
every later request and retry. The callback must use bounded local clock
sampling; a blocked callback can exceed the wait limit while holding the lock.
The adapter must retain exclusive ownership of the descriptor through the
context and control close, reuse, duplication and inheritance. A preemption
between the final lock check and context entry makes the subsequent per-request
check essential. The primitive does not create a cross-host lock or protect
against an independent client that ignores the lock.

The offline [clock contract](../../scripts/qi_tuna_dispatch_clock.py) checks
caller-supplied UTC, suspend-aware boot-time and boot-identity observations. It
rejects expired bounds, changed boot identity, backward readings, excessive
clock disagreement and malformed numbers, and latches a refusal for the
attempt. The contract does not acquire Linux clock readings, choose an approved
tolerance, acquire a lock, guard a request or attest the caller's observations.
The eventual adapter must supply and validate those boundaries and test every
request and retry; passing the standalone clock tests does not admit dispatch.
The contract assumes one serialized owner in one process and keeps no durable
restart history. Normal attribute assignment or deletion cannot change its
bounds or clear its refusal; Python introspection and a hostile process remain
outside that boundary. UTC and boot time both advance during suspend, so the two-clock
contract cannot detect a short suspend. The adapter needs an independently
reviewed suspend detector if the approved rule refuses every suspend, as well
as durable attempt disposition and refusal after restart.

For a possible suspend check, bracket each `CLOCK_BOOTTIME` sample with
`CLOCK_MONOTONIC` samples. The boot-minus-monotonic offset lies between
`boot - monotonic_after` and `boot - monotonic_before`, subject to the clock and
sampling assumptions recorded in the packet. Compare the resulting interval
with the initial offset interval and retain the raw readings and their boot
identity. A lower bound on offset growth above the approved tolerance supports
a suspend observation; overlapping intervals leave smaller changes unresolved.
The adapter must refuse if the approved clock-uncertainty or offset-growth
limit cannot be established. A finite-width sample cannot prove the absence of
every arbitrarily short suspend. A case that requires that stronger claim needs
an independently supported mechanism; the two-clock contract cannot supply it.
The packet must specify how UTC sampling, syscall failure, boot change and
restart interact with these bounds before an implementation uses the rule.

## Offline evidence required before approval

Tests must use a fake provider transport and prove that no resource-creation
call occurs for changed source or packet bytes, absent or misbound approval,
stale admission, incompatible backend, full queue, changed policy, nonzero
charge, expired deadline, duplicate invocation or malformed marker. Concurrent
attempts must produce at most one successful consumption. Fault injection must
cover interruption before and after marker creation and each resource request,
including an accepted request with a lost response. Tests must verify exact
request ordering, immutable checked source bytes, enqueue recovery or durable
blocked ambiguity, and sufficient evidence for read-only reconciliation on
failed paths. A clean local
test or a self-consistent approval file does not prove provider availability or
owner approval.

An independent review must inspect the final guard, packet and tests. Only then
can fresh read-only admission and an explicit owner decision address the QX
case and the separate QX-to-Tuna end-to-end policy gap. A successful QX screen
cannot approve the Tuna case or resolve Tuna's intermediate readout mapping.
