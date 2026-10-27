# Idle-penalty probe on ibm_kingston: written case

Status: approved by the owner on 2026-10-26 ("this is approved"), after the Codex daybreak-blue review, its fixes and a
final advisor review, for the binding record below. It ran as Kingston job `dbfrg3fpc3tc739o4kag`; the results are in
[IDLE_PENALTY_PROBE_FINDINGS.md](IDLE_PENALTY_PROBE_FINDINGS.md).

## Question

Retained Kingston runs charge idle qubits about three times the relaxation the reported T1 and T2 predict
(kappa about 3 on qubits 73-95, about 1.6 on the encoded N=21 qubits 104-126;
`docs/local/idle-followups/FINDINGS.md` on the build host). Fits to retained runs cannot say why:

- they cannot identify kappa per qubit;
- the calibration reading alone moves kappa between 2.5 and 4;
- they cannot separate three candidates, namely relaxation faster than reported, free-evolution dephasing faster
  than the Hahn-echo T2 IBM reports, and dephasing from readout elsewhere on the chip.

This run measures each candidate directly, per qubit, in one job under one calibration:

- (a) kappa_1 = Gamma_1 T1 on every placed qubit, from a 10/40/100 us relaxation ladder against same-job
  assignment references, normalized to the calibration in force at execution;
- (b) the visibility and phase change of an idling qubit while its partner (and every other replica) reads out,
  against two quiet references in their own PUBs;
- (c) kappa_2* and kappa_2e from Ramsey and Hahn-echo ladders on every placed qubit. IBM reports T2 "from a Hahn
  echo sequence" (`docs/notes/ibm_quantum/qpu-information.md`), and `NoiseModel.from_backend` charges every idle
  that echo T2, so kappa_2* / kappa_2e above 1 is dephasing an undecoupled circuit idle pays and the noise model
  omits;
- (d) a later repeat compared with `scripts/idle_penalty_report.py --compare` tests stability across
  calibrations; this case covers the first run only.

## Why a simulation cannot answer it

Aer's noise model is built from the reported T1, the echo T2 and the assignment errors. It contains no
free-evolution T2*, no readout-induced dephasing and no Stark shift. On the dry run's own predictions the analyzer
returns kappa_1, kappa_2* and kappa_2e within 0.02 of 1, and no readout effect. That is its self-check
(`--self-check`), and it is the null the hardware result is read against.

## Design

The campaign `idle_penalty` (`gororoba_quantum/idle_penalty.py`) has 44 two-qubit members. live_run places them on
31 disjoint coupled pairs (62 qubits). The pairs come from the live calibration's quality policy and layout
score. One wide dynamic circuit per member carries every pair; with `--no-isolated-reference` that makes 44 PUBs
in one job. Every member opens with an active reset of both qubits and a barrier. All arms therefore share one
job and one calibration window, and each preparation is independent of the previous shot at the 20 us delay.

The arms:

- assignment references (ground, excited);
- the relaxation ladder on both qubits;
- Ramsey and echo ladders on each qubit in turn, with its partner in |0>;
- a static-ZZ arm;
- matched readout arms with the partner's 12-read train during or after the idle;
- a short arm with 3 reads in a 10 us idle, which unwraps the 40 us phase beyond its 25 kHz alias.

One CZ phase-kickback member anchors the pair to a coupler. `routed_pair_violations` refuses a placement off a
coupler, and refuses one whose readout train would outlast the idle on the live Target's measure duration.
`--check-placement` confirms on the record that no physical coupler joins two replicas.

## Backend, account, shots and seconds

- Backend: ibm_kingston (Heron r2), pinned. Calibration and placement come from the record of the final dry
  run, made immediately before approval.
- Account: primary (default saved account). Its remaining seconds are 117 at the dry run, against a 60 s
  reserve floor. A usage read precedes the submit.
- Shots: 4096 per PUB, 44 PUBs, one dynamic job; twirling off, dynamical decoupling none, isolated reference off.
  4096 is the optimization: every preregistered band keeps a wide margin at the sqrt(2) larger errors, and the
  halved charge leaves quota for the repeat that question (d) needs.
- Expected charge: Target-duration bound plus the measured scheduler residual of retained dynamic Kingston PUBs
  (2245 to 2447 dt, about 10 us, per `collect.json` `pub_timing` of `2026-10-18T090603.530638Z` and
  `2026-10-25T193443.839527Z`), plus 2.3 s per job. That gives 16.4 s at a 10 us residual and 18.2 s at 20 us.
  The ceiling is 25 s, 1.25 times the high estimate plus rounding.
- Expected credits: none beyond the plan's QPU seconds.

The 20 us delay has completed on Kingston before: `results/live/2026-10-18T214519.655411Z` and
`2026-10-18T220218.089776Z`, 32768 shots each, 3 s billed. The excitation excess there matched 50 us within one
standard error (`results/live/N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md`).

**Fallback rule.** The 50 us record is submitted only if the 20 us job ends with a service error and zero
circuit execution time. That signature belongs to the 0 us failures of
`results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md`. The fallback is this case's design at 50 us with a 30 s
ceiling, from its own dry run against the calibration in force when it is made. The primary's spendable seconds
(117 less the 60 s reserve) cover the 20 us ceiling and the 50 us ceiling together only if the failed job billed
under 2 s. A usage read precedes the fallback.

## Preregistered decisions

The decisions are in the docstring of `scripts/idle_penalty_report.py`, fixed before any hardware data. Two
thresholds moved after the dry-run self-check showed that sampled predictions can read |t| above 3:

- both readout statistics sit at alpha 1e-3, with t quantiles, on pair means (31 units);
- a readout effect must appear against both quiet references with one sign, and the quiet null must not fire;
- dephasing needs a negative mean in every branch.

The decisions:

- kappa_1 "optimistic T1 present" when the median exceeds 1.5 and its band lies above 1;
- quasi-static dephasing "present" when the band of the median kappa_2* / kappa_2e lies above 1;
- readout dephasing and readout shift each "present", "absent" or "unresolved" by the two-reference rule;
- repeat stability "stable", "drifted" or "unresolved" by `--compare`.

Predicted precision at 4096 shots, from the self-check on the binding record (order-statistic 95% intervals):

| Quantity | Self-check value |
|---|---|
| kappa_1 median | 1.006 [0.998, 1.014] |
| kappa_2* median | 0.993 [0.984, 1.011] |
| kappa_2e median | 1.004 [0.993, 1.021] |
| pair-mean visibility difference | standard error about 0.002 |
| pair-mean frequency shift | standard error about 0.014 kHz |

Under the live noise model, the exact branch laws (`dynamic_density.probabilities`) of every readout arm equal
those of its quiet reference to 3e-16 for both roles. The model carries no readout effect, so any measured one
is the device's.

## Binding records

| Field | Value |
|---|---|
| Run directory | `results/live/2026-10-26T202236.647959Z` |
| record.json sha256 | `a343bf3372f21fc7ecf760ff4ad0093a61df744eacae7d060d39e120bcf27ce6` |
| Calibration | 2026-10-26T12:25:31-07:00, fingerprint `a498595454fc0377...` |
| Placement | 31 pairs, checked against a fresh live export: every pair on a coupler, none joining two replicas |
| Policy | 4096 shots, rep_delay 20 us, ceiling 25 s per job and in total, no isolated reference, no DD, no twirl |

If the calibration values move before the submit, the submit writes `approval_required` and sends nothing. The
dry run is then remade with the identical flags and submitted, under the same approval.

## Commands

From `gororoba_quantum/`, with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `PYTHON` exported, and
`D=docs/evidence/anu_qrng/draw-2026-10-26T191135Z.json` (seed values at indices 0 and 1):

```sh
"$PYTHON" live_run.py --groups idle_penalty --backends ibm_kingston --max-pending 300 --shots 4096 \
  --rep-delay 0.00002 --no-isolated-reference --max-execution-seconds 25 --max-total-execution-seconds 25 \
  --seed-transpiler "qrng:$D#0" --seed-simulator "qrng:$D#1" --out ../results/live
"$PYTHON" calibration_snapshot.py --export ibm_kingston --out SNAPSHOT
"$PYTHON" ../scripts/idle_penalty_report.py RUN --self-check --check-placement --snapshot SNAPSHOT
# after approval:
"$PYTHON" live_run.py ... (the same flags) --submit --approved-record RUN --approved-record-sha256 SHA
"$PYTHON" live_run.py --collect RUN_SUBMITTED
"$PYTHON" ../scripts/idle_penalty_report.py RUN_SUBMITTED --out RUN_SUBMITTED/idle-penalty-report.json
```

The fallback replaces `0.00002` by `0.00005` and both ceilings by 30, after its own dry run.
