# Reviewer-feedback audit

This is a CPU-only mathematical and ideal-circuit audit, not a hardware execution,
repository modification, or authorization to spend QPU time.

Run with Python and NumPy:

```sh
python audit.py --out audit_results.json
```

## Scope

The reviewer supplied a reversible signed-XOR lookup, a proposed controlled
associator experiment, and an alleged zero-divisor pair. The audit tests those
claims under `(a,b)(c,d) = (ac - conjugate(d)*b, d*a + b*conjugate(c))`.
The direct integer doubling implementation is independently checked against the
iterative sign algorithm in the inspected `cd_core.py` blob
`ccb51aa4b9e9bab6ab8675fa634d25cb77291cf1`.

## Results

* All 256 basis products agree between the two arithmetic implementations.
* The reversible extension of the proposed sign-register lookup is bijective
  on all 512 basis states. It does not implement coefficient multiplication by
  simply tracing out the retained input and sign registers.
* The proposed normalized pair `(e1+e10)/sqrt(2)` and
  `(e2-e13)/sqrt(2)` multiplies to `(e3+e7+e8-e12)/2`, not zero.
* The corrected pair with second operand `(e4-e15)/sqrt(2)` does multiply to
  zero. The reviewer's sign-tagged lookup still returns data labels 5 and 14
  each with probability one half; neither is an algebraic zero output.
* The universal coefficient contraction M obeys `M M^dagger = 16 I`; its
  physical success Kraus operator can be `M/4`, with success probability
  `||xy||^2/16` on normalized coefficient states.
* The fixed-operand five-qubit LCU has ideal selector-zero probabilities 0,
  1/2, and 1 for the corrected dark pair, the reviewer's proposed pair, and
  the corrected bright control, respectively.
* The fixed-basis-pair associator unitary is verified for all 256 pairs.
* All 4096 basis triples contain 1848 non-associating triples. These are also
  the 1848 non-associating ordered distinct imaginary triples among 2730.
* Uniform input over all triples gives witness expectation 25/256 and
  ancilla-one probability 231/512, not deterministic minus one.
* In a Hadamard overlap test, measure X before the last H or Z afterward.
  Literal X after the last H gives zero for the balanced example.
* The complex-linear extension of even an associative real subalgebra has
  zero divisors; the real Hurwitz norm statement cannot be applied to
  arbitrary complex coefficient states.

Exact integer assertions and floating-point ideal-state checks are distinguished
in `audit.py`. The script establishes no hardware fidelity, gate-cost estimate,
publication-priority claim, external-field detection, or non-complex fundamental
quantum theory.
