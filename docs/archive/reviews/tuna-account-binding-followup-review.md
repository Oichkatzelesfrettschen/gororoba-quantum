Artifact: staged Python security primitive plus pytest contract. I read both complete staged blobs, the design and archived review, the local marker implementation/tests, and retained OpenAPI `Member`, `Role`, and `Transaction` schemas.

## Findings

1. **SERIOUS — the archived review is stale against the current staged blobs.**

   [tuna-account-binding-review.md:15](../../../docs/archive/reviews/tuna-account-binding-review.md) says the function omits `user_id` and `role`; the current staged implementation validates both at [qi_tuna_account_binding.py:24](../../../scripts/qi_tuna_account_binding.py). The review also says test objects omit those fields at [line 44](../../../docs/archive/reviews/tuna-account-binding-review.md), while every nominal current fixture supplies them.

   Its recorded SHA-256 hashes at [lines 70–73](../../../docs/archive/reviews/tuna-account-binding-review.md) also differ from the current index hashes reported below.

2. **SERIOUS for dispatch readiness, but explicitly outside the primitive’s local claim — authenticated account binding remains absent.**

   The function accepts caller-supplied `member_id`, decoded member data, and secret material. Exact agreement between the path ID and body ID proves internal consistency only. The retained `/members/{id}` operation requires a bearer token but accepts a caller-selected path ID; neither that operation nor the `Member` schema attests that `user_id` is the OAuth subject.

   The module accurately disclaims provider authentication at [qi_tuna_account_binding.py:1](../../../scripts/qi_tuna_account_binding.py), and the design acknowledges the missing OAuth-subject binding at [tuna-qx-exact-dispatch-guard.md:59](../../../docs/design/tuna-qx-exact-dispatch-guard.md).

3. **SOUND — all required retained `Member` fields receive strict validation.**

   The retained schema requires `id`, `team_id`, `user_id`, `role`, and `is_active`; `Role` permits exactly `"member"` and `"admin"`. Lines 24–39 enforce:

   - exact `int` types and positive values for all three identifiers;
   - equality between the supplied and observed member IDs;
   - exact `str` type and the two retained roles;
   - the singleton Boolean value `True` for activity.

   Exact `type(...) is int` correctly rejects Python booleans. The OpenAPI schema permits additional properties by default, so accepting extra dictionary fields does not contradict it.

4. **SOUND within its named boundary — the keyed namespace has stable team identity.**

   [qi_tuna_account_binding.py:40](../../../scripts/qi_tuna_account_binding.py) computes HMAC-SHA-256 over a domain-separated canonical host and positive team ID. With one unchanged 32-byte secret, all members of one team select the same digest while member ID, user ID, and role changes do not alter it.

   Stability ends when the shared secret or marker root changes. The primitive validates secret representation and length, not entropy, provenance, version, protection, distribution, rotation, alias handling, or cross-host custody. The design correctly leaves those obligations open at [lines 54–68](../../../docs/design/tuna-qx-exact-dispatch-guard.md).

5. **SOUND locally — marker integration selects one single-filesystem consumption name.**

   [test_qi_tuna_account_binding.py:75](../../../tests/scripts/test_qi_tuna_account_binding.py) derives the same account digest through two members of one team and supplies both to `consume()`. The marker name uses account and approval digests, and exclusive creation makes the second local attempt collide.

   The separate marker test also statically covers packet substitution under the same approval. This establishes only the reviewed directory and filesystem boundary. It establishes neither shared cross-host storage nor authenticated approval.

6. **SERIOUS for the eventual guard — freshness and team-wide transaction visibility remain unimplemented.**

   The account function accepts a previously decoded snapshot and performs no acquisition or freshness check. The retained `Member` schema contains no timestamp, revision, or ETag.

   The retained `Role` description says administrators can inspect team transaction history while regular members cannot. Nevertheless, the namespace intentionally accepts both roles. A regular member’s successful local derivation therefore supplies no evidence of complete team-wide transaction visibility. The retained `Transaction` schema separately records `team_id` and nullable `member_id`; the eventual adapter must reconcile those scopes.

7. **FATAL to any claim that the staged tree already guards dispatch — no production integration exists.**

   A staged-index call-site search found no runtime caller of `account_digest()` or `consume()` outside their definitions and tests. Fresh admission, OAuth identity, shared-secret custody, transaction reconciliation, marker creation, and the first provider write are not joined by an adapter. The design itself says the generic CLI remains callable at [tuna-qx-exact-dispatch-guard.md:155](../../../docs/design/tuna-qx-exact-dispatch-guard.md).

8. **SLOPPY — the public type annotation overstates accepted inputs.**

   `account_digest()` advertises `Mapping[str, object]` but rejects every mapping implementation except an exact built-in `dict` at [qi_tuna_account_binding.py:22](../../../scripts/qi_tuna_account_binding.py). Either the annotation should say `dict[str, object]`, or the runtime contract should accept mappings.

   The focused tests also omit several negative branches, including missing `id`, `user_id`, or `is_active`, zero `user_id`, non-string roles, and non-dictionary mappings. The implementation rejects those cases, but the tests do not independently earn every strictness claim.

## Exact current staged SHA-256

- `scripts/qi_tuna_account_binding.py`: `0ff51eb43ef9f71266bbd17abe8879e833833d3b2f155e2ae464c448714bb967`
- `tests/scripts/test_qi_tuna_account_binding.py`: `46976bfe9c7681777ba48056de9096bb60eb26e495221fbb1bd7c319bd51ca45`

Both digests remained identical across two consecutive reads of the index. The retained OpenAPI file hashes to `714f66165611b38842dfe3497bb7f1ea818c9df756b3ed87ff128c838cac185f`.

Verdict: the local schema validator, keyed team derivation, and marker composition are sound under their explicit caller-controlled assumptions. They do not provide authenticated OAuth-subject binding, freshness, team-wide transaction visibility, durable shared-secret custody, cross-host single use, or dispatch enforcement. No tests or external operations were run; the review used local, read-only inspection only.
