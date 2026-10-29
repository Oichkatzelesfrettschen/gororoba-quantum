The standalone subject-binding primitive is sound. The revision resolves the archived review’s coherent-transition defect and most test gaps. The code still does not authenticate a subject or admit a refresh-time provider request.

## Residual findings

1. **SERIOUS if treated as acquisition admission — provider integration remains absent.**

   [bind_subject()](../../../scripts/qi_tuna_subject_binding.py) is stateless. A separate [IdentityContinuity](../../../scripts/qi_tuna_identity_guard.py) latches mismatches within one process, but the staged call graph contains only tests and catalogue references—no provider-request path.

   The binding also omits issuer and audience by design. The future adapter must authenticate those values and the readbacks, invoke the comparison after every credential reload, and preserve refusal across restarts before the next provider request. The design accurately retains that limitation at [tuna-destination-sequential-evidence-case.md:243](../../../docs/design/tuna-destination-sequential-evidence-case.md).

2. **SLOPPY test precision — coherent transitions are detected, but field invariants are not directly asserted.**

   [test_binding_detects_user_and_member_changes_with_same_subject_and_team()](../../../tests/scripts/test_qi_tuna_subject_binding.py) checks only whole-binding inequality. The test does not directly assert that:

   - subject and team digests remain unchanged;
   - only the user digest changes for a coherent user transition;
   - only the member digest changes for member or role transitions.

   Static inspection confirms the intended behavior, and the separate account tests establish the shared team namespace. Explicit per-field assertions would make the regression test diagnostic rather than merely sensitive.

3. **SLOPPY Unicode boundary — direct coverage improved, but scalar-clean JSON is not a general contract.**

   The tests now cover valid non-ASCII subjects, literal-versus-escaped equivalent JSON, malformed UTF-8, and escaped duplicate keys at [test_qi_tuna_subject_binding.py:99](../../../tests/scripts/test_qi_tuna_subject_binding.py). Exact comparison correctly keeps normalization variants such as NFC and NFD distinct for an opaque subject identifier, although no test records that rule.

   The shared parser still permits escaped lone surrogates in ignored string fields. A lone surrogate cannot impersonate `oidc_sub`, because the caller-supplied subject must encode as UTF-8, but the parser does not establish a general Unicode-scalar-clean JSON claim.

## Contract checks

- Coherent same-subject, same-team user/member/role changes now alter the binding through distinct user and member-role digests.
- HMAC messages use separate, versioned provider domains. The accepted encodings are unambiguous:
  - subject: UTF-8 subject tail;
  - user: canonical decimal user ID;
  - member: canonical decimal member ID, NUL separator, and allow-listed role;
  - team: separate team domain and canonical decimal team ID.
- Exact-type validation rejects Boolean/integer aliases and subclasses:
  - subject: exact `str`, 1–256 code points, UTF-8 encodable;
  - JSON bodies: exact `bytes`, 1–2 MiB each;
  - identifiers: exact positive `int`, with no explicit provider-schema upper bound;
  - activity: singleton `True`;
  - role: exact `"member"` or `"admin"`;
  - secret: exact `bytes`, exactly 32 bytes.
- [_json_object()](../../../scripts/qi_tuna_source_association.py) rejects duplicate keys recursively after escape decoding, malformed UTF-8, non-object roots, empty or oversized bodies, non-finite constants, overflow-to-infinity floats, and recursion failure.
- The module-level disclaimer at [qi_tuna_subject_binding.py:1](../../../scripts/qi_tuna_subject_binding.py) accurately states that the primitive establishes neither authentication nor admission.

The archived review’s first and third findings are resolved; its refresh-admission finding remains. Its recorded hashes describe the earlier blobs.

## Exact staged SHA-256

- `scripts/qi_tuna_subject_binding.py`: `243a2fcfa56783c57f8db79bdae38568b6400e5fb5b1c2138aa98ffed394b203`
- `tests/scripts/test_qi_tuna_subject_binding.py`: `bdf61e319ae830903202e551136663756247d5c6dbf2133a0380be1debc2522b`

Reviewed dependencies:

- `scripts/qi_tuna_account_binding.py`: `0ff51eb43ef9f71266bbd17abe8879e833833d3b2f155e2ae464c448714bb967`
- `scripts/qi_tuna_source_association.py`: `4abd49b146891fcb3ab374e20bd2dc978025046f7381b191923e315e35ab75be`

The before-and-after observations recorded identical HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`, status digest `3f8e4dac…`, index digest `ec6f2854…`, and local-ref digest `b3670f4c…`. Both target worktree hashes matched their staged hashes. The targeted staged whitespace check produced no findings.

No tests, credentials, network or provider operations, jobs, uploads, draws, messages, or edits were performed.
