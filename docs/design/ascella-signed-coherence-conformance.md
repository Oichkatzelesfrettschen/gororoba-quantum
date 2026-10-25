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
Its `--check` mode, run by gate core-record-check-06 (tests/test_cli_record_checks.py), validates the retained bytes: every
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
writes [`configuration-holdout.json`](../evidence/ascella-order-coefficients/configuration-holdout.json).
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
