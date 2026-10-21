# open_gororoba inventory: box-kites, assessors, zero divisors

Compiled 2026-10-17 from a read-only search of the open_gororoba repository
(github.com/Oichkatzelesfrettschen/open_gororoba) at commit
f540610412409004c4f8f0843dbee6352e6a293a; every path, count and claim id below
refers to that tree, and registry/claims.toml at that commit is the status
authority. Nothing was built or run. gororoba_quantum/cd_core.py is the
specification (docs/notes/algebra_circuit_rules.md), so a box-kite fact enters a design only after
recomputation from cd_core, and this inventory locates the sibling code.

## Code clusters

1. crates/algebra_analysis/src/boxkites.rs + boxkites/{types,strut_table,production_rules,cross_assessors,
   coassessor_graph,face_sign_census,imbalance,tests}.rs (~103 tests). strut_table.rs: 6 assessors per
   box-kite, A..F labeling, struts (A,F),(B,E),(C,D). Also boxkite_alignment.rs, grassmannian.rs,
   zd_graphs.rs, exact_annihilator.rs.
2. crates/de_marrais_2000/src/{assessors,trips,count}.rs: NUM_BOX_KITES=7, ASSESSORS_PER_BOX_KITE=6,
   TOTAL_ASSESSORS=42, ZD_PAIRS_PER_ASSESSOR=4, TOTAL_ZD_PAIRS=168, ZD_PAIRS_PER_BOX_KITE=24;
   O_TRIPS 7, S_TRIPS 28.
3. crates/algebra_experimental/src/emanation/ (30 files, ~9447 lines, ~226 tests): trip_sync,
   strut_spectroscopy, sail_loop, sail_classification, twist_transitions, lanyard*, delta_transition,
   brocade, tray_racks, table_builder, skybox. (Docs cite a stale single-file emanation.rs.)
4. Other: cd_kernel (sedenion_membership, mult_table), gororoba_algebra construction/{chingon,cd_tower},
   gororoba_cli_algebra bins {dump_assessors,zd_algebra,motif_census,cd_tower_report},
   gororoba_cli_quantum qec-boxkite-sweep, quantum_core/src/qec_boxkite.rs, brown_1972 zd_criterion,
   sign_imbalance sedenion_foliation, algebra_experimental cd_tower_violations (BOX_KITE_VIOLATION_COUNTS).

## Rocq

proofs/theories/DeMarraisAssessors.v (o_trip 7, s_trip 28, production rules 1-3), BoxKite.v (42 assessors,
7 box-kites), BrownAssessorEquivalence.v (cover + pairwise disjoint), ZDGraph.v (uniform XOR per kite,
seven distinct signatures), proofs/verified/C003_AssessorsBoxkites.v, C1135_BoxKiteFusionRules.v.
Admitted usage not checked.

## Data (data/csv/)

de_marrais_assessors.csv (42), de_marrais_boxkites.csv (42: kite, strut_signature, low, high),
de_marrais_strut_table.csv (7: A..F), de_marrais_boxkite_edges.csv (84: edge_type, sign_solutions),
sedenion_box_kites_clustered.csv, sedenion_zd_edges.csv (360), pathion_zd_edges.csv (3654),
reggiani_standard_zero_divisors.csv (84), reggiani_standard_zero_divisor_pairs.csv (336),
zd_motif_invariants.csv (dims 64/128/256 only), sedenion_nilpotent_candidates.csv (1539),
data/results/higher_cd/pathion_control/ (dim 32: 210 assessors, 465 ZD-graph edges, 2 components).
Legacy 16/32/64 adjacency matrices (LC-0151..0153) are Refuted/Superseded (C-020, C-044, C-450): do not use.

## Claims (status)

- Verified: C-003 (42 assessors, 7 box-kites); C-454 (strut table matches all 7); C-468 (84 ZD cells at
  dim 16); C-470..C-475 (oriented trip sync; DMZ edge count invariant; 8 lanyard faces per kite;
  3 strut pairs per S0 delta transition; 4 brocade relabelings per kite; 28 O-trip sails in 7 loops of 4);
  C-1135 (2 fusion channels per kite, sigma x sigma = 1 + psi); C-1341 (assessor fraction 0.5 for D>=16);
  C-1342 (components D/2-1, nodes per component D/2-2 at D=16,32,64); C-443 (dim 32 complement graph
  15 components: 8 K(2,...,2) heptacross + 7 mixed); C-444 (components = PG(n-2,2) points);
  C-1255 (D=16 flat-band fraction 21/42); C-1107 (alternator counts 336, 5040, 52080);
  partner-graph spectrum {-4,-2,0,2,4} multiplicities {7,14,42,14,7} (C-1309/C-1252).
- Provisional: C-1715 (components 7,15,31,63,127 at D=16..256); C-1716 (densest components are
  cocktail-party K(2,...,2) with m=D/4-1, Laplacian 0^1, (2m-2)^m, (2m)^(m-1); universal motif conjectural);
  C-1718 (243 components, N=D/2-2, rational adjacency); C-1724 (2688 vs 336 conflation in avt.rs doc).
- Refuted/falsified near the program: C-020, C-044, C-025, C-068, C-426, C-455, C-466, C-1329, C-1332,
  C-1352, C-1353, C-1358, C-1461 (holonomy refuted), C-1530, C-1732, C-1372.

## Doc discrepancies in open_gororoba

- docs/book/src/algebra/box-kites.md cites C-050..C-060 for box-kite invariants; those ids are unrelated.
- Same doc names emanation.rs (4400 lines, 113 tests); now a 30-file directory.
- zero-divisors.md calls the 42 "primitive cross-assessor pairs"; they are 42 assessors (84 diagonal ZDs,
  168 or 336 pairs by convention).
