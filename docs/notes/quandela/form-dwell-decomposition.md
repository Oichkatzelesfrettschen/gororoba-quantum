# Form versus dwell on qpu:belenos: decomposition of D1 to D4

This note decomposes the four form-versus-dwell designs of
[strategy.md](strategy.md) section 7 item 10 into the chip facts they rest
on, the retained runs that shaped them, and the Python capabilities that can
and cannot stand in for hardware. Names follow strategy.md section 1a: a
single job (S) carries one setting, an iterated job (I) carries many, dwell
is the samples spent consecutively on one setting, and a served mesh is named
by the sha256 prefix of its compiled circuit. The preregistered thresholds are
in `results/quandela/sessions/2026-10-18T084900Z-qpu_belenos-belenos_mesh-dwell/dwell-preregistration.json`.

## 1. The question as factors

Q1's bright block kept 0.470 and 0.504 of its one-click samples on mesh
29dc6ef8 as a 10000-sample S job, and 0.949 on the same mesh as a 1500-sample
iteration of an I job (c2eea262). Three factors changed between those cells:

| Factor | Q1 (leaks) | c2eea262 seed 20 (holds) | Isolated by |
|---|---|---|---|
| Form: payload `Computation` or `ComputationIterator` | S | I | D1 against Q1 holds the form and changes the dwell |
| Dwell: samples on the setting | 10000 (13 to 15 s) | 1500 (about 2 s of sampling) | D1, and the D2 ladder inside one I job |
| Mesh | 29dc6ef8 | 29dc6ef8 | held; D3 and D4 repeat the question on a fresh mesh |
| Position | first and only setting of its job | 21st of 24 settings | not isolated; the ladder's interleaved 1500-sample iterations bound its effect inside I |
| Calibration and time | 2026-10-17 21:36 and 2026-10-18 02:55 | 2026-10-18 07:45 | bounded by the 0.034 cross-job scale (Q1 against its replay across a calibration) |

job-08's mesh e296b6a9 held in both forms (0.886 S at dwell 10000, 0.907 I
at dwell 1500), so the leak is not a property of every long S job; D3 tests
whether a fresh mesh behaves like 29dc6ef8 or like e296b6a9.

## 2. Chip facts the designs rest on

Each fact is retained in strategy.md sections 1, 1a, 2 and 7 with its run.

- **One fixed mesh.** The processor record's architecture is 552 Rx beam
  splitters at calibrated angles (1.557 to 1.662 rad) and 574 heater phases:
  276 MZIs in 70 columns plus 22 edge phases on modes 0 and 23. Every served
  circuit carries that topology, so a setting is 574 numbers, and a photon
  crosses about 48 elements whatever the block's width.
- **The transpiler draws the unused columns.** The service fits the target's
  occupied input columns with exqalibur's CircuitOptimizer from random
  starting phases; the other 23 columns stay random. Q1's bright block fans
  the photon over modes 16 to 23 inside the mesh and relies on interference
  to re-converge onto modes 20 and 21, so a mesh can be sensitive to phase
  error where another solution of the same target is not.
- **compilation_seed selects the served mesh** (16 of 16 configurations in
  job-07; 22 distinct meshes from 24 seeds in c2eea262), and seed 1 served
  e296b6a9 in both forms. The service's unseeded default is not seed 0:
  unseeded S jobs served 29dc6ef8, which seed 20 also serves in the I form.
- **Sources and detectors.** Twelve modes carry photon sources (0, 2, 4, 6,
  8, 9, 12, 13, 16, 18, 20, 22); detectors are threshold detectors with
  relative output transmissions of 194 to 401 on modes 12 to 23 and dark
  rates up to 42 per second on mode 5 at the dry run. One-photon samples
  arrive at about 770 per second, and shots used equal samples kept.
- **Cost and time.** A job bills 1 credit plus 1e-06 per billed shot; every
  I job so far billed 1.003 whatever its total shots (the inferred
  one-iteration rule). A setting costs about 5.2 s of overhead plus 0.75 ms
  per sample, and a job ends at 300 s.
- **Drift.** Exact repeats of one I body 36 minutes apart returned the same
  meshes and histograms differing by a median TVD of 0.128 (job-03 against
  its repeat), while Q1 and its replay on 29dc6ef8 agreed within 0.034 across
  a calibration. Within one I job, repeated seeds agreed within 0.005.

The inferred dwell mechanism, untested: holding one heater pattern for 13 s
lets thermal crosstalk between neighboring heaters build toward a steady
state that differs from the calibrated one, and a mesh whose re-convergence
depends on many interfering paths (29dc6ef8) loses the photon where a more
direct solution (e296b6a9) does not. D1 and the D2 ladder test the dwell half
of that chain; D3 and D4 test whether susceptibility is a mesh property.

## 3. What the retained runs taught

| Run | Lesson that shapes D1 to D4 |
|---|---|
| Q1 7419efb8, replay 7af74302 | 29dc6ef8 leaks about half its light as an S job, reproducibly across a calibration (0.470, 0.504) |
| diagnostics job-01 to job-03 (sim) | width and gate form do not change the full-mesh compilation; the leak is not a 24-mode fitting artifact |
| C1 job-03 to job-06 and its repeat | no fixed error class fits random meshes; the chip drifts between jobs, so cross-job comparisons need a measured scale |
| job-02 4e208d22 | Q1's target, sent as architecture phases, holds 0.987 in the I form at seed 0; the leak is job specific |
| job-08 8d28f121 | an S job at seed 1 holds 0.886 on e296b6a9: S alone does not leak |
| job-07 b8e2ec0c | the seed selects the mesh; 32 iterations of 1500 samples fit in 221 s |
| job-09 c2eea262 | 29dc6ef8 holds 0.949 in the I form; drift within a job is 0.005; the iterated per-setting overhead is about 5.2 s |

## 4. What local computation can and cannot answer

[python-stack.md](python-stack.md) maps the installed packages; section 4
there carries the evidence for each line below.

- **Mesh prediction: no.** exqalibur's CircuitOptimizer is deterministic
  per seed locally, but Perceval never passes `compilation_seed` to it, and
  no local seed from 0 to 63 reproduced a served phase. D3's mesh is known
  only after its job returns it. The 22 seed and mesh pairs of c2eea262 on
  one fixed target are a new test set for a bitwise replay.
- **Noise simulation: partial.** Perceval's NoiseModel carries brightness,
  indistinguishability, g2, transmittance, a static per-heater phase error
  and phase quantization, and detectors take per-mode efficiencies. It has no
  dark counts and no time-varying phase drift, so it cannot model a dwell
  effect; `qd_belenos_mesh` scans static error classes on returned meshes,
  which is how a D1 to D4 mesh is scored after it returns.
- **Time-ordered samples: unverified.** The `samples` command returns a
  `BSSamples` stream that Perceval serializes in order, but no retained job
  shows the cloud returns events in acquisition order, so the designs keep
  `sample_count` and resolve dwell across iterations instead.
- **Counts: yes.** Wilson intervals and the per-iteration mesh digest come
  from `qd_box_kite_analysis.py`; `qd_belenos_mesh.py --dwell` applies the
  preregistered readings.

## 5. The designs

| Design | Case | Form | Seed and mesh | Dwell | Isolates | Dry run |
|---|---|---|---|---|---|---|
| D1 | job-10 | S | unseeded, 29dc6ef8 expected | 1500 | dwell at fixed S form and mesh | 1500 shots estimated, 1.0015 credits, ceiling 1.003 |
| D3 | job-11 | S | 46667 (ANU draw value 0), fresh | 10000 | mesh susceptibility at Q1's leaking condition | 10000 shots, 1.01 credits, ceiling 1.02 |
| D2 | job-12 | I | 20, 29dc6ef8 | 1500, 10000, 1500, 40000, 1500, 60000 | dwell inside the I form, drift between | with D4: 166000 shots; 1.003 under the one-iteration billing rule, 1.166 if every shot bills, ceiling 1.332 |
| D4 | job-12 | I | 46667, D3's mesh if seeds carry across forms | 1500, 10000, 40000 | D3's I partner | in D2's job |

Readings (preregistered): D1 at most 0.65 reads form, at least 0.90 reads
dwell, each with the 0.034 cross-job margin; D3 reads generic or mesh
susceptible on the same thresholds; a ladder reads dwell when pooled
1500-sample in_block exceeds pooled long-dwell in_block by at least 0.25 plus
its short-iteration spread, and flat when by at most 0.05 plus that spread.

| D1 | D2 | Reading |
|---|---|---|
| form | flat | the S form leaks on 29dc6ef8 at any dwell; dwell is not the cause |
| dwell | dwell | long dwell causes the leak in either form |
| dwell | flat | long dwell leaks only in the S form: form and dwell interact |
| form | dwell | both act; the S form leaks early and long I iterations also lose light |

D3 and D4 repeat the reading on a fresh mesh when they pair (D4's mesh equals
D3's). The order is D1, D3, then the D2 + D4 job, back to back, so the
cross-job scale stays near its measured 0.034.

## 6. Outcome

The series ran as preregistered for 3.1315 credits (section 11 of
strategy.md and `dwell.json` hold the numbers). Two premises of this
decomposition failed and are corrected in strategy.md section 1a: an S job's
13 to 15 s is overhead (1500 and 10000 samples both took 14 s), and an I job
bills its largest iteration's `max_shots`. With acquisition near 4 x 10^4
samples per second, "dwell" in these designs is a sample budget, not seconds
of heater exposure. 29dc6ef8 held 0.918 in a 1500-sample single job and
0.90 to 0.99 in every iteration up to 60000 samples, so its leak needs the
single-job form with a large budget; the fresh mesh 14a96ca6 held 0.937 in
a 10000-sample single job and declined to 0.852 at the end of the iterated
job.

The light-cone reading (`docs/evidence/quandela/belenos_light_cone.json`,
strategy.md section 7 item 11) reads the same cells inside source 20's cone
of each served mesh, which excludes the off-cone clicks that come and go on
modes 0, 1 and 5. Every seeded iterated cell and D3 then hold 0.982 to 0.995
at every budget, D4's decline is off-cone clicks on mode 5, and the cells
that lose light inside the cone are the single jobs on 29dc6ef8 (Q1 0.507
and 0.518, D1 0.918). Case job-13 (strategy.md item 12) then ran Q1's single
job at seed 20 and kept 0.389 inside the ideal cone, its preregistered
statistic: seeding plays no part, and the leak is a 10000-sample single job
on 29dc6ef8, as the raw D1 to D4 readings suggested, with D4's decline
removed as off-cone clicks.
