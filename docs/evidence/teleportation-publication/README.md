# Teleportation publication evidence contract

The two editable SVG masters retain the audited October evidence snapshot.
They are not a report of a new experiment. [sources.json](sources.json)
binds the original v6 archive, each master and three historical repository
records. New XML IDs identify every displayed Tuna route, match rate and
interval, its shot denominator, and both Kingston endpoint cards. The
claim that the IDs leave every visible element and all geometry unchanged
is asserted by the author; the v6 original bytes are not retained here, so no
check here verifies it. The Kingston plate displays the measured-statistics
summary of the collect record; the replayed-statistics summary of the same
record is never displayed.

- [Tuna-17 master](tuna17.svg): four different input/route cells, terminal
  readout, basis-dependent all-shot decoding, no common-channel average.
- [Kingston master](kingston.svg): a distinct dynamic energy-control
  experiment, static phase compensation in both executable branches,
  outcome-dependent Y-rotation sign, model-Hamiltonian energy units and an
  uncrossed stronger floor. The positive unitary comparison is not a
  general entanglement witness or a physical-work extraction claim.

## Build and verification

[publication_plates.py](../../../scripts/publication_plates.py) uses the
[shared validator](../../../gororoba_quantum/publication_evidence.py) to
check record identities before deriving displayed strings. A changed or
missing source is an error.
Git blob SHA-1 pins repository identity; every release also records SHA-256
of every source read and every emitted asset. In a git checkout the builder
also resolves `git rev-parse REVISION:PATH` for each source at the manifest's
`source_revision` and refuses a blob that differs; the receipt field
`source_revision_check` reads `verified`, or `unverified: REASON` where no git
metadata can answer. No archive Python is executed.

```sh
python scripts/publication_plates.py --out "$NEW_RELEASE_DIRECTORY" --render
```

Python is sufficient for source/SVG checks. PNG export and rendered decoder
bounds additionally require Inkscape and the SVG's DejaVu Sans font. Font
files are not distributed. The renderer version enters `release.json`;
PNG byte equality across different renderers/fonts is not assumed.

The on-demand gate `core-teleportation-publication-source-bound-release` of
[ci/gates.json](../../../ci/gates.json) runs `publication_plates.py --check`,
which builds the full source-bound release in temporary storage and compares
the receipt with the manifest (sources, revision check, master digests).

An explicit `--layout-only` run works without historical records, emits
`evidence_bound: false`, and cannot be described as source validation.
Both modes retain `hardware_replayed: false`: display/source consistency
is not independent raw-shot replay, provider provenance verification, or a
fresh scientific replication. Raw acquisition checks remain with the
existing record readers and on-demand historical replays.

The builder refuses existing release destinations. It validates master
hashes, SVG structure, notation, source-specific data nodes, all A/B native
subscripts and the decoder's 12-pixel minimum horizontal clearance. Bounded
admission tests use synthetic JSON/XML only, with failure mutations for
digest drift, duplicate keys, nonfinite values, hidden or missing endpoints
(`opacity`, `fill-opacity`, `font-size`, `visibility`, `display`, `fill`
presentation attributes), processing instructions, source ambiguity, a wrong
source blob id and path escape. The checks raise under `python -O` too;
publication validation does not depend on stripped assertions.

## Scope and remaining evidence

The builder and validator bind each plate to a repository-owned source
manifest, and bounded regressions cover them. The
[fixed-route six-state design](../../design/fixed-route-teleportation-benchmark.md)
addresses the state/topology confound prospectively, without relabelling
the historical data as a completed benchmark. Its acquisition and the
live-output/reference-output tests are not performed.

External reference, unverified: the gororoba-open repository may carry a
module named `quantum_core::teleportation_frame`. This tree holds no copy of
it, no local gororoba-open ref names it, and nothing here asserts or relies on
its behavior.

Work status and acquisition holds: [plan record](../../state/plans/teleportation-publication-and-fixed-route.json).
