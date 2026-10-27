# Case: q147's persistent excitation, a two-read control on 147-148-149 and 141-142-143

Status: draft awaiting the owner's approval. No submission has been made. The plan record is
[primorial-q147-persistent-excitation](../../docs/state/plans/primorial-q147-persistent-excitation.json).

## The finding this case follows

[PRIMORIAL_COHERENCE_CASE_3.md](PRIMORIAL_COHERENCE_CASE_3.md) measured, on the backup instance at a 20 us
repetition delay, q147's preparation excess and its shot history
([case3/README.md](../../docs/evidence/primorial_cover/case3/README.md), "q147's shot history"):

- q147 reads excited in 0.08 percent of prep0 shots and 4.89 percent of x_history shots, so a |1> left by the
  previous shot survives the 20 us delay in about one shot of twenty.
- In the stage-2 job, `g88_readout_0`, which prepares every path in |000> as prep0 does, reads q147 excited in
  0.0675 +- 0.0040 of 4000 shots. Any law that scales the excess with q147's own end-state history tops out at
  0.0518 at the calibrated |1> read efficiency (3.97 standard errors below the reading) and at 0.0587 at the
  in-job efficiency (2.21 standard errors below).
- The link runs forward in time through the readout event. Each |1>-prepared arm that reads q147 as 0 is followed,
  in submitted order, by a |0>-prepared arm that reads q147 excited more often (0.095 against 0.051, z -4.62, and
  two further arms at z -2.31 and -2.46); the arm after that shows no link. In the x_history jobs, a shot read as
  1 and sent to |0> by its X leaves most of the next shot's excess in place (0.039 and 0.036 against 0.049 and
  0.050), where a carried population predicts about 98 percent of it removed.
- q142, uncoupled to q147, reads 0.085 in the same stage-2 arm against 0.027 in both of its controls.

Case 3 read the excess as a population through lambda 0.66 +- 0.25, and its post-hoc analysis rejects the
mechanism that reading assumes. Two readings remain: a population present when the circuit starts, raised by the
previous circuit's readout event rather than by its end state, or a misassignment of q147's readout that the
in-job assignment inversion absorbs. Case 3's one-read arms cannot tell them apart.

## What it measures and why simulation cannot answer it

A measurement projects the qubit onto the state it reads, up to misassignment. A second measurement right after the
first therefore reads 1 again when the first read found a population, with probability 1 - e01 less the T1 decay
over one measurement, and reads the prepared |0> when the first read was a misassignment. The persistence
pi = P(second read 1 | first read 1) of an initialize-measure-measure arm separates the two readings, and the
same arm after an X separates, among the |1> shots the first read calls 0, those that kept their population
(the second read recovers them) from those that lost it before the first read.

The backend reports neither the per-qubit preparation channel nor the dependence of a readout on the previous
circuit's readout event. The calibration noise model starts every qubit in |0> and misassigns each read
independently, so it predicts pi = e10 on every |0> arm and no link between circuits; the dry run below prices
both arms at the readout error alone. Only the device answers the question.

## Design

The state-prep-control family gains two static arms (`diagnostic_experiments.STATE_PREP_ARM_STEPS`):
`x_remeasure` (x, measure, measure) and `remeasure` (init, measure, measure), each on a two-bit register, bit 0
the first read and bit 1 the second. The run selects `prep0,x_remeasure,remeasure`: three static PUBs in one job,
in that row order, each measuring every named qubit in the same shots. The service runs every circuit of shot s
in row order before shot s + 1 ([repetition-rate-execution](../../docs/notes/ibm_quantum/repetition-rate-execution.md);
case 3 read the forward link in submitted order), so

- each `remeasure` shot follows the same shot's `x_remeasure` read, the |1> readout event the stage-2 link
  conditions on, with the 20 us repetition delay between them;
- each `prep0` shot follows the previous shot's `remeasure` read, a |0> readout event, the control's history;
- the three rows together make the job a |1>, |0>, |0> history, between stage 2's mixed history and the
  single-arm controls.

Qubits: 147, 148, 149, 141, 142, 143, the two case-3 paths that carry the two anomalous qubits and their path
partners as in-job references. Shots 32768 per PUB at a 20 us repetition delay, on ibm_kingston through the
backup account, as the case-3 controls ran. Twirling and dynamical decoupling stay off (the family refuses
both), so the two reads are the device's measurements with nothing between them.

Expected events on q147 at 32768 shots: about 1600 to 2200 first reads of 1 on `remeasure` (0.05 to 0.07 of the
shots, between x_history's and the stage-2 reading), which places pi within +- 0.03 at 99 percent; about 6000
first reads of 0 on `x_remeasure` at stage 2's 0.81 to 0.83 |1> read fraction, or about 250 at the calibrated
e01 of 0.0076.

## Preregistered readings

The analysis is `scripts/remeasure_history.py RUN`, whose docstring fixes the rule; its `--self-test` reproduces a
synthetic run laid out by construction. Per qubit:

1. **Persistence.** pi on `remeasure` with its two-sided 99 percent Clopper-Pearson interval. The reading is
   *population* when the interval lies above 0.5 and *misassignment* when it lies below; otherwise undecided. A
   population on q147 predicts pi near (1 - 0.0076) exp(-2.18 us / 350 us) = 0.986 at the case-3 stage-2
   calibration (`--e01 0.0076 --t1-us 350` prints the value for the calibration in force); a misassignment
   predicts pi near q147's prep0 fraction, below 0.01.
2. **The |1> shots read as 0.** P(second read 1 | first read 0) on `x_remeasure`, under the same rule. Case 3's
   stage-2 |1> arms read q147 as 1 in 0.81 to 0.83 of shots against a calibrated e01 of 0.0076. A population
   reading here says those shots were in |1> and misassigned, a misassignment reading says they had left |1>
   before the first read.
3. **The readout-event link.** P(`remeasure` first read 1 | `x_remeasure` first read 0) against the same given a
   read of 1, as a two-proportion test, with the second read of `x_remeasure` as a second conditioning. The
   readout-event hypothesis predicts the first fraction above the second, as in stage 2 (0.095 against 0.051,
   z -4.62); the end-state hypothesis predicts the opposite order or none. The same conditioning one shot later
   (`remeasure` at shot s against `x_remeasure` at shot s + 1) is the null arm and predicts no link.
4. **The successor.** P(`prep0` at shot s + 1 | `remeasure` reads at shot s), the |0> readout event's effect on
   the next circuit, against prep0's pooled case-3 fraction of 0.0008 on q147.
5. **q142.** The same four readings. The stage-2 excess of 0.085 against controls of 0.027 predicts, under the
   readout-event hypothesis, a `remeasure` first-read fraction above `prep0`'s in the same job.

Items 1 and 2 decide; items 3 to 5 are descriptive with their predictions stated. 148, 149, 141 and 143 are
references: their prep0 fractions in case 3 lie between 0.001 and 0.03, so each gives a few hundred first reads
of 1 at most and its pi carries a wide interval.

## Budget

The dry run below estimates 4.6 s for the one job (three PUBs of 32768 shots at 20 us plus the 2.3 s declared
job overhead), under a 12 s ceiling (`--max-execution-seconds 12 --max-total-execution-seconds 12`). The backup
account reported 197 s remaining at the dry run. The run bills one static job.

## Dry run

Made from the working tree of commit b7ee3e4 with the arm change applied (the record's `sources_modified` is
true; the pull request that carries this case retains the code), at the ibm_kingston calibration of
2026-10-27T12:00:41-07:00:

| record | campaign | PUBs | shots | record.json sha256 |
| --- | --- | ---: | ---: | --- |
| `2026-10-27T191857.888009Z` | state-prep-control prep0, x_remeasure, remeasure on 6 qubits | 3 | 32768 | `914a19475d3304e7851ea3a3347c93a84088d34862e8f8f2fcb96797eb305bc7` |

The simulated summaries read each arm at the readout error alone, as the model predicts: on q147 prep0 0.0022,
the remeasure first read 0.0030 and both reads 0.0, x_remeasure's first read 0.9899 and both reads 0.9820; on
q142 prep0 0.0334, the remeasure first read 0.0334 and both reads 0.0011, x_remeasure 0.9756 and 0.9529.

The binding dry run is the one `approved_run.sh` makes immediately before the submit from the case's commit; its
record and sha256 fill the table below after the submit.

| record | record.json sha256 | submitted run |
| --- | --- | --- |
| | | |

## Commands

From the repository root, with `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` and
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`. The dry run:

```sh
cd gororoba_quantum
"$PYTHON" live_run.py --family state-prep-control --layout 147,148,149,141,142,143 \
  --state-prep-arms prep0,x_remeasure,remeasure --max-replicas 1 --backends ibm_kingston --shots 32768 \
  --rep-delay 2e-05 --max-execution-seconds 12 --max-total-execution-seconds 12 --out ../results/live
```

After approval, the binding dry run and the submit in one invocation; the check requires the fresh plan to hold
the three arms in row order on the six qubits under the approved ceiling:

```sh
sh scripts/approved_run.sh --check '"$PYTHON" -c "
import json, sys
r = json.load(open(sys.argv[1] + \"/record.json\"))
c = r[\"family_configuration\"]
ok = list(c[\"arms\"]) == [\"prep0\", \"x_remeasure\", \"remeasure\"] and c[\"qubits\"] == [147, 148, 149, 141, 142, 143]
ok = ok and [p[\"kind\"] for p in r[\"execution_pubs\"]] == [\"static\"] * 3 and r[\"shots\"] == 32768
ok = ok and r[\"budget_plan\"][\"combined_ceiling_seconds\"] <= 12 and r[\"policy\"][\"twirl\"] is False
sys.exit(0 if ok else 1)
" "$RUN"' -- --family state-prep-control --layout 147,148,149,141,142,143 \
  --state-prep-arms prep0,x_remeasure,remeasure --max-replicas 1 --backends ibm_kingston --shots 32768 \
  --rep-delay 2e-05 --max-execution-seconds 12 --max-total-execution-seconds 12 --out ../results/live
```

Collection, the calibration at the run's execution start (as case 3's stage snapshots), and the preregistered
analysis with q147's e01 and T1 from that snapshot:

```sh
cd gororoba_quantum && "$PYTHON" live_run.py --collect ../results/live/RUN_SUBMITTED
"$PYTHON" calibration_snapshot.py --export ibm_kingston --at EXECUTION_START --out SNAPSHOT && cd ..
"$PYTHON" scripts/remeasure_history.py results/live/RUN_SUBMITTED --e01 E01_Q147 --t1-us T1_Q147_US \
  --out docs/evidence/primorial_cover/case3/remeasure-history.json
```

The results land in a new section of [case3/README.md](../../docs/evidence/primorial_cover/case3/README.md)'s
successor document, the run enters `docs/state/research_state.json`, and the plan record closes on that receipt.
