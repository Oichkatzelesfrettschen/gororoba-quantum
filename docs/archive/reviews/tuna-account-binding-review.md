Artifact: staged Python security primitives for team-derived HMAC namespacing and single-use local approval markers. The relevant fields are cryptographic domain separation, authorization, filesystem atomicity, and distributed account coordination. I read the complete staged blobs, their staged integration references, the final staged design, and the retained OpenAPI schema.

## Findings

1. **FATAL — the staged tree does not implement a dispatch guard.**

   The staged index contains no runtime caller of `account_digest()` or `consume()` outside tests. The design itself calls for a new lock-owning adapter at [tuna-qx-exact-dispatch-guard.md:116](../../../docs/design/tuna-qx-exact-dispatch-guard.md) and acknowledges that the generic submitter remains callable at [line 153](../../../docs/design/tuna-qx-exact-dispatch-guard.md). The existing submitter proceeds from mutable local inputs to `Client()` and provider reads at [qi_platform.py:880](../../../scripts/qi_platform.py), then creates the first remote project at [line 961](../../../scripts/qi_platform.py) without either primitive.

   Consequently, every current generic submission path bypasses the account namespace, approval-consumption marker, raw-response checks, transaction admission, and cross-host rules.

   Remedy: implement the case-specific adapter, make it the sole permitted path for the bound manifest, and place authenticated approval validation, account binding, the durable marker, and fresh admission checks before the first resource-creation request.

2. **SERIOUS — a self-consistent member object is mistaken for authenticated account identity.**

   [qi_tuna_account_binding.py:16](../../../scripts/qi_tuna_account_binding.py) accepts a caller-supplied member ID and dictionary. Lines 24–33 check only `id`, `team_id`, and `is_active`. The retained OpenAPI `Member` schema additionally requires `user_id` and `role`; its `/members/{id}` operation is bearer-authenticated lookup by a supplied path ID, not an attestation that the returned member represents the OAuth subject ([openapi.json:1](../../../docs/notes/quantum_inspire/api/openapi.json), JSON pointers `/paths/~1members~1{id}` and `/components/schemas/Member`).

   Provider resources, meanwhile, use `Client.member_id` loaded from the SDK configuration at [qi_platform.py:335](../../../scripts/qi_platform.py). Nothing equates that member with the record supplied to `account_digest()`.

   Reachable primitive-level bypass: supply another self-consistent active member/team record; the HMAC changes, so [qi_tuna_consumption_marker.py:35](../../../scripts/qi_tuna_consumption_marker.py) selects a fresh marker name for the same actual client and approval. Provider-level reachability remains unestablished because the adapter is absent and live access was prohibited.

3. **SERIOUS — authorization identity is freely selectable.**

   [qi_tuna_consumption_marker.py:18](../../../scripts/qi_tuna_consumption_marker.py) accepts any three 32-byte strings. Changing `approval_digest` creates a new filename; no code verifies a signed receipt, trusted operator provenance, account binding, or packet-to-approval relationship. Tests use arbitrary repeated bytes at [test_qi_tuna_account_binding.py:74](../../../tests/scripts/test_qi_tuna_account_binding.py).

   The primitive accurately says that it “grants no approval,” but the staged integration supplies no authorization gate around it. A digest is an identifier, not evidence that anybody approved anything.

4. **SERIOUS — secret rotation, account aliases, and directory choice renew the namespace.**

   The account primitive enforces secret length only at [qi_tuna_account_binding.py:20](../../../scripts/qi_tuna_account_binding.py). Any 32-byte value—including low-entropy repeated bytes—passes. The test explicitly confirms that changing the secret changes the namespace at [test_qi_tuna_account_binding.py:56](../../../tests/scripts/test_qi_tuna_account_binding.py). Changing the marker directory creates another independent namespace.

   Therefore the same provider team and approval can obtain a fresh marker through:

   - a different local account alias with another secret;
   - secret loss or rotation;
   - another home directory, container, or host;
   - another filesystem copy of the marker directory.

   Exact host equality is fail-closed for aliases, but passing the canonical host string does not prove where the member response originated. The implementation needs one durable secret version and marker root per provider team, an explicit alias map, and a cross-host coordination mechanism or a refusal whenever those invariants cannot be demonstrated.

5. **SERIOUS — duplicate-key rejection and snapshot freshness exist only as caller assumptions.**

   The primitive receives an already-decoded `dict`; duplicate keys have already disappeared. The existing client returns `response.json()` at [qi_platform.py:400](../../../scripts/qi_platform.py), while the design explicitly requires retaining raw response bytes before decoding at [tuna-qx-exact-dispatch-guard.md:137](../../../docs/design/tuna-qx-exact-dispatch-guard.md).

   The account-binding tests use partial objects that are invalid under the retained `Member` schema because they omit `user_id` and `role`. The member schema also supplies no timestamp, revision, or ETag. A previously active record remains acceptable after deactivation or team reassignment.

   Remedy: use a raw-body transport with duplicate-key rejection, validate the complete schema, bind method/URL/status/body digest and canonical host, and fetch or revalidate membership under the dispatch lock immediately before marker creation.

6. **SERIOUS — team scope, member scope, queue scope, and transaction scope remain unreconciled.**

   The HMAC collapses every active member of a team into one namespace; the test deliberately proves that at [test_qi_tuna_account_binding.py:9](../../../tests/scripts/test_qi_tuna_account_binding.py). Provider resource ownership and the queue check are member-scoped, while transactions contain both `team_id` and `member_id`.

   The retained OpenAPI `Role` description says regular members cannot inspect the team’s transaction history. Thus a team-derived namespace does not imply that the submitting member can obtain a complete team-wide transaction snapshot. The retained observation of one `individual_user` team with one member in [usage.md:3](../../../docs/notes/quantum_inspire/usage.md) is historical evidence, not a durable invariant.

   The authorization object must explicitly state whether approval is team-wide or member-specific and bind both team and submitting member identities. Admission must either obtain provider-supported team-wide state with sufficient authorization or narrow its claims to the observable member boundary.

7. **SERIOUS — local marker durability does not close the provider transaction boundary.**

   Inside one reviewed filesystem, marker creation precedes local success and ambiguous files remain consumed. Across a remote POST, however, no atomic transaction exists. The design correctly requires permanent refusal after a lost response or uncertain persistence, but no staged adapter or durable quarantine mechanism implements that rule.

   An `fsync` failure can leave an entry visible during the current boot yet absent after a crash. The module’s instruction that the caller quarantine the attempt across restart is necessary, but no caller or second durable authority exists.

## Sound portions

- The HMAC message encoding is sound: a domain-separated canonical production host followed by one positive integer’s canonical ASCII decimal representation is injective for the accepted input class. HMAC-SHA-256 is appropriate for hiding an enumerable team ID when the 32-byte key is genuinely random and protected.
- Exact host matching rejects aliases rather than merging them accidentally.
- The marker key concatenates two fixed-width 32-byte values, so it has no concatenation ambiguity.
- Omitting `packet_digest` from the filename is correct: the same account and approval must collide even when a caller substitutes another packet.
- `os.dup`, descriptor-relative `O_EXCL | O_NOFOLLOW`, mode `0600`, complete-write looping, and file-plus-directory `fsync` provide a defensible single-filesystem primitive under its stated trust assumptions.

## Exact staged SHA-256 hashes

- `scripts/qi_tuna_account_binding.py`: `ef3a0fd9e475d1aa4300cd034237dd6620b5eeed651a6e41552c16945904570a`
- `tests/scripts/test_qi_tuna_account_binding.py`: `855ab5e355c94a0af8cb07bd3ed5dbb1706b61291e80cb51c57a64f1a5128a38`
- `scripts/qi_tuna_consumption_marker.py`: `dbaf93d5db016d483a22066ec0224e81ea6de9aff066f54655b747fc71534a61`

Additional integration surfaces:

- `tests/scripts/test_qi_tuna_consumption_marker.py`: `cb8a431c7f89f3d2c062e50f7f2a3a777ca3d027d16c244286d654630ce5c6cc`
- `docs/design/tuna-qx-exact-dispatch-guard.md`: `8913cd47a8f769a3aef8b93122dd678c2b5b2614c01246f7bde0e42841414f7a`
- Retained OpenAPI: `714f66165611b38842dfe3497bb7f1ea818c9df756b3ed87ff128c838cac185f`, matching its manifest.

The staged design changed during the read-only review from Git blob `f484108…` to `286822d…`; the final review uses blob `286822d8996393a2393655c7d66645292b42524d`. The three requested hashes remained stable. Final measurements recorded HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`, identical worktree/index bytes for the five listed target files, and a clean targeted `git diff --cached --check`.

No tests, network requests, credentials, provider calls, jobs, uploads, draws, messages, or repository writes occurred.

Verdict: the two primitives are locally reasonable, but they do not yet constitute an authorization or dispatch guard. The decisive missing artifact is the lock-owning adapter that binds the actual OAuth member and team, authenticated approval receipt, stable cross-host namespace, raw duplicate-rejected response, transaction boundary, and marker creation to the first provider request. Until that adapter and its failure-path evidence exist, the QX case remains unapproved and directly bypassable through the generic submitter.
