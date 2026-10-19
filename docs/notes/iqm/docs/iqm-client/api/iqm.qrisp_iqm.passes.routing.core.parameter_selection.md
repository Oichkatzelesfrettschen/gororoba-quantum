> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.parameter_selection.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.parameter_selection.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 19c6fa54920668f25b4e16be66caf65cc10093d426fae6d30ae2db0414231cc3.

# parameter_selection

Full path: iqm.qrisp_iqm.passes.routing.core.parameter_selection

Parameter selection for the SABRE layout-and-route transpiler.

Maps a single `effort` integer to the internal tuning parameters (init_layout_attempts, C, layout_iterations) that control how much classical compute is invested in finding a good mapping.

## Design rationale

The transpiler has three independent knobs:

- **init_layout_attempts (ILA)** — how many random starting layouts to evaluate. Up to `cpu_count` layouts are evaluated in parallel; each additional batch of `cpu_count` adds one parallel-wave.

- **layout_iterations** — how many back-and-forth refinement passes each layout candidate receives.

- **C** — routing diversity multiplier. `C * cpu_count` independent routing runs are performed for the best layout.

The relative importance of ILA vs C depends on the number of 2-qubit gates in the circuit:

- **Shallow circuits** (few 2-qubit gates): layout choice dominates — invest more in ILA.

- **Deep circuits** (many 2-qubit gates): routing stochasticity dominates — invest more in C.

The crossover follows the empirically fitted relationship `ILA_importance% = -11.14 * log2(num_2qb_gates) + 114.5` (R² = 0.69).

Layout iterations saturate at 3 for 14/16 tested regimes.

## Fitting methodology

The formula was calibrated on an 11,520-point parameter sweep covering grid sizes 3×3 to 11×11 and circuits with 30 to 1000 random 2-qubit gates. Per-regime response surfaces `depth ~ 1/(log ILA + 1) + 1/(log C + 1)` achieved R² = 0.72–0.90.

Validation (Formula C in `fit_parameters_v3.py`):

- Median efficiency vs model-optimal = 100%

- Mean efficiency = 77%

- Worst-case absolute depth penalty \< 0.7 gates (\< 0.5%)

Functions

|  |  |
|----|----|
| [`compute_parameters`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.parameter_selection.compute_parameters.html#iqm.qrisp_iqm.passes.routing.core.parameter_selection.compute_parameters "iqm.qrisp_iqm.passes.routing.core.parameter_selection.compute_parameters")(effort, num_2qb_gates\[, ...\]) | Derive transpiler parameters from a single effort level. |
