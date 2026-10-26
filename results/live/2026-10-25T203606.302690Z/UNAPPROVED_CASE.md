# QPU case: qet-ladder packed across ibm_kingston

This case supersedes [the single-pair case](../2026-10-25T201449.111343Z/UNAPPROVED_CASE.md). The owner approved the
fresh job on 2026-10-25, conditional on a final adversarial review whose findings are resolved here: a primary subset
fixed by calibration alone, no selection on noise-model margins, the |11> readout calibration, and the Target-matched
branch durations of PR #513.

## Binding

- [record.json](record.json) SHA-256 `492796a94b7fefdd59726576b091b0b0b9f44c9e661a97fece4ad413491c1caf`;
  [isa.qpy](isa.qpy) SHA-256 `1a80652b244b94cb575082c84e4ee6a524874a46fc8138ad0098b1707598e710`.
- Experiment digest `9ed053a779f385e424f3f94ff9f59650473e82dd505a9f5bab68b7d65fe59971`; source commit `afd0758`,
  sources unmodified; Kingston calibration 2026-10-25T13:27:48-07:00.
- Account `backup-ibm-quantum-platform`, with 560 of 600 s remaining; the 60 s reserve is held.

## Design

The run is 19 dynamic circuits of `qet_ladder.py`, 8192 shots each, in one job. It packs 14 disjoint replicas: every
pair the placer finds on Kingston after `--exclude-qubits` removes the 79 qubits whose calibrated readout error
exceeds 1 percent. Each replica is (Alice, Bob):

[149, 150], [15, 19], [105, 117], [44, 45], [80, 81], [21, 36], [61, 62], [109, 118], [55, 59], [49, 50],
[140, 141], [77, 85], [91, 98], [79, 93].

Each mid-circuit measurement therefore broadcasts 14 simultaneous captures. Run collection extracts the scheduled
capture-to-receive latency from the retained `scheduler_timing` with `scripts/heron_feedforward_latency.py` and reports
it beside `q_eff`.

## Preregistered endpoints

1. **Primary.** The unweighted mean over the 14 replicas of the per-replica raw `channel_floor_margin`, with a
   t-interval across replicas (13 degrees of freedom). Rule: the one-sided 95 percent lower bound exceeds zero. Readout
   error lowers the raw margin, so a positive bound does not come from readout.
2. **Mutation.** The same mean of `prod_channel_floor_margin` has a one-sided 95 percent upper bound below zero.
3. **Secondary.** The mean `readout_corrected_channel_floor_margin`, which inverts the per-replica assignment
   channels from the |00> floor arm and the |11> calibration. Also the per-replica `information_excess` and `q_eff`,
   which are nonlinear and are reported per replica, never from pooled distributions.
4. **Device map.** Per-replica margins against each pair's calibration.

A primary bound at or below zero, with the fixed arms near their predicted values, falsifies feed-forward execution
of the record-steered rotation at this operating point. A record-independent arm below the measured `-<H_A>` beyond
its interval falsifies the readout's state description.

## Prediction (calibration-noise Aer model, per replica)

| Endpoint | Ideal | Model mean over 14 | Model range |
|---|---|---|---|
| raw channel floor margin | 0.1147 | 0.0568 | 0.0175 to 0.0742 |
| readout-corrected margin | 0.1147 | about 0.10 | 0.0805 to 0.1216 |
| product-state margin | -0.2473 | about -0.28 | -0.3121 to -0.2535 |

Each replica's margin carries about 0.023 of shot noise at 8192 shots, and the model's spread between pairs is about
0.012. The predicted primary interval is therefore about 0.057 +- 0.012 at the one-sided 95 percent level.

## Cost

155,648 shots at the 250 us repetition delay plus a 4.5 us schedule come to about 39.6 s, plus about 2.3 s of job
overhead: roughly 42 s expected, with a 60 s ceiling.

## Submit command

```sh
cd gororoba_quantum
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
"$PYTHON" live_run.py --groups qet_ladder --backends ibm_kingston --exclude-qubits "$(cat EXCLUDE)" \
  --shots 8192 --no-isolated-reference --max-execution-seconds 60 --max-total-execution-seconds 60 \
  --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live \
  --approved-record ../results/live/2026-10-25T203606.302690Z \
  --approved-record-sha256 492796a94b7fefdd59726576b091b0b0b9f44c9e661a97fece4ad413491c1caf --submit
```

`EXCLUDE` is `ibm_kingston:0,2,4,6-8,12,14,16,18,22,24,27,29,31-35,39,43,46-47,51-54,58,60,63,65,67-70,72-73,75-76,78,83,87,90,92,94,96,99-104,107,111-116,119-121,124-125,127,129-133,135,138-139,142-143,145-146,153,155`.
