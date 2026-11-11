# Exact A5 quantum-claim contracts

This successor makes the 2026-11-11 falsification audit executable. The historical
[HHL/QSVT probe](../hhl-qsvt-falsify/README.md) measured a Pauli expansion. These checks cover the natural
signed-permutation expansion, selected complete kernel projectors, the failed scalar kernel predicate, and
the distinction between rational and modular rank. They establish algebraic contracts and counterexamples;
they do not establish a quantum speedup or a compiled QSVT resource estimate.

## Implemented contracts

The reusable module is [cd_quantum_contracts.py](../../../gororoba_quantum/cd_quantum_contracts.py).
The deterministic producer is [check_a5_quantum_contracts.py](../../../scripts/check_a5_quantum_contracts.py),
and [exact-contracts.json](exact-contracts.json) is its source-bound, float-free receipt.

| Contract | Exact check | Falsification boundary |
| --- | --- | --- |
| Natural LCU | Each A5 basis left action is a signed permutation. Rational signed weights prepare probabilities abs(a_i)/alpha; SELECT preserves the selector and applies the signed basis permutation. Its selected block equals L_a/alpha | Wrong coefficient signs, normalization, padding or data/selector indices must fail; selector size excludes implementation workspace |
| Support-dependent resources | A dense coefficient vector needs 32 terms and five selector qubits; a two-support vector needs one. alpha=norm1(a), with alpha^2/norm2(a)^2 <= support size | This upper bound is not an evaluation of the spectral norm or a hardware depth claim |
| Complete kernel projector | For B=A^T A and supplied positive roots r, P=product_r(I-B/r) must be symmetric, idempotent and annihilated by A. Its polynomial constant term makes it identity on ker(A) | AP=0 alone would allow P=0; the polynomial form supplies completeness. Missing or incorrect roots that leave a nonzero singular direction fail. Extra unused positive roots are permitted and are not reported as the minimal spectrum |
| Failed isotropy predicate | All 31 imaginary A5 basis actions are skew. L_e1 is invertible, yet v^T L_e1 v=0 for all v over each retained odd field; v=e0 has L_e1 v=e1 | A scalar isotropy test is not a kernel-membership oracle. Characteristic two is outside this odd-modulus diagnostic |
| Rank changes with the field | A=[[1,2],[(p+1)/2,1]] has determinant -p, rank_Q=2 and rank_Fp=1; the receipt includes a nonzero modular kernel vector and its integer image | An integer or complex lift cannot silently inherit the modular rank |

For a=e1+/-e10, the certified projector has nullity eight. For a=e25+/-e8 it has nullity twelve.
In all four cases the supplied nonzero Gram roots are 2 and 4, so

```
P_ker = I - 3B/4 + B^2/8.
```

The named spectra are also independently represented in the existing
[photonic spectral record](../a5-photonic-crosschecks/README.md). This does not classify every A5 spectrum.

The bounded tests in [test_cd_quantum_contracts.py](../../../tests/gororoba_quantum/test_cd_quantum_contracts.py)
use signed rational coefficients, noncoordinate kernels, zero and invertible matrices, malformed inputs,
missing/wrong roots, explicit modular witnesses and both existing two-term SELECT circuit constructions.
The circuit checks compare every matrix entry of the selected block for both positive and negative coefficients.
Qiskit matrix comparisons use absolute component tolerance 1e-12; the algebraic receipt uses exact rational arithmetic.
They reuse [select_lcu.py](../../../gororoba_quantum/select_lcu.py); no second SELECT framework is introduced.
`verify()` supplies a small pure case to the admission contract suite. Retained-file replays run on demand.

## Replay

Use the repository-pinned interpreter. These deterministic exact checks consume no random seed and contact
no provider. Native numerical libraries retain their normal CPU dispatch.

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=2 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
"$PYTHON" -B -W error scripts/check_a5_quantum_contracts.py \
  --check docs/evidence/a5-quantum-contracts/exact-contracts.json
"$PYTHON" -B -m pytest tests/gororoba_quantum/test_cd_quantum_contracts.py \
  tests/test_a5_photonic_scope.py \
  "tests/gororoba_quantum/test_contract_suites.py::test_contract_unit[cd_quantum_contracts:verify]" \
  "tests/gororoba_quantum/test_contract_suites.py::test_every_suite_is_accounted"
```

[validation.json](validation.json) records the 87 tests this command selects, pinned Ruff and bounded-import mypy checks, and all three exact retained-record replays under the complete pinned runtime. Full hosted admission remains a separate integration check.

The producer binds `cd_core.py`, the contract module and its own source bytes. A changed source or scientific
field requires a new receipt. The replay gate declares this float-free JSON under `replays` in `ci/gates.json`.

## Related implementation and remaining mathematical scope

The [photonic scope replay](../a5-photonic-crosschecks/README.md) checks the saved optical operators and
all selected input columns, separates returned-event denominators and certifies agreement with embedded A4.
It does not infer full A5 nullity from the two-dimensional slice.

The [workload fit](../../notes/topics/quantum-linear-algebra-fit-a5.md) records the current algebraic frontier.
E8 degree five is already closed at both primes. The restricted-target extension of
[the monomial ladder](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/5a8b151c5edeafbd9e6f17fa38610ed5467497b3/docs/evidence/a5-exceptional-fibers/monomial-ladder/README.md) preserves the full m I^d denominator,
uses degree five as a control and targets the remaining 140 degree-six directions. A finite-jet lower bound
becomes an exact result only when it reaches the known upper bound.

The existing exact algebra and Rocq interfaces belong to `gororoba-open`; this change adds their experimental
consumer checks in `gororoba-quantum`. Infrastructure and document repositories acquire no duplicate provider,
algebra, proof or paper-byte implementations from this task.
