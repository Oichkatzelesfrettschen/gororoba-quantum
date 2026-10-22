# Sedenion left-operator Clifford envelope

The standard `cd_core` sedenion basis supplies eight real 16 by 16 left operators, `L_e1` through `L_e8`, satisfying `L_ea^2=-I` and `L_ea L_eb + L_eb L_ea=0` for distinct indices in this subset. Their 256 ordered Clifford words have exact integer Hilbert-Schmidt Gram matrix `16 I256`. The words are linearly independent and span `M16(R)`, establishing this concrete `Cl(0,8)` representation.

The [certificate](certificate.json) binds the generator indices, dimensions, exact checks and source hashes. Replay from the repository root:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" gororoba_quantum/hypercomplex_clifford_envelope.py --check docs/evidence/sedenion-clifford-envelope/certificate.json
```

All arithmetic uses signed permutation matrices and bounded `int64` sums. Every word remains a signed permutation; each Gram entry has absolute bound 16. The replay compares the entire Gram matrix against `16 I256`. Ordered word construction preserves factor order and maps independent masks through `parallel.ordered_map`.

The [full-generator counterexample](../hypercomplex-operators/certificate.json) still records 84 failed ordered distinct-generator anticommutators among all fifteen imaginary sedenion units. The eight-generator result and the fifteen-generator failure concern different finite sets.

Sedenion coefficient multiplication remains nonassociative and has zero divisors. `L_e1 L_e2` differs from `L_(e1 e2)`. The associative envelope therefore preserves useful operator structure without identifying coefficient products with compositions. Real antisymmetric generators exponentiate to orthogonal matrices that fit a complex four-qubit encoding; a future device case must state its device question, compilation error and baseline. The finite certificate supplies algebraic conformance, rather than particle dynamics, scalar-field discrimination or quantum advantage.

Furey's [2607.18450v3 source note](../../notes/papers/2607.18450.md) places an `EndR(V)` construction in the contemporary research context. The finite replay verifies the named standard-CD subset independently of that paper's particle interpretation.
