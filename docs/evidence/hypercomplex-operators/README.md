# Hypercomplex operator evidence

`certificate.json` binds source hashes, exact derivation/stabilizer/Clifford checks, the even five-mode reference and seventeen matrix-propagated probability frames. `probability-evolution.html` displays those local simulation frames. The bundle contains mathematical computation rather than provider acquisitions.

The successor [runtime annotation certificate](certificate-runtime-annotations.json) binds the type-only algebra import in the dynamics module. The import permits the campaign diagnostics to run in the isolated Quantum Inspire environment without loading SymPy. Exact observations agree with the original certificate; floating propagation agrees within the admitted replay tolerance. The original certificate and explorer retain their bytes.

The [parallel runtime certificate](certificate-parallel-runtime.json) additionally binds process-pooled exact pair, derivation, ladder and occupation checks. The [pooled propagation certificate](certificate-pooled-propagation.json) also binds explicit frame pooling. The [dense pooled dephasing certificate](certificate-pooled-dephasing.json) and its [historical source text](dephasing-dense-source.py.txt) retain the implementation that review rejected for its growing collection of dense worker results. The [diagonal dephasing certificate](certificate-diagonal-dephasing.json) and [source text](dephasing-diagonal-source.py.txt) bind the compact-vector correction. The active [formatted diagonal dephasing certificate](certificate-diagonal-dephasing-formatted.json) binds the same correction after pinned formatting. Workers return only length-`size^2` vectors; accumulation follows site order. All scientific certificate fields remain identical; source identities change. All successors preserve the exact-field and floating-tolerance rules.

Replay from the repository root:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/hypercomplex_evidence.py --check docs/evidence/hypercomplex-operators/certificate-diagonal-dephasing-formatted.json
```

Exact fields compare exactly. Floating probability and representative residual fields use absolute tolerance 1e-12. Source changes require a separately retained certificate; the writer refuses to replace different certificate bytes.

The retained [library table](libraries.md) records 275 distributions. The expanded [current inventory](../../state/hypercomplex-libraries/libraries.md) also covers maintained ecosystem/candidate tables and provider PyPI records. `libraries.json` preserves environment-specific pins, observed host versions and import locations. Host observations are snapshots and can differ from the pinned CI or provider environments.

The [design](../../design/hypercomplex-operator-evidence.md) states falsifiers and interpretation boundaries. The [runbook](../../runbooks/hypercomplex-operator-cases.md) states provider cases, pacing and approvals. Hardware acquisitions will supply separate raw records and measured renderings after approval.
