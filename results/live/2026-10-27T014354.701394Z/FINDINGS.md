# N=21 orbit window-dose sweep: findings

The free-idle arm of the N=21 orbit loses feedback contrast with dose faster than the execution Target's T1 and T2
predict, and the Hahn echo removes most of that excess: D1 and D3 hold and D2 reads kappa_P = 1.77 times the
Target's rate. The one-rate family the decisions fit misfits the sweep by a factor of 85 in chi2 per degree of
freedom, and the excess reads as a per-replica coherent precession rather than a faster decay. The detuning-sign test that followed this run
(Kingston job `dbge2jpj4t8s73ac6fk0`, [findings](../2026-10-27T173602.753176Z/FINDINGS.md)) measured that
precession with its sign and found it to turn at the frame offset of the work bit for 16 minus that of the work bit
for 1, slope 1.010 [0.977, 1.043].

## Run

ibm_kingston job `dbg04idjm0ks73efj0j0` on the backup instance (`f59f9992321c`), under the approved envelope
[n21-orbit-window-dose-envelope.md](../../../docs/design/n21-orbit-window-dose-envelope.md) in its 50 us and 90 s
revision (commit `27d7d08`). The approved dry run `2026-10-27T013902.641724Z` planned at the Kingston calibration of
2026-10-26T17:55:09-07:00, and this run submitted it: 19 four-qubit replicas, 26 PUBs of 8,192 shots in one dynamic
job at a 50 us repetition delay, seven doses from 0 to 14,000 dt in a free-idle (plain) and a Hahn-echo arm, each
with and without feed-forward. The shot loop ran from 02:54:52 to 02:56:17 UTC, `circuits_execution_time_ns`
reads 83.87 s, and the service billed 86 s.

Two earlier submissions of the same envelope reached their 30 s `max_execution_time` and ended with error 1305
(`RuntimeJobMaxTimeoutError`): job `dbfvdfdjm0ks73efhflg` at a 20 us delay (run `2026-10-27T005259.826486Z`, from
dry run `2026-10-27T003928.422192Z`) and job `dbfvqm8iudkc73e3diq0` at 50 us (run `2026-10-27T011304.736763Z`,
from dry run `2026-10-27T010222.461059Z`). Their records stay beside this run as the attempt history the runtime
seed ledger names; they hold no shots.

## Schedule

The scheduler table of every PUB (`raw/dbg04idjm0ks73efj0j0/pub_*.json`, `scheduler_timing.circuit_duration`)
puts the feedback members at 152 us (dose 0) to 1,212 us (14,000 dt, echo) and the members without feedback at
23 us to 79 us. The service runs the 19 replicas' feed-forward branches one after another, so a feedback PUB lasts
about 19 times one replica's dose and branch. The 26 PUBs average 343.8 us per shot; with the 50 us delay,
212,992 shots take 83.9 s, which is the measured shot-loop time. The planner priced the replicas as parallel and
estimated 23.5 s, so the two 30 s attempts ran out of time on the serialization, not on a stalled loop.

## Decisions

`scripts/n21_dose_decisions.py` wrote [dose-decisions.json](dose-decisions.json) from the raw registers, the
scheduled-idle replay [idle-replay.json](idle-replay.json) and the dose-scaled model family
[idle-scaling.json](idle-scaling.json), the three commands of the envelope's Decisions section, run under the
pinned CI interpreter. Every interval is conditional on the execution Target's per-qubit T1 and T2 point values.

| Decision | Result | Verdict |
|---|---|---|
| D1, plain contrast at 14,000 dt minus dose 0 | -0.246 +- 0.005, one-sided upper bound -0.239 | holds |
| D2, plain rate kappa_P | 1.77, 95 percent interval [1.17, 2.56], chi2_min 426.8 on 5 (scale factor 85.4, shape p 5e-90) | plain idle loss beyond the Target, the interval excluding 1 |
| D3, kappa_P - kappa_E | 1.17 [0.84, 1.51], with kappa_P 1.82 [1.44, 2.27] and kappa_E 0.65 [0.30, 1.08], chi2_min 442.2 on 10 (scale factor 44.2) | the Hahn echo removes idle loss beyond the Target model |
| Amendment, all-idle rate | not computed: the exact model refuses laws of the all-idle family at the largest factors | |

The block-drift check over 16 blocks per PUB finds dispersion beyond shot noise, chi2 485.2 on 390 (p 0.0007), and
inflates the covariance of each member whose ratio exceeds one; the largest ratio is 1.82, on the 7,000 dt
feedback member of the plain arm.

## Contrasts

The pooled feedback contrast of each arm, measured and as the Target model predicts it (`arms` in
`dose-decisions.json`); standard errors are 0.003 throughout.

| Dose (dt) | Plain measured | Plain model | Echo measured | Echo model |
|---|---|---|---|---|
| 0 | +0.100 | +0.169 | | |
| 1,752 | +0.038 | +0.142 | +0.070 | +0.148 |
| 3,500 | -0.026 | +0.116 | +0.060 | +0.129 |
| 5,252 | -0.075 | +0.092 | +0.047 | +0.112 |
| 7,000 | -0.119 | +0.070 | +0.029 | +0.096 |
| 10,500 | -0.143 | +0.029 | +0.004 | +0.068 |
| 14,000 | -0.146 | -0.008 | -0.005 | +0.044 |

The echo arm sits 0.050 to 0.078 below its model at every dose, while the plain arm falls away from its model with
dose, from 0.069 below it at dose 0 to 0.189 below at 7,000 dt. The dose-0 deficit is present before any dose.

## Reading

The envelope foresaw two readings of a positive D3, quasi-static dephasing and static detuning, and the design does
not separate them. A post-hoc split of the
no-feedback member's second-round contrast into a relaxation offset (the mean over the first bit) and a coherence
(the difference over the first bit) placed the relaxation on the Target model at every dose and the whole deviation
in the coherence, which turned as a cosine of the dose at a replica-specific rate of a few to about 30 kHz and
stayed flat in the echo arm. That split ran outside the preregistered analysis and is not retained; it fixed the
magnitude of each replica's rate and not its sign, since the cosine is even in frequency, and it motivated the
signed test below rather than deciding anything itself.

The detuning-sign envelope turned that reading into a preregistered falsifier: same-calibration Ramsey offsets of
each replica's two work qubits against the orbit's signed precession, read through both quadratures. Its three
decisions hold on 17 or 18 replicas each, so the dose-time residual of this run is a precession of the two work
qubits' frequencies off the frames the gates track, refocused by the echo. The same findings document excludes
static ZZ coupling by the state the replicas hold during the dose, and corrects the first decomposition's work-qubit
positions to initial-layout positions 0 and 3. A readout-induced Stark shift cannot drive the no-feedback member,
whose PUB runs the replicas in parallel with no readout during the dose.

The dose-0 offset of both arms is a phase each replica's orbit carries before any dose; the echo leaves it in place
because it refocuses only the dose delay. This run does not locate its source.

## Feedback member and the serialization

The envelope's amendment named a per-replica comparison of each contrast residual with the replica's serialized
wait as the answer to the serialization question. That comparison, as first drawn, regressed the residual of the
no-feedback member, which the service does not serialize, and is withdrawn. The feedback member's scored branch
carries almost no model contrast, so its agreement with the model tests nothing. Its serialized wait holds the
control and the work register entangled in free idle, where the same per-qubit frame offsets, now of the control and
all three work qubits, would dephase it. Testing that needs the control's and the bit for 4's offsets, which this
run does not measure.

## Limits

Both fitted families misfit by the scale factors above, so kappa_P and delta read the pooled loss of a precession,
not a decay rate; the verdicts stand as preregistered, and the per-replica `kappa_p_per_replica` rows carry the
spread. The run has one calibration and no between-calibration variance. The dose grid's 14 us spacing at its top
aliases near 35 kHz.

## Retention

The backup inventory was observed before this submission, so the backup retention audit lists the raw archive
under `awaiting_observation`; the run joins coverage and the research registry at the next inventory observation.
The runtime seed ledger row for draw `docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json`, indices 0 and 1, names
dry run `2026-10-27T003928.422192Z` with the two resubmitted dry runs of the same envelope.
