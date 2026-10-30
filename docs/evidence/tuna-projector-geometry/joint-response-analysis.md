# Tuna destination controls: exploratory joint response

The complete nominal-one case and the three acquired jobs of the stopped
nominal-zero case each retain ordered 20-bit binary labels. The
[joint-response replay](../../../scripts/qi_tuna_joint_response.py) validates
both frozen case artifacts before reading their six raw lists. Its output is
[the retained joint-response record](joint-response-analysis.json). The replay
uses the declared inverse destination map and verifies that each six-bit
joint table projects onto all three previously validated early/terminal
four-cell tables. The joint analysis was chosen after acquisition.

## Joint quantities

Let `X` contain early labels for physical qubits 4, 11, 6 and their terminal
labels in that order. Bit zero is early 4. Each job has 4096 shots and a
64-cell joint histogram. For a mask `s` from 1 to 63, the parity observable
is `(-1)^popcount(s & X)`. Its response contrast is the rotated average minus
the arithmetic average of the two baseline averages; the endpoint contrast
is after minus before. The all-zero mask is constant and excluded from
inference. This fixed family covers all interactions among these six labels.
The six tables retain joint counts, all parity numerators and all eight joint
patterns of early/terminal disagreements.

| Descriptive comparison | Nominal one | Nominal-zero prefix |
|---|---:|---:|
| Maximum absolute empirical parity response | 0.044677734375, mask 54 | 0.963623046875, mask 4 |
| Empirical total variation from averaged baseline | 0.03662109375 | 0.4832763671875 |

Mask 54 includes early and terminal labels of qubits 11 and 6. Its three
nominal-one parity averages are -0.189453125, -0.150390625 and -0.20068359375.
The second line is a descriptive distance between observed histograms. Its
finite-sample bias and uncertainty are not quantified by the parity intervals.
Mask 4 is the early label of qubit 6. Its nominal-zero parity response
corresponds to a +0.4818115234375 early-one frequency contrast. The original
six-job primary case remains `implementation route unavailable`; the prefix is
not an acceptance or a causal comparison.

## Simultaneous post-acquisition bounds

The 63 nonconstant functions and the two contrasts form a fixed family of
126 statistics, defined on the existing six-bit outcome space. Define each
conditional average along the recorded chronological history as in the
[nominal-one contract](destination-one-response-uncertainty.md), replacing its
cell indicator by the selected parity observable in [-1, 1]. The conditional
Hoeffding bound permits arbitrary adapted dependence and requires fixed sample
counts and the declared chronology. The bound is unconditional across repeated
processes; conditioning on a favorable completion can invalidate that reading.
The three response weights are
`-1/(2n)`, `1/n`, `-1/(2n)`, and the two endpoint weights are `-1/n`, `1/n`.
For `n=4096`, the respective sums of squared weights are `3/(2n)` and `2/n`.
The observable's range has length 2. A two-sided union bound over all 126
statistics at alpha 0.01 gives

    response radius = sqrt(3 log(25200) / 4096) <= 0.086155685839
    endpoint radius = sqrt(4 log(25200) / 4096) <= 0.099484016822

The radii are evaluated with 60-digit decimal precision and rounded upward to
12 decimal places. The maximum nominal-one response mask has interval
approximately [-0.04148, 0.13084]. The expanded family therefore does not
establish the nominal-one case's 0.10 tolerance. The interval targets a
realized predictable response average under the recorded-history assumptions;
it is not a stationary population, a causal destination effect or a bound on
an unobserved transient. Neither the frozen primary outcome nor the stopped
case's refusal changes.

## Algebraic interpretation and alternative mechanisms

Let `k = m4 + 2 m11 + 4 m6`, where each `m` is the early XOR terminal
reported label. For the repository's `cd_core` convention, the octonion
associator sign at basis pair `(1,6)` is `(-1)^(m11 + m6)`, exactly the mask-54
parity. The [associator census](../../notes/topics/cd_associator_defect_census.md)
derives the sign; the labels and pair were selected during this exploratory
analysis. A classical encoding gives an algebraic observable; it does not show
that the device implements a non-associative physical process. The small
nominal-zero mask-54 response, 0.02587890625, simultaneously shows that the
chosen compression can miss the much larger early-qubit-6 response.

The [readout diagnosis](readout-cause-diagnosis.md) and
[upstream request](../../notes/quantum_inspire/destination-response-upstream-request.md)
retain the unresolved alternatives: result association, changed acquisition
schedule or threshold, physical readout/context, memory and an intermediate
drift transient. A fixed early-label permutation leaves the terminal margin of
one retained dataset invariant, but it cannot explain the cause of a difference
between separate jobs. Acquisition-index traces, served schedules and
configuration identities and retained IQ can distinguish some alternatives
without another quantum execution. No new provider execution, simulator run or
upstream message is authorized by this descriptive analysis.
