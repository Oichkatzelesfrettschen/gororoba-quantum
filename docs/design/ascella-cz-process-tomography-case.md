# Ascella postselected CZ process tomography case

This is the written case for two qpu:ascella jobs of 72 template iterations each. The jobs measure the process
fidelity of the postselected Ralph CZ gate as the service compiles it, by quantum process tomography on two dual-rail
qubits carried by two photons. [scripts/ascella_cz_tomography_case.py](../../scripts/ascella_cz_tomography_case.py)
builds the frozen requests in
[results/quandela/cases/ascella_cz_tomography](../../results/quandela/cases/ascella_cz_tomography/job-00/cases.json),
checks them, forecasts the outcome under Perceval's noise model and analyzes the collected runs. Nothing has been
sent, and each job waits for the owner's approval of this case.

## The gate

- Perceval's catalog entry `postprocessed cz` is a 6-mode unitary: control rails (0, 1), target rails (2, 3), vacuum
  ancilla modes (4, 5). The script requires its heralds to be {4: 0, 5: 0}.
- The same unitary is H CNOT H, with H a balanced beam splitter on the target rails and CNOT the unitary of
  `cnot_unitary()` in [qd_teleportation_rehearsal.py](../../scripts/qd_teleportation_rehearsal.py). `--check` requires
  the two to agree to 1e-9.
- The permanent of the 2 x 2 submatrix of each input and output pair gives the amplitude of the subspace with one
  photon on each rail pair. `--check` requires that 4 x 4 block to equal diag(1, 1, 1, -1) / 3, so the gate succeeds
  with probability 1/9 for every input in the dual-rail subspace and applies CZ exactly there.
- The qubit |0> is the photon on the first rail of its pair and |1> the photon on the second.

## Instrument

- **Window.** The six logical modes occupy chip modes 0..5. The photons enter chip modes 0 and 2, both connected
  source modes of qpu:ascella. The platform record states `support_multi_photon` false, so each input mode holds at
  most one photon.
- **Why that window.** Among the windows whose first and third modes are connected source modes (starting at 0, 2, 4
  or 6), the window at 0 has the lowest summed dark rate in the retained read (1273 detections per second against
  1381, 5869 and 9638). `--check` requires the retained read to select it.
- **Eligibility.** A sample counts when exactly two threshold clicks occur across all twelve returned modes, one on a
  control rail (modes 0, 1) and one on a target rail (modes 2, 3). The click pair names the readout outcome: control
  rail then target rail, 00, 01, 10 or 11. Every other sample is tallied as excluded by cause (three or more clicks,
  fewer than two, two clicks off the rails).

## Tomography settings

- **Inputs.** The Pauli eigenstates |0>, |1>, |+>, |+i> on each qubit, 16 inputs. The photons enter rail 0 of each
  pair and a preparation unitary on the pair rotates them into the state.
- **Readouts.** The 9 product Pauli bases XX, XY, ..., ZZ. A rotation on each rail pair ahead of the clicks maps the
  basis onto the rails.
- **Setting count.** 16 inputs x 9 readouts = 144. The product Pauli design needs all 9 readouts per input, because
  each of the 9 two-body correlators (such as the XY correlator) appears in exactly one basis pair; a smaller set would
  need non-product readouts. Each setting gives 3 independent frequencies, 432 in total against the 240 free
  parameters of a trace-preserving two-qubit process. `--check` requires the 144 x 4 design matrix to have rank 256,
  the free parameters of the Choi matrix before the trace constraint.
- **Folding.** Each setting is one 6 x 6 unitary, the readout rotations after the CZ after the input preparations.
  `--check` requires its coincidence block to equal (R x R)(CZ / 3)(P x P) and its law to equal the ideal one for all
  144, and compares one setting per readout pair with Perceval's SLOS backend.
- **One mesh.** `photonic_template` decomposes every setting into the same nearest-neighbor Rx/phase mesh on chip
  modes 0..5, so all 144 iterations share one circuit and differ in `circuit_params` and `compilation_seed`.

## Compilation seeds and the compiled object

The service re-transpiles every circuit ([strategy.md](../notes/quandela/strategy.md), "The server re-transpiles every
circuit"), so each setting is compiled into its own mesh under its own `compilation_seed`. The measured object is the
service-compiled average gate: the mean of the process over 144 meshes, not one fixed physical gate.
- Preparation, readout and gate errors do not separate, because each compiled mesh carries all three.
- The vendor figure for the CNOT, 93.8 +- 0.6 % ([literature.md](../notes/quandela/literature.md), vendor Ascella
  paper), is a comparison point for a different gate on a calibrated chip. It is no prediction for this case.

Every compilation seed and the bootstrap seed come from one ANU QRNG draw,
[draw-2026-10-31T034409Z.json](../evidence/anu_qrng/draw-2026-10-31T034409Z.json) (200 uint16 values). The rule is
nonzero values in index order with repeats skipped; no value was skipped. The 144 compilation seeds take indices 0 to
143 in schedule order, each used once, and the bootstrap seed of the device analysis takes index 144. The forecast
takes indices 145 to 148 (one per variant) and 149 to 188 (one per coverage dataset); each value seeds a
`SeedSequence` whose two children drive the synthetic dataset and its bootstrap, and indices 189 to 199 stay unused.
Each `cases.json` lists its compilation indices under `compilation_seeds`, so the case owns the whole draw in the
seed ledger of `ci/seed_provenance.py`.

## Jobs and order

A setting belongs to job-00 when the indices of its two input labels (0, 1, +, i) have an even sum, and to job-01
otherwise. Each job holds all four states on each qubit and the full nine readouts of eight inputs. Inside a job the
order is input-major, so a `max_duration` truncation drops whole trailing inputs and keeps complete state
tomographies of the earlier ones. 144 iterations at about 3 s each exceed the 300 s `max_duration`, so the case needs
two jobs.

## Estimator

1. Each setting's four eligible counts normalize to frequencies, a trace-preserving conditional process.
2. A linear least-squares inversion maps the 144 x 4 frequencies to the 16 x 16 Choi matrix J = sum_ij |i><j| x
   Lambda(|i><j|), trace 4.
3. Dykstra alternating projections onto the positive cone and the trace-preserving hyperplane give the nearest
   completely positive trace-preserving map, renormalized on the input marginal so that the trace-preserving
   constraint holds exactly.
4. The process fidelity is F_pro = <Phi_CZ| J |Phi_CZ> / 16 and the average gate fidelity is (4 F_pro + 1) / 5.
5. The bootstrap resamples every setting's eligible events multinomially, 500 replicates drawn from one generator
   before the estimator maps over them, and reports the 95 % basic interval (2 F - q_high, 2 F - q_low, capped at 1) of the
   replicate quantiles q. The positivity projection biases the fidelity downward under noise, so the percentile
   interval sits below the estimand; the coverage study below measures that and fixes the interval type. The
   percentile interval, the linear-inversion fidelity before the projection, the bootstrap median, the eligible events
   per setting and the exclusions by cause are descriptive.

Perceval 1.3.1 provides `perceval.algorithm.ProcessTomography` and `ProcessTomographyMLE`. Both take a computer
object and run their own preparation and measurement settings; neither offers an entry point for counts from a
retained run (`dir()` of the classes lists none), so the case carries its own estimator.

Requirement: the noiseless frequencies of all 144 settings give F_pro = 1 to 1e-9 (`--check`, and
`tests/scripts/test_ascella_cz_tomography_case.py`). The test also recovers the analytic F = (1 - p) + p/16 of a
depolarized CZ.

## Forecast under noise

`--forecast` recomputes [forecast.json](../../results/quandela/cases/ascella_cz_tomography/forecast.json) from the
retained platform read (read of 2026-10-31 04:11 UTC: HOM 87.54 %, g2 1.9 %, transmittance 5.82 %, clock 13.33 MHz, per-mode dark rates). Each
setting's six-mode unitary runs through Perceval's SLOS processor with `NoiseModel(indistinguishability=HOM, g2=g2)`;
each photon is then detected with the transmittance as probability, a mode with n photons clicks with probability
1 - (1 - T)^n, and each mode adds one dark click first order. The pipeline at perfect indistinguishability, no g2, no
loss and no dark counts reproduces the exact law (`--check`).

Per variant, the expected eligible counts at 6000 samples per iteration give the estimator's value (the estimand). One
synthetic dataset, sampled multinomially from those counts under its own draw value, then runs the analysis as a
device run would, so the interval comes from noisy counts:

| Variant | Estimand F_pro | Estimand F_avg | Sampled F_pro | 95 % basic interval | Sampled F_avg | 95 % basic interval |
|---|---|---|---|---|---|---|
| source only (HOM, g2) | 0.812 | 0.850 | 0.808 | 0.804 to 0.826 | 0.846 | 0.843 to 0.861 |
| source and loss | 0.786 | 0.829 | 0.771 | 0.764 to 0.789 | 0.816 | 0.811 to 0.831 |
| source, loss and dark counts | 0.783 | 0.826 | 0.778 | 0.773 to 0.796 | 0.822 | 0.819 to 0.837 |
| g2-corrected overlap, loss and dark counts | 0.821 | 0.857 | 0.805 | 0.800 to 0.823 | 0.844 | 0.840 to 0.859 |

The forecast of record is the source, loss and dark counts variant: 0.783 process fidelity and 0.826 average gate
fidelity at the live figures.
- The source dominates: the HOM visibility of 87.54 % alone takes the gate to 0.812. The two-photon interference in the
  beam splitters of the gate is as sensitive to distinguishability as the HOM test.
- The g2-corrected variant replaces the HOM read with the first-order overlap (V + g2) / (1 - g2) = 0.912 (Ollivier et
  al., PRL 126, 063602 (2021), the relation [ascella-two-photon-associator-case.md](ascella-two-photon-associator-case.md)
  cites, not retained here). It brackets the forecast from above.
- The forecast models the designed unitary on six modes. It leaves out mesh phase error, light the compiled mesh sends
  outside the window, and mode-dependent detector efficiency. A measured fidelity below the forecast measures those.

**Coverage study (decides the interval type).** The study draws 40 synthetic datasets from the expected counts of the
source, loss and dark counts variant, runs 200 bootstrap replicates on each, and counts how often each interval
covers the estimand 0.7826:

| Interval | Coverage of 40 datasets (nominal 0.95) |
|---|---|
| basic | 0.925 |
| percentile | 0.35 |

The mean point estimate lies 0.0080 below the estimand, which is the positivity projection's bias; the percentile
interval inherits it twice. The analysis therefore reports the basic interval, preregistered in `cases.json`, and the
point estimate carries the bias in its record (`mean_point_bias`).

## Written acquisition case

**What it measures.** The process fidelity to the ideal CZ and the average gate fidelity of the postselected Ralph CZ
as qpu:ascella compiles it, over 144 settings, with a bootstrap interval, and how far it falls below the source-limited
forecast.

**Why simulation cannot answer it.** Local SLOS and Perceval's noise model return the law of the designed unitary at
modeled source figures. The question is the device:
- what the 144 service-compiled meshes realize, including phase error and light outside the window;
- whether the HOM figure of Quandela's own test predicts the interference inside a compiled six-mode gate;
- how much of the vendor's 93.8 % CNOT figure this compiled-per-setting route retains.

**Platform.** qpu:ascella: 12 modes, at most 6 photons, connected source modes 0, 2, 4, 6, 8 and 10, threshold
detectors, `max_duration` 300 s, 1e-6 credits per shot with 1 credit per job. The plan below re-reads all of this.

**Jobs and iterations.** Two jobs of 72 template iterations, job-00 then job-01 in sequence (the token admits one
running and one queued job, and `plan` refuses when either exists).

**Shots.** Each iteration takes 6000 samples. The caps follow the largest Perceval `estimate_required_shots` of the
job's settings, times 1.25, rounded up to 100000 ([shot-estimate.json](../../results/quandela/cases/ascella_cz_tomography/shot-estimate.json)):

| Job | `max_samples` | `max_shots` per iteration | Largest estimate | Mean estimate | Plan's summed estimate |
|---|---|---|---|---|---|
| job-00 | 432000 | 500000 | 360334 | 258215 | 18591510 |
| job-01 | 432000 | 2300000 | 1801670 | 302066 | 21748730 |

The estimate varies by input because the photons of input |1>|0> enter rails 1 and 2, which meet on a 2/3
beam splitter that sends them to separate modes with probability 1/9; threshold detectors read the bunched rest as one
click, so job-01's setting in-10-ZZ needs about six times the mean estimate. The yield formula Clock x T^2 x 1/9 gives
T^2/9 = 3.8e-4 eligible events per shot, 5.0e3 per second of attempts; Perceval's estimates are higher, and the two-photon associator run used 74 shots per sample against the
69 its estimate predicted ([ascella_associator_case.py](../../scripts/ascella_associator_case.py)), so the plan's
estimate is the authoritative figure. The forecast expects about 148700 eligible events in all, 1030 per setting on
average.

**Credits.** A job bills its largest iteration's `max_shots` ([billing runbook](../runbooks/quandela-credit-optimization.md)).
- job-00: 1 + 500000 x 1e-6 = 1.5 credits, expected and ceiling.
- job-01: 1 + 2300000 x 1e-6 = 3.3 credits, expected and ceiling.
- Total: 4.8 credits against the 200-credit monthly free grant, under the 6-credit target.
`plan` printed credit ceilings 1.5 and 3.3 for the retained requests.

**Seconds.** Compilation dominates. Retained qpu:ascella template jobs ran 84 iterations in 248 s, 96 in 288 s, and 8
two-photon iterations in 25 s: about 3 s per iteration whatever the sample count between 2048 and 32768. 72 iterations
need about 216 s plus acquisition: the plan expects 18.6 and 21.7 million shots for the two jobs, and even the caps
total (36 and 165.6 million shots) take under 13 s at 13.33 MHz. The bound passed to `plan` is
240 s against the 300 s `max_duration`.

**HOM rule: an owner decision.** Strategy design rule 1 ([strategy.md](../notes/quandela/strategy.md)) holds
two-photon cases until the live HOM exceeds 90 %. The live read is 87.54 %, and `plan` prints that warning for both
jobs. The owner's waiver for the associator case covered that case only. The gate's fidelity depends on the
indistinguishability directly (forecast above), so the owner chooses between running at 87.54 % to measure the gate as
the device stands and waiting for a recovered HOM.

**Stopping rule.**
- A terminal error with no counted iteration allows one resubmission of the identical body under the same approval,
  from a fresh run directory, after `plan` passes again. A second error stops the case.
- A job that returned counts is never resubmitted under this approval.
- A job truncated by `max_duration` leaves the pooled estimate undecided and its complete inputs descriptive. Running
  the missing settings is a new written case.
- The service-compiled mesh of each iteration enters `results.json` as `computed_circuit`. The analysis does not read
  it.

**Procedure after approval.**

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="$HOME/.config/quandela/cloud-token"
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)
for JOB in job-00 job-01; do
  RUN=results/quandela/runs/$STAMP-qpu_ascella-ascella_cz_tomography-$JOB
  mkdir -p "$RUN"
  cp results/quandela/cases/ascella_cz_tomography/$JOB/cases.json \
     results/quandela/cases/ascella_cz_tomography/$JOB/circuit.json "$RUN"/
  case $JOB in job-00) CREDITS=1.5 ;; job-01) CREDITS=3.3 ;; esac
  CASE="--platform qpu:ascella --max-credits $CREDITS --expected-seconds 240 --per-job-credits 1.0"
  "$PYTHON" scripts/qd_platform.py plan "$RUN" $CASE
  "$PYTHON" scripts/qd_platform.py submit "$RUN" $CASE --approval "APPROVAL TEXT"
  "$PYTHON" scripts/qd_platform.py collect "$RUN" --timeout 3600
done
"$PYTHON" scripts/ascella_cz_tomography_case.py --analyze results/quandela/ascella-cz-tomography-analysis.json \
  results/quandela/runs/$STAMP-qpu_ascella-ascella_cz_tomography-job-00 \
  results/quandela/runs/$STAMP-qpu_ascella-ascella_cz_tomography-job-01
```

Before each submit the plan must show qpu:ascella available with 0 running and 0 queued jobs, an unchanged price per
shot, the connected source modes 0 and 2, and Perceval's estimate within the job's caps. The submitting host needs the
Quandela token file and network access to `api.cloud.quandela.com`.

**Analysis.** `--analyze` pools both runs and writes the process fidelity and average gate fidelity with their 95 %
bootstrap intervals, the linear-inversion fidelity, the forecast values, the eligible events per setting and the
exclusions by cause. A pooled estimate needs all 144 settings with eligible events; otherwise the process reads
`undecided`. After collection the retained runs enter `docs/state/research_state.json` and the strategy run log in
the change that retains them.

## Read-only checks behind this case

| Check | Result |
|---|---|
| `ascella_cz_tomography_case.py --check` | passes: CZ block, 144 folded settings, SLOS agreement, noiseless limit, ideal fidelity 1, both jobs bound |
| `ascella_cz_tomography_case.py --forecast` | recomputes forecast.json byte for byte |
| `qd_platform.py plan` on job-00 and job-01 | passes: ceilings 1.5 and 3.3, HOM warning at 87.54 %; retained as `plan-read.json` in each job directory |
| `ci/seed_provenance.py --check`, `anu_qrng.py check` | pass: the manifests own the draw, no literal seed |
