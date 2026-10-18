# Tuna-17 run design: platform configuration and the packed box-kite follow series

A Tuna-17 batch costs the account about three minutes of wall time no
matter what it holds: 120 s of enforced pause, a few seconds of fixed cost per
job, collection and checks. The scarce resource is circuits per batch (three)
and batches per hour, not shots. This note records what the platform
documentation, the API and the retained runs establish about that cost, and
how the box-kite follow series (`scripts/box_kite_cases.py`, `FOLLOW_PLAN`)
spends it. `docs/evidence/box_kite_follow_design/design.json` recomputes every
measured number below from retained records (`scripts/box_kite_follow_design.py`,
gates core-439 and core-440).

## Platform configuration

| Fact | Consequence for a case | Source |
|---|---|---|
| Tuna-17's default compiler passes are SWAP2CZDecomposer then CZDecomposer; mapping, routing and optimization are empty | the gate list runs in the order and on the qubits written; adjacent self-inverse pairs execute | catalogue `default_compiler_config`; `docs/evidence/quantum_inspire/toolchain_check.json` preserves the gate and control sequence of every follow and twin circuit |
| The control stack schedules as late as possible after decomposition; `barrier` and `wait(n)` (20 ns cycles) are the only timing controls | one-qubit gates slide late and line up across qubits; a barrier run fixes an order | [Tuna page](site/kbase_tuna-operational-specifics.md); `scripts/qi_toolchain_check.py` docstring |
| Native: Rx, Ry, Rz, X90, Y90, mX90, mY90, X, Y, Z, I, S, Sdag, T, Tdag, CZ; H, CNOT, SWAP, CR, CRk are decomposed | H costs more than one instruction; its decomposition is not published | Tuna page |
| A job submits `number_of_shots` and `raw_data_enabled` only; `compile_stage` labels a file and changes nothing | no repetition-delay, initialization-time or active-reset option exists; `reset` is measure and flip | `docs/notes/quantum_inspire/api` OpenAPI `JobIn`, `FileIn` |
| `raw_data_enabled` returns one bit string per shot; `qi_platform.py` always requests it and retains `raw/` | per-shot data are available; whether their order is temporal is untested | catalogue `supports_raw_data`; `scripts/qi_platform.py` |
| At most 3 jobs queued on a hardware backend, abuse removes the account; "avoid unnecessary loss of processor hours" | the repository submits 3 circuits per batch, one batch at a time, 120 s apart | [FAQ](site/faq.md); terms |
| The platform publishes no calibration data | the account's own readout pairs, coupler-ZZ map and T0 ladder are the device model | `docs/notes/quantum_inspire/tuna-17.md` |

## Measured constraints

**Shot cost.** Over the 126 completed Tuna-17 jobs retained (4096, 8192 and
16384 shots), execution time fits 2.92 +- 0.46 s per job plus 0.509 +- 0.032
ms per shot (residual 1.2 s): the 500 us initialization dominates, so a
16384-shot job takes about 11 s and the 21-job follow series about 238 s.
The fit also carries 0.92 +- 0.38 us per CZ line per shot, against the
documented 60 ns: a 2.4-sigma term with no known mechanism, which may be
control-stack time rather than qubit time. The fit over the 105 jobs before
the follow series predicted 233.6 s for it; its 21 jobs executed in 243.3 s,
4% more, about two residual standard deviations of a 21-job sum.

**Readout drift.** Across the three T0 batches (15:41Z to 15:48Z), e01 and
e10 of the six LCU qubits moved by at most 0.0071 (q13, |1> misassignment);
most per-qubit homogeneity chi-squares sit at their two degrees of freedom.
A readout pair in every batch therefore buys little: readout pairs at the
start, middle and end of the series bracket every witness within one batch,
and `BRACKET_DRIFT_MAX` = 0.02, about three times the observed spread, stops
the series. Differences of two replicas on one qubit in one batch, such as
the twist test, carry no readout correction to first order.

**Simultaneous pairs.** The admitted coupling graph (TUNA17 without q0, q5,
q6, q7, q9 and q15) has 10 couplers; its largest induced matching has 3
couplers and there are 5 of them, `LCU_PAIRS` among them. Re-admitting q0,
q9 and q15, whose readout recovered, raises the count of maximum matchings
but not their size, so three LCU replicas per circuit is the device's limit
under the no-shared-coupler rule.

**Walk placement.** A star walk (control plus three data) and a path walk
(control plus two) fit in one circuit without a shared qubit or coupler in 12
ways, all of them star 14 with path 4. Under the coherent ZZ model of the
design record, the data order (11, 12, 16) on star 14 keeps |<X_c>| at 0.947
with a 0.8 us CZ window, against 0.751 to 0.889 for the other orders; the
60 ns window gives at least 0.995 for every order. Path 4 with data (1, 2)
keeps 0.978. Static ZZ costs under one percent at the documented CZ time, so
placement matters only if the CZ window is long.

**Phase scale.** With the targets' Ramsey detunings of 2026-10-16
(coupler-ZZ map), the walk control's phase about omega is -7 to -8 degrees
for a 60 ns CZ window and -54 (star) to -63 (path) degrees for a 0.8 us
window. Detunings drift between days and each CZ adds its residual local
phase on top, so these numbers set the scale the phase readouts resolve
(about 0.5 degree at 16384 shots), not a prediction, and a measured phase
alone does not identify the CZ window.

## The follow series

Seven batches, 21 jobs, 16384 shots each:

| Batch | Circuits | What they measure |
|---|---|---|
| 0 | readout-0, readout-1, walk-omit | readout bracket; both omit-last controls |
| 1 | lcu-bright-x-1, lcu-bright-x-2, depth-9-x | bright crossover in X; bright edge at CZ depth 9 on all pairs, X |
| 2 | lcu-bright-y-1, lcu-bright-y-2, depth-9-y | the same in Y |
| 3 | readout-0, readout-1, walk-x | readout bracket; both walk signs (star 14: 6 CZ, path 4: 4 CZ) |
| 4 | walk-y, lcu-dark-x-1, lcu-dark-x-2 | both walks read in Y; dark crossover and strut in X |
| 5 | lcu-dark-y-1, lcu-dark-y-2, depth-5-x | dark crossover and strut in Y; depth 5, X |
| 6 | depth-5-y, readout-0, readout-1 | depth 5, Y; readout bracket |

The X and Y circuits that one Bloch vector combines run in one batch or in
consecutive ones, and walk-x and walk-y run as consecutive jobs, so a phase
drift between the two quadratures has one pause, about two minutes, to act
in; `validate_series` refuses a plan whose pair lies more than
`QUADRATURE_SPAN` = 1 batch apart. The ladder slopes rest on depths 1 and 9
(an unweighted fit on 1, 5, 9 gives depth 5 zero weight), and those two
share a batch in each setting.

- **Crossover.** In each lcu circuit pair, the edge (1,10)(4,15) of kite 3
  at y_sign y and its twist (4,10)(1,15) of kite 6 at -y trade the pairs
  (1, 4) and (10, 13). The average of the two same-pair differences cancels
  both the pair offset and the circuit offset, so twist equality is tested
  at shot noise, without the 0.1007 pair allowance T0 imposed. The edge and
  the twist differ only in local Z, S and Sdag gates, which Tuna executes
  as written, so a nonzero difference measures a gate-dependent error.
- **Two observables per replica.** A setting on the data qubit leaves the
  selector marginal unchanged, so every lcu replica gives the T1
  classification statistic and a conditional coherence. Bright rows populate
  the a = 0 branch (census E_0 = -1 in X), dark rows the a = 1 branch
  (E_1 = +1), the strut both (0); Y reads the imaginary part, 0 for every row.
- **Coherence depth ladder.** The bright edge at CZ depths 1, 5 and 9 in X
  and Y on all three pairs gives magnitude and phase against depth beside the
  population of the same replicas. The joint coherence Pc(n) m(n) and the
  population contrast 2 Pc(n) - 1 both decay as lambda^n under a global
  depolarizing channel, while the conditional magnitude m(n) alone decays as
  lambda^n / Pc(n); their rate ratio r_coh / r_pop separates dephasing
  (below 1) from depolarizing error. The phase slope per CZ is the data
  qubit's detuning phase over one CZ window plus the CZ's residual local
  phase; the fit unwraps the phase along depth, so it identifies a slope
  below pi / 4 rad per CZ in magnitude, since adjacent depths lie four CZs
  apart.
- **Walks.** walk-x reads the associator signs, walk-omit the branch-marked
  controls, walk-y the control's imaginary part; with walk-x it gives the
  control's phase and the coherence magnitude that T0's r cross-predicts.

Against the plan it replaces (T1, coherence and walk stages: 7 batches of one
witness and a readout pair, 7 witnesses with 18 replicas at 4096 shots), the
follow series runs in the same 7 batches with 15 witnesses and 42 replicas at
16384 shots. It adds the allowance-free twist test, both-branch Bloch
vectors, the coherence ladder and the walk phase, and cost 243 s of
execution.

## Libraries

- numpy carries the design model (state vectors of at most four qubits under
  diagonal ZZ and detuning phases), the timing least squares and the
  analysis bootstraps, batched over draws.
- Qiskit builds and state-vector-checks every emitted circuit; libqasm and
  OpenSquirrel replay the platform's parse and compile passes
  (`qi_toolchain_check.py`); qxelarator runs the identical bytes locally
  before any QX or Tuna submission.
- Enumeration with itertools is exact and immediate at this graph size (11
  admitted qubits, 10 couplers), so no graph library enters the design; the
  placement scores run through `parallel.ordered_map`.
- stim models Pauli channels and cannot carry the coherent ZZ and detuning
  phases the design turns on. mthree's independent calibration equals the
  per-qubit tensor inversion at two qubits per replica. The follow run shows
  a context-dependent readout error on q13 (Results below), which a
  calibration taken in the all-excited readout-1 state cannot carry, whatever
  the inversion. quimb and cotengra pay off far above seven active
  qubits. pyzx and other optimizers would cancel the local-phase pairs whose
  cost the twist test measures. galois has no GF(2) synthesis to do: the
  walks are fixed CNOT sequences from the census.

## Results, 2026-10-17

The series ran from 23:08Z to 23:29Z, after its five QX twin batches read
every deterministic replica exactly; every batch passed its checks, the
brackets moved at most 0.0076, and the verdict is continue with no stop and
no refutation (`results/quantum_inspire/box_kite_tuna_17_follow_analysis.json`,
gate core-425; claims `qi-tuna17-boxkite-follow-crossover` and
`qi-tuna17-boxkite-follow-ladder-drift`).

- Classification: all six rows, |D| 0.916 to 0.967, the strut D = 0.001.
- Twist equality in all four block x setting crossovers: |Delta| at most
  0.0040, |z| at most 2.44, with no pair allowance.
- Coherence: every depth-1 X sign as the census states; Y components at most
  0.052 in magnitude; strut branches inside 0.1 + 3 sigma, the largest
  +0.135 against 0.136.
- Walks: <X_c> = -0.784 (star) and -0.937 (path) with omega's sign,
  magnitudes 0.819 and 0.938 inside 0.10 of r^n_CZ, phases 0.297 and 0.052
  rad about omega; the path omit control reads -0.119 against a limit of
  0.126.
- The X and Y replicas of a depth-9 bright edge, which sit in consecutive
  batches and share the selector marginal, differ by 0.024 to 0.033 on all
  three pairs, 4 to 7 shot-noise sigma: deep-circuit populations scatter by
  about 0.03 between batches. The ladder's reported intervals carry shot
  noise only, so r_coh / r_pop = 1.040 and 1.047 on (1,4) and (10,13) and
  the (12,14) depth-9 population 0.483 are not established; depths 1 and 9
  in X share batch-01, which a within-batch ladder can use.
- Against T0, seven and a half hours earlier, the
  bright-edge populations fell by 0.209 on (12,14) at depth 9 and by 0.106
  on (10,13) at depth 5.
- q13: the readout-1 bracket gives e10 = 0.091, and the bright (10,13)
  coherence's raw -0.911 corrects to -1.105; on the dark branch, where e01
  enters, raw 0.942 corrects to 0.990. The all-qubit bracket overstates
  q13's |1> misassignment in the witness context, through neighbor-dependent
  readout or through readout-1's own X on q13.

## Open questions

- Readout context: a bracket with only the witness's qubits excited, beside
  the all-qubit pair, would separate neighbor-dependent readout on q13 from
  a preparation error of readout-1's X.
- The raw shot order: a run with a deliberate mid-job change would show
  whether the retained list is temporal, which would let drift be tracked
  within a job.
- The per-CZ time term and the decomposition of H: an A/B of H against
  Y90 then X on one replica would price the decomposed gate, and a ladder of
  `wait` cycles beside the CZ ladder would separate the detuning phase from
  the CZ's residual phase.
- Measuring a subset of the register: every retained Tuna-17 circuit
  measures all qubits.
- The MCP server lacks the queue read restricted to the account, batch-level
  status and completed-job logs (`scripts/qi_mcp_server.py`).
