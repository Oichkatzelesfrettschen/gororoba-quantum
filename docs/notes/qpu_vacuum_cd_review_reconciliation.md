# Reconciliation of the patch-window, campaign and vacuum/dark-sector reviews

Four external reviews of the patch-window acquisition and campaign records,
one synthesis on dark-sector and quantum-vacuum research, and seven further
reviews of the resulting reconciliation made claims
about this repository, its sister project and the literature. Each row
gives the claim, its status and the artifact that settles it. Statuses:
verified (reproduced from retained data or source), refined (reproduced and
sharpened), corrected (the claim or a repository statement was wrong and
the record now says so), refuted (the source contradicts the claim), open
(needs work named in the row), out of scope (needs apparatus or authority
this repository lacks).

## QPU records

| Claim | Status | Evidence |
|---|---|---|
| The ten registered patch endpoints all have intervals containing zero; the result is nondetection, not equivalence | verified | `collect.json` family_analysis; results/live/PATCH_WINDOW_FINDINGS.md reports the collector's ten rows |
| The findings first reported window control 0 where the contract registers control 1, and omitted the spectator endpoint | corrected | the findings table now comes from the collector; control-0 and work-B rows are labeled descriptive |
| The executed case differs from the approved case in source, digest and circuit archive | refined | source commit and experiment digest differ; the compiled `isa.qpy` is byte-identical (`cd45b699`) in both records; the run stays classified as an approval and review-gate deviation; issues #76 (classifier parity) and #77 (approval receipt) |
| Four approval refusals were reported | corrected | three refusal records exist, each for one cause, the mixed static/dynamic group |
| The account spent 210 s over 15 jobs, 270 PUBs and 659456 PUB shots: 49 s historical and 161 s in the campaign, leaving 19 s of the 180 s campaign cap and 390 s of the 600 s account window | verified | a fresh read-only service inventory and the regenerated retention audit (results/live/qpu-job-inventory.json, qpu-job-retention-audit.json); the earlier ten-job snapshot is dated as historical |
| The product-state Ramsey probes rule out the window as the source of the orbit phase | corrected | small sampled phases and nondetection constrain unconditional idle detuning only; a same-calibration orbit refit finds context dependence that no phase-specific mechanism explains uniquely (rows below), so no mechanism is localized |
| The RCA joint quasi-static fit (49.9 on 18 dof) supports the window attribution | corrected | the retained rca-mechanism-fit.json records the joint fit as skipped; the RCA marks the numbers superseded |
| The refit's two kickback phases are separately estimable | corrected | the modeled law depends only on theta = phi1 + phi2 (amplitude (1 + st) e1 + t e4 + s e16 with s, t the round phases): (phi1 + t, phi2 - t) leaves every probability unchanged; the phase model has 4 identifiable parameters, not 5 (Jacobian rank 4) |
| The phase and arm-bias models have equal complexity, and the shared-phase test has 4 degrees of freedom | corrected | effective dimensions are 4 and 5; adding phase to the shared-bias model adds 1, and three context phases against one shared phase add 2 (LR 16.14, reported without a calibrated p-value); AIC 12.49 against 12.61 in the nominal context is a tie |
| The arm-bias model is a mechanism alternative to phase | refined | its deviance equals the first-bit homogeneity G^2 in every context (2.606, 1.535, 0.634): the control bit is measured before the arms diverge, so equal first-bit marginals are a causality constraint and the arm-bias model is the causal saturated model; the one-phase model's excess over it is 1.89, 2.47 and 1.16 on 1 degree of freedom |
| The refit's e0 parameter models a mid-circuit misclassification | corrected | `observe` flips the reported first bit after the feedback law runs, so e0 is a post-hoc report relabel; a feedback-assignment error needs an instrument in which the reported bit selects the correction |
| A branch-unsigned average measures the round-1 work coherence | refuted | after the first control measurement the two branches carry opposite coherences (+-e^{i phi1}/2), so the unsigned average is 0 on an ideal device; the estimator weights each shot by (-1)^b0 and retains the branch record |
| Contrast is insensitive to fitted phase (0.70 to 0.17 rad with contrast 0.183 to 0.170) | verified | results/live/N21_ORBIT_RCA.md; the selected-coherence design in the findings addresses it |
| The orbit context sensitivity sits in the feedback arm | verified | per-arm counts in the findings: the no-feedback score stays within -0.135 to -0.141 |
| Qubit 144 retains 0.894 after 7.6 us against 0.953 predicted from its calibration T1 | verified | Jeffreys interval [0.874, 0.913]; one delay does not identify a new T1 |
| The next experiment is prefix-resolved or selected-coherence phase measurement with interferometric closure | open | no case is written; the four-outcome orbit law cannot separate phase from arm-dependent loss, and the case needs its own approval |

## Mathematics

| Claim | Status | Evidence |
|---|---|---|
| The non-associating fraction of basis triples tends to about 1/2 | refined and proved | exact closed form N(D) = (D-2)(D-4)(D+6)/2 and the per-pair and per-subspace structure behind it ([cd_associator_defect_census.md](cd_associator_defect_census.md)) |
| omega(1, 6, k) is one parity character at mask D-2, an unexpectedly simple law | proved | Theorem 4 in [cd_associator_defect_census.md](cd_associator_defect_census.md); the census gate checks it from 16 to 4096 |
| The cross-scale pair's Walsh support grows while its leading mode dominates | refined; eight-point formula verified to 4096, its derivation not yet reviewed | support exactly 5D/16 and peak 1 - 16/D for D >= 32 |
| Dark-dark products return to the 24-index block in 24D - 704 ordered pairs | verified and proved | XOR count proof in the census note |
| The associator defect is the coboundary of the sign cochain, so its cocycle identity carries no nontrivial class | verified | the identity holds by construction; the census note records it |
| Kirshtein Lemma 3 characterizes non-association exactly by the O_16 subloop | corrected | the lemma gives sufficient conditions; [1207.4230.md](1207.4230.md) now quotes them; quasi-octonion subspaces carry 72 non-associating triples |
| The sedenions have 8 octonion and 7 other 8-dimensional basis subalgebras | verified | census subspace split at D = 16 and the eight octonion and seven power-associative subalgebras of [Wilmot](2505.11747.md); the Cawagas record binds bibliographic identity only |
| The N=21 orbit laws are (3/8, 1/4, 1/8, 1/4) with feedback and (3/8, 1/8, 1/8, 3/8) without, contrast difference 1/4 | verified | `law` in results/live/2026-10-13T201757.782152Z/orbit_refit.py and `qpe_diagnostics.n21_labeled_law` |
| A first-swap prefix has zero control coherence on the full-cycle eigenstate chi+ = (e1 + w^2 e4 + w e16)/sqrt(3), while the full multiplier gives exp(2 pi i/3) | verified | direct evaluation: <chi+|S_41|chi+> = 0, <chi+|U|chi+> = -1/2 + i sqrt(3)/2; a prefix-phase design needs probes with nonzero overlap |
| rho_{01,10} = (<XX> + <YY> + i(<XY> - <YX>))/4 for |ab> ordering | verified | checked on a random two-qubit density matrix; the conjugate convention fails, so a selected-coherence case fixes the register order before acquisition |
| Walk A first returns its state and operator at depth 24; walk B returns its state at 30 and its operator at 120; depth-4 returns 9/16 and 1/4 | verified | `ripple_dynamics.EXPECTED_PERIODS` already asserts the periods; recomputed from `predict.associator_phase` |
| N(D), the pair law and the 168/72 plane split hold in every dimension | proved | a doubling lifting identity whose coefficients depend only on the 16 relation classes of the lower triple, certified in the census gate; derivation from external reviews, checked here ([cd_associator_defect_census.md](cd_associator_defect_census.md)) |
| The plane-type counts O(D) and Q(D) are new | corrected | Wilmot's Table 5 already tabulates them (1, 8, 50, 310, 2046, ... and 7, 105, 1085, ...); the closed forms and the plane functional l_W reproduce every listed value |
| Ordinary and split forms share every basis associator | verified | the split tables of splitoct and hypercomplex-engine match all 512 octonion associator signs with three of seven imaginary squares negative ([packages/README.md](packages/README.md)) |
| External hypercomplex packages implement the repository's algebra | verified | hypercomplex, hypercomplex-engine, Cayley-Calculator and cayley-dickson give tables identical to cd_core; octonion is a signed Fano relabeling; hypercomplex-algebra repeats its engine; mathdunders is not an algebra ([packages/README.md](packages/README.md)) |
| A package element inverse certifies an invertible multiplication | refuted | x = e1 + e10 has x x^-1 = 1 while L_x has rank 12 of 16 |
| cd_core._determinant is fraction-free | corrected | it divided in floats; it now eliminates over Fractions |
| The QET record-flip optimum is sqrt(C^2 + (1-2q)^2 A^2) - C and E_B has a cancellation-free rationalized form | verified | scripts/qet_two_qubit_reference.py checks both and the local-energy identity |
| `total, bob_local = hamiltonians(h, k)` fails the enabled Ruff F rules | refuted | F841 excludes tuple unpacking (RUF059 covers it, not selected); the variable now feeds the local-energy identity check |
| The two-qubit QET protocol injects h^2/r and lets Bob extract sqrt(h^2+4k^2) - (h^2+2k^2)/r | verified | scripts/qet_two_qubit_reference.py at machine precision; the supplied grid search sat about 4e-8 below the optimum at k = 0.1; the model matches [Hotta](1002.0200.md) under sigma^z -> -sigma^z |

## Sister project (open_gororoba, read-only here)

| Claim | Status | Evidence |
|---|---|---|
| casimir_core labels the electromagnetic coefficient pi^2/720 as a scalar result | verified | [open_gororoba_handoff.md](open_gororoba_handoff.md#vacuum-model-code-checks) |
| The worldline integrand has length^-3 dimensions while documented as a 3+1D energy density | verified | same section |
| The loop indicator includes single-surface self-energy | verified | same section |
| The reported Monte Carlo error is negative | verified | same section |
| The sign_imbalance energy law has no minimum at F = 3/8 | verified | same section |
| The Leech complement is an algebraic coordinate complement, not a physical sector | verified | same section and the census proof |
| The six findings warrant upstream issues | filed | open_gororoba #209 to #214 at b977e43f, including the seed overlap (4,174 shared seeds between adjacent quadrature nodes), the single-plate double-crossing fixture, and the 56 against 28 pair count |

## Literature claims

| Claim | Status | Evidence |
|---|---|---|
| Dark SRF improved dark-photon limits by modeling frequency instability (March 2026) | verified | [2510.02427](2510.02427.md), PRL 136, 111802 |
| ALPS II sets 1.5e-9 1/GeV below about 0.1 meV | verified | [2512.14110](2512.14110.md) |
| A dielectric haloscope excludes 387.72 to 391.03 ueV (February 2026) | verified | [2503.23354](2503.23354.md), PRL 136, 071001 |
| A levitated force sensor improved symmetron limits by more than six orders | verified | Nature Astronomy 9, 598 ([web-source note](casimir-dark-sector-web-sources.md)) |
| An atom-interferometry proposal uses sequence alternation and in situ gravity calibration (April 2026) | verified | [2511.09750](2511.09750.md), PRD 113, 084047 |
| A worldline dynamical-Casimir paper treats imperfect time-dependent boundaries (July 2026) | verified | [2604.13237](2604.13237.md), v3 dated 2026-07-22 with journal DOI 10.1103/vn2g-ryw1 |
| QET has been demonstrated on superconducting hardware | verified | [2301.02666](2301.02666.md) |
| LZ reported one high-energy recoil at 2.6 sigma global (September 2026) | verified | [2609.02823](2609.02823.md) |
| DES Y6 shows a 2.3 to 3.2 sigma preference for evolving dark energy | verified | the DES Y6 results page states 2.2 to 3.0 sigma by data combination and 2.3 to 3.2 sigma when one probe is left out (web-source note); the 3x2pt paper ([2601.14559](2601.14559.md)) alone reports w consistent with -1 |
| A July 2026 Nano Letters paper proposes a magnetic-fluid Drude-plasma discriminator | verified | accepted 2026-07-08, PubMed entry 2026-07-14, issue 26(34) dated 2026-09-02 (web-source note); companion prediction [2601.00483](2601.00483.md) |
| Ford and Roman bound negative energy density | verified | [gr-qc/9607003](gr-qc-9607003.md) |
| The ASA statement warns against reading nondetection as absence | verified | web-source note |
| IBM batch jobs may run out of order with calibrations between them | verified | web-source note |
| The dynamical Casimir effect is experimentally demonstrated | verified | [1105.4714](1105.4714.md), already registered |
| Ideal Casimir pressures and energy densities (50 to 1000 nm), the 10 mV electrostatic pressures, sphere-plane forces for R = 50 um, the Yukawa pressure -2.11e-16 alpha Pa and the 100 nm mass equivalent -4.82e-17 kg/m^3 | verified | recomputed from hbar, c, epsilon_0 and G; ideal-conductor benchmarks only |

## Out of scope for this repository

Precision Casimir force metrology, tourmaline and quartz nonlinear optics,
driven-cavity photon statistics, resonant dark-photon or axion searches and
atom-interferometric fifth-force tests need physical apparatus and
calibration this repository does not have; [vacuum_field_run_opportunities.md](vacuum_field_run_opportunities.md)
records what a gate-model experiment can and cannot contribute. Proposals for
Superforce, scalar-ZPE couplings or extra spacetime dimensions need field
equations and predictions that differ from established theory before any
measurement here bears on them.
