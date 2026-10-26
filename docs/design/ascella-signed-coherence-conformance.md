# Ascella order amplitudes, coefficient geometry and measured art

The next scientific question is whether Ascella preserves the **signed
commutator amplitude and its interference with the anticommutator**, across a
finite angle family. The completed pilot observes intensities. The follow-up
measures the coherence those intensities leave undetermined, extracts the
predicted harmonic coefficients, and renders their measured geometry.

The plan contains one 64-setting order-family job, a 300-second cap and a
1.2-credit ceiling. The recorded tariff gives 1.016384 credits. The
[frozen request](../../results/quandela/cases/ascella_signed_coherence/job-00/cases.json),
its serialized job body and their
[local replay](../../results/local-simulation/ascella-signed-coherence-replay/README.md)
precede the [written acquisition case](#written-acquisition-case). Under the
owner's approval of that case, job `739a5271` ran on 2026-10-24: all 27
endpoints qualify, and 1.27 % of events fall outside the logical block, above
the case's dark-count bound
([retained run](../../results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/README.md)).
The registry cites the runner image's
[analysis](../../results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/analysis-runner-image.json),
which the replay gate reproduces; the run's
[first analysis](../../results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/analysis.json)
keeps its bytes from a system-numpy build that differs in the last ulps, with the same 27 verdicts.
Wave evolution
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
The sign-even `x_k^e` and `y_k^e` use `(z1+z2+z3+z4)/4`; direct sign contrast
stays descriptive.
The mutation difference uses `(p1-p2-p3+p4)/2`, not division by four. The
absolute mutation dark probability uses the two commuting arms,
`D_mut=(p2+p3)/2`.

The sign-odd estimator returns `(z_+ - z_-)/2` under stable repeated arms, so a
common sign-even error `b(theta)` in `z_+=f+b`, `z_-=-f+b` cancels from it, and
the sign-even estimator `(z_+ + z_-)/2` returns `b`. The ideal response is
`C_odd=C=(1-exp(-2i theta))/2` and `C_even=0`. The replay's counterexample,
sign-specific coherences `C_+=C(1+0.2i)` and `C_-=-C(1-0.2i)`, keeps every
sign-odd X/Y and dark coefficient exactly ideal and gives `C_even=0.2iC`:
`X_even=-0.1 sin(2 theta)` and `Y_even=0.1-0.1 cos(2 theta)`. It is a positive
state at every planned angle (`p0=0.52`, `p3=D`, `p1=0.48-D>=0.0277`), and its
sign-even coherence reaches magnitude 0.1902. The primary analysis therefore
covers the sign-odd and sign-even X/Y coefficients and the sign-averaged dark
coefficients; "complete coefficient spectrum" names those 25 sequences.

The 15 sign-odd X/Y and dark coefficients, the 10 sign-even X/Y coefficients,
the mutation difference and the absolute mutation dark probability form 27
primary endpoints. Allocate family error 0.01 equally: `alpha_j=0.01/27`. Each
sign-even coefficient has registered ideal value zero and the same 0.05
coefficient tolerance. The sign-even counterexample is a required negative
control: at expected counts its coefficients `X_even` sine 2-theta `=-0.1`,
`Y_even` constant `=0.1` and `Y_even` cosine 2-theta `=-0.1` have intervals
wholly outside the tolerance, so the family falsifies it, and replay.py raises
if it would not. A weak twist of 0.05 is a second, separate case with the
opposite registered disposition: its `X_even` sine 2-theta and `Y_even`
cosine 2-theta coefficients `=-0.025` have signed intervals
`[-0.039485, -0.010515]` and its `Y_even` constant `=0.025` has
`[0.014757, 0.035243]`, all three excluding the exact ideal zero and lying
wholly inside the tolerance. It is reported as "exact ideal excluded;
coefficient-tolerance conformance supported", and replay.py raises if the two
decisions stop separating. Both dispositions come from expected counts and the
declared radius formula; they are not measured rejection probabilities. The
mutation dark tolerance is 0.05, fixed
before acquisition. A probability lies in `[0, 1]`, so the endpoint's interval
is intersected with `[0, 1]` before any decision; closure qualifies when the
upper bound `min(1, D_mut + r)` is at most 0.05, and fails when the lower bound
exceeds 0.05. A perfectly closed mutation, `D_mut=0` with radius 0.01619, gives
the clipped interval `[0, 0.01619]` and qualifies.
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
| X/Y constant coefficient, sign-odd or sign-even | 0.010242515 |
| X/Y sine or cosine coefficient, sign-odd or sign-even | 0.014485103 |
| Dark constant coefficient | 0.005121257 |
| Dark sine or cosine coefficient | 0.007242552 |
| Mutation difference | 0.022902959 |
| Mutation dark probability | 0.016194838 |

The sign-even weights differ from the sign-odd weights only in sign, so the
two radii agree. The 27-endpoint radii are the 17-endpoint radii times
`sqrt(log(5400)/log(3400))=1.0280528`. Keeping the 17-endpoint radii would take
8,659 eligible events per iteration instead of 8,192, 5.69% more; the design
keeps 8,192. Projecting the simultaneous coefficient box onto each sampled
point bounds the signed X or Y value within 0.03921 at `theta=0` and 0.04873
at the other four angles; those are the widths the atlas draws.

A sign-specific response is `C_+=C_even+C_odd` or `C_-=C_even-C_odd`, so its
reconstructed coefficient carries both radii, 0.020485 for a constant and
0.028970 for a sine or cosine coefficient, and the two 0.05 coefficient
tolerances allow it a worst-case deviation of 0.10. The sign-odd radii alone
never bound a sign-specific response.

An earlier revision of this plan registered 17 primary endpoints, the
sign-odd and dark coefficients and the two mutation endpoints at
`alpha_j=0.01/17`, with radii 0.009963024, 0.014089844, 0.004981512,
0.007044922, 0.022277999 and 0.015752924 in the table's order; the sign-even
coefficients stayed descriptive. That family is superseded planning and
interprets no acquisition.

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
3. **Coefficient spectrum.** Show the 25 primary coefficients and intervals
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
sign-even response, ideal zero, beside the counterexample's.

An angle-index animation moves through separately prepared circuits. Its label
states parameter sweep, not measured time evolution. Measured points, theoretical
curves and any model interpolation remain visually distinct. Raw counts,
manifest identity, estimator and rendering code accompany the final artwork.

## Builder requirements and subsequent questions

[`ascella_coherence_request.py`](../../scripts/ascella_coherence_request.py)
freezes the common twelve-mode circuit, exact entry sequence, analyzer
conventions and commuting mutation in
[`results/quandela/cases/ascella_signed_coherence/job-00`](../../results/quandela/cases/ascella_signed_coherence/job-00/cases.json).
Its `--check` mode, run by gate core-record-check-07 (tests/test_cli_record_checks.py), validates the retained bytes: every
iteration's Perceval unitary matches the twelve-mode manifest operator, every
operator matches the closed form `[[Q+,Q-],[Q-,Q+]]` under its analyzer, and
every registered ideal equals the readout law of that form. The check also
requires refusal of a perturbed unitary, exchanged X and Y analyzers and a
four-entry input occupation. The `sample_count` command signature of the
retained Ascella record takes `max_samples`, `max_shots` and
`compilation_seed` only, so the request leaves `final_mode_number` at its
input-width default of twelve. `--body` builds the job body through
`qd_platform.payload`, which reads the live qpu:ascella record and records the
body instead of sending it, and retains
[`job-body.json`](../../results/quandela/cases/ascella_signed_coherence/job-00/job-body.json)
with its build record; Perceval's per-setting estimate is 524,288 shots
against the 1,048,576 cap. `--check` deserializes that body and requires 64
entries carrying the manifest's `circuit_params`, 8,192 samples, 16,384 shots
and seed 0, the twelve-entry input, the one-photon filter and the empty
mitigation list, with each entry's bound unitary equal to the design operator
within 1e-9. Preflight compares the fresh body with the retained one in every
field except `process_id`. The
[local replay](../../results/local-simulation/ascella-signed-coherence-replay/README.md)
executes the serialized body through SLOS and Naive and runs the registered
estimators of [`ascella_coherence_analysis.py`](../../scripts/ascella_coherence_analysis.py)
on the ideal response, a seeded sample of the iterator, the equal-contrast and
sign-even counterexamples, a diagonal mixture, conjugation, exchanged readouts
and a missing iteration; every disposition this section registers holds.
Aliasing is a property of the five-point transform, which the derivation
records. Fresh preflight and the applicable
[evidence-closure procedure](../runbooks/evidence-closure.md) precede submission.
The retained deliverables are the scientific plan, the local derivation
evidence, the frozen request and its local replay.

A later axis-angle experiment can vary the generator from I toward J. For
`B=cos(phi)+sin(phi)(cos(gamma)I+sin(gamma)J)`, the commutator norm predicts
`D=sin(theta)^2 sin(phi)^2 sin(gamma)^2`. Orientation-sensitive readouts can
then distinguish axes with the same norm. That richer scan becomes a separate
case after the coefficient atlas establishes which measurement discrepancies
require explanation. Wave evolution and Fourier mathematics remain separate
scientific families rather than filler in this job.

## Written acquisition case

The case submits the frozen request once to qpu:ascella: one job of 64
iterations, 8,192 samples and a 16,384-shot cap per iteration (aggregate caps
524,288 and 1,048,576), seed 0, the explicit empty mitigation list, a
twelve-entry input and twelve returned modes. It names `cases.json`
`3c92af45df7502bab5c6f2d74779aa83b04f7af2094b62b499b6e29ca0e69520`, the
retained `job-body.json`
`7931578af1d340d0a6b51a82cca8dfc0a5b2b6f21e47cee334b5d032a473c7e8`, and that
body's digest without `process_id`,
`e323b1c6fd98747215a7c7a4574ab10a08f5392c1fc0b5edfafafcde09905c07`.

The job measures the 27 primary endpoints of the preceding sections on the
physical instrument. Local SLOS and Naive already return the ideal response to
1e-12, so simulation answers only what the request asks for; the question is
what Ascella's mesh, phase settings and detectors return. No repository model
covers that response, as the descriptive pilot distances of 0.0005 to 0.028
total variation show.

**Seconds.** Expected 200 seconds against the 300-second `max_duration`. The
eight-iteration pilot `889c0b21` completed 65,536 samples in 25 provider
seconds. If every second scaled with iterations or samples, 64 iterations at
the same budget would take 200 seconds; any fixed setup lowers that. The
service's behavior at `max_duration` is unobserved, and the mutation block runs
last, so a truncated job loses the mutation closure and the analysis returns
`complete: false`.

**Credits.** Ceiling and expectation 1.016384 credits: the 1.0 per-job price
plus 16,384 billed shots at 1e-6 credits
([billing runbook](../runbooks/quandela-credit-optimization.md)), inside the
user's 1.2-credit limit. Pilot `889c0b21` debited exactly 1.016384 free
credits. Six errored qpu:ascella jobs debited nothing: the token's qpu:ascella
total reads 1.016384 free credits over seven jobs. The token's totals before
the case are 57.24 free credits over 65 jobs, with zero paid credits. The
account-wide remaining balance is unobserved.

**Why not more shots per job.** The per-job price dominates, and shots cost
1e-6 credits each, so a job's statistical yield is limited by its 300 seconds
rather than by credits. One timing point cannot separate per-iteration setup
from per-sample time. If all 25 pilot seconds were per-sample time, 64
iterations would fit in 300 seconds only up to 12,288 samples each, which
leaves no margin. That gain would shrink the radii by a factor of only 0.82,
and it would invalidate the frozen digests, the replay receipts and the
registered radii. The job therefore runs as frozen. Its measured duration
supplies the second timing point that sizes any larger or repeated job. A
repeat of the identical body costs 1.016384 credits; a between-job comparison
needs its own analysis registered before its data, so it is a separate case.

**Fresh read.** [`case-preflight/`](../evidence/ascella-order-coefficients/case-preflight/preflight.json)
holds the read-only plan of 2026-10-24 07:04:46 UTC by
`ascella_coherence_request.py --preflight`, together with its `catalogue.json`
and `observation.json`:
- qpu:ascella was available on its Explorer row and processor record, with
  92.37% availability for 2026-10-24, a 300-second `max_duration` and no
  booked maintenance. qpu:belenos carries weekly maintenance from 2026-10-29
  08:30 to 12:00 UTC.
- The price was 1e-6 credits per shot, and token occupancy was 0 running and
  0 queued of 1 and 1.
- HOM was 87.28%, g2 1.9% and the clock 13.33 MHz.
- The processor advertised connected input modes 0, 2, 4, 6, 8 and 10. Mode
  0 carries the request's photon.
- The advertised software was mosaiq-arcturus 2.1.5.2.post4, hardware-core
  3.9.3, pcvl-worker 2.1.1, universalchipworker 2.1.3, exqalibur 1.4.1 and
  perceval-quandela 1.3.0, behind cloud API v2.10.1-rc1.
- Perceval estimated 524,288 shots.
- The planned body equaled the retained body in every field except
  `process_id`.

**Token sharing.** The job token admits one running and one queued job, and
`plan` refuses while either is occupied. The armed
[BDSC drift series](../../results/quandela/schedules/bdsc-drift-series.json)
submits a 213.6-second qpu:belenos job at each odd UTC hour from 07:00 to
19:00 on 2026-10-24, and a due drift job waits while the token is busy. The
Ascella job therefore starts at least 10 minutes after a drift job's start
and finishes before the next one. On the 200-second projection, a start
between hh:10 and hh:50 past an odd hour leaves both jobs their windows.

**Untested path.** No completed Ascella job has yet used a twelve-entry input,
an explicit empty mitigation list or more than eight iterations. Pilot
`889c0b21` sent four entries and no mitigation field. Every retained Ascella
job that carried an explicit mitigation list ended in the
`circuit_input_ports`/`set_pic_input` worker error, but all of those jobs
predate the advertised mosaiq-arcturus 2.1.5.2.post4 update and the pilot's
completion. An error is therefore a live outcome, and on the retained
evidence it costs nothing.

**Stopping rule.**
- A terminal error with no counted iteration allows one resubmission of the
  identical body under the same approval, from a fresh run directory, after
  `--preflight` passes again.
- A second such error stops the case and is reported.
- A completed, partial or canceled job that returned counts is never
  resubmitted under this approval. An incomplete analysis keeps its raw counts
  as descriptive evidence.

**Dark counts.**
- At the fresh read the processor reports 12,159 dark detections per second
  summed over twelve detectors: 9,908 on detectors 8 to 11 and 651 on
  detectors 1 to 3.
- Pilot setting `order-i1-j0-representative0` has its ideal support on mode 0
  and returned 4 of 8,192 events on modes 1 to 3.
- Scaling those 4 events by the ratio 12,159/651 bounds the dark share of
  twelve-mode eligible events at about 75/8,192, or 0.91%.
- The bound assumes the stray events are dark counts in proportion to each
  detector's reported rate. Crosstalk would make the bound conservative, and
  a rate-independent mechanism would break it; the uncertainty is medium.
- A share of that size scales every statistic by about 0.99. Coefficients then
  move by at most about 0.005, inside the 0.05 coefficient tolerance, though
  the shift can exclude an exact ideal.
- `outside_logical_block` in the analysis record reports the measured share.

**Procedure after approval.** These commands contain no job-specific
placeholder:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="$HOME/.config/quandela/cloud-token"
RUN=results/quandela/runs/$(date -u +%Y-%m-%dT%H%M%SZ)-qpu_ascella-ascella_signed_coherence-job-00
mkdir -p "$RUN"
cp results/quandela/cases/ascella_signed_coherence/job-00/cases.json \
   results/quandela/cases/ascella_signed_coherence/job-00/circuit.json "$RUN"/
"$PYTHON" scripts/ascella_coherence_request.py --preflight "$RUN"
"$PYTHON" scripts/ascella_coherence_request.py --submit "$RUN" "APPROVAL TEXT"
"$PYTHON" scripts/qd_platform.py collect "$RUN" --timeout 3600
"$PYTHON" scripts/qd_platform.py snapshot --out "$RUN/platform-after"
"$PYTHON" scripts/qd_platform.py observe --out "$RUN/platform-after"
"$PYTHON" scripts/ascella_coherence_run.py --run "$RUN"
```

`--preflight` also writes `platform-before/` through `qd_platform.snapshot`
and `qd_platform.observe`, and the procedure writes `platform-after/` the same
way after collection:
- `catalogue.json` holds:
  - the curated Explorer rows;
  - every processor record: `perfs` (clock, per-detector dark counts, HOM,
    g2), `specs.software_versions` (mosaiq-arcturus, hardware-core,
    pcvl-worker, universalchipworker, exqalibur, perceval-quandela),
    `connected_input_modes`, `constraints`, `known_mitigations`,
    `default_mitigations`, the `architecture` blob and the server command set;
  - the API version, token occupancy and usage, and local package versions.
- `observation.json` holds the raw answer of every GET route in the retained
  cloud and account OpenAPI documents (`docs/notes/quandela/api/`), plus the
  public and Explorer platform lists and every platform's processor record.
  It is scrubbed of `FORBIDDEN_KEYS`. The Explorer rows keep every field,
  including the booked maintenance windows. The record also carries both
  OpenAPI documents, health, availability, the usage report and the provider
  RSS feed. Each answer is kept with its HTTP status, content type, retrieval
  time and sha256, and a refused or unanswered route is recorded as such.
- The observer omits three kinds of route. Token records are credentials,
  each QRNG read is a billed request that needs its own case, and the session
  routes (logout, oauth) perform account actions. `collect` reads and retains
  the job's own status, data and result.

The before and after pair brackets the job, because no job field names the
executing worker or a hardware-configuration digest. The portal dashboard
behind https://cloud.quandela.com/webide/ needs a browser session that the job
token cannot open ([API audit](../evidence/quandela/input-port-api-audit/README.md#dashboard-queue-and-accounting-boundaries)),
and neither the repository nor a web search finds a public Quandela telemetry
or Grafana endpoint. The run therefore records no dashboard telemetry and no
platform queue depth.

`--submit` holds the token's submit lock and repeats the plan. It refuses a
body that departs from the retained one before writing its checkpoint, and it
refuses a run directory that holds anything but the two copied request files
and `preflight.json`. Every directory under `results/quandela/runs/` reads as a sent job to
`scripts/research_state.py`, so a run directory whose preflight refuses
leaves the tree through `trash-put` before anything is committed. `collect`
retains the raw result and the partial result
of an error. `--run` attributes each counted iteration only at its own
position, checks the echoed `circuit_params`, and writes `analysis.json`. The
retained run then enters `docs/state/research_state.json`, the strategy run
log and this plan's receipts in the change that retains it.


## Open problems after job-00 and the permuted repeat

Job `739a5271` (job-00) qualifies all 27 endpoints and leaves three device
questions open. [`ascella_coherence_repeat.py --diagnose`](../../scripts/ascella_coherence_repeat.py)
writes their exploratory reading,
[`job-00-diagnostics.json`](../evidence/ascella-order-coefficients/job-00-diagnostics.json).

**Analyzer contrast.**
- The returned nominal compiled model matches the target: every statistic
  computed from the returned `computed_circuit` and `computed_input` lies
  within 2.2e-4 of its registered ideal, and none puts more than 6.2e-7 of the
  photon outside modes 0 to 3. The check covers the circuit the provider
  reports, not the applied voltages or the implemented unitary.
- The block-conditioned X and Y statistics read z = V ideal + c with V 0.970
  (standard error 0.009) on both readouts by ordinary least squares, 0.979 and
  0.975 by inverse-variance weights, while the direct readout reads
  slope 1.004. The deficit sits in the interference contrast of the hardware;
  the reported compilation and the intensities lie close to ideal, and the
  direct response carries small resolved departures of its own (job-01's dark
  constant 0.2547, interval [0.2511, 0.2583]).
- X residuals exceed multinomial noise: the inverse-variance weighted fit
  leaves chi-square 195 on 18 degrees of freedom, against 44 on 18 for Y, and
  the matched quadrature ideal explains little of it (coefficient -0.017,
  chi-square 176 on 17) ([response geometry](#response-geometry-of-both-jobs)).
  The X readout carries setting-specific errors. The diagnostics record's
  `residual_chi2` standardizes ordinary-least-squares residuals by unequal
  variances and has no chi-square reference.
- A 3 % contrast deficit is the calibrated-chip scale Maring et al. report for
  Ascella, total variation (3.0 +- 1.3) % over random phase settings
  ([literature, source 1](../notes/quandela/literature.md#1-maring-et-al-ascella-platform)).
- The X sign-odd constant (0.4697) and the Y sign-odd sin(2 theta)
  coefficient (0.4777) exclude 0.5 for this reason. Block-conditioned
  counts move them only to 0.4751 and 0.4851, so outside-block dilution
  removes 18 % of the X shortfall and 33 % of the Y shortfall (14 % and 29 %
  in job-01). The fractions describe a change of denominator, not a
  decomposition into physical causes.

**Outside-block clicks.**
- 6,659 of 524,288 events land on modes 4 to 11, 4 to 586 per setting, with
  1,424, 1,783 and 2,376 on modes 8, 9 and 10, the detectors with the largest
  plan-time dark rates (3,275, 4,114 and 5,290 per second). The pooled
  composition follows those rates except for an excess on modes 4 and 6
  (chi-square 110 on 7 degrees of freedom): a dark-rate-shaped background
  with further structure. The composition alone bounds the catalogue share
  above by 0.90 and admits no positive lower bound; the
  [two-component fit](#response-geometry-of-both-jobs) separates the parts.
- The outside-block count alternates in execution order: log counts have
  lag-1 autocorrelation -0.66 and lag-2 +0.73 (permutation p below 1e-4),
  with six phase slips over 64 iterations, while the size of the
  compiled-phase change from the predecessor predicts nothing (Spearman 0.22,
  p 0.09). Because job-00 runs the four arms of each block consecutively, the
  alternation is confounded with arm parity.
- `physical_perf` reads 0.0209 in every iteration
  ([literature, source 31](../notes/quandela/literature.md#31-perceval-performance-fields)),
  so the provider reports no per-iteration acquisition time. Ascella's settling time
  is unpublished; other thermo-optic devices settle in microseconds
  ([source 30](../notes/quandela/literature.md#30-thermo-optic-switching-times)),
  a comparison that leaves the settling share of the 2.5 to 3 s each iteration
  costs unresolved.

## Permuted repeat (job-01)

The owner approved job-01 on 2026-10-24: job-00's 64 circuits (same
`circuit_params`, seed 0, empty mitigation list and twelve-entry input) in the
order that values 0 to 63 of the retained ANU QRNG draw
[`draw-2026-10-18T083846Z.json`](../evidence/anu_qrng/draw-2026-10-18T083846Z.json)
fix, at 16,384 samples and 32,768 shots per iteration. The order puts 17 of
job-00's 32 high-outside settings at even positions and 15 at odd, so setting
identity and execution parity separate. Its ceiling is 1.032768 credits and
its expected duration under 240 s: job-00 took 186 s, and if acquisition time
scales with samples at the rate the outside-block dark clicks imply (about
34 s of job-00's 186), doubling the samples adds about 34 s; the per-sample
rate is an inference of medium confidence. The stopping rule of job-00
applies.

`--compare A B OUT` applies the preregistered comparison, each test at
alpha 0.01 against 20,000 seeded permutations:

| Question | Statistic | Reading |
|---|---|---|
| Fixed per-setting cause | Spearman of per-setting log(count + 1/2) outside-block counts, job-00 against job-01 | supported when positive at p < 0.01 |
| Alternation in execution order | lag-1 autocorrelation of job-01's log counts | supported when negative at p < 0.01 |
| Reconfiguration size | Spearman of job-01's log counts against compiled-phase change | supported when positive at p < 0.01 |
| Sample-budget scaling | log2 of the median outside-block count ratio, job-01 over job-00 | acquisition-proportional at 0.5 or more, per-iteration below |
| Static X and Y errors | Pearson of per-setting contrast residuals across the jobs, per readout | reproduces when positive at p < 0.01 |
| Contrast stability | V(job-01) - V(job-00) per readout with its standard error | reported |

`--self-test` builds synthetic job-01 runs from job-00's counts under a fixed
per-setting cause, an alternation, a reconfiguration-size law, a
per-iteration burst, static residuals and drifting residuals, and requires
each reading to come out as generated. job-01's own 27 endpoints come from
`ascella_coherence_repeat.py --analyze RUN` with job-00's estimators.

**Outcome.** Job `6ef8e8db` ran on 2026-10-24 at 15:31 UTC
([retained run](../../results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/README.md),
[comparison](../evidence/ascella-order-coefficients/repeat-comparison.json)):
1,048,576 samples in 186 s for 1.032768 credits, all 27 endpoints qualifying.
The outside-block clicks follow the execution sequence (lag-1 -0.653, setting
Spearman -0.075) and grow with the samples (log2 ratio 0.83); the analyzer
residuals reproduce (X 0.974, Y 0.802) at a stable contrast of 0.97. Both jobs
report 186 s in total. No retained record separates acquisition time from
reconfiguration or other overhead, and the jobs ran six hours apart in
different orders, so the equal totals assign no marginal time to the further
524,288 samples; the case's per-sample estimate (about 34 s) is neither
confirmed nor bounded. A timing budget for larger sample counts needs
component timing or controlled repeats that vary only the budget.

## Response geometry of both jobs

[`ascella_response_geometry.py`](../../scripts/ascella_response_geometry.py)
writes one exploratory record over both runs,
[`response-geometry.json`](../evidence/ascella-order-coefficients/response-geometry.json),
with analytic references only. It settles which part of the analyzer deficit
a uniform gain explains and how the outside-block background splits.

**Gain relations.** A setting-independent complex gain g maps the ideal
coherence C(theta) = (1 - exp(-2i theta))/2 to g C(theta), which fixes five
linear relations among the sign-odd coefficients. Projecting each job's
simultaneous registered intervals onto them keeps the family coverage:

| Relation | job-00 | job-01 |
|---|---|---|
| X0 + Xc2 = 0 | -0.0276 [-0.0524, -0.0029] | -0.0303 [-0.0478, -0.0128] |
| Y0 + Yc2 = 0 | -0.0029 [-0.0276, 0.0219] | -0.0073 [-0.0248, 0.0102] |
| X0 - Ys2 = 0 | -0.0081 [-0.0328, 0.0167] | -0.0049 [-0.0224, 0.0126] |
| Xs2 + Y0 = 0 | -0.0120 [-0.0367, 0.0128] | -0.0174 [-0.0349, 0.0001] |
| Xc2 + Ys2 = 0 | -0.0196 [-0.0485, 0.0094] | -0.0254 [-0.0458, -0.0049] |

X0 + Xc2 excludes zero in both jobs and keeps its value under the
block-conditioned denominator (-0.0298, -0.0307), so dilution does not cause
it; Xc2 + Ys2 excludes zero in job-01 alone. The Y relations and the X-to-Y
relations hold. The X sign-odd response therefore departs from a scaled and
rotated ideal circle along its constant-minus-cos(2 theta) direction, while
the Y response and the X-Y phase relation stay within a common gain; job-01
also resolves X cos(4 theta) at 0.0143 [0.0041, 0.0245].

**Configuration response.** The 64 settings of each job compile to 30
distinct returned configurations: each block's arms 0 and 3 share one, and
arms 1 and 2 another. The theta-0 X and Y arms 0 and 3 compile to one
configuration, and the mutation arms 0 and 3 compile to the theta-1 direct
arms 0 and 3. The settings sharing a configuration agree within a job
(analyzer chi-square 23.0 on 21 and 15.8 on 21; direct 16.8 on 13 and 6.5 on
13). Pooled per configuration, the block-conditioned statistics agree between
the jobs on X (3.3 on 10 degrees of freedom, p 0.97) and Y (8.3 on 10,
p 0.59), with pooled residual correlations 0.997 and 0.965. The direct
statistic differs between the jobs at 25.5 on 10 (p 0.0045, one of three
readouts tested), carried by the dark constant moving from 0.2504 to 0.2547.

**Held-out prediction.** Job-00's inverse-variance gain-and-offset fit
predicts job-01's pooled configurations at chi-square 402 on 10 (X) and 106
on 10 (Y), in the full residual covariance its two shared parameters give the
predictions, against 3.3 and 8.3 for job-00's own configuration values. A uniform
gain and offset fail on held-out data; a fixed per-configuration response
predicts it within counting noise. These results support a reproducible
configuration-dependent analyzer response over the two acquisitions; they
name no calibration mechanism and set no equivalence margin on drift.

**Outside-block background.** One profile with a per-iteration amplitude,
n_jm = e_j d_m, fails: the pooled profiles of the four quartiles of
per-iteration outside total differ (likelihood ratio 407 on 21 degrees of
freedom in job-00, 921 on 21 in job-01). The lowest quartile (11 and 25
events per iteration) spreads over modes 4 to 11 with mode 10 at 0.16 and
0.11, and the highest quartile (325 and 656) follows the catalogue dark
profile with mode 10 at 0.38 and 0.39. The even- and odd-position pooled
profiles agree (9.3 and 8.1 on 7, p 0.23 and 0.32), but the phase slips mix
high and low iterations within each parity, so that split is weak; the
quartile split tracks the amplitude itself. The
Poisson fit n_jm = a_j f_m + b_j d_m, with the catalogue profile d fixed and
one profile f fitted, has a flat likelihood ridge; iterations whose
catalogue-shaped amplitude fits to zero pin it, so the catalogue-shaped
component carries 6,202 to 6,267 of 6,659 job-00 events and 12,289 of 13,268
job-01 events at every admissible point. Its log amplitude alternates
(lag-1 -0.65 to -0.71 in job-00, -0.71 in job-01), while the fitted
component (weight on modes 4 to 9) alternates weakly (-0.10 and -0.26). Both
components roughly double with the samples. The fit is descriptive and its
shares are model values: job-00's 0.93 exceeds the 0.90 the pooled
composition allows any exact catalogue share, because the catalogue
overpredicts mode 11; quartile-pooled Pearson residuals of 58 and 97 on 32
cells show structure the fit leaves; and the fitted profile f differs between
the jobs on modes 10 and 11. The alternation sits in a catalogue-dark-shaped
component; converting its amplitude into acquisition time needs a detector
gating model the records lack.

## Restricted physical models of the analyzer response

The per-configuration response reproduces across the jobs while a uniform gain
and offset fail, so the next question is whether one physical error of the chip,
shared by every configuration, produces it. Each configuration's returned
`computed_circuit` gives the provider's model of the 12-mode mesh: fixed
characterized couplers (Rx angles near 1.45 rad, identical in every setting)
and 126 heater phases that all change between settings. A shared error family
perturbs that mesh identically in every setting, so one parameter set predicts
all three readouts. The families follow the Belenos mesh models of
[`qd_belenos_mesh.py`](../../scripts/qd_belenos_mesh.py) (`predict`,
`static_cross_validation`):

| Family | Parameters | Mechanism |
|---|---|---|
| nominal | none | the returned circuit as reported |
| dephasing | sigma | independent Gaussian heater phase noise, exact density-matrix channel (`channel`) |
| dephasing + heater gain | sigma, kappa | every returned phase in [0, 2 pi) scales to (1 + kappa) phi |
| dephasing + thermal crosstalk | sigma, c | every phase gains c times the sum of its mesh neighbors' phases (`neighbours`) |
| dephasing + coupler offset | sigma, delta | every coupler angle shifts by delta |
| dephasing + coupler noise | sigma, sigma_theta | independent Gaussian coupler-angle noise, exact channel |
| static heater offsets | 126 offsets, prior width tau 0.1 and 0.3 rad | fixed offset per heater, maximum a posteriori, pure-state propagation |

**Fit.** Each family is fitted on job-00 alone by maximum likelihood of the
block-conditioned four-mode multinomial (n0 to n3 of every setting, all
readouts and the mutation block), from the zero-perturbation start, so the fit
needs no seed. The static family keeps both prior widths and selects neither.

**Score.** Each fitted family predicts job-01's pooled configuration
statistics of the X and Y readouts (10 configurations each). The held-out
statistic is the quadratic form of the residuals in job-01's multinomial
variances plus J C J^T, with C the fitted parameters' covariance (inverse
observed information, plus the prior precision for the static family) and J
the prediction Jacobian. The direct readout's dark constant moved between the
jobs (0.2504 to 0.2547), which no static model can follow, so its held-out
statistic is reported and decides nothing.

**Decision.** A family explains the analyzer response when both held-out X and
Y statistics give p > 0.01 on 10 degrees of freedom and its predicted
block-conditioned X0 + Xc2 for job-01 lies inside job-01's projected
simultaneous interval of that relation. A mechanism is named only when a family
passes and every family nested in it without the distinguishing term fails.
When no family passes, the shared-error families tested here are rejected as
the source of the configuration response, which then needs per-configuration
calibration error outside this list.

**Outcome.** [`ascella_physical_models.py`](../../scripts/ascella_physical_models.py)
writes [`physical-models.json`](../evidence/ascella-order-coefficients/physical-models.json).
Every setting's block-conditioned multinomial carries a fixed in-block
background: the setting's outside-block count, shared over modes 0 to 3 by
the catalogue dark rates (354, 392, 314 and 80 per second against 14,797 on
modes 4 to 11). It accounts for the few counts in cells the mesh leaves dark.
Job-01's background term uses job-01's own outside counts; that moves its
predicted statistics by about 2e-4 against residuals of 0.02 to 0.06. The
covariance C of the low-dimensional families is the inverse expected (Fisher)
information, in place of the observed information the paragraph above names;
the static families use the observed information, the exact Hessian of the
posterior at its mode, which Newton steps from the L-BFGS endpoint reach.
Each left-out fit of that record starts from the full-data mode, so the
omitted configuration's counts choose the basin of a posterior that can hold
several; the [training-only refit](#leave-one-configuration-out-from-training-data)
replaces that column. No preregistered family passes, so the record names no
mechanism.

| Family | Job-00 X / Y | Job-01 held-out X / Y | Left-out X / Y, full-data start, counting only | Predicted X0 + Xc2, job-01 |
|---|---|---|---|---|
| nominal | 343 / 75 | 663 / 238 | 343 / 75 | 0.000 |
| dephasing (sigma 0.022 rad) | 320 / 73 | 618 / 236 | | 0.000 |
| heater gain (kappa 0.0014) | 283 / 55 | 527 / 167 | | -0.005 |
| thermal crosstalk | 319 / 78 | 616 / 241 | | -0.001 |
| coupler offset | 326 / 93 | 628 / 241 | | 0.001 |
| coupler noise | 320 / 73 | 617 / 235 | | 0.000 |
| static heater offsets, tau 0.1 | 55 / 33 | 53 / 46 | 287 / 95 | -0.022 |
| static heater offsets, tau 0.3 | 41 / 22 | 39 / 30 | 300 / 134 | -0.025 |
| detector efficiency (supplementary) | 254 / 43 | 465 / 119 | | -0.002 |
| static coupler offsets, tau 0.1 (supplementary) | 45 / 18 | 59 / 32 | 196 / 64 | -0.022 |
| static heater 0.3 and coupler 0.1 offsets (supplementary) | 7 / 9 | 7 / 13 | 266 / 800 | -0.026 |

Each entry sums ten configurations of one readout. The job-00 column is
descriptive, because the fit used those counts. Job-01's block-conditioned
X0 + Xc2 reads -0.0307 [-0.0483, -0.0131].
- The one- and two-parameter families fail in and out of sample and leave
  X0 + Xc2 at -0.005 or above. Each family is rejected as the source of the
  analyzer response in the form fitted: homogeneous independent Gaussian
  heater phase noise, a uniform heater gain, nearest-neighbor thermal
  crosstalk, a uniform coupler offset, homogeneous coupler noise and per-mode
  detection efficiency. Correlated or drive-dependent phase noise lies
  outside these families. The efficiency fit's mode-2 term runs to its -0.5
  bound; the rejection is that fit's, and a symmetry argument at theta = 0
  constrains only X0 + Xc2 + Xc4, so it does not exclude efficiency by itself.
- Shared static heater offsets (rms 0.060 and 0.137 rad) or coupler offsets
  (rms 0.039 rad) reproduce X0 + Xc2 and correlate with job-01's
  configuration residuals at 0.96 to 0.98 on X. Each kind alone fails
  job-01, with the same misfit in and out of sample. Heater and coupler
  offsets together (258 parameters) pass job-01: X 7.0 (p 0.72) and Y 12.6
  (p 0.25) on 10, with X0 + Xc2 at -0.026.
- That pass tests reproducibility, which job-00's raw configuration values
  already give (3.3 and 8.3 on 10). Refitted without one configuration, the
  static families transfer only part of the response. They lower the
  left-out X statistic from the nominal mesh's 343 to between 196 (coupler
  offsets) and 300, still 20 to 30 times the counting noise. Only coupler
  offsets lower Y (64 against 75), and the combined family raises it to 800.
  The offsets reproduce each configuration they were fitted on far better
  than one they were not.
- That column starts each left-out fit from the full-data mode and scores it
  in counting variance alone. The training-only refit below, scored with the
  fitted-prediction variance, supersedes it.

The X0 + Xc2 departure and the X residual pattern are therefore
configuration-dependent responses of the compiled circuits that reproduce
across the jobs. The tested low-dimensional families fail; the static
families reproduce the fitted configurations and predict left-out ones
poorly (next section). The physical cause stays unidentified: these fits
neither show that the underlying errors are independent between
configurations nor exclude every shared error of the chip. The supplementary
families and the leave-one-configuration-out test were added after the
preregistered table and decide nothing. The fitted families replay within
1e-3 relative plus 1e-8 absolute across BLAS builds, the unfitted nominal
family at the certificate tolerance.

### Leave-one-configuration-out from training data

[`ascella_configuration_holdout.py`](../../scripts/ascella_configuration_holdout.py)
writes [`configuration-holdout-unclipped-light.json`](../evidence/ascella-order-coefficients/configuration-holdout-unclipped-light.json).
It supersedes [`configuration-holdout.json`](../evidence/ascella-order-coefficients/configuration-holdout.json),
built while the static fit clipped the block light at 1e-9: an L-BFGS path from
zero that crosses a clipped cell takes another branch, and the combined
family's fold 3 there sits in a local mode 4.36 higher in negative log
posterior. The sums below are unchanged at the precision shown.
For each static family and each of job-00's 30 configurations, the fold fit
removes the configuration's settings and reaches the posterior mode from the
zero start, so neither the start nor the mode selection reads the left-out
counts. The left-out X and Y statistics are scored in their counting variance
v plus the local prediction variance g C g^T, with C the inverse posterior
Hessian of the fold fit and g the statistic's analytic gradient over the
offsets. The folds share 28 or 29 training configurations, so the sums below
are descriptive and carry no chi-square reference. The criterion was fixed
before the run (plan `ascella-configuration-holdout-training-only`): a sum of
30 or more on 10 configurations for X or Y keeps the shortfall with the
prediction uncertainty included; a sum below 20 with a median
prediction-to-counting variance ratio above 1 reads as weakly identified
predictions rather than a rejection.

| Family | Left-out X / Y, counting only | Left-out X / Y, with prediction variance | Median prediction / counting variance, X / Y |
|---|---|---|---|
| nominal | 343 / 75 | 343 / 75 | 0 / 0 |
| static heater offsets, tau 0.1 | 342 / 171 | 205 / 88 | 0.63 / 0.62 |
| static heater offsets, tau 0.3 | 476 / 123 | 167 / 45 | 0.82 / 0.61 |
| static coupler offsets, tau 0.1 | 257 / 109 | 87 / 36 | 0.76 / 0.60 |
| static heater 0.3 and coupler 0.1 offsets | 535 / 1114 | 27 / 52 | 12.7 / 2.2 |

- From training data alone, every static family predicts left-out
  configurations worse in counting variance than the full-data start did
  (X 257 to 535 against 196 to 300), and all four do worse than the returned
  mesh on Y (109 to 1114 against 75).
- With the prediction variance, every family stays at 30 or more on 10 for
  X or Y, so the shortfall stands under the preset criterion. The combined
  family's X sum of 27 comes with a median prediction variance 12.7 times
  the counting variance: its X predictions are weakly identified rather than
  confidently wrong, and its Y sum of 52 carries the shortfall.
- The prediction variance is the local quadratic approximation at each fold
  mode; a posterior with distant modes can carry more uncertainty than it
  shows. Confidence that no static error of the returned mesh model predicts
  left-out configurations is medium. It would rise if a mesh model with a
  drive-dependent heater response also failed this test, and fall if a
  shared family's standardized sums came within twice the configuration
  count.

### Drive-dependent heater response under the same folds

Ascella's control path maps voltages to phases by phi = A V^2 + b
([literature](../notes/quandela/literature.md), 2306.00874 SI S-IV), so a
heater's power is linear in its commanded phase and an error of its fitted
slope shifts the realized phase in proportion to the drive. The family adds
one slope k_h per heater to the tau-0.3 heater offsets: heater h realizes
phi + a_h + k_h phi, with phi the returned phase in [0, 2 pi) as the drive,
a_h under N(0, 0.3^2) and k_h under N(0, 0.1^2), whose spread at the mid
drive pi (0.31 rad) matches the offset prior (252 parameters).
[`ascella_configuration_holdout.py --drive`](../../scripts/ascella_configuration_holdout.py)
fits it under the folds and score of the section above and writes
[`heater-drive-holdout-heater-basis.json`](../evidence/ascella-order-coefficients/heater-drive-holdout-heater-basis.json).
The family runs as the heater basis (1, phi) of the next section, with each
heater's offset and slope adjacent among the coefficients;
[`heater-drive-holdout.json`](../evidence/ascella-order-coefficients/heater-drive-holdout.json),
written while the offsets and slopes formed two blocks, keeps its bytes.
The reordered L-BFGS path from zero reaches another mode in two folds, 0.13
lower in negative log posterior on left-out configuration 20 and 0.39 higher
on 23, which serves no readout; the X sum moves from 36.05 to 36.09 and every
figure below is unchanged at its quoted precision.
The family, its single prior width and the reading of each outcome were fixed
in step `drive-dependent-heater-family` of plan
`ascella-configuration-holdout-training-only` before the run: a sum of 30 or
more for X or Y keeps the shortfall; both sums below 20 read as weak
identification when a median variance ratio exceeds 1 and as prediction of
left-out configurations otherwise; any other outcome is inconclusive.

| Family | Left-out X / Y, counting only | Left-out X / Y, with prediction variance | Median prediction / counting variance, X / Y |
|---|---|---|---|
| nominal | 343 / 75 | 343 / 75 | 0 / 0 |
| static heater offsets, tau 0.3 | 476 / 123 | 167 / 45 | 0.82 / 0.61 |
| heater offsets 0.3 and drive slopes 0.1 | 474 / 186 | 36.1 / 24.8 | 10.4 / 2.1 |

- The X sum of 36.1 keeps the shortfall under the preset criterion: with its
  prediction variance included, the drive-linear family still misses the
  left-out X statistics, and every fold mode is positive definite (lowest
  Hessian eigenvalue 0.86).
- The X predictions carry a median prediction variance 10.4 times the
  counting variance, so most of the drop from 167 to 36 comes from wider
  predictions rather than closer ones; the counting-only sums (474 and 186)
  match or exceed the offset family's. The Y sum of 24.8 sits in the
  inconclusive band.
- Confidence that no shared static or drive-linear heater error of the
  returned mesh model predicts left-out configurations rises from medium to
  medium-high. The drive is the returned phase with its zero at 0: the
  passive phase b, which sets where the provider wraps a heater's drive, is
  absent from the returned circuit, and a per-heater wrap point, a quadratic
  term in the drive and crosstalk through A stay outside the family. A family
  with those terms whose standardized sums fall below 20 with variance ratios
  at most 1 would lower it.

### Polynomial and harmonic drive responses

The drive-linear family above is one member of a wider class: a heater's
drive is fixed by its returned phase, so an error in its phase-voltage map
shifts it by some function of that phase. The passive offsets b of
(0.1 +- 1.2) rad ([2306.00874](../notes/papers/2306.00874.md), SI S-IV) set
where each heater wraps, and a quadratic drive term bends the response; both
lie outside the drive-linear family.
[`ascella_drive_response.py`](../../scripts/ascella_drive_response.py) shifts
heater h of configuration c by sum_k b_k(phi_ch) w_hk under independent
N(0, tau^2) priors on the coefficients, in two bases:

- polynomial: shifted Legendre polynomials of the drive (phi mod 2 pi) / 2 pi
  to order 1 or 2, which place every heater's wrap at phi = 0;
- harmonic: 1, cos(j phi) and sin(j phi) to order 1 or 2. Each heater wraps at
  its own unreported offset b_h, and a per-heater response to the drive is a
  2 pi-periodic function of the returned phase whatever the wrap, which the
  harmonics expand without one.

Order 0 is the static heater-offset family, and the drive-linear family is
the basis (1, phi) with its own widths for the two functions
(`static_light` evaluates both through one heater basis). Each family is fitted on all of
job-00 and scored on job-01 as in the physical-model table, and runs the
training-only folds of the section above on the 19 configurations that serve
the X or Y readout, from the zero start. The reading is that section's,
fixed before this run: a standardized sum of 30 or more on 10 for X or Y keeps
the shortfall, and a sum below 20 with a median prediction-to-counting
variance ratio above 1 reads as weakly identified predictions.
[`drive-response.json`](../evidence/ascella-order-coefficients/drive-response.json)
holds the outcome:

| Family | Coefficients | Job-00 X / Y | Job-01 held-out X / Y | Left-out X / Y, counting only | Left-out X / Y, with prediction variance | Median prediction / counting variance, X / Y |
|---|---|---|---|---|---|---|
| polynomial, order 1, tau 0.3 | 252 | 3.7 / 5.7 | 5.4 / 10.8 | 539 / 225 | 32 / 28 | 10 / 2.8 |
| polynomial, order 2, tau 0.3 | 378 | 1.2 / 1.9 | 4.0 / 9.0 | 426 / 94 | 7.6 / 3.9 | 32 / 22 |
| harmonic, order 1, tau 0.3 | 378 | 1.3 / 1.7 | 4.0 / 9.4 | 386 / 103 | 3.5 / 3.3 | 104 / 20 |
| harmonic, order 1, tau 0.1 | 378 | 1.9 / 3.1 | 4.0 / 12.6 | 387 / 133 | 14.8 / 7.1 | 21 / 6.5 |
| harmonic, order 2, tau 0.3 | 630 | 1.2 / 1.2 | 4.3 / 6.7 | 564 / 127 | 1.5 / 1.0 | 485 / 182 |

- Every family fits job-00 within its counting noise and passes job-01 with
  X0 + Xc2 at -0.026 to -0.028, inside the interval. That tests
  reproducibility, which job-00's raw configuration values already give.
- The order-1 polynomial spans the drive-linear family's functions under one
  prior width for both, and it keeps the shortfall on X (32) under the preset
  criterion, as the drive-linear family does (36.1); its Y sum of 28 lies
  between the thresholds.
- The other four predict left-out configurations with a median prediction
  variance 6.5 to 485 times the counting variance, and their sums fall below
  20: the 29 training configurations do not determine their left-out
  predictions, so the test neither rejects nor supports them. Their point
  predictions do worse than the returned mesh on every readout (X 386 to 564
  against 343, Y 94 to 133 against 75).

The harmonic families carry each heater's wrap point and the order-2
families a quadratic drive term, the terms the drive-linear section left
outside its family, and 29 training configurations do not identify them.
They neither meet that section's lowering condition (sums below 20 with
variance ratios at most 1) nor sharpen the shortfall, so its medium-high
confidence stands. A hardware case that repeats one configuration under many
perturbed compilations would constrain these coefficients: confidence would
rise if the shortfall remained under them and fall if they predicted
left-out configurations within the preset criterion.

The posteriors of these 252 to 630 coefficients hold several modes, and which
one an L-BFGS path from zero reaches follows the rounding of the BLAS kernel
and of numpy's SIMD loops: under a forced SSE-only OpenBLAS kernel one
order-1 harmonic family reaches a mode 0.009 lower in negative log posterior
than under the host kernel. The record is written and replayed under the
kernel pair every gate path sets (`ci/run_gates.py`, `ci/pr_checks.sh` and the
audit workflow): the OpenBLAS Haswell kernel and numpy's x86-64-v3 loops with
AVX-512 dispatch off, which every x86-64-v3 runner shares. The static fit's block light
is the normalized |psi|^2 without a clip: the order-2 harmonic family puts a
fold's cell below 1e-9, where a clipped light zeroed its derivative and the
Hessian difference read the kink as eigenvalues near -7e5, so Newton steps
could not certify the mode. The floor now guards only the setting
probabilities, which the in-block background keeps above it on every setting
of these runs; `physical-models.json` replays unchanged under that path.

## Perturbed-compilation case (job-02)

Plan
[`ascella-perturbed-compilation-case`](../state/plans/ascella-perturbed-compilation-case.json)
fixes the setting, the perturbation and the readings below before any
acquisition. Job-00 and job-01, both at compilation seed 0, return identical
heater phases and couplers for all 30 configurations, so the service compiles
a submitted unitary deterministically and every configuration answers with
one mesh. Every heater family above therefore predicts each configuration's
error from that one mesh, and 29 training configurations leave the drive
coefficients unidentified. On Belenos the service fits the occupied input
column from random starts that `compilation_seed` selects, and distinct seeds
serve distinct meshes of the same target
([form-dwell findings](../notes/quandela/form-dwell-decomposition.md)).
Repeating one logical setting at many seeds holds its ideal output fixed
while the heaters move.

**What it measures.** Job-02 submits theta2-x-arm0 (configuration 13 of
job-00, theta 2 pi/5, phi +pi/4, X readout) 64 times at 8,192 samples per
iteration. Every eighth position, starting at position 0, runs at seed 0,
job-00's mesh. The other 56 positions run at the nonzero values of the ANU
QRNG draw
[`draw-2026-10-25T182813Z.json`](../evidence/anu_qrng/draw-2026-10-25T182813Z.json),
taken in index order (indices 0 to 55, with no repeat or zero among them).
The setting carries the largest X residual of the drive-linear training-only
folds: observed 0.8813 against 0.9309 predicted, standardized -4.21. Its
prediction variance is small, so the residual reflects the model rather than
an unidentified fit. Readings, each at alpha 0.01:

| Reading | Statistic | Reading rule |
|---|---|---|
| R1, compilation dependence | dispersion of the block-conditioned X statistic over the distinct served meshes against the anchors' dispersion, by label permutation | dependent when the perturbed dispersion exceeds the anchors' |
| R2, prediction | each heater family fitted on job-00 scored on the perturbed iterations in counting plus fitted-prediction variance | shortfall at or above the chi-square 0.999 quantile on the iteration count; predicted below its 0.97 quantile with median variance ratio at most 1 |
| R3, identification | each family refitted on job-00 plus job-02 and rescored on the 19 training-only folds | the 30-on-10 and below-20 rule of the training-only folds |

Every per-heater family, static offsets included, predicts that the served
mesh moves the X statistic. A null R1 at the design's power therefore refutes
per-heater phase error as the cause of the configuration response and moves
the search to compile-independent elements: the source, the detectors and the
couplers' fixed angles. A dependent R1 with an R3 shortfall under identified
coefficients raises the confidence that no heater family explains the
response. R3 sums below 20 with variance ratios at most 1 lower it. The
service's behavior at nonzero seeds on Ascella is known only once the job
returns. If the returned `computed_circuit` values realize fewer distinct
heater-phase vectors than seeds, R1 to R3 read the distinct set and the
record states the collapse. A single distinct mesh reads as "seed ignored"
and decides nothing about the heaters.

**Why simulation cannot answer it.** Local SLOS returns the ideal statistic
for every seed. The question is how Ascella's heaters err when the same
target is compiled onto other phases, and the served meshes are unknown
until the job returns: Perceval does not pass `compilation_seed` to the local
optimizer.

**Sizing.**
[`compilation-design.json`](../evidence/ascella-order-coefficients/compilation-design.json),
written by
[`scripts/ascella_compilation_design.py`](../../scripts/ascella_compilation_design.py),
sizes the case before acquisition. It stands in for the served meshes with
248 phase vectors of the returned layout that reproduce the setting's
twelve output intensities to 1e-6, found from deterministic starts spread
over the torus. Their heaters sit a median 1.57 rad from job-00's, and 84 %
move by more than 0.5 rad. It plants each family's job-00 posterior mode as
the device response. At 56 perturbed and 8 anchor iterations of 8,192
samples:

| Planted family | Planted X spread | R1 power | Detectable X SD at power 0.9 | R3 median ratio X / Y, without job-02 | with job-02 |
|---|---|---|---|---|---|
| static heater offsets | 0.115 | 1.000 | 0.0039 | 0.96 / 0.61 | 0.25 / 0.25 |
| drive-linear | 0.174 | 1.000 | 0.0041 | 6.86 / 2.28 | 0.54 / 0.52 |
| polynomial order 1 | 0.141 | 1.000 | 0.0041 | 4.85 / 4.65 | 0.55 / 0.55 |
| harmonic order 1 | 0.140 | 1.000 | 0.0041 | 135 / 38 | 0.90 / 0.76 |

R1 detects a compilation-induced standard deviation of 0.004 in the X
statistic, a twelfth of the setting's 0.05 residual. Twenty-four perturbed
iterations would leave the harmonic family at a median ratio of 3.15 on X.
The R3 ratios use the leave-one-out approximation of each fold, the full-data
posterior Hessian less the left-out configuration's information. Without
job-02 the approximation gives the training-only folds' recorded ratios to
within a factor of 2.2 (drive-linear X 6.86 against 10.4, polynomial order 1
X 4.85 against 10.2).

**Sizing correction.** The approval rested on `compilation-design.json`,
which keeps its bytes. That record sized R1 by the perturbed dispersion alone
as a chi-square, while R1 divides it by the dispersion of eight anchors. It
also credited R3 with the anchors' information, which R3 never trains on.
Its successor,
[`compilation-design-anchor-ratio.json`](../evidence/ascella-order-coefficients/compilation-design-anchor-ratio.json),
sizes the anchor-ratio test as noncentral F on 55 and 7 degrees of freedom
(critical ratio 5.84) and gives R3 only the perturbed iterations:
- R1 detects a compilation-induced X standard deviation of 0.013 at power
  0.9, not 0.004, and every planted family still gives power 1.000.
- At 56 + 8 iterations of 8,192 samples, the order-1 harmonic family's R3
  median ratio on X is 1.04. The corrected rule therefore chooses 16,384
  samples (1.032768 credits).

The run used the approved 8,192 samples. Its realized R3 ratios, 0.23 to
0.86 on X, meet the criterion.

**Seconds.** Expected 186 s against the 300-second `max_duration`. Job-00 and
job-01 each took 186 s for 64 iterations, at 8,192 and 16,384 samples, so
the 64-iteration job takes job-00's time unless a nonzero seed costs the
service compilation time that seed 0 does not. Whether the service recompiles
per seed is unobserved, and the expectation carries that uncertainty.

**Credits.** Ceiling and expectation 1.016384 credits: 1.0 per job plus
16,384 billed shots of one iteration at 1e-6, the tariff that billed job-00
exactly. The account's usage report reads 3.07 free credits spent on
qpu:ascella over 9 jobs, and 67.1 across all platforms.

**Request.**
[`scripts/ascella_coherence_request.py job-02`](../../scripts/ascella_coherence_request.py)
writes
[`job-02/cases.json`](../../results/quandela/cases/ascella_signed_coherence/job-02/cases.json),
and `--body job-02` freezes the body against the live processor record without
sending it. `--check` rebuilds the request and requires each iteration's seed,
the closed-form operator and the body entries. It also refuses a perturbed
unitary, a moved seed and a four-mode output width. The procedure is that of
job-00: `--preflight RUN`, then the owner's approval of this case, then
`--submit RUN APPROVAL`, then collection.

**Outcome.** The owner approved the case on 2026-10-25, and job `788097fb`
ran at 18:47 UTC
([retained run](../../results/quandela/runs/2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02/README.md),
[reading](../evidence/ascella-order-coefficients/compilation-reading.json)).
It returned 524,288 samples in 186 s for 1.016384 credits. Ascella honors the
seed: the 56 seeds served 56 distinct meshes, with heaters a median 1.58 rad
from job-00's, and the 8 anchors served job-00's mesh.

- **R1.** The X statistic moves with the served mesh. The perturbed iterations'
  dispersion is 7.08 times the anchors' (permutation p 0.0049). The 56 meshes
  read 0.865 to 0.915, a mean of 0.888 against the ideal 0.9045. The anchors
  read a mean of 0.883, as job-00 read 0.881.
- **R2.** Every job-00 fit misses the new meshes. All meshes share one set of
  fitted coefficients, so R2 takes the residuals' joint quadratic form in
  diag(v) + G C G^T. That gives 1150 for the static offsets, 649 for the
  drive-linear family, 771 for the order-1 polynomial and 201 for the order-1
  harmonic, against 94.5. The sum of individually standardized squares,
  which the first implementation scored until review noted the shared
  covariance, reads 1035, 223, 235 and 13.9. It hid the harmonic family's
  miss behind a median prediction variance 254 times the counting variance.
- **R3.** Refitted with job-02, every family is identified on the training-only
  folds (median variance ratios 0.23 to 0.86 on X) and keeps the left-out X
  shortfall (sums 85 to 377 on 10). Three of four keep it on Y; the harmonic
  family reads 20.9 there.

Under the preset reading, R1's dependence with R3's identified shortfall
raises the confidence that no per-heater error family of this document
explains the configuration response: high, and a family that predicted the
left-out configurations within the criterion would lower it. The heaters'
state matters, but static offsets and responses to each heater's own
returned phase cannot carry it. The untested candidates couple heaters:
thermal crosstalk between neighbors, coupler-angle error and mesh-dependent
loss. The 56 served meshes of one logical setting are the test set any such
model must predict.

## Heater-coupling families on the served meshes

Plan
[`ascella-heater-coupling-families`](../state/plans/ascella-heater-coupling-families.json)
fixed eight families, their priors, the training set and the reading before
any of them met job-02. Each family is fitted on job-00 alone, from the zero
start, and predicts the pooled X statistic of every one of job-02's 56 served
meshes. The meshes share the fitted parameters, so the score is R2's joint
quadratic form in counting plus shared prediction covariance: 94.46 or more
(chi-square 0.999 on 56) reads shortfall, and below 77.52 (0.97) with a
median prediction-to-counting variance ratio at most 1 reads predicted.
Two assumptions stand in for missing provider data. The returned phase in
[0, 2 pi) stands for the heater's drive power, because the passive offset is
absent from the returned circuit. The layout's (mode, column) distance
stands for physical distance. A screen that reads no mesh feature found no
association of the X statistic with execution index, its parity, its lag-1
neighbor or the outside-block count (every p above 0.19), so the reading
carries no sequence term. Before the plan was written, a feasibility screen
sized the kernel and loss priors against job-02's served phases and its
observed X spread, so that each family at its prior scale could produce the
observed compilation-induced spread. That choice favors the families and makes
a shortfall conservative.

[`heater-coupling.json`](../evidence/ascella-order-coefficients/heater-coupling.json),
written by
[`scripts/ascella_heater_coupling.py`](../../scripts/ascella_heater_coupling.py):

| Family | Fitted coupling (job-00) | Quadratic form | Median variance ratio | Predicted X SD over meshes | Reading |
|---|---|---|---|---|---|
| uniform crosstalk on mesh neighbors, with dephasing | c -0.00065 (SE 0.00026) | 937 | 0.003 | 0.0017 | shortfall |
| uniform coupler offset, with dephasing | delta 0.0021 (SE 0.0006) | 952 | 0.002 | 0.0018 | shortfall |
| static coupler offsets, tau 0.1 | RMS 0.039 rad | 762 | 1.19 | 0.0141 | shortfall |
| heater (tau 0.3) and coupler (tau 0.1) offsets | RMS 0.061 / 0.026 rad | 327 | 66 | 0.0282 | shortfall |
| crosstalk kernel, c_d for d = 0, 1, 2 modes within two columns | -0.0006, 0.0007, -0.0020 | 1107 | 0.009 | 0.0054 | shortfall |
| kernel with heater and coupler offsets | 0.0046, 0.0006, 0.0006 | 359 | 32 | 0.0272 | shortfall |
| drive loss, intensity e^{-gamma phi} | gamma -0.0049 (SE 0.0002) | 785 | 0.003 | 0.0059 | shortfall |
| drive loss with heater and coupler offsets | gamma -0.0083 (SE 0.0018) | 348 | 27 | 0.0284 | shortfall |

The 56 meshes read an X standard deviation of 0.0113 around 0.887. Their
mean counting variance accounts for 0.0044 of it, which leaves a
compilation-induced standard deviation of 0.0104. The predicted spreads in the
table carry no counting noise, so 0.0104 is their comparison. The families
fall into two groups. The coupling-only families fit job-00 to a
small coupling and predict too little spread. The families that carry
per-element offsets predict spread of the right size, but at mesh-by-mesh
positions that the observations do not follow. Across the 56 meshes, the
correlation between predicted and observed X lies between -0.04 and 0.19 for
every family. The record states these spreads and correlations beside each
reading as descriptions; they are not preregistered statistics. Both
drive-loss fits put gamma below zero, a gain with drive power, which no
heater loss produces. The loss-alone posterior on job-00 rises monotonically
for every gamma at or above zero (gradient +45,000 at zero), so a fit held to
physical loss lands on gamma 0, the nominal mesh, and the loss-with-offsets
family reduces to the heater and coupler offsets family; both readings stay
shortfall. The identification folds, refitted on job-00 plus
job-02's meshes and read under the training-only rule, keep the left-out X
shortfall for all four kernel and loss families: sums 180 to 347 on 10, with
median variance ratios 0.01 to 0.60, so the shortfall comes with identified
coefficients. They decide nothing under the plan.

Under the preset reading, no heater-coupling family of the plan predicts the
served meshes, and none of the twelve families scored on job-02 (the four
per-heater families of R2 and these eight) explains the configuration
response. Confidence that the mechanism lies outside the 126 heaters' and
132 couplers' static and drive-linear parametrizations: medium-high. Two
things would lower it: a family outside the plan that predicts job-02 from
job-00 under the same reading, or the layout distance proving a poor stand-in
for physical distance once the provider's heater geometry or applied-voltage
calibration is known. The candidates the plan leaves untested are
crosstalk that is nonlinear in drive power, crosstalk over the physical
rather than the logical layout, and an error outside the mesh that the
compilation still reaches, such as the source's spectral overlap with
mesh-dependent paths.

## Decomposition of the served-mesh response

Plan
[`ascella-mesh-response-decomposition`](../state/plans/ascella-mesh-response-decomposition.json)
examines job-02 beyond the X statistic. One ANU QRNG draw splits the 56
perturbed meshes into 28 exploration meshes and 28 held-out meshes
([`mesh-split.json`](../evidence/ascella-order-coefficients/mesh-split.json)),
and the held-out half enters only a confirmation step. Every screen on the
exploration half is retained with its trial count and a matched null.

**Block geometry and leakage**
([`mesh-decomposition.json`](../evidence/ascella-order-coefficients/mesh-decomposition.json)).
The block light splits into two parts:
- *A mean deficit that does not depend on the mesh.* Mode 0 loses 0.015 at the anchor mesh and 0.012 over the perturbed meshes, and modes 1 and 3 gain it. The anchor mesh read the same deficit in job-00.
- *A mesh-dependent scatter.* Over quiet iterations, which exclude the dark-shaped background bursts, the noise-whitened covariance of the block fractions reads counting noise at the anchor mesh (eigenvalues 0.15, 1.3, 2.5) and an excess in all three block directions over the perturbed meshes (2.5, 5.3, 6.0). The whitening carries the multinomial over block and outside clicks through the background subtraction.

The outside-block clicks are timed bursts with the catalogue dark profile
(lag-1 correlation -0.32 in execution order). In quiet iterations the dark
block output and the outside modes together hold at most 0.0025 of all
clicks, dark clicks included. Every static heater fit from job-00 would put
0.007 of the light there at its median mesh, and up to 0.12 at the worst.

**Exploration screens**
([`mesh-exploration.json`](../evidence/ascella-order-coefficients/mesh-exploration.json)):
- *Heater-phase quantization.* Rounding every returned phase to a grid (960 resolution and origin trials) reaches a per-mesh X correlation of 0.685. Against 100 scrambled-origin nulls at equal trials, p is 0.059, and the best resolution of 0.35 rad wrecks job-00's likelihood.
- *Scalar mesh features.* Total phase, squared phase, near-wrap count and sensitivity norms track the X statistic with |r| at most 0.17.
- *The dark block output.* Mode 2 separates coherent error from noise. A coherent error moves the bright modes at first order and fills a dark output at second order. Incoherent noise fills it at the order it lowers contrast.
  - Uniform dephasing strong enough to produce the observed X deficit would put 0.005 of the block light into mode 2. The observed excess is 0.0005, ten times less.
  - The exploration meshes fill mode 2 with 4.3 counts per quiet iteration against 0.8 at the anchor, overdispersed across meshes (p 0.003). The eight outside modes together gain about as much as mode 2 alone, so the mesh-dependent error stays near the logical block.
  - Mode-2 counts follow neither the bright modes' counts nor their shares (|rho| at most 0.23), which excludes detector crosstalk from the neighbors.

**Twelve-output likelihood**
([`twelve-output.json`](../evidence/ascella-order-coefficients/twelve-output.json),
[`scripts/ascella_twelve_output.py`](../../scripts/ascella_twelve_output.py)).
Every block-conditioned fit above was blind to light leaving the block. The
twelve-output likelihood scores every output, with each iteration's
background weight profiled against the catalogue dark profile. The chip
factors as O M I. Because the service fits only the occupied column, an
output stage O acts on the target column every mesh shares. An input
admixture I reaches the outputs through each mesh's unconstrained columns.
Each family below is fitted on job-00 alone and scored on the exploration
meshes over the three block coordinates (threshold 129.8 on 84):

| Family | Gain over nominal on job-00 | Predicted leak | Exploration quadratic form | Per-mesh X correlation |
|---|---|---|---|---|
| nominal mesh | 0 | 0 | 1975 | -0.05 |
| output stage, neighbor couplings | 447 | 0.0006 | 1545 | -0.01 |
| input stage, admixture into the other inputs | 822 | 0.0016 | 1305 | 0.14 |
| both stages | 957 | 0.0018 | 1387 | 0.15 |

Every family reads shortfall. The output stage, fitted across job-00's 30
configurations, predicts this setting's X at 0.904 against the observed
0.887. A fixed output-side map therefore cannot carry the setting's deficit
while it also fits the other configurations.

**Source and detector families**
([`source-detector.json`](../evidence/ascella-order-coefficients/source-detector.json),
[`scripts/ascella_source_detector.py`](../../scripts/ascella_source_detector.py)).
Source and detector terms act on each output's intensity after the mesh.
Detector efficiency scales output m by eta_m relative to mode 0; a uniform
transmittance cancels in the one-photon normalization, so a per-mode
transmittance is the same parameter. Photon bunching adds gamma I_m^2:
under threshold detection a two-photon emission that leaves both photons
in output m reads as one click there with probability |a_m|^4, and split
pairs fail the one-photon eligibility. Perceval 1.3.1's `NoiseModel`
reproduces that form to 1e-9 on a dense 12-mode unitary for distinguishable
and indistinguishable noise photons alike, and gives gamma 0.0098 at job-00's
platform g2 of 1.9 %. Every served mesh realizes the same target column from
input mode 0, so these families predict the same light on all 56 meshes.
The observed block fractions against one constant fraction vector form at
least 451.7 on 84 coordinates (466.0 at the exploration mean), against
129.8: no model whose block fractions stay constant over the meshes is
kept, and these families move theirs only through the per-iteration
background weight. They therefore test the mean deficit:

| Family | Parameters | Gain over nominal on job-00 | Exploration-mean X | Mean deficit in standard errors |
|---|---|---|---|---|
| nominal mesh | 0 | 0 | 0.904 | -7.8 |
| per-mode detector efficiency | 11 | 67.8 | 0.900 | -6.3 |
| bunching at the platform g2 | 0 | -20.9 | 0.904 | -8.1 |
| efficiency and platform bunching | 11 | 50.1 | 0.901 | -6.6 |
| efficiency and free bunching | 12 | 67.8 | 0.900 | -6.3 |

The observed exploration-mean X is 0.887. Every family misses the mean by
more than six standard errors of the observed mean (0.0115 over the square
root of 28). Job-00 rejects the bunching that the platform's g2 implies:
fitted freely on gamma itself, gamma stops at its bound 0, where the
negative log posterior still falls toward negative gamma (slope 1771), and
gamma 0.01 costs 18.2. The fitted efficiencies raise modes 1 and 3
by 4 % and 3 % and move the setting's X by 0.003 of its 0.017 deficit.
Source multiphoton emission, detector efficiency and transmittance therefore
carry neither the mean deficit nor the spread.

**Reading.** Six classes of model that see only the returned circuit fail on
job-02's meshes:
- fixed per-element offsets;
- drive responses of each heater's own phase;
- crosstalk on returned phases, uniform or by kernel;
- drive-power loss;
- fixed input- and output-stage maps;
- source multiphoton emission and per-mode detection.

The error is coherent, specific to the compilation, close to the logical block
and reproducible at the seed-0 mesh. Maring et al.'s control model accounts
for every one of these properties
([2306.00874](../notes/papers/2306.00874.md), pp. 3-4 and S-IV). The applied
voltages solve phi = A V^2 + b with a 126 x 126 crosstalk matrix A, more than
16,000 fitted parameters and an hourly recalibration. A served mesh's residual
error is then that calibration's error at its own voltages, which the
returned circuit does not carry. Confidence: medium-high. A model outside
these classes that passes the held-out confirmation would lower it. The
calibration snapshot or the applied voltages per iteration would test it
directly.

## Seed-repeat case (job-03)

Plan
[`ascella-seed-repeat-case`](../state/plans/ascella-seed-repeat-case.json)
fixes the readings below before acquisition. Every model fitted to job-02
treats each served mesh's X deviation as a deterministic function of that
mesh. Only the seed-0 mesh has been served twice under separate submissions:
job-00 read 0.881 there and job-02's anchors 0.883. The calibration reading
above predicts reproduction while the calibration in force stays the same,
and the hourly recalibration of Maring et al. can change it between jobs.

**What it measures.** Job-03 submits job-02's 64 settings of theta2-x-arm0
at 16,384 samples per iteration, each with job-02's compilation seed and
circuit parameters under the same setting name. The seeds are identifiers
that job-02's request takes from
[`draw-2026-10-25T182813Z.json`](../evidence/anu_qrng/draw-2026-10-25T182813Z.json).
The 8 seed-0 anchors keep every eighth position, the drift monitor. The 56
perturbed meshes take the off-stride positions in the order of values 0 to
55 of
[`draw-2026-10-26T033936Z.json`](../evidence/anu_qrng/draw-2026-10-26T033936Z.json),
so each mesh follows another predecessor than in job-02. Value 56 of that
draw seeds the permutation nulls. Readings, each at alpha 0.01:

| Reading | Statistic | Reading rule |
|---|---|---|
| M, mesh identity | settings whose `computed_circuit` equals job-02's under the same name | the readings below use the identical subset; with no perturbed mesh repeated, job-03's meshes join the held-out set of the decomposition plan and P1 is not read |
| A, anchor control | job-03 minus job-02 anchor mean X, in counting standard errors | a moved mean marks a calibration change between the jobs |
| P1, reproduction | Pearson r of the 56 perturbed X statistics between the jobs, against 20,000 label permutations | fixed per mesh at p below 0.01 with r at least 0.784; partly fixed at p below 0.01 with r below 0.784; not reproduced at p at least 0.01 |
| P2, replicated dependence | job-02's R1 anchor-ratio test on job-03 alone | dependent when the perturbed dispersion exceeds the anchors' |

A fully fixed per-mesh error reaches r = s_c^2 / sqrt((s_c^2 + s_n^2)(s_c^2
+ s_n^2 / 2)) = 0.880, with job-02's compilation-induced standard deviation
s_c = 0.01037 and counting variance s_n^2 = 1.965e-5 at 8,192 samples, halved
at job-03's 16,384
([heater-coupling reading](../evidence/ascella-order-coefficients/heater-coupling.json),
`observed_spread`). The 0.01 Fisher-z lower bound of that ceiling on 56
meshes is 0.784. P1 detects r = 0.459 at power 0.9, a fixed share of 52 % of
the compilation variance. Two readings are exploratory and decide nothing:
the Spearman correlation of per-mesh dark-output (mode 2) counts between the
jobs, and the Spearman correlation of each mesh's X change with the change
in its predecessor's L1 compiled-phase distance.

Reproduction with steady anchors places the error in a fixed property of
each mesh's voltages. No reproduction with steady anchors places it in the
compilation or the calibration in force at each job. A moved anchor mean
marks a calibration change between the jobs, and P1 then reads a lower
bound on the fixed share.

**Why simulation cannot answer it.** Local SLOS returns the ideal statistic
for every seed, and Perceval's `SimulatedComputer` uses `compilation_seed`
for random phase noise rather than for the remote compilation. Whether a
served mesh repeats its error depends on Ascella's calibration and control
loop, which no local model holds.

**Sizing.** At 8,192 samples, job-02's own, the ceiling reads 0.845 and its
lower bound 0.726 for 1.016384 credits; the owner chose 16,384 samples, which
raise both for 0.016 credits more.

**Backend and seconds.** `qpu:ascella`, available on 2026-10-26 at 03:40 UTC
with HOM 86.96 % and g2 2 %. Expected 186 s against the 300-second
`max_duration`: job-00, job-01 and job-02 each took 186 s for 64 iterations.

**Credits.** Ceiling and expectation 1.032768 free credits: 1.0 per job plus
32,768 billed shots of one iteration at 1e-6, the tariff that billed job-01
exactly. The usage report reads 70.35 free credits spent this
month across all platforms, 4.08 of them on `qpu:ascella`.

**Request.**
[`scripts/ascella_coherence_request.py job-03`](../../scripts/ascella_coherence_request.py)
writes
[`job-03/cases.json`](../../results/quandela/cases/ascella_signed_coherence/job-03/cases.json)
(digest `2fec6bf1…`), and `--body job-03` froze the body against the live
processor record without sending it (digest `64de4fe5…`). `--check` rebuilds
jobs 00 to 03 and their bodies. The procedure is that of job-02:
`--preflight RUN`, the owner's approval of this case, `--submit RUN
APPROVAL`, collection.

**Outcome.** The owner approved the case at 16,384 samples on 2026-10-26.
The platform reported a calibration state at 03:50 UTC, and job `e2f30d83`
ran at 03:57 UTC
([retained run](../../results/quandela/runs/2026-10-26T035018Z-qpu_ascella-ascella_signed_coherence-job-03/README.md),
[reading](../evidence/ascella-order-coefficients/seed-repeat-reading.json)).
It returned 1,048,576 samples in 186 s for 1.032768 credits.

- **M.** Every setting's `computed_circuit` equals job-02's under the same
  name: the service compiles a given seed to the same mesh nine hours and a
  calibration later.
- **A.** The anchors read 0.8858 against job-02's 0.8829, 1.48 standard errors
  apart: steady.
- **P1.** The 56 perturbed X statistics correlate with job-02's at r 0.885
  (p 5e-5), at the 0.880 ceiling of a fully fixed per-mesh error: fixed per
  mesh. The perturbed mean reads 0.8869 against 0.8868.
- **P2.** The compilation dependence replicates: dispersion ratio 36.8,
  p 0.00025.

The exploratory readings find no predecessor effect (rho 0.06, p 0.67) and
a weak dark-output correspondence (rho 0.18, p 0.18) at about four mode-2
counts per iteration.

Each served mesh carries its own analyzer error, and that error survives the
interval and the calibration between the jobs. Thermal history and drift
between jobs drop out as causes, and so does a calibration error that
changes with each hourly refit. The error is a fixed property of the map
from each mesh's returned phases to the light the chip emits, and the
returned circuit does not carry it. Every family of the decomposition
section, fitted on job-00, misses this deterministic per-mesh target. The
per-mesh statistics of job-02 and job-03 together form a reproducible test
set, job-03's at half job-02's counting variance.

## Element offsets fitted on the served meshes

Every element-offset family above was fitted on job-00 alone, where 30
configurations share the seed-0 mesh. Plan
[`ascella-fixed-mesh-error-model`](../state/plans/ascella-fixed-mesh-error-model.json)
fits them on the served meshes themselves: job-00 plus the 28 exploration
meshes of [`mesh-split.json`](../evidence/ascella-order-coefficients/mesh-split.json),
each mesh's X statistic pooled over job-02 and job-03 by setting name, at
about a third of job-02's counting variance. Two families, each the
block-conditioned static fit at its posterior mode: heater offsets under
N(0, 0.3²) with coupler offsets under N(0, 0.1²) (258 parameters), and the
coupler offsets alone (132). A family reaches the held-out half only when its
median prediction-to-counting variance ratio on the held-out designs stays at
or below 1 and its 28 exploration leave-one-mesh-out refits sum below 56.9,
the chi-square 0.999 quantile on 28. The folds share all but one training
mesh, so their residuals are dependent and 56.9 is the plan's fixed
threshold rather than the sum's calibrated distribution
([`fixed-mesh-error.json`](../evidence/ascella-order-coefficients/fixed-mesh-error.json),
[`scripts/ascella_fixed_mesh_error.py`](../../scripts/ascella_fixed_mesh_error.py)):

| Family | Held-out variance ratio | Leave-one-out sum | Leave-one-out X correlation | Held-out reading |
|---|---|---|---|---|
| heater and coupler offsets | 2.42 | 597 | 0.59 | not run |
| coupler offsets | 0.54 | 1133 | 0.08 | not run |

Any two of the 28 exploration meshes differ at all 126 heaters, and their
pairwise circular phase distances have a coefficient of variation of 0.052.
The served meshes sit nearly equidistant, so no smooth map from phase to
error can be learned by neighborhood, and the plan's Mantel screen does not
run.

The heater and coupler offsets failed both gates. Their leave-one-out
predictions still followed the unseen exploration meshes, at Pearson 0.59
and Spearman 0.55 (p 0.003). The offsets overshoot the spread, with a
regression slope of 0.40, and the mean residual of -0.014 is the
mesh-independent deficit no element offset carries. A complete-prediction
quadratic form reads shortfall for a partial predictor, so plan
[`ascella-fixed-mesh-confirmation`](../state/plans/ascella-fixed-mesh-confirmation.json)
tests that signal on the held-out half by an affine-invariant statistic. The
28 held-out predictions of one fit on the training set were frozen
([`fixed-mesh-frozen-predictions.json`](../evidence/ascella-order-coefficients/fixed-mesh-frozen-predictions.json))
and their digest committed with the plan before any held-out residual was
computed. The primary reading is the one-sided Pearson correlation of those
predictions with the held-out pooled X, by the t distribution on 26 degrees of
freedom at alpha 0.01 (critical r 0.437, power 0.86 at the exploration's 0.59)
([`fixed-mesh-confirmation.json`](../evidence/ascella-order-coefficients/fixed-mesh-confirmation.json),
[`scripts/ascella_fixed_mesh_confirmation.py`](../../scripts/ascella_fixed_mesh_confirmation.py)):

| Statistic | Held-out value |
|---|---|
| Pearson r | 0.318 (t 1.71, one-sided p 0.050) |
| reading at alpha 0.01 | not carried |
| Spearman correlation | 0.29 |
| r² against the 0.978² attenuation ceiling | 0.101, 10.6 % of the ceiling |
| one-sided 99 % Fisher-z upper bound of r | 0.661, 45.7 % of the ceiling |
| affine slope of observed on predicted | 0.22 |
| predicted against observed X spread | 0.0147 against 0.0102 |
| full quadratic form on 28 | 638, shortfall (as the plan expected) |
| scatter form on 27, one free constant | 506, shortfall (as the plan expected) |

The exploration correlation of 0.59 shrinks to 0.32 on the unseen half. That
is the regression to the mean expected of a 258-parameter fit selected on 28
meshes. The point estimate puts a tenth of the compilation-induced variance
with the static element offsets, and the data still admit up to 46 % at the
99 % upper bound, so the reading fails to establish the offsets as a carrier
without excluding a partial one. The returned circuit with fixed per-element
offsets does not reproduce the fixed per-mesh error. The design statement of
the decomposition section stands. Confidence that the error depends on a
quantity the returned circuit omits, such as the applied voltages under the
calibration in force: medium-high. Two things would lower it: a family that
carries the held-out meshes at alpha 0.01 under a fresh preregistration, or
new served meshes that the same fitted offsets carry under the reading the
new-seed case below fixes.
The applied voltages per iteration, which the provider has not published,
would test it directly. Both plans spent the held-out half on this one
reading, so a further offline family needs new served meshes.

## New-seed meshes case (job-04 and job-05)

Plan
[`ascella-new-seed-meshes-case`](../state/plans/ascella-new-seed-meshes-case.json)
fixes the predictors, the score and the acquisition rule below before any
new-seed job is submitted. The two plans above spent the held-out half on one
reading, which left the heater and coupler offsets at r 0.318 (p 0.050).
That reading sits between no effect and a partial carrier of up to 46 % of
the compilation-induced variance, and only meshes no fit has seen can
separate the two. Job-03 showed each served mesh's X statistic fixed across a
recalibration, so meshes served by later jobs join one test set.

**Predictors.** The served mesh is known only from the returned
`computed_circuit`, so the plan freezes each predictor's offsets rather than
its predictions
([`new-mesh-offsets.json`](../evidence/ascella-order-coefficients/new-mesh-offsets.json),
[`scripts/ascella_new_mesh_offsets.py`](../../scripts/ascella_new_mesh_offsets.py)).
A prediction is the static light of the returned mesh under those offsets.
The offsets and free masks were committed and pushed in 9e92be5 before any
seed was drawn. A later commit removed only an exact covariance digest,
which a last-bit BLAS change would break, so the record now reads digest
`bbf0ff94…` and replays within the fit bounds.

- **P-A** is the heater and coupler offsets fitted on job-00 plus the 28
  exploration meshes, the fit plan `ascella-fixed-mesh-confirmation` scored.
  Its frozen offsets reproduce that plan's held-out predictions to 9e-15.
- **P-B** is the same family fitted on job-00 plus all 56 perturbed meshes of
  jobs 02 and 03, pooled by setting name.

**Score.**
[`scripts/ascella_new_mesh_score.py`](../../scripts/ascella_new_mesh_score.py)
holds the contract as code, and its tests run it on the retained job-02 and
job-03 runs.
- **Mesh identity.** A served mesh is its returned `computed_circuit` with
  its `computed_input`.
- **What enters the primary.**
  - Anchors never enter it.
  - A mesh that jobs 00, 02 or 03 served is excluded.
  - A mesh served by both new jobs counts once, in job-04.
  - A job with fewer than three meshes, or a partial job, stays descriptive.
    Partial means a setting without counts or a status other than completed.
- **Primary statistic.** For each predictor, the Pearson r of predicted with
  observed block-conditioned X, both centered within each job. It is read
  one-sided by the t distribution on n − 1 − J degrees of freedom at alpha
  0.005 each, which is Bonferroni 0.01 over the two predictors.
- **Bounds.** The one-sided 99.5 % Fisher-z bounds use standard error
  1/√(n − J − 2). The share is r²/c² under the plug-in ceiling
  c² = s_c²/(s_c² + mean counting variance), conditional on the retained
  s_c² = 1.41e-4.
- **Anchor control.** Each job's anchor mean X minus job-03's reads moved when
  its magnitude exceeds s_c = 0.0119, which marks a gross calibration event.
  Job-03 reproduced every per-mesh error at the ceiling across a
  recalibration that moved the anchors by 0.00285. The control gates only the
  bounded outcome: centering removes an additive shift, and a calibration
  change cannot correlate frozen predictions with unseen meshes.

| Outcome | Condition | Reading |
|---|---|---|
| both carried | P-A and P-B at p below 0.005 | the returned circuit with element offsets carries the fixed per-mesh error, for the share between the bounds |
| P-A carried only | P-A alone | as above, for P-A's share |
| P-B carried only | P-B alone | as above; the carrier lies in offsets that the 28 exploration meshes left underdetermined |
| bounded | neither carried, every scored job steady, both upper shares below 10.6 % | the static element offsets carry less of the compilation-induced variance than the larger upper share |
| inconclusive: anchors moved | neither carried, a scored job moved | no bound |
| inconclusive | neither carried otherwise | no bound |

10.6 % is the held-out point estimate of the confirmation plan. Secondary and
descriptive: the Spearman correlation and the affine slope of the centered
values, and each job's dispersion ratio. Pooling with the 28 spent held-out
meshes is exploratory and decides nothing. The readings spend every new
mesh, so a family proposed after scoring needs further seeds or the applied
voltages that Perceval#799 requests.

**What it measures.** Job-04 submits theta2-x-arm0 (configuration 13 of
job-00, theta 2 pi/5, phi +pi/4, X readout) 80 times at 32,768 samples and
32,768 `max_shots` per iteration.
- **Anchors.** The seed-0 mesh of job-00 sits at every eighth position: 10
  anchors.
- **New seeds.** The other 70 positions take the usable values 0 to 69 of
  [`draw-2026-10-26T174307Z.json`](../evidence/anu_qrng/draw-2026-10-26T174307Z.json).
  A value is usable when it is nonzero, not a repeat and not one of job-02's
  56 seeds, taken in index order.
- **Job-05.** Job-05 continues the same seed sequence from usable value 70 in
  one of three frozen variants: `job-05-i80`, `job-05-i88` or `job-05-i96`.
  Job-04's provider-reported duration d4 alone picks the variant:
  - With job-04 complete and d4 at most 279 s, job-05 runs
    8·floor(min(96, 279·80/d4)/8) iterations.
  - A partial job-04, or d4 above 279 s, sends no job-05, and the reading
    runs on job-04 alone.
  - The score refuses a job-05 run of any other variant.
  - The rule reads completion and duration only, never an X count, so it
    selects nothing on the outcome.

**Why simulation cannot answer it.** Local SLOS returns the ideal statistic
for every seed, and Perceval's `SimulatedComputer` uses `compilation_seed`
for random phase noise rather than the remote compilation. Which mesh the
service serves at a new seed, and what X that mesh emits under Ascella's
calibration, exist only on the chip.

**Sizing.** Every Ascella job so far ran 64 iterations in 186 s, at both
8,192 and 16,384 samples. Fixed overhead per job cannot be negative, so
2.90625 s per iteration is an upper bound on the per-iteration time under a
linear duration model. 80 iterations then take at most 232.5 s, 67.5 s below
the 300-second `max_duration` the platform admits. The retained sources do
not say what happens when a job reaches that limit: truncation, error and
partial results all remain possible. That uncertainty is why the first job
runs 80 iterations, and why its measured duration sizes the second job
within the same 21-second margin that 96 iterations hold at the bound.

Job-03 billed 32,768 shots per iteration and collected only 16,384, so 32,768
samples per iteration double the observations at the credits already paid.
Going higher would raise the ceiling from 0.983 to 0.991 for under one point
of power. Ten anchors per job keep the stride-8 drift coverage.

Noncentral-t power and the probability that a true r of 0 ends bounded
(marginal, per predictor):

| Branch | Meshes | Critical r | Power at r 0.25 / 0.318 / 0.437 | Bounded if null | Credits |
|---|---|---|---|---|---|
| job-04 alone (stop rule) | 70 | 0.306 | 0.30 / 0.53 / 0.89 | 0.55 | 1.032768 |
| job-04 + job-05-i80 | 140 | 0.218 | 0.64 / 0.89 / 1.00 | 0.90 | 2.065536 |
| job-04 + job-05-i88 | 147 | 0.213 | 0.67 / 0.91 / 1.00 | 0.92 | 2.065536 |
| job-04 + job-05-i96 | 154 | 0.208 | 0.69 / 0.92 / 1.00 | 0.93 | 2.065536 |
| three jobs of 80 (alternative) | 210 | 0.178 | 0.85 / 0.98 / 1.00 | 0.99 | 3.098304 |

[`scripts/ascella_new_seed_sizing.py`](../../scripts/ascella_new_seed_sizing.py)
writes the table to
[`new-seed-sizing.json`](../evidence/ascella-order-coefficients/new-seed-sizing.json).
Two fixed jobs of 96 iterations reach 0.95 at r 0.318, but they place the
first job 21 s below an undocumented limit with no measurement behind it.

**Backend and seconds.** `qpu:ascella`, available on 2026-10-26 at 17:42 UTC
with HOM 87.46 % and g2 2.1 %, Perceval 1.3.0 on the worker. Expected at most
232.5 s for job-04 and at most 279 s for job-05, submitted one after the
other.

**Credits.** 1.032768 free credits per job: 1.0 per job plus 32,768 billed
shots of one iteration at 1e-6. Jobs 01 and 03 were billed exactly this
tariff, and job-03 collected half the shots it paid for. Two jobs come to
2.065536. The usage report reads 71.38 free credits spent this month across
all platforms, 5.11 of them on `qpu:ascella` over 11 jobs, which leaves
128.62 of 200.

**Request.**
[`scripts/ascella_coherence_request.py`](../../scripts/ascella_coherence_request.py)
writes the case directories under
`results/quandela/cases/ascella_signed_coherence/`:

| Case | `cases.json` | `job-body.json` |
|---|---|---|
| `job-04` | `abbe4e5a…` | `0f905efc…` |
| `job-05-i80` | `0f1f94e5…` | `134cb95d…` |
| `job-05-i88` | `87a926b7…` | `839ceb3b…` |
| `job-05-i96` | `c50b53d8…` | `5a5930ea…` |

`--body` froze each body against the live processor record without sending
it. `--check` rebuilds every job and its body, with the retained bytes of
jobs 00 to 03 unchanged. `ascella_coherence_repeat.run_record` attributes the
iterations of any count, and on the four retained runs it reproduces
`ascella_coherence_run.attributed` exactly.

The procedure:
1. Run `--preflight` on job-04.
2. Obtain the owner's approval of this case.
3. Run `--submit` on job-04 and collect it.
4. Apply the duration rule.
5. Run `--preflight` and `--submit` on the admitted job-05 variant, and
   collect it.
6. Run the score.
