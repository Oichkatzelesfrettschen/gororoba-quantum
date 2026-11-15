# Tuna-17 null rotation scan: gate-noise and q12 phase refit of the retained histograms

Status: exploratory post-hoc fit of retained shots. It submits no provider job, draws no random number, changes no
retained record and no preregistered verdict (the series reads `unresolved_none` in
[the analysis](../../../results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json)). Entry:
`scripts/qi_pathion_null_rotation_scan_phase_refit.py`; record:
[pathion_null_rotation_scan_tuna_17_phase_refit.json](../../../results/quantum_inspire/pathion_null_rotation_scan_tuna_17_phase_refit.json);
test: `tests/scripts/test_qi_pathion_null_rotation_scan_phase_refit.py`. Subject: the 30 data circuits of the 21
retained batches `results/quantum_inspire/runs/2026-11-15T001929Z-pathion_null_rotation_scan_tuna_17-batch-*`,
read as in [the exploratory reading](tuna17-null-rotation-scan-line-phase.md).

## Result

Computed over the measured counts, with the density-matrix forward model below:

- A zero-parameter exact circuit fits the 30 x 32 outcome counts with chi-square 2,696,334.5 on 930 degrees of
  freedom. One retention per data batch, which contracts the exact law toward uniform, lowers it to 182,795.4 on 920.
  The figure 182,795.4 is therefore the exact circuit with ten fitted retentions, and the noise-free model proper
  stands at 2,696,334.5.
- Five gate-noise terms fit with chi-square 51,766.95 on 925 degrees of freedom. Three of the five parameters (pulse
  amplitude damping, pulse phase damping and CZ depolarizing) end below 1e-4, so the fit rests on CZ amplitude damping
  (0.01943) and CZ phase damping (0.03231).
- A z rotation of q12 of -0.1508 rad lowers the chi-square to 42,848.8 on 926 degrees of freedom (four free
  parameters: CZ amplitude damping, CZ phase damping, a selector flip that ends at 0, and the q12 phase). With the
  five noise terms and the q12 phase together the value is 42,849.0 on 924 (q12 phase -0.1508).
- The best chi-square per degree of freedom is 46.3. The statistic shows that the retained counts scatter more than
  independent multinomial draws around each of these mean laws; it cannot say how much of that excess is a
  missing term of the mean law and how much is overdispersion from drift or the shot-order line (Limits).
- A deterministic multistart and profile search found no lower minimum than any headline value above (Search).

| Quoted figure | Reproduced | Model | Record key (`models.NAME.KEY`) |
|---|---|---|---|
| exact model, 182,795.4 | 182,795.354 on 920 | `exact_circuit_batch_retention` | `histogram_chi2`, `dof` |
| five noise terms, 51,767 on 925 | 51,766.952 on 925 | `five_noise_terms` | `histogram_chi2`, `dof` |
| q12 phase about -0.151 rad, 42,849 | 42,848.820 on 926; phase -0.150753 | `cz_noise_flip_q12_z_after_pulse` | `histogram_chi2`, `values.z12` |
| the same with the five noise terms | 42,849.038 on 924; phase -0.150796 | `five_noise_terms_q12_z_after_pulse` | `histogram_chi2`, `values.z12` |
| phase damping 0.031 or 0.032 | 0.032313 (five noise terms); 0.031077 (with the selector flip) | `five_noise_terms`, `five_noise_terms_selector_flip` | `values.cp` |

The two phase-damping figures belong to two models: the five-term fit gives 0.0323135 and the same fit with a
selector flip (0.01661, flipping when bit d0 reads 0) gives 0.0310771. The two q12-phase fits give 0.02717 and
0.02700, so a quoted phase damping names its model.

The selector-contrast chi-square over the 30 circuits (`contrast_chi2`) reads 4,785.7 (exact circuit), 1,179.1
(retention), 1,126.1 (five terms), 703.7 (five terms and selector flip) and 428.4 (q12 phase, four parameters).

## Model

The retained `b0` circuit (five region qubits, the instruction list that
`scripts/qi_pathion_null_rotation_scan_cases.py` parses from the pinned text) runs on a density matrix with each
arm's pulse rewrite and injected angle. The five noise terms act as follows: pulse amplitude and phase damping
(`pa`, `pp`) after each pulse; two-qubit depolarizing (`cd`), then amplitude and phase damping (`ca`, `cp`) on both
qubits after each CZ. The q12 phase is a z rotation of q12 after each of its pulses (`z12`) or after each CZ that
touches it (`c12`). The law over the five logical bits goes through the joint readout matrix of the mean of the two
adjacent readout brackets, and the Pearson chi-square compares it with the 32 counts of each circuit. In all seven
models an expected probability below the floor 1e-9 enters the denominator as the floor; every model's
`min_expected_probability` (0.0023 for the exact circuit, 0.0031 to 0.0035 for the gate-noise models, 0.013 for the
retention model) lies far above it, so the floor changes no reported number. Each fit is `scipy.optimize.least_squares`
with the bounds, `start`, `x_scale` and `diff_step` stored in the record per model (the retention model keeps the
scipy defaults for the last two, stored as 1.0 and `null`). Degrees of freedom are 30 x 31 less the declared
parameters, a parameter that ends on a bound included. The self-test checks the simulator against `forward_law` and
`noisy_law`, recovers a planted q12 phase of -0.1 rad and a planted retention from exact counts, and requires
`verify_search` to reject a search that finds a lower minimum.

The script selects the run directories by the names of the series plan and requires each `raw/` directory to hold
exactly the files that the run's retained manifest lists. The script does not test that git tracks them; the run on a
clean checkout of the branch shows that every input is tracked.

`--check` replays the seven headline fits, compares the record with relative and absolute tolerance 1e-5 (starts,
step scales and floor included) and requires that the stored search found no lower minimum. Both q12 placements
(`z12` after pulses, `c12` after CZ gates) reach the same computed chi-square to 1e-12 relative. `hypothesis:` the
counts cannot tell the two placements apart. The pinned `b0` holds five q12 pulses and four CZ gates that touch q12;
by the circuit structure a z rotation after each of the first four pulses reaches the matching position after a CZ,
and the fifth stands last before the computational-basis measurement and leaves the outcome law unchanged. This is an
inference from structure and the equal scores, not a separate test.

## Search

The headline of each model is one bounded fit from its stored start, which proves termination and no global
optimality. `--profile` replays a deterministic search that draws no random number, and the record stores for every
model the number of starts and the lowest chi-square found (`models.NAME.search`):

- the two q12-phase models fix the phase on 17 grid points across its bounds (-0.4 to 0.4 rad), fit the other three
  parameters from three starts (near the lower bounds, the stored start, the bound midpoints) and refine each local
  minimum of the profile with the phase free (52 fits). The profile has one basin, at the grid point -0.15 rad
  (42,849.18) and refined to -0.1508;
- each five-noise-term model fits from the stored start, a start of 1e-4 in every parameter, the bound midpoints and
  its fitted point (4 fits);
- the retention model profiles each of the ten batch retentions on its own (96 grid points across the bounds, then a
  bounded scalar refinement), since its objective separates by batch.

| Model | Headline | Lowest found | Starts |
|---|---|---|---|
| `exact_circuit_batch_retention` | 182,795.35448 | 182,795.35447 | 10 |
| `five_noise_terms` | 51,766.95172 | 51,766.78891 | 4 |
| `five_noise_terms_selector_flip` | 51,570.04871 | 51,570.04566 | 4 |
| `five_noise_terms_q12_z_after_pulse` | 42,849.03833 | 42,848.82018 | 4 |
| `cz_noise_flip_q12_z_after_pulse` | 42,848.81982 | 42,848.81977 | 52 |
| `cz_noise_flip_q12_z_after_cz` | 42,848.81982 | 42,848.81977 | 52 |

The lowest values lie 0.22 or less below the headlines (at most 5.1e-6 relative), inside the 1e-5 tolerance. Inference:
the midpoint and fitted-point starts stop a little further along the headline's basin, since no start ends at a
chi-square that differs by more than that; the record keeps the chi-squares and not the end points. The search found
no second basin. It covers the listed starts only; another start or a grid of other spacing could still find one.

Reproduce under the pinned interpreter from the repository root, with four workers:

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4
"$PYTHON" -B -W error scripts/qi_pathion_null_rotation_scan_phase_refit.py --self-test
"$PYTHON" -B -W error scripts/qi_pathion_null_rotation_scan_phase_refit.py --check results/quantum_inspire
"$PYTHON" -B -W error scripts/qi_pathion_null_rotation_scan_phase_refit.py --profile results/quantum_inspire
```

## Limits

- The statistic treats each count as an independent multinomial draw. The retained shot order carries a
  periodic component and the batches drift ([the exploratory reading](tuna17-null-rotation-scan-line-phase.md)), so a
  chi-square per degree of freedom of 46 to 56 (computed) holds the inadequacy of the mean law and overdispersion
  together. The fit separates neither; it shows only that the retained counts scatter beyond independent multinomial
  draws around these mean laws.
- The q12 phase was chosen after a sweep of ten candidate phase terms on the same counts. The drop from 51,767 to
  42,849 is a post-hoc improvement, with no held-out circuit and no multiplicity correction.
- `hypothesis:` a z error of about -0.15 rad on q12 is the physical cause. The computed fits show that this one term
  lowers the chi-square more than any other single term of the ten-model sweep; they do not identify a pulse, a CZ
  or a frame update as its source, and a CZ-conditional phase of any qubit pair stays untested.
- The readout matrix is fixed from the brackets and the fit has no readout parameter, so a misfit can sit in the
  readout as well as in the gates.
- The statements hold for these 30 circuits and these seven model forms. They give no value for another day,
  qubit set or backend.
