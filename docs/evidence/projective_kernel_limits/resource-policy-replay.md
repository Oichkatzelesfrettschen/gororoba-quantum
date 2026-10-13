# Projective kernel limits replay under the half-CPU policy

The original SHA256SUMS ledger retains its recorded bytes. The separate
SHA256SUMS.resource-policy-replay ledger binds the changed parallel.py worker
default and retains every other artifact identity. Normal and optimized exact
replay reproduced result.json while retaining proof_obligations.json. The worker
configuration supplies resource-policy evidence; speedup requires measurement.

resource-policy-replay.json identifies the source transition. The shared
scripts/check_kernel_resource_policy_receipt.py checks all three mathematical
bundles, including schemas, source digests, duplicate rows, exact artifact
denominators and unchanged data identities. Its --self-test rejects six copied
fixture mutations per bundle and compares retained source hashes before and after.

From the repository root, set PYTHON to the intended interpreter and run:

```sh
"$PYTHON" -B -W error scripts/check_kernel_resource_policy_receipt.py
"$PYTHON" -B -O -W error scripts/check_kernel_resource_policy_receipt.py --self-test
"$PYTHON" -B -W error docs/evidence/projective_kernel_limits/replay.py --check
"$PYTHON" -B -O -W error docs/evidence/projective_kernel_limits/replay.py --check
```
