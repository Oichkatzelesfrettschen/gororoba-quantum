# Ripple spatial packing and derived observables

The retained historical ripple plan assigns seven five-qubit atlas lanes, two four-qubit walk lanes, and three Design C lanes of widths three, four, and five: 55 logical qubits before routing footprints and separation buffers. The source schedule contains 146 physical execution rows: 96 canonical atlas rows, five matched companion rows, 24 readout rows, and 21 isolated rows. The walk occupies ten atlas/companion rows; the nine Design C members occupy three atlas rows. Extra physical qubits alone do not remove any required row.

The historical ripple and rank cases require current-source renewal and remain
held behind the model-discrimination decision. Their current admission and
execution authorization are false.

The supported family interface fixes one placement per scientifically distinct lane. `algebra_planning.family_candidates` and the CLI require replica tier one. The optimizer also permits arbitrary dependence among components in each shared shot, so additional identical replicas do not automatically reduce the required shot count. Raising replica tiers or filling an isolated row would alter the current measurement contract.

## Concrete next packing designs

1. A fourteen-lane atlas with six edge-pair blocks has a provisional 100-row count: 48 atlas + 12 readout + 28 atlas-isolated + 4 walk-isolated + 3 ladder-isolated + 5 matched companion rows. The design uses 90 logical qubits and retains every original edge's eight phases within its assigned patch. However, twelve edges per kite occupy at most twelve of fourteen lanes. The design therefore loses the incumbent every-kite-on-every-lane coverage and introduces an incomplete crossover. The 46-row reduction (31.5 percent) cannot carry the incumbent balance claim or admission unchanged.

2. An explicit 110-row construction restores every-kite-on-every-lane coverage. Index kites by `k = 0..6`, edge-pair blocks by `b = 0..6`, and lane banks by `s = 0,1`. Blocks zero through five carry edge pairs `(0,1), (2,3), ..., (10,11)`; block six repeats `(0,1)` as labeled bridge copies. Assign each copy to lane `7*s + ((k+b) mod 7)` and execute all eight phases of that copy on its fixed template and lane. Every block occupies all fourteen lanes, and every kite visits all fourteen lanes across the seven blocks. The 84 canonical edge sweeps remain; fourteen additional edge/patch copies supply the missing coverage. Keep copy labels distinct in inference and retain identical fourteen-lane companions across each two-way walk comparison. The arithmetic becomes 56 atlas + 14 readout + 28 atlas-isolated + 4 walk-isolated + 3 ladder-isolated + 5 companion = 110 rows: 36 fewer than 146 (24.7 percent), with 90 logical qubits. The construction establishes the stated coverage and row count. Routing, placement, randomization, uncertainty, scheduler duration, and noisy admission remain to be qualified; every-kite/lane coverage alone does not establish every possible edge/patch balance.

3. Packing the twenty rank-sector science rows into twenty ordinary atlas rows is a separate combined-family design. Preserve all sixteen rank-sector isolated rows as globally isolated workloads, retain the ripple isolated rows, and keep rank activity out of the matched walk pair unless both companion rows receive identical rank activity. The ideal row arithmetic becomes 146 + 16 = 162 instead of 146 + 36 = 182, with 87 logical qubits before routing and buffers. The combined design changes the packed context of both families, so independently prepared cases cannot inherit their old admission. The current family selector does not combine families.

4. Reuse the completed folded-QPE evidence. Any new dynamic/fixed-placement case requires separate admission and approval. Spatially allocating different diagnostic variants to unrelated patches confounds mechanism and patch. A future balanced patch crossover requires its own controls, scheduler qualification, and pricing; a Batch wrapper supplies no same-shot packing.

The 146-row schedule remains the reference atlas design. Its next preparation follows the model-discrimination decision and requires fresh placement and statistical admission. Native dry-run scheduler availability remains a separate provider capability constraint.

## Bounded placement evidence

The [placement evidence](placement-feasibility-evidence.json) records a classical probe against the Kingston calibration labeled `2026-10-11T22:36:25-07:00`, using source commit `105aa36f88579b337a315f7421ef01144bdf8858`. The probe selected one routed candidate per group at seed `20261010`, retained embeddings above the 0.9 relative quality floor, and required physical one-hop separation, including excluded couplers. Same-pool mappings with identical occupied qubit sets were coalesced only for feasibility.

| Selected finite domain | Logical qubits | Binary variables | HiGHS result | Solver seconds |
| --- | ---: | ---: | --- | ---: |
| Incumbent ripple, 12 groups | 55 | 332 | Infeasible | 0.036 |
| Fourteen-lane edge-parity split, 19 groups | 90 | 505 | Infeasible | 0.063 |
| Ripple plus rank sectors, 20 groups | 87 | 738 | Infeasible | 0.102 |

The 90- and 87-qubit backtracking probes each reached their 180-second limit before the binary solver settled their selected domains. A separate audit compared 409,289 cross-group candidate pairs and confirmed that the edge constraints implement occupied-qubit versus other-buffer conflicts while allowing buffer-buffer overlap. The production pairwise precheck reproduced all three finite-domain results. A certificate rejects only the selected candidate combination; other routing seeds, candidate combinations, calibrations, and policies remain outside the result. The probe sent zero primitive calls and zero QPU jobs.

The 90-qubit probe split incumbent atlas members by edge parity. It did not compile or place the new 110-row allocation, whose group composition and bridge copies require separate preparation. The compact evidence retains occupied-qubit sets and physical edges for replay of the finite binary models, and hashes the full mapping payloads and routed source files. That replay establishes spatial incompatibility within the recorded domains; it does not reproduce calibration scoring or qualify an execution schedule.

## Additional visuals from the planned acquisition

- For each four-bit walk outcome distribution, calculate all fifteen nontrivial Z-string parities. The complete vector is the classical Walsh transform of the measured distribution; it does not recover unmeasured coherent phases. A parity texture or signed hypercube color field supplies a view beyond return probability.
- Form the five Hamming-distance shell probabilities about the prepared basis vertex, the mean distance, and its second moment. The RX mixer connects one-bit neighbors, so radial occupancy on the four-dimensional Boolean cube has a direct circuit interpretation. Arbitrary artistic embeddings must retain the basis-label mapping.
- Estimate classical collision probability with `sum_x n_x (n_x - 1) / (N (N - 1))` for N > 1. The estimator is unbiased under independent stationary repetitions. Inverse participation and entropy are nonlinear descriptive summaries unless uncertainty is separately propagated.
- Fit each eight-phase atlas fringe to a discrete Fourier basis. Show the first harmonic's quadratures, phase lag, and higher-harmonic residuals; retain the raw points and simultaneous intervals. A contrast-derived graph overlays measured visibility on the exact signed box-kite edges. The algebraic edge sign and noisy inferred contrast remain distinct fields.
- Use retained shot ordering to compute same-PUB cross-lane covariance of ancilla or return indicators and connected parity correlations. Show a separate covariance matrix per fixed execution row or matched block. Pooling unlike rows can create correlation from different programmed means. Observed covariance can diagnose shared disturbance but does not identify a specific crosstalk mechanism.
- For rank-sector shots, retain all four selector outcomes, their parity, and leakage into each unsuccessful selector state. The current circuit measures selectors only; a data-qubit distribution would require additional measurements and a new archive/analysis contract.

These observables would reuse the planned ripple/rank rows after an approved acquisition. The statistical contract covers selected means and contrasts; newly promoted inferential claims need explicit uncertainty and multiple-comparison treatment. Exploratory visuals would remain descriptive and derive from the retained raw archive of that future acquisition. The completed folded-QPE archive supplies its own distinct measured outcomes.

## Source surfaces

- `ripple_experiments.py`: fixed lanes, source templates, randomized bundles, matched companions, per-edge readout controls, isolated sentinels.
- `ripple_contracts.py`: raw endpoints, crossover, packed/isolated differences, interpretation limits.
- `algebra_planning.py`: one-replica family policy, exact sparse-row validation, actual routed ancilla writer controls.
- `live_run.py`: joint placement, physical one-hop buffers, sparse fusion, lossless shot-ordered register storage.
- `experiment_optimizer.py`: arbitrary within-shot dependence and simultaneous precision admission.
- `rank_sector_experiments.py`: twenty science rows, sixteen isolated rows, selector-only measurement.
