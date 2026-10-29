The staged private store is sound as a narrow, serialized local-filesystem primitive. It does not yet establish crash-safe scientific provenance or admission. I found four SERIOUS integration boundaries and no FATAL defect.

Reviewed artifacts span Python filesystem durability, concurrency, provenance, strict source/result association, and statistical evidence admission.

## Findings

1. **SERIOUS — a late persistence failure can leave a capture that the loader accepts.**

   `_write_exclusive()` writes complete bytes before file and directory `fsync` calls ([qi_tuna_private_readbacks.py](../../../scripts/qi_tuna_private_readbacks.py)). A failure from the final file sync, directory sync, or close can leave all nine expected entries readable. The loader checks the entry set and contents, but it has no successful-completion or failure-quarantine authority ([line 194](../../../scripts/qi_tuna_private_readbacks.py)).

   The staged failure test injects the first checkpoint sync failure, which necessarily leaves an incomplete set ([test_qi_tuna_private_readbacks.py](../../../tests/scripts/test_qi_tuna_private_readbacks.py)). It does not inject a final metadata sync or close failure after every expected name exists.

   The current design correctly declares cross-restart quarantine unimplemented ([tuna-destination-sequential-evidence-case.md](../../../docs/design/tuna-destination-sequential-evidence-case.md)). A durable attempt journal must mark the capture ambiguous before any request and require a terminal durable decision before scoring.

2. **SERIOUS — self-consistency is being used where authenticated capture provenance is required.**

   `_read_private()` validates each opened inode’s type, owner, permissions, link count, size, and pre/post metadata ([line 160](../../../scripts/qi_tuna_private_readbacks.py)). That is good per-file mutation detection.

   `load_private_readbacks()` accepts any internally consistent checkpoint, metadata, and bodies in the directory. It receives no externally authenticated checkpoint or capture digest, emits no directory identity or per-entry reader manifest, and provides no cross-file snapshot commitment. A coherent replacement containing another job under the same slot, arm, source, and manifest can therefore survive the local checks unless the caller supplies the promised external authentication.

   The integration test compares the reload with the still-resident in-memory capture ([test_qi_tuna_readback_collection.py](../../../tests/scripts/test_qi_tuna_readback_collection.py)). That proves same-process round-trip fidelity. It does not prove restart provenance, quarantine, or coherent-substitution resistance.

   The adjudication layer should bind an externally authenticated checkpoint digest, ordered receipt hashes, producer hashes, directory/capture identity, and reader observations.

3. **SERIOUS — validated provenance still collapses into an unbound score row.**

   The association decoder returns only `slot`, `arm`, `kind`, `early_ones`, and `terminal_ones` ([qi_tuna_source_association.py](../../../scripts/qi_tuna_source_association.py)). The integration test passes that row directly to `score_sequence()` ([test line 198](../../../tests/scripts/test_qi_tuna_readback_collection.py)).

   The score carries no job/result identity, checkpoint digest, assignment commitment, receipt hashes, observation boundary, account identity, charge evidence, or producer identity. A hand-written row is indistinguishable to the scorer.

   Request ordering and returned shot-list ordering are preserved. They do not establish physical acquisition order: the collector reads four mutable endpoints sequentially, and the scorer checks only contiguous caller-supplied slot numbers. The design accurately states that an adjudication record remains required ([design line 162](../../../docs/design/tuna-destination-sequential-evidence-case.md)).

4. **SERIOUS — unsuccessful attempts remain outside retention.**

   The transport emits a `Readback` only after HTTP 200, valid media type, and a complete bounded body ([qi_tuna_readback_transport.py](../../../scripts/qi_tuna_readback_transport.py)). An initial 401, partial or oversized stream, clock expiry, malformed envelope, and retention-callback failure leave no complete attempt receipt.

   The private store can therefore retain successful response receipts but cannot establish complete request chronology, retry history, or deadline adjudication. The working-tree design now specifies the missing intent and terminal-attempt journal precisely.

5. **SLOPPY — tests undersample the evidence-critical failure surface.**

   The staged tests cover exact-byte replay, simple body corruption, insecure directory mode, first-sync failure, and out-of-order calls. They omit:

   - final file or directory sync failure after all names exist;
   - close failure and exact file-before-directory sync ordering;
   - zero-progress and partial writes;
   - symlink, hardlink, special-file, owner, mode, and link-count substitutions;
   - borrowed-descriptor replacement after duplication;
   - concurrent writer/reader and cross-file substitution;
   - externally authenticated checkpoint/capture identity;
   - restart recovery and durable quarantine.

## Sound mechanisms

- Descriptor duplication prevents later reuse of the caller’s descriptor number from redirecting operations.
- Fixed descriptor-relative names eliminate traversal.
- `O_CREAT|O_EXCL|O_NOFOLLOW` blocks overwrites and final-component symlinks.
- File sync precedes directory sync on successful writes.
- Exact entry-set checks reject ordinary incomplete captures and unexpected files.
- Reader checks reject symlinks, non-regular files, foreign ownership, group/other access, hardlinks, oversized files, and detectable in-read mutation.
- Body SHA-256 values, strict metadata shapes, locators, queries, status, and media types are revalidated.
- The documentation explicitly withholds provider truth, observation timing, physical acquisition order, and scientific admission.

The privacy claim remains conditional. The code checks the leaf directory’s effective owner and mode bits. It does not inspect the parent path, mount/filesystem semantics, non-POSIX ACL models, or other processes sharing the same user identity. Root or equivalent privilege remains outside this boundary.

## Exact byte identities

Final observation: `2026-10-28T06:35:08Z`, HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`.

| Artifact | Staged SHA-256 | Working-tree SHA-256 |
|---|---|---|
| `scripts/qi_tuna_private_readbacks.py` | `4fb6db329b26db801ef871ab4bd083888296503e6c34e76e6ebea35d6ed69a66` | same |
| `tests/scripts/test_qi_tuna_private_readbacks.py` | `c152c48e6aad2d515ec55b1addf3c5742df81cbaf9b9ff4ae6354e1ec63a33b9` | same |
| `tests/scripts/test_qi_tuna_readback_collection.py` | `16411ec2ca498b13608303e3192c96bd4329e5851a5ee9d6b40dbc3aedfe0c91` | `defce53be3bb1d2c119db4369f05b3748238d5949c100825a3b058959fca336b` |
| `scripts/qi_tuna_readback_collection.py` | `42b825488bc60aee3745f9597b1b85b04c271e8e286efb21d32e40b67dc089df` | same |
| `scripts/qi_tuna_readback_transport.py` | `246672e6346a555ec67bb54f23e6be47157b357f36c451a6d8649766d2c65a00` | same |
| `scripts/qi_tuna_source_association.py` | `4abd49b146891fcb3ab374e20bd2dc978025046f7381b191923e315e35ab75be` | same |
| `scripts/qi_tuna_sequential_score.py` | `d344f69db36dcc79a6ce605686aa1dfcc488fa034ad09fdfab5c7d7f9d16611b` | same |
| `docs/design/tuna-destination-sequential-evidence-case.md` | `bea0efbe93d7ce86346a638c1e68358f2e0c956cb5128527d8eaa5023fbeb081` | `ec226298cd14453e2855387d0f3e4d4a90ca41298000a111f8a63c23fffaa45b` |
| `docs/design/tuna-readout-mapping-identifiability.md` | `ec84bc1e8a57705b891bf0fd2858c290608c9f89a6cd2ec90766fc4cc44e0ff8` | same |

The acquisition-design working tree changed during the review; the verdict incorporates the final `ec226…` bytes. The named staged target hashes, integration working-tree hash, and HEAD remained unchanged across the measured observations.

The review ran no tests, linters, network requests, credential reads, provider operations, jobs, uploads, draws, messages, or repository writes.
