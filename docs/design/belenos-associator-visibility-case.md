# Belenos in-situ two-photon visibility

`scripts/belenos_associator_visibility.py` builds two `qpu:belenos` jobs that measure the photon overlap V of two source
pairs in the compiled circuit. It reuses the closure design of the Ascella two-photon associator case
([ascella-two-photon-associator-case.md](ascella-two-photon-associator-case.md)), whose job of 2026-10-29 read an
in-situ visibility of 0.892 +- 0.004 against the platform's HOM 0.890 and closed its visibility test.

## Question

The teleportation rehearsal on the layout `(18, 19, 20, 17, 22, 23, 16, 21)` of `qd_teleportation_rehearsal` job-02
places its input, Bell and CNOT photons on chip modes 18, 20 and 22. Job-02, job-03 and the exact replay of job-02 read
a pooled accepted-event correctness of 0.823 (1495 of 1816 events), while the teleportation model at the reported HOM
0.879 (g2 0.014, the anchor read's per-mode transmission) forecasts 0.848. Sweeping the model's source
indistinguishability reproduces 0.823 at 0.846 (0.8258 at 0.85, 0.8228 at 0.846, 0.8183 at 0.84). The shortfall has
two candidate homes: photon overlap below the reported figure, or error the model omits (compiled-mesh error,
detector imbalance). This case measures the overlap of two of the three photon pairs the teleportation circuit
interferes, (18, 20) and (20, 22), on the chip modes it uses. The pair (18, 22) does not fit a four-mode window, and the
collective three-photon phase of the teleportation analyzer is outside a two-photon measurement, so a high overlap on
both pairs removes the overlap explanation for these pairs only.

## Design

Each job runs the eight template iterations of the Ascella case on one four-mode window of the 24-mode chip: the
octonion associator block (a = (e6 + e7)/sqrt2, b = (e5 + e7)/sqrt2) and the quaternion control block (a = (e1 +
e2)/sqrt2, b = (e1 + e3)/sqrt2), each route in the order LaLb, Lab, Lab, LaLb. The two photons enter the window's
logical modes 0 and 2. On the window's span (e0..e3) the two control routes are one operator, so the four control
iterations run one circuit under four compilation seeds. Under the two-photon mixture model the associator LaLb route
reads D = +f(V) and the other three routes read D = -f(V), f(V) = V / (V + 1.5 (1 - V)); the in-situ visibility is
V_eff = 1.5 f / (1 + 0.5 f) with f = -mean D_control. The closure C = Delta + 2 mean D_control vanishes at every V and
detects error that differs between routes.

| Job | Window (chip modes) | Photon modes | Teleportation role (layout of job-02 and job-03) |
|---|---|---|---|
| job-00 | 18 to 21 | 18, 20 | input q0 and Bell photon a0, the pair the analyzer interferes |
| job-01 | 20 to 23 | 20, 22 | a0 and b0, the pair the postselected CNOT entangles |

Both photon modes of each window are connected source inputs, and every window mode reads at most 12.5 dark counts
per second in the read of 2026-10-31 03:39:51 UTC, under the 100 per second `DARK_LIMIT` of the teleportation case.
`--check-live JOB` repeats that check on the live platform record between `plan` and `submit`.

**Compilation seeds.** job-00 takes indices 0 to 7 and job-01 indices 8 to 15 of the ANU QRNG draw
[`draw-2026-10-31T040009Z.json`](../evidence/anu_qrng/draw-2026-10-31T040009Z.json), each in index order, registered
in [`allocations.json`](../evidence/qrng_seeds/allocations.json).

## Analysis (`--analyze RUN`)

- **Binding.** A result iteration binds to its setting by `compilation_seed`, each seed once, and its echoed
  `circuit_params` must equal the setting's. Missing, malformed and error entries bind to nothing.
- **Events.** An event is accepted when exactly two modes click, both inside the window; three or more clicks, two
  clicks with one outside the window and fewer than two clicks are counted by cause.
- **Endpoints.** Delta and D per route with multinomial standard errors, and the Ascella case's decisions: associator
  realized (Delta above 5 standard errors with |Delta_control| within max(0.05, 3 se)) and visibility closure (|C|
  within max(0.05, 3 se)).
- **Mesh spread.** Each iteration's D is reported. Within a block the sign-aligned iteration endpoints share one
  expectation under the mixture model, so their chi-square about the inverse-variance mean measures the spread of the
  separately compiled meshes; its Birge ratio, when above 1, scales the visibility's standard error
  (`se_with_mesh_spread`).
- **Visibility.** V_eff is reported only when all four control iterations are counted.
- **Overlap reading (preregistered, one-sided).** Compiled-mesh error that every route shares lowers V_eff and passes
  the closure: a random error exp(i eps H) after each block at eps 0.05 biases V_eff by -0.019 while 96 % of draws
  stay inside the closure tolerance. The reading is therefore one-sided. V_eff - 3 se_with_mesh_spread above the
  teleportation-fit forecast (0.824 for job-00, 0.8265 for job-01, the Perceval forecast at source indistinguishability
  0.846) reads "overlap high": low photon overlap does not explain the teleportation shortfall on that pair. Any lower
  V_eff reads "unresolved": overlap and mesh error remain candidates.
- **HOM comparison.** The Ascella case's |Delta - Delta_pred(V_HOM)| is kept descriptive. Delta_pred omits g2, so a
  source exactly at the read departs from it by about 0.06 (Delta_pred(0.879) 1.658 against the forecast 1.596), above
  its 0.05 tolerance.

## Forecast

`--simulate OUT JOB --hom H --g2 G [--per-mode]` writes the local noise simulation (Perceval `NoiseModel`, threshold
clicks, 2048 two-click samples per iteration) beside a staged request. Exact (unsampled) Perceval probabilities at
g2 0.014 and the read's per-mode transmission give:

| Source indistinguishability | Reading | V_eff job-00 | V_eff job-01 |
|---|---|---|---|
| 0.9057 | reported HOM 0.879 taken as raw visibility, M = (V + g2)/(1 - g2) | 0.882 | 0.884 |
| 0.879 | reported HOM taken as Perceval's indistinguishability | 0.856 | 0.858 |
| 0.846 | teleportation fit on this layout | 0.824 | 0.8265 |

One job's binomial standard error is about 0.005. The ideal-detection forecast at g2 0 returns V_eff 0.879 exactly;
the drop under g2 comes from multiphoton emission whose extra photon is lost: a uniform detection efficiency of 0.1
with g2 0.014 reproduces the whole drop, while per-mode transmission imbalance at g2 0 moves V_eff by under 0.002.

**The g2 convention is unresolved.** At the Ascella read of 2026-10-29 (HOM 88.96 %, g2 1.9 %, transmittance 5.61 %)
the same Perceval model forecast V_eff 0.858, and the run measured 0.892 +- 0.004, 8.5 standard errors higher and
equal to the reported HOM. Either the reported HOM is a raw visibility that already carries g2 (the 0.882 row), or
Perceval's distinguishable-multiphoton model overstates the contamination. The teleportation model carries the same
term (0.880 at g2 0 against 0.848 at g2 0.014), so its fitted 0.846 moves with the convention. A V_eff near 0.88 on
Belenos replicates the Ascella pattern on a second chip; the one-sided reading against 0.824 holds under either
convention for an overlap that high.

## Written case

- *What it measures.* The in-situ two-photon overlap of the source pairs (18, 20) and (20, 22) in compiled circuits on
  the teleportation layout's modes, the spread of the separately compiled meshes, and whether route-dependent error
  appears beside the overlap (the closure).
- *Why a simulation cannot answer it.* The overlap of the chip's demultiplexed photons on these modes, and the
  compiled meshes' error, are properties of the device; the reported HOM figure is a source calibration value, and
  the local model only maps an assumed overlap to the statistic.
- *Backend and budget.* `qpu:belenos`, two jobs submitted one after the other, eight iterations each, 2048 samples
  and 262,144 `max_shots` per iteration (the Ascella case's budget), `min_detected_photons` 2, credit ceiling
  1.262144 per job (1 + 262,144 x 1e-06), 2.52 credits for both. The live plan of 2026-10-31 estimated 1,187,640
  shots per job, about 148,000 per iteration, 1.77 times under the cap. `plan` prints the warning for HOM at or below
  90 %. Expected seconds 120 per job: the retained Belenos runs bound three-photon acquisition, fixed cost included, at
  12.8 microseconds per detection event; with detection events per pulse proportional to the photon count (an
  assumption), eight iterations at 262,144 events take at most 8 x (6.9 + 5.0) = 95 s.
- *Procedure.* Copy `cases.json` and `circuit.json` of the job into a fresh run directory under
  `results/quandela/runs/`, then run `scripts/qd_platform.py plan` with `--platform qpu:belenos --max-credits 1.262144
  --expected-seconds 120 --per-job-credits 1.0 --admit-status running`,
  `scripts/belenos_associator_visibility.py --check-live JOB`, `submit` with the same arguments, `collect`, and
  `scripts/belenos_associator_visibility.py --analyze RUN`.
- *Stopping rule.* A terminal error with no counted iteration allows one resubmission of the identical request under
  the same approval from a fresh run directory; a job that returned counts is not resubmitted.

## Outcome

Both jobs ran on 2026-10-31 at HOM 88.6 %, g2 1.4 %, transmittance 4.89 % and returned all eight iterations (claim
`qd-belenos-visibility-per-seed-mesh-spread` in [research_state.json](../state/research_state.json)).

| Job | Pair | Control D per seed (arms 0 to 3) | Spread chi-square (3 dof) | V_eff | se with spread | Closure C |
|---|---|---|---|---|---|---|
| 6de00147 | 18, 20 | -0.646, -0.873, -0.853, -0.672 | 241 | 0.827 | 0.047 | 0.238 |
| 04f3d55a | 20, 22 | -0.817, -0.638, -0.528, -0.424 | 382 | 0.696 | 0.084 | 0.165 |

The four control iterations of a job run one circuit, so their spread is the spread of the four compiled meshes the
service returned. It inflates the visibility's standard error about tenfold, the preregistered overlap reading is
unresolved on both pairs, and the closure fails through the control block. The case measured the mesh term rather than
the overlap. As an exploratory reading chosen after the data, the largest |D| of each pair's eight meshes (0.902 and
0.817) inverts to V 0.93 and 0.87 if mesh error and multiphoton emission only lower |D|. A follow-up that measures
overlap on this chip either repeats one seed many times and selects the mesh with the largest contrast in a first
job, or models the mesh as a random effect with enough seeds to estimate its distribution. The mode-swap case (claim
`qd-belenos-mode-swap-per-seed-mesh-variance`) confirmed that a seed reproduces its mesh across jobs and that per-seed
mesh error dominates this chip's error budget, so the selection route is sound.
