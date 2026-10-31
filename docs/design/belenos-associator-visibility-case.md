# Belenos in-situ two-photon visibility

`scripts/belenos_associator_visibility.py` builds two `qpu:belenos` jobs that measure the photon overlap V of two source
pairs in the compiled circuit. It reuses the closure design of the Ascella two-photon associator case
([ascella-two-photon-associator-case.md](ascella-two-photon-associator-case.md)), whose job of 2026-10-29 read an
in-situ visibility of 0.892 against the platform's HOM 0.890 and closed its visibility test.

## Question

Teleportation job-01 on `qpu:belenos` measured an accepted-event correctness of 0.802 over 1262 events, while the
noise model of `scripts/qd_teleportation_rehearsal.py` at the reported HOM 0.871 forecast 0.841. Sweeping the model's
source indistinguishability at job-01's anchor transmissions reproduces 0.802 near 0.81 (0.8446 at 0.871, 0.8138 at
0.83, 0.7860 at 0.79, 0.7600 at 0.75). The shortfall therefore has two candidate homes: photon overlap below the
reported figure, or error the model omits (compiled-mesh error, detector imbalance). This case measures the overlap
of the photon pairs the teleportation circuit interferes, on the chip modes it uses.

## Design

Each job runs the eight template iterations of the Ascella case on one four-mode window of the 24-mode chip: the
octonion associator block (a = (e6 + e7)/sqrt2, b = (e5 + e7)/sqrt2) and the quaternion control block (a = (e1 +
e2)/sqrt2, b = (e1 + e3)/sqrt2), each route in the order LaLb, Lab, Lab, LaLb. The two photons enter the window's
logical modes 0 and 2. Under the two-photon mixture model both control routes read D = -f(V), f(V) = V / (V + 1.5
(1 - V)); the in-situ visibility is V_eff = 1.5 f / (1 + 0.5 f) with f = -mean D_control. The associator block reads
Delta = 2 f(V), so the closure C = Delta + 2 mean D_control vanishes at every V, and a departure is route- or
mesh-dependent error rather than photon overlap.

| Job | Window (chip modes) | Photon modes | Teleportation role (layout of job-02 and job-03) |
|---|---|---|---|
| job-00 | 18 to 21 | 18, 20 | input q0 and Bell photon a0, the pair the analyzer interferes |
| job-01 | 20 to 23 | 20, 22 | a0 and b0, the pair the postselected CNOT entangles |

Both photon modes of each window are connected source inputs, and every window mode reads at most 12.5 dark counts
per second in the read of 2026-10-31 03:39:51 UTC, under the 100 per second `DARK_LIMIT` of the teleportation case.

**Compilation seeds.** job-00 takes indices 0 to 7 and job-01 indices 8 to 15 of the ANU QRNG draw
[`draw-2026-10-31T040009Z.json`](../evidence/anu_qrng/draw-2026-10-31T040009Z.json), each in index order, registered
in [`allocations.json`](../evidence/qrng_seeds/allocations.json).

**Analysis (`--analyze RUN`).** A result iteration binds to its setting by `compilation_seed`. An event is accepted
when exactly two modes click, both inside the window; three or more clicks, two clicks with one outside the window
and fewer than two clicks are counted by cause. The record carries Delta and D_control per route with binomial
standard errors, V_eff with its delta-method standard error, and the Ascella case's decisions: associator realized
(Delta above 5 standard errors with |Delta_control| within max(0.05, 3 se)), visibility closure (|C| within max(0.05,
3 se)) and the descriptive comparison with the HOM figure read at submission.

## Forecast

`--simulate OUT JOB --hom H --g2 G [--per-mode]` writes the local noise simulation (Perceval `NoiseModel`, threshold
clicks, 2048 two-click samples per iteration) beside a staged request. At g2 0.014:

| Source indistinguishability | Detection | V_eff job-00 | V_eff job-01 | se |
|---|---|---|---|---|
| 1.0 (g2 0) | ideal | 1.0000 | 1.0000 | 0 |
| 0.879 | ideal | 0.8725 | 0.8725 | 0.0043 |
| 0.879 | read's per-mode transmission | 0.8565 | 0.8577 | 0.0046 |
| 0.81 | read's per-mode transmission | 0.7887 | 0.7922 | 0.0057 |

The per-mode transmission of the read lowers V_eff by about 0.016, and the closure stays within 0.009 of zero under
it. The reported-figure hypothesis (0.879) and the job-01 hypothesis (0.81) differ by about 0.067 in V_eff, near 13
standard errors of one job. The comparison with the teleportation shortfall is descriptive: the teleportation
analyzer interferes three-photon terms, and the mixture model of this case is a two-photon model.

## Written case

- *What it measures.* The in-situ two-photon overlap of the source pairs (18, 20) and (20, 22) in compiled circuits on
  the teleportation layout's modes, and whether a route- or mesh-dependent error appears beside it (the closure).
- *Why a simulation cannot answer it.* The overlap of the chip's demultiplexed photons on these modes, and the
  compiled meshes' error, are properties of the device; the reported HOM figure is a source calibration value, and
  the local model only maps an assumed overlap to the statistic.
- *Backend and budget.* `qpu:belenos`, two jobs submitted one after the other, eight iterations each, 2048 samples
  and 262,144 `max_shots` per iteration (the Ascella case's budget), `min_detected_photons` 2, credit ceiling
  1.262144 per job (1 + 262,144 x 1e-06), 2.52 credits for both. Expected seconds 120 per job: the retained Belenos
  runs bound the fixed cost of an iteration at 6.9 s and three-photon acquisition at 12.8 microseconds per detection
  event; with detection events per pulse proportional to the photon count (an assumption), a two-photon event takes
  at most 19.2 microseconds, so eight iterations at 262,144 events take at most 8 x (6.9 + 5.0) = 95 s.
- *Procedure.* Copy `cases.json` and `circuit.json` of the job into a fresh run directory under
  `results/quandela/runs/`, then run `scripts/qd_platform.py plan` and `submit` with `--platform qpu:belenos
  --max-credits 1.262144 --expected-seconds 120 --per-job-credits 1.0 --admit-status running`, `collect`, and
  `scripts/belenos_associator_visibility.py --analyze RUN`.
- *Stopping rule.* A terminal error with no counted iteration allows one resubmission of the identical request under
  the same approval from a fresh run directory; a job that returned counts is not resubmitted.
