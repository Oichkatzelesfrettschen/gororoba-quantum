# Projector source audit and QX conformance scope revalidation

The 27 October 2026 revalidation accepts the original source/datasource audit
and QX emulator conformance completion scopes with the historical corrections
below. The revalidation inspected checkout revision
`e17cd829bd65dde0fda0fdbc564eb44701297021`. Successful emulator conformance
does not establish successful Tuna hardware qualification.

## Historical wording and acquired hardware result

The [design](../../design/tuna-projector-geometry.md) opening status,
“prospective”, describes the initial pre-acquisition design. The
[QX report](qx-conformance.md) statement that Tuna behavior and early
classical-bit retention remain unmeasured describes the pre-Tuna inspection
and the limits of QX evidence. Its requirement for completed review and fresh
hardware admission checks describes the pre-submission stage.

The subsequent [Tuna qualification report](tuna-qualification.md) records
12,288 completed shots and a failed contrast/early-final screen. The retained
[qualification decision](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/qualification.json)
reports `passed=false`. The [readout diagnosis](readout-cause-diagnosis.md)
investigates that failure; its posthoc explanations do not turn the failed
screen into a successful qualification.

The [ordered readout successor case](../../design/tuna-readout-ordered-response-admission.md)
remains a separate, unapproved acquisition at this revalidation. The consumed
initial Tuna authorization does not authorize that successor.

The [evidence overview](README.md) community CLI inspection refers to
[DeadmanXXXII/Inspire at commit 40301831dac2d804bf692061c27c434be870332f](https://github.com/DeadmanXXXII/Inspire/tree/40301831dac2d804bf692061c27c434be870332f).
That inspection found README/LICENSE documentation rather than an executable
CLI. The overview's installed-stack and “Nothing was installed” statements
describe the initial diagnostic environment and operation. They are historical
observations, not a current machine-wide package inventory or a statement
about subsequent PKGBUILD work.

## Receipt comparison

The earlier completion receipts name revision
`0da3fc555a453f6eeff0392f39d39186c906a536`, which predates the three Markdown
files below. Their receipt-matching bytes first appear at
`f6e4ef6c570f68dabf68b7b7c0a234d89b25ba74`: the comparison located each file
in its Git history and matched the SHA256 of `git show REVISION:PATH` to its
receipt. Comparing against that matching content establishes these changes:

| File | Observed change since receipt-matching content |
| --- | --- |
| `docs/design/tuna-projector-geometry.md` | Appends the qualification-admission link; mathematical derivation, source boundaries, QX screen and acquisition design retain their original text. |
| `docs/evidence/tuna-projector-geometry/README.md` | Adds the completed, failed hardware qualification and the posthoc readout-diagnosis link. |
| `docs/evidence/tuna-projector-geometry/qx-conformance.md` | Updates historical authorization wording and adds the supplemental full-joint-law audit, three total-variation distances, dependence caveat and replay command. |

The revalidation measured these SHA256 values for the three Markdown files:

| File | SHA256 |
| --- | --- |
| Design | `96eeb473ad50cb1e6f7eaa51407d16d532e06bbbdc72f699760120b5010be948` |
| Evidence overview | `432fa77e89441faa871e9267966669e1177d33d482648e48075362f50b82e954` |
| QX report | `881195d241e6f188efdafb1c59fed1226ff0c3f4bcd6b07c80b78f95e2048b96` |

The original receipt-bound source observations and QX evidence retain these
hashes:

| Artifact | SHA256 |
| --- | --- |
| [Datasource connectivity](datasource-connectivity.json) | `19f695aac7392c69881481b23c1b326ae0e3ada0124f909da3ca07a50be44f09` |
| [Usage observation](usage-observation.json) | `bb32387fb3fd779f565c421b70ad557fecb0b3c26755d8c65b7a2327c700626c` |
| [QX conformance](../../../results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/conformance.json) | `ceb6efcf570c43a6e772254716119fa8f555d20279832acd5a9d5968ffbc9c62` |
| [QX results](../../../results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/results.json) | `a0929b26fa2899f2386ee99eccf1226db30c8cd4731dca4de752e1fabf62d3c4` |
| [QX submission](../../../results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/submission.json) | `cd28627c7c58f068171a8469be80c53a8e6c708d24573a77e720de3106455642` |
| [Conformance checker](../../../scripts/qi_projector_conformance.py) | `91673afc2ab504a13413d78ec2b512bcd99370fb56b135e35eb7f0ad20b8aff9` |

## Verification and bounded conclusions

The pinned Python 3.14.7 interpreter, with `GOROROBA_WORKERS=2`, replayed:

```sh
"$PYTHON" scripts/qi_projector_distribution_audit.py --check \
  results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/joint-law-audit.json
```

The checker printed `QX full-law audit matches`. Relative file targets in the
three original Markdown files resolved; that path check did not validate
anchors. The supplemental audit remains descriptive emulator evidence.

The inspected changes support renewed completion receipts for
`source-and-instrument-audit` (the source scope and distinction between
provider connectivity and local dependencies) and `qx-conformance-case`
(the approved three-circuit, 2048-shot emulator batch, bound raw results and
descriptive analysis). The historical corrections in this note form part of
those bounded conclusions.

Successful Tuna qualification, restored calibration access, full causal
campaign readiness, current SDK inventory and successor provider approval
remain outside those completion scopes. The
[ordered-response verification record](readout-ordered-response-verification.json)
retains its original 59-file preservation observation and enumerated hashes.
This revalidation leaves that observation's scope intact; the Markdown and
receipt-artifact comparisons above establish only their named surfaces.
