# Staged patch-window characterization and validation

The orbit window analysis ([QPU_OPTIMIZATION.md](../../gororoba_quantum/QPU_OPTIMIZATION.md))
shows that the compiled feed-forward and omitted-correction members hold the
work state on different physical qubits during the mid-circuit window. This
plan stages a characterization of the pinned ibm_fez patch (control 142, work
136 and 144, spectator 143, neighbors 123 and 145), a frozen intervention
choice, and an independent validation on new observations.

## Budget

| Stage | Aggregate ceiling |
|---|---|
| Characterization | 26 s |
| Validation of one frozen intervention | 14 s |
| Campaign buffer | 6 s |

The usable budget is min(campaign remaining, account remaining - reserve -
unsettled ceilings). Each stage submits only after a fresh priced case and
explicit owner approval; an informative unresolved result ends the campaign.

## Characterization design: 46 circuits, 65,536 shots

| Circuit family | Circuits | Shots each | Purpose |
|---|---:|---:|---|
| Paired plain Ramsey, three durations, X/Y | 6 | 1,024 | Phase and visibility against executed exposure |
| Paired echoed Ramsey, three durations, X/Y | 6 | 1,024 | Refocusing response |
| Zero-idle paired X/Y references | 2 | 1,024 | Preparation and analysis anchor |
| Single-work-qubit long-delay X/Y references | 4 | 1,024 | Paired-preparation ZZ context |
| Control 0/1 measurement-and-reset Ramsey, three durations, X/Y | 12 | 1,024 | Measurement-associated response |
| Explicit measurement omitted, reset retained, middle duration, control 0/1, X/Y | 4 | 1,024 | Separates the measurement from the reset |
| Excite work A or B, zero and long delay | 4 | 1,024 | Transfer against preparation |
| Unexcited long-delay and all-one immediate references | 2 | 1,024 | Population and readout background |
| Original, barrier-only, barrier-plus-echo orbit pairs | 6 | 4,096 | Contemporaneous intervention contrasts |

24 static and 22 dynamic circuits run in separate jobs with per-PUB shots;
40 x 1,024 + 6 x 4,096 = 65,536.

## Design rules

- Simultaneous X on both work qubits leaves their mutual ZZ unrefocused,
  since (X_A X_B)(Z_A Z_B)(X_A X_B) = Z_A Z_B; the single-qubit references
  separate that context effect.
- Weak population transfer leaves dispersive phase possible: with
  Delta/2pi = 10 MHz and g/2pi = 0.4 MHz the transfer bound is 0.6 percent
  while g^2 t / Delta over 5.6 us is 0.56 rad.
- Phase fits use executed exposure from the returned schedule, piecewise
  across carrier changes, echo pulses, measurement, reset and dispatch.
- The barrier-only and barrier-plus-echo orbit members match state-bearing
  duration or carry duration as an explicit factor.

## Admission and analysis

- Admission contracts test phase differences, visibility differences,
  exchange excess and between-context orbit contrasts, replacing the
  positive-X proxy.
- Fits use count likelihoods with preparation and readout nuisances, leave
  phase undefined when visibility is unresolved, search periodic basins,
  keep finite intervals at boundary counts, and pass planted-mechanism
  coverage checks.
- Every analyzed row binds job id, PUB identity, shots, register order,
  compiled-circuit hash, physical mapping, raw hash and timing.

## Checklist

- [ ] Source imports and notes in docs/ (registry, INDEX, README)
- [ ] 46-circuit groups with per-PUB shots and exact-law checks
- [ ] Executed-exposure timing qualification on a dry run
- [ ] Contracts and analyzer repairs with planted-mechanism coverage
- [ ] Priced characterization case at or below 26 s; owner approval
- [ ] Frozen intervention and validation case at or below 14 s; owner approval
