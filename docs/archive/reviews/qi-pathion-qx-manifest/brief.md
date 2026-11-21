# Brief: gororoba-quantum pull request 961 (issue 945), canonical_float in the one-CZ null case generator

Material: branch qi-pathion-qx-manifest-canonical-serializer; the change is `git diff origin/main...HEAD`.
Files: scripts/qi_pathion_one_cz_null_cases.py (`canonical_float` and its three call sites),
tests/scripts/test_qi_pathion_one_cz_null_bracketed.py, the four retained
results/quantum_inspire/cases/pathion_one_cz_null_qx/batch-*/cases.json manifests and their receipts.

## Claims under review

1. `canonical_float` clears the sign of zero in the rounded probabilities and contrasts and leaves every other value
   unchanged.
2. The four retained manifests keep their bytes and the receipt digests that bind them.
3. A rebuild reproduces the retained bytes on linux x86_64 and aarch64; the darwin-arm64 difference is a signed zero.
4. Two new tests fail on the code before the change.

Work read-only; run no provider call.
