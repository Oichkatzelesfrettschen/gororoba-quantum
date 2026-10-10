# open_gororoba survey -- deep notes

Companion to `open_gororoba_survey.md`. This file records the evidence trail,
the derivations, the scripts, and the side observations behind the survey. It
is organized so that every number in the survey can be traced to a command or a
file:line here.

## 1. Provenance and replay

| Item | Value |
| --- | --- |
| Repository | open_gororoba, HEAD fe668020 ("algebra_analysis: state the pathion zero-divisor component convention (15 cross-pair, 22 all-plane)") |
| Working tree at start | `.gitignore` modified, `.ignore` untracked; both pre-existing; survey changed nothing |
| Rocq | 9.1.1 (`rocq --version`), checker `rocqchk` |
| Python | 3.14.7 |
| numpy / sympy | 2.5.3 / 1.14.0 |
| Interpreter variable | `PYTHON=${PYTHON:-python3}` |

Commands used against the repository (all read-only):

```sh
# every .v file: count by directory
find . -name '*.v' -not -path './.git/*' | sed 's|/[^/]*$||' | sort | uniq -c
# admission/axiom scan outside comments and strings: section 9 script
# axioms of a built module, no files written:
cd proofs && rocqchk -o -R theories OpenGororoba -R verified OpenGororobaVerified OpenGororobaVerified.C958_ZDGraphTopology
# staleness of built objects:
for v in theories/*.v verified/*.v; do [ "$v" -nt "${v%.v}.vo" ] && echo "STALE $v"; done
# stale module recompiled in a scratch directory (nothing written under the repository):
coqc -R $P/theories OpenGororoba -R $P/verified OpenGororobaVerified PathionZDGraph.v   # run in a scratch dir
```

Not run, with reason: `cargo test`/`cargo build` (writes `target/` into the
repository; the survey is read-only); full Rocq rebuild (writes `.vo`);
`rocqchk` on Moreno/Brown/Schafer/Float modules (time); the heavy-lane Rust
tests (hours, GPU).

## 2. Search log

Directories excluded from keyword searches because they hold generated logs
and mirrors: `target`, `vendor`, `build`, `logs`, `out`, `archive`,
`reports/gates`, `data/output/audit`, `crates/data_core/src/registry_mirrors`,
`registry/data`, `registry/knowledge`, `registry/markdown_export`.

| Pattern | Result |
| --- | --- |
| `Shor`, `RSA`, `integer factoring`, `prime factor` | no algorithmic hit; "factoring" appears in `group_theory.rs:136` (smallest prime factor helper), `BellCHSH.v:26` (algebraic factoring), a comment in `flavor_lifts/src/basis.rs:252`, and a prose sentence in `DE_MARRAIS_PRESTO_DIGITIZATION.md:232` (Kummer ideals) |
| `QFT`, `quantum Fourier` | registry text only, meaning quantum field theory (for example `docs_tcmt_*`) |
| `period finding`, `order finding`, `modular exponentiation`, `phase estimation`, `discrete log` | none |
| `modpow`, `powmod`, `totient`, `gcd`, `Miller-Rabin`, `BigUint` | `num-bigint` is a workspace dependency "for the Monster group order" (`Cargo.toml:170`); no modular arithmetic code |
| `qubit`, `CNOT`, `Toffoli`, `QASM`, `qiskit` | `quantum_core::{hardware,mps,peps,tensor_network_classical}`; `docker/Dockerfile` and `bin/run_quantum_container.sh` mention qiskit-style tooling for the container only |
| `butterfly` | list in survey section 4; four unrelated senses (CD Cariow schedule, bit permutation, IDCT, Hofstadter butterfly) plus GPU warp reduction |
| `fold`, `folding` | only generic uses (rayon fold, "manifold"); no CD "folding" concept as such. The nearest concepts: the four-case sign recursion, `CompressedSignTable`, de Marrais Theorem 11 table embedding, the fold recursion derived in section 8 |
| `fwht`, `WHT`, `Walsh`, `Hadamard` | `crates/fwht`, `cd_kernel::turboquant::*` (KV-cache quantization), `cariow_factorization.rs`, `C1636`, MPS Hadamard gates, `CDFidelity.v` axiom |

## 3. Rocq corpus detail

### 3.1 Counts

| Location | `.v` files |
| --- | --- |
| `proofs/theories` | 136 |
| `proofs/verified` | 162 |
| `proofs/extraction` | 4 |
| `curated/01_theory_frameworks` | 10 |
| `data/output/audit/claim-family-evidence-adjudication` | 1 |

`proofs/metrics/summary.csv` reports 35 theory files and 104 verified files
(older snapshot; the tree has 136 and 162). `docs/THEOREMS.md` indexes 162
files, all `kernel_checked`.

### 3.2 Scan for admissions and axioms (comment- and string-aware)

Totals over all 313 files: `Admitted` 0, `admit` 0, `Abort` 0, `Conjecture` 0.
Files under `proofs/` with `Axiom` or `Parameter` tokens (count of Axiom/Parameter):
Brown1972ChapterIII 3/6, C1538_MorZDSymmetry 4/0, C1539_MorSkewSymm 12/6,
C1542_MorVlambdaOrbit 1/1, CDDoubleFunctor 7/8, CDFidelity 1/1, CDTraceZero
33/12, CarlsonIntegrals 10/0, FloatAxioms 9/7, HModuleDim 9/7,
HurwitzTheorem 4/2, SStructuralGaps 12/3, TightBindingTopology 4/5,
C958_ZDGraphTopology 1/0. Under `curated/`: ConfineModel 0/2 and six
`confine_theorems_*_axioms.v` / `_rocq_axioms.v` files with 2590, 5182, and
10366 axioms each.

Module-type structure of the Moreno lane: C1538 declares
`Module Type CDAlgInnerTrace` (line 43) and `Module MorZDSymmetry (Alg :
CDAlgInnerTrace)` (line 59); C1539 declares `Module Type CDAlgMoreno` (28) and
`Module MorSkewSymm` (66); CDTraceZero declares `Module Type CDAlgTraceZero`
(59) and `Module TraceZero` (147). The axioms are interface obligations.
`MorenoSedenionInstance.v:33` instantiates `CDAlgMoreno` with the sedenions;
its header states the kernel-equality part of Moreno Theorem 1.15 still rests
on functor-internal axioms.

### 3.3 `rocqchk -o` results (non-Stdlib axioms only)

Run on built `.vo` files. "none" means the Axioms list contained only
`Stdlib.*` entries (classical reals, functional extensionality) or was empty.

| Module | Non-Stdlib axioms |
| --- | --- |
| C1636_Cariow2013SedenionSchedule | none |
| C1469_TowerTrilinearity | none (no axioms at all) |
| C1467_XORSignCocycle | none (no axioms at all) |
| C1471_HigherCDTrilinearity | none |
| C1468_SlotShiftEquivariance | none (no axioms at all) |
| HigherCD | none |
| M3IsAssociator, M3IsAssociatorPathion | none (no axioms at all) |
| C1140_PathionQuantizedGap | none |
| PathionZDGraph | stale `.vo`: `pathion_zd_components`; rebuilt from current source: closed under the global context |
| BrownAssessorEquivalence, DeMarraisAssessors | none |
| C1141_ZDGraphGeneralStructure | none (no axioms at all) |
| C957_VoudonZD, C956_RoutonAVT | none |
| WilmotCDStructure | none (no axioms at all) |
| CDFidelity | `wht_assoc_image`, `wht_preserves_associator` |
| SStructuralGaps | 15: `s1_g2_stabilizer_is_su3`, `s2_brown_thm714_trace_restriction`, `s2_brown_thm715_abstract`, `s2_brown_lemma717_normalized_zero_divisors`, `s3_hurwitz_dim_must_be_1248`, `s3_hurwitz_uniqueness`, `s4_e8_octonionic_origin`, `s4_f4_is_aut_j3o`, `s5_three_generations_from_T`, `s6_aut_oct_is_g2`, `s7_clifford_8_periodicity`, `s7_spinor_rank_is_rho`, `su3_f`, `abstract_sed_mul_lo`, `abstract_sed_mul_hi` |
| CDDoubleTower, ZD_Criterion, C1135, C1137 | none |
| C881_GF2CubicMinDegree, C1142_XORScatterGatherDuality | none (no axioms at all) |
| C1628_IDCT8ButterflyCompaction | none |
| WilmotPathionRetraction, WilmotRetractionTheorem, C003, SedenionXorGroup, CDSignSection | none (no axioms at all) |
| CDSignBridge, C1470, PathionAssociator, CDPowerAssociative, CDInnerProduct, BrownGeneralizedCD | none |
| C958_ZDGraphTopology (run separately) | `zd_graph_three_components` |

### 3.4 Per-file notes beyond the survey tables

- `CDSignBridge.v:1-45`: explains why `vm_compute` cannot reduce goals over R
  and uses `cbv` plus `ring`; the 64-case octonion theorem takes 3 to 10
  seconds (per its header). Claims "tower-rewrite speedup" for the norm lemma.
- `CDSignSection.v:32-60`: packages the sign recursion into fixed-dimension
  sections (`Oct8Signs`, `Sed16Signs`, `Path32Signs`); `check_fano_line_signs`
  verifies the seven oriented Fano lines.
- `M3IsAssociator.v:57-127`: "m3 = Assoc" statement for all 210 ordered
  distinct imaginary octonion triples (7*6*5), boolean reflection by
  `vm_compute`. 42 Fano-line triples have zero associator coefficient; the 168
  others have absolute value 2.
- `M3IsAssociatorPathion.v:1-30`: header concedes confusion about 455 versus
  4495 versus 26970 triple counts; the proved content is the sign-table
  agreement and the 210/2730 counts.
- `C1474_FuelAdequacy.v:55-98`: `fuel_adequate_{4,8,16,32,64}`,
  `fuel_mono_{16,32,64}`, `fuel_insufficient_{16,32}`. Fuel is the recursion
  depth bound; the Fixpoint needs fuel = log2(dim) + 1.
- `C1469_TowerTrilinearity.v` header says "Cocycle Properties at dim=16, 32,
  64" and "Trilinearity" in its name; the body contains no trilinearity.
- `C1471_HigherCDTrilinearity.v:1-20` header: "each level uses ONLY the
  previous level's lemmas". The theorem `X_assoc_trilinear_scale_1` is
  `assoc (scale r a) b c = scale r (assoc a b c)`.
- `HigherCD.v` defines the doubling `(a,b)(c,d) = (ac - conj(d) b, d a + b
  conj(c))` over nested records; 65536 is the last level.
- `CDDoubleTower.v:1-30`: header claim "verified CD tower from dim=1 to
  dim=32 with no per-level proofs".
- `C1142_XORScatterGatherDuality.v:1-25`: the hardware consequence stated is
  that the gather form has no write collisions and maps to Tensor Core tiles
  (`gpu/tensor_avt`).
- `C1135_BoxKiteFusionRules.v:1-30`: "Ising anyon fusion rule sigma x sigma = 1
  + psi" is an analogy; the theorem is that two assessors of each box-kite
  yield products differing in sign at a specific component (cbv + ring + lra).
- `C1137`: the "quantized topological gap" is `|[e_i, e_k, e_{i XOR 8}]|^2 = 4`
  with probes chosen per i; "uniform value 4" is a property of selected
  probes, not of all probes.
- `C881_GF2CubicMinDegree.v:1-40`: reformulation of a refuted claim; labels and
  classes were extracted at runtime from `algebra_analysis::projective_geometry`
  and hard-coded.
- `ParityClique.v` / `C882`: edge counts `n(n-1)/2` for the K_n claimed in the
  parity-clique decomposition; the decomposition itself is a Rust-side claim.
- `C1628_IDCT8ButterflyCompaction.v`: the decoder-side justification for
  compacting a two-pass IDCT onto a fragment dot-product ALU; no relation to
  the CD tower.
- `proofs/extraction/*`: extraction experiments (R2VB DP4, quaternion, FP24).
- `FloatAxioms.v`, `FloatRealBridge.v`, `FP24Representable.v`: floating-point
  model axioms for the DP4/R300 work.
- `proofs/theories/Brown1972Chapter*.v`, `BrownGeneralizedCD.v`: Brown 1972
  dissertation lanes; Chapter III declares a module-type algebra with norm
  axioms.
- Physics-side proofs (ADM, Casimir, Bekenstein, Brans-Dicke, Cassini, GPB,
  CHSH, SU(3), E6/E7/E8/F4 Cartan derivations, Hofstadter/Chern, TCMT) are
  outside the CD scope of the survey.

### 3.5 Topic map of the 298 theory and verified files

CD algebra core and linearity: Prelude, CayleyDicksonAlgebra, Quaternion,
Sedenion, Pathion, HigherCD, OctonionNorm, OctonionInverse, CDLinearLemmas,
CDNegLemmas, CDScalarExtension, CDConjAntimorph, CDInverse, CDInnerProduct,
CDFusedBilinear, CDTraceZero, CDPowerAssociative, CDDoubleFunctor,
CDDoubleTower, CDTowerInstantiation, DicksonCDProcess, Dickson1921.

Signs and XOR: M3IsAssociator, M3IsAssociatorPathion, CDSignBridge,
CDSignSection, CDSignHalfStep, SedenionSignBridge, SedenionXorGroup,
C1467, C1468, C1469, C1470, C1471, C1474, C1142, C017, C034.

Associators and alternativity: CDAssociator, SedenionAssociator,
PathionAssociator, HomotopyTransferAssociator, AlternatorTraceExclusion,
SedenionAlternativityFails, SedenionGapWitnesses, C001, C011, C030, C1455.

Zero divisors, box-kites, Fano: BoxKite, ZDGraph, PathionZDGraph, ZD_Criterion,
BrownAssessorEquivalence, DeMarraisAssessors, ParityClique, GF2Algebra,
FanoPlane, WilmotCDStructure, WilmotPathionRetraction, WilmotRetractionTheorem,
Moreno1997, MorenoKerLaNonAlternative, MorenoSedenionInstance, C1538-C1549,
C1627, C003, C004, C005, C010 (two), C013-C016, C026, C957, C958, C958b,
C1135, C1137, C1140a/b/c, C1141, C881, C882, C1636-C1638.

Cariow/butterfly: C1636, C1628, IDCT8EvenOdd, IDCT8ExactBound, R2VBTransformDP4.

Not CD: the remainder (cosmology, optics, entropy, quantum inequalities,
Lie algebra derivations, float semantics).

## 4. Rust crate map (sizes are `.rs` line counts)

| Crate | Lines | Role for this survey |
| --- | --- | --- |
| `cd_kernel` | 29018 | sign table, multiply, associator, Cariow, trigintaduonion, turboquant |
| `algebra_analysis` | 36490 | box-kites, zero divisors, annihilators, codebooks, imbalance |
| `algebra_experimental` | 54576 | emanation tables, tower violation counts, novel_algorithms, Leech/pathion, Majorana braiding |
| `gororoba_algebra` | 40573 | typed tower 32..1024, GPU Voudon, tensor AVT |
| `quantum_core` | 24138 | MPS, Grover, hardware profiles, QEC-labeled modules |
| `fwht` | 263 | Walsh-Hadamard + fast JL rotation |
| `wilmot_2025` | 499 | counting formulas |
| `de_marrais_2000` | 540 | assessor enumeration |
| `sign_imbalance` | 9217 | signed-graph imbalance |
| `moreno_1997`, `brown_1967`, `brown_1972`, `schafer_1945`, `dickson_1919`, `hurwitz_1898` | 969, 334, 2711, 448, 894, 771 | paper-scoped emulations |
| `lattice_filtration` | 2923 | Lambda_256..2048 filtration for mass spectrum |
| `cd_spin_bridge`, `spin_tomography_core` | 594, 1060 | two-qubit channel parameters |

`algebra_analysis::boxkites::find_box_kites` returns an empty vector unless
dim = 16 (`boxkites.rs:62`). The census for higher dimensions is
`motif_components_for_cross_assessors(dim)` and
`motif_components_for_all_planes(dim)`.

`algebra_experimental::novel_algorithms` holds 30 files of exploratory code.
The ones relevant to the survey: `deep_factorization.rs` (heuristic, 95 lines),
`padic_cd_crypto.rs` (32 lines: scale by a constant, multiply by the vector
`[0.5; 16]`, test asserts a nonzero first component),
`sedenionic_braid_compiler.rs` (39 lines: fold `cd_multiply` over 16-vectors),
`zd_tensor_network.rs` (maps bond indices to sedenion basis elements and skips
contractions between orthogonal zero-divisor sets).

## 5. Dimension ladder, full numbers

### 5.1 Cross-pair motif census (from the Ti tests; CSV corroboration)

Dim 128, 63 components of 62 nodes. Classes (edges: count): 180:9, 516:8,
756:7, 948:7, 1092:7, 1284:7, 1524:8, 1860:10. Sum of counts 63; total edges
9*180 + 8*516 + 7*756 + 7*948 + 7*1092 + 7*1284 + 8*1524 + 10*1860 = 65100.
The 1860-edge class is K_{2,...,2} with 31 parts, 60-regular; the 180-edge
class has degrees [4^60, 60^2].

Dim 256, 127 components of 126 nodes. Classes (edges: count): 372:10, 1092:9,
1716:8, 2436:8, 2676:7, 3396:7, 3444:7, 4020:7, 4164:7, 4740:7, 4788:7,
5508:7, 5748:8, 6468:8, 7092:9, 7812:11. Total 523404. The 7812-edge class is
K_{2,...,2} with 63 parts, 124-regular; the 372-edge class has degrees
[4^124, 124^2].

CSV files: `data/csv/cd_motif_components_{16,32,64,128,256}d.csv` (rows 7, 15, 31,
63, 127 plus header), `cd_motif_edges_{16,32,64,128}d.csv` (rows 84, 924,
7980, 65100 plus header), `cd_motif_nodes_{16,32,64,128}d.csv`,
`cd_motif_summary_by_dim.csv` (dims 16 and 32 only), `apt_dimensional_census_summary.csv`
(dims 4..32), `de_marrais_*.csv` (dim 16).

### 5.2 Scaling laws the tests assert (16..128)

components = dim/2 - 1; nodes per component = dim/2 - 2; maximum K_2-type part
count = dim/4 - 1; motif classes = dim/16; K_2-type component count = 3 +
log2(dim); largest component edges = C(dim/2 - 2, 2) - (dim/4 - 1).
Octahedra occur only at dim 16.

### 5.3 Alternator counts and growth ratio

Ratios V(2N)/V(N) computed from the table in `cd_tower_violations.rs:86`:
15.0000, 10.3333, 9.0000, 8.4667, 8.2258, 8.1111, 8.0551, 8.0275, 8.0137,
8.0068 (dims 16->32 up to 8192->16384). The source comment gives 8.0145 for
8192; the listed constants give 8.0137. The counts use the convention
"ordered triples (i, j, k), i < j, k free, [e_i, e_j, e_k] + [e_j, e_i, e_k]
nonzero"; the source notes the literature formula (N-1)(N-2)(N-8) counts
something else.

### 5.4 Imbalance ratio

0.000, 0.307, 0.377, 0.388, 0.385, 0.381, 0.378 at dims 16..1024 (comments in
`imbalance.rs:16` and `tests.rs:6960`); the claim is convergence to 3/8 from
above, a statement about a sequence of seven values.

### 5.5 Emanation tables

Strut constants S = 1..dim/2 - 1. Regime counts 1, 2, 4, 8 at dims 16, 32, 64,
128. DMZ totals at dim 32: 8 * 168 + 7 * 72 = 1848; at dim 64: 9 * 840 +
7 * 456 + 8 * 168 + 7 * 552 = 7560 + 3192 + 1344 + 3864 = 15960; the DMZ count
of every regime equals twice the edge count of the matching motif class of
section 5.1 (dim 64: 840/420, 456/228, 168/84, 552/276; dim 128: 360/180,
1032/516, 1512/756, 1896/948, 2184/1092, 2568/1284, 3048/1524, 3720/1860), so the
total DMZ count at dim D is twice the cross-pair edge total E(D). The totals
168, 1848, 15960 at dims 16, 32, 64 equal the cocycle-violation counts at dims
8, 16, 32 (section 8.11).

### 5.6 Wilmot formulas, extended

`blade_count(m) = 2^(m+3) - 1`; `zd_count(m) = N(N-1)(N-3)(N-7)/16`. From the
formula (not from `WilmotCDStructure.v`, which evaluates m <= 2): m = 3
(dim 64) gives 820260; m = 4 (dim 128) gives 14881860. `wilmot_2025` tests
assert triad counts 35, 455, 4495, 39711 and associative triads 7, 35, 155, 651.

### 5.7 What each of 2048 and 4096 has

2048: alternator count 2132832240; `Lambda_2048` of 2048 lattice points with 139
forbidden prefixes (`prefix_chain_theorem.rs:1-30`); `cd2048_*` Rocq
definitions and scale lemmas; `test_imbalance_ratio_dim2048` (ignored, no
recorded value); C-1512 sampled sign check; `data/csv/cayley_dickson/2048d_lattice_mapping.csv`
(2048 rows, basis element to {-1,0,1}^8 point).

4096: alternator count 17121206256; `is_in_lambda_4096` and
`enumerate_lambda_4096` (`lambda_predicates.rs:110,117`); `cd4096_*` Rocq
definitions and scale lemmas; `fast_associator.rs` memory estimate; APT
placeholder.

Both: no zero-divisor census, no box-kite count, no annihilator data, no
emanation-table data, no Rocq theorem about signs.

## 6. Name collisions and traps

- "Rocq at 512/1024/2048": thread-count capability model (survey 2.5).
- "Pathion": 32D everywhere except `data/csv/64D_Pathion_Adjacency_Matrix.csv`.
- "Voudon": 256D; `DekaVoudon` 1024D; `Endekavoudon` 2048D in
  `cd_tower_violations.rs` (renamed from "Icosikaivoudon"); 4096D is "Dodekvoudon"
  there and "CD-4096" elsewhere.
- "Fano resonance": optics (TCMT), not the Fano plane.
- "Butterfly": Hofstadter spectrum, IDCT even-odd split, CUDA warp reduction.
- "Hadamard": Hadamard product (Cariow), Hadamard matrix (WHT), and Hurwitz-
  Hadamard-style norm identities in prose.
- "QFT": quantum field theory.
- "Modular": de Marrais (s,g)-modularity; "modular tensor" categories in curated
  CSVs; modular chaos plot artifact.
- "Hurwitz": Hurwitz's composition theorem (1898) versus Hurwitz groups of order
  84(g-1) (footnote 19 of the de Marrais source).
- "Stabilizer": `StabilizerLikeCode` in `quantum_core::stabilizer_like` is a
  trait for non-Pauli parity structures, not Pauli stabilizer groups.
- "Compiler": `sedenionic_braid_compiler` folds products; no gate IR.
- "Cocycle": `C1467` theorem names versus the group 2-cocycle identity.
- "Cariow multiplier count": 122 (`cariow_factorization.rs`, C1636, C-1493)
  versus 84 (`fast_associator.rs:26`).

## 7. Source documents named in the repository (not re-verified)

de Marrais 2000 (arXiv:math/0011260), 2004 "Flying Higher Than A Box-Kite",
"Presto! Digitization I" (arXiv:math/0603281), "Placeholder Substructures III"
(arXiv:math/0703745); Moreno 1997 (arXiv:q-alg/9710013) and 1998; Brown 1967,
1972; Reggiani 2024; Wilmot 2025 (arXiv:2505.11747v3); Cariow 2012 and 2013;
Albuquerque and Majid (arXiv:math/9802116, abstract checked here: octonions as
a twisting of the group algebra of Z_2^3, with higher 2^n-onion Cayley algebras
listed among examples; the journal reference is not given on the arXiv page and
was not confirmed). Shor-algorithm resource literature (Beauregard 2003,
Gidney and Ekera 2019, Gidney 2025) is not in the repository and is not cited
for any number in the survey.

## 8. Derivations and insights

### 8.1 The sign recursion in GF(2) form (the fold)

Notation: n index bits, p = (a, p'), q = (b, q') with top bits a, b; f_n(p,q)
= 1 iff sign(p,q) = -1; f_n^T(p,q) = f_n(q,p); z(q') = [q' = 0] = product of
(1 + q'_i).

Rust cases (`signs.rs:38-55`): (a,b)=(0,0): f_n(p',q'); (0,1): f_n(q',p');
(1,0): f_n(p',q') + [q' != 0]; (1,1): [q' = 0] + [q' != 0] f_n(q',p'), and
since f_n(0, p') = 0 this is [q'=0] + f_n(q',p'). Summing the four cases with
indicator weights over GF(2):

    f_{n+1} = (1+a)(1+b) f + (1+a) b f^T + a(1+b)(f + 1 + z) + a b (z + f^T)
            = (1+b) f + b f^T + a(1+b) + a z
            = f(sigma_b(p',q')) + a(1+b) + a z(q'),

where sigma_b swaps p' and q' when b = 1. Checked against the full table for
n = 1..10 (`fold.py`).

Meaning: "doubling" is a conditional swap of the two index registers, a
diagonal correction, and one multi-controlled phase testing q' = 0. The
q' = 0 test is the identity-element exception in CD conjugation
(`conj(e_0) = e_0`, `conj(e_k) = -e_k`), and it is one source of top-degree
monomials. The conditional swap's b(f + f^T) term is another: the cubic
monomials of f_3 are a q0 q1 from a z(q') and p1 q0 b and p0 q1 b from the swap.

### 8.2 Circuit consequence

Unrolling: phase circuit P_n(p,q) = [Z_a, CZ_{a,b}, C^{(n)}Z_{a, q' = 0}] ,
CSWAP_b(p' <-> q'), P_{n-1}(p',q'), CSWAP_b(p' <-> q'). All phase gates commute
with each other. Gate totals: n(n-1) controlled swaps (each level k contributes
2k), 3n - 2 multi-controlled-Z gates, widths 2, 1, 2, k for k up to n. The full
basis product is P_n followed by n CNOTs (p_i -> q_i). Simulated at gate
level on all 4^n inputs for n <= 6.

Resource examples: dim 32 (n=5): 20 controlled swaps, 13 phase gates; dim 256
(n=8): 56 and 22; dim 4096 (n=12): 132 and 34. A controlled swap is one Toffoli
plus two CNOTs; a width-w multi-controlled-Z is O(w) Toffolis with ancillas
(standard result, not computed here). Estimates of Toffoli totals are of order
10^2 at n = 12; they were not computed.

Contrast with the expanded polynomial: 261637 monomials at n = 12. The
monomial count is the wrong size measure for circuits.

Caveat: the circuit implements the basis product with the p register retained.
The algebra product of two superposed vectors contracts p away and is not
unitary (survey 9.1).

### 8.3 Monomial count (closed form), proof sketch

ANF of f_{n+1} from 8.1: the a-free part is f + b (f + f^T); the a-part is
a (1 + b + z) = a b + a * sum_{T != empty} q'_T (the constant monomial 'a'
cancels because z contains the constant 1). Therefore

    N(n+1) = N(n) + |M xor M^T| + 2^n,

with M the monomial set of f_n and M^T its image under p <-> q. Since
f(p,0) = f(0,q) = 0, M has no pure-p and no pure-q monomials, so the b*m terms
never collide with the a-part. |M xor M^T| = 2 N(n) - 2 |M and M^T|. The
swap-invariant monomials of f_n are exactly p_i q_i, i = 1..n (induction: the
n old ones persist; 'ab' is new and swap-invariant; a q'_T maps to b p_T, which
is not in M_{n+1}; verified numerically for n <= 9). Hence

    N(n+1) = 3 N(n) - 2n + 2^n,   N(1) = 1,   N(n) = (3^n + 1)/2 - 2^n + n.

Matches the computed counts 1, 3, 9, 29, 95, 307, 973, 3033, 9339, 28511,
86537 (n = 1..11). The exponent log2(3) = 1.585 appears at the representation
level: three of the four doubling quadrants contribute independent monomial
copies (f, b f, b f^T), the same count as a Karatsuba split but arising from the
sign function, not from the product.

Number of top-degree (n) monomials in f_n: 2^(n-1) - 1 (computed for
n = 3..11: 3, 7, 15, 31, 63, 127, 255, 511, 1023; not derived).

### 8.4 The cocycle defect equals the associator support

The associator of basis elements is
`(e_a e_b) e_c - e_a (e_b e_c) = (s(a,b) s(a^b,c) - s(b,c) s(a,b^c)) e_{a^b^c}`.
It is non-zero iff the 2-cocycle identity fails at (a,b,c). Counts of failing
ordered triples over [0, dim)^3: 168 (dim 8), 1848 (16), 15960 (32), 130200
(64). Cross-checks inside the repository: 168 = non-Fano ordered distinct
imaginary triples (`M3IsAssociator.v:127`); 1848 = 3375 - 1527
(`C1467_XORSignCocycle.v:126`). Consequence for the sister project: the
associator tensor needs no separate computation; it is the cocycle defect of the
sign table.

### 8.5 Left multiplication as translation times phase

`L_{e_p} = P_p D_p`; `P_p` permutes q -> p XOR q; `D_p = diag((-1)^{f_p(q)})`.
Boolean degree of f_p in the bits of q: 0 for p = 0, exactly n-1 for every other
p, for n = 3..11. Octonion rows (degree 2) are CZ/Z products (Clifford).
Sedenion rows (degree 3) contain CCZ-type monomials (not Clifford). For fixed p
the number of monomials averages 3.0, 7.8, 18.0, 39.4, 83.6, 173.9, 357.4,
728.6, 1477.3 (n = 3..11).

Contrast with Clifford algebras/Pauli strings: the sign is bilinear, degree 1
per row. The repository's C-1511 reports a bilinear sign matches `cd_sign` on 21
of 42 octonion products.

### 8.6 The generated group

Group G_n = <L_{e_p} (p in F_2^n), -1> in the signed permutation group of
2^n points. |G_n| = 4, 8, 128, 4096, 2^21, 2^38, 2^71, 2^136 for n = 1..8.
For n >= 3 the pattern is |G_n| = 2^(n + 2^(n-1)): a translation part of order
2^n (the XOR group) times a sign subgroup of order 2^(2^(n-1)) = 2^(dim/2).
Observed for n = 3..8; not proved. The group is a 2-group inside
F_2^n x| {+-1}^(2^n), so every element has 2-power order. A modular
multiplication permutation has order ord_N(a), generally not a power of 2.
Prediction for n = 9: 2^265 (not run; dim 512 is expected to take longer than
the 765 seconds the dim-256 run needed).

### 8.7 Walsh spectrum facts

For rows p >= 1, the largest |Walsh coefficient| divided by dim (correlation
with the best affine function): n=3: 0.5 for all rows; n=4: 0.75 for all rows;
for n >= 5 the rows split: the minimum tends to 0.5 (0.502 at n = 11), the
median is about 0.78, the maximum tends to 1 (0.998 at n = 11). So some rows
are almost Pauli-Z strings with sparse corrections, and the worst rows are
about half-correlated. Neither a flat (bent, 2^(-n/2)) nor a delta spectrum.
The XOR-convolution part of L_a (all signs +1) is exactly diagonalized by the
Walsh-Hadamard transform with eigenvalues WHT(a); the sign twist is what
Cariow's sparse term corrects.

### 8.8 Edge-count self-similarity

Largest cross-pair component at dim D: C(D/2 - 2, 2) - (D/4 - 1) edges. This
equals the basis-participation edge count (d^2 - 6d + 8)/2 of C958 at d = D/2
for D = 32, 64, 128, 256, 512 (84, 420, 1860, 7812, 32004). So the maximal
component at D has the combinatorics of the whole basis-participation graph at
D/2: a recursive-doubling signature, consistent with Theorem 11's sub-block
embedding.

### 8.9 Why Cariow stops at dim 16 and what it is

`Y = Bcheck X - 2 Bhat X`: Bcheck is block-symmetric Toeplitz over the F_2^4
group, diagonalized by the 16-point Walsh-Hadamard transform (four butterfly
stages `x -> (x_lo + x_hi, x_lo - x_hi)`); Bhat is a 106-term sparse correction
(`CARIOW2013_BHAT_TERMS`, `cariow_factorization.rs:55`). The schedule exploits a
dimension-specific sign pattern; the repository states no generic 3-for-4
rewrite exists because conjugation and non-commutativity block Karatsuba
(`fast_associator.rs:14-26`). On a quantum register the four classical stages
become one layer of four Hadamard gates.

### 8.10 Quality observations about the corpus

- The registry mirrors the proof set as 162 `kernel_checked` entries; none
  carry an "axiom-bearing" or "arithmetic only" flag.
- `C1468_SlotShiftEquivariance.v` header, theorem list, and two comments give
  three different accounts of what is preserved.
- The repository's own commit history shows a pattern of precision fixes
  (HEAD fe668020 clarifies the pathion convention; the stale `.vo` for the same
  file still carries the older axiom). Treat any census number as
  convention-dependent until its test and comment are read together.

### 8.11 Closed forms for the defect count and the zero-divisor edge total

Computed: the number v(N) of ordered triples (a,b,c) in [0,N)^3 with a failing
2-cocycle identity (equivalently, with non-zero basis associator) is 168, 1848,
15960, 130200, 1046808, 8385048, 67101720, 536856600, 4294938648 for N = 8..2048
(and 0 for N = 2, 4). All nine satisfy

    v(N) = N^3/2 - 14 N + 24,

equivalently g(N) = N^3/2 - v(N) satisfies g(2N) = 2 g(N) + 24 with g(8) = 88.
Not proved here.

At the basis level the associator coefficient is `sigma1 - sigma2` and the
antiassociator coefficient is `sigma1 + sigma2` for signs sigma1, sigma2
in {+1, -1}; so "antiassociator = 0" (Brown 1972, Theorem 7.15 condition iii,
formalized for one pair in `ZD_Criterion.v:375`) means "associator != 0". The
cross-pair zero products at dimension 2N therefore correspond to defect
triples at dimension N. Measured fact: the repository's cross-pair edge totals
at D = 16, 32, 64, 128, 256 (84, 924, 7980, 65100, 523404; tests at
`boxkites/tests.rs:673-860`, CSV through 128) equal v(D/2)/2 exactly, giving

    E(D) = D^3/32 - 7 D/2 + 12.

The identity is checked at five dimensions, not proved; the factor 2 between
ordered defect triples and edges is not derived here. The
dim-256 total 523404 is asserted in the repository only by an `#[ignore]`d
test; the identity reproduces it without running that test.

Extrapolations (conditional on the identity continuing to hold): E(512) =
4192524, E(1024) = 33550860, E(2048) = 268428300, E(4096) = 2147469324.
Consistency checks against the repository's 512 and 1024 text: 255 components
x 254 nodes at 512 give a mean of 16441 edges per component, between
e_min = 756 and e_max = 32004; the mean runs at about e_max/2 (4121 against
7812 at 256, measured; 16441 against 32004 at 512, predicted). The comment at
`tests.rs:6129` reads "511 components x 510 nodes x ~129K edges each"; 129540 is
e_max(1024), and read literally the comment would give about 66 million edges,
twice E(1024) = 33550860. The comment is loose and is not an assertion, so it
does not support the prediction.

Dimension relation: the sedenion cross-pair graph (D = 16, 84 edges) has half as
many edges as the octonions have non-Fano ordered triples (168); the pathion
graph (D = 32, 924 edges) has half as many edges as the sedenions have
non-associative ordered triples (1848).

## 9. Replayable scripts

Place the five files in one directory and run with an interpreter that puts the
script directory on its path (for example `$PYTHON checks.py`; the isolated
mode `-I` removes the script directory and breaks the local import). Timings:
checks 1 minute, fold under 1 minute, group to n = 6 about 1 second, n = 8 about
13 minutes.

### 9.1 cdlib.py

```python
"""Cayley-Dickson sign function and Boolean-function helpers (stand-alone)."""
import numpy as np
from math import log2


def sign(dim, p, q):
    """Direct transliteration of cd_basis_mul_sign (crates/cd_kernel/src/cayley_dickson/signs.rs)."""
    if dim == 1:
        return 1
    half = dim // 2
    if p < half and q < half:
        return sign(half, p, q)
    if p < half and q >= half:
        return sign(half, q - half, p)
    if p >= half and q < half:
        s = sign(half, p - half, q)
        return s if q == 0 else -s
    qh, ph = q - half, p - half
    if qh == 0:
        return -1
    return sign(half, qh, ph)


def signtab(n):
    """Sign table for dim = 2**n by block doubling (same four cases, vectorized)."""
    T = np.ones((1, 1), dtype=np.int8)
    for k in range(n):
        h = 1 << k
        N = np.zeros((2 * h, 2 * h), dtype=np.int8)
        N[:h, :h] = T                      # lo-lo
        N[:h, h:] = T.T                    # lo-hi : sign_h(q-h, p)
        blk = T.copy()
        blk[:, 1:] = -blk[:, 1:]
        N[h:, :h] = blk                    # hi-lo : negate unless q == 0
        blk2 = T.T.copy()
        blk2[:, 0] = -1
        N[h:, h:] = blk2                   # hi-hi : -1 if q-h == 0 else sign_h(q-h, p-h)
        T = N
    return T


def anf(tt):
    """Moebius transform: truth table (length 2**m) -> ANF coefficient vector."""
    a = np.asarray(tt, dtype=np.uint8).copy()
    m = int(round(log2(len(a))))
    for i in range(m):
        s = 1 << i
        a = a.reshape(-1, 2 * s)
        a[:, s:] ^= a[:, :s]
        a = a.reshape(-1)
    return a


def anf_rows(F):
    A = np.asarray(F, dtype=np.uint8).copy()
    d = A.shape[1]
    for i in range(int(round(log2(d)))):
        s = 1 << i
        A = A.reshape(A.shape[0], -1, 2 * s)
        A[:, :, s:] ^= A[:, :, :s]
        A = A.reshape(A.shape[0], d)
    return A


def popcount_table(m):
    return np.array([bin(i).count("1") for i in range(1 << m)], dtype=np.int8)


def wht_rows(M):
    M = np.asarray(M, dtype=np.int64).copy()
    d = M.shape[1]
    h = 1
    while h < d:
        M = M.reshape(M.shape[0], -1, 2, h)
        a = M[:, :, 0, :].copy()
        b = M[:, :, 1, :].copy()
        M[:, :, 0, :] = a + b
        M[:, :, 1, :] = a - b
        M = M.reshape(M.shape[0], d)
        h *= 2
    return M
```

### 9.2 checks.py

```python
"""Independent checks on the CD sign function. Run from the directory holding cdlib.py: PYTHON=${PYTHON:-python3}; $PYTHON checks.py"""
import numpy as np
from cdlib import sign, signtab, anf, anf_rows, popcount_table, wht_rows


def conj(x):
    y = -x.copy()
    y[0] = x[0]
    return y


def mul(x, y):  # doubling formula (a,b)(c,d) = (ac - conj(d) b, d a + b conj(c))
    n = len(x)
    if n == 1:
        return x * y
    h = n // 2
    a, b, c, d = x[:h], x[h:], y[:h], y[h:]
    return np.concatenate([mul(a, c) - mul(conj(d), b), mul(d, a) + mul(b, conj(c))])


def check_doubling_and_orthogonality():
    for n in (1, 2, 3, 4, 5):
        dim = 1 << n
        T = signtab(n)
        assert all(T[p, q] == sign(dim, p, q) for p in range(dim) for q in range(dim))
        for p in range(dim):
            L = np.zeros((dim, dim))
            for q in range(dim):
                x = np.zeros(dim); x[p] = 1
                y = np.zeros(dim); y[q] = 1
                z = mul(x, y)
                e = np.zeros(dim); e[p ^ q] = T[p, q]
                assert np.array_equal(z, e)
                L[p ^ q, q] = T[p, q]
            assert np.array_equal(L @ L.T, np.eye(dim))
    print("doubling formula == sign recursion; every L_(e_p) orthogonal (dims 2..32)")


def check_basic_properties(nmax=11):
    for n in range(2, nmax + 1):
        d = 1 << n
        T = signtab(n).astype(int)
        assert (T[0] == 1).all() and (T[:, 0] == 1).all()
        assert all(T[p, p] == -1 for p in range(1, d))
        A = T[1:, 1:]
        off = ~np.eye(d - 1, dtype=bool)
        assert (A[off] == -A.T[off]).all()
        assert int((A > 0).sum()) == (d - 1) * (d - 2) // 2
    print(f"identity, squares, antisymmetry, positive count (d-1)(d-2)/2 hold for dims 4..{1 << nmax}")


def check_cocycle(nmax=6):
    print("2-cocycle violations of s(a,b)s(a^b,c) == s(b,c)s(a,b^c):")
    for n in range(1, nmax + 1):
        d = 1 << n
        T = signtab(n).astype(int)
        a, b, c = np.meshgrid(range(d), range(d), range(d), indexing="ij")
        bad = int((T[a, b] * T[a ^ b, c] != T[b, c] * T[a, b ^ c]).sum())
        print(f"  dim={d}: {bad} of {d ** 3}")


def check_anf(nmax=11):
    pc = popcount_table(2 * nmax)
    print("n dim | row degrees {deg: rows} | mean/max row monomials | joint degree | joint monomials | closed form")
    for n in range(1, nmax + 1):
        d = 1 << n
        F = (signtab(n) == -1).astype(np.uint8)
        A = anf_rows(F)
        deg = np.array([pc[np.nonzero(A[p])[0]].max() if A[p].any() else 0 for p in range(d)])
        vals, cnts = np.unique(deg, return_counts=True)
        mono = A.sum(axis=1)
        J = anf(F.reshape(-1))
        nz = np.nonzero(J)[0]
        closed = (3 ** n + 1) // 2 - 2 ** n + n
        assert len(nz) == closed
        print(n, d, dict(zip(vals.tolist(), cnts.tolist())), f"{mono.mean():.1f}/{mono.max()}", int(pc[nz].max()), len(nz), closed)


def check_walsh(nmax=11):
    print("n dim | min, median, max over rows p>=1 of max_k |W_p(k)| / dim")
    for n in range(3, nmax + 1):
        d = 1 << n
        W = wht_rows(signtab(n)[1:])
        c = np.abs(W).max(axis=1) / d
        print(n, d, round(float(c.min()), 4), round(float(np.median(c)), 4), round(float(c.max()), 4))


if __name__ == "__main__":
    check_doubling_and_orthogonality()
    check_basic_properties()
    check_cocycle()
    check_anf()
    check_walsh()
```

### 9.3 fold.py

```python
"""Fold recursion f_{n+1}(a,b,p',q') = f_n(sigma_b(p',q')) + a(1+b) + a*[q'==0] and its gate-level circuit."""
import numpy as np
from cdlib import signtab, anf


def F(n):
    return (signtab(n) == -1).astype(np.int8)


def check_recursion(nmax=10):
    for n in range(1, nmax + 1):
        f, g, N = F(n), F(n + 1), 1 << n
        z = np.zeros(N, dtype=np.int8)
        z[0] = 1
        for a in (0, 1):
            for b in (0, 1):
                base = f.T if b else f
                val = base ^ (a * (1 - b)) ^ (a * z[None, :])
                assert np.array_equal(val, g[a * N:(a + 1) * N, b * N:(b + 1) * N]), (n, a, b)
    print(f"fold recursion reproduces the sign table for n = 1..{nmax} -> {nmax + 1}")


def build(n):
    """Gate list on wires p_0..p_{n-1} (0..n-1) and q_0..q_{n-1} (n..2n-1)."""
    gates = []

    def rec(k, P, Q):
        if k == 1:
            gates.append(("MCZ", [P[0], Q[0]], []))
            return
        a, b, Pl, Ql = P[k - 1], Q[k - 1], P[:k - 1], Q[:k - 1]
        gates.append(("MCZ", [a], []))                 # Z on a
        gates.append(("MCZ", [a, b], []))              # CZ on a,b   (a + ab = a(1+b))
        gates.append(("MCZ", [a] + Ql, Ql))            # a * [q' == 0], negative controls on q'
        gates.append(("CSWAP", b, list(zip(Pl, Ql))))
        rec(k - 1, Pl, Ql)
        gates.append(("CSWAP", b, list(zip(Pl, Ql))))

    rec(n, list(range(n)), list(range(n, 2 * n)))
    return gates


def simulate(n, gates):
    T = F(n)
    for p in range(1 << n):
        for q in range(1 << n):
            bits = [(p >> i) & 1 for i in range(n)] + [(q >> i) & 1 for i in range(n)]
            par = 0
            for g in gates:
                if g[0] == "MCZ":
                    par ^= int(all((bits[w] ^ (w in g[2])) == 1 for w in g[1]))
                elif bits[g[1]]:
                    for x, y in g[2]:
                        bits[x], bits[y] = bits[y], bits[x]
            if par != T[p, q]:
                return False
    return True


def counts(gates):
    fred = sum(len(g[2]) for g in gates if g[0] == "CSWAP")
    widths = [len(g[1]) for g in gates if g[0] == "MCZ"]
    return fred, len(widths), max(widths)


if __name__ == "__main__":
    check_recursion()
    for n in range(1, 7):
        gs = build(n)
        assert simulate(n, gs)
    print("gate-level circuit matches the sign table on all 4^n inputs for n = 1..6")
    print("n dim Fredkin MCZ max_width | ANF monomials")
    for n in (4, 5, 6, 8, 10, 11, 12):
        fr, m, w = counts(build(n))
        assert fr == n * (n - 1) and m == 3 * n - 2 and w == n
        print(n, 1 << n, fr, m, w, "|", (3 ** n + 1) // 2 - 2 ** n + n)
    # swap-invariant monomials of f_n are exactly p_i q_i (drives N(n+1) = 3N(n) - 2n + 2^n)
    for n in range(1, 10):
        d = 1 << n
        nz = [int(m) for m in np.nonzero(anf(F(n).reshape(-1).astype(np.uint8)))[0]]
        S = set(nz)
        tr = lambda m: ((m & (d - 1)) << n) | (m >> n)
        inter = [m for m in nz if tr(m) in S]
        assert len(inter) == n and all(bin(m).count("1") == 2 and (m >> n) & m & (d - 1) for m in inter)
    print("M intersect M^T = {p_i q_i} (n monomials) for n = 1..9")
```

### 9.4 group.py

```python
"""Order of the group generated by the signed permutations L_(e_p) and -1 (sympy Schreier-Sims)."""
import math, sys, time
from sympy.combinatorics import Permutation, PermutationGroup
from cdlib import sign


def gens(dim):
    out = []
    for p in range(dim):
        img = [0] * (2 * dim)
        for q in range(dim):
            s = sign(dim, p, q)
            for t in (0, 1):                      # point 2q+t is (+e_q) for t=0, (-e_q) for t=1
                img[2 * q + t] = 2 * (p ^ q) + (t if s == 1 else 1 - t)
        out.append(Permutation(img))
    out.append(Permutation([x ^ 1 for x in range(2 * dim)]))   # -1
    return out


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    for n in range(1, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 6):
        dim = 1 << n
        t = time.time()
        o = PermutationGroup(gens(dim)).order()
        print(f"dim={dim}: log2|G| = {math.log2(o):.0f}; predicted n + 2^(n-1) = {n + 2 ** (n - 1)} (n >= 3); {time.time() - t:.1f}s")
```

### 9.5 defect.py

```python
"""Count ordered triples (a,b,c) in [0,2^n)^3 where the sign 2-cocycle identity fails
(= basis triples with non-zero associator), and compare with the cross-pair ZD edge counts."""
import sys, time
import numpy as np
from cdlib import signtab


def violations(n):
    d = 1 << n
    T = signtab(n)
    idx = np.arange(d)
    X = idx[:, None] ^ idx[None, :]
    total = 0
    for a in range(1, d):
        s1 = T[a][:, None] * T[a ^ idx, :]          # s(a,b) s(a^b,c)
        s2 = T * T[a][X]                            # s(b,c) s(a,b^c)
        total += int((s1 != s2).sum())
    return total


if __name__ == "__main__":
    edges = {16: 84, 32: 924, 64: 7980, 128: 65100, 256: 523404}   # cross-pair edges: tests.rs + data/csv/cd_motif_edges_*
    for n in range(3, int(sys.argv[1]) + 1):
        t = time.time()
        v = violations(n)
        D = 1 << (n + 1)
        known = edges.get(D)
        note = "" if known is None else f"  repo edges({D}) = {known}; 2*edges = {2 * known}; match: {v == 2 * known}"
        print(f"N={1 << n}: non-associative ordered triples = {v}; v/2 = {v // 2} = predicted cross-pair edges({D}){note}  [{time.time() - t:.0f}s]", flush=True)
```

Usage: `$PYTHON defect.py 9` prints v(N) for N = 8..512 and compares with the
repository's cross-pair edge totals; `defect_big.py` (loop over n = 10, 11
calling `violations`) took 1 and 10 seconds.

### 9.6 Comment- and string-aware Rocq scan

```python
"""Comment- and string-aware scan of Rocq sources for admissions, axioms, parameters.
Usage (from the repository root): $PYTHON scan_v.py proofs curated data"""
import os, re, sys


def strip(src):
    res, i, depth, n = [], 0, 0, len(src)
    while i < n:
        c = src[i]
        nx = src[i + 1] if i + 1 < n else ""
        if depth == 0 and c == '"':
            res.append(" ")
            i += 1
            while i < n:
                if src[i] == '"':
                    if i + 1 < n and src[i + 1] == '"':
                        i += 2
                        continue
                    i += 1
                    break
                if src[i] == "\n":
                    res.append("\n")
                i += 1
            continue
        if c == "(" and nx == "*":
            depth += 1
            i += 2
            continue
        if c == "*" and nx == ")" and depth > 0:
            depth -= 1
            i += 2
            continue
        if depth > 0:
            if c == "\n":
                res.append("\n")
            i += 1
            continue
        res.append(c)
        i += 1
    return "".join(res)


PAT = {
    "Admitted": re.compile(r"\bAdmitted\s*\."),
    "admit": re.compile(r"\badmit\b"),
    "Axiom": re.compile(r"^\s*(Axiom|Axioms)\b", re.M),
    "Parameter": re.compile(r"^\s*(Parameter|Parameters)\b", re.M),
    "Conjecture": re.compile(r"^\s*Conjecture\b", re.M),
    "Abort": re.compile(r"\bAbort\s*\."),
}

rows = []
for root in sys.argv[1:]:
    for dp, _, fns in os.walk(root):
        for f in fns:
            if f.endswith(".v"):
                path = os.path.join(dp, f)
                s = strip(open(path, encoding="utf-8", errors="replace").read())
                rows.append((path, {k: len(v.findall(s)) for k, v in PAT.items()}))
rows.sort()
print(len(rows), "files;", {k: sum(r[1][k] for r in rows) for k in PAT})
for path, c in rows:
    if any(c.values()):
        print(path, c)
```

Usage: `$PYTHON scan_v.py proofs curated data` run from the repository root
prints totals and the files with admissions, axioms, parameters, or conjectures.

## 10. Falsifiers and open items

| Claim | What would falsify it | Status |
| --- | --- | --- |
| Row degree is n-1 for every non-identity p, all n | one row of lower degree at some n | verified n = 3..11; unproved |
| |G_n| = 2^(n + 2^(n-1)) | order different at n = 9 | verified n = 3..8; unproved |
| N(n) closed form | none expected: proof sketch in 8.3 | proof sketch plus n = 1..11 |
| v(N) = N^3/2 - 14N + 24 and E(D) = v(D/2)/2 | a computed v(N) off the formula, or a measured edge total off E(D) | v: N = 4..2048; E: D = 16..256; extrapolation to D = 4096 unmeasured |
| Fold recursion | none expected: algebraic identity | verified n <= 10, circuit n <= 6 |
| Heavy-lane census numbers | rerun disagreement | not rerun (no `cargo` in the read-only tree); CSV row counts agree for edges through 128 |
| Cocycle defect equals associator support | an associator zero where the defect is non-zero | identity of definitions; counts cross-checked against two Rocq theorems |
| 15960 coincidence (8.4) | independent derivation showing the two quantities are unrelated | open |

Next experiments with value for the sister project: (a) compile the fold
circuit to a Clifford+T gate set and record T counts per dimension; (b) check the
circuit against `L_{e_p}` from `get_sedenion_matrices()` for n = 4; (c) test the
block-encoding normalization `sum |a_p|` for chosen elements; (d) rerun the
cross-pair census at 512 and 1024 and compare with the test predictions;
(e) derive the associator tensor from the fold recursion to avoid the O(dim^3)
enumeration; (f) prove v(N) = N^3/2 - 14N + 24 from the fold recursion and
check E(512) = 4192524 against the ignored census when a heavy lane is
available.
