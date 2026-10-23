# Ascella signed-coherence and order conformance

This proposed experiment uses one packed Ascella job to distinguish signed
interference, commuting-generator mutation, analyzer contrast and matched-repeat
stability. The [successful eight-setting acquisition](../../results/quandela/runs/ascella-mosaiq-update-order-retry/README.md)
establishes sampling recovery for its retained request. Its output intensities
cannot distinguish the sign reversal introduced below. Local simulation can
verify the intended operator; only hardware can measure the combined
preparation, compilation, optical mesh and detection response.

This document is a written experiment plan, not an executed case or a frozen
native payload. The plan queues no job. The scope is one optical order/conformance
family; wave evolution and Fourier experiments remain separate. Implementation
must produce and validate the manifest before submission. The user's 1.2-credit
allowance is a ceiling, rather than a spending target.

## Execution envelope and packing

| Quantity | Proposed value |
|---|---:|
| Provider and platform | Quandela Cloud, `qpu:ascella` |
| Jobs | 1 |
| Iterations | 64: eight four-arm blocks in each of two cycles |
| Input | One photon in connected input mode 0 |
| Returned modes | All 12 |
| Logical modes | 0, 1, 2, 3 |
| Representative and compilation seed | 0 and 0, fixed throughout |
| Command | `sample_count` |
| Processing | Explicit empty mitigation list; `min_detected_photons=1` |
| Samples per X/Y signal or null iteration (32 entries) | 12,288 |
| Samples per direct or reference iteration (32 entries) | 4,096 |
| Shot cap per X/Y signal or null iteration | 24,576 |
| Shot cap per direct or reference iteration | 8,192 |
| Maximum total samples | 524,288 |
| Maximum total shots | 1,048,576 |
| Hard execution cap | 300 seconds |
| Recorded-tariff expected charge | 1.024576 credits |
| User-specified credit ceiling | 1.2 credits |

The [billing runbook](../runbooks/quandela-credit-optimization.md) records the
iterated-job rule: one credit plus the shot tariff times the largest iteration's
`max_shots`, not the sum across iterations. Thus the proposed charge is
`1 + 0.000001 * 24576 = 1.024576`. A read-only platform query on 2026-10-23
reported Ascella available, a 300-second maximum and 0.000001 credits/shot.
That response does not expose the per-job charge. The one-credit component
remains a retained-usage assumption that the submission plan must confirm.
Refresh availability, account occupancy, tariff and processor capabilities
immediately before admission; a changed offer requires recalculation within the
ceiling. An account-wide queue confers no cancellation authority over other jobs.

One experiment shares a circuit structure, photon filter and mitigation policy.
The [client runner](../../scripts/qd_platform.py) supports parameterized template
iterations and checks each setting's shot estimate. Its template path currently
uses uniform manifest quotients; heterogeneous budgets are honored only by its
seeded path. The proposed allocation therefore requires a scoped runner extension
covering setting validation, aggregate sum checks, per-setting shot estimates,
serialization, largest-cap pricing and retained-result budget checks. Perceval
1.3.1 `ExecutionFactory.add_iteration` accepts `circuit_params`, `max_samples`
and `max_shots` together. Adding budget fields to template settings alone would
leave the intended allocation unapplied. The builder must place every
operator below on one common parameterized structure; a list of unrelated
circuit objects is not the proposed packing mechanism. The installed Perceval
1.3.1 `ExecutionFactory` appends ordered parameter dictionaries and exposes no
numerical iteration ceiling in that method; that client observation does not
establish an unrestricted service limit.

The retained timing point is 25 seconds for eight settings with 8,192 samples
each. Under the *additional* common affine model
`T=a+h*settings+s*total_samples`, with unchanged nonnegative coefficients, both
setting count and sample total increase eightfold, implying
`T=200-7a <= 200 seconds`. Different mesh-dependent overhead, compilation,
service behavior or acquisition rates can violate the model. Two hundred seconds
is a conditional planning bound, not a measured completion prediction. The
300-second cap leaves model-relative headroom but guarantees neither completion
nor a retained result prefix. Raising every setting to 100,000 samples merely
to approach 1.2 credits would sacrifice completion opportunity without a
measured Ascella throughput model.

## Operator convention and observable

The [operator source](../../gororoba_quantum/hypercomplex_operators.py) defines
`q=z+w*j` and

\[
\chi(a+bi+cj+dk)=\begin{pmatrix}z&w\\-w^*&z^*\end{pmatrix},
\quad z=a+bi,\quad w=c+di.
\]

Use `I=chi(i)`, `J=chi(j)`, `A(theta)=cos(theta)I_2+sin(theta)I` and
`B(phi)=cos(phi)I_2+sin(phi)J`. The order operator is

\[
U(\theta,\phi)=S\,\mathrm{diag}(AB,BA)\,S,
\qquad S=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix}\otimes I_2.
\]

Embed the four-mode operator as `U direct-sum I_8`. The source representative is
`e_0`; do not exchange columns 0 and 1 between cycles. The commuting mutation
replaces `J` with `I` in `B`, keeping both angles at `pi/4` and retaining both
splitter stages. The mutation changes the intended property and the ideal
observable, as required by the [hardware-probe rules](../notes/algebra_circuit_rules.md#hardware-probes).

For representative 0, the ideal four-mode column is

\[
v=(e^{i\theta}\cos\phi,\ -\cos\theta\sin\phi,\ 0,\ i\sin\theta\sin\phi)^T.
\]

At `theta=pi/4, phi=+pi/4` or `-pi/4`, direct probabilities are
`(1/2,1/4,0,1/4)`: direct measurement loses the sign. The original pilot already
contains path recombination; its dark probability
`p_2+p_3=sin(theta)^2 sin(phi)^2` changes from 1/4 to 0 under the commuting
mutation. In contrast, unrecombined `AB e_0` and `BA e_0` have identical
intensities at these angles.

Add an analyzer after `U`, acting on the ordered mode pair `(0,3)` and as
identity elsewhere:

\[
H_X=\frac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix},\qquad
H_Y=\frac1{\sqrt2}\begin{pmatrix}1&-i\\1&i\end{pmatrix}.
\]

The output-0 minus output-3 probability is respectively

\[
X_{03}=2\mathrm{Re}(v_0^*v_3)=\sin^2\theta\sin(2\phi),\qquad
Y_{03}=2\mathrm{Im}(v_0^*v_3)=\tfrac12\sin(2\theta)\sin(2\phi).
\]

These are fixed **complex-encoding** observables. The module header identifies
only sums within adjacent complex-channel pairs as quaternion-ray position
observables. Mixing channels 0 and 3 does not turn `X03` or `Y03` into intrinsic
quaternion-ray positions. The experiment tests an optical implementation of the
complex encoding; it cannot establish fundamental quaternionic quantum mechanics
or refute an already-proved algebraic identity. A compiled whole-unitary result
also does not prove that separate physical devices applied `A` and `B` in a
specified temporal order.

```mermaid
flowchart LR
    A[One photon at input 0] --> B[Order operator or reference preparation]
    B --> C[Identity or X or Y output analyzer]
    C --> D[All twelve returned modes]
    D --> E[Occupation-sum-one denominator]
    E --> F[Balanced contrasts and matched null subtraction]
```

## Exact 64-iteration sequence

Cycle one runs the following blocks in table order. Every block runs arms
`positive, negative, negative, positive`. Cycle two reverses the **block order**,
while preserving that internal arm order and every request parameter. Cycle,
block and arm-position labels identify entries; the physical representative
remains 0. Distinct entry names must not change the requested operator or seed.

| Block name | Positive request | Negative request | Readout |
|---|---|---|---|
| X signal | `U(pi/4,+pi/4)` | `U(pi/4,-pi/4)` | `HX`, output imbalance |
| X null | `U(0,+pi/4)` | `U(0,-pi/4)` | `HX`, output imbalance |
| Y signal | `U(pi/4,+pi/4)` | `U(pi/4,-pi/4)` | `HY`, output imbalance |
| Y null | `U(0,+pi/4)` | `U(0,-pi/4)` | `HY`, output imbalance |
| Direct commutation | Different generators `I,J`, angles `pi/4,pi/4` | Commuting generators `I,I`, same angles | Identity analyzer; modes 2 and 3 |
| Routing reference | Prepare `e_0` | Prepare `e_3` | Identity analyzer; output imbalance |
| X coherent reference | Prepare `(e_0+e_3)/sqrt(2)` | Prepare `(e_0-e_3)/sqrt(2)` | `HX`, output imbalance |
| Y coherent reference | Prepare `(e_0+i e_3)/sqrt(2)` | Prepare `(e_0-i e_3)/sqrt(2)` | `HY`, output imbalance |

Every reference preparation starts from the same physical input `e_0` and
bypasses the order operator through parameter values on the common template.
A builder can use the pair preparation

\[
P(t,\eta)=\begin{pmatrix}\cos t&-e^{-i\eta}\sin t\\
e^{i\eta}\sin t&\cos t\end{pmatrix}_{(0,3)}.
\]

Routing uses `t=0` or `pi/2`, with `eta=0`. X references use `t=pi/4` and
`eta=0,pi`; Y references use `t=pi/4` and `eta=+pi/2,-pi/2`. All remaining
modes receive identity. The builder must validate the entire twelve-mode
operator, not merely reproduce its first-column intensities.

## Denominators and primary endpoints

For iteration `i`, let `N_i` count every reported occupation vector whose
occupation sum is one across all twelve modes. Let `n_im` count its mode `m`.
Use `z_i=(n_i0-n_i3)/N_i` and `p_i=(n_i2+n_i3)/N_i`. Outcomes outside the
selected mode pair contribute zero to the imbalance but remain in its
denominator. Do not condition on the 0/3 pair or on the dark ports. Preserve
vacuum and multiple-occupation exclusions separately. Returned occupations are
reported data, not a measurement of photon-number resolution or physical click
multiplicity; Ascella advertises threshold detectors.

For X/Y, routing and coherent-reference blocks define

\[
C=(z_1-z_2-z_3+z_4)/4.
\]

For direct commutation define

\[
\Delta_{\rm dark}=(p_1-p_2-p_3+p_4)/2.
\]

The different divisor matters: the latter estimates the target-minus-mutation
probability difference, whose ideal value is 1/4. Within each cycle,
`Dx=C_Xsignal-C_Xnull` and `Dy=C_Ysignal-C_Ynull`. Average corresponding
contrasts across cycles for the pooled endpoints. Define `Lmax=max_i l_i`,
where `l_i` is the conditional probability of a reported occupation-sum-one
outcome in modes 4 through 11 in iteration `i`.

| Primary endpoint / question | Ideal prediction | Proposed allowed region |
|---|---:|---|
| `Dx`: does the real signed interference survive null subtraction? | 0.5 | [0.45, 0.55] |
| `Dy`: does the imaginary signed interference survive null subtraction? | 0.5 | [0.45, 0.55] |
| `dark difference`: does commuting mutation change the response? | 0.25 | [0.20, 0.30] |
| `Rx`: does the X coherent reference retain signed contrast? | 1 | [0.95, 1] |
| `Ry`: does the Y coherent reference retain signed contrast? | 1 | [0.95, 1] |
| `Rroute`: do the deterministic routes retain signed contrast? | 1 | [0.95, 1] |
| `Lmax`: does every iteration confine detected outcomes to logical modes? | 0 | [0, 0.01] |
| `Dx cycle difference`: does the matched real contrast remain stable? | 0 | [-0.05, 0.05] |
| `Dy cycle difference`: does the matched imaginary contrast remain stable? | 0 | [-0.05, 0.05] |

The 0.05 engineering margin, 0.01 confinement tolerance and family error budget
0.01 are **proposed design choices**, not vendor specifications or established
performance facts. An interval contained in its allowed region qualifies that
endpoint under the statistical model; an interval disjoint from the region
falsifies tolerance-conformance; overlap is inconclusive. For `Lmax`, upper
bound at most 0.01 qualifies and lower bound above 0.01 falsifies; otherwise the
result is inconclusive. A signed-response interval excluding zero distinguishes
that response from the zero-response alternative, but does not identify which
physical mechanism produced it. Report ideal-model residuals separately from
these engineering decisions.

Use raw reference contrasts as endpoints. Own-axis coherent references qualify
contrast, but their response to a small relative phase error is second order;
they do not identify its sign. Cross-quadrature reference measurements would
be needed for first-order phase calibration. Do not divide science contrasts
by reference contrast without a separately validated joint preparation and
detection model. Such a correction is outside this plan.

## Simultaneous uncertainty

Allocate `alpha_j=0.01/9=1/900` to each of the nine primary endpoints. For a
linear endpoint `Ehat=sum_i c_i Zbar_i`, use the weighted Hoeffding radius

\[
r_j=\sqrt{\tfrac12\log(2/\alpha_j)
\sum_i c_i^2(b_i-a_i)^2/N_i}.
\]

For the independent weighted trial variables, the sum of squared range widths
is `sum_i c_i^2(b_i-a_i)^2/N_i`. The bounded-sum Hoeffding tail
`2 exp(-2 r^2 / squared_width_sum)` gives the stated radius.
The analyzer/routing event variable ranges over `[-1,1]`; the dark event is
Bernoulli in `[0,1]`. At the proposed eligible counts (12,288 for X/Y
signal/null entries and 4,096 for direct/reference entries):

| Endpoint | Coefficients across iterations | Radius |
|---|---|---:|
| Pooled `Dx`, `Dy` | 16 of magnitude 1/8, range width 2 | 0.0174641 |
| Pooled `Rx`, `Ry`, `Rroute` | 8 of magnitude 1/8, range width 2 | 0.0213891 |
| Pooled dark difference | 8 of magnitude 1/4, range width 1 | 0.0213891 |
| `Dx`, `Dy` cycle differences | 16 of magnitude 1/4, range width 2 | 0.0349282 |

Recompute with actual eligible `N_i`; zero makes the endpoint unavailable.
Intersect intervals with each endpoint's mathematical range. These bounds
assume independent eligible observations and a sampling/stopping mechanism for
which conditioning on `N_i` preserves the stated bounded-observation model.
Hoeffding need not assume identical distributions, but interpretation as a
stationary device response requires stability. `sample_count` contains no
shot-order data with which to establish temporal independence. Preserve
per-iteration and per-cycle estimates and state the assumptions alongside
inference. Endpoint independence is unnecessary for the family union bound.
The tight cycle margin is deliberate: at the nominal denominator, an estimated
cycle difference must be within about 0.01507 of zero for its interval to fit
entirely inside the proposed 0.05 margin.

For confinement, allocate `alpha_i=alpha_L/64=1/57600` to a **two-sided**
Clopper-Pearson interval for each iteration, with tail probability `1/115200`.
For `K_i` outside-subspace events among `N_i` eligible observations:

\[
L_i=\begin{cases}0&K_i=0\\
\operatorname{Beta}^{-1}(\alpha_i/2;K_i,N_i-K_i+1)&K_i>0,
\end{cases}
\]
\[
U_i=\begin{cases}1&K_i=N_i\\
\operatorname{Beta}^{-1}(1-\alpha_i/2;K_i+1,N_i-K_i)&K_i<N_i.
\end{cases}
\]

Use `[max_i L_i, max_i U_i]` for `Lmax`. The implementation source is
[`bdsc.clopper_pearson`](../../gororoba_quantum/bdsc.py), called with
`alpha=1/57600`; its beta quantiles already split the two tails. At zero
outside-subspace events and the smaller nominal `N_i=4096`, the upper bound is
`1-(1/115200)^(1/4096) = 0.0028412745`, approximately 0.2841%.
Binomial coverage assumes identically distributed independent eligible trials
within each iteration; the union bound needs no independence between
iterations. All 64 iteration intervals must exist to qualify uniform
confinement. Conditional outside-subspace probability is not calibrated
absolute loss or transmission efficiency.

## Coherent-error model and identifiability

The following derivatives describe a restricted nuisance model, not every
phase error in the compiled physical mesh. Replace the ideal path splitter by
`S(a)=[[cos a,sin a],[sin a,-cos a]] tensor I_2`, with `a=pi/4`.
For analyzer axes use

\[
M(\beta,\delta)=\cos\beta Z_{03}+\sin\beta
(\cos\delta X_{03}+\sin\delta Y_{03}),
\]

where X uses `(beta,delta)=(pi/2,0)` and Y uses `(pi/2,pi/2)`.
All offsets below are common across both signs and signal/null requests;
angle derivatives have units per radian.

| Perturbation | Derivative of `(Dx,Dy)` at the ideal point |
|---|---|
| Additive theta offset, including nominal-zero null settings | `(1,-1)` |
| Additive phi offset | `(0,0)` |
| Input path splitter angle offset | `(-1/2,-1/2)` |
| Output path recombiner angle offset | `(1/2,1/2)` |
| Relative state phase `v3 -> exp(i epsilon) v3` | `(-1/2,1/2)` |
| Analyzer polar tilt around balanced beta | `(0,0)` |
| Analyzer azimuth offset | `(1/2,-1/2)` |

These analytic derivatives were checked by central differences of the stated
operators during design; implementation must retain an executable check with
its numerical step and tolerance. The nonzero entries show why null
subtraction does not cancel every coherent error. Relative state phase and
analyzer azimuth remain confounded. Errors that differ by sign, block,
preparation or physical compilation can introduce further terms. Enumerate
and audit the implemented circuit's relevant perturbations before assigning
mechanistic explanations to a measured residual.

The `+,-,-,+` weights cancel an additive affine trend in equally spaced
**iteration index** within a block. They do not guarantee cancellation of
physical-time drift when durations differ, or nonlinear drift, predecessor
memory or sign-dependent compilation errors. Reversed block order supplies
matched-request diagnostics, not causal isolation of carryover. Returned
compiled meshes can distinguish requested/compiled discrepancies from measured
ones, but metadata does not prove physically applied controls.

## Admission, completion and interpretation

The complete inferential analysis requires all 64 attributable iteration
echoes in the contracted order, matching settings, budgets and processing.
Repeated identical entries cannot independently prove execution order: order
interpretation relies on the service's ordered iterator contract. Returned
array position alone is insufficient when errors or omissions leave identity
ambiguous. Validate full echoed parameters and any available execution metadata.

The [result parser](../../scripts/qd_platform.py) preserves partial/error
answers, and the [execution reference](../notes/quandela/perceval/reference/runtime/execution.md)
allows partial-result retrieval. Neither establishes that a timeout preserves
a completed prefix. The parser explicitly treats absent entries without
positions as unattributed. Retain partial raw evidence and descriptive counts,
but perform no inferential partial-job qualification in this design. Any
missing, malformed, zero-eligible or unattributable iteration makes all nine
complete-job decisions unavailable. Do not replace missing arms, automatically
retry, or reassign a successful entry to a failed position.

Implementation, before any actual submission, must:

1. Extend and validate heterogeneous template budgets end to end, including
   unchanged uniform-budget behavior. Generate one common twelve-mode template and the exact 64-entry sequence,
   with immutable manifest, circuit and serialized-request hashes.
2. Validate each full unitary and its source column against the formulas;
   check analyzer signs, coherent-reference preparations, direct sign-blindness,
   commuting mutation sensitivity and the stated phase response locally.
3. Validate the coherent-error Jacobian and identify residual nuisance
   assumptions; preserve the distinction between an optical operator and a
   physical sequence of separate gates.
4. Exercise serialization and local SLOS/Naive execution on the actual
   request, using the [serialized-request replay](../../results/local-simulation/ascella-serialized-order-replay/README.md)
   as a mechanism reference. Local evidence remains simulation.
5. Refresh processor, command, processing, occupancy, tariff and duration
   records; require every setting's shot estimate to fit its cap and verify
   full-output return behavior and explicit mitigation serialization.
6. Freeze endpoint definitions, multiplicity allocation, tolerances,
   denominators and missing-result rules; validate the readout on synthetic
   signed, commuting, leakage and incomplete-result counterexamples.
7. Present the generated case and its fresh preflight under the applicable
   [evidence-closure procedure](../runbooks/evidence-closure.md) before submission.
   This plan supplies neither a frozen native request nor a claim that such a
   request has passed admission.

The finite scope is one supported input, one representative, selected four-mode
complex-encoding observables, twelve returned modes and two cycles. The job is
not six-source qualification, full twelve-mode process tomography, independent
phase reconstruction, calibrated absolute loss measurement or a foundational
quantum-mechanics test. The [library inventory](../state/hypercomplex-libraries/libraries.md)
provides qualified tools, not a requirement to execute unrelated distributions.
Perceval/exqalibur, NumPy/SciPy and exact or high-precision algebra checks serve
specific implementation checks; library count is not scientific coverage.
