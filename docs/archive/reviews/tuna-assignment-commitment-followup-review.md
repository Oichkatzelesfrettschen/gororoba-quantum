Reviewed artifact: targeted Python commitment validator and regression suite, with cryptographic, parser, provenance, and scientific-boundary claims. I read the complete changed artifacts and relevant plan entry.

## Verdict: bounded PASS with one SLOPPY test-coverage finding

The current commitment implementation closes the raw-boolean and non-object defects at its own boundary. The broader historical ANU adapter remains defective and is accurately recorded as unresolved.

### SLOPPY — regression mutations can hide partial validation

The implementation correctly checks every raw element at [line 70](../../../scripts/qi_tuna_assignment_commitment.py), but the regression fixture places invalid elements only at indices 0 and 1 at [line 96](../../../tests/scripts/test_qi_tuna_assignment_commitment.py).

An in-memory mutation from:

```python
for value in raw_answer["data"]
```

to:

```python
for value in raw_answer["data"][:2]
```

passed all six checked-in tests. The mutated validator then accepted this exact counterexample:

```text
wrapper values[23] = 1
raw data[23]       = true
```

Python’s `True == 1` behavior then carries the malformed tail element through the historical adapter.

The non-object test similarly uses only `[]` at [line 98](../../../tests/scripts/test_qi_tuna_assignment_commitment.py). A mutation that rejects lists instead of requiring a dictionary passed all six tests; raw `null` then escaped as `AttributeError`.

The suite also lacks a deeper duplicate-key object fixture. The implementation’s recursive hook correctly rejected `{"meta":{"x":1,"x":2}}`, but a selective duplicate checker that retained the tested wrapper and embedded top-level checks passed the suite.

Recommended additions:

- Place boolean aliases and range violations at first, middle, and final indices.
- Parameterize raw top-level values over `[]`, `null`, string, number, and boolean.
- Add a duplicate-key fixture inside an embedded nested object.

These are regression-strength defects. The current implementation itself checks the full list and every raw top-level type correctly.

## Counterexample results

The repaired validator produced controlled `ValueError` rejection for:

- Raw `false,true` paired with wrapper integers `0,1`
- Raw list, null, string, number, boolean, and object without `data`
- Wrapper duplicate keys
- Embedded raw duplicate keys
- Deeper embedded duplicate keys
- Look-alike host, extra query parameter, and reordered query
- 31- and 33-byte salt or catalogue fields
- Noncanonical and calendar-invalid timestamps
- Values `-1` and `65536`
- Raw `NaN`, `Infinity`, and `-Infinity`
- Wrapper `NaN`
- Empty and oversized records

The exact legacy endpoint remains accepted.

Plausible broad weakenings of integer typing, draw count, source equality, calendar parsing, fixed field sizes, JSON constants, and duplicate parsing were all killed by the expanded suite.

## Historical adapter boundary

The unchanged [`anu_qrng.admit()`](../../../scripts/anu_qrng.py) still behaved as documented:

```text
historical_adapter_bool_alias=ACCEPT
historical_adapter_nonobject=REJECT:AttributeError
```

The follow-up makes no false general-repair claim:

- The [QRNG note](../../../docs/notes/qrng/README.md) explicitly records both defects and limits the repair to the Tuna validator.
- The [design](../../../docs/design/tuna-destination-private-assignment.md) states that the historical adapter remains unchanged.
- The [plan](../../../docs/state/plans/tuna-readout-mapping-identifiability.json) retains the generic repair as `todo`, including evidence migration and replay requirements.

## Remaining boundaries

The documentation accurately preserves these limitations:

- A canonical future timestamp such as year 9999 is accepted; syntax provides neither acquisition time nor a witness.
- Replaying a release prefix and rolling back to a shorter prefix are accepted. The function is stateless, and [the regression test](../../../tests/scripts/test_qi_tuna_assignment_commitment.py) records that limitation.
- A zero-filled 32-byte salt is accepted; the validator checks size, not entropy.
- Any 32-byte catalogue digest is accepted; the function never opens or verifies catalogue bytes.
- Source strings are labels, not provider-origin authentication.
- The primitive supplies neither first-draw evidence, custody, concealment, post-stop enforcement, conditional fairness, nor an execution guard.
- The primitive authorizes no provider operation and binds releases to no actual job.

The commitment boundary is therefore closed for exact record parsing, byte commitment, and validation of one supplied release-prefix snapshot. The acquisition, custody, temporal-release, catalogue-admission, and execution protocol remains deliberately open.

## Hash and check record

Every binding matched both staged and working bytes:

| Artifact | SHA-256 |
|---|---|
| Commitment validator | `aee57318f778b1da78a29994177c7f8254458c1052cb134068692b556e48cb1b` |
| Tests | `0cc08d1cd69d3b7102b70ecd471f7dee102e91a426c8b6b03525aa9e6bbb7195` |
| Design | `216fda791d62c90554abac04883bc7536ffa5901d8c428c659f9dd0bafdc4590` |
| Historical adapter | `6dfb9876bd02df4656114a6c660956d584974ecbb1d7250e1bf40885aafcfaae` |
| Alternatives catalogue | `353c28a3342835478f1713f61fe590ceb8a0bd0f5f7cdea59a03a6c7a126cde4` |
| QRNG note | `b8f5d894b357d596edb6c9b0b05f71c63b0837b3a9624ebe38da52f83d20f262` |

Results: six target tests passed; formatting, lint, type, Bandit, plan-tracker, and diff checks passed under the installed read-only toolchain. The initial and final Git-visible status fingerprints both equal `430758ce…b0787`.

Goal tracker usage: 53,876 tokens over approximately 3 minutes 19 seconds.
