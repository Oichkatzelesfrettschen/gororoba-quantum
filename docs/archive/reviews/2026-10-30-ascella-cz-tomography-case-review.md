# Adversarial review: Ascella postselected CZ process tomography case

Target: branch `quandela/ascella-cz-tomography-case`, commits 1af7e8566, 9c53ea96e, 4b1e2c5cd on 5cb08d53f.
Read in full: `scripts/ascella_cz_tomography_case.py`, `docs/design/ascella-cz-process-tomography-case.md`, the
plan reads, `shot-estimate.json`, the `forecast.json` summary, and the draw record. Sampled: `cases.json` through
`--check`, plus `qd_platform.template_experiment` lines 787-830 and the collect path at lines 1944-2011.
Nothing was sent, and no file outside `docs/local/` changed.

Fields: statistical estimation (quantum process tomography, bootstrap), linear-optics physics (postselected
two-photon gates, partial distinguishability), and provider operations (Quandela billing, timing, seeds).

## Deterministic checks (run in the worktree)

| Check | Result |
|---|---|
| `ascella_cz_tomography_case.py --check` | rc 0: both jobs bind, credit ceilings 1.5 and 3.3, ideal F 1.000000000000 |
| `ascella_cz_tomography_case.py --forecast` | rc 0: forecast.json recomputes byte for byte (28 s) |
| `pytest tests/scripts/test_ascella_cz_tomography_case.py` | 11 passed |
| `ci/pinned_tool.py` ruff check, ruff format --check, mypy | clean |
| `scripts/hypercomplex_libraries.py --out docs/state/hypercomplex-libraries --check` | rc 0, "validated 359 distributions" |
| `ci/seed_provenance.py --check` | rc 0, 309 literals accounted |
| `scripts/check_markdown_links.py` | rc 0 |

## Findings, worst first

### 1. SERIOUS (blocks submit): the preregistered estimand is not the process fidelity of the postselected gate

**Barb.** The design calls per-setting normalization "a trace-preserving conditional process". Once the success
probability depends on the input, the conditional map rho -> E(rho)/Tr E(rho) is not linear. Linear inversion then
has no consistent solution, and the CPTP projection repairs a modeling error rather than sampling noise.

**Grounding.** The probe (scratch, `probe_norm.py`) uses the case's own `forecast_setting` and compares two
reconstructions. One is the case estimator on conditional frequencies. The other is linear inversion on absolute
eligible probabilities with the fidelity normalized by the trace, F = <Phi|J|Phi> / (4 Tr J).

| Model | Success max/min over 16 inputs | Case LI min eig (no sampling noise) | Case CPTP F_pro | Physical postselected F_pro |
|---|---|---|---|---|
| HOM 0.8754 only, g2 0, lossless | 1.498 | -0.128 | 0.8234 | 0.8338 (J_abs PSD, min eig -2e-15) |
| source only | 1.560 | -0.141 | 0.8124 | 0.8229 |
| source, loss and dark counts (forecast of record) | 1.641 | -0.134 | 0.7826 | 0.7862 |

With distinguishability alone, the absolute-rate Choi matrix is positive semidefinite to machine precision, so the
true postselected process is a valid trace-non-increasing CP map. The conditional frequencies of that same process
give a Choi matrix with eigenvalues summing to -0.43 (trace 4) with no sampling noise at all.

The design text "The positivity projection biases the fidelity downward under noise" names the wrong mechanism. At
infinite data the projection already takes the record variant from 0.801 to 0.783 (`estimand_linear_inversion_fidelity`
against `estimand_process_fidelity` in forecast.json).

The bias against the physical fidelity is 0.004 in the forecast of record and 0.010 with distinguishability alone. The
basic interval's half-width is about 0.011 (forecast table). The bias therefore matters for coverage of the physical
quantity, and the coverage study covers only the estimator's own limit.

The device-versus-forecast comparison stays like for like, because both sides pass through the same estimator. The
headline "process fidelity to the ideal CZ" does not. `plan` binds `cases_sha256`, and the estimator text sits in
`cases.json` under `preregistered`, so the fix has to land before submit.

**Remedy.** With uniform loss, P(at least one click) = 1 - (1 - T)^2 wherever the two photons go, so it does not
depend on the setting. Each iteration's `result_fields.nb_shots_used` is retained, as the associator results show,
which makes eligible counts / `nb_shots_used` an absolute-rate denominator that is the same for every setting. Then:
- Preregister linear inversion (or a trace-non-increasing CP projection) on those rates, with F = <Phi|J|Phi> / (4 Tr J).
- Keep the conditional estimator as a descriptive companion.
- Or keep the conditional estimator and rename its target "estimator limit of the conditional reconstruction", stating
  the 0.004 to 0.010 offset.

The absolute-rate route is exposed to transmittance drift between job-00 and job-01, because eligible / shots scales
with T / 2. Normalize per job, or record `perfs_at_plan` T for both jobs and preregister a tolerance.

Confidence: high on the mechanism and on the HOM-only numbers. The device-side size depends on the compiled meshes.

### 2. SLOPPY: the time model conflates shots with clock pulses; the cap-scenario bound is off by about 9x

**Barb.** "even the caps total (36 and 165.6 million shots) take under 13 s at 13.33 MHz" divides shots by the pulse
clock. The runbook vocabulary defines a shot as "one detection event of at least one photon"
(`docs/runbooks/quandela-credit-optimization.md`, Vocabulary).

**Grounding.**
- The shot rate is 13.33 MHz x P(at least one click), with P = 1 - (1 - 0.0582)^2 = 0.113, which gives about
  1.5 M shots/s.
- Expected usage of 21.7 M shots (job-01 plan) takes about 14 s. With 72 x 2.9 s of per-iteration overhead, job-01
  needs about 223 s, inside 240 s and 300 s.
- If job-01 ran every iteration to its cap (165.6 M shots), acquisition takes about 110 s and the job about 320 s,
  past `max_duration`. The doc says this case takes under 13 s.
- The 3 s per iteration is well supported. Retained qpu:ascella runs fit 2.9 s per iteration, and pairs at equal
  iteration counts show the shot cost is small: signed coherence at 0.52 and 1.05 Mshots both took 186 s; the
  associator at 1.21 Mshots and the predecessor at 0.26 Mshots both took 25 s.
- The largest retained job total is 3.15 Mshots and the largest retained iteration is 0.15 Mshots. job-01 expects
  21.7 Mshots, and its in-10-ZZ setting expects 1.8 Mshots, so the model is extrapolated 7x past the retained data.
- The "yield formula" paragraph repeats the conflation: "3.8e-4 eligible events per shot" is per pulse.

**Remedy.** Restate the acquisition time as shots / (clock x (1 - (1 - T)^2)). Give the expected value (about 15 s
per job) and the all-caps value (about 110 s, which would truncate), and note the 7x extrapolation. This does not
block: every iteration hitting its cap under a 6000-sample stop needs roughly a 2x yield collapse, and the stopping
rule already treats a truncation as undecided.

### 3. SLOPPY: the coverage study picks the interval type but does not establish nominal coverage

**Grounding.** 37/40 for the basic interval has a Clopper-Pearson 95 % interval of 0.796 to 0.984. 14/40 for the
percentile interval has 0.206 to 0.517. The two do not overlap, so basic over percentile is a sound decision.
`COVERAGE_FLOOR` 0.9 at 40 datasets, however, passes with probability 0.26 when true coverage is 0.85, and 0.08 when
it is 0.80. The study also measures coverage of the estimator's own limit, the estimand in finding 1.

**Remedy.** Describe the result as "basic over percentile", not "0.925 coverage". If nominal coverage matters, run
200 or more datasets (local and free) and score them against the physical fidelity once finding 1 is fixed.

### 4. SLOPPY: the vendor 93.8 % CNOT comparison lacks a stated metric and appears among the reasons for hardware

**Grounding.**
- `docs/notes/quandela/literature.md:161` gives "CNOT 93.8 +- 0.6 %" with no fidelity type (process, average or
  truth-table) and no HOM at measurement. The same entry gives HOM 0.9296 and corrected indistinguishability 0.9438.
- At those values the case's own model gives physical F_pro 0.901 and 0.920, and F_avg 0.921 and 0.936
  (`probe_hom.py`). Either the 93.8 % is another metric or this source model cannot reach it.
- The doc's own gate section shows that CZ = H CNOT H, so "a different gate" is weaker than the real differences,
  which are the metric and the source conditions.
- `cases.json` says "uncompiled-per-setting chip". The literature entry carries no statement about per-setting
  compilation, so that phrase has no support.
- "How much of the vendor's 93.8 % CNOT figure this compiled-per-setting route retains" is listed under "Why simulation
  cannot answer it", although it is no question about the device.

**Remedy.** Cite the fidelity type with the paper section, or drop the bullet from the case's reasons and drop the
"uncompiled-per-setting" phrase from `preregistered.vendor_comparison`. The same circuit under process tomography has
been reported in the literature, for example Kiesel et al. and Langford et al., both PRL 95 (2005). That is the right
comparison class; register the sources and verify their numbers before citing them.

### 5. SLOPPY: `--analyze` pairs iterations with settings by position

**Grounding.** `eligible_counts` uses `zip(manifest["settings"], entries, strict=False)`. Collect keeps the service's
`results_list` order (qd_platform.py 1952-1989). Each returned iteration echoes its `compilation_seed`. Requested and
echoed seeds match on mesh-port-1, signed-coherence job-06 and target-slot-drift, and this case's 144 seeds are unique.

**Remedy.** Match each entry to its setting by echoed `compilation_seed`, and require that the match is a bijection.
Also require each run's `cases.json` sha256 to equal the retained case, and the two runs to be distinct jobs.

### 6. SLOPPY: the pooled estimate has no rule for the time gap between the two jobs

**Grounding.** The jobs split the inputs by parity, so a change in HOM or T between job-00 and job-01 looks like
input-dependent process error in the pooled inversion. The procedure runs `collect --timeout 3600` between them. If
collect times out, the job-01 `plan` refuses while job-00 is still in flight, and the loop simply ends.

**Remedy.** Preregister a pooling condition: job-01's `perfs_at_plan` HOM and T within a stated tolerance of job-00's,
or a maximum gap. Without it, report the pooled estimate as descriptive.

### 7. COSMETIC / minor

- "the HOM visibility of 87.54 % alone takes the gate to 0.812": the source-only variant also includes g2. HOM alone
  gives 0.823 through the case estimator; g2 alone gives 0.981.
- The design doc's Ollivier relation drops the `[U]` (unverified) flag that the associator doc
  (`ascella-two-photon-associator-case.md:106`) carries for the same relation.
- Dark-click probability is rate / clock per pulse, which is conservative if the service gates on a 1 ns coincidence
  window (literature.md: "coincidence window 1 ns"). The dark-count variant moves F by 0.003, so the choice is harmless.
- The least-squares inversion is unweighted, while eligible events per setting run from about 645 (in-01-XX) to about
  5300 (in-10-ZZ). This costs efficiency, not correctness.
- The shot cap of in-10-ZZ rests on Perceval's 300 shots per sample. The case's own noise model at the live HOM needs
  157. The cap of 383 per sample therefore covers 2.4x the model, or 1.25x Perceval's ideal-interference figure. A
  cap hit costs that setting samples and leaves the estimate decidable. Adequate.
- 11 draw values (indices 189-199) are owned and unused. That is permitted by the ledger, but it wastes them.
- Credits: the latest retained usage (target-slot-drift, 2026-10-30 20:06 UTC) shows 137.2 of 200 free credits used
  this month. 4.8 credits fit, but the case does not state the remaining allowance.

## SOUND

- **Folded settings.** Preparation columns (cos theta/2, e^{i phi} sin theta/2), readout vectors conj(R[k]), the Y
  readout H diag(1, -i) projecting rail 0 onto |+i>, and the dual-rail convention are right. `--check` proves
  (R x R)(CZ/3)(P x P) for all 144 settings by permanents, success 1/9, and agreement with SLOS on one setting per
  readout pair.
- **Full operator.** `template_experiment` verifies the full 12 x 12 operator for schema `qd-hypercomplex-cases-v1`
  (qd_platform.py 818-826), so the target photon's column is pinned too.
- **Informational completeness.** The 4 Pauli eigenstates span qubit operators, and the 9 product Pauli bases with
  4 outcomes span all 16 two-qubit Paulis. The design matrix has rank 256 (`design_pseudoinverse` requires it).
- **Choi conventions.** Input factor first, Tr[(rho^T x E) J], F_pro = <Phi|J|Phi>/16 and F_avg = (4F + 1)/5 are
  correct.
- **Dykstra.** It matches the CLARABEL nearest-CPTP solution in F to six digits (0.782632 and 0.812445), with a
  Frobenius gap of 1e-5 and 116 to 158 sweeps. The trace-preserving residual is 6e-12 before the final input
  renormalization, so that step is cosmetic. Three sampled datasets agree to 1e-5.
- **Window choice.** Dark sums 1273, 1381, 5869 and 9638 match `plan-read.json`.
- **Billing.** charge = 1 + 1e-6 x min(total shots used, largest iteration max_shots) fits all 36 retained qpu:ascella
  jobs with usage pairs, including a5-kernel-slice at 1.06, which the runbook's "used or not" wording misstates. For
  this case expected usage exceeds the caps (18.6 M against 0.5 M, 21.7 M against 2.3 M), so the charges are 1.5 and
  3.3, as stated. The runbook needs the min form; this case does not.
- **Seeds, library gate, tests, lint, links and forecast reproducibility** all pass. Echoed compilation seeds equal
  the requested ones on retained runs, which supports "each setting compiles under its own seed".
- **Job split.** The even/odd index-sum split gives each job all four states on each qubit. Input-major order makes a
  truncation drop whole inputs, and the analysis declares the process undecided unless all 144 settings return events.
- **HOM floor.** It is correctly surfaced as an owner decision, not waived.

## Steelman

The case is engineered with unusual care. Every setting is proven against permanents and SLOS. The template binds
the full operator per iteration. The estimator recovers F = 1 and a depolarized CZ analytically. Dykstra is
numerically exact against a conic solver. Forecast and coverage are reproducible byte for byte from a retained
QRNG draw. Billing and duration rest on a retained ledger that fits every Ascella job. The estimator still compares
device and forecast like for like, so the measured gap to the source-limited forecast keeps its meaning.

## Verdict

Fit after named fixes. The blocking fix is the estimand. The preregistered "process fidelity" is the limit of a
per-setting-normalized linear inversion. Under the case's own noise model that inversion is non-physical at infinite
data (minimum eigenvalue -0.13), and it sits 0.004 to 0.010 below the trace-normalized fidelity of the postselected
map, which is comparable to the interval half-width. Because `cases.json` is bound into the plan hash, the
preregistration has to change before submit: either an absolute-rate estimator normalized by `nb_shots_used`, or an
honest rename of the target.

The duration sentence, the coverage wording, the vendor 93.8 % bullet, seed-matched iteration pairing and a pooling
rule between jobs are doc or code fixes that do not change the request bodies, except the pairing, which touches
only `--analyze`.

HOM at 87.54 % against the 90 % floor remains the owner's decision. To earn trust, show a forecast table with both
the conditional and the absolute-rate fidelity, and a coverage study of 200 or more datasets scored against the
physical quantity.
