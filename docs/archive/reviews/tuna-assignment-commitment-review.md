The SHA-256 commitment encoding earns a bounded cryptographic PASS, but the retained-response validator has one SERIOUS type-confusion defect. The prospective protocol should remain unfrozen until that defect and its missing regression test are fixed.

Reviewed fields: cryptographic commitment, adversarial JSON parsing, provenance boundaries, and conditional-randomization design. I read every requested artifact in full and performed only read-only local probes.

## Findings

### SERIOUS — raw booleans masquerade as `uint16` integers

[`anu_qrng.admit()`](../../../scripts/anu_qrng.py) compares raw and wrapper arrays with Python equality. Python treats `False == 0` and `True == 1`. The subsequent range check examines only the wrapper values at [line 102](../../../scripts/anu_qrng.py), while the commitment validator likewise checks only wrapper values at [line 69](../../../scripts/qi_tuna_assignment_commitment.py).

This exact malformed record was accepted:

```json
raw.data = [false, true, 2, 3, ..., 23]
values   = [0,     1,    2, 3, ..., 23]
```

The record used a correct `raw_sha256`, source, timestamp, type, and length. The adapter therefore does not validate an exact raw `uint16` response, contrary to the claims in the [design](../../../docs/design/tuna-destination-private-assignment.md) and commitment contract at [line 87](../../../docs/design/tuna-destination-private-assignment.md).

Remedy: validate that the raw answer is an object and that every raw `data` element satisfies `type(value) is int` and the declared range before comparing it with wrapper values. Add this exact boolean/integer counterexample to both the adapter and commitment tests.

### SLOPPY — malformed raw container types escape as `AttributeError`

A wrapper whose correctly hashed raw text is `[]` reaches `answer.get(...)` at [line 92](../../../scripts/anu_qrng.py) and raises:

```text
AttributeError: 'list' object has no attribute 'get'
```

[`draw_values()`](../../../scripts/qi_tuna_assignment_commitment.py) does not catch `AttributeError`. The malformed record is refused, but the validator fails through an implementation accident rather than its declared `ValueError`/`DrawError` path.

Remedy: require `isinstance(answer, dict)` immediately after decoding and raise `DrawError` for every unsupported raw top-level type.

### SLOPPY — the tests leave coherent weakening mutations undetected

The hard-coded OpenSSL vector strongly pins the commitment byte layout, and the existing tests cover both duplicate-key layers plus basic release ordering. The target suite nevertheless permits implementation-only mutations that violate the documented contract:

- Changing `len(values) != 24` to `len(values) < 24` still rejects the tested 23-value record but admits 25 values.
- Replacing exact URL equality with endpoint-prefix matching still rejects `example.invalid` while admitting suffixes, extra parameters, or look-alike hosts.
- Replacing calendar parsing with a fixed-width timestamp regex still rejects the tested noncanonical timestamp while admitting dates such as `2026-02-30`.
- Allowing uppercase commitment digests still rejects the tested 63-character digest.
- Checking only nonempty salt/catalogue inputs still passes every existing test while admitting ambiguous variable-width fields.
- Removing nonstandard-number rejection remains invisible because neither wrapper nor raw `NaN`/`Infinity` appears in the tests.
- The suite never reads the actual catalogue, so coherent catalogue, manifest, or source changes cannot affect it.

Important missing cases include the accepted boolean/raw-integer mismatch, a non-object raw response, 25 values, lower and upper range violations, 31/33-byte salt and catalogue fields, uppercase and nonhex digests, the exact legacy endpoint as a positive case, extra/reordered URL parameters, calendar-invalid timestamps, nonstandard JSON constants, empty/oversized/non-`bytes` records, repeated verification calls, and prefix rollback.

Repeated calls and rollback belong in a future stateful guard rather than this pure function, but a boundary test should record that the primitive intentionally accepts both.

## Encoding reconstruction

The independent payload layout is unambiguous for accepted inputs:

```text
offset 0    31 bytes  "gororoba-qi-tuna-assignment-v1\0"
offset 31   32 bytes  salt
offset 63   32 bytes  catalogue SHA-256 bytes
offset 95    8 bytes  unsigned big-endian draw-record length
offset 103   N bytes  exact draw-record bytes
```

For the test fixture:

- Record length: 507 bytes
- Length encoding: `00000000000001fb`
- Total payload: 610 bytes
- Salt: bytes `00` through `1f`
- Catalogue digest fixture: bytes `20` through `3f`
- OpenSSL 3.6.5 result: `994e19c4baf8eb6c196636c74183e2267efe56d7145d55c9d3d037d88952e228`

The result exactly matches the oracle in [the test](../../../tests/scripts/test_qi_tuna_assignment_commitment.py). Fixed-width fields and the explicit record length defeat boundary-shifting attacks. Escape-equivalent duplicate keys were rejected in both wrapper and embedded raw JSON.

Digest comparison uses a lowercase 64-hex grammar and `hmac.compare_digest`; altered draw, salt, and catalogue inputs fail against an established digest.

## Release and assignment behavior

The 24-slot mapping is correct: slot `t` uses value index `t-1`; bit zero selects `baseline`, and bit one selects `rotated`.

Measured behavior:

- Empty and proper partial prefixes are accepted.
- Complete 24-slot openings are accepted.
- Gaps, duplicates, wrong arms, and within-list reordering are rejected.
- Repeating the same prefix is accepted.
- Verifying two slots and then verifying only one slot is accepted.

The last two outcomes establish that the primitive stores no temporal state. The documentation accurately assigns replay, rollback, release timing, and post-stop enforcement to a separately reviewed guard.

## Catalogue observation

The current catalogue contains exactly 48 alternatives: one baseline and one rotated choice for every slot 1–24. Independent checks found matching:

- All 48 `cases.json` hashes
- Both source-file hashes
- All backend snapshot hashes
- Compiler receipt hash
- Producer hash
- Catalogue hash

The catalogue declares `provider_execution_authorized=false` and explicitly states that it establishes neither assignments nor a served schedule at [line 292](../../../results/quantum_inspire/proposals/tuna-destination-slot-alternatives/catalogue.json).

That observation applies only to the present files. The commitment function accepts arbitrary 32-byte catalogue digest input and never reads or validates catalogue bytes.

## Threat and scientific boundaries

The documentation accurately states the remaining boundaries:

- Source URL and timestamp checks establish syntactic consistency only.
- A fabricated but internally coherent record passes; provider origin and first-draw status remain unwitnessed.
- The function neither generates a salt nor measures salt entropy; an all-zero salt is accepted.
- The caller holding `record_bytes` can derive every future arm. Returning `None` does not protect those inputs.
- The function cannot detect early disclosure, selective retry, arm-dependent delay, repeated release, prefix rollback, or post-stop misuse.
- The low bit is balanced only under a uniformly distributed `uint16`; the implementation does not establish uniformity, independence, concealment, provider behavior, or conditional fairness.
- The primitive neither binds releases to actual jobs nor authorizes provider activity.

A SHA-256 digest here proves only byte-level agreement with a later opening under the stated hash assumptions. The digest proves neither custody, acquisition timing, provider authorship, entropy, randomness, nor scientific fairness.

## Verification record

Every binding matched both working and staged bytes:

- Commitment script: `2a7dd6a2…c1c342`
- Tests: `bb619bce…458b5f`
- Design: `1f048c71…2f2fda`
- ANU adapter: `6dfb9876…cfaae`
- Catalogue: `353c28a3…26cde4`

The target tests passed: `2 passed`. Ruff formatting/lint, mypy, Bandit, and staged/working `git diff --check` passed. The installed Ruff 0.14.11 and mypy 1.19.1 differ from repository pins; the read-only constraint precluded a pin wrapper that could download or cache tools.

The initial and final `git status --porcelain=v1` outputs had identical SHA-256 `6fa89e34…42dd0`; that measurement establishes unchanged Git-visible status only.

Goal tracker usage: 73,077 tokens over approximately 4 minutes 48 seconds.
