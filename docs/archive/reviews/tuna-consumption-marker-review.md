## Verdict

The staged primitive is a defensible local fail-closed tombstone, not an approval guard. Its account-plus-approval key correctly prevents one approval event from selecting a new marker merely by changing the packet. One serious descriptor-lifetime gap and one serious test-evidence gap remain. Authentication, crash recovery, cross-host exclusion, filesystem semantics, and provider idempotency remain unresolved exactly as the current design largely acknowledges.

I read both staged blobs and the complete current working-tree design. I ran no tests, linters, network operations, credential reads, provider operations, jobs, uploads, draws, messages, or repository writes.

## Findings

1. **SERIOUS — The borrowed directory descriptor has an unstated close-and-reuse race.**

   [qi_tuna_consumption_marker.py:19](../../../scripts/qi_tuna_consumption_marker.py) verifies the object currently occupying the descriptor number. Lines 38 and 47 later reuse that integer for `openat` and directory `fsync`. Another thread can close the descriptor and reuse its number between those operations. The marker can consequently be created relative to a different directory, or the wrong directory can be synchronized.

   The concurrency test keeps the descriptor open until both workers finish, so [test_qi_tuna_consumption_marker.py:23](../../../tests/scripts/test_qi_tuna_consumption_marker.py) does not exercise this boundary.

   Remedy: specify exclusive borrowed-descriptor lifetime, duplicate the descriptor into private ownership at entry, validate and use only the duplicate, and add deterministic descriptor-substitution coverage. Authentication of a descriptor does not freeze the process descriptor table.

2. **SERIOUS — The tests do not preserve several central protocol guarantees.**

   The staged tests establish:

   - The same supplied account and approval collide even when the packet changes.
   - Two same-process threads obtain one creation and one `FileExistsError`.
   - An injected file or directory `fsync` error leaves the marker consumed in the still-running filesystem namespace.

   They never inspect the marker name, exact JSON bytes, packet/account/approval fields, mode, or file type. A regression that removed `packet_sha256` from the payload or weakened `0600` would pass every staged test. A domain or key-derivation change also lacks a known-vector test, allowing durable markers created by different versions to occupy different names.

   Missing static contracts include malformed and symlink entries, partial and zero-progress writes, descriptor reuse, distinct account and approval inputs, subprocess contention, and exact file-before-directory synchronization order. Actual crash durability cannot be established by these mocked `fsync` tests.

3. **SLOPPY — The design should describe directory validation more exactly.**

   [tuna-qx-exact-dispatch-guard.md:137](../../../docs/design/tuna-qx-exact-dispatch-guard.md) says the primitive does not “validate the directory.” The code does verify that the descriptor currently names a directory. The missing guarantees are directory identity, ownership, descriptor lifetime, namespace integrity, and filesystem semantics. The document should name those absent guarantees rather than using “validate” for several different claims.

4. **SOUND — Approval reuse and key derivation are locally correct.**

   [qi_tuna_consumption_marker.py:23](../../../scripts/qi_tuna_consumption_marker.py) hashes a domain separator followed by two fixed-width values: account digest and approval-event digest. Fixed widths remove concatenation ambiguity. Excluding the packet digest from the filename is intentional and correct: changing the packet cannot create a new consumption key. The canonical JSON content records all three supplied digests.

   This guarantee applies only to the supplied bytes. A caller can manufacture a new approval digest, alias one account under another digest, or supply a packet digest unrelated to any packet. The primitive authenticates none of them.

5. **SOUND, within a trusted local-filesystem boundary — Creation and failure behavior fail closed.**

   `O_CREAT|O_EXCL` reserves one name atomically where the filesystem implements the required semantics. `O_NOFOLLOW` prevents following an existing final-component symlink; any existing regular file, hard link, symlink, truncated marker, or malformed marker causes refusal. The descriptor-relative fixed filename avoids path traversal.

   The JSON is not atomically published as a complete object: another observer can see an empty or partial file after exclusive creation. The design’s rule that every incomplete marker remains consumed makes that exposure safe.

   A successful return follows complete writes, file `fsync`, and directory `fsync`. A post-creation error leaves a live marker that blocks reuse. A crash following a failed or incomplete synchronization can erase that marker, so durable quarantine must exist outside this function before reuse can be prohibited across restart.

## Local guarantee versus unresolved boundary

| Surface | Primitive guarantee | Still unresolved |
|---|---|---|
| Approval reuse | Same supplied account plus approval selects one name, independent of packet | Authentic approval receipt, canonical event identity, and protection against caller-selected digests |
| Account binding | Supplied account digest affects name and payload | Authenticated account derivation, aliases, multiple homes, and shared-account hosts |
| Packet binding | Successful payload records the supplied packet digest | Trusted hashing of exact packet bytes; manifest and attempt binding must be transitive through the packet |
| Atomicity | One creator wins within one conforming namespace | Complete JSON is published incrementally; hostile namespace writers can unlink or replace it |
| Durability | Successful return follows file and parent-directory `fsync` | Filesystem/hardware semantics and failed-sync crash recovery |
| Symlinks and links | Existing final-component entries fail closed | Directory provenance, descriptor reuse, post-create unlink/replacement, and hostile same-user processes |
| Concurrency | Local `O_EXCL`; staged test covers two threads | Separate directories, hosts, noncompliant clients, and distributed-filesystem semantics |
| Provider | None | Quotes, billing changes, queue races, ambiguous accepted requests, idempotency, and lost-response recovery |

The current design correctly retains these provider and multi-host blockers at [tuna-qx-exact-dispatch-guard.md:75](../../../docs/design/tuna-qx-exact-dispatch-guard.md), [line 118](../../../docs/design/tuna-qx-exact-dispatch-guard.md), and [line 130](../../../docs/design/tuna-qx-exact-dispatch-guard.md). The primitive therefore supplies one useful local mechanism but does not make the proposed dispatch admissible.

## Exact staged SHA-256 hashes

Computed from the Git index blobs:

- `scripts/qi_tuna_consumption_marker.py`: `07423bf464e5ba66281d1c21f6187a4a6fa847897371a504620118e1980c10fb`
- `tests/scripts/test_qi_tuna_consumption_marker.py`: `f03f010e6437f504d8d894d134e4a3f1cc54ef3d7cc0630fcf95bda11f9f91b8`

The scoped before-and-after observations remained `A` for both staged files and `AM` for the design document. Both Python worktree files had zero unstaged diff relative to their indexed blobs.
