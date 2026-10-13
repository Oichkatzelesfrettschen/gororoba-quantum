# Reconciliation of the patch-window, campaign and vacuum/dark-sector reviews

Four external reviews of the patch-window acquisition and campaign records,
and one synthesis on dark-sector and quantum-vacuum research, made claims
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
| The campaign spent 210 s over 15 jobs, 270 PUBs and 659456 PUB shots, leaving 19 s of the 180 s cap | verified | a fresh read-only service inventory and the regenerated retention audit (results/live/qpu-job-inventory.json, qpu-job-retention-audit.json); the earlier ten-job snapshot is dated as historical |
| The product-state Ramsey probes rule out the window as the source of the orbit phase | corrected | small sampled phases and nondetection constrain unconditional idle detuning only; a same-calibration orbit refit finds context dependence that a no-phase arm-loss model fits as well as a phase model, so no mechanism is localized |
| The RCA joint quasi-static fit (49.9 on 18 dof) supports the window attribution | corrected | the retained rca-mechanism-fit.json records the joint fit as skipped; the RCA marks the numbers superseded |
| Contrast is insensitive to fitted phase (0.70 to 0.17 rad with contrast 0.183 to 0.170) | verified | results/live/N21_ORBIT_RCA.md; the selected-coherence design in the findings addresses it |
| The orbit context sensitivity sits in the feedback arm | verified | per-arm counts in the findings: the no-feedback score stays within -0.135 to -0.141 |
| Qubit 144 retains 0.894 after 7.6 us against 0.953 predicted from its calibration T1 | verified | Jeffreys interval [0.874, 0.913]; one delay does not identify a new T1 |
| The next experiment is prefix-resolved or selected-coherence phase measurement with interferometric closure | open | no case is written; the four-outcome orbit law cannot separate phase from arm-dependent loss, and the case needs its own approval |

## Mathematics

| Claim | Status | Evidence |
|---|---|---|
| The non-associating fraction of basis triples tends to about 1/2 | refined | exact closed form N(D) = (D-2)(D-4)(D+6)/2 and the per-pair and per-subspace structure behind it ([cd_associator_defect_census.md](cd_associator_defect_census.md)) |
| omega(1, 6, k) is one parity character at mask D-2, an unexpectedly simple law | refined | the degree-1 case of the repository's associator degree formula (open proof, task M1) |
| The cross-scale pair's Walsh support grows while its leading mode dominates | refined | support exactly 5D/16 and peak 1 - 16/D for D >= 32 |
| Dark-dark products return to the 24-index block in 24D - 704 ordered pairs | verified and proved | XOR count proof in the census note |
| The associator defect satisfies a cocycle identity and so may carry topological meaning | corrected | omega is the coboundary of the sign cochain; its cocycle identity holds by construction |
| Kirshtein Lemma 3 characterizes non-association exactly by the O_16 subloop | corrected | the lemma gives sufficient conditions; [1207.4230.md](1207.4230.md) now quotes them; quasi-octonion subspaces carry 72 non-associating triples |
| The sedenions have 8 octonion and 7 other 8-dimensional basis subalgebras | verified | census subspace split at D = 16; [Wilmot](2505.11747.md) and Cawagas ([web-source note](casimir-dark-sector-web-sources.md)) |
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
| DES Y6 shows a 2.3 to 3.2 sigma preference for evolving dark energy | corrected | the registered Y6 3x2pt abstract ([2601.14559](2601.14559.md)) states LambdaCDM parameter differences from the CMB (1.8, 2.3, 2.8 sigma) and w consistent with -1; the (w0, wa) analysis is in unregistered companion papers |
| A July 2026 Nano Letters paper proposes a magnetic-fluid Drude-plasma discriminator | refined | published 2026-09-02, Nano Lett. 26, 11398 (web-source note); companion prediction [2601.00483](2601.00483.md) |
| Ford and Roman bound negative energy density | verified | [gr-qc/9607003](gr-qc-9607003.md) |
| The ASA statement warns against reading nondetection as absence | verified | web-source note |
| IBM batch jobs may run out of order with calibrations between them | verified | web-source note |
| The dynamical Casimir effect is experimentally demonstrated | verified | [1105.4714](1105.4714.md), already registered |

## Out of scope for this repository

Precision Casimir force metrology, tourmaline and quartz nonlinear optics,
driven-cavity photon statistics, resonant dark-photon or axion searches and
atom-interferometric fifth-force tests need physical apparatus and
calibration this repository does not have; [vacuum_field_run_opportunities.md](vacuum_field_run_opportunities.md)
records what a gate-model experiment can and cannot contribute. Proposals for
Superforce, scalar-ZPE couplings or extra spacetime dimensions need field
equations and predictions that differ from established theory before any
measurement here bears on them.
