# Exact branch-resolved law of the encoded N=21 feedback pair

`validation.json` pools three Kaggle CPU kernels that sampled the two
dynamic circuits of `results/live/2026-10-17T003834.987727Z/isa.qpy`
(n21_encoded_feedback and n21_encoded_no_feedback, seven active qubits on
ibm_kingston) under the ibm_kingston calibration snapshot
`docs/evidence/calibration/history/ibm_kingston/20261016T1213360700.json`,
with Aer statevector trajectories, seeds 1000, 2000 and 3000 (circuit k takes
seed + k), 196,608 shots per circuit per kernel: 589,824 shots per circuit.

`scripts/n21_exact_model_validation.py --check validation.json` (gate
core-485) recomputes the exact law of each circuit with
`gororoba_quantum/dynamic_density.py` from the same snapshot and ISA, samples
nothing, and applies `n21_exact_planning.validate_exact`: every one of the
eight outcome probabilities within the simultaneous Hoeffding radius at total
tail 1e-3, sqrt(ln(16000) / (2 x 589,824)) = 0.00286, and each arm's signed
score P(01) - P(11) and the endpoint contrast (feedback arm minus control
arm) within their own Bernstein radii, with the variance and range of the
exact law and tail 1e-3 split over the three score checks. The score checks
spend their own 1e-3, so the replay's family-wise false-rejection rate is at
most 2e-3; the planner's in-run check likewise spends simulation_alpha twice.

| Circuit | exact law | pooled frequency | max gap |
| --- | --- | --- | --- |
| n21_encoded_feedback | 0.28338, 0.25129, 0.21857, 0.24676 | 0.28276, 0.25084, 0.21879, 0.24760 | 0.00084 |
| n21_encoded_no_feedback | 0.28333, 0.23586, 0.21866, 0.26216 | 0.28475, 0.23560, 0.21912, 0.26053 | 0.00163 |

| Check | exact | pooled sample | gap | Bernstein radius | z (exact-law sd) |
| --- | --- | --- | --- | --- | --- |
| feedback arm score | 0.00453 | 0.00324 | -0.00128 | 0.00384 | -1.40 |
| control arm score | -0.02630 | -0.02493 | +0.00137 | 0.00384 | +1.49 |
| contrast | 0.03083 | 0.02817 | -0.00265 | 0.00768 | -2.04 |

Every check passes, but both arms shrink toward zero in the sample and the
contrast sits 2.04 standard deviations below the exact value (two-sided
p = 0.041 for one preplanned test). The pool cannot separate a model bias of
about 9 percent of the contrast from sampling noise: the contrast radius is
2.9 times the gap. If the sampled contrast were the model's, shots for the
same power would grow by (0.03083 / 0.02817)^2 = 1.20; at the reference
plan of `gororoba_quantum/N21_USAGE_BUDGET.md` (05:40 Kingston calibration,
R = 2 read through the variance upper confidence limit, alpha 0.049 after
the covariance falsifier's 0.001) that is about 144,353 shots per arm,
97.3 s, above the 95 s job ceiling. A pool about four
times larger would put a bias of this size near four standard deviations; it
has not been sampled. The kernels ran Kaggle's image Python with numpy
2.1.3, qiskit 2.5.2 and qiskit-aer 0.17.2 on four CPUs; the collected runs
are `results/kaggle/2026-10-17T090404Z-gororoba-n21-exact-model-s1000`,
`...T090412Z-...-s2000` and `...T090416Z-...-s3000`. The law is the Aer
noise model's; a hardware discrepancy is outside what this comparison tests.

## Aer density-matrix cross-check

`crosscheck.json` compares `dynamic_density.probabilities` with Aer's own
law on the same restricted circuits and snapshot, computed without sampling
any outcome probability (`scripts/n21_exact_crosscheck.py`, gates core-487
`--check` and core-488 `--self-test`). AerSimulator with
`method="density_matrix"` applies every channel as a superoperator, and a
`save_density_matrix(conditional=True)` before the mid-circuit measure and at
the end returns the exact state behind each recorded-memory key. qiskit-aer
0.17.2 keys a conditional save on `ClassicalRegister::memory_hex`, which
`apply_roerror` overwrites with the readout-flipped value (and writes into
the register `check_conditional` reads), so one key averages both true
outcomes in sampled proportions. The oracle therefore runs twice per circuit,
with qubit 5's readout set to the identity and then to the swap: each key
then names one (true, recorded) branch, and the branch weight is the saved
pre-measurement probability times the noise model's own readout entry.
Terminal measures leave the oracle circuit; the joint diagonal of the end
state over their qubits, through the tensor product of their readout
matrices, gives each branch's recorded tail. Each circuit has four branches;
all four were visited (unvisited weight 0).

| Model | Circuit | max gap per outcome | arm score, Aer | arm score, dynamic_density |
| --- | --- | --- | --- | --- |
| raw | n21_encoded_feedback | 8.1e-10 | 0.004525708506 | 0.004525708478 |
| raw | n21_encoded_no_feedback | 1.06e-9 | -0.026300845739 | -0.026300843774 |
| cleaned | n21_encoded_feedback | 4.2e-16 | 0.004525708506 | 0.004525708506 |
| cleaned | n21_encoded_no_feedback | 1.2e-15 | -0.026300845739 | -0.026300845739 |

The contrast is 0.030826554245 from Aer under either model and
0.030826552251 from dynamic_density under the raw model, a gap of
-2.0e-9; under the cleaned model the two agree to 1.0e-15.

The raw-model gap comes from Aer's noise truncation. qiskit-aer's
`QuantumError::set_circuits` (src/noise/quantum_error.hpp, `threshold_ =
1e-10`) discards every noise circuit of probability at most 1e-10 without
renormalizing; live_run's errors carry such components on q105's single-qubit
gates (1.8e-10 per error) and on cz(q105, q117) (1.6e-10), 6.4e-8 summed
over each circuit. Every noise circuit is trace preserving, so the discarded
part scales every branch by the same factor, which Aer's renormalization at
the measure and at sampling removes: Aer's raw law equals the law of the
cleaned model (those components removed in Python, the rest renormalized) to
5.6e-16. dynamic_density keeps them. The first divergent instruction is
instruction 1 of the restricted feedback circuit (x on restricted qubit 1,
ibm_kingston q105) and instruction 5 of the restricted control (cz on
restricted qubits 1 and 2, q105 and q117), counted in the circuits
`snapshot_laws.restrict_circuit` returns: the normalized states of the two
engines agree to 7e-19 and 6e-17 before it and differ by 1.2e-10 and 8.5e-11
after it. The raw per-outcome gaps lie under the truncation bound
D / (1 - D) = 6.4e-8.

The tolerance, 1e-12, separates the float error of two engines evolving one
channel (at most 1.7e-15 in any normalized branch state, 1.2e-15 in any law
or branch weight) from the smallest effect the comparison resolves, one
truncated component (order 1e-10). On dynamic_density's three-qubit fixture,
which carries no truncated component, the default Semantics matches the
oracle to 1.5e-16 and each of the seven other combinations of body noise,
reset-error order and recorded condition departs by 0.024 to 0.087.

The cross-check settles that dynamic_density computes Aer's density-matrix
law on both circuits to 2e-9 in the contrast, so the contrast's z = -2.04
does not come from its branch semantics: the model gap it would need,
0.00265, is six orders larger. The pool was sampled with Aer statevector
trajectories, a different method on the same channel; the cross-check does
not test that sampler, so the remaining explanations are sampling noise
(p = 0.041 for one preplanned test) or a departure of the trajectory sampler
from its channel, the latter untested.

## Initial excitation

`crosscheck_prep_excitation.json` repeats the comparison with every active
qubit starting in (1 - eps)|0><0| + eps|1><1|, eps = 0.01, the placeholder
preparation excitation of the shorter repetition-delay dry runs
(`scripts/n21_exact_crosscheck.py --prep-excitation 0.01 --out`, gate
core-526 `--check` in normal and optimized Python). Aer receives the channel
as a leading `pauli_error([("X", 0.01), ("I", 0.99)])` instruction on each of
the seven qubits (`dynamic_density.with_prep_excitation`), dynamic_density
as `probabilities(..., prep_excitation=0.01)`, which applies the bit flip to
its initial density matrix; the channel has one implementation in each engine.

| Model | Circuit | max gap per outcome | largest branch-state gap |
| --- | --- | --- | --- |
| raw | n21_encoded_feedback | 8.0e-10 | 3.6e-9 |
| raw | n21_encoded_no_feedback | 1.0e-9 | 3.6e-9 |
| cleaned | n21_encoded_feedback | 6.1e-16 | 1.0e-15 |
| cleaned | n21_encoded_no_feedback | 9.4e-16 | 1.6e-15 |

Under the cleaned model the engines agree within the 1e-12 tolerance at every
save and in the contrast (gap 1.1e-15); under the raw model the gaps stay
under the truncation bound, as at eps = 0. The channel lowers the exact
contrast from 0.030826554245 to 0.029231572435 (shift -0.001595), the
amount by which an unmeasured 1 percent residual excitation per qubit would
shrink the admitted effect.
