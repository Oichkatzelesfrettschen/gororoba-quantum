# Case: segmented coprime swap sweep of ibm_fez qubit 143

Status: approved and executed. ibm_marrakesh qubit 47 ran first as a
baseline and ibm_fez qubit 143 ran the question (section Execution).
Nothing in this document submits.

## Question

The ground Ramsey sweep (run 2026-10-20T031212.175942Z, section "Beat
models of qubit 143" of [N21_ORBIT_RCA.md](N21_ORBIT_RCA.md)) shows two
coherent lines of qubit 143 with weights 0.644 / 0.356 and a splitting
known only modulo 299.04 kHz. This run measures:

1. which alias cell holds df (sign and magnitude of the splitting);
2. whether the two lines are a classical mixture fixed within each shot
   (charge parity, static or slowly switching) or an exchange-coupled TLS,
   read through two separate signatures: the correlation of a shot's
   segments (a line fixed in a shot correlates them, a TLS does not, at
   every TLS population p) and the Z swap after an X preparation (depth
   (1 - p) 4 a (1 - a));
3. whether the herald readout perturbs the Ramsey (backaction control).

A noise simulation cannot answer it: the Aer model built from calibration
carries one line per qubit and predicts visibility near 0.99 at every
delay, while the hardware reads a beat. The question concerns qubit 143
itself, the AGENTS.md criterion for IBM hardware below 16 qubits.

## Design

- ibm_fez, `--pin-layout ibm_fez:142,136,143,144` (control 142 in |0>,
  spectator 143 as logical qubit 2), `--init-herald --ground-control-split`.
- 23 delays: 0, multiples of 693 dt to 8316 dt and of 819 dt to 8190 dt
  (gcd 63 dt = 0.252 us, an unaliased complex band of 3.97 MHz).
- 6 segments per shot (`--segments 6`). Each segment: herald, preparation,
  idle of exactly delay dt, basis change, readout; a reset of 143 opens
  every segment after the first, so each preparation follows a herald
  readout exactly as in segment 1. Segment 1 heralds all four pinned
  qubits; later segments herald 143. Each segment writes its own
  registers (`s<k>_herald`, `s<k>_read`), 15 clbits per shot.
- Per delay one xy arm (X, Y, X, Y, X, Y after |+>: both quadratures share
  every shot, so no inter-PUB drift separates them) and one z arm (Z after
  an X preparation, six times).
- Backaction controls: xy arms at 0 and 693 dt with a 1250 dt (5 us) idle
  between herald and preparation.
- 48 PUBs x 1536 shots, one dynamic job, no if_else (the per-job broadcast
  budget stays unused), no twirling, no dynamical decoupling, rep_delay
  50 us.

The compiled dry-run ISAs place each idle as one delay of exactly the
configured dt on qubit 143 alone, six times per arm (and the 1250 dt
pre-idle in the controls); tests/gororoba_quantum/test_qpu_planning_segmented_sweep.py
holds that on FakeFez.

## Optimization: more samples per billed second

Measured fact: the retained run's circuits_execution_time equaled shots x
(rep_delay + circuit_duration), circuit_duration including INIT and FINI
(1717 dt); charge added 2.62 s. The repetition delay plus INIT/FINI cost
56.9 us per shot against a mean idle of 16.8 us, so the shot is the costly
unit and more reads per shot is the lever.

| Option | Billed effect | Statistical effect | Decision |
|---|---|---|---|
| (a) K segments per shot | each extra segment costs reset + herald + readout + gates + idle (1264 dt + idle) instead of 56.9 us + INIT/FINI | segments of a shot share a fixed line; the analysis scores the shot's pattern, which turns the correlation into a TLS-vs-mixture discriminator | adopted, K = 6 |
| (b) rep_delay 20 to 30 us | K = 6 x 1024: 16.0 s at 50 us against 14.6 s at 30 us | changes segment 1's start condition against the retained run and the four-repeat series; 20 us is the documented floor and both Kingston 20 us jobs ended 1305 ([REP_DELAY_ZERO_CONTROL_FINDINGS.md](REP_DELAY_ZERO_CONTROL_FINDINGS.md)) | rejected, 50 us kept |
| (c) measure_2 heralds and readouts | 80 dt less per measure, under 4 % of the shot | different readout physics and assignment error; Aer has no measure_2, so planning and ideal validation would need a stand-in | rejected |
| (d) Fisher-optimal allocation | runtime 0.48 deprecates differing pub.shots in one job | the locally optimal design is computed at the fitted alias, the quantity under test | uniform kept; allocation would come from segment counts |
| measure_reset in place of readout + reset | 415 dt less per segment (about 8 %) | not emitted by the planner's compile path; Aer lacks it | not adopted |

Trade table (scripts/n21_q143_segmented_sweep.py --design,
[n21-q143-segmented-design.json](n21-q143-segmented-design.json), gate
core-616). Asimov expected LLRs at the retained static fit under the
shot-level likelihood with e0, e1 free, df confined to its alias cell for
every alternative, and the TLS population p0 profiled; tls rows give the
worst p0 over {0, 0.5, 1}. "1 x 2048" is the uniform one-read design.

| Design | PUBs x shots | Kept reads | Rule (s) | Charge est. (s) | Worst alias pair | tls truth, worst p0 | static truth vs tls | telegraph 0.01 / 0.03 / 0.1 per us |
|---|---|---|---|---|---|---|---|---|
| 1 x 2048 (uniform) | 69 x 2048 | 138910 | 14.7 | 13.8 | 1570 | 11.2 | 20.2 | 49 / 11 / 846 |
| 2 x 2048 | 48 x 2048 | 185872 | 12.9 | 12.3 | 2503 (truth cell 0) | 764 | 1009 | 58 / 276 / 879 |
| 4 x 1536 | 48 x 1536 | 279303 | 13.5 | 13.1 | 4340 (truth cell 0) | 2149 | 4129 | 121 / 299 / 308 |
| 6 x 1024 | 48 x 1024 | 279468 | 11.9 | 11.8 | 4549 (truth cell 0) | 2550 | 5752 | 425 / 661 / 487 |
| **6 x 1536 (chosen)** | 48 x 1536 | 419202 | 16.7 | 16.3 | 6823 | 3825 | 8627 | 553 / 992 / 731 |

The chosen design reads 2.97 times the uniform design's kept reads for
1.6 s more by the cost rule, and every separation the selection rule names
(50) is passed by a factor of 76 or more; the uniform design fails the TLS
separation at p0 = 1 under this likelihood. LLRs come from one local refit
per alternative, so a refit trapped above the alternative's minimum
overstates its row; the telegraph columns of the uniform design (49 at
0.01 above 11 at 0.03) show that limitation.

## Analysis rules (preregistered)

scripts/n21_q143_segmented_sweep.py, whose import closure over scripts/
(with n21_q143_beat_model.py, n21_orbit_rca.py, n21_spectator_ramsey.py)
and gororoba_quantum/ (qpe_diagnostics.py and what it imports) the policy
binds as `segmented_analyzer_closure`; a changed closure file makes
the submission refuse with approval_required.

- Selection: a shot whose segment-1 herald reads any neighbor (142, 136,
  144) excited is dropped; a segment whose 143 herald reads 1 is
  marginalized out of its shot's pattern.
- Schedule admission: every segment's pre-idle, Ramsey idle and pulse count
  in the returned scheduler table equal the member's design.
- Family alpha 0.05 over six tests (0.00833 each): herald_admission
  (per-bit spread of the excitation a herald reading 0 lets through,
  segment-1 bits and each later 143 herald),
  segment_exchangeability (first X and Y read against the later ones, per
  shot), herald_backaction (controls against the same delay, per-shot X
  and Y means with their covariance), alias
  resolution, model decision, z_memory.
- Primary data: every X and Y segment and segment 1 of each Z arm. If
  exchangeability fails, the primary data fall back to the first X and
  first Y segment per shot.
- Alias: static fit per df cell; resolved when the second-best cell's NLL
  exceeds the best by more than log(1 / 0.00833) = 4.79.
- Model decision: the lower of static and telegraph against tls by the
  same margin: tls, line_mixture or undecided.
- z_memory: segment 1 of each Z arm against its later segments (Wald,
  per shot); a TLS left excited by the swap moves it, a line mixture does
  not.
- `RUN_DIR` writes segmented-sweep.json; `--check` requires equal bytes.

Planted truths (tests/scripts/test_n21_q143_segmented_sweep.py): the one-segment chain equals the
binomial; segment marginals equal the telegraph kernel; a refused segment
marginalizes; static draws pass exchangeability and a later-segment offset
fails it; a 10 % coherence loss in the controls reads backaction; a static
plant favors the line mixture over tls by 6065 and a tls plant tls by 6981.

## Cost and quota

- Dry run 2026-10-21T025706.848746Z (code commit 0ce8d59, experiment source
  digest 212b66dffd52..., record.json sha256
  37671686b78ee7981af9b159973716e72c040cfc592e30d7f28306b5c1441015, analyzer
  closure 5998e98c268e...; ibm_fez calibration 2026-10-21T02:31:53Z, 156
  pending): planner estimate 15.5 s (Target durations, 2.3 s job overhead); with INIT/FINI added the execution rule gives 13.7 s and
  the retained charge offset 16.3 s; the rule above 16.7 s.
- Ceiling `--max-execution-seconds 30`, cap 30 s: 1.8 times the expected
  charge, so neither a slower shot loop nor queue-side overhead reaches
  it, and rep_delay stays at the 50 us of the completed runs.
- Quota: 151 s remaining at the dry run; after this run about 134 s.
- Envelope: 15 to 18 s billed.

## Submit command

From gororoba_quantum/, after approval, with the dry run made by the same
command without the last three lines:

```sh
"$PYTHON" live_run.py --family n21-orbit-rca --shot-allocation uniform \
  --objective minimum_charge --local-compute auto \
  --local-compute-method density_matrix_dynamic_statevector \
  --simulation-threads 12 --simulation-memory-mb 512 --optimize \
  --backends ibm_fez --shots 1536 --seeds 8 --max-pending 250 \
  --min-remaining-seconds 60.0 --max-execution-seconds 30 --rep-delay 5e-05 \
  --no-isolated-reference --cross-group-buffer --shot-tiers 1536 \
  --replica-tiers 1 --optimizer-candidates 6 --model-shots 16384 \
  --precision 0.08 --alpha 0.05 --power 0.8 --simulation-alpha 0.01 \
  --job-overhead-seconds 2.3 --classical-latency-us 20.0 \
  --reserve-seconds 0.0 --max-total-execution-seconds 30.0 \
  --init-herald --ground-control-split \
  --segmented-delays-dt 0,693,819,1386,1638,2079,2457,2772,3276,3465,4095,4158,4851,4914,5544,5733,6237,6552,6930,7371,7623,8190,8316 \
  --segments 6 --backaction-delays-dt 0,693 --backaction-pre-idle-dt 1250 \
  --pin-layout ibm_fez:142,136,143,144 --out ../results/live --submit \
  --approved-record ../results/live/RECORD_DIR \
  --approved-record-sha256 RECORD_SHA256
```

`--approved-record` takes the dry run's record directory (approval writes
approval-consumed.json beside its record.json); `--approved-record-sha256`
is that record.json's digest. The approving dry run lands under
results/live/ from this command without `--submit` and the two approval
flags, after the branch's final commit, so the experiment digest and the
analyzer closure match. Its 48 PUBs wrote their ideal laws densely over 2^15
outcomes (84 MB records, 16 MB cases); the retained dry runs and runs hold
them re-encoded through law_encoding, and each directory's
dense-sha256.json names the original record digest the approval binds
(scripts/encode_wide_run.py --check, gate core-618). `--max-pending 250`
admits ibm_fez's queue (156 pending at the dry run).

## Execution

ibm_fez held 1,480 to 1,730 pending jobs from 03:48Z on 2026-10-21, above
the case's `--max-pending 250`. Before any submission the owner approved
the move: "Choose kingston or marrakesh; the hardware specs are the same."
The run went to ibm_marrakesh, which shares the Heron r2 156-qubit numbering: star 142,136,143,144 and
137,148,147,146 met calibration exclusions there, and the dry run
2026-10-21T042551.694368Z (record.json sha256
9bc5c743165853b7fa861ff726c63dbc8b8c1c03161a17e8776c4e0f243054c8) pinned
`ibm_marrakesh:57,46,47,48`, spectator 47. Run 2026-10-21T043156.858484Z,
job dbc40u8c77vs7385ee0g, ran 04:33:35Z to 04:34:03Z and billed 18 s.

Marrakesh qubit 47 is another physical qubit: the run is a segmented
Ramsey and Z baseline of qubit 47 and says nothing about the two lines of
fez 143. The alias lattice and prior residues come from 143, so on 47
the alias cell and model decision read a weak second line through priors
built for another qubit.

The bound analyzer could not read any returned run: it validated the herald
prefix with rca.herald_program, which refuses every later-segment herald;
it counted one measure play per readout, while the Heron r2 table plays
four or more per measure and reset; it indexed the four orbit herald roles
with reset-herald keys; and it fixed the spectator at 143. The amended
analyzer reads the barrier stages of the returned table, the spectator
from the run, and every herald through its undetected excitation, and
writes `segmented-sweep-6d59d710eb61.json` beside the record as an
amended analysis. On run 2026-10-21T043156.858484Z all 48 members admit
their schedule (pre-idle 1250 dt on both controls, every idle as
designed) and the heralds admit; Z members leave about twice the reset
excitation of xy members (segment 6: 0.019 against 0.010), which the
design predicts and the herald drops. Amended verdicts on qubit 47:
exchangeable segments (51.5 against 72.1), herald backaction (47.9
against 13.7, a Wald test of each pair's per-shot X and Y means), z_memory (284 against 42), and a line mixture over tls
(239) with a 0.048 second line at alias cell -2 (df -0.735 MHz), T1 81
us and T2* 52 us (`hw-n21-q47-segmented-baseline`).

### ibm_fez qubit 143

ibm_fez fell to 2 pending at 06:36Z; the dry run
2026-10-21T063625.403699Z (record.json sha256
b5cfb7d199dea7f8dcedb99b0ee48b17a1147c1818ee561d9a2d77ac6c6b6b32) pinned
`ibm_fez:142,136,143,144` from main at c062df1. Run
2026-10-21T064222.721454Z, job dbc5u19gv2cc73e9l340, ran 06:43:18Z to
06:43:41Z and billed 16 s.

The preregistered segmented-sweep.json refuses every member: the ibm_fez
table opens with a barrier before INIT, which the bound stage reader kept
as an 842 dt idle ahead of the segment-1 herald. The amended reader starts
the program at INIT and ends it at FINI, and its analysis
(segmented-sweep-6d59d710eb61.json) admits all 48 members (1508 to
1528 kept shots each, dead gaps 1264 dt as designed) and every herald.

| Test | qubit 143 (fez) | qubit 47 (marrakesh) |
|---|---|---|
| segment_exchangeability | exchangeable, 42.2 against 72.1 | exchangeable, 51.5 |
| herald_backaction | none, 3.5 against 13.7 | backaction, 47.9 |
| z_memory | none, 18.3 against 42.3 | memory, 284 |
| model_decision | line mixture, tls worse by 10060 | line mixture, by 239 |
| second-line weight 1 - a | 0.471 | 0.048 |
| alias | cell 0 resolved, next cell worse by 5342 | cell -2 |
| df | -90.2 kHz | -735 kHz |
| switching rate (telegraph) | 0 per us | 0 per us |
| T1, T2* (fit) | 152 us, 138 us | 81 us, 52 us |

Answers. (1) df = -90.2 kHz in alias cell 0, the residue the retained
836 dt sweep left modulo 299.04 kHz, now unaliased. (2) The two lines of
qubit 143 are a classical mixture fixed within each shot: the segments of
a shot correlate as one line, an exchange-coupled TLS is worse by 10060 in
NLL, and the Z arms carry no swap memory; the fitted switching rate is 0,
so the line holds over a shot, 30 to 230 us across the delays. The weights 0.529 / 0.471
differ from the retained sweep's 0.644 / 0.356. A line pair near equal
weight, fixed over a shot and split by tens of kHz, is the signature of
charge-parity splitting; this run measures the mixture and its stability
and leaves the mechanism to a parity-resolved readout. (3) The 1250 dt
pre-idle moves no quadrature, so the herald readout leaves qubit 143's
Ramsey unperturbed, where qubit 47 shows backaction under the same design.

Switching time. Shots run column-wise over the 48 PUBs, so consecutive
shots of one PUB lie one column apart: 8.934 ms by the metered
circuits_execution_time (13.72 s over 1536 shots), 9.656 ms by the single
execution chunk's wall span, whose overhead bounds the period above. Each
shot's six reads label its line by the log-likelihood ratio under the
static fit's two lines, informative at the half-cycle delays 1386, 1638,
4095, 4158 and 6930 dt (df t near an odd half cycle) and empty at the
whole-cycle ones. The labels split into two clusters (the positive
fraction 0.534 matches a = 0.529) and correlate across shots: mean
autocorrelation 0.552, 0.392, 0.281 and 0.198 at lags of 1 to 4 columns, a
two-state telegraph with tau = 26.2 ms at the metered period (moving-block
bootstrap, 64-column blocks, 2.5 to 97.5 percent 19.3 to 30.5 ms; 28.3 ms
at the wall period) and mean dwell 56 and 50 ms in the two lines. A drift
common to both lines would correlate the raw reads where the lines agree:
at the four whole-cycle delays up to 30.5 us the raw lag-1 correlation
stays within 0.034 (standard error 0.026), and at 8316 dt (33 us) the raw
0.090 equals that arm's own label correlation 0.089, the lines' residual
separation there. scripts/n21_q143_line_switching.py writes
line-switching.json beside the run (gate core-617,
`hw-n21-q143-segmented-lines`). The correlation across 8.9 ms also means
the per-shot Wald statistics above treat correlated shots as independent:
the non-rejections and the model and alias margins survive that, while a
rejection near its threshold would not.

## Failure modes

- Segment correlation the model omits: the analysis treats segments of a
  tls shot as independent; a TLS coherence carried across a reset would
  correlate them weakly. Exchangeability and z_memory read it.
- Reset failure or leakage: a failed reset reads 1 at the 143 herald and
  the segment drops; |2> reads 1 and drops the same way.
- Herald backaction: the 1250 dt controls; a backaction verdict marks the
  short-delay points as perturbed.
- Neighbor excitation within the shot: only segment 1 heralds 136, 142
  and 144; an excitation arising later in a shot shifts 143 by its ZZ
  undetected. The retained run's control-only and all-zero selections
  agreed within 0.002.
- 1305 ceiling cancellation: 30 s against about 16 s expected.
- Calibration drift between plan and execution: live_run rechecks the
  calibration fingerprint at the batch and refuses on a changed value.
