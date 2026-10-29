No FATAL or SERIOUS residual defect appears in the two staged blobs. The commitment remains a sound byte-binding primitive. Three SLOPPY robustness/evidence gaps remain.

### Residual findings

1. **SLOPPY, high confidence — the integer bound depends on interpreter-global JSON behavior.**

   [qi_tuna_capture_commitment.py:43](../../../scripts/qi_tuna_capture_commitment.py) admits integers up to 6,291,456 bits, approximately 1.89 million decimal digits. [json.dumps at line 78](../../../scripts/qi_tuna_capture_commitment.py) must expand each accepted integer before the final size check.

   Normal CPython integer-to-decimal limits reject values far below that stated bit cap. A process that raises or disables that global limit instead performs the potentially expensive conversion before enforcing `MAX_BODY`. The same explicitly in-range capture can therefore hash or fail depending on process configuration.

   [The integer test at line 125](../../../tests/scripts/test_qi_tuna_capture_commitment.py) supplies an already over-limit value, so it never exercises accepted large integers, decimal expansion, zero, negative signs, or the runtime digit ceiling.

   Remedy: impose a small, fixed bit bound below the pinned runtime’s decimal-conversion ceiling, ideally derived from the closed locator contract, and test both sides of that bound.

2. **SLOPPY, high confidence — the aggregate precheck does not bound canonical-JSON allocation.**

   [The aggregate calculation at line 58](../../../scripts/qi_tuna_capture_commitment.py) counts Python characters rather than escaped ASCII JSON bytes. `ensure_ascii=True` can expand one non-BMP character into a 12-byte surrogate-pair escape. Quotes, controls, negative signs, zero values, JSON punctuation, and field names also escape or add bytes.

   [The exact check at line 79](../../../scripts/qi_tuna_capture_commitment.py) ultimately fails closed, but only after `json.dumps(...).encode("ascii")` constructs the expanded string and byte copy. The input is finite, so the defect is bounded amplification rather than unbounded allocation.

   [The bound tests at line 120](../../../tests/scripts/test_qi_tuna_capture_commitment.py) exercise only individual maxima. They never reach either the four-receipt aggregate branch or the post-escaping canonical-size branch.

   Remedy: preflight escaped byte sizes or serialize through a bounded sink. Add one individually valid aggregate-overflow case and one Unicode-escape expansion case.

3. **SLOPPY, high confidence — “external commitment” names provenance the test does not establish.**

   [The fixed digest at line 75](../../../tests/scripts/test_qi_tuna_capture_commitment.py) closes the follow-up’s implementation-generated-fixture weakness as a regression vector. The repository contains that digest only in this test; the staged artifacts retain neither its canonical input bytes nor an independent OpenSSL receipt.

   The test therefore proves behavior against a fixed literal, not external authentication. Rename the test accordingly or retain the independently generated input and command receipt if external provenance matters.

### Sound portions

- The parametrized test covers all four receipt positions, coherent same-length body-plus-digest substitution, valid `200` to `201` substitution, and complete checkpoint-plus-four-receipt replacement at [line 63](../../../tests/scripts/test_qi_tuna_capture_commitment.py).
- The new validation guards do not alter the canonical schema or hashing path. The Unicode, escape, and ordered-query vector remains `f1ec857e2781615b8d049718cfdb6b68369d36efbdb6b54f252b4825c55a1342` at [line 94](../../../tests/scripts/test_qi_tuna_capture_commitment.py).
- Exact-type checks continue to reject boolean/integer aliasing.
- The bounds do not imply provider authentication, source association, durable retention, timing, or scientific admission. The module assigns those obligations to the caller at [line 3](../../../scripts/qi_tuna_capture_commitment.py), and `capture_commitment` explicitly hashes “without authenticating” at [line 19](../../../scripts/qi_tuna_capture_commitment.py).

### Exact staged SHA-256 inputs

| Staged artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_capture_commitment.py` | `47b734ebbef9929b8001f20e9174010a1fb4cc59c05fd1a70f3320ed0494d817` |
| `tests/scripts/test_qi_tuna_capture_commitment.py` | `543bde2afc082c15d554c97c3d41f6184469040d5a26189b0c48c361d1cb6560` |
| Initial review | `a682bd9818a08c2d6b47d1baea6f20ce555d79a631b9df01743279f42b0793b7` |
| Follow-up review | `1803b2912ca4c7785ffe8643449d0aa46f44b36b2619a4a11adc74d47d87a685` |

The archived reviews’ recorded producer and test hashes are historical and do not cover the current bounded blobs. Final HEAD remained `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`; repeated staged hashes matched, the two named working-tree files matched their index entries, and the focused staged whitespace check was clean.

Static inspection only. I ran no tests, imports, credentials, network access, provider operations, jobs, uploads, draws, external messages, or edits.
