# Unapproved QPU case: qet-ladder on ibm_kingston

Status: UNAPPROVED. This record is a submit-free dry run. Writing the case authorizes nothing and submits no job.

## Binding

- [record.json](record.json) SHA-256 `9c6a0413394baef52d57dbf512aed0d891390a9e50294b7a21e519d513b00e0e`;
  [isa.qpy](isa.qpy) SHA-256 `fb38fa9748d351888d6c14d52131b84c8d82c8d0d5e9bff2aaed2d5c659a9bdb`.
- Experiment digest `d43d66466a71bd546459c48cd259db7dd14f36cfe775a4f0143277480010c00f`; source commit `0c1baec`,
  sources unmodified; qiskit 2.6.0, qiskit-ibm-runtime 0.50.0.
- Account `backup-ibm-quantum-platform` (`GOROROBA_IBM_ACCOUNT`), with 560 of 600 s remaining at 2026-10-25T20:17Z. The
  primary account's 117 s minus the 60 s reserve falls below the 60 s ceiling.

## What it measures

The ladder of [pais-claims-falsification.md](../../../docs/notes/topics/pais-claims-falsification.md#falsification-experiments)
runs 18 dynamic circuits of `gororoba_quantum/qet_ladder.py` on qubits 149 (Alice) and 150 (Bob). Their calibration
reads T1 = 350 and 284 us and readout errors of 0.40 and 0.66 percent. Every arm measures X_A mid-circuit and branches
on the bit (idle branches are a 16 dt delay, equal to the two-sx rotation branches), then reads A again and reads B
in the arm's basis. The run makes one dynamic job of 18 PUBs at 8192 shots each, with twirling and dynamical
decoupling off.

Preregistered endpoints and decision rules (one-sided, 95 percent):

1. The channel floor margin `-<H_A> - L_fb` on the ground state is positive: the record-steered rotation lowers Bob's
   local energy below the value that every record-independent operation is bound by. A margin at or below zero, with
   the fixed arms at their predicted values, falsifies the device's feed-forward channel for this protocol.
2. The product-state margin is negative, and the drop between the two margins is positive (the mutation test).
3. `q_eff` lies below the 0.2566 zero crossing. Its value measures whether the branch executes the rotation the
   recorded bit selects, the channel the N = 21 Kingston feedback null left unresolved.
4. Every record-independent arm's L stays at or above the measured `-<H_A>` within its interval. A violation
   falsifies the state description of the readout.

## Why simulation cannot answer it

The ideal and calibration-noise laws are computed here. What they cannot supply is whether measure-and-feed-forward
on this stack executes the selected branch on the shot that produced the bit. The N = 21 encoded feedback contrast
read +0.0027 against a predicted +0.0344 on Kingston, and its three candidate causes are readout assignment, latency
idle and branch dephasing, all properties of the device. This two-qubit circuit isolates that channel with one CZ.

## Prediction (calibration-noise Aer model in the record)

| Endpoint | Ideal | Noise model |
|---|---|---|
| channel floor margin | 0.1147 | 0.0698 |
| product-state margin | -0.2473 | -0.2999 |
| margin drop (mutation) | 0.3620 | 0.3696 |
| information excess | 0.1147 | 0.1376 (inflated by relaxation) |
| contrast | 0.2236 | 0.2307 |
| q_eff | 0 | -0.066 (model sampling noise) |

At 8192 shots the margin's standard error is about 0.023, which puts the noise-model margin at about 3.0 sigma, a
power near 0.91 for rule 1 at the one-sided 95 percent level.

## Cost

147,456 shots at the 250 us repetition delay plus a 4.5 us schedule, about 37.5 s, plus about 2.3 s of job overhead:
roughly 40 s expected, with a 60 s ceiling.

## Submit command (after approval)

```sh
cd gororoba_quantum
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
"$PYTHON" live_run.py --groups qet_ladder --backends ibm_kingston --exclude-qubits ibm_kingston:0-148,151-155 \
  --shots 8192 --max-replicas 1 --no-isolated-reference --max-execution-seconds 60 \
  --max-total-execution-seconds 60 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live \
  --approved-record ../results/live/2026-10-25T201449.111343Z \
  --approved-record-sha256 9c6a0413394baef52d57dbf512aed0d891390a9e50294b7a21e519d513b00e0e --submit
```
