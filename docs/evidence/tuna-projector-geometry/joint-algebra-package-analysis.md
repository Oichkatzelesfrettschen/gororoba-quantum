# Package-checked algebraic summaries of Tuna joint responses

The [joint-response analysis](joint-response-analysis.md) gives an eight-cell
probability vector for the three early/terminal disagreement bits. This note
uses the repository's Cayley-Dickson convention to analyze those measured
binary labels. The mapping and chosen basis pair were selected after acquisition.
The mathematics does not assert an octonionic device, calibrated populations,
QND behavior, a causal destination effect, or a completed nominal-zero case.

## Exact encoding and counterexample

For a job, write `k = m4 + 2*m11 + 4*m6`, where each `m` is early XOR terminal,
and write `p = sum_k (count[k]/4096) e_k`. The ordinary octonion basis follows
[`cd_core`](../../../gororoba_quantum/cd_core.py). For basis pair `(e1,e6)`,
calculate the sign mean `E[omega(1,6,k)]` and the ordinary Euclidean squared
norm of the coefficient vector of the associator

    (e1 e6) p - e1 (e6 p).

The second statistic is a quadratic function of the chosen empirical
probability coordinates; its norm is not a measured quantum-state norm or a
physical excitation probability. Exact rational calculations give:

| Retained case, execution order | Sign mean | Coefficient-associator squared norm |
|---|---:|---:|
| Nominal one, baseline before | -97/512 | 764037/1048576 |
| Nominal one, rotated destinations | -77/512 | 1434981/2097152 |
| Nominal one, baseline after | -411/2048 | 3101879/4194304 |
| Nominal zero prefix, baseline before | -65/512 | 1316907/2097152 |
| Nominal zero prefix, rotated destinations | -245/2048 | 2586339/4194304 |
| Nominal zero prefix, baseline after | -21/128 | 1391655/2097152 |

The nominal-one sign response equals `183/4096`, the mask-54 parity response
in the joint analysis. The nominal-zero sign response is `0.02587890625`,
while that prefix's early-qubit-6 probability response is `0.4818115234375`.
The selected sign compression misses the larger marginal contrast. Neither
comparison identifies why separate jobs returned different labels.

The source-bound standard and split tables agree on all 512 ordered
basis-associator signs at dimension 8, but standard `e4^2=-1` and split
`e4^2=+1`. Agreement on associator signs alone cannot identify the algebra.
The coefficient norm above is explicitly Euclidean for both comparisons;
the split algebra's own quadratic form has different signature.

## Independent package use and provenance

The [fresh local runtime observation](joint-package-runtime-observation.json)
uses installed hypercomplex, hypercomplex-engine, hyprat and SplitOct packages.
The [capture provenance](joint-package-runtime-provenance.json) records the UTC
capture interval, producer identity, two exact-byte captures and Arch package
integrity checks. The probe obtains the registered release digest for each
package from `scripts/algebra_package_tables.py`, requires exactly one matching
archive and checks every installed Python module against a release archive
member. All 32 module files matched. The imported top-level module for each
package belongs to the checked distribution.

The installed `hypercomplex`, `hypercomplex-engine` and `hyprat` tables use
the identity map onto `cd_core`; the probe checks all 64 basis products in
dimension 8 and all 256 in dimension 16 for each implementation. `SplitOct`
and the engine's split table agree on all 64 dimension-8 basis products.
The probe compares all 512 split and standard associator signs, checks the
contrasting `e4` squares, and computes the six data-derived associators with
both installed exact rational implementations. The note's
[offline table replay](joint-algebra-analysis.json) independently evaluates the
same fractions from the [retained package tables](../algebra_packages/tables.json)
after revalidating their registered maps and the six raw-shot records. Offline
replay checks the historical package tables; it does not inspect the packages
currently installed on a later machine.

Pandas independently groups each six-bit raw-shot distribution; SciPy's
Hadamard transform checks every parity numerator. SymPy and python-flint agree
on the exact `183/4096` response; mpmath checks the conditional-Hoeffding
radius's upward rounding. NumPy and SciPy also calculate descriptive
Hellinger distances of `0.055941976930` for nominal one and `0.453281338498`
for the nominal-zero prefix. The corresponding Jensen-Shannon **distances**
are `0.063710980845` and `0.523562104011` in square-root bits. Those finite
histogram distances have no uncertainty interval in this analysis.

To replay the ordinary CI evidence without optional packages:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/qi_tuna_joint_algebra.py --check \
  docs/evidence/tuna-projector-geometry/joint-algebra-analysis.json
```

To repeat the live package observation, install the registered package versions,
place exactly one archive for each of the four registered digests in
`TUNA_PACKAGE_ARCHIVES`, and select an interpreter with the packages named in
the observation. Use a new, nonexistent output path:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/qi_tuna_joint_package_runtime.py \
  --archives "$TUNA_PACKAGE_ARCHIVES" --out "$OUTPUT"
```

The package table's [source notes](../../notes/packages/README.md) own release
URLs, digests and independence limits. `hypercomplex-algebra` wraps the
engine and is not an independent implementation. The optional-package runtime
probe remains separate from the pin-only offline gate; its floating-point
outputs may differ across library builds. Neither path submits a provider job.
