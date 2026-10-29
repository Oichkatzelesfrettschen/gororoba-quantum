Artifact: staged Python identity-continuity guard and regression tests. Fields: state-machine correctness, authentication boundaries, concurrency, Unicode handling, and security composition. I read the complete staged blobs and dependencies; execution remained static.

## Residual findings

1. **SERIOUS if used as acquisition admission — authentication and authorization remain external.**

   [qi_tuna_identity_guard.py:1](../../../scripts/qi_tuna_identity_guard.py) assigns authenticated approval plus issuer/audience verification to the caller. The staged call graph contains definitions and tests but zero provider-request callers. The helper does not validate token signatures, validity times, authenticated readbacks, user approval, or request authorization.

   Remedy: the future adapter must authenticate fresh evidence, bind the approved case, verify issuer/audience, and run the guard immediately before every provider request.

2. **SERIOUS if used concurrently or across restart — refusal remains caller-serialized and process-local.**

   [IdentityContinuity.check()](../../../scripts/qi_tuna_identity_guard.py) has no lock, and construction initializes a fresh `_refused=False`. A new process or instance resets refusal; concurrent callers lack an atomic check-and-request boundary. The staged [design](../../../docs/design/tuna-destination-sequential-evidence-case.md) states these limits accurately.

   Remedy: hold one account lock across authenticated reload, guard comparison, and request dispatch; persist or reconcile refusal across restarts and account users.

I found no FATAL, unconditional SERIOUS, or SLOPPY residual within the helper’s declared one-serialized-process contract.

## Sound surfaces

- Guard-owned snapshots: `_snapshot()` validates and returns four immutable exact-`bytes` values; caller mutation cannot change the stored tuple. The regression appears at [test_qi_tuna_identity_guard.py:55](../../../tests/scripts/test_qi_tuna_identity_guard.py).
- Missing-field refusal: exact-type instances missing attributes produce `ValueError`, which `check()` latches before re-raising. The uninitialized exact-type case appears at [line 66](../../../tests/scripts/test_qi_tuna_identity_guard.py).
- Four comparisons: subject, team, user, and member digests each pass through `hmac.compare_digest`; the list comprehension evaluates all four before `all()`.
- Coherent transitions: [test_qi_tuna_subject_binding.py:78](../../../tests/scripts/test_qi_tuna_subject_binding.py) directly checks subject/team stability, user-only changes, and member/role-only changes.
- Unicode: [line 109](../../../tests/scripts/test_qi_tuna_subject_binding.py) covers equivalent literal/escaped JSON, malformed UTF-8, escape-decoded duplicate keys, and distinct NFC/NFD opaque subjects.
- The archived reports’ embedded target hashes describe earlier blobs. The hashes below identify the current staged review inputs.

## Exact staged inputs

SHA-256 covers the unmodified bytes emitted by `git show :path`.

| Staged path | SHA-256 | Git blob |
|---|---|---|
| `scripts/qi_tuna_identity_guard.py` | `7073ed96284fe2abb0b323866103518f9f999844e7612076117c1bf365cae798` | `73a51dd8336227e146d8154194137f29342594fb` |
| `tests/scripts/test_qi_tuna_identity_guard.py` | `1e5e49d687d97b939ac932f794530fce739886e21109246eef1f95e5b262990a` | `88c8562c30129abd1c19d08c93c73d72fd9488e5` |
| `tests/scripts/test_qi_tuna_subject_binding.py` | `ed21d801759bf5c2b7749ead0dd6b2473edbc441c25590ce1fd08b6392beb262` | `c2738bef2ee13b55cce839c46138f355a57dfaa7` |
| `docs/archive/reviews/tuna-identity-continuity-review.md` | `ae7cbf7370d138c0146cc4af2f7b7737db3f9a436462d8ea539545ce786248a5` | `76b00462946e20898d5f8986052bd9087823d7ad` |
| `docs/archive/reviews/tuna-subject-binding-followup-review.md` | `4f5b5bbade668dccd8c785e3b4277b0787a596775c5b0d72980eb24e9fa5e06c` | `ddc2a97792668611e96034768590de07b02fa500` |

Reviewed dependencies:

- `qi_tuna_subject_binding.py`: `243a2fcf…b203`, blob `2ce68123…a0e8`
- `qi_tuna_account_binding.py`: `0ff51eb4…967`, blob `f344c712…6904f`
- `qi_tuna_source_association.py`: `4abd49b1…75be`, blob `26a0bbcc…46e2`
- Acquisition design: `871873bb…a07`, blob `b1628ad7…4fe`

## Static-review boundary

No tests, linters, credentials, network access, provider operations, jobs, uploads, draws, external messages, or repository edits were performed. The targeted staged whitespace check produced zero findings.

HEAD remained `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`, local-head refs retained digest `ac228966…af8b`, and every reviewed staged blob remained identical. Concurrent checkout activity changed the global index-entry digest from `48d1b91d…37d1a` to `04866a87…bbe5` and changed the status digest repeatedly (`409c9eb0…faecb`, `8d830df5…d116`, then `5ffd2f70…3ff`). The observations therefore establish preservation only for the reviewed paths, HEAD, and local refs—not the entire active checkout.

Verdict: the staged revision repairs the two concrete continuity defects and the subject-binding test gaps. Trust remains bounded to a structurally valid, serialized, single-process comparison; authenticated admission and restart-safe request gating remain future integration work.

The review tracker completed in approximately 3 minutes 35 seconds.
