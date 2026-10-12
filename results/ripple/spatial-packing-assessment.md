# Ripple spatial packing and derived observables

The prepared ripple family already assigns seven five-qubit atlas lanes, two four-qubit walk lanes, and three Design C lanes of widths three, four, and five: 55 logical qubits before routing footprints and separation buffers. The source schedule contains 146 physical execution rows: 96 canonical atlas rows, five matched companion rows, 24 readout rows, and 21 isolated rows. The walk occupies ten atlas/companion rows; the nine Design C members occupy three atlas rows. Extra physical qubits alone do not remove any required row.

The supported family interface fixes one placement per scientifically distinct lane. `algebra_planning.family_candidates` and the CLI require replica tier one. The optimizer also permits arbitrary dependence among components in each shared shot, so additional identical replicas do not automatically reduce the required shot count. Raising replica tiers or filling an isolated row would alter the current measurement contract.

## Concrete next packing designs

1. Fourteen atlas lanes provide a bounded schedule redesign. Pair two edge blocks per physical row, keep all eight phases of each edge on the same lane/template, and preserve the two-way walk crossover with an identical fourteen-lane atlas companion workload. Atlas rows become 48 and readout rows become 12. One dark/bright isolated sentinel per atlas lane becomes 28 rows; four walk and three ladder isolated rows remain. Five companion rows remain. The resulting arithmetic is 48 + 12 + 28 + 4 + 3 + 5 = 100 rows, compared with 146: 46 fewer rows (31.5 percent). Logical occupancy becomes 90 qubits. This is a design count, not a placement, schedule, charge, or noise result. Every required routed footprint must fit with physical one-hop buffers on admitted qubits, and the denser workload needs fresh admission. Preserve the original 84 edges and eight phases; do not trade edge completeness for occupancy.

2. Packing the twenty rank-sector science rows into twenty ordinary atlas rows is a separate combined-family design. Preserve all sixteen rank-sector isolated rows as globally isolated workloads, retain the ripple isolated rows, and keep rank activity out of the matched walk pair unless both companion rows receive identical rank activity. The ideal row arithmetic becomes 146 + 16 = 162 instead of 146 + 36 = 182, with 87 logical qubits before routing and buffers. The combined design changes the packed context of both families, so independently prepared cases cannot simply inherit their old admission. The current family selector does not combine families.

3. Keep folded-QPE in its separately admitted dynamic/fixed-placement case. Spatially allocating different diagnostic variants to unrelated patches confounds mechanism and patch. A future balanced patch crossover requires its own controls, scheduler qualification, and pricing; a Batch wrapper supplies no same-shot packing.

The existing exact schedule is the appropriate immediate preparation target. Candidate one can save more rows than candidate two, but neither has a proven live placement or execution schedule. Native dry-run scheduler availability remains a separate provider capability constraint.

## Additional visuals from existing shots

- For each four-bit walk outcome distribution, calculate all fifteen nontrivial Z-string parities. The complete vector is the classical Walsh transform of the measured distribution; it does not recover unmeasured coherent phases. A parity texture or signed hypercube color field supplies a view beyond return probability.
- Form the five Hamming-distance shell probabilities about the prepared basis vertex, the mean distance, and its second moment. The RX mixer connects one-bit neighbors, so radial occupancy on the four-dimensional Boolean cube has a direct circuit interpretation. Arbitrary artistic embeddings must retain the basis-label mapping.
- Estimate classical collision probability with `sum_x n_x (n_x - 1) / (N (N - 1))` for N > 1. The estimator is unbiased under independent stationary repetitions. Inverse participation and entropy are nonlinear descriptive summaries unless uncertainty is separately propagated.
- Fit each eight-phase atlas fringe to a discrete Fourier basis. Show the first harmonic's quadratures, phase lag, and higher-harmonic residuals; retain the raw points and simultaneous intervals. A contrast-derived graph overlays measured visibility on the exact signed box-kite edges. The algebraic edge sign and noisy inferred contrast remain distinct fields.
- Use retained shot ordering to compute same-PUB cross-lane covariance of ancilla or return indicators and connected parity correlations. Show a separate covariance matrix per fixed execution row or matched block. Pooling unlike rows can create correlation from different programmed means. Observed covariance can diagnose shared disturbance but does not identify a specific crosstalk mechanism.
- For rank-sector shots, retain all four selector outcomes, their parity, and leakage into each unsuccessful selector state. The current circuit measures selectors only; a data-qubit distribution would require additional measurements and a new archive/analysis contract.

These observables require zero additional QPU rows. The current admission contract covers selected means and contrasts; newly promoted inferential claims need explicit uncertainty and multiple-comparison treatment. Exploratory visuals can be labeled descriptive and derived from the unchanged raw archive.

## Source surfaces

- `ripple_experiments.py`: fixed lanes, source templates, randomized bundles, matched companions, per-edge readout controls, isolated sentinels.
- `ripple_contracts.py`: raw endpoints, crossover, packed/isolated differences, interpretation limits.
- `algebra_planning.py`: one-replica family policy, exact sparse-row validation, actual routed ancilla writer controls.
- `live_run.py`: joint placement, physical one-hop buffers, sparse fusion, lossless shot-ordered register storage.
- `experiment_optimizer.py`: arbitrary within-shot dependence and simultaneous precision admission.
- `rank_sector_experiments.py`: twenty science rows, sixteen isolated rows, selector-only measurement.
