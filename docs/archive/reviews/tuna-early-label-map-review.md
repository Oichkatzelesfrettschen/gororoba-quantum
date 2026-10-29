Review configuration: `gpt-daybreak-blue-latest`, high effort, default tier.

## Findings

- FATAL: none.
- SERIOUS: none.

### SLOPPY — tests count 48 entries but do not require 48 distinct signed permutations

`tests/scripts/test_qi_tuna_early_label_maps.py:33-35` checks only `len(maps) == 48`. The scalar replay at lines 99-118 evaluates whatever map specifications the record contains; it never requires:

- each source tuple to be a permutation of `(0,1,2)`;
- all 48 `(permutation, polarity)` pairs to be distinct;
- each 64-state transformation to be bijective;
- the inverse of every map to belong to the family.

A concrete coherent mutation survives the suite: replace the six permutations with six repetitions of the identity permutation while retaining all eight polarity masks:

```python
maps = [
    ((0, 1, 2), flip)
    for _ in range(6)
    for flip in range(8)
]
```

This produces 48 entries but only eight distinct maps. Independently replayed against the retained histograms, it still gives:

```text
nominal_one:        minimum 600
nominal_zero_prefix: minimum 6310
```

It also retains the identity first, includes the early-q6 flip, passes both synthetic examples, and passes the scalar score test after coherent record regeneration. The exact `--check` and gate would also pass once the record was regenerated from the defective producer. Thus the tests permit the advertised exhaustive family to collapse silently.

Required regression:

```python
expected = [
    (permutation, flip)
    for permutation in itertools.permutations(range(3))
    for flip in range(8)
]
assert observed == expected
```

The test should additionally construct all 64-state maps and require bijectivity, 48 distinct transformations, terminal preservation, and inverse closure.

This is a regression-coverage defect, not an error in the currently staged producer or record.

## Verified sound portions

The binding-file hashes remained unchanged throughout review:

- producer: `271486a916177ad96d5f5203c2c5c4233e14312542b8954abd7abd3050f789af`
- tests: `b7123903e8d68666ee1ed2132df38c674121476a1e8ce7ded99a4aa9526defe5`
- record: `5093dcda0011f164a3a22427ec7c287d0b7b6bc2f5d15c20782f311020d21008`
- note: `c70f8fec3e0d35b7d798df4546afa5f4022b49f4a22d99d118b03dd11bfd8583`

Independent scalar reconstruction established for the current artifact:

- exactly 48 distinct signed permutations;
- every map is a bijection of all 64 states;
- every map preserves the three terminal bits;
- every inverse belongs to the same 48-map family;
- all six source histograms contain exactly 4,096 shots;
- all 96 reported scores match scalar integer calculations;
- all source and producer hashes match;
- normal and optimized exact replays pass.

`output_bit_sources[b]` means that output early bit `b` receives the stated input bit, followed by the polarity-mask flip. Counts are pushed through that map correctly at `scripts/qi_tuna_early_label_maps.py:24-34`. Because the complete signed-permutation group is closed under inversion, choosing the forward or inverse convention cannot change the minimum over the full family. Both observed minimizers are themselves involutions:

- nominal one: identity;
- nominal-zero prefix: flip early q6.

The total-variation denominator is correct:

\[
\operatorname{TV}\!\left(P_R,\frac{P_B+P_A}{2}\right)
=
\frac{\sum_x |2C_R(x)-C_B(x)-C_A(x)|}{4\cdot4096}.
\]

All reported values match:

| Case | Minimum | Terminal lower bound |
|---|---:|---:|
| Nominal one | `600/16384 = 0.03662109375` | `232/16384 = 0.01416015625` |
| Nominal-zero prefix | `6310/16384 = 0.3851318359375` | `6286/16384 = 0.3836669921875` |

The lower bound is exact: summing each signed 64-cell difference over early labels gives the terminal projection, and the triangle inequality gives

\[
\sum_t\left|\sum_e d_{t,e}\right|
\leq
\sum_{t,e}|d_{t,e}|.
\]

The producer implements and checks that contraction at `scripts/qi_tuna_early_label_maps.py:35-42`.

The exact PR gate is present at `ci/gates.json:5097-5106`. `--check` is read-only, while `--out` uses exclusive creation (`scripts/qi_tuna_early_label_maps.py:77-89`). Staged whitespace checking was clean apart from the repository’s existing fsmonitor warning.

## Scientific limits

The minimum is selected after acquisition from 48 alternatives. It has no uncertainty interval and is not a preregistered estimator. It excludes only a single fixed early-bit signed permutation as a complete explanation of the empirical nominal-zero histogram difference.

The analysis does not exclude:

- time-varying or shot-dependent mappings;
- faults involving terminal labels;
- schedule or reconstruction changes;
- calibration drift or apparatus memory;
- other differences between the separately executed jobs.

The nominal-zero primary endpoint remains `implementation route unavailable`. The result supports no causal destination effect, physical mechanism, calibrated population, or further acquisition.

Pytest was not run because this read-only sandbox lacks writable temporary storage. Normal and `-O` exact checks and the independent scalar audit did run.

Verdict: **the current staged numerical result is correct and scientifically bounded, but the regression suite has one SLOPPY exhaustiveness gap.** Durable acceptance of the advertised 48-map family should wait for the distinct-bijection/inverse-closure regression above.