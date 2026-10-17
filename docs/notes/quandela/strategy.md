# Quandela Belenos strategy guide

A living guide to getting the most science per credit out of Quandela Cloud's
photonic platforms with this repository's tooling. Each section states what
holds, the authority behind it (a retained run, the captured guide, the
Perceval 1.3.1 source or an exact computation), and what it changes in a
case. A new run or a refuted conjecture updates the section it touches and
the run log at the end.

## 1. Cost model (measured)

| Item | Value | Authority |
|---|---|---|
| Per job, any Explorer platform | 1 credit, drawn as `free_credits` from the 200-credit monthly pool | token usage report after jobs e12075f3 (sim) and 7419efb8 (QPU) |
| Per shot, qpu:belenos and qpu:ascella | 1e-06 credits | platform record; job 7419efb8 charged 1.01 for 10000 shots |
| Per shot, every simulator | 0 | platform record; six sim:belenos jobs charged 6.00 |
| Seconds charged | `duration_seconds` in the usage report (12 to 18 s per sim job, 13 s for a 10000-shot QPU job) | usage report |

The job, not the shot, is the cost unit: a 10000-shot QPU job costs 1.01
credits and a 347113-shot two-photon job 1.35. Everything that puts more
configurations into one job (iterations, packing) divides the cost; nothing
that adds shots changes it materially.

## 2. Platform facts that shape a case

- **Job names** are stored in a varchar(50); a longer `job_name` answers
  HTTP 424 "value too long for type character varying(50)". The runner names
  a job `SERIES/job-NN` and refuses longer names.
- **sim:belenos** applies its own default noise model when the payload sends
  none: g2 0.003, indistinguishability 0.92, transmittance 0.06 (result field
  `noise`). It is not the QPU's live figures (g2 1 %, HOM 92.6 % on
  2026-10-17), so a sim prediction of a QPU number sends the QPU's
  NoiseModel or recomputes locally.
- **Rates.** qpu:belenos delivered 10000 one-photon samples in 13 s, about
  770 per second (`physical_perf` 0.0074), not the clock times transmittance
  estimate of about 10^4 per second. The summed detector dark counts (about
  68 per second, 38.2 on mode 5 and 19.6 on mode 0) are then about 9 % of a
  job's samples; an analysis subtracts duration times the per-mode dark
  count before it attributes clicks outside a block to the optics.
- **Compilation.** Both the simulator and the QPU return `computed_input`
  and `computed_circuit`. For a 24-mode circuit the compiled circuit is the
  full chip mesh: 552 beam splitters (Rx convention, calibrated angles such as
  1.5867 against pi/2) and 574 phase shifters, so a photon crosses about 48
  elements whatever the block's size. The sim and the QPU returned
  byte-identical compiled circuits for the same case, so a QPU deviation from
  a sim result is the hardware's realization of that circuit.
- **Input adaptation.** A photon on a mode without a source makes the cloud
  add routing permutations and re-transpile (`guide/user-guide/04-compilation.md`);
  every case puts photons on the connected modes 0, 2, 4, 6, 8, 9, 12, 13,
  16, 18, 20, 22.
- **Iterations.** One Perceval `ComputationIterator` job carries a list of
  iterations, each with any of `circuit_params`, `input_state`,
  `min_detected_photons`, `max_samples`, `max_shots`, `postselect` and
  `compilation_seed` (`perceval/runtime/computation_iterator.py`); the result
  answers `results_list`, one entry per iteration. A whole parameter scan
  costs one job.
- **Compilation seeds** are an iteration key, and `CompilationAveraging` is a
  known mitigation of both Belenos platforms, so the spread over compilations
  is measurable inside one job.
- **Weekly maintenance** blocks qpu:belenos (2026-10-22 07:30 to 11:00 UTC
  in the platform record); the runner refuses any status other than
  `available`.

## 3. Client safety

`perceval.serialization.deserialize` evaluates parameter expressions through
sympy, and the deprecated result-mapping branch of
`RPCBasedCommunicationLayer.get_results` calls `__import__` on a module name
taken from the service's answer. The runner never calls either: it parses
counts from the BSCount string itself, reads a compiled circuit through the
protobuf message class (`exqalibur.serialization.circuit_pb2.Circuit`), posts
through a no-redirect opener and keeps the token out of every file it writes.

## 4. Circuits from first principles

- **Encoding.** A photon carries the Design B product x y. V = L_x on
  span{e_L', e_U'} divided by sqrt2 is M / 2 for the sign block
  M = [[g(L,L'), s g(U,U')], [s g(U,L'), g(L,U')]], and the circuit is the
  Halmos dilation [[V, sqrt(I - V V^T)], [sqrt(I - V^T V), -V^T]], exact over
  Q(sqrt2) (`scripts/qd_box_kite_cases.py`).
- **Native gates.** Every sign matrix is M = D1 K D2 with +-1 diagonals and
  K the edge core [[1, 1], [1, 1]] or the strut core [[1, 1], [1, -1]], and
  dil(D1 K D2) = diag(D1, D2) dil(K / 2) diag(D2, D1). So every block is a
  pi-phase layer, a core and a pi-phase layer of Perceval's BS.H (balanced),
  PS(pi) and PERM:
  - edge core (BS.H_01 BS.H_23) PS_2 SWAP_13 (BS.H_01 BS.H_23): the core
    routes, it does not mix label and dilation space;
  - strut core BS.H_01 BS.H_02 BS.H_13 BS.H_23: balanced mixing of label and
    dilation modes, the beam splitters of a Hong-Ou-Mandel suppression.
  The box-kite signs enter only as pi phases; edge against strut is a
  routing core against a mixing core. Perceval places beam splitters on
  adjacent modes only, so the non-adjacent pair is
  SWAP_12 (BS.H_01 BS.H_23) SWAP_12. Every native list is checked against its
  unitary in exact arithmetic, and the runner checks Perceval's unitary of
  the circuit it sends against the case to 1e-12.
- **What one photon can show.** Only column 0 of U is observable, and an
  output phase changes no click probability, so a one-photon block tests
  that the chip implements a known distribution: classical-wave
  interference, never a nonclassical effect.
- **What two photons show.** One photon on each input port of the dilation
  is the bipartite case: the label coincidence is |perm(V)|^2 =
  (perm M / 4)^2, and perm M = g(L,L') g(L,U') (1 + p0 p1), det M =
  g(L,L') g(L,U') (1 - p0 p1) for the kite phase products. An edge
  (p0 = p1) bunches at 1/4 and a strut (p0 != p1) suppresses to 0 against
  1/8 for distinguishable photons. The box-kite octahedron is K_{2,2,2}:
  struts pair assessors within one of its three parts, edges join parts, and
  the permanent vanishes exactly on the within-part pairs.
- **The phase fringe.** With the input phase as a parameter, a block's
  algebra probability is P(phi) = [4 + 2 cos phi (m00 m01 + m10 m11)] / 8:
  an edge follows (1 + cos phi) / 2 (bright at 0, dark at pi) and a strut is
  flat at 1/2. One iterated job over phi = k pi/4 measures visibility (the
  chip's zero-divisor contrast) and phase offset (its phase error) on one
  compiled mesh, where common-mode errors cancel (`belenos_fringe`).
- **Coverage.** Census Design B rows reach 14 of the 16 sign matrices;
  cd_core witness pairs supply the other two, and every two-label two-blade
  product at D = 16, 32 and 64 maps to one of the 32 (M, t) circuits
  (`docs/evidence/box_kite_census/two_blade_blocks.json`).

## 5. Analysis rules

- One-photon block: in_block (one-click samples on the block's modes over
  all one-click samples, ideal 1) separates routing loss from the algebra
  share a; the per-mode total variation distance uses every sample.
- Two-photon block: threshold detectors with min_detected_photons 2 keep
  only two-click samples, so the observable is the conditional label
  fraction f(V) = (V L_ind + (1 - V) L_dist) / (V T_ind + (1 - V) T_dist),
  fitted under the g2 read at submission; a two-mode HOM job reads only (0, 1)
  coincidences under that filter and carries no V.
- Fringe: a(phi) per iteration and the closed-form fit A + B cos phi +
  C sin phi over the eight phases (`scripts/qd_box_kite_analysis.py`).

## 6. Open conjectures and their falsifiers

| Conjecture | Test | Falsifier |
|---|---|---|
| The QPU leakage comes from fitting a 24-mode unitary | belenos_diagnostics job-01 (4-mode compact) against single/job-04 | in_block of the compact job within 4.5 standard errors of 0.470 |
| The chip leaks even for the identity | belenos_diagnostics job-00 (identity, photon at mode 20) | in_block above 0.9 |
| The transpiler re-fits native gates as a unitary | diagnostics job-02/job-03 on sim:belenos: compare computed_circuit | a computed circuit that differs from the unitary form's |
| The server runs iterations in one job on one compiled mesh | belenos_fringe on sim:belenos | no results_list, or one computed_circuit per iteration |
| The fringe visibility separates edge from strut on hardware | belenos_fringe job-00 and job-01 on qpu:belenos | edge visibility within 4.5 standard errors of the strut's |
| The chip implements U, not its transpose | a U / U^T job pair | counts closer to the transpose's column |

## 7. Tricks not yet used

- Seed averaging: repeat the fringe's phases over several `compilation_seed`
  values in one job and report the spread.
- Pre-compilation reuse: send the simulator's `computed_circuit` and
  `computed_input` to the QPU; the protobuf decode above is the parser's base.
- Minimal one-photon circuits: a 2 to 3 beam-splitter state preparation of
  column 0 gives the same distribution with fewer elements, at the cost of
  no longer running the algebra map on the chip.
- Grouping configurations that share a detection distribution, so repeated
  jobs measure compile variance instead of duplicating an experiment.
- A likelihood fit of all six two-click mode pairs with V and g2, and the
  quasi photon-number-resolving detectors to recover bunched events.

## 8. Run log

| Date (UTC) | Job | Platform | Case | Credits | Result |
|---|---|---|---|---|---|
| 2026-10-17 21:35 | refused | sim:belenos | single/job-04 | 0 | HTTP 424, job name over 50 characters |
| 2026-10-17 21:36 | e12075f3 | sim:belenos | single/job-04 bright | 1.00 | a = 1 (5003/4996/0/0) |
| 2026-10-17 21:37 | 7419efb8 | qpu:belenos | single/job-04 bright | 1.01 | in_block 0.470, a = 0.256 |
| 2026-10-17 | five jobs | sim:belenos | dark, strut, one-hot, pair edge, pair strut | 5.00 | every exact ideal; strut V = 0.918 |
