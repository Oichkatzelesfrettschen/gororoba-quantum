# AFLOW crystallographic prototype A_cF4_225_a (FCC Cu-type)

[P] marks a statement on the inspected prototype page. [I] marks the mapping
to the repository's crystallographic comparison. The reading covers the
prototype designation header; the downloadable structure files and property
tables were outside the cited scope.

## Citation and retrieval

- Source: AFLOW crystallographic prototype database.
- Page: <https://aflow.org/p/A_cF4_225_a-001/>
- Page header states: "Face-Centered Cubic (Cu, $A1$, fcc) Structure:
  A_cF4_225_a-001".
- Retrieval: fetched 2026-10-19; response bytes retained only as the hash
  below (external web reference, not hosted).
- Page: 37,260 bytes,
  SHA-256 `55f198df0f98bf73e7d3d690750680df5d4201ba2d8cde5108e706839c63d2ca`.

## Mathematical content used

[P] The prototype label is A_cF4_225_a: Pearson symbol cF4, space group 225
(Fm-3m), copper-type face-centered cubic.

[I] This is the comparison prototype for the repository's finding that the
364-vector D14 kissing configuration, projected onto any 3 of its 14
support coordinates, yields 19 points (origin + octahedron(6) + cuboctahedron
(12)) with point group Oh — the 12-shell being the FCC nearest-neighbor
shell. The repository's audit notes the prototype is shared by copper and
other materials; FCC here is a structural correspondence, not a
copper-specific physical prediction.

## Lattice the projection spans

[I] The 19 projected points are exactly the points of Z^3 with |v|^2 <= 2
(multiplicities 220, 22 each and 1 each by squared norm 0, 1, 2). Their
integer span is Z^3, the primitive cubic lattice (Pm-3m, Pearson cP1); the
12-point cuboctahedral shell alone spans D3, the FCC lattice of this
prototype (Fm-3m, cF4), at index 2 in Z^3. The full 19-point set is the
first two coordination shells of the simple cubic lattice, six neighbors at
radius 1 and then twelve at sqrt(2), which is the reversed shell order the
synthesis note records against FCC. The FCC prototype matches the
cuboctahedral shell only. The counting argument and an spglib and SeeK-path
cross-check are in the [lattice cross-check
evidence](../../evidence/seekpath-lattice-crosscheck/README.md#d14-coordinate-projection).

## Mapping and evidence boundary

[I] AFLOW supplies only the prototype designation. All projections, point
groups, and shell counts are computed in the repository from its own lattice
data. No materials property (beyond the crystallographic designation) is
imported from AFLOW.
