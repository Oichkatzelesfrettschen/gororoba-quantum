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
service-compiled average gate: the mean of the process over 144 meshes, not one fixed physical gate. Preparation,
readout and gate errors do not separate, because each compiled mesh carries all three.

Every compilation seed and the bootstrap seed come from one ANU QRNG draw,
[draw-2026-10-31T034409Z.json](../evidence/anu_qrng/draw-2026-10-31T034409Z.json) (200 uint16 values). The rule is
nonzero values in index order with repeats skipped; no value was skipped.
- The 144 compilation seeds take indices 0 to 143 in schedule order, each used once.
- The bootstrap seed of the device analysis takes index 144.
- The five forecast variants take indices 145 to 149; each value seeds a `SeedSequence` whose two children drive the
  synthetic dataset and its bootstrap.
- Indices 150 to 199 are owned and unused.

The 200 coverage datasets of the forecast take indices 0 to 199 of a second draw,
[draw-2026-10-31T044412Z.json](../evidence/anu_qrng/draw-2026-10-31T044412Z.json) (256 uint16 values, none skipped),
one value each, under the same two-child rule; indices 200 to 255 are owned and unused. Each `cases.json` lists its
compilation indices under `compilation_seeds`, and `forecast.json` names the second draw, so the case owns both draws
whole in the seed ledger of `ci/seed_provenance.py`.

## Jobs and order

A setting belongs to job-00 when the indices of its two input labels (0, 1, +, i) have an even sum, and to job-01
otherwise. Each job holds all four states on each qubit and the full nine readouts of eight inputs. Inside a job the
order is input-major, so a `max_duration` truncation drops whole trailing inputs and keeps complete state
tomographies of the earlier ones. 144 iterations at about 3 s each exceed the 300 s `max_duration`, so the case needs
two jobs.

## Estimator

A shot of the service is a detection event of at least one photon ([billing runbook](../runbooks/quandela-credit-optimization.md),
vocabulary), and an iteration stops at its `max_samples` of two or more clicks. With uniform detection loss T, the
chance of at least one click per attempt is 1 - (1 - T)^2 whatever the two photons do inside the gate, so it is the
same for all 144 settings (the model gives 0.1147 for every setting at the live read). Eligible events divided by the
iteration's `nb_shots_used` is therefore an absolute rate, proportional to the probability that the postselected gate
succeeds with that outcome.

1. **Rates.** Each iteration gives four absolute rates, its eligible events per outcome over `nb_shots_used`.
2. **Linear inversion.** A least-squares inversion (unweighted) maps the 144 x 4 rates to the 16 x 16 Choi matrix
   J = sum_ij |i><j| x Lambda(|i><j|). The postselected gate succeeds with an input-dependent probability, so J is
   trace non-increasing and keeps its trace, the mean eligible rate.
3. **Fidelity.** F_pro = <Phi_CZ| J |Phi_CZ> / (4 Tr J) and F_avg = (4 F_pro + 1) / 5. Both the numerator and the trace
   are linear in the rates, so F_pro is a ratio of two linear functionals and carries no projection bias.
4. **Interval.** The bootstrap resamples every iteration parametrically: its samples multinomially over the four
   eligible outcomes and the rest, and its shots as the samples plus a negative binomial count of failures at the
   observed sample share. It draws 500 replicates from one generator before the estimator maps over them and reports
   the 95 % percentile interval. The coverage study below fixes the type.

**Why not the conditional map.** An earlier reconstruction normalized each setting to its eligible events. Once the
success probability depends on the input, the conditional map rho -> E(rho) / Tr E(rho) is not linear, so the linear
inversion has no consistent solution and the projection onto a completely positive trace-preserving map repairs a
modeling error, not finite-sample noise. Under the case's own model at the live read the conditional reconstruction
has a least Choi eigenvalue of -0.13 (-0.128 and -0.134 in the two variants checked) with no sampling noise, and its limit sits 0.004 to 0.010 below the
postselected map's fidelity. The case keeps it as a descriptive companion (`conditional_process_fidelity`).

**Why not a positive projection.** The nearest positive matrix of the same trace removes unphysical directions but
moves the Choi matrix toward the trace-normalized simplex: in the forecast it lowers the sampled fidelity by 0.02 to
0.03 (indistinguishability only: 0.807 against 0.833 unprojected), and a projection that renormalizes its own trace
lowers it by 0.12. The unprojected fidelity has a mean bias of 0.0004 over the 200 coverage datasets. The projected
fidelity and the least eigenvalue of J over its trace (about -0.004 at the exact rates of the record variant) are
descriptive.

**Pooling the two jobs.** The parity split makes any drift between the jobs look like input-dependent error, so the
pool is preregistered in `cases.json`:
- Job-01's rates are multiplied by g(T_job-00) / g(T_job-01) with g(T) = T / (2 - T), the ratio of the eligible rate
  (proportional to T^2) to the shot rate (proportional to 1 - (1 - T)^2) under uniform loss. T comes from each run's
  `perfs_at_plan`.
- The pool is decided only when the two plans' HOM differ by at most 1.0 percentage point, their transmittance by at
  most 0.3 percentage points, and the two submissions lie at most 12 hours apart. Otherwise the pooled estimate is
  reported as descriptive.
- A missing setting, or a pair of runs that is not both jobs, leaves the estimate undecided.

**Binding.** `--analyze` binds each returned iteration to the setting that has its echoed `compilation_seed`, one to
one. It requires each run's `cases.json` to equal the retained case byte for byte and the two runs to be distinct
jobs. An entry that is missing, malformed or an error (the kinds `qd_platform.result_summary` writes for a cut-short
job) is counted and skipped without raising.

Perceval 1.3.1 provides `perceval.algorithm.ProcessTomography` and `ProcessTomographyMLE`. Both take a computer
object and run their own preparation and measurement settings; neither offers an entry point for counts from a
retained run (`dir()` of the classes lists none), so the case carries its own estimator.

Requirements (`--check` and `tests/scripts/test_ascella_cz_tomography_case.py`): the noiseless rates of all 144
settings give F_pro = 1 to 1e-9; a depolarized CZ gives the analytic F = (1 - p) + p/16; and a postselected map
M rho M^dagger with M = CZ diag(1, 0.8, 0.6, 0.5), whose success probability depends on the input, gives its exact
F = |Tr(CZ^dagger M)|^2 / (4 Tr M^dagger M) under the primary estimator, where the conditional estimator misses it.

## Forecast under noise

`--forecast` recomputes [forecast.json](../../results/quandela/cases/ascella_cz_tomography/forecast.json) from the
retained platform read (2026-10-31 04:11 UTC: HOM 87.54 %, g2 1.9 %, transmittance 5.82 %, clock 13.33 MHz, per-mode
dark rates). Each setting's six-mode unitary runs through Perceval's SLOS processor with
`NoiseModel(indistinguishability=HOM, g2=g2)`; each photon is then detected with the transmittance as probability, a
mode with n photons clicks with probability 1 - (1 - T)^n, and each mode adds one dark click first order. The
pipeline at perfect indistinguishability, no g2, no loss and no dark counts reproduces the exact law (`--check`).

Per variant the table lists the primary estimator's value at the exact absolute rates (the estimand), the
conditional estimator's value beside it, and one synthetic dataset of 4000 samples per iteration sampled under its own
draw value and analyzed as a device run would be:

| Variant | Estimand F_pro | Conditional | Estimand F_avg | Sampled F_pro | 95 % interval | Sampled F_avg | 95 % interval |
|---|---|---|---|---|---|---|---|
| indistinguishability only (HOM) | 0.834 | 0.823 | 0.867 | 0.833 | 0.813 to 0.852 | 0.867 | 0.851 to 0.881 |
| source only (HOM, g2) | 0.823 | 0.812 | 0.858 | 0.821 | 0.802 to 0.841 | 0.857 | 0.841 to 0.872 |
| source and loss | 0.790 | 0.786 | 0.832 | 0.789 | 0.770 to 0.809 | 0.831 | 0.816 to 0.847 |
| source, loss and dark counts | 0.786 | 0.783 | 0.829 | 0.768 | 0.749 to 0.788 | 0.815 | 0.799 to 0.831 |
| g2-corrected overlap, loss and dark counts | 0.826 | 0.821 | 0.861 | 0.832 | 0.812 to 0.854 | 0.866 | 0.849 to 0.883 |

The forecast of record is the source, loss and dark counts variant: 0.786 process fidelity and 0.829 average gate
fidelity at the live figures, about 99000 eligible events in all (690 per setting on average).
- The HOM visibility of 87.54 % alone takes the gate to 0.834; g2 on top takes it to 0.823; loss and dark counts take
  it to 0.786. The two-photon interference in the beam splitters of the gate is as sensitive to distinguishability as
  the HOM test.
- The g2-corrected variant replaces the HOM read with the first-order overlap (V + g2) / (1 - g2) = 0.912 [U] (Ollivier
  et al., PRL 126, 063602 (2021); the relation
  [ascella-two-photon-associator-case.md](ascella-two-photon-associator-case.md) cites, not retained here). It brackets
  the forecast from above.
- The forecast models the designed unitary on six modes. It leaves out mesh phase error, light the compiled mesh sends
  outside the window, and mode-dependent detector efficiency. A measured fidelity below the forecast measures those.
- The vendor paper's CNOT figure, 93.8 +- 0.6 % ([literature.md](../notes/quandela/literature.md)), names no fidelity
  type there, so the case draws no numeric comparison to it.

**Coverage study.** The study draws 200 synthetic datasets from the rates of the source, loss and dark counts variant,
runs 200 bootstrap replicates on each, and counts how often each interval covers the physical fidelity 0.7862, the
primary estimator's value at the exact rates:

| Interval | Datasets covering | Coverage | Exact 95 % binomial interval |
|---|---|---|---|
| percentile | 187 of 200 | 0.935 | 0.891 to 0.965 |
| basic | 186 of 200 | 0.930 | 0.885 to 0.961 |

Both types cover alike, both exact binomial intervals contain the nominal 0.95, and both exceed the 0.90 floor
that `--check` requires of the reported type. The analysis reports the percentile
interval, preregistered in `cases.json`.

## Written acquisition case

**What it measures.** The process fidelity to the ideal CZ and the average gate fidelity of the postselected Ralph CZ
as qpu:ascella compiles it, over 144 settings, with a bootstrap interval, and how far it falls below the
source-limited forecast.

**Why simulation cannot answer it.** Local SLOS and Perceval's noise model return the law of the designed unitary at
modeled source figures. The question is the device:
- what the 144 service-compiled meshes realize, including phase error and light outside the window;
- whether the HOM figure of Quandela's own test predicts the interference inside a compiled six-mode gate.

**Platform.** qpu:ascella: 12 modes, at most 6 photons, connected source modes 0, 2, 4, 6, 8 and 10, threshold
detectors, `max_duration` 300 s, 1e-6 credits per shot with 1 credit per job. The plan below re-reads all of this.

**Jobs and iterations.** Two jobs of 72 template iterations, job-00 then job-01 in sequence (the token admits one
running and one queued job, and `plan` refuses when either exists).

**Shots.** Each iteration takes 4000 samples. The caps follow the largest Perceval `estimate_required_shots` of the
job's settings, times 1.25, rounded up to 100000
([shot-estimate.json](../../results/quandela/cases/ascella_cz_tomography/shot-estimate.json)). The caps keep the all-caps
time below `max_duration` (Seconds below).

| Job | `max_samples` | `max_shots` per iteration | Largest estimate | Mean estimate | Plan's summed estimate |
|---|---|---|---|---|---|
| job-00 | 288000 | 400000 | 240223 | 172144 | 12394362 |
| job-01 | 288000 | 1600000 | 1201113 | 201377 | 14499166 |

The estimate varies by input because the photons of input |1>|0> enter rails 1 and 2, which meet on a 2/3 beam
splitter that sends them to separate modes with probability 1/9; threshold detectors read the bunched rest as one
click, so job-01's setting in-10-ZZ needs about six times the mean estimate. The forecast expects about 99000
eligible events in all.

**Credits.** A job bills its largest iteration's `max_shots` ([billing runbook](../runbooks/quandela-credit-optimization.md)).
- job-00: 1 + 400000 x 1e-6 = 1.4 credits, expected and ceiling.
- job-01: 1 + 1600000 x 1e-6 = 2.6 credits, expected and ceiling.
- Total: 4.0 credits against the 200-credit monthly free grant.
`plan` printed credit ceilings 1.4 and 2.6 for the retained requests.

**Seconds.** Compilation dominates: retained qpu:ascella template jobs fit 2.95 to 3.0 s per iteration (80 iterations
in 243 s, 84 in 248 s, 96 in 288 s), so 72 iterations need about 216 s.
- A shot is a detection event of at least one photon, so the shot rate is the clock times the chance of one click:
  13.33 MHz x (1 - (1 - 0.0582)^2) = 13.33 MHz x 0.113 = 1.5 million shots per second.
- Expected: the plan's 12.4 and 14.5 million shots take 8 and 10 s, so the jobs take about 224 and 226 s against the
  240 s bound passed to `plan`.
- Worst case, every iteration at its cap: 28.8 million shots take 19 s (job-00 about 235 s) and 115.2 million take
  76 s (job-01 about 292 s), both below the 300 s `max_duration`. `--check` requires this bound; a cap above about 1.7 million
  shots per iteration would take job-01 past 300 s when every iteration reaches it.
- The model extrapolates acquisition: the largest retained job spent 3.15 million shots, and these jobs expect 4 to 5
  times that, with the worst case 37 times. A cap hit costs that setting samples, and the stopping rule treats a
  truncation as undecided.

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
- Job-01 is submitted only after job-00 collects a terminal status. A collect that times out is repeated once; a
  second timeout stops the case with job-01 unsent, and the owner decides what happens to the running job. The
  procedure below stops at a failed `collect` (`set -e`).
- The service-compiled mesh of each iteration enters `results.json` as `computed_circuit`. The analysis does not read
  it.

**Procedure after approval.**

```sh
set -eu
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="$HOME/.config/quandela/cloud-token"
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)
for JOB in job-00 job-01; do
  RUN=results/quandela/runs/$STAMP-qpu_ascella-ascella_cz_tomography-$JOB
  mkdir -p "$RUN"
  cp results/quandela/cases/ascella_cz_tomography/$JOB/cases.json \
     results/quandela/cases/ascella_cz_tomography/$JOB/circuit.json "$RUN"/
  case $JOB in job-00) CREDITS=1.4 ;; job-01) CREDITS=2.6 ;; esac
  CASE="--platform qpu:ascella --max-credits $CREDITS --expected-seconds 240 --per-job-credits 1.0"
  "$PYTHON" scripts/qd_platform.py plan "$RUN" $CASE
  "$PYTHON" scripts/qd_platform.py submit "$RUN" $CASE --approval "APPROVAL TEXT"
  "$PYTHON" scripts/qd_platform.py collect "$RUN" --timeout 3600 ||
    "$PYTHON" scripts/qd_platform.py collect "$RUN" --timeout 3600
done
"$PYTHON" scripts/ascella_cz_tomography_case.py --analyze results/quandela/ascella-cz-tomography-analysis.json \
  results/quandela/runs/$STAMP-qpu_ascella-ascella_cz_tomography-job-00 \
  results/quandela/runs/$STAMP-qpu_ascella-ascella_cz_tomography-job-01
```

Before each submit the plan must show qpu:ascella available with 0 running and 0 queued jobs, an unchanged price per
shot, the connected source modes 0 and 2, and Perceval's estimate within the job's caps. The submitting host needs the
Quandela token file and network access to `api.cloud.quandela.com`.

**Analysis.** `--analyze` pools both runs under the rules of the estimator section and writes the process fidelity and
average gate fidelity with their 95 % intervals, the pooling status, the descriptive projected and conditional
fidelities, the forecast values, the eligible events per setting, the exclusions by cause and the uncounted iterations
by kind. A pooled estimate needs all 144 settings with eligible events; otherwise the process reads `undecided`. After
collection the retained runs enter `docs/state/research_state.json` and the strategy run log in the change that
retains them.

## Read-only checks behind this case

| Check | Result |
|---|---|
| `ascella_cz_tomography_case.py --check` | passes: CZ block, 144 folded settings, SLOS agreement, noiseless limit, ideal fidelity 1, both jobs bound, modeled seconds inside the bounds |
| `ascella_cz_tomography_case.py --forecast` | recomputes forecast.json byte for byte |
| `qd_platform.py plan` on job-00 and job-01 | passes: ceilings 1.4 and 2.6, HOM warning at 87.54 %; retained as `plan-read.json` in each job directory |
| `ci/seed_provenance.py --check`, `anu_qrng.py check` | pass: the manifests and forecast own both draws, no literal seed |

## Outcome

Both jobs ran on 2026-10-31 at HOM 87.56 %, g2 1.8 %, transmittance 5.81 % (jobs fee9dd00 and 518f8687, 4.7 minutes
apart, claim `qd-ascella-postselected-cz-process-fidelity` in [research_state.json](../state/research_state.json)).
The owner admitted the status `running` after two submissions lost a race between `plan` and `submit`, so both jobs
queued behind other users' jobs; nothing else in the case changed. Every setting returned counts, and the pool is
decided.

| Quantity | Estimate | 95 % percentile interval |
|---|---|---|
| Process fidelity (primary, unprojected) | 0.849 | 0.828 to 0.869 |
| Average gate fidelity | 0.879 | 0.863 to 0.895 |
| Projected process fidelity (descriptive) | 0.811 | |
| Conditional process fidelity (descriptive) | 0.819 | |

The primary estimate lies above every forecast variant, including indistinguishability alone (0.834) and the full
source, loss and dark-count model (0.786). Under the Perceval model that places the in-situ photon overlap above the
reported HOM, as the Ascella associator case's in-situ visibility (0.892 at HOM 0.890) and the Belenos suppression
case's HOM lower bound (0.910 at HOM 0.886) also indicate.
