# A_5 kernel bundles: critical review of the evidence record

Target: `docs/evidence/a5-kernel-bundles/README.md` and `ledger.md` on branch `geometry/a5-kernel-bundles` at
`a4f9127`, read against the eleven producer scripts in the same directory, their tests and retained results, and
`docs/design/a5-kernel-bundles-program.md`.

## Phase 0: artifact, field and visibility

The artifact is a mathematics record. It holds written proofs in algebraic topology and representation theory: the
K-theory of homogeneous spaces, stable-range cancellation for complex vector bundles, and compact-orbit moduli of
`G_2 x U(1)`. Each proof is backed by an exact-arithmetic Python certificate with mutation controls. The record
claims four results:

- the constant symmetry algebra is `g_2` plus four central directions, with no boost lift;
- orbit moduli and stabilizer representations on every piece of nullity at least 12;
- an exact Pfaffian transition cocycle with structure groups `U(6)`, `U(8)` and diagonal `SU(2)`;
- the equivalence classes: five trivial complex bundles of nullity twelve, the nullity-sixteen bundle
  `C^2+3 xi` with the nonzero class `x` in reduced `K^0(V_2(R^7))=Z/2`, every real bundle trivial, and every
  characteristic class zero.

The review covers the whole README, the whole ledger, the whole of `bundle_invariants.py`, and the topology,
representation-ring and pass-flag sections of the other ten producers. It covers their pooling calls and the tests of
the final certificate. The record's Lie solve, Pfaffian frames and stabilizer linear algebra were replayed, not
re-derived.

Deterministic layer:
- pinned Ruff check and format: clean;
- pinned mypy over the 22 files: clean;
- `git diff --check`: clean.

Replay: every producer's `--out` run reproduced its retained result byte for byte. Every `--self-test` passed in
normal and `-O` Python, and every `test_*.py` passed, in 508 s in total; `kernel_symmetry.py` took 92 s and
`aligned_orbit_moduli.py` 119 s for the self-test pair and tests. Wall times on the shared host with
`GOROROBA_WORKERS=4`:

| Producer | Seconds |
| --- | ---: |
| `kernel_symmetry.py` | 9 |
| `kernel_frames.py` | 3 |
| `stabilizer_representation.py` | 3 |
| `nullity_sixteen_bundle.py` | 0 |
| `aligned_orbit_moduli.py` | 3 |
| `aligned_stabilizer_representation.py` | 7 |
| `v_orbit_moduli.py` | 5 |
| `v_topology_representation.py` | 13 |
| `isotropic_orbit_data.py` | 3 |
| `transition_atlas.py` | 2 |
| `bundle_invariants.py` | 0 |

No producer invokes Singular; the computer algebra is sympy, `DomainMatrix` and `Fraction`.

## Independent checks run for this review

- **Branching probe.** The probe restricted the three derived `su(2)` stabilizer generators at both nullity-sixteen
  representatives to the imaginary octonions and to the adjoint action on the fourteen derivations. It computed both
  Casimirs exactly under the common adjoint trace form.
  - On the 7, the spectrum is `{0 (x3), 3/16 (x4)}`.
  - On the 14, the spectrum is `{0 (x3), 3/16 (x8), 1/2 (x3)}`.
  - The ratio `(1/2)/(3/16)=8/3` is the `V_2 : V_1` Casimir ratio, and the matching `3/16` on the 7 excludes `V_3`.
  - Thus `7 -> 3 V_0 + 2 V_1` and `14 -> 3 V_0 + 4 V_1 + V_2` hold on the actual stabilizer.
- **Phase-period probe.** The probe applied `J = L_(e_16)` to the open `V` representative. It multiplies every nonzero
  coordinate of `z` by `-i`, including the middle coordinate `mu = 4i`. The base phase therefore rotates the `mu/abs(mu)`
  circle freely with winding number `-1` and period `2 pi`. That is the hypothesis the pullback lemma needs.
- **Hand derivations.**
  - The cancellation form is the following: the fibration `U(k+1)/U(k) = S^(2k+1)` makes
    `Vect^C_k(X) -> Vect^C_(k+1)(X)` bijective when `dim X <= 2k`. A stably trivial complex rank-`k` bundle on a CW
    complex of dimension `d <= 2k` is therefore trivial.
  - The mapping-torus groups are `K^0(M_-)=Z` and `K^1(M_-)=Z+Z/2`, from `1-f^* = diag(0,2)` on `K^0(S^6)` with
    `K^1(S^6)=0`.
  - The Koszul complex over `Z[x]` is `Tor_0 = Z[x]/(2x,x^2)`, `Tor_1 = Z` and `Tor_2 = 0`. The last holds because
    `gcd(2, x+8) = 1` in `Z[x]`.
  - The completeness arguments for `rho`, `(lambda, rho)` and the Gram ball were rederived.

## Findings, worst first

### SERIOUS 1: the classification certificate certifies its own constants

**Barb.** `bundle_invariants.py` is a typed transcript of the README proof. Its three mutations edit the transcript,
so none of them can detect a wrong input.

**Grounding.** The pass flag depends on literals:
- `graph_circle_section = True` in `_b9_classification`;
- `stable_trivial = True` in `_aligned_classification`;
- `reduced_class = (0, 0)` in `_open_v_classification`;
- `standard_doublets = 2` in `_vb_classification`;
- `nullity_sixteen_doublets = 3` and `aligned_doublets = 2` in `_adjacency_certificate`;
- `_trivial_characteristics`, which returns the strings `"1"` and `"zero"`;
- `denominator_exact`, which compares a hand-written list of seven calls with the hand-written `PIECES`.

Each mutation flips the literal it is named after:
- `drop_vb_standard_doublet` sets `standard_doublets = 1`;
- `inject_v_torsion` sets `reduced_class = (0, 1)`;
- `odd_rank_antipodal_clutching` sets `rank = 5`.

The pass flag then fails because it compares the same literal. The bound-result validations compare upstream prose
fields by string equality, for example `"trivial rank 16 by stable-range cancellation"` and `"3x=x != 0"`. That
proves only that the upstream file contains the sentence.

The genuine computations in this certificate are few:
- `R_(e_16)` is skew, and `R^2 = -I_32`;
- the committed `base_phase_lift` triple flag;
- the `(1,2,1)` multiplicities and commutant dimension 6, read from a bound `VB` row;
- the digest, schema and pass bindings.

The program file, section 5, requires "`--self-test` mutation controls that must fail when the property is removed".
These remove a constant instead.

The README sentences this concerns:
- "The finite classification then proves that all five nullity-twelve complex bundles are trivial ..." (Scope);
- "Its class in the displayed free and order-two summands is `(0,0)`" (open `V` paragraph);
- "All seven total Chern classes equal one. All Stiefel-Whitney and Pontryagin classes of the underlying real bundles
  vanish.";
- "The mutations delete one `VB` doublet, inject the order-two class into `V`, or replace the even-rank antipodal
  clutching by odd rank; all three fail in normal and optimized Python. The finite denominator, input digests, exact
  right-phase matrix calculation, K-classes, cancellations, clutching weights, adjacency rows, and mutations are in
  `bundle-invariants-result.json`."

The ledger's item-4 row correctly labels the mathematics **Inferred**. The README nonetheless presents the JSON as
carrying "K-classes" and "cancellations" that no code computes.

The written mathematics is correct. Every step checked out by hand (see SOUND below), so this finding concerns what
the certificate demonstrates, not whether the classification is true.

**Remedy.**
- Derive every input the certificate uses from the bound rows. Count `V_1` multiplicities from each bound
  `irreducible_decomposition`, and reduce them mod `generator_order` from the nullity-sixteen result. Read the CW
  dimensions from the bound topology.
- Move mutations to the inputs: feed a fabricated `VB` row with three doublets, or a mapping-torus `K^0` of `Z^2`.
- Otherwise, relabel the JSON as a structured restatement of the written proof and say so in the README sentence that
  lists its contents.

### SERIOUS 2: hand-typed inputs carry the Observed label

**Barb.** The nullity-sixteen K-theory and both mapping-torus topologies start from constants typed into the scripts.
The ledger files the conclusions downstream of those constants as observations.

**Grounding.** In `nullity_sixteen_bundle.py`, `_representation_ring_checks` hard-codes:
- `fundamental_restriction = (3, 2)`;
- `adjoint_restriction = (2, 4, 1)`.

`_base_topology_checks` hard-codes `euler_boundary = 2`. The AHSS statement is a string. The Koszul syzygy arithmetic
downstream is genuinely computed.

In `v_topology_representation.py`, `_topology_certificate` hard-codes `square_root_winding = 1`. The unit-section
cohomology is a literal dictionary chosen by the sign of that constant. Only the mapping-torus K-groups follow
arithmetically from the Wang entry. In `aligned_orbit_moduli.py`, `_topology_checks` returns a literal cohomology dictionary, and its
`trivialize_monodromy` mutation swaps in a second literal dictionary.

The ledger's nullity-sixteen row states: "**Observed:** ... The restrictions `7 -> 3V_0+2V_1` and
`14 -> 3V_0+4V_1+V_2` give Koszul relations `2x` and `x^2+8x`, so `reduced K^0(V_2(R^7))=(Z/2){x}`". The open-`V`
topology row lists the "Wang-map" checks among its observations. The program file, section 5, requires the record to
"Separate observed from inferred".

The README presents mutations of these constants as rejections by the replay: "Three mutations remove one doublet,
replace the Euler boundary by one, or replace `3+2t` by the rank-preserving false branching `5+t`; the replay rejects
all three." It also says "The exact rows, Wang maps, input digests, and mutation controls are in
`v-topology-representation-result.json`."

The aligned topology row is labeled **Inferred** in the ledger, so the aligned dictionary is not mislabeled. Its
`trivialize_monodromy` mutation still follows the self-referential pattern of SERIOUS 1.

The branching probe above shows that both restrictions hold on the actual stabilizer generators. The values are
right; the label is wrong.

**Remedy.**
- Compute the 7 and 14 restrictions from the exact stabilizer generators. Use the Casimir spectra under the adjoint
  trace form; the probe takes about twenty lines and seconds of runtime.
- Feed the computed polynomials into the Koszul step.
- Relabel the cellular boundary, the square-root winding and the topology dictionaries as **Inferred** with their
  written arguments, or compute the winding from `alpha^2+beta^2` along an explicit loop.

### SERIOUS 3: a serial loop over independent items holds most of the symmetry replay

**Barb.** The slowest serial computation in the record runs outside the pool the repository mandates.

**Grounding.** `_center_dimension` in `kernel_symmetry.py` loops serially over the 18 basis triples. Each iteration
forms 18 commutators of `32 x 32` rational matrices, independently of the others. Measured alone with
`GOROROBA_WORKERS=4`, it takes 5.5 s of the producer's 9 s wall time. `_orbit_dimensions` in the same file loops
serially over the seven independent orbit rank computations, in 0.87 s.

AGENTS.md says that every CPU-bound loop over independent items runs through `parallel.py`, and that "a serial loop
over such items is a defect review rejects". The program file repeats the rule, "script builders included".

Every `self_test` in the directory also runs its mutation builds one after another, and each build is independent.
Their cost was not measured; this is a lower-priority instance of the same rule.

The record has no other qualifying serial loop:
- `_find_three_pivots` in `transition_atlas.py` is an early-exit search;
- the inner loops of the per-fixture tasks run inside pooled workers;
- `nullity_sixteen_bundle.py` and `bundle_invariants.py` contain no CPU-bound independent loop.

**Remedy.** Map the per-`fixed` commutator rows and the per-orbit rank computations through
`parallel.ordered_map`, and assemble the sparse matrix in input order.

### SLOPPY 4: the clutching table carries no information

**Barb.** "`-I_6`, joined to `I_6` in `SU(6)`" answers a question that complex bundles never ask.

**Grounding.** `GL(k,C)` is connected for every `k`. A constant clutching matrix of any rank and any determinant is
therefore null-homotopic, `-I_5` included: the path `exp(i t) I_5` for `0 <= t <= pi` stays in `U(5)`.
`_antipodal_clutching_certificate` declares the rank-five clutching not null-homotopic because its determinant is
`-1`. That test is false for complex bundles, so the odd-rank mutation refutes a criterion that does not hold.

The actual clutching of a bundle over the mapping torus `M_-` is a map `S^6 -> U(6)` after trivializing the bundle
over `S^6`. Its class lies in `pi_6(U(6)) = pi_6(U) = 0` by Bott periodicity. The README never mentions this group.

The phrase "natural geometric clutching `-I_6`" is undefined until a trivialization of `T S^6 tensor C` is fixed,
and the README fixes none.

The README sentence "The path `diag(exp(i t),...,exp(-5 i t))` lies in `SU(6)` and joins `I_6` to `-I_6`. Thus both
aligned complex bundles are actually trivial." is a non sequitur. The triviality already follows from reduced
`K^0(M_-)=0` and cancellation, which the preceding sentences state.

**Remedy.** Delete the `SU(6)` path, its mutation and the "Thus" sentence. Either drop the clutching table or label it
as heuristic and add `pi_6(U(6))=0`.

### SLOPPY 5: the `B9` homotopy model rests on an unsourced transitivity claim and a literal `True`

**Barb.** The `B9` product `G_2 x open(B^3)` rests on "`G_2` acts simply transitively on oriented coassociative
frames". The repository grounds that statement nowhere, and the certificate records it as
`graph_circle_section = True`.

**Grounding.** `docs/SOURCES.json` and `docs/notes/papers/` contain no source for the statement. The nearest source,
`docs/notes/papers/2411.18881.md`, concerns `G_2` acting simply transitively on the sedenion zero-divisor set `Z(S)`.
That is a different object unless the record maps one onto the other.

The exact computation establishes only that the `G_2` stabilizer is zero-dimensional. Suppose it were a nontrivial
finite group `Gamma`. The full stabilizer would then be `graph(rho) Gamma` and each orbit `G_2/Gamma`. The section
`g -> (g,1)` would not descend to that quotient, and associated bundles could be nontrivial flat bundles. Only the
prose argument excludes that case, so the `B9` triviality claim rests on it too.

The argument is correct and can be closed:
- the first three vectors of an orthonormal frame in a coassociative plane form a special triple, because the
  plane's normal contains the first two vectors' cross product;
- `G_2` acts simply transitively on special triples, and orientation fixes the fourth vector;
- the unit section of the connected cone `B9` is connected, so exactly one orientation occurs.

The README does not state the connectedness step, and AGENTS.md's grounding rule requires a registered source for
"mathematical invariants".

The gap therefore reaches the README sentence "Every bundle associated to the graph circle is therefore trivial",
as well as the `pi_1 = 0` entry and the completeness of the Gram invariant. The special-triple argument closes it.
The severity stays SLOPPY because the conclusion is true; the record states it without earning it.

**Remedy.**
- Register a source for the transitivity of `G_2` on special triples and coassociative frames, or map the normalized
  `B9` frames onto `Z(S)` and cite 2411.18881.
- Add the connectedness sentence.
- Check at one fixture that the four real columns span a coassociative plane, either by vanishing of the associative
  3-form on the plane or by `u x w = 0` together with the 4-form calibration.

### SLOPPY 6: the standard theorems are stated without their exact form or a source

**Barb.** Hodgkin's spectral sequence, the cancellation range and Bott periodicity are each used as "applies" with no
citation. The cancellation inequality appears in two forms.

**Grounding.** The README writes "`2*6>11`" and "lies in the cancellation range". The code tests `2k > d`, which is
strictly stronger than the sufficient condition `d <= 2k` and therefore conservative. The README never states the
theorem it invokes.

The Hodgkin hypotheses are correct: `pi_1(G_2) = 0` is torsion-free, `SU(2)` is connected, and `R(G_2)` is polynomial
on the two fundamental representations. The collapse argument is also correct, since `Tor` has only columns 0 and 1.
Neither is sourced. AGENTS.md grounds algebraic invariants in registered sources, and the record already has a
literature route through `docs/SOURCES.json`.

**Remedy.**
- State the cancellation lemma once in the form "stably trivial, complex rank `k`, CW dimension `d <= 2k` implies
  trivial".
- Register the source for it (Husemoller's *Fibre Bundles*, the stable-range chapter) and the source for Hodgkin
  (Hodgkin 1975, *The equivariant Kunneth theorem in K-theory*). Verify the chapter numbers before citing them.

### COSMETIC 7

The VB row of the ledger and the README's VB paragraph speak of a "moduli clutching". The tautological line is
trivial over the punctured sphere, so `VB_unit = V_2(R^7) x B` globally, with a constant base-point stabilizer.
`E` is then `G_2 x_(SU(2)) W` for an `SU(2)`-equivariant bundle `W` over `B`. Its isotypic multiplicity bundles are
line and plane bundles over a space of the homotopy type of a circle, so they are trivial. Read that way, the
connectedness of `GL(1) x GL(2) x GL(1)` is exactly the right fact. The word "clutching" is unnecessary.

## SOUND

- **`B9` triviality** rests on the explicit section `g -> (g,1)` of `G_2 x U(1) -> (G_2 x U(1))/graph(rho)`. It never
  uses cancellation, which would fail there because `dim G_2 = 14 > 12 = 2k`.
- **`VB`** uses cancellation only on the 11-dimensional Stiefel factor: `C^2 + 2 xi` has class `2x = 0`, and
  `11 <= 12`. The borderline 12-dimensional `V_2(R^7) x S^1` is never fed to the inequality. The circle direction is
  handled by the equivariant reduction above, whose constant `SU(2)` stabilizer along the global section was checked
  by hand.
- **The aligned pieces** have homotopy model `M_-` of dimension 7, `K~^0(M_-) = 0` and `7 <= 12`. The model `M_-`,
  the Alexander-duality cross-check (`H_11(V_2) = Z`, `H_5(V_2) = Z/2`) and the monodromy `u -> -u` are correct.
- **Open `V`.** `V_unit` is `S^1 x (fibration over B with fiber T S^6 and antipodal monodromy)`, homotopy equivalent
  to `S^1 x M_-`. The phase probe confirms a free `S^1` action of winding number one on the `mu` circle with domain
  period `2 pi`. The bundle is therefore `pr^*(E|_(M_-))` and trivial. Reduced `K^0(V_unit) = K^1(M_-) = Z + Z/2` is
  correct, and both coordinates vanish by the pullback.
- **`N_+-`.**
  - The Hodgkin hypotheses, the collapse and the edge map `x -> [xi]-2` are correct, and the restrictions are now
    exactly verified.
  - `Tor_0 = Z + (Z/2)x` agrees with the AHSS: `H^6 = Z/2` is the only even torsion.
  - `c(xi) = 1` because `c_1` and `c_2` land in zero groups and `c_3(xi) = 0` by rank.
  - `E_R` is stably trivial of rank `16 > 11` and hence trivial.
  - The quaternionic nontriviality follows correctly by forgetting to the complex class.
- **The orbit invariants are proved, not sampled.**
  - `rho` is complete by phase normalization and the transitivity of `G_2` on `V_2(R^7)` and `S^6`.
  - `(lambda, rho)` is complete because the phase fixes `mu`, the quadric fixes `u dot u`, and the unit formula fixes
    `u^* u`.
  - The Gram ball is complete modulo SLOPPY 5.
  - The constancy of the representations along connected principal loci follows from integer multiplicities on a
    constant-rank kernel with a fixed stabilizer. The fixtures check the implementation, and the README says so.
- **The transition cocycle** `g_IJ = P_I F_J` is a rational-function identity forced by `P_I F_I = I`. The `U(6)` and
  `U(8)` reductions by Gram normalization are standard. The refusal to claim `Sp(3)` is correctly scoped.
- **Derived numbers in the upstream producers.** `kernel_symmetry.py` derives the nullspace dimension 18, the
  projection ranks 16 and 17, the boost rank increase, the center dimension 4, the derived dimension 14 and the seven
  orbit ranks, and compares each against a stated constant or `EXPECTED_ORBIT_DIMENSIONS` in its pass flag. The
  fixture producers compare computed tangent ranks and stabilizer dimensions with their expected values, and
  `_require` the stabilizer dimensions 1 and 4. The printed-only constants are confined to the topology helpers and
  the final certificate named in SERIOUS 1 and 2.
- **The `--out` replay** is byte-identical on all eleven producers, and every self-test and test passes. Ruff and mypy are clean. No Singular is used. Every producer
  stays under the 15 s `pr.yml` gate budget on this host. `v_topology_representation.py`, at 13 s, has the least
  margin on a slower hosted runner.

## Steelman

The record's mathematics is right, and the hard step was correctly identified and avoided. `B9`, whose homotopy
dimension 14 exceeds the cancellation range, is handled by an explicit section. The 12-dimensional `VB` is split into
an 11-dimensional cancellation and an equivariant circle argument. The open `V`, whose reduced K-group is genuinely
nonzero, is reduced by a free phase action to a space with vanishing reduced K-theory.

The nullity-sixteen order-two class is computed by a correct Hodgkin calculation and agrees with the cellular AHSS.
The ledger is candid where it matters most: the item-4 classification is labeled **Inferred**. The record lists its
open residuals explicitly: the component census, the real type of `xi_R`, and nonconstant smaller reductions. Every
retained result replays byte for byte from `--out`.

## Verdict

The core is sound. The classification table is correct:
- the five complex bundles of nullity twelve are `C^6`;
- `N_+-` is `C^2 + 3 xi` with class `x != 0` in `Z/2`;
- every real bundle is trivial, and every characteristic class vanishes.

Hand checks and two exact probes confirm the branching restrictions and the phase winding that the inferred steps
need. What the record overstates is its machine evidence. `bundle_invariants.py` and the topology helpers restate the
proofs as constants, and mutate those constants, so no planted error in the geometry or the inputs could make them
fail.

The single most important fix is to derive the certificate's inputs from the bound rows and to mutate inputs rather
than literals. The cheapest decisive step is to replace the hand-typed `7` and `14` restrictions with the Casimir
computation from the exact stabilizer generators. With that done, the item-4 row can keep **Inferred** for the
topology theorems and **Observed** for every number a script derives.
