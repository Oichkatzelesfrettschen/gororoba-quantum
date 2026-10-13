# Kernel determinant replay under the half-CPU policy

The original SHA256SUMS ledger retains the admitted source bytes. The separate
SHA256SUMS.resource-policy-replay ledger binds the changed parallel.py worker
default while retaining every other artifact identity. Normal and optimized
finite-result replay reproduced result.json and proof_obligations.json; the
resource change supplies configuration evidence rather than a speedup claim.

resource-policy-replay.json records the source transition. The standalone
scripts/check_kernel_resource_policy_receipt.py checks its schema, canonical
source, every digest, duplicate ledger rows and the complete denominator.
Its --self-test uses copied fixtures to reject six metadata, denominator and
result mutations while comparing all original source hashes before and after.
Both Python modes join the CI manifest.

From the repository root, set PYTHON to the intended interpreter and run:

```sh
"$PYTHON" -B -W error scripts/check_kernel_resource_policy_receipt.py
"$PYTHON" -B -O -W error scripts/check_kernel_resource_policy_receipt.py --self-test
"$PYTHON" -B -W error docs/evidence/kernel_determinant/replay.py --check
"$PYTHON" -B -O -W error docs/evidence/kernel_determinant/replay.py --check
```
