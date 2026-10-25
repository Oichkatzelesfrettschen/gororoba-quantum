# Heron r2 latency cost of feed-forward logical recovery

This design measures how much logical entanglement fidelity a Heron r2
feed-forward correction loses to the classical controller's latency, against a
Pauli-frame correction that applies the same syndrome in post-processing with
no latency. It supplies the decay rate delta that the latency-constrained
recovery model needs. That model rewards an intervention by exp(-delta T) for
sojourn time T, and nothing in the repository measures delta on an encoded
qubit. The approved run ran on ibm_kingston on 2026-10-25; its result is in
[LATENCY_RECOVERY_FINDINGS.md](../../results/live/LATENCY_RECOVERY_FINDINGS.md).

## Question and why hardware answers it

[feedforward-latency.json](../evidence/heron_platform/feedforward-latency.json)
gives the compiled latency. On ibm_kingston, a broadcast that carries two
captures reaches its `Receive` 208 cycles (832 ns) after capture end. One
carrying a single capture takes 201 cycles on Kingston and ibm_fez.

During that window the data qubits idle while the controller distributes the
outcome. Aer's noise model applies a conditional instantly and dephases an
idle qubit at the calibrated T1 and T2 only. It therefore omits both the
controller window and any dephasing that a neighbor's readout induces.

The spectator Ramsey of qubit 143 showed that the Target model can miss a
device's idle coherence entirely: Aer predicted visibility 0.993 where the
hardware read 0.622 ([N21_SPECTATOR_RAMSEY_CASE.md](../../results/live/N21_SPECTATOR_RAMSEY_CASE.md)).

The retained window sweep (record 2026-10-19T151959.226467Z,
[N21_ORBIT_RCA.md](../../results/live/N21_ORBIT_RCA.md)) found no resolved
cost of 415 and 830 extra dt. It measured an algorithm contrast near 0.15
with standard error 0.008, so it bounds the cost near 5 percent of that
contrast. This run reads a four-qubit entangled block (the reference qubit
and three data qubits), whose phase coherence decays about four times faster
per unit idle than one qubit's. It reads that block at full contrast, not at
0.15.

## Circuit

Six logical qubits: reference `r`, data `d0 d1 d2`, syndrome ancillas
`a0 a1`. Every member runs these steps:

1. Prepare: `H(r)`, `CX(r, d0)`, then encode the bit-flip code with
   `CX(d0, d1)` and `CX(d0, d2)`, giving `(|0>|000> + |1>|111>)/sqrt 2`.
2. Error: the error arms apply `X(d0)`. After the unencoding of step 6, an
   X on d1 or d2 stays on its own qubit and never reaches the observable, so
   d0 is the only location whose error the recovery must undo.
3. Syndrome: `a0 <- d0 xor d1`, `a1 <- d1 xor d2`, then measure both into
   `s`. Barriers bracket the two measurements in every member, so the data
   and reference qubits idle through the readout in every arm.
4. Window: the arm's idle or feed-forward (below).
5. Correction: the feed-forward arms apply `X(d0)` when `s == 0b01`
   (`a0 = 1`, `a1 = 0`). That is a single conditional, so the branch drives
   one qubit.
6. Decode `CX(d0, d2)`, `CX(d0, d1)`, rotate `r` and `d0` into the member's
   Pauli basis, and measure them.

Entanglement fidelity with the ideal Bell state is
`F = (1 + <XX> - <YY> + <ZZ>)/4`. The arms that also read `XY` and `YX`
separate a coherent phase from a decay. The coherence is
`C = sqrt(((<XX> - <YY>)/2)^2 + ((<XY> + <YX>)/2)^2)` and the phase is
`phi = atan2((<XY> + <YX>)/2, (<XX> - <YY>)/2)`. A drop in F with C intact is
a frame error that a virtual Z removes. A drop in C is a decay.

## Arms

`L` is the scheduled feed-forward overhead for the backend: 215 cycles on
ibm_kingston (208 to `Receive` plus its 7). `W` is a 10 us idle, 2500 cycles,
long enough that its T1/T2 cost exceeds the detection radius (Power below),
so the window cost resolves delta.

| Arm | Window after the syndrome barrier | Correction |
|---|---|---|
| `ff_0` | none added | feed-forward `X(d0)` |
| `ff_w` | `delay(W)` on r, d0, d1, d2 | feed-forward `X(d0)` |
| `frame_0` | none | Pauli frame from `s` |
| `frame_l` | `delay(L)` | Pauli frame from `s` |
| `frame_lw` | `delay(L + W)` | Pauli frame from `s` |
| `ff_0_unencoded` | none, steps 1 and 6 skip the encoding | feed-forward `X(d0)` |

The Pauli frame flips the `d0` outcome of the Z and Y bases when `s == 0b01`.
The no-correction null reads the frame members without the flip.

Members:
- the five encoded arms with the `X(d0)` error in `XX YY ZZ XY YX`: 25;
- `ff_0` and `frame_0` without an error in `XX YY ZZ`: 6;
- `ff_0_unencoded` with the error in `XX YY ZZ`: 3.

That is 34 members, all dynamic and in one job. Ideal values, from exact
dynamic simulation:
- every encoded arm, with or without the error: F = 1;
- the no-correction null with the error: F = 0, with `<XX> = 1`,
  `<YY> = 1`, `<ZZ> = -1`;
- `ff_0_unencoded` with the error: F = 1/4.

The unencoded arm is the mutation test. Removing the code removes the
property, and the ideal observable falls from 1 to 1/4. The null arm decides
against F = 0.

## Contracts

Preregistered, family alpha 0.05 split equally over the seven inferential
tests. Aer applies a conditional instantly, so the latency endpoints have no
modeled effect to plan a directional test against. They, and the window costs,
are precision endpoints: the planner prices the interval half-width, and the
analysis applies the rule in the last column to the retained interval.

| Contract | Statistic | Planned as | Decision |
|---|---|---|---|
| `recovery` | F(`ff_0`) - F(null) | one-sided | lower bound above 0.5 |
| `code_property` | F(`ff_0`) - F(`ff_0_unencoded`) | one-sided | lower bound above 0.25 |
| `latency_cost` | F(`frame_0`) - F(`ff_0`) | half-width 0.05 | resolved when the lower bound exceeds 0 |
| `latency_is_idle` | F(`frame_l`) - F(`ff_0`) | half-width 0.05 | holds when the interval lies inside +-0.01; a wider interval is reported as unresolved |
| `window_cost_ff` | F(`ff_0`) - F(`ff_w`) | half-width 0.05 | resolved when the lower bound exceeds 0; divided by W, the decay rate delta |
| `window_cost_frame` | F(`frame_l`) - F(`frame_lw`) | half-width 0.05 | as `window_cost_ff`, through idle alone |
| `window_slope` | `window_cost_ff` - `window_cost_frame` | half-width 0.1 | holds when the interval lies inside +-0.01 |
| `decay_not_phase` | C(`frame_0`) - C(`ff_0`) beside phi(`ff_0`) - phi(`frame_0`) | descriptive | names the loss decay or frame |

A failed `latency_is_idle` with a passing `latency_cost` names a
feed-forward cost beyond the idle. That excess is the device-specific part:
readout-induced dephasing or controller behavior that Aer does not model.

## Power

The planner bounds each endpoint with Hoeffding intervals that hold under
arbitrary dependence within a shot, at alpha/7. At 16384 shots per member a
difference of two arms reaches a half-width near 0.046 and `window_slope`
near 0.095; 8192 shots miss both targets. Normal-theory standard errors,
near 0.005 for a difference at 16384 shots, are reported beside the
preregistered intervals as description.

A submit-free exploration on ibm_kingston (calibration 2026-10-25T12:03:28-07:00,
medians T1 258 us, T2 163 us) predicted under Aer F(`ff_0`) = 0.915, the null
0.014 and the unencoded arm 0.251. It put the T1/T2 cost of the 215-dt idle
`L` at 0.006, below any reachable radius, so `latency_cost` and
`latency_is_idle` resolve only a feed-forward cost well beyond T1 and T2. It
put the window cost at 0.017 for a 526-dt window and 0.081 for 2500 dt; the
second exceeds the 0.046 half-width, which sets `W`.

## Placement and seeds

ibm_kingston carries the two-capture latency the windows assume. Another
backend needs its own `L` and `W` from a retained or dry-run schedule. On
ibm_fez, qubit 143 is excluded: it carries two Ramsey lines
([N21_ORBIT_RCA.md](../../results/live/N21_ORBIT_RCA.md)).

Readout correction is skipped for feed-forward circuits. Every arm's final
measurement is identical, so readout error biases each F alike, and
differences between arms cancel it to first order.

The family draws no randomness of its own: its circuits, frame rule and
contracts are deterministic. Layout search and the planner's model sampling use
the runner's `SEED_TRANSPILER` range and `SEED_SIMULATOR`, the reproduction
identifiers of ci/reproduction_seeds.json that every live_run family plans
with.

## Implementation

Family `latency-recovery` in `gororoba_quantum/diagnostic_experiments.py`,
with its circuit builder, ideal laws, summary (F, C, phi per arm and the
frame-corrected null), `family_contracts`, `record_groups`, the
`qpu_planning.family_candidates` branch, the `qpu_cases` case text and the
`live_run.py` CLI validation. The `state-prep-control` family is the
structural template. Contract tests cover:
- the ideal laws above;
- the frame correction on synthetic distributions;
- the mutation and null arms;
- barrier placement, with no data-qubit gate inside the syndrome window.

The case follows the order of [AGENTS.md](../../AGENTS.md#qpu-time-and-calibration):
dry run, analysis, written case, approval, and only then `--submit`.

## What it cannot show

- The schedule's latency is a plan: the run measures the fidelity cost of
  whatever the controller executes, not the latency's jitter.
- A bit-flip code protects no phase, so the run measures the idle cost of
  coherence, the quantity delta needs, and says nothing about a code that
  also corrects phase.
- One layout and one calibration give one device's number.
