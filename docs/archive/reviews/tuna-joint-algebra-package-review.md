Review configuration: `gpt-daybreak-blue-latest`, high effort, default tier.

## Findings

- FATAL: none.
- SERIOUS: none.
- SLOPPY: none.

## Algebra and retained-data checks

The exact algebra is correct.

- The mismatch index is consistently \(k=m_4+2m_{11}+4m_6\), matching the reviewed disagreement ordering and the note at `docs/evidence/tuna-projector-geometry/joint-algebra-package-analysis.md:12-18`.
- `scripts/qi_tuna_joint_algebra.py:20-31` correctly evaluates
  \[
  (e_1e_6)p-e_1(e_6p)
  \]
  coefficient-by-coefficient. XOR by \(1\oplus6\) is a permutation, so summing the squared coefficients introduces no hidden collisions.
- Independent exact arithmetic reproduced all twelve retained fractions: six sign means and six Euclidean coefficient-norm squares.
- The associator-sign vector for \(k=0,\ldots,7\) is
  `(+,+,-,-,-,-,+,+)`. This is exactly the parity of mismatch bits \(m_{11}\oplus m_6\), corresponding to six-bit Walsh mask 54. Each job’s sign mean therefore equals `parity_numerators[54]/4096`, as enforced at `scripts/qi_tuna_joint_algebra.py:37-41`.
- The nominal-one response is exactly `183/4096`; the nominal-zero-prefix sign response is `53/2048 = 0.02587890625`. The cases remain separate and retain their original boundaries.
- The reported norm is the dimensionless Euclidean squared norm of coefficients in the chosen basis. It is neither an algebra norm for the split table nor a measured quantum-state norm. The note states that limitation explicitly at `docs/evidence/tuna-projector-geometry/joint-algebra-package-analysis.md:20-22` and `39-43`.

The source-bound ledger check exhaustively verifies every ordinary dimension-8 and dimension-16 basis product for the three selected implementations: \(3(64+256)=960\) products. It also verifies all 512 ordered standard/split associator-sign triples and the contrasting squares \(e_4^2=-1\) versus \(e_4^2=+1\). Independent loops reproduced those results with zero discrepancies. The implementation is at `scripts/algebra_package_tables.py:636-704`.

## Package and archive provenance

All four supplied archives have the exact registered `RELEASES` digests:

- `hypercomplex` 0.3.4
- `hypercomplex-engine` 0.5.0
- `hyprat` 0.2.0
- `splitoct` commit `e29e72f805c2`

The direct in-memory capture established:

- exactly one matching archive for each pin;
- all 32 installed functional Python files have byte content present in the corresponding archive;
- installed distribution versions match the retained observation;
- each imported top-level module originates within its checked distribution;
- all six retained jobs reproduce the source-bound exact algebra results.

Normal and optimized captures were both byte-identical to `joint-package-runtime-observation.json`, SHA-256 `caba2333007c0060e5bb9a658ab0009e47387244683241683b02be1e2210595a`.

The distinction between evidence classes is sound:

- `scripts/qi_tuna_joint_algebra.py` is the package-free offline verifier used by the PR gate (`ci/gates.json:5086-5095`).
- `scripts/qi_tuna_joint_package_runtime.py` is an environment-dependent observation requiring the installed optional packages and pinned archives.
- The offline verifier does not pretend to reconstruct the fresh installed-package observation. The documentation states this at `docs/evidence/tuna-projector-geometry/joint-algebra-package-analysis.md:64-68` and `79-102`.

All producer, record, ledger, joint-response, and provenance hashes matched their recorded bindings.

## Distance definitions

Independent standard-library calculations reproduced both metrics:

| Case | Hellinger distance | Jensen–Shannon distance |
|---|---:|---:|
| Nominal one | `0.055941976930` | `0.063710980845` sqrt bits |
| Nominal-zero prefix | `0.453281338498` | `0.523562104011` sqrt bits |

The Hellinger implementation is
\[
H(P,Q)=\frac{\|\sqrt P-\sqrt Q\|_2}{\sqrt2}.
\]

SciPy’s `jensenshannon(..., base=2)` returns the square root of Jensen–Shannon divergence, so the recorded unit “square-root bits” is correct (`scripts/qi_tuna_joint_package_runtime.py:160-171`). Both compare the rotated 64-cell six-bit distribution with the arithmetic mean of the two baseline distributions. They are descriptive float64 statistics without uncertainty intervals, as disclosed in the retained note.

## Execution and test surface

The following checks ran successfully:

- normal offline exact `--check`;
- optimized `-O` offline exact `--check`;
- normal direct in-memory installed-package capture;
- optimized direct in-memory installed-package capture;
- independent exact associator and table enumeration;
- independent Hellinger and Jensen–Shannon calculations;
- archive, installed-file, module-origin, input-hash, and provenance checks.

I did not run pytest because the read-only sandbox provides no writable temporary directory. I inspected both test files completely. They cover normal/optimized offline replay, exact-byte mutation, exclusive output, corrupted tables, missing archives, existing-output preservation, exhaustive-dimension summaries, split controls, six-job coverage, and distance units. The optional runtime tests are correctly marked `audit`.

## Scientific limits and verdict

The analysis maps retained binary labels into a chosen, post-acquisition Cayley–Dickson coordinate encoding. Package agreement proves arithmetic agreement under that encoding. It does not prove physical non-associativity, calibrated populations, QND behavior, readout causality, stationarity, or completion of the nominal-zero six-job case. The upstream provenance request remains unsent, and no further acquisition is authorized.

**Verdict: bounded PASS for the exact retained-data algebra, source/archive provenance, package-runtime observation, and descriptive distance calculations.**