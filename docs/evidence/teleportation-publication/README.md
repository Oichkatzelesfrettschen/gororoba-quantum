# Teleportation publication evidence contract

The two editable SVG masters retain the audited October evidence snapshot.
They are not a report of a new experiment. [sources.json](sources.json)
binds the original v6 archive, each master and three historical repository
records. New XML IDs identify every displayed Tuna route, match rate and
interval, its shot denominator, and both Kingston endpoint cards. Adding
these IDs changes no visible element or geometry.

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
missing source is an error, not permission to reuse yesterday's label.
Git blob SHA-1 pins repository identity; every release also records SHA-256
of every source read and every emitted asset. No archive Python is executed.

```sh
python scripts/publication_plates.py --out "$NEW_RELEASE_DIRECTORY" --render
```

Python is sufficient for source/SVG checks. PNG export and rendered decoder
bounds additionally require Inkscape and the SVG's DejaVu Sans font. Font
files are not distributed. The renderer version enters `release.json`;
PNG byte equality across different renderers/fonts is not assumed.

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
digest drift, duplicate keys, nonfinite values, hidden or missing endpoints,
source ambiguity and path escape. The checks raise under `python -O` too;
publication validation does not depend on stripped assertions.

## Discussion closure and remaining evidence

The conversation produced layouts and standalone checks; it did not land a
repository-owned source binding or common-route experiment. This change
adds those interfaces and their bounded regressions. The
[fixed-route six-state design](../../design/fixed-route-teleportation-benchmark.md)
addresses the state/topology confound prospectively, without relabelling
the historical data as a completed benchmark. Its acquisition and the
live-output/reference-output tests remain unperformed here.

The Rust consumer in gororoba-open's `quantum_core::teleportation_frame`
contains only reusable phase-quotiented Clifford/Pauli-frame algebra, with
exact matrix-oracle tests. It holds no hardware data, channel-fidelity claim
or duplicate publication history. Documents and infrastructure repositories
receive no copied scientific records or operational changes from this work.

Work status and acquisition holds: [plan record](../../state/plans/teleportation-publication-and-fixed-route.json).
