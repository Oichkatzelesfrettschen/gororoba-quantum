Artifact: staged Python identity-binding primitive and tests, reviewed against the staged account/JSON helpers and current working-tree acquisition design. Fields: authentication boundaries, keyed pseudonyms, strict JSON parsing, and refresh-time identity continuity.

No FATAL finding exists in the standalone primitive. Two SERIOUS integration limitations prevent treating it as an acquisition guard.

## Findings

1. **SERIOUS — coherent user or member changes can produce an identical binding.**

   [SubjectBinding](../../../scripts/qi_tuna_subject_binding.py) retains only `subject_digest` and `team_digest`. `bind_subject` validates `user.id`, `member.id`, and `member.user_id`, then discards those identities. [account_digest](../../../scripts/qi_tuna_account_binding.py) deliberately hashes only `team_id`.

   Consequently, a coordinated replacement of `user.id`, `member.user_id`, and `member.id` passes and returns identical digests when `oidc_sub` and `team_id` remain unchanged. A member-role change also leaves both digests unchanged. The account tests explicitly establish that distinct members and users in one team share the team digest at [test_qi_tuna_account_binding.py:9](../../../tests/scripts/test_qi_tuna_account_binding.py).

   This conflicts with the acquisition design’s requirement to verify the effective member after every credential reload and stop on an identity change at [tuna-destination-sequential-evidence-case.md:204](../../../docs/design/tuna-destination-sequential-evidence-case.md).

   Remedy: retain separate keyed user and member digests under distinct domains, or make the future adapter compare the exact private user ID, member ID, role, subject, and team. Keep the team-only digest for its intended shared approval namespace.

2. **SERIOUS if composed as acquisition admission — refresh changes are distinguishable but never refused.**

   `bind_subject` is stateless and accepts a coherent changed subject. The test deliberately changes the subject and user record together and expects a new digest at [test_qi_tuna_subject_binding.py:27](../../../tests/scripts/test_qi_tuna_subject_binding.py). Repository search found only test callers; no acquisition adapter compares an approved binding before the next request.

   The working design assigns that refusal to a future adapter at [tuna-destination-sequential-evidence-case.md:242](../../../docs/design/tuna-destination-sequential-evidence-case.md) and still lists live admission as required work at [line 511](../../../docs/design/tuna-destination-sequential-evidence-case.md). The documentation therefore remains honest, but the staged helper cannot yet enforce the design.

   Remedy: pin the approved full identity binding, reacquire authenticated evidence after every token reload or retry, and refuse any subject, issuer, user, member, role, or team transition before another provider request.

3. **SLOPPY — the principal test overclaims “rejects each changed identity.”**

   The name at [test_qi_tuna_subject_binding.py:9](../../../tests/scripts/test_qi_tuna_subject_binding.py) promises more than the test proves. Its rejection table changes one side of a relationship and creates an inconsistent record. It does not exercise coherent user/member replacement, role transition, or stateful refresh refusal. Its coherent subject change is accepted.

   Remedy: rename the test around snapshot consistency and digest separation; put identity-transition rejection in adapter-level tests.

4. **SLOPPY test-evidence gap — Unicode behavior is stronger than the direct coverage.**

   The implementation rejects malformed UTF-8 JSON bytes, and the subject’s explicit UTF-8 encoding rejects unpaired surrogates. Exact decoded-string comparison appropriately keeps normalization variants distinct for an opaque subject identifier. The staged tests cover a caller-supplied lone surrogate, but omit malformed JSON UTF-8, valid non-ASCII subjects, escaped-versus-literal equivalent subjects, and escaped duplicate keys.

   The generic parser also does not recursively prohibit escaped lone surrogates in ignored string fields. That does not permit subject spoofing because `oidc_sub` must equal an encodable subject, but it limits any broader claim of Unicode-scalar-clean JSON.

## Sound properties

- Exact `type(value) is int` checks reject Python’s `bool`/`int` alias for user, member, and team identifiers. Both activity fields require the singleton `True`; inactive records and integer `1` are rejected.
- [_json_object](../../../scripts/qi_tuna_source_association.py) rejects duplicate keys recursively after escape decoding, `NaN`, infinities, overflow-to-infinity floats, malformed UTF-8, oversized bodies, and non-object roots.
- Subject and team HMACs use SHA-256 with distinct, versioned, provider-scoped domains. Each construction has one variable tail, so concatenation is unambiguous.
- Returned values omit raw subject, user, member, and team identifiers. They are stable, linkable pseudonyms whose privacy depends on the documented high-entropy 32-byte secret remaining private.
- The subject digest binds the Quantum Inspire API authority and `sub`, not the token’s actual issuer or audience. This is sound only when the caller pins one approved issuer and audience; accepting multiple issuer contexts would require binding the issuer as well.

## JWT and provider-admission boundary

No staged path validates a JWT or establishes provider admission. The code does not parse a token, verify a signature, resolve keys, constrain algorithms, check issuer/audience/time claims, perform provider I/O, authenticate response bytes, prove pagination completeness, or establish uniqueness.

The phrases “caller-verified” and “already authenticated” are preconditions, and the module explicitly disclaims authentication and admission at [qi_tuna_subject_binding.py:1](../../../scripts/qi_tuna_subject_binding.py). The working design likewise describes token validation prospectively and says installed libraries establish neither a served token contract nor a verified identity at [tuna-destination-sequential-evidence-case.md:235](../../../docs/design/tuna-destination-sequential-evidence-case.md).

An authenticated provider response would establish only the response observed through that authenticated request. It would not by itself prove token-to-user semantics, complete pagination, unique subject mapping, refresh continuity, provider authorization, or acquisition admission.

## Staged SHA-256

Computed from the staged bytes with `git show :<path> | sha256sum`:

- `scripts/qi_tuna_subject_binding.py`: `29173067c1ecd98df5a7ea70ad47c2f22ae633fdbfba1527a20736a3a6832e8f`
- `tests/scripts/test_qi_tuna_subject_binding.py`: `0c1b84986aef8b82486e83f29d86411b987891166ecac40bfbf16d4a559a3a91`
- Reviewed dependency `scripts/qi_tuna_account_binding.py`: `0ff51eb43ef9f71266bbd17abe8879e833833d3b2f155e2ae464c448714bb967`
- Reviewed parser dependency `scripts/qi_tuna_source_association.py`: `4abd49b146891fcb3ab374e20bd2dc978025046f7381b191923e315e35ab75be`

No tests, credentials, network operations, provider actions, uploads, draws, messages, or repository writes were performed.
