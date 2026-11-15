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

Measured, in the density-matrix forward model below:

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
- No model fits: the best chi-square per degree of freedom is 46.3.

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
adjacent readout brackets, and the Pearson chi-square compares it with the 32 counts of each circuit. Each fit is
`scipy.optimize.least_squares` with the bounds, starts and step scales stored in the record. Degrees of freedom are
30 x 31 less the declared parameters, a parameter that ends on a bound included. The self-test checks the simulator
against `forward_law` and `noisy_law` and recovers a planted q12 phase of -0.1 rad from exact counts.

`--check` replays all seven fits and compares the record with relative and absolute tolerance 1e-5. Both q12 placements
(`z12` after pulses, `c12` after CZ gates) reach the same chi-square to 1e-12 relative; the counts do not tell them
apart.

Reproduce under the pinned interpreter from the repository root (about 40 s with four workers):

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_WORKERS=4
"$PYTHON" -B -W error scripts/qi_pathion_null_rotation_scan_phase_refit.py --self-test
"$PYTHON" -B -W error scripts/qi_pathion_null_rotation_scan_phase_refit.py --check results/quantum_inspire
```

## Limits

- The statistic treats each count as an independent multinomial draw. The retained shot order carries a
  periodic component and the batches drift ([the exploratory reading](tuna17-null-rotation-scan-line-phase.md)), so a
  chi-square per degree of freedom of 46 to 56 shows model inadequacy and overdispersion together; the fit does not
  separate them.
- The q12 phase was chosen after a sweep of ten candidate phase terms on the same counts. The drop from 51,767 to
  42,849 is a post-hoc improvement, with no held-out circuit and no multiplicity correction.
- `hypothesis:` a z error of about -0.15 rad on q12 is the physical cause. The fit shows that this one term absorbs
  more of the misfit than any other single term of the ten-model sweep; it does not identify a pulse, a CZ or a frame update as its
  source, and a CZ-conditional phase of any qubit pair stays untested.
- The readout matrix is fixed from the brackets and the fit has no readout parameter, so a misfit can sit in the
  readout as well as in the gates.
- The statements hold for these 30 circuits and these seven model forms. They give no value for another day,
  qubit set or backend.
