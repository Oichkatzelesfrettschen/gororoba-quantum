# Evidence-map resolution: validation boundary

The [resolution design](../../design/evidence-map-resolution.md) and the
[disposition](disposition.json) distinguish completed documentation corrections,
existing main-branch features, open-PR integration, offline audits, and physical
questions. They do not replace the research-state registry.

## Retained files

- [checks.json](checks.json) contains the six extracted 24-mode count vectors,
  the exact fraction results, both 24-job ID lists, the Pauli-series arithmetic,
  source pins, and SHA-256 identities of the supplied source extracts.
- [validation.json](validation.json) records 31 local arithmetic and document
  checks. It is not a repository CI receipt or a new physical result.
- [disposition.json](disposition.json) records sixteen work items with explicit
  actions and closure evidence. No scientific status is promoted by this file.

The input extracts and infographic are conversation-supplied secondary
artifacts. Their hashes identify the inputs used in this pass; they do not
assert those entire original files are retained in this repository. The six
count vectors and job lists needed for the stated arithmetic are retained in
checks.json. Its source paths and commit identities locate the primary records;
the resolution design supplies the corresponding repository links. No compressed
raw-provider result is independently replayed here.

## Arithmetic that can be checked directly

For two count vectors a and b, divide each by its own sum and use
`TV = (1/2) sum_m |a_m/sum(a) - b_m/sum(b)|`. The own ideal is 1/4, 1/2,
1/4 on modes 0, 2 and 4; the predecessor ideal is 1/2, 1/4, 1/4 on modes
1, 3 and 7. Compare each target row with its immediately preceding retained
row. Every count is a nonnegative integer and each vector has 24 entries.

The 24-job identity check is equality of the two complete job-ID sets, with no
duplicates. The pilot total is `24 * 16384 = 393216`. The retained Pauli
analysis contains `27 * 32768 = 884736` shots. Its reference-rate change is
`abs(2409 - 1483) / 32768 = 0.02825927734375`, exceeding `0.02`.

These calculations preserve the causality boundary: the transform distribution
resembles the previous setting, but fixed ordering does not identify the
mechanism. A frozen stop remains a stop.

The source map before editing has Git blob identity
`81cc610c6d5ab60df1e1a812fb4d9552b48bf384`, independently recomputed from the
retrieved text before replacements. Existing research results and retained
provider records are unchanged.

## Checks not claimed

The validation environment has no complete repository checkout, no registered
Codex execution environment, and no access to the pinned ruff/mypy packages.
No production Python changes are pushed. No repository-wide link checker,
source gate, scientific gate, or complete PR tier runs in this pass. Opening a
PR requests review; it does not establish a clean review or a merge approval.

Validate the new relative links and the affected documentation under the
repository's current checks before merging. Existing PR #358 owns the separate
CI/fitter repairs and its required environment validation. This change does
not duplicate or certify them.

No provider account read, QRNG request, circuit upload, simulator/QPU job,
maintenance action, or extra spending is authorized or performed.
