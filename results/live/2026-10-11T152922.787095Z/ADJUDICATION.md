# Adjudication of the first hardware record

Record `2026-10-11T152922.787095Z`, job `db5qmqclf4us73c4e1ug` on ibm_kingston
(Heron r2, dt = 4 ns), six dynamic PUBs at 4,096 shots. The preregistered
analysis is `collect.json`. This note reads the lossless result under
`raw/db5qmqclf4us73c4e1ug/` (shot-ordered registers, the backend scheduler
table of every PUB, job metrics) through `gororoba_quantum/adjudicate.py`,
whose output `adjudication.json` carries its own analysis digest. Every number
below is in that file unless marked as arithmetic on it.

## What held

- **Hybrid Shor admission.** Factor yield 0.4971 [0.4726, 0.5216] against the
  exact uniform null 0.2969 and the identity null 0.0042 [0.0003, 0.0080]
  (collect.json). The raw registers confirm the pruned structure: only phase
  bits 6 and 7 vary in every replica, the six leading bits read zero in every
  shot, and the null replicas read the zero outcome in 97.2 to 99.0 percent of
  shots against 96.6 to 99.2 percent in the replay.
- **Packing on the same layout.** Packed replica 0 against the reference
  replica 0 on identical physical qubits: hybrid Shor +0.0020, folded QPE
  -0.0037, both inside the 0.03 margin under the preregistered Newcombe
  interval. The backend scheduler tables show the packed PUB executes the
  identical per-qubit instruction sequence as the reference PUB on every
  replica-0 qubit of both groups, with every start time offset by 23 dt
  before the first measurement and by 187 dt after it. Shot-wise correlation
  of correctness between the fifteen replica pairs of the packed PUB stays
  below 0.045 in magnitude (null standard deviation 0.0156): the replicas
  do not share shot-to-shot failures.
- **No drift inside the job.** Correctness per 512-shot block varies within
  sampling error for every replica (folded QPE s1 replica 0: 0.63 to 0.69 at a
  block standard deviation of 0.021).
- **Throughput.** Metrics put circuit execution at 6.7067 s for 24,576 PUB
  shots, 272.9 us per shot. The backend's default repetition delay is 250 us
  and the scheduled circuit durations average 22.9 us (5,727 dt), so the
  per-shot execution time is the repetition delay plus the scheduled
  circuit, with 0.06 us unaccounted. The 9 s charge includes 2.3 s outside
  circuit execution.

## What the preregistered analysis got wrong or could not see

**The folded-QPE gap is in both rounds, and idle dephasing explains a
quarter of it.** Pooled over the four prepared eigenstates and three
replicas:

| view | p_correct | first bit correct | second bit correct given first | round-1 error | round-2 error |
|---|---:|---:|---:|---:|---:|
| hardware | 0.7154 | 0.8990 | 0.7956 | 0.1010 | 0.2044 |
| replay, archived circuit | 0.8988 | 0.9603 | 0.9360 | 0.0397 | 0.0640 |
| replay, schedule-aware | 0.8476 | 0.9555 | 0.8870 | 0.0445 | 0.1130 |

The first bit is measured before any mid-circuit measurement, reset, or
feed-forward, after eigenstate preparation and the controlled multiplication
by 4; hardware makes 2.5 times the replay's error there. The second bit
follows the measurement, the classical round trip, the reset, and the
controlled multiplication by 2; hardware makes 3.2 times the replay's error
there. The schedule-aware replay inserts the idle time the backend scheduler
table shows on every qubit (every instruction of every replica matched its
table instance; 9,939 to 13,426 dt of delay per replica) so the execution-time
model charges T1 and T2 (median 279 us and 213 us over the used qubits) for
the wait. That moves the second-round error from 0.064 to 0.113 and the
first-round error by 0.005, and closes 0.051 of the 0.183 gap in p_correct.
The remaining 0.132 is a gate-level excess present in both rounds at a
similar ratio, which the calibration-derived Pauli model does not carry;
coherent error accumulation in the preparation and controlled multipliers
and measurement-induced dephasing of the work register during the mid-circuit
measurement are the two mechanisms consistent with the split, and only a
matched ladder separates them (HARDWARE_PLAN.md, "Risks").

**The decoder is not the cause.** A swapped bit order would spare the
symmetric labels 00 and 11 and hit 01 and 10; the four labels read 0.735,
0.693, 0.714, and 0.720. The wrong outcomes concentrate on the second bit
flipped (label 0 reads 10 in 0.20 of shots, label 2 reads 00 in 0.20), in
both directions, which is loss of second-round visibility, not a bias.

**Hybrid Shor's factor yield hides the same gap.** The yield counts outcomes
with an odd top pair, which a uniform distribution over the four valid
outcomes and a noisy one both put near 0.5; it agrees with the replay (0.4971
against 0.4955) while the per-replica distance to the replay reaches 0.125.
The raw top-pair distributions show replicas 0 and 1 (qubits 0, 1, 2, 3, 16
and 80, 81, 82, 83, 96) with a biased second bit (0.30 to 0.32 of shots on
the two odd outcomes against 0.19 on the even ones) and replicas 2 to 5
within 0.03 of uniform, as the replay is for all six. A bias is a coherent
error on those layouts, not the randomization the Pauli model draws; the
packing comparison sits on replica 0 and holds there because the packed and
reference copies share the layout and its bias.

**The "36.1 us per feed-forward" claim does not survive.** The wall span of
the execution chunk minus the circuit execution time, divided by the shot
count, is 36.1 us, but that quantity is chunk overhead the metrics do not
attribute to circuits at all. The scheduler tables give the feed-forward
directly: a broadcast of 533 dt (2.13 us) on the reference PUB and 577 dt on
the packed PUB, a receive of 7 dt, so a round trip of 540 to 584 dt (2.16 to
2.34 us); the segment from the first capture to the end of the last reset
on the control qubits spans 1,299 dt (5.2 us) on the reference PUB and 1,463
dt (5.9 us) on the packed PUB, during which the work qubits idle for 1,380 to
2,380 dt.

**The 187 dt packing cost is attributable.** The packed PUB (nine streams)
differs from the reference PUB (two streams) by 23 dt before the first
measurement (alignment across 45 initialized qubits), 44 dt in the broadcast
width (577 against 533 dt for seven more streams), and 120 dt in the stagger
of the resets whose captures share readout channels; the per-qubit offsets in
`adjudication.json` carry the steps. The scheduler residual difference of
148 dt in collect.json is this 187 dt less the 39 dt by which the Target
bounds of the two circuits differ.

**The equivalence verdict for folded QPE depends on the interval.** Under
the distribution-free Hoeffding interval at 90 percent (half-width 0.0270 at
4,096 shots per arm) the folded-QPE difference reads [-0.0306, +0.0234] and
crosses the margin, while hybrid Shor reads [-0.0250, +0.0290] and stays
inside. collect.json reports both views beside the preregistered verdict
from this revision on; the preregistered verdict stands as the Bernoulli
score interval's claim.

## What the program changes because of this

1. Every collection writes the lossless result under raw/ before any
   analysis (live_run.py `write_raw_result`), and `--preserve-raw` recovers
   it for a record collected under an earlier revision, as done here.
2. `adjudicate.py` is the versioned second analysis; its digest is separate
   from the experiment digest that binds the submission.
3. The dynamic-latency item of the roadmap reads the scheduler table rather
   than waiting for a ladder to measure the round trip; the ladder's remaining
   question is the mechanism of the gate-level excess, not the latency.
4. The model-hardware gap, not throughput, is the open question any next
   submission has to be designed around.
