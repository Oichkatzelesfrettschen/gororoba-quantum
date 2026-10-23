# Ascella order amplitudes, coefficient geometry and measured art

The next scientific question is whether Ascella preserves the **signed
commutator amplitude and its interference with the anticommutator**, across a
finite angle family. The completed pilot observes intensities. The follow-up
measures the coherence those intensities leave undetermined, extracts the
predicted harmonic coefficients, and renders their measured geometry.

The plan contains one proposed 64-setting order-family job, a 300-second cap
and a 1.2-credit ceiling. The recorded tariff gives 1.016384 credits. The plan
contains neither a frozen native payload nor a new submission. Wave evolution
and Fourier families retain separate cases. The science-led design replaces
the fixed-angle reference-and-repeat design in this document's Git history;
all settings now probe the order mathematics, its sign symmetry or its
commuting mutation. Uniform budgets remove the earlier proposed requirement
for heterogeneous template-budget support.

## What the completed acquisition establishes

The [retained acquisition](../../results/quandela/runs/ascella-mosaiq-update-order-retry/README.md)
contains eight settings, two values of each angle and two representatives.
It completes in 25 seconds and returns 65,536 samples.

| Question or hypothesis | Evidence and conclusion |
|---|---|
| Does the unchanged request still fail at the instrument boundary? | All eight settings complete. Continuing failure of that request is contradicted at the recorded observation. The provider's private repair remains unobserved. |
| Does the dark output open when both angles are nonzero? | With both angles pi/4, representative 0 gives 2198/8190 = 0.26838 and representative 1 gives 2167/8187 = 0.26469, against the ideal 0.25. Zero-angle controls give 2 to 14 dark events per setting. The qualitative dependence is observed. |
| Does a strictly noiseless requested law describe every recorded event? | Counts occur in ideal-zero channels. Faithful interpretation of those events contradicts the strictly noiseless model. The conclusion concerns the combined instrument and observation model, rather than quaternion algebra. |
| Does the device pass a specified numerical tolerance? | Measured/requested conditional total variation ranges from 0.0004883 to 0.0279609. The pilot supplies descriptive distances, without preregistered tolerance or calibrated uncertainty decisions. |
| Does the optical state retain phase coherence? | Direct intensities cannot distinguish the ideal state from a diagonal mixture with the same probabilities. The pilot leaves this question open. |
| Does changing noncommuting generators to commuting generators remove the response? | The pilot contains zero-angle controls but lacks the same-angle commuting-generator mutation. |
| Does the instrument realize fundamental quaternionic mechanics? | The complex optical encoding does not test that claim. |

Returned numerical meshes agree with the requested conditional probabilities
within 0.0002982 total variation. Metadata conformance differs from physically
measured phase conformance. Four returned modes also leave output leakage,
absolute loss and isolated temporal drift unresolved.

## Derive the amplitudes before choosing measurements

The source of convention is
[`hypercomplex_operators.py`](../../gororoba_quantum/hypercomplex_operators.py):

\[
\chi(a+bi+cj+dk)=\begin{pmatrix}a+ib&c+id\\-c+id&a-ib\end{pmatrix}.
\]

Let `I=chi(i)`, `J=chi(j)`, `K=IJ=chi(k)`,
`A=cos(theta) identity + sin(theta) I` and
`B=cos(phi) identity + sin(phi) J`. Define four real coefficients:

\[
a=\cos\theta\cos\phi,\quad b=\sin\theta\cos\phi,\quad
c=\cos\theta\sin\phi,\quad d=\sin\theta\sin\phi.
\]

Then

\[
AB=a+bI+cJ+dK,\qquad BA=a+bI+cJ-dK.
\]

The order interferometer `S diag(AB,BA) S` separates the symmetric and
antisymmetric terms:

\[
U=\begin{pmatrix}Q_+&Q_-\\Q_-&Q_+\end{pmatrix},\quad
Q_+=\{A,B\}/2=a+bI+cJ,\quad Q_-=[A,B]/2=dK.
\]

For source mode 0 its state is

\[
\psi=(a+ib,-c,0,id)^T.
\]

The direct probabilities are `(a^2+b^2,c^2,0,d^2)`. In particular,

\[
D=p_2+p_3=d^2=\|[A,B]\|_F^2/8.
\]

The dark probability measures a squared norm. Squaring loses orientation.
The bright-to-dark coherence retains products of the lost amplitude with two
symmetric coefficients:

\[
X=2\operatorname{Re}(\psi_0^*\psi_3)=2bd
  =\sin^2\theta\sin(2\phi),
\]
\[
Y=2\operatorname{Im}(\psi_0^*\psi_3)=2ad
  =\tfrac12\sin(2\theta)\sin(2\phi).
\]

These products provide the central experimental improvement: the acquisition
measures how the commutator interferes with the anticommutator, beyond its
squared magnitude. Direct intensities remain identical for `phi` and `-phi`,
while X and Y reverse sign. Under `theta -> -theta`, X stays even and Y becomes
odd. A single positive pi/4 point gives X=Y and hides that distinction.

Use the following output analyzers on ordered mode pair `(0,3)`, with identity
on the other modes:

\[
H_X=2^{-1/2}\begin{pmatrix}1&1\\1&-1\end{pmatrix},\qquad
H_Y=2^{-1/2}\begin{pmatrix}1&-i\\1&i\end{pmatrix}.
\]

Their output-0 minus output-3 probability measures X and Y respectively.
These are complex-encoding observables. Adjacent channel-pair sums carry the
source module's quaternion-ray position interpretation; an analyzer mixing
channels 0 and 3 does not inherit that interpretation.

## A finite coefficient atlas

Fix `phi=+pi/4` for the ideal curve. Write `x=X`, `y=Y`, and `q=D`:

\[
x=\frac{1-\cos2\theta}{2},\qquad
y=\frac{\sin2\theta}{2},\qquad
q=\frac{1-\cos2\theta}{4}.
\]

Three exact identities tie phase-sensitive data to intensity:

\[
(x-1/2)^2+y^2=1/4,\qquad x=2q,\qquad
y^2=2q(1-2q).
\]

In complex form, `C=X+iY=2 psi_0^* psi_3=(1-exp(-2i theta))/2`: the
coherence between the bright mode 0 and the dark mode 3, relative to the mode-0
reference amplitude. The first locus is a circle; the circle together with
`x=2q` implies the third identity, so agreement with all three is one joint
test rather than three independent confirmations. The final identity has two
signed branches:
intensity determines the magnitude of y under the ideal model but leaves its
sign unresolved. The five planned angles sample both branches.

At `theta_k=k*pi/5`, `k=0,...,4`, decompose each measured sequence into the
complete five-dimensional discrete basis:

\[
f_k=f_0+f_{c1}\cos2\theta_k+f_{s1}\sin2\theta_k
       +f_{c2}\cos4\theta_k+f_{s2}\sin4\theta_k,
\]

where `f_0=sum(f_k)/5`, and each sine/cosine coefficient is the corresponding
weighted sum times `2/5`.

| Sequence | Constant | cos(2 theta) | sin(2 theta) | cos(4 theta) | sin(4 theta) |
|---|---:|---:|---:|---:|---:|
| Signed X | 1/2 | -1/2 | 0 | 0 | 0 |
| Signed Y | 0 | 0 | 1/2 | 0 | 0 |
| Direct dark probability | 1/4 | -1/4 | 0 | 0 | 0 |

The discrete transform is saturated: all five coefficients are retained.
Unintended second-harmonic coefficients reveal finite-grid departures that a
three-coefficient fit discards. Frequencies that alias on this grid remain
indistinguishable. Agreement on five angles does not establish a continuous
functional law between them.

The [derivation replay and theory atlas](../evidence/ascella-order-coefficients/README.md)
check the circle identities symbolically and compare the coefficient formulas
against the repository matrix over the planned points and additional angles.
The equations are standard consequences of quaternion/SU(2) algebra. The
methodological contribution is their use as a finite hardware discrimination
protocol and an evidence-bearing visualization; a literature novelty claim
requires a separate prior-art comparison.

## Extract a nuisance model from the mathematics itself

The vector coefficients also distinguish a restricted common phase rotation
from deformation of the mathematical response. Let `r=(x,y)` and suppose the
whole measured response obeys `r_measured=eta R(delta) r_ideal`, with one
angle-independent attenuation `0 <= eta <= 1` and one real planar rotation R(delta).
Write vector coefficients `A0=(x0,y0)`, `Ac=(xc1,yc1)` and `As=(xs1,ys1)`.
The model requires

\[
A_c=-A_0,\qquad A_s=J_2 A_0,\qquad
J_2=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.
\]

Both second-harmonic vector coefficients must also equal zero.
Consequently `A0 dot As=0`, `norm(A0)=norm(As)=eta/2`, and
`det(A0,As)=eta^2/4`. A common rotation changes the orientation but preserves
these relations. Conjugation reflects the curve and reverses the determinant.
Unequal quadrature attenuation generally violates the equal-norm condition;
a theta-dependent distortion can populate the second harmonic. A diagonal
mixture gives eta=0, where the inferred orientation becomes undefined.

In complex form the model is `C_measured=g C_ideal` with one complex gain
`g=eta exp(i delta)`, whose coefficients are `C_0=g/2`, `C_c1=-g/2`,
`C_s1=ig/2`. A global phase `psi -> exp(i gamma) psi` leaves `C` unchanged, so
`delta` is a relative phase between modes 0 and 3, or a rotation of the
quadrature reference. Uniform transmission loss scales every detected channel
alike and cancels from the conditional probabilities, so `eta` is an
attenuation of the measured coherence response (dephasing, unequal losses,
analyzer visibility and compilation errors all contribute), not an optical
transmission estimate.

This is calibration through the scientific coefficients: the same acquisition
tests whether a two-parameter response model explains the departure. The
inferred `eta=2 norm(A0)` and `delta=atan2(y0,x0)` describe that model; they do
not identify a unique physical decoherence rate or instrument phase. Retain
raw coefficients and use the same simultaneous confidence set to test model
relations. Model fitting never silently corrects the preregistered ideal-model
comparison. A general real-linear mixing of the two quadratures can mimic
other effects; the restricted model remains compatible when its constrained parameter set
intersects the simultaneous confidence box. An empty intersection rejects it.
Compatibility supplies neither a unique mechanism nor a tolerance-qualified
model acceptance. Fitting an arbitrary map to five points supplies a different
model with different constraints.

## Questions, competing models and falsifiers

| Scientific question | Competing prediction | Registered observation that distinguishes it |
|---|---|---|
| Does order interference retain signed off-diagonal coherence? | A bright/dark-dephased state has the same direct probabilities and X=Y=0. | A simultaneous interval for a predicted nonzero X/Y coefficient excludes zero, under the preparation/analyzer model. |
| Does the response carry the correct orientation and theta parity? | Conjugation reverses Y; interchanging analyzers exchanges X and Y; sign erasure removes the signed response. | The complete X/Y coefficient vectors discriminate these specified alternatives at the sampled points. |
| Does the commutator magnitude connect to its coherent cross-terms? | Unrelated or attenuated phase responses can preserve dark intensity while violating x=2q or the circle. | Propagate the joint coefficient confidence set into finite-grid identity residuals. Exclusion of zero rejects the exact joint model. |
| Does a same-angle commuting mutation change the dark probability by the predicted contrast? | An order-insensitive response predicts equal target and mutation output. | The balanced target-minus-mutation interval excludes zero and is compared with its registered nonzero ideal. |
| Does the commuting mutation close the dark branch? | A contrast alone fixes neither probability: target 0.252746 with mutation 0.08 gives the same 0.172746 as target 0.172746 with mutation 0. | The absolute mutation-dark interval lies inside the registered near-zero tolerance. |
| Does the device reproduce only the expected coefficient support? | Additional finite-grid components give nonzero cos(4 theta) or sin(4 theta). | Their simultaneous intervals exclude zero; conformance also uses the explicit coefficient tolerances below. |

The hardware conjectures concern the combined preparation, compiled mesh,
analyzers and conditional detection. The device receives the composite
operators `U`, `H_X U` and `H_Y U`; a common software template fixes their
shared structure, but compilation or hardware errors can depend on the whole
programmed circuit, so the three readouts can carry different effective
preparations. The operational result is conformance of the compiled circuit
family, with the selected coherence inferred under the preparation/analyzer
model. Where the service keeps the preparation controls fixed and varies only
analyzer controls, the builder preserves that structure. The commuting
mutation replaces generator `J` by `I`, which changes the programmed matrix as
well as the order relation; it tests the encoded commutator response and does
not certify the physical application order of two independent devices. The algebraic identities themselves are
proved consequences of the stated operators. A mismatch rejects a hardware
model or its assumptions; it does not refute a mathematical theorem.

For an individual state, positivity gives `X^2+Y^2 <= 4 p0 p3`, with equality
for the ideal pure state. The sign-pooled quantities below are **not** a purity
estimator for either physical sign state. Raw sign-specific populations and
quadratures remain available for descriptive diagnostics. Analyzer-dependent
loss and postselection can prevent the three readouts from sharing one
normalized density matrix. A deficit does not uniquely identify decoherence;
an apparent positivity violation first challenges that measurement model.
Single-photon linear-optical intensities also admit classical wave descriptions.
The acquisition supplies neither quantum advantage nor a nonclassicality witness.

## Exact 64-setting design and budget

For each `theta_k=k*pi/5`, run direct, X and Y readout blocks, in that order.
Each block has four arms with `phi=+pi/4,-pi/4,-pi/4,+pi/4`.
Five angles times three readouts times four arms gives 60 settings.

Append one four-arm direct-readout mutation block at
`theta=pi/5, phi=pi/4`. Its arms use `I,J`; `I,I`; `I,I`; `I,J`.
The latter pair commutes while preserving both nonzero angle magnitudes.
Its target-minus-mutation dark prediction is
`sin(pi/5)^2/2 = 0.172745751406`.

Every entry starts from physical input mode 0, representative 0 and compilation
seed 0. Embed the four-mode operator into twelve modes and return all twelve.
The platform's `final_mode_number` defaults to the input-state width and drops
states with a photon on an unused mode
([platform record](../../results/quandela/runs/ascella-mosaiq-update-order-retry/platform-before-submission.json)),
so a twelve-mode intended matrix is insufficient by itself. The serialized
request carries a twelve-entry input occupation, a twelve-mode circuit, an
effective output width of twelve, and returns twelve-mode occupations; eligible
events outside the logical four-mode block stay in the denominator. The local
replay of the frozen request checks each of these fields.
Use `sample_count`, an explicit empty mitigation list and
`min_detected_photons=1`. One common parameterized template implements the
operator and analyzer choices. A builder validates every full unitary and
serialized setting; separate unrelated circuit objects do not establish
supported iterated-job packing.

| Resource | Proposed cap |
|---|---:|
| Jobs / settings | 1 / 64 |
| Samples / shots per setting | 8,192 / 16,384 |
| Aggregate sample / shot caps | 524,288 / 1,048,576 |
| Execution time | 300 seconds |
| Recorded-tariff expected debit | 1.016384 credits |
| User ceiling | 1.2 credits |

The [billing runbook](../runbooks/quandela-credit-optimization.md) records
`1 + 0.000001 * max_iteration_shots`, giving 1.016384 credits. The one-credit
component comes from retained usage; the platform shot tariff alone does not
confirm every offer charge. Fresh availability, occupancy, tariff, supported
outputs and per-setting estimates precede admission. Increasing expenditure
toward 1.2 credits is useful only when the instrument can finish the added work.

The pilot supplies one timing point, eight settings in 25 seconds. The
additional model `T=a+h*settings+s*total_samples`, with common nonnegative
coefficients, implies `T64=200-7a <= 200 seconds`. Changed mesh overhead,
throughput or service behavior can invalidate the model. The 300-second cap
is a bound on the request, not a measured guarantee of completion.

The tradeoff favors finite mathematical coverage over a separate drift study,
full process tomography or an axis-angle sweep. ABBA cancels additive affine
iteration-index nuisance within a sign block. Unequal durations, nonlinear
drift and analyzer changes remain nuisance mechanisms. The run does not
isolate temporal drift or establish separately applied physical A/B devices.

## Estimators and simultaneous decisions

For each iteration, `N_i` counts all reported occupation-sum-one events across
twelve modes. Define `z_i=(n_i0-n_i3)/N_i` for an analyzer readout and
`p_i=(n_i2+n_i3)/N_i` for direct readout. Outcomes in other modes remain in the
denominator. Preserve vacuum/multiple-occupation exclusions and all twelve
counts; reported occupations do not establish photon-number resolution.

At each angle, signed `x_k` and `y_k` use
`(z1-z2-z3+z4)/4`; `q_k=(p1+p2+p3+p4)/4` averages direct signs.
Retain direct sign contrast and sign-even analyzer components descriptively.
The mutation difference uses `(p1-p2-p3+p4)/2`, not division by four. The
absolute mutation dark probability uses the two commuting arms,
`D_mut=(p2+p3)/2`.

The four-arm estimator returns `(z_+ - z_-)/2` under stable repeated arms, so a
common sign-even error `b(theta)` in `z_+=f+b`, `z_-=-f+b` cancels from it. The
primary analysis therefore covers the sign-odd X/Y coefficients and the
sign-averaged dark coefficients. The replay's counterexample keeps all fifteen
primary coefficients exactly ideal with sign-specific coherences
`C_+=C(1+0.2i)` and `C_-=-C(1-0.2i)`. It is a positive state at every planned
angle (`p0=0.52`, `p3=D`, `p1=0.48-D>=0.0277`), and its sign-even coherence
reaches magnitude 0.1902. The sign-even X/Y responses and direct sign contrast
are displayed beside the primary atlas and stay descriptive; "complete
coefficient spectrum" always names those primary sequences.

The 15 discrete coefficients, the mutation difference and the absolute
mutation dark probability form 17 primary endpoints. Allocate family error
0.01 equally: `alpha_j=0.01/17`. The mutation dark tolerance is 0.05, fixed
before acquisition; the endpoint qualifies closure when its whole interval
lies in `[0, 0.05]`. Adding the ten sign-even X/Y coefficients would give 27
endpoints and widen every radius by a factor of 1.0319 at unchanged cost; that
expansion is an open decision of the plan's owner.
For any linear endpoint with raw-iteration weights `c_i` and event range
`[a_i,b_i]`, use

\[
r_j=\sqrt{\tfrac12\log(2/\alpha_j)
               \sum_i c_i^2(b_i-a_i)^2/N_i}.
\]

Analyzer events have range [-1,1]; direct dark events have range [0,1]. At
8,192 eligible events per iteration the resulting half-widths are:

| Endpoint type | Hoeffding radius |
|---|---:|
| X/Y constant coefficient | 0.009963024 |
| X/Y sine or cosine coefficient | 0.014089844 |
| Dark constant coefficient | 0.004981512 |
| Dark sine or cosine coefficient | 0.007044922 |
| Mutation difference | 0.022277999 |
| Mutation dark probability | 0.015752924 |

The 17-endpoint radii are the 16-endpoint radii times 1.0037487. Projecting
the simultaneous coefficient box onto each sampled point bounds the signed
X or Y value within 0.0381 at `theta=0` and 0.0474 at the other four angles;
those are the widths the atlas draws.

Recompute using actual eligible counts. Independence of eligible observations
and appropriate sampling/stopping assumptions underlie these bounds. Aggregate
`sample_count` does not establish temporal independence. Endpoint independence
is unnecessary for the family union bound.

The proposed engineering tolerance is absolute coefficient error at most 0.05,
and absolute mutation-difference error at most 0.05. These are design choices,
not vendor specifications. A coefficient tolerance of 0.05 is not a pointwise
tolerance: inverting the five-point transform, coefficient errors within 0.05
allow a sampled value to move by up to 0.15 at `theta=0` and 0.18284 at the
other angles, before physical constraints. Verdicts and artwork carry the
words "coefficient tolerance". An interval wholly inside the allowed region
qualifies that endpoint; a disjoint interval falsifies tolerance-conformance;
overlap is inconclusive. Separately report whether an exact ideal or specified
alternative lies outside its simultaneous interval. Excluding an exact ideal
can coexist with passing a finite engineering tolerance.

The complete coefficient box reconstructs the finite five-point grid. Propagate
that same joint set through the linear and nonlinear identities, using bounded
interval optimization or conservative interval arithmetic. This adds no new
error allocation. Squaring point estimates alone introduces bias and supplies
no confidence statement. A wide propagated set gives an inconclusive identity
test rather than permission to report a precise physical residual.

All 64 attributable, valid iterations are required for the registered complete
analysis. Missing, zero-eligible or ambiguous entries leave the complete
inference unavailable; raw partial counts remain descriptive evidence. Echoed
parameters and budgets must match; identical repeated echoes rely on the
service's ordered iterator contract. Timeout-prefix retention is unproven.
Automatic retry and silent missing-arm substitution are outside the design.

## Quantum art carries the mathematical evidence

The artwork is a **measured coefficient atlas**. A theoretical preview appears
in the [replay bundle](../evidence/ascella-order-coefficients/README.md); its
curves explicitly carry the label THEORY ONLY.

1. **Signed coherence circles.** Plot the five measured `(x_k,y_k)` points with
   simultaneous uncertainty, angle labels and the ideal circle as a distinct
   reference. Display sign-specific responses separately from the signed
   projection. Hue encodes angle or an explicitly identified coherence argument;
   phase is undefined when the coherence vanishes. A diagonal-mixture reference
   collapses to the origin while its direct-intensity profile stays unchanged.
2. **The two branches intensity hides.** Plot measured Y against measured dark
   probability. Positive and negative branches reveal orientation that an
   intensity-only picture loses. A ribbon width can encode dark probability,
   with units and a legend. Lines joining the five measured points indicate
   sampling order, not measured intermediate states.
3. **Coefficient spectrum.** Show the 15 primary coefficients and intervals
   beside the exact rational predictions. Unintended coefficient support
   remains visible instead of being smoothed away for visual appeal.
4. **Twelve output channels.** A companion probability strip retains every
   returned mode and the exclusion counts. It shows conditional redistribution,
   rather than claiming calibrated absolute optical loss. The twelve-mode dark
   probability is `D_12=f_4 D_4`, with `f_4` the fraction of eligible events in
   the logical four-mode block and `D_4` the pilot's four-output conditional;
   the strip shows both, so a leakage change reads as a change in `f_4`.

The theory preview carries angle labels, a colorbar and direction arrows for
both traversals, since conjugation reverses the traversal of the same circle.
It marks the origin as both the diagonal-mixture reference and the ideal point
at `theta=0`; the origin alone never classifies a setting as incoherent, and
the nonzero-angle coefficients carry that discrimination. Its error bars are
the projected simultaneous radii above, and a separate panel draws the
sign-even response the primary endpoints cancel.

An angle-index animation moves through separately prepared circuits. Its label
states parameter sweep, not measured time evolution. Measured points, theoretical
curves and any model interpolation remain visually distinct. Raw counts,
manifest identity, estimator and rendering code accompany the final artwork.

## Builder requirements and subsequent questions

Implementation freezes the common twelve-mode circuit, exact entry sequence,
full-unitary checks, analyzer conventions, commuting mutation and request
hashes. Local replay executes the actual serialized request through SLOS/Naive.
Synthetic diagonal mixtures, conjugation, swapped readouts, aliasing and missing
arms exercise the analysis. Fresh preflight and the applicable
[evidence-closure procedure](../runbooks/evidence-closure.md) precede submission.
The current deliverable is the scientific plan and local derivation evidence.

A later axis-angle experiment can vary the generator from I toward J. For
`B=cos(phi)+sin(phi)(cos(gamma)I+sin(gamma)J)`, the commutator norm predicts
`D=sin(theta)^2 sin(phi)^2 sin(gamma)^2`. Orientation-sensitive readouts can
then distinguish axes with the same norm. That richer scan becomes a separate
case after the coefficient atlas establishes which measurement discrepancies
require explanation. Wave evolution and Fourier mathematics remain separate
scientific families rather than filler in this job.
