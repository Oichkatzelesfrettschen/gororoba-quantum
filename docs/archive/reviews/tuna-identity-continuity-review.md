Artifact: complete staged Python identity-continuity implementation and pytest contract, reviewed against the staged subject-binding dependencies and current working-tree acquisition design. Fields: state-machine correctness, authentication boundaries, concurrency, and security composition.

## Findings

1. **SERIOUS — the approved identity is aliased, not immutable.**

   [IdentityContinuity.__init__](../../../scripts/qi_tuna_identity_guard.py) stores the caller’s `SubjectBinding` object directly. Although [SubjectBinding](../../../scripts/qi_tuna_subject_binding.py) uses `frozen=True`, it lacks `slots=True` and retains a mutable instance dictionary. A caller holding the approved object can replace `approved.__dict__["subject_digest"]` or another digest after validation. The guard then reads the changed baseline at [line 48](../../../scripts/qi_tuna_identity_guard.py), allowing a corresponding changed observation to pass without latching refusal.

   The guard’s custom `__setattr__` protects only assignments to the guard object; it does not protect the aliased binding. The tests never mutate the approved object after construction.

   Remedy: copy the four validated bytes into guard-owned slots during construction and compare only those snapshots. Adding `slots=True` to the frozen binding would remove the routine `__dict__` mutation surface, but hostile same-process code remains outside any enforceable Python object boundary.

2. **SERIOUS — some malformed exact-type observations escape the refusal latch.**

   `_validate()` first establishes exact `SubjectBinding` type, then directly retrieves all four attributes at [line 16](../../../scripts/qi_tuna_identity_guard.py). An exact-type instance with a missing attribute—possible through `SubjectBinding.__new__`, deletion from its instance dictionary, or concurrent mutation—raises `AttributeError`. `check()` catches only `ValueError` at [line 59](../../../scripts/qi_tuna_identity_guard.py), so `_refused` remains false and a later valid check can succeed.

   The working design’s claim that every malformed observation latches refusal at [line 259](../../../docs/design/tuna-destination-sequential-evidence-case.md) is therefore broader than the implementation. The test covers only a present but short `bytes` field.

   Remedy: make validation return one immutable four-digest snapshot and normalize structural access failures into the guard’s refusal exception before comparison. Add malformed exact-instance and post-construction mutation cases.

3. **SLOPPY — “one process” understates the actual serialization boundary.**

   The module header correctly says “one serialized process,” but the design says only “in one process.” There is no lock. Concurrent calls can both observe `_refused == False`; a valid check can complete while another call is still discovering a mismatch. Concurrent mutation can also occur between `_validate(observed)` and the later reread of the same attributes.

   The future adapter must hold one lock across credential reload, authenticated identity observation, guard check, and the provider request. The design already requires a serial account lock and live admission at [line 538](../../../docs/design/tuna-destination-sequential-evidence-case.md), so the repository does not presently claim that this helper supplies concurrency control.

## Sound properties

- `_validate()` requires the exact `SubjectBinding` class and exact `bytes` values of length 32. Subclasses, `bytearray`, and wrong-length digests are rejected.
- All four fields—subject, team, user, and member/role—are compared. The list comprehension evaluates all four constant-time `hmac.compare_digest` calls before `all()` decides.
- Normal mismatches and ordinary malformed fields raise `ValueError`, set `_refused` first, and make later calls fail.
- `bind_subject()` separates identity dimensions correctly: subject, team, user ID, and member ID plus role use distinct HMAC domains. Its dependency tests cover coherent user, member, and role changes. The guard test directly composes a coherent member-ID transition; a role transition follows the same changed `member_digest` path, though the guard test does not exercise that composition directly.
- Authentication limits are explicit. Neither helper validates a token signature, issuer, audience, validity time, provider-response authenticity, uniqueness, pagination, or observation freshness.
- Restart and cross-user limits are explicit. A new process receives a fresh, unrefused object; there is no durable latch, interprocess coordination, or shared-account exclusion.
- Provider admission remains separate. Identity continuity establishes neither backend availability, queue capacity, cost, approval, source binding, nor authorization to create a provider resource. The design still requires fresh admission and explicit user approval at [lines 541–545](../../../docs/design/tuna-destination-sequential-evidence-case.md).

## Exact byte provenance

Two consecutive staged reads produced identical SHA-256 values at HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`:

- `scripts/qi_tuna_identity_guard.py`: `543a25b4394bf8407214ce3e6370b0d309a26f62624b7f9541947d6574f4cf5f`
- `tests/scripts/test_qi_tuna_identity_guard.py`: `f048d860a52e993a42f0a48af78657bebd76e1d5da03a7559cb5f1d6661e0e21`
- `scripts/qi_tuna_subject_binding.py`: `243a2fcfa56783c57f8db79bdae38568b6400e5fb5b1c2138aa98ffed394b203`
- `tests/scripts/test_qi_tuna_subject_binding.py`: `bdf61e319ae830903202e551136663756247d5c6dbf2133a0380be1debc2522b`
- `scripts/qi_tuna_account_binding.py`: `0ff51eb43ef9f71266bbd17abe8879e833833d3b2f155e2ae464c448714bb967`
- `scripts/qi_tuna_source_association.py`: `4abd49b146891fcb3ab374e20bd2dc978025046f7381b191923e315e35ab75be`
- Staged acquisition design: `44b26d9ad18d7611a6f1efc8ed27a8f666c0ce4b70d75f9c3f4544a03f292367`
- Working-tree acquisition design containing the guard discussion: `9287b2ab7ca3f34a1e0bb02423410c9589cb2367cddc87cb02ef5ec46404652a`

Verdict: the four-field comparison and ordinary refusal latch are sound within a trusted, serialized call stream. The aliased approval baseline defeats the stronger immutable-state claim and should block treating the helper as complete. Even after that repair, authentication, durable restart refusal, concurrency, and provider admission must remain external adapter obligations.

No tests, linters, network access, credentials, provider operations, jobs, uploads, draws, messages, or edits were performed. Prior memory informed only the offline, evidence-first report shape; every technical conclusion above was rederived from the current bytes.
