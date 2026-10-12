# Prior-work synthesis: what is known, what is ours, what the device showed, and what follows

This note joins the per-source notes and the five handbacks under
notes/handbacks/ into one ledger. Every repository claim carries one label:
known theorem reproduced, new proof or formalization, new implementation or
measurement, or candidate new result. [V] marks a fact re-verified in this
tree by a gate or by the orchestrator; [A] marks a delegate's derivation
carried by no gate; [H] marks a hardware measurement from record
2026-10-11T152922.787095Z.

## Ledger

| repository claim | label | source and item | what remains ours |
|---|---|---|---|
| |G_n| = 2^(n + 2^(n-1)), H_n elementary abelian of rank 2^(n-1), C_n of rank 2^(n-1) - 1 | known theorem reproduced | Kirshtein 2012, eq. (5), Thm 34, Thm 35, Lemma 10 (1207.4230.md) | the parity-lemma proof, the Boolean-coordinate form, the Rocq plan; Kirshtein's printed bound leaves a factor 2 that Lemma 2 closes [A] |
| H_n as even-weight functions of the low bits plus the top coordinate; RM(n-2, n-1) direct sum | reformulation of a known theorem | Kirshtein p. 20 generators; Elkies, RM(m-1, m) is the parity-check code (elkies-2013-m256.md) | H_n = (g \| g + c 1), C_n = H_n shortened at the origin [A] |
| sign-function degree log2(dim) - 1; associator degree max(1, bitlen(max(i, j)) - 2); census 21, 84, 360, 1488, 6048 | candidate new result | Bales 2016 states no ANF degree (1602.02843.md); induction proofs from his Cor. 4.3, Prop. 4.2, Prop. 4.5 exist as unverified derivations [A] | the formal proof |
| Walsh spectral classes within one degree: 1, 1, 2, 6, 22 classes at dims 8 to 128 | candidate new result | none found; scripts/associator_walsh_classes.py [V] | the classification and its multiplicities |
| sedenion zero-divisor spectrum {0 (x4), 1/2 (x8), 1 (x4)} | known theorem reproduced | BCDI 2009 Thm 7.2, Cor. 7.3, Prop. 7.4: M_a = L_{a*} L_a / \|a\|^2 with {0, 1, 2}; B^T B = M_a / 2 (0905.2987.md) | the Design D fringe as the eigenvalue-2 weight [A] |
| Sedenion finite corpus and four-partner structure | known theorem reproduced | Reggiani 2024 Table 1; BDI 2005 Cor. 11.2 (2411.18881.md, math-0511691.md) | [shared count conventions](cayley_dickson_sparse_census.md): 84 table pairs, 336 ordered signed rows, 168 first-relative-sign +1 rows, 84 canonical first operands [V] |
| zero-divisor membership predicate (scalar parts zero, equal norms, orthogonal halves) and det L_v = D_1^4 D_2^2 | known theorem reproduced | Koebisu v2 Lemma 3.3, Cor. 3.8, Thm 3.7; BDI 2005 Lemmas 9.4, 9.5, Prop. 12.1 (2512.13002.md) | the two counterexamples as regression fixtures [V] |
| annihilator dimensions and the maximal stratum 2^(n-4) copies of V_2(R^7) | known theorem reproduced | BDI 2005 Prop. 9.10, Thm 13.2, Thm 15.7; BCDI 2007 Thms 1.3, 1.5, 7.5 (math-0702075.md) | the retained exact [A_5 sparse census](cayley_dickson_sparse_census.md) [V]; the continuous ZD_12 length-ratio analysis remains open |
| Fano Z-string of the octonion associator (Design A) | close prior conceptual overlap; known theorem reproduced for the duality | Levratti 2026, author-hosted, Def. 1.1 (levratti-2026-fano-css.md); all 21 associator phases are the dual strings [V] | the associator reading, normalized slices, interference circuit, compile and hardware records |
| associator as a 3-cocycle of a 2-cochain twist | known theorem reproduced | Albuquerque-Majid 1998 Def. 2.3 / 7.1 (math-9802116.md); F_AM(x, y) = cd_sign(y, x) [A] | none |
| semiclassical inverse QFT with one recycled control | known theorem reproduced | Griffiths-Niu 1996 Fig. 2, eqs. (10)-(11) (quant-ph-9511007.md); recycling per Mosca-Ekert and Parker-Plenio via Martin-Lopez | the exact circuit domain, hardware mapping, controls, measured performance |
| N = 15 hybrid Shor admitted on hardware by factor yield | new implementation or measurement, narrowed | Martin-Lopez 2012 p. 2: power-of-two orders make the outcome phase-insensitive (1111.4147.md) [V in order_finding.py] | the yield tests controlled arithmetic and the decoder, not the feed-forward |
| packed replicas on disjoint layouts with a same-job reference | new implementation or measurement, narrowed | QuMC 2021 (2102.05321.md): packing, partitioning, one-hop crosstalk window are prior art | identical-ISA VF2 embeddings, hard exclusions, the TOST margin, concurrent dynamic measurements, drift gates |
| affine-residual challenger rejected | new implementation or measurement | Kissinger-MvdG 2019 (1904.00633.md): break-even 35 CNOTs against a 91-CNOT minimum [A] | the closed negative result; the uncontrolled-B conjugation idea is open |
| hidden-shift or Albert claims | none retained | Roetteler 2008/2009, GRR 2011, Decker et al., Kaufman-Minzer, Gilyen et al. (0811.3208.md and following) | Design C is the u-marginal of a known sampling subroutine; no associator phase is bent [A]; the 2^(d+1) derivative test refutes a blanket classical bound |

## What the device showed, in the units it reports

ibm_kingston (Heron r2) runs at dt = 4 ns with a 250 us default repetition
delay. One submitted PUB shot of the six-PUB dynamic job cost 272.9 us of
circuit execution: the repetition delay plus a 22.9 us scheduled circuit.
Measurement is 2.18 us (545 dt), a reset the same plus a conditional play,
and the feed-forward round trip is a 533 to 577 dt broadcast plus a 7 dt
receive, 2.2 to 2.3 us, growing 44 dt for seven more parallel streams [H].
The work register idles 5.5 to 9.5 us across a measure-reset-feed-forward
segment; with T2 medians of 213 us that idle costs the folded-QPE second bit
about 5 points under the T2 model, a quarter of the 18-point gap to the
calibration-derived Pauli model [H for the measured gap]. The remaining
residual has unresolved causes; two of six layouts carry a coherent
second-bit bias. The mechanism ladder tests specific explanations under
the control assumptions in HARDWARE_PLAN.md. Nine concurrent
feed-forward streams cost 187 dt of schedule against two, with no measurable
fidelity cost on the shared layout, and that layout had a cross-group
one-hop neighbor in the packed PUB [H, V]. The factor-yield admission of
hybrid Shor is true and phase-insensitive; folded QPE is the one feed-forward
test the record contains [V].

## What the program does next, in order

1. The feed-forward mechanism ladder on one layout (HARDWARE_PLAN.md,
   "Risks"): archived circuit; measurement replaced by an equal delay with
   the correction applied unconditionally; measurement kept and
   feed-forward removed; two-control QPE. Each contrast tests a mechanism
   under explicit control assumptions; the contrasts alone cannot assign
   the whole residual to gate errors. The written case remains a prerequisite
   for requesting hardware approval.
2. The feed-forward-sensitive order-finding circuit, N = 21, a = 4 at two
   phase bits, whose four-outcome distribution moves by 1/8 in total
   variation in the sorted ideal probability masses when feed-forward is
   removed. The sampled gate checks sorted masses; labeled-outcome validation
   remains a prerequisite for a hardware case that relies on the exact
   distribution. The N21 case follows the mechanism ladder.
3. The two cubic Walsh classes at dimension 32 on five qubits
   (collision probabilities 11/32 and 5/32), after the class census is
   compared with a formal proof of the degree formula.
4. Packing keeps a one-hop buffer between groups as the default
   (QuMC's crosstalk window); the pilot's adjacency showed no cost at the
   0.03 margin on one layout and is not evidence for every pair.
5. Mathematics with finite acceptance tests: formalize the degree
   induction; exact-arithmetic rerun of the A_6 Stiefel nullity (a
   candidate negative answer to Moreno's open question [A]); the ZD_12
   length-ratio parameter; the C1465 statement review in open_gororoba.
   The A_5 sparse census, exact rank predicates, kernel-chart identities,
   and restricted attachment topology have retained gates. The
   [global classification roadmap](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md#global-classification-roadmap-and-admission-gates)
   tracks the remaining continuous base components, smooth subdivisions,
   full bundle attachments, global invariants, and unrestricted dimensional
   construction.
6. Cheap self-tests the handbacks named: the Fano-line Z-string product,
   the 63/42 anticommutation split, the mixed-flat corpus shape.
7. The [static job case](../../results/live/2026-10-11T203535.690679Z/STATIC_CASE.md)
   remains behind the mechanism ladder and N21. Its approximately 23-second
   expectation differs from the two 90-second per-job service ceilings
   (180 seconds combined). The case tests static-workload model conformance.
   The Albert construction needs a different encoding than LCU (alpha of
   1458) before a case exists.
