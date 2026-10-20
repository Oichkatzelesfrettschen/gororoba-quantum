# Model discrimination before atlas spending

The execution priority starts with the existing shot-ordered observations,
selects a concrete optimizer action, and validates the action before a broad
atlas consumes QPU time. The [execution roadmap](../../gororoba_quantum/QPU_EXECUTION_ROADMAP.md)
owns job identities and accounting; the shared coordination ledger owns
execution assignment. Both proposed atlas cases remain unapproved.

## How the literature fits the decision

| Question | Sources | Useful design consequence |
| --- | --- | --- |
| What does feedback cost or improve? | [Corcoles](2102.01682.md), [semiclassical QFT](papers/quant-ph-9511007.md), [qubit recycling](papers/1111.4147.md) | Compare the specified estimator and unitary-power access; measurement count differs from billed seconds. |
| Can readout explain the residual? | [QILGST](papers/2103.03008.md), [interpretable instruments](papers/2602.03938.md), [Pauli-noise ambiguity](2505.22629.md) | Separate classical report error from continuing-state disturbance and coherent error. Identifiability comes before fitting. |
| Does packing change the mechanism? | [QuMC](2102.05321.md), [palloq](papers/2112.07091.md), [Sarovar](papers/1908.09855.md), [Rudinger](papers/1810.05651.md) | Treat companion activity and patch as controls; a qubit-distance rule supplies a placement constraint, not measured independence. |
| Does time confound the contrast? | [Proctor](papers/1907.13608.md), [NIST blocking](quantum_experiment_design_sources.md) | Preserve shot order, execution windows and balanced placement; inspect drift and dependence before using stationary-repetition intervals. |
| Where do seconds go? | [IBM usage documentation](quantum_experiment_design_sources.md), [retained timing](../../gororoba_quantum/QPU_EXECUTION_ROADMAP.md) | Price initialization/repetition and job overhead alongside compiled duration; reduce shots only against a declared precision target. |
| What does an algebraic fringe establish? | [Koebisu](2608.08232.md), [Reggiani](papers/2411.18881.md), [Zhilina](papers/2608.28163.md), [block encoding](papers/1806.01838.md) | Distinguish finite circuit validation, continuous topology, and normalization-dependent uncertainty. |

## Existing observations constrain models

The [terminal-channel analysis](../../results/live/2026-10-12T055624.091217Z/TERMINAL_CHANNEL_HYPOTHESIS.md)
rejects one additional common binary stochastic channel as the complete repair
of the specified replay. Its conditional simultaneous interval and stationarity
assumptions remain part of the result. The analysis neither rules out replacing
the original readout model nor identifies a unique physical cause.

The coherent and dynamic arms use different terminal writers and contain other
routing/control differences. Their performance gap motivates a controlled
comparison. The same gap alone cannot choose between readout, measurement
backaction, latency, coherent error and history dependence. The retained
no-feedback joint outcomes also prevent labeling every mismatch as a wrong
classical discriminator bit.

The old jobs are exploratory evidence for the next design. A new model keeps
distinct training and validation observations. A model earns use in the
optimizer only when it predicts the declared contrast and the selected action
improves a held-out hardware endpoint at the declared cost.

## Coordinated minimum pilot and decision boundary

The execution owner documents the candidate in `MODEL_DISCRIMINATION.md` on
[the active experiment PR](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/36).
The proposed pilot has four PUBs: labels `s1,s3`, each with measured feedback
`F` and known-label unconditional `P(-pi/2)` correction `U`. Both arms retain
the first measurement, reset and both recorded bits. Compilation must establish
a common routed prefix/suffix, terminal writer and matched schedule before the
contrast receives its intended interpretation.

The proposed decision adopts `U` only if both labels satisfy
`lower_CP(p_U)-upper_CP(p_F)>0.01`. Four one-sided Clopper-Pearson bounds use
tail probability `0.0125` each, giving simultaneous coverage at least 95%
under the stated binomial sampling assumptions. The complete new acquisition
is prospective validation. Drift or dependence requires a revised uncertainty
contract; a failure to pass remains inconclusive rather than evidence of
equivalence. The policy applies to the known-label witnesses. An unknown-phase
algorithm cannot replace its required feedback using a label it does not know.

At 8192 shots/PUB, the owner's historical conditional timing estimate is
11.2425 seconds for 32768 PUB-shots. That estimate uses earlier circuits and
does not constitute a new compiled dry run or a charged-time guarantee.
Fresh calibration, exact QPY, source identity, precision, job limits and user
approval still determine submission. The measurable action also needs
equal-or-lower charged time, or an explicit justified cost tradeoff, before
becoming an optimizer policy.

## Algebraic reduction is a separate optimizer candidate

The [folding audit](open_gororoba_folding_proofs.md) proves why discarding a
fold complement can destroy zero products. A complete affine-XOR block
decomposition retains every sector and gives
`||L_x y||^2=sum_C ||B_C y_C||^2`. For this observable, sectorwise acquisition
can replace a five-qubit data state with weighted two-qubit block states on
the existing four-term support family. Full coherent action has a different
contract and retains the sector label. Kernel classification requires every
sector, exact weights and transitions.

An eventual hardware comparison prices all sectors, preparation, LCU
normalizations and joint uncertainty. For `q=alpha^2 p`, a probability
interval of half-width `h` becomes a norm-squared interval of half-width
`alpha^2 h`; fixed reconstructed precision can require shots proportional
to `alpha^4`. Thus fewer qubits or more simultaneous endpoints alone cannot
decide the optimizer. Exact CPU calculations first verify the same output;
hardware then tests accuracy and billed cost against matched controls.

## Atlas admission

A broad atlas needs a stated estimand that the smaller decision cannot answer,
a practical effect or equivalence margin, complete controls, multiple-testing
coverage, and an incremental cost argument. Four probes of a real four-state
sector yield four quadratic values, while a general symmetric Gram matrix has
ten entries. Repeated signed-cosine laws and identical ideal sector vectors
are useful controls, not independent discoveries of topology.

The [Koebisu decomposition](koebisu_rank_stratum_research.md) assigns exact
rank and attachment proofs to classical symbolic work. The QPU supplies
physical implementation evidence for a specified observable. That division
keeps the scientific question and the expensive measurement aligned.
