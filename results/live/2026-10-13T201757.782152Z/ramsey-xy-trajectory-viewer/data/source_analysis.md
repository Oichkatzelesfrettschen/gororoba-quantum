# Fez patch-window characterization: evidence and limits

**Hardware:** IBM Fez, same-calibration acquisition 2026-10-13, control Q142, work Q136/Q144, Q143 orbit work-bit / characterization spectator, neighbors Q123/Q145.

**Provenance:** Three job IDs in [retained findings](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/eb64ead57b75beb07ba8018ccfbc1e6242c5ec21/results/live/PATCH_WINDOW_FINDINGS.md); 46 circuits and 65,536 circuit-shots, 25 charged QPU seconds. Approved digest `50d512b5b40ad31f920d3cbfadc0f20e299a549b1570f0f1d2c20a031b723a70` (source 4aaea17) differs from executed `ec6e86629948407640b5e7a66a2306cca8bd7d1004227f66de50aedee898cc2f` (source `9b86a1349aa48cc3834ed446cbda7da55c3724e5`). The replacement ran without renewed digest-specific authorization. The raw data remain usable as explicitly labeled measurements. Retained base commit `eb64ead57b75beb07ba8018ccfbc1e6242c5ec21`. This reproduction uses source analysis counts and estimates, not independently rehashed raw bitstrings.

## I. Observational statistics

The X and Y circuits are distinct experiments run with matched executed idle. Define `X=2k_X/N-1`, `Y=2k_Y/N-1`, `R=sqrt(X²+Y²)`, `phi=atan2(Y,X)` with `N=1024` per basis. Only the specified separately prepared states and measurement contexts are covered. Both X and Y timing match at every retained point.

### Values at 7.604 microseconds

|Condition|Qubit|X zeros / 1024|Y zeros / 1024|Raw radius|Principal phase (rad)|
|---|---:|---:|---:|---:|---:|
|plain|Q136|963|553|0.8845|+0.0907|
|plain|Q144|985|523|0.9241|+0.0233|
|echo|Q136|988|511|0.9297|-0.0021|
|echo|Q144|994|518|0.9415|+0.0124|
|window c0|Q136|962|525|0.8793|+0.0289|
|window c0|Q144|983|496|0.9205|-0.0340|
|window c1|Q136|976|526|0.9067|+0.0302|
|window c1|Q144|986|473|0.9289|-0.0821|


The largest absolute principal phase in the 26 recorded X/Y pairs is **0.1262 rad**. These are local Ramsey phases, not the full N21 orbit-phase observable. The maximum raw length is **1.000322**, slightly above one; this is a statistical estimator with separate uncorrected readouts, not a state with a physical Bloch radius greater than one.

There are two sources of phase uncertainty: measurement noise and frequency aliasing. The echo and measurement-window fits remain unresolved because delays spaced by 2 μs admit aliases spaced by 0.5 MHz. `ramsey_fits_model_dependent.csv` reproduces the stored fitted detunings and retains the unresolved flags. Point-estimate phases alone do not unwrap the intervening evolution.

## II. Registered contrasts

> Correction: the table in this section lists window control 0 and the work-B
> measured/reset-only and paired/single comparisons as registered endpoints.
> The registered family is the collector's ten rows in
> `../../collect.json` family_analysis (window control 1, spectator excess,
> work A only for the reference comparisons); see
> `results/live/PATCH_WINDOW_FINDINGS.md`. The other rows are descriptive.


| Endpoint | Difference | Registered half-width | Interval contains zero |
|---|---:|---:|---|
| Echo − plain · A | -0.08200 | ±0.229 | Yes |
| Echo − plain · B | -0.01000 | ±0.229 | Yes |
| Window c0 − plain · A | -0.14300 | ±0.229 | Yes |
| Window c0 − plain · B | -0.02100 | ±0.229 | Yes |
| Control c1 − c0 · A | +0.05500 | ±0.229 | Yes |
| Measured − reset-only · A | -0.00781 | ±0.229 | Yes |
| Measured − reset-only · B | +0.05469 | ±0.229 | Yes |
| Paired − single · A | -0.02539 | ±0.229 | Yes |
| Paired − single · B | -0.00586 | ±0.229 | Yes |
| Orbit barrier − nominal | -0.04224 | ±0.24 | Yes |
| Orbit echo − barrier | +0.02490 | ±0.24 | Yes |

The list above is the expanded set of **11 displayed comparisons**, including separate work A/B terms; the repository plan reports its contracts in grouped form. Every interval `estimate ± registered Hoeffding half-width` includes zero. This is evidence that no effect was **resolved at registered precision**, not evidence of exact null effects. Some intervals include physically meaningful effects. Ordinary 1.96×SE intervals are a different descriptive calculation and are not substituted in the decision rule.

## III. Orbit contrasts versus previous phase fits

The three current contrasts are 0.201416 nominal, 0.159180 barrier, and 0.184082 barrier+echo. Differences: -0.042236 and +0.024902; each lies within the registered ±0.240 bound. These are **not measurements of the complex orbit-state phase**.

The prior RCA reported fitted phases 0.59, 0.70, 0.41, 0.63, and 0.17 rad for differing run arms. These were model fits with calibration differences and poor fit on at least one arm. In its nominal-repeat versus echo comparison, the inferred phase changes by ~0.53 rad but the measured contrast by only -0.013. The chosen contrast can be insensitive to the phase quantity of interest. Transferring the earlier phase claim into the new acquisition is unsupported.

## IV. Excitation retention and crosstalk

Work A: baseline-normalized retention `0.92736` against calibrated `exp(-7.604/94)=0.92229`. Exploratory Jeffreys-binomial posterior median/95% interval: `0.92758`, `[0.9085929255696198, 0.9449536308982351]`.

Work B: baseline-normalized retention `0.89381` against calibrated `exp(-7.604/157)=0.95272`. Exploratory Jeffreys-binomial posterior median/95% interval: `0.89406`, `[0.8734362644159488, 0.912688975670689]`. The normalized shortfall is **5.89 percentage points**. The posterior intervals condition on independent binomial measurements and **do not include calibration-T1 uncertainty, context-dependent preparation/readout, or nonstationarity**. They do not establish a revised T1 or a specific physical mechanism.

When a single work qubit is deliberately excited, the other recorded qubits have **unprepared-qubit point estimates at most 1.17%** across the retained 0 and 7.604 μs controls. Some Wilson upper limits reach about 2.04%, so a point-estimate ceiling is not an upper confidence bound. No joint orbit-state test follows from these controls.

## V. Model and process audit

1. The 25-second charge is inside the 27-second execution ceiling, but the submitted digest differs from what was approved. The dry-run/submit classifier mismatch created the three refusals; calibration drift was not their cause. The outcome should be retained as an unapproved replacement, not retroactively merged with the approved case.
2. Current local X/Y phase and population measurements identify no large freely precessing idle-window phase at sampled settings; they cannot exclude an entangled-state-dependent interaction or the earlier phase under a different calibration.
3. The original `N21_ORBIT_RCA.md` suggests the window is causal; the later findings recommend a gate-local mechanism. Neither attribution is yet uniquely identified by available data. Preserve both and record the hypotheses as competing, not settled.
4. The current orbit contrasts and one-qubit Ramsey observables cannot establish a complete coherent error mechanism. The next discriminating experiment is exact round-1 multiplier-prefix tomography with branch/joint-coherence observables and matched physical schedules, evaluated under same-run calibration. **No new QPU run is authorized by this report.**
5. The results measure quantum-circuit and device behavior, not physical Casimir/ZPE force, spontaneous spacetime geometry, or the mathematical existence of the group G₂.

## Figure index

- `00_publication_overview`: compact paper-style summary of six linked evidence classes.
- `01_registered_contrasts`: registered decisions without post-hoc replacing confidence bounds.
- `02_ramsey_magnitude_phase`: all 26 local X/Y records on executed times.
- `03_ramsey_phasors`: complex-plane X/Y coordinates, *not* orbit state tomography.
- `04_orbit_contrasts`: same-calibration signed contrasts and ordinary descriptive SE.
- `05_population_retention`: observed excitations and baseline-adjusted calibration curves.
- `06_exchange_background`: spectator and neighbor population leakage controls.
- `07_earlier_orbit_inference`: model-dependent earlier phase fits against observed contrasts.

The full interactive offline explorer is `index.html`; numerically sourced CSVs are in `data/`. The exact unfiltered raw PUB archives are available from the linked upstream run, not inside this extract.
