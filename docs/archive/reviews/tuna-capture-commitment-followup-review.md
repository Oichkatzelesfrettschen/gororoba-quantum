The staged changes close the requested mutation and integration gaps at the byte-binding level. I found one remaining test-evidence weakness and one inherited robustness limitation. Static inspection covered all three staged files in full.

## Verification

| Requirement | Static result |
|---|---|
| Same-length coherent body substitution | Confirmed. The 9-byte `{"id":11}` body becomes 9-byte `{"id":22}`, with SHA-256 recomputed for the substitute ([test:69](../../../tests/scripts/test_qi_tuna_capture_commitment.py)). |
| Every receipt position | Confirmed. `position` spans `range(4)`, and the replacement is installed at that position ([test:63](../../../tests/scripts/test_qi_tuna_capture_commitment.py)). |
| Status mutation | Confirmed. Valid status `200` becomes `201` at every position ([test:78](../../../tests/scripts/test_qi_tuna_capture_commitment.py)). |
| Whole coherent replacement | Confirmed. The checkpoint changes from job 11 to 22 while all four receipts receive the changed path, body, and recomputed digest. The replacement fails against the original commitment and succeeds against its own ([test:84](../../../tests/scripts/test_qi_tuna_capture_commitment.py)). |
| Canonical Unicode/escape vector | Confirmed. The vector includes `é`, newline, quote, tab, and Unicode content type, with a literal expected digest ([test:93](../../../tests/scripts/test_qi_tuna_capture_commitment.py)). |
| Ordered query vector | Confirmed. The canonical vector contains two ordered query pairs rather than an object that could collapse ordering or multiplicity ([test:100](../../../tests/scripts/test_qi_tuna_capture_commitment.py)). |
| Direct scoring removed | Confirmed. `Fraction`, `score_sequence`, and the sequential-score assertion are absent. The integration stops after association decoding and checks only decoded counts ([integration:108](../../../tests/scripts/test_qi_tuna_readback_collection.py), [integration:200](../../../tests/scripts/test_qi_tuna_readback_collection.py)). |

## Remaining weaknesses

1. **SLOPPY — “external commitment” remains implementation-generated.**

   The mutation test assigns `fixed_commitment = capture_commitment(original_capture)` ([test:75](../../../tests/scripts/test_qi_tuna_capture_commitment.py)). The commitment remains fixed across mutations, so the test correctly calibrates binding. It is neither pre-existing nor externally authenticated, which the archived review explicitly requested at [review:43](../../../docs/archive/reviews/tuna-capture-commitment-review.md).

   Remedy: replace that computed value with an independently derived literal digest or retained fixture receipt. The separate canonical Unicode vector supplies independent encoding evidence, but it does not make this mutation test external.

2. **SLOPPY — direct construction still admits unbounded envelope metadata.**

   The producer bounds checkpoint and body bytes but leaves path length, content-type length, query count, query-key length, and integer magnitude unbounded ([producer:20](../../../scripts/qi_tuna_capture_commitment.py), [producer:31](../../../scripts/qi_tuna_capture_commitment.py)). This remains a robustness issue for direct callers, rather than a demonstrated transport-path defect.

3. **Inherited boundary — admission remains deliberately absent.**

   The integration still derives the expected commitment from the same captured object ([integration:197](../../../tests/scripts/test_qi_tuna_readback_collection.py)). Removing scoring prevents that self-comparison from masquerading as scientific admission, and the renamed test accurately says “without admission.” The staged files still provide no independent account, request, timing, durability, quarantine, or charge adjudication. The producer documents that boundary correctly at [producer:1](../../../scripts/qi_tuna_capture_commitment.py).

## Exact staged SHA-256 identities

| Staged artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_capture_commitment.py` | `7e5eac896f14dfa3757f27e7d4a35ead98e857f06ab5b13eb91a140fc146b97e` |
| `tests/scripts/test_qi_tuna_capture_commitment.py` | `6c285e7ec517fdf8eebb3558f9caf41733e2acfea4951e02c30d17a51c7ccd56` |
| `tests/scripts/test_qi_tuna_readback_collection.py` | `0c39d0b512cb4a8f5f8815d1e8b8441d780eba254517dd5175cb32f4f3e27fbe` |

Verdict: the commitment primitive and requested mutation coverage are sound within the declared byte-binding boundary. Direct scoring has been cleanly removed. Full closure of the archived review still requires an actually pre-existing external commitment fixture; full acquisition admission remains outside these staged artifacts.

The review ran statically against HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`. Initial and final staged hashes matched, and the four reviewed working-tree files matched their index entries. I ran no tests, linters, imports, network access, credentials, provider operations, jobs, uploads, draws, messages, or edits.
