# Handback: quantum systems and synthesis sources

Final statement of the delegate that wrote quant-ph-9511007.md, 1111.4147.md,
2102.05321.md, 1904.00633.md, 1806.01838.md, and 1811.08580.md, imported in
substance. [A] marks the delegate's own derivation or computation, run as
scratch scripts outside the repository and carried by no gate; [V] marks a
claim the orchestrator re-verified in this tree; [P] marks a statement of the
source. The delegate disclosed one read-only git status call, grep, sed,
sha256sum, and pdfinfo runs with a source directory as working directory
(all six sha256 values match), and two numpy scripts in the scratchpad.

The labels above describe the imported audit snapshot. A reproduced [V]
claim carries the finite check stated beside it; the label supplies neither
an all-input proof nor a continuing assertion about every later revision.
The [hardware plan](../../../gororoba_quantum/HARDWARE_PLAN.md#hardware-evidence-and-next-cases)
and [QuMC note](../../notes/2102.05321.md) carry the reconciled execution policy and
remaining checks.

## The finding that changes a retained claim

- [A] The N = 15 hardware admission does not test the semiclassical inverse
  QFT. For a power-of-two order the ideal outcome distribution does not
  depend on the feed-forward phase (Martin-Lopez, page 2: r = 2^p yields an
  incoherent mixture of p qubits). For N = 15, a = 2 the executed rounds are
  multiplier 4, then multiplier 2; the control is entangled with orthogonal
  work states (|1> +- |4> against |2> +- |8>), so the second bit is uniform
  whatever phase is applied. The delegate's exact two-round calculation
  gives {1/4, 1/4, 1/4, 1/4} with and without the -pi/2 conditional phase.
- [V] Reproduced in this tree with Aer on the repository's own circuits: the
  N = 15, a = 2 order-finding circuit with its if_else blocks removed gives
  the same four-outcome distribution as the archived circuit (each outcome
  0.244 to 0.255 at 20,000 shots), while folded QPE with the label 1 or 3
  drops from a deterministic outcome to a 0.51 / 0.49 split without the
  feed-forward.
- [A] Leading-identity pruning fires if and only if ord(a) is a power of two,
  exactly the cases where the phase is invisible. Every unit modulo 15 has
  order 2 or 4, so no N = 15 hybrid-Shor circuit can test the feed-forward.
- [A] The interference-sensitive test is N = 21, a = 4 at two phase bits:
  ideal distribution (3/8, 1/4, 1/8, 1/4), and (3/8, 1/8, 1/8, 3/8) without
  feed-forward, 1/8 apart in TVD. Order recovery is identically zero at two
  bits, so the observable is the four-outcome distribution.
- [A] The one-line comparison of the semiclassical circuit against a
  full-register QPE is the check Griffiths-Niu page 4 requires; no
  repository gate runs it.

## Griffiths and Niu 1996 (quant-ph/9511007)

- [P] Their construction is Figure 2 with equations (10) and (11): one
  accumulated classical phase phi' = phi / 2 + c / 4 per box.
- [A] The semiclassical QFT and the per-prior-bit if_test form: known theorem
  reproduced. Recycling and reset are not theirs; Martin-Lopez credits
  Mosca-Ekert and Parker-Plenio. The hardware-conformance bullet is new
  implementation or measurement, with the invariance caveat above.

## Martin-Lopez et al. 2012 (1111.4147)

- [P] Their N = 21 run is a qutrit on the orbit {1, 4, 16} with
  post-selection instead of feed-forward; the orbit size is the order, so
  the compile consumes what the algorithm returns.
- [A] The power-of-two invariance: known theorem reproduced, with a separate
  consequence bullet labeled new implementation or measurement. The
  repository's identity-padded full register does not consume the answer,
  and the repository has no N = 21 hardware result.

## Niu and Todri-Sanial, QuMC (2102.05321)

- [P] Packing identical instances is prior art in concept (they cite CQCS,
  reference 34); their delta = 0.1 bounds a predicted score difference, the
  nearer analog of the repository's replica floor, not of the 0.03 margin.
- [A] New implementation or measurement applies only to: identical-ISA VF2
  embeddings; hard exclusion of qubits and edges; the same-job replica-0
  reference with the TOST margin; the concurrent dynamic-circuit
  measurements (187 dt); the calibration-drift gates.
- [A] The imported allocator snapshot excludes neighbors within a group
  and enforces only disjointness across groups, permitting adjacency. The
  retained pilot belongs to that policy: the
  [prior-work synthesis](../../notes/prior_work_synthesis.md#what-the-device-showed-in-the-units-it-reports)
  reports a cross-group neighbor in its packed PUB. That historical
  placement remains part of the pilot's evidence.
- The allocator's default `cross_group_buffer=true` excludes other groups'
  physical CZ neighbors, including couplers excluded from routing.
  `--no-cross-group-buffer` explicitly selects disjointness alone. The
  policy change leaves the pilot's placements intact; the detailed
  all-record adjacency census remains a separate check in the
  [QuMC note](../../notes/2102.05321.md#action-items).

## Kissinger and Meijer-van de Griend 2019 (1904.00633)

- [A] The repository's Gauss-Jordan linear synthesis: known theorem
  reproduced. The affine-challenger rejection: new implementation or
  measurement, with a break-even of 35 promoted CNOTs (210 of headroom at
  6 CX each); Gauss-Jordan needs 113 CNOTs and the exhaustive minimum is 91,
  so even a perfect CNOT synthesis loses at the surrogate level (2,892
  against 2,556). The phase-controlled A is not a parity map, so
  steiner-gauss does not apply to it.
- [A] Candidate new result: conjugating by an uncontrolled B. Work-register
  gates commute with the control-only operations between rounds, so
  adjacent conjugators merge, the first and last vanish, and with one B for
  all multipliers the boundary cost is zero. Done: the exhaustive search over
  the 83,328 cosets of GL(5,2)/S_5 finds a unique ten-round optimum of 1,896
  against 2,556. The routed admission on FakeFez admits cosets cutting the
  median routed CZ by 27.5 percent (ten rounds) and 33.2 percent (the
  two-round diagnostic). Both cuts are new implementation or measurement
  ([MODULAR_SYNTHESIS.md](../../../gororoba_quantum/MODULAR_SYNTHESIS.md#linear-work-register-encoding)).

## Gilyen, Su, Low, Wiebe 2018 (1806.01838)

- [A] The Albert observable T = L_{A o B} - L_A L_B, built from Lemmas 53 and
  52 on a 32 x 32 padding (Definition 43): candidate new result; all the
  machinery is theirs. Worst-case alpha is 1458, about 5e-7 success
  probability per shot, so the construction must change (for example an
  exact unitary dilation). T is Hermitian only if [L_A, L_B] = 0, which
  depends on the trace-form symmetry of L_A, asserted from general knowledge
  and flagged. The Gram-metric requirement of the handoff is the coordinate
  metric, a different object from the Gram matrix of Lemma 47. Designs B and
  D are a Lemma 52 instance with m = 2, beta = 2: known theorem reproduced.
  "Jordan" in the paper is C. Jordan's lemma, unrelated to Jordan algebras.

## Freedman, Shokrian-Zini, Wang 2018 (1811.08580)

- [A] E_i of equation (27) is the repository's L_{e_i}: Table 1 transcribed
  and compared with cd_sign(8, i, j) for i = 1..7, j = 0..7, 56 of 56 signs
  agree. The support-equality step in the Theorem 5.1 proof gives the
  diagonality of the associator operator W. Both: known theorem reproduced.
  Everything else is background: equiangular projections, SO(8)
  universality, the Adams bound. No Fano Z-string, associator readout,
  Albert content, or hardware.

## Orchestrator's reading

The feed-forward invariance limits the retained N = 15 claim to controlled
arithmetic and factor decoding. `order_finding.py` samples the N = 15
circuit with and without conditional phases and checks folded-QPE
sensitivity. Its N = 21, a = 4 two-bit check compares sorted sampled
probabilities. A hardware case must first establish labeled probabilities
and the register-to-phase mapping against an independent exact branch or
coherent-QPE calculation; sorted masses alone permit label permutations.
[HYBRID_SHOR.md](../../../gororoba_quantum/HYBRID_SHOR.md#evidence-levels)
states the phase-insensitive factor-yield boundary and identifies folded
QPE as the first record's feed-forward test. The
[hardware queue](../../../gororoba_quantum/HARDWARE_PLAN.md#hardware-evidence-and-next-cases)
places the matched folded-QPE ladder first, the N = 21 distribution test
second, and the written static-witness case third. The first two cases
remain unwritten. The physical-neighbor buffer implements cross-group
separation by default. The affine challenger's break-even arithmetic closes
that synthesis candidate; uncontrolled-B conjugation remains a separate
open search.
