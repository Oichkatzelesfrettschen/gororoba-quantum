# BDSC acceptance diagnostics and root-cause boundaries

This note analyses the retained qualification runs at commit
`365ed05d355de838bf6873f748be8d854438b101`. It supplements the
[qualification design](../../design/bdsc-qualification.md) and
[frozen runbook](../../runbooks/bdsc-qualification-case.md); it does not change
an approved case, a contrast, a margin, an epoch, or a retained record.
No provider read, acquisition, retry, QRNG draw, or additional expenditure is
authorized here. Epoch-1 interpretations remain exploratory while the
observation contract and the frozen complete readout remain outstanding.

## Evidence scope

The source review covers the current case generator, one-click readout,
collection path, Ascella control, submitted target columns, and run receipts.
Independent arithmetic below uses every one-click count vector of the 24
empty-mitigation settings in `tc-none-e1` and `mm-none-e1`, with each run's
receipt. The 24 default-mitigation settings and the compressed raw responses
are not replayed here. The reported 9/16 violated sum rules are the campaign's
exploratory readout, not an independently regenerated verdict in this note.

Source locations under `results/quandela/runs/`:

- `2026-10-21T162332Z-qpu_belenos-bdsc_qualification-tc-none-e1/`:
  `cases.json`, `submission.json`, `results.json`.
- `2026-10-21T165036Z-qpu_belenos-bdsc_qualification-mm-none-e1/`:
  `cases.json`, `submission.json`, `results.json`.
- `2026-10-21T122531Z-qpu_belenos-bdsc_qualification-tc-def-e1/`:
  `submission.json`.
- `2026-10-21T203428Z-qpu_ascella-bdsc_ascella_control-job-00/`:
  `results.json`.

A returned count is called a returned count, not an independently established
raw detector event. Relative `t_out` fields are sensitivity-model weights,
not calibrated absolute efficiencies or an acceptance certificate.

## The sum-rule conclusion

For orthonormal f,g, the ensembles {f,g}, {+,-}, and {+i,-i} each sum to the
same density operator. For a fixed effect F and correctly prepared inputs,

    p(+) + p(-) = p(f) + p(g) = p(+i) + p(-i).

The identity also survives every fixed linear trace-preserving preparation
channel: dephasing, a common coherent phase error, and a fixed unitary do not
alone invalidate it. A violation rejects the combined preparation,
common-effect, linear-observation and stationarity assumptions. It does not
isolate preparation error, nor does it exclude detector/acceptance effects.
A diagonal phase applied only at the output cannot change Fock intensities.
State-dependent compilation or errors remain possible, but must be separated
from conditioning and processing.

The actually analysed probability is one-click conditioned. With selected
unconditional effect G and acceptance effect D,

    p_s = Tr(G rho_s) / Tr(D rho_s).

The linear identity need not hold for this ratio. Correct states and a fixed
physical detector suffice to violate it when D is not scalar.

Exact countermodel: in the f,g basis choose D = diag(0.06, 0.04),
G = diag(0, 0.04). Both are positive and G <= D <= I. Perfect preparation gives
probabilities (0, 1, 0.4, 0.4, 0.4, 0.4) on (f,g,+,-,+i,-i), with both residuals
-0.2. No phase error, varying measurement, or incorrect preparation is needed.

## A receipt-predicted alternative explains the leading shift

Assume, only for a sensitivity calculation, an ideal requested output column
v and terminal detection weights w_m proportional to the reported `t_out`.
Then the conditional distribution is

    q_m = w_m |v_m|^2 / sum_j w_j |v_j|^2.

This uses ratios only. Values exceeding 100 are not interpreted as
probabilities. The weights are taken from each run's receipt without fitting
them to the measured histogram.

### Target-complement pair

The manifest sends f to mode 0, g to mode 12, and each of the four
superpositions to equal intensities on those two modes. Mode 12 is selected;
mode 0 is complementary. `tc-none-e1` reports w_0 = 109.69 and w_12 = 81.10.
Thus perfect inputs predict

    p(f) = 0, p(g) = 1,
    p(+) = p(-) = p(+i) = p(-i) = 81.10 / 190.79
                                     = 0.425074689449,
    Delta_R = Delta_I = -0.149850621102.

This prediction is inside the reported 0.375--0.437 superposition range and
has the sign and approximate size of the reported -0.17 sum-rule deficit.
It explains why apparently good basis endpoints do not exclude detector
imbalance: a single occupied mode stays certain after conditioning.
The two-mode acceptance anisotropy in this scenario is about 0.14985, not the
small acceptance deviation assumed in optimistic certificate planning.
It is not a measured bound on D.

### Middle-middle pair

The target maps e1 to equal intensity on modes 8 and 20, and e2 to modes 9
and 21. The latter mode of each pair is selected. The `mm-none-e1` receipt gives
w_8 = 99.75, w_20 = 59.40, w_9 = 84.98 and w_21 = 119.63. Therefore

    p(f) = 59.40 / (99.75 + 59.40) = 0.373232799246,
    p(g) = 119.63 / (84.98 + 119.63) = 0.584673280876,
    p(each superposition) = (59.40 + 119.63) / 363.76
                          = 0.492165163844,
    Delta_R = Delta_I = 0.026424247567.

The reported basis probabilities, about 0.356--0.370 and 0.547--0.590, need
not be attributed first to phase error. The receipt-weight model already
predicts their asymmetric direction and approximate scale. It is not an
explanation of every residual or a substitute for device calibration.

## Independently checked returned-count examples

The selected set is {12,13,16,18,19,20,21,22,23,4,6,7}.
The two 24-component vectors below are ordered by mode 0 through 23.

`tc-none-e1/out-m`:

    [171468,1524,241,20,121,1796,153,39,55,169,31,37,
     123810,44,10,32,55,52,40,29,72,29,29,24]

There are 299880 one-click records, 124445 selected records, 40 zero-click
records and 80 multiple-click records; the total is 300000. The selected
fraction is 0.414982659731. Of the one-click records, 1.5346% lie outside the
intended two-output support. On the intended outputs alone,

    n_12 / n_0 = 0.722058926447,
    w_12 / w_0 = 0.739356367946.

The ratio of these odds is 0.976604730480. Applying the receipt's inverse
weights as a sensitivity calculation gives 0.494081955497 on the intended
pair, or 0.487869865444 across all outputs. Neither number is an observed
probability, an admitted correction, or confirmatory evidence. out-m is the
closest TC superposition row to the receipt prediction; the full table below
carries the other eleven.

`tc-none-e1/out-f`:

    [280390,6533,1560,7684,279,1579,299,230,229,263,235,218,
     12,36,12,13,44,57,45,32,59,22,21,27]

There are 299879 one-click records, 1106 selected records, 92 zero-click
records and 29 multiple-click records. The selected fraction is
0.003688154222. However, 6.49896% of the one-click records lie outside the
intended single output, mode 0. A small selected fraction alone therefore
hides substantial wrong-mode response in other complementary outputs.

Removing a fraction d of returned records changes one bounded outcome
probability by at most d. If each of four settings drops at most 0.0006,
the sum-rule change caused solely by that removal is at most 0.0024.
That cannot account for a residual near -0.17. It does not bound the much
larger or state-dependent optical losses absent from the returned records.

## All 24 empty-mitigation rows against the receipt weights

Each row counts one-click records only. "Observed" is the selected fraction
over all one-click records, "receipt" the terminal-weight prediction above,
"support" the selected fraction on the intended outputs alone, "reweighted"
the support fraction after dividing each intended output's count by its
`t_out`, and "outside" the one-click share off the intended support. The
ideal selected value is 0, 1 or 0.5 for TC basis states and superpositions
and 0.5 for every MM row.

    TC   observed receipt support reweighted outside | MM  observed receipt support reweighted outside
    out-f  0.0037  0.0000  0.0000  0.0000   6.50%    | out-f  0.3696  0.3732  0.3690  0.4955   1.34%
    out-g  0.9860  1.0000  1.0000  1.0000   1.69%    | out-g  0.5473  0.5847  0.5498  0.4645   1.68%
    out-p  0.4013  0.4251  0.4030  0.4773   1.37%    | out-p  0.4632  0.4922  0.4655  0.4774   1.24%
    out-m  0.4150  0.4251  0.4193  0.4941   1.53%    | out-m  0.4900  0.4922  0.4949  0.5042   1.58%
    out-pi 0.3940  0.4251  0.3997  0.4738   2.44%    | out-pi 0.4769  0.4922  0.4793  0.4870   1.90%
    out-mi 0.4373  0.4251  0.4404  0.5156   1.42%    | out-mi 0.4886  0.4922  0.4899  0.4930   0.89%
    rev-f  0.0023  0.0000  0.0000  0.0000   1.35%    | rev-f  0.3559  0.3732  0.3608  0.4866   2.65%
    rev-g  0.9865  1.0000  1.0000  1.0000   1.61%    | rev-g  0.5899  0.5847  0.5846  0.4999   5.82%
    rev-p  0.3915  0.4251  0.3972  0.4712   3.09%    | rev-p  0.4679  0.4922  0.4711  0.4726   1.80%
    rev-m  0.3753  0.4251  0.3813  0.4546   2.96%    | rev-m  0.5085  0.4922  0.5083  0.5038   3.67%
    rev-pi 0.3944  0.4251  0.3955  0.4694   3.38%    | rev-pi 0.4854  0.4922  0.4890  0.4990   1.38%
    rev-mi 0.3937  0.4251  0.3997  0.4738   3.21%    | rev-mi 0.4751  0.4922  0.4771  0.4864   1.20%

The sum-rule residuals per template, observed against receipt-predicted:

    TC out: Delta_R -0.1734 (-0.1499), Delta_I -0.1584 (-0.1499)
    TC rev: Delta_R -0.2221 (-0.1499), Delta_I -0.2008 (-0.1499)
    MM out: Delta_R +0.0364 (+0.0264), Delta_I +0.0487 (+0.0264)
    MM rev: Delta_R +0.0306 (+0.0264), Delta_I +0.0147 (+0.0264)

The receipt weights account for 0.150 of the TC deficit: 86 to 95 percent of
it in the outward template and 67 to 75 percent in the reverse template. The
reweighted TC superposition fractions span 0.455 to 0.516 rather than sitting
at 0.5, and every reverse row lies below 0.475. A shared terminal-weight
model cannot produce that template split, so the reverse template carries
an additional response the receipts leave unexplained.

The MM basis rows reweight to 0.465 to 0.500 from raw values of 0.356 to
0.590, so the receipt weights carry most of the MM basis asymmetry. Two MM
superposition rows carry a setting-specific term that the selected fraction
cannot see. Reweighted to shares of the four intended outputs (ideal 0.25
each), rev-m reads mode 8 0.122, mode 20 0.246, mode 9 0.375, mode 21 0.258,
and rev-p reads mode 9 0.304. Modes 8 and 9 are both complementary, so an
8-to-9 exchange leaves the selected fraction unchanged. A terminal weight or
an acceptance filter acting on fixed output intensities cannot move counts
between f's outputs and g's outputs, because f and g occupy disjoint outputs;
the redistribution therefore requires coherent coupling of f's outputs into
g's in the transfer implemented for those settings.

Each setting carries its own `compilation_seed`, so a setting combines its
prepared relative phase with its own compilation of the transfer. rev-m and
rev-p alone do not separate a dependence on relative phase from one
compilation that realized the transfer badly. Drift is unlikely, though not
excluded: rev-m's neighbors in execution order, rev-f and out-f, reweight to
0.511/0.484 and 0.504/0.495. The epoch-1 data thus carry an acceptance-scale
explanation of the leading TC shift and a setting-specific coherent transfer
error in the reverse MM template. Neither displaces the other, and the
per-mode vectors, not the selected fraction, carry the second. The
[forensic reconstruction](#forensic-reconstruction-of-the-retained-belenos-runs)
shows that the returned circuits leave the requested relative phase free, so
the redistribution belongs to the implemented transfer if the returned circuit
describes what ran, which `returned_circuit_semantics` leaves unresolved.

## Separate even response shifts from phase-sensitive response

For a six-state cell define

    m_Z = (p_f + p_g)/2,
    m_X = (p_+ + p_-)/2,
    m_Y = (p_+i + p_-i)/2,
    d_X = (p_+ - p_-)/2,
    d_Y = (p_+i - p_-i)/2.

One fixed unconditioned effect has m_X = m_Y = m_Z. The d components describe
its two coherent quadratures. The reported common depression of all four
superpositions is primarily an even-component anomaly, not by itself a
phase-fringe measurement. Fit the even and odd components separately.

For a common filtered measurement in a two-dimensional test space, write
D = d0 I + d.sigma and G = g0 I + g.sigma. On Bloch direction n,

    p(n) = (g0 + g.n) / (d0 + d.n).

Test the model with 0 <= G <= D, not by forcing conditional probabilities
into a linear effect. Six probabilities generally do not identify all
parameters or the physical location of the filter. A feasible model is a
counterexplanation, not a unique root-cause assignment.

## Offline diagnosis before any new case

1. Bind each setting to its case, submitted body, QRNG indices, echoed seed,
   observation index and run. Preserve actual start/stop timestamps. The
   four-hour queue wait makes submission-time calibration potentially stale.
2. Export every per-mode count vector and every excluded category. Preserve
   selected probability and wrong-support probability separately.
3. Evaluate the ideal-column and receipt-weight scenarios without fitting.
   On default-mitigated outputs, keep the unmitigated scenario explicitly a
   counterfactual rather than a prediction of the processed estimator.
4. Evaluate complete submitted and returned circuit columns, including
   coherent phases. Matching parameter echoes proves attribution, not
   physical phase accuracy or preservation of a common measurement.
5. Fit successively richer diagnostic models: scalar acceptance; diagonal
   terminal weights; constrained G,D filtering; additive wrong-mode response;
   template/seed/epoch-dependent transfer. Use held-out settings or epochs
   for predictive checks. Do not use an unrestricted per-setting fit as an
   explanation.
6. Keep the frozen 96-observation formal readout unchanged. A receipt-weight
   adjustment is exploratory and never replaces its counts or likelihood.

A future separately approved matched output-swap probe can help separate
routing from terminal weights. For intended two-port odds o and stable
relative efficiency r, forward and swapped logical output assignments give
O_f = r o and O_s = o/r. Then sqrt(O_f O_s) = o and sqrt(O_f/O_s) = r.
This requires stable transfer apart from the declared swap, negligible or
modelled background, and complete outcome accounting. It is not a license to
relabel the already acquired masks or add settings to epoch 2.

## Forensic reconstruction of the retained Belenos runs

`scripts/bdsc_forensics.py` carries out steps 1 to 5 above over the five
retained qpu:belenos runs: the four first-acquisition jobs and the repeat of
the target-complement pair under default mitigation (`tc-def-e2`, job
`ee6fc975-ff80-4273-9360-70fc5243b9b1`). It writes
[forensics.json](../../evidence/bdsc/forensics/forensics.json), which gate
core-622 rebuilds.
For each of the 60 settings the record holds the observation index, the
requested and echoed seed, the parameter digest and its echo deviation (zero
on all 60), the mitigation request of the sent body, the run timestamps, the
plan source figures, the execution noise model, the 24 one-click counts with
the zero- and multi-click categories, and the hashes of the returned compiled
circuit and experiment. Every standard error and deviance below is a
reference value under independent Bernoulli trials per returned sample. That
observation law rests on `count_provenance` (unsupported under defaults) and
`uncorrected_observations` (unresolved), and the processing a
default-policy run received is unknown (`processor_record_completeness`).

### The returned circuit preserves output intensities, not phase

Each iteration returns a 24-mode circuit of 1150 components: 552 beam
splitters, 574 phase shifters and 24 barriers. On every setting its unitary
reproduces the intensities of the requested source column to a
total-variation distance of at most 2.5e-4. It does not reproduce the
column's relative phase. The overlap |<v|U e_6>|^2 is 0.99999 on the
target-complement f and g settings, each a single output, and ranges from
0.0067 to 0.949 on the middle-middle f and g settings, each spread over two
outputs, and from 0.0024 to 0.9998 on the superpositions. Both banks
send f and g to disjoint outputs: modes 0 and 12 for target-complement, and
8, 20 against 9, 21 for middle-middle. Every superposition therefore requests
the same intensities, and direct counting cannot see its relative phase. A
single photon under direct detection cannot reveal an output phase, so the
overlaps carry no physical information; they show only that the compiler
treats that phase as free. Three consequences follow.

- These banks' sum rules test only intensity linearity, the even components
  m_X = m_Y = m_Z. d_X and d_Y carry no quadrature information. A "+"
  setting's realized relative phase is whatever its compilation chose, so no
  fixed effect in the logical frame ties a d component to its label. The d
  components measure setting-to-setting response differences.
- This design cannot test phase error. Testing it needs a measurement that
  recombines the f and g outputs.
- The returned matrix of the reverse middle-middle settings rev-m and rev-p
  matches the requested intensities, yet the counts move between f's outputs
  and g's. If the returned circuit describes the configuration applied
  (`returned_circuit_semantics`, unresolved), the redistribution is a
  physical departure from it, an error of the chip's internal phases rather
  than of a requested input phase the circuit never encodes.

### A matched request returned the same circuit

The 552 beam-splitter angles are bit-identical across all 60 settings of both
epochs (one `beam_splitter_model_sha256`), while every phase shifter differs
between any two compilations. The retained sim:belenos runs of `tc-none-e1`
and `tc-def-e1` used the same seeds and parameters as the qpu:belenos runs.
They returned byte-identical circuits on all 24 settings, nine hours and two
noise models apart (`compilation_determinism`). On that evidence, 24
settings on one day, a matched seed repeats the returned transformation while
the compiler's component model holds; the diagnostic case tests it again on
every matched pair. The beam-splitter digest records any change of that
model. An unchanged digest says nothing about the physical chip.

### The repeat repeats the request, not the compilation

`scripts/bdsc_cases.py` draws each seed by observation index, epoch
included, so `tc-def-e2` ran all 12 settings with new seeds. On the five
repeat levels it matches epoch 1 in logical target, submitted parameters and
processing request. It differs in seed and returned circuit. The component
model is the same. The execution noise model moved from g2 0.010,
indistinguishability 0.876, transmittance 0.0613 to 0.009, 0.804 and 0.0525.
No calibration between the two executions is documented.

    setting  epoch 1  epoch 2   shift    | setting  epoch 1  epoch 2   shift
    out-f    0.0045   0.0023   -0.0022   | rev-f    0.0030   0.0026   -0.0004
    out-g    0.9856   0.9824   -0.0033   | rev-g    0.9845   0.9865   +0.0020
    out-p    0.4674   0.4516   -0.0159   | rev-p    0.4545   0.4957   +0.0412
    out-m    0.4876   0.4529   -0.0347   | rev-m    0.4913   0.4618   -0.0295
    out-pi   0.5380   0.4727   -0.0654   | rev-pi   0.4812   0.4726   -0.0086
    out-mi   0.4834   0.4728   -0.0107   | rev-mi   0.5066   0.4354   -0.0712

The four basis settings move by at most 0.0033, against reference standard
errors of a difference of 0.00014 to 0.00032. The eight superpositions move
by -0.071 to +0.041, seven of them downward, against a reference standard
error of 0.0013: a common drop of 0.024 with a spread of 0.035 about it. The
reading below is an inference, rated moderate. The spread at fixed requests
with new compilations is a per-compilation response; the common drop is a
change of the device, of its characterization or of the default policy's
processing calibration, which these data cannot separate. A balanced split
is sensitive to first order in internal phase error, while routing the whole
photon to one output is sensitive only to second order, which would explain
why the basis settings hold. Only an empty-mitigation repeat separates
processing from physics. A matched-seed block that reproduces its counts
would raise the rating of the per-compilation reading; a matched seed that
shifts would lower it.

### Scatter at one requested intensity

Within one template the four superpositions request one output intensity, so
their spread is the per-setting compilation response (seed and parameters
together) plus counting noise. The reference standard error of each is
0.0009.

    job          outward mean   SD     | reverse mean   SD     | split
    tc-def-e1       0.4941   0.0305    |    0.4834   0.0219    | +0.0107
    tc-none-e1      0.4119   0.0190    |    0.3887   0.0090    | +0.0232
    mm-def-e1       0.4919   0.0147    |    0.4766   0.0061    | +0.0154
    mm-none-e1      0.4797   0.0124    |    0.4842   0.0177    | -0.0045
    tc-def-e2       0.4625   0.0118    |    0.4664   0.0250    | -0.0039

The within-template SD runs from 7 to 34 times the reference error. Scatter
among four states does not by itself violate a sum rule. In the f, g basis
an effect whose off-diagonal elements reach the counts -- possible only in a
design that recombines the f and g outputs -- such as
F = [[0.003, 0.02 - 0.02i], [0.02 + 0.02i, 0.986]], with
eigenvalues 0.0022 and 0.9868, gives superposition responses 0.5145, 0.4745,
0.5145 and 0.4745: an SD of 0.023, with both residuals zero. The evidence
against one fixed effect is the residuals below and the shifts at fixed
requests above.

    job / template     m_Z     m_X     m_Y     d_X     d_Y   Delta_R  Delta_I
    tc-def-e1 out    0.4951  0.4775  0.5107  -0.0101 +0.0273  -0.0351  +0.0314
    tc-def-e1 rev    0.4937  0.4729  0.4939  -0.0184 -0.0127  -0.0417  +0.0003
    tc-def-e2 out    0.4923  0.4522  0.4727  -0.0006 -0.0000  -0.0802  -0.0392
    tc-def-e2 rev    0.4945  0.4787  0.4540  +0.0170 +0.0186  -0.0316  -0.0811
    tc-none-e1 out   0.4948  0.4081  0.4156  -0.0069 -0.0217  -0.1734  -0.1584
    tc-none-e1 rev   0.4944  0.3834  0.3940  +0.0081 +0.0003  -0.2221  -0.2008
    mm-def-e1 out    0.4889  0.4999  0.4840  -0.0098 -0.0101  +0.0219  -0.0100
    mm-def-e1 rev    0.4773  0.4774  0.4757  -0.0003 -0.0074  +0.0001  -0.0031
    mm-none-e1 out   0.4584  0.4766  0.4828  -0.0134 -0.0058  +0.0364  +0.0487
    mm-none-e1 rev   0.4729  0.4882  0.4802  -0.0203 +0.0051  +0.0306  +0.0147

The reference standard error of a residual is 0.0013 for target-complement
and 0.0018 for middle-middle. The one-click share outside a setting's
intended support has a median of 0.016 to 0.025 per job and reaches 0.112
(tc-def-e2 rev-pi), so the selected fraction alone misses comparable
wrong-mode response.

### Fitted models

Each job's 12 selected fractions are fitted by binomial reference deviance
under three models:

- linear (4 parameters): a fixed effect under scalar acceptance;
- intensity (3 parameters): Tr(G rho)/Tr(D rho) with G and D diagonal in the
  f, g basis;
- filtered (7 parameters): the full ratio with 0 <= G <= D.

The intensity model is the physically meaningful filtered model for a
phase-blind design. The filtered model's off-diagonal terms fit compilation
noise. Across the ten held-out splits (fit on one template, predict the
other), intensity predicts as well as filtered or better in eight. On the
empty-mitigation target-complement job the linear model misses by up to
0.106, while intensity misses by at most 0.037. Acceptance therefore carries
the bulk of that deficit, consistent with the receipt-weight prediction
above. On every job the best in-sample model still leaves a largest
residual of 0.016 to 0.037, against reference standard errors near 0.001,
which is the per-setting response. Fitted on `tc-def-e1`, the best model
predicts `tc-def-e2` with a largest residual of 0.050.

### Root-cause comparison

| Model | Explains | Misses | Nonidentifiable from retained data | Discriminating intervention |
|---|---|---|---|---|
| A: ideal column | target-complement f and g endpoints within 0.018 | every superposition deficit and residual | none | none needed |
| B: plan-receipt terminal weights | sign and 67 to 95 % of the empty-mitigation target-complement deficit; middle-middle basis asymmetry | the template split, per-setting scatter, the shifts at fixed requests | weight semantics against acceptance | output-swap probe; uncorrected observations |
| C: common intensity filter G, D | the common even-component shift per job | within-template scatter (max residual 0.025 to 0.049) | the filter's physical location | measured acceptance t_s per state |
| D: wrong-mode response and background | outside-support shares of 0.009 to 0.112 | the selected-fraction shifts among on-support outputs | dark counts against routing error | per-mode counts under a matched request |
| E: per-compilation transfer response | within-template scatter; the spread of 0.035 about the common drop at fixed requests with new seeds; robust endpoints | nothing retained; untested at a matched seed | its stability over time | matched-seed repeat; several seeds per state |
| F: preparation or phase drift | nothing specific: the design is phase-blind | d components with no label-bound phase | untestable in this design | recombining two-quadrature measurement |
| G: change of device, characterization or default-processing calibration | the common superposition drop of 0.024 from epoch 1 to the repeat | empty-mitigation behavior | confounded with E under defaults | empty-mitigation matched repeat |

### Evidence ledger

| Level | Holds | Status |
|---|---|---|
| Exact mathematics | E0 spectrum {0^4, (1/2)^8, 1^4}, the kernel projector, the optical target, the six-state identities | established (`bdsc_certificate.py --check`) |
| Local simulation | SLOS reproduces every ideal selected probability of the qualification and diagnostic cases within 1e-15 | established |
| Returned hardware records | 60 settings, their counts, seeds, parameter echoes, sent policy, returned circuits and noise models | retained and reconstructed (core-622) |
| Qualified physical probabilities | binomial confidence on returned counts | unavailable: the observation law is unestablished |
| Provider claims | applied processing under defaults, raw-count provenance, the meaning of the returned circuit, recalibration times | unresolved (`provider_contract.json`) |

The [diagnostic case](../../runbooks/bdsc-qualification-case.md#amendment-of-2026-10-22-a-crossed-diagnostic-replaces-the-confirmation-plan)
is the intervention that separates per-compilation response, block-to-block
change and template under one policy.

## Ascella incident and the scope of a comparison

Job `c2edef5d-5e6f-4161-83fc-aadd024171fb` returns zero shots and samples after
one second, with

    hardware_info.circuit_input_ports must be defined in the hardware_config
    to use Instruments.set_pic_input().

This localizes the failed dispatched path to provider instrument input-port
configuration before useful acquisition. It does not establish that every
Ascella endpoint or possible job fails, nor does it independently certify
cloud compatibility of the submitted circuit. Local Perceval validates the
ideal mathematics, not provider configuration.

The retained Ascella control is not an identical hardware counterfactual:
`scripts/bdsc_ascella_control.py` uses a seeded dense twelve-mode pair, input
4 and odd-output selection. Belenos uses sparse target/complement and
middle/middle columns in 24 modes. Success on one does not isolate the cause
on the other; failure on both can involve shared compilation, processing or
preparation assumptions. Compare matched support, logical transformations,
selection rules and calibrated acceptance before making device-local causal
claims.

Report the exact job ID, endpoint, timestamps, error, source mode and
processing request to the provider through an approved communication. Retry
only under the existing approval scope or a new written case after a
configuration remedy or independently justified readiness check. The public
`available` status is not an end-to-end instrument-health guarantee.

## Collection and epoch controls

`scripts/qd_platform.py collect` repeats each terminal GET of the existing
job -- status, result, job data and usage -- after a transient failure until
the collection deadline, and never repeats the POST that created the job. A
first collection writes `raw/result.json` before it parses the answer or reads
the job data and usage, so a later failure leaves the scientific bytes on
disk and a rerun completes the record. A usage report that stays unreadable
is recorded as `usage_absent`, and the charge falls back to the billing rule.
A job canceled before its start time is charged 0 credits: every retained
such job (the 2026-10-21 queue test and the three canceled diagnostic block-1
submissions of 2026-10-22) left the usage total unchanged, while the billing
rule would read the per-job price whenever another job shares its window.

`result_summary` keeps every entry of a partial iterated answer at its
position: a counted iteration as a completed job would, an iteration answered
with the worker's error text as `error`, and an unreadable entry as
`malformed`, and appends one `missing` entry for each iteration the case
expects but the answer omits. Only counted iterations contribute counts, and the BDSC readout
still admits only a completed, non-partial result.

`body_mitigations` reads the requested policy from `payload.mitigations`
alone, decoding Perceval's archive string, and refuses the key at any other
depth. The submission check and the BDSC readout both compare its value with
the manifest policy exactly, so an absent key, an empty list and a nonempty
list stay distinct. This records the requested policy; the processing the
provider applied remains a provider-contract question.

The shared template constructors of `scripts/bdsc_certificate.py`
(`template_ops`, `template_params`, `template_unitary`, `union_ops`,
`union_params`) take the optical width as a required `modes` argument, and
`bdsc_certificate.MODES` stays the 24 modes of qpu:belenos. The 12-mode
Ascella control passes its own width, so construction no longer depends on
call order. `bdsc_certificate.py --self-test` covers both widths and a
24-mode construction on either side of a 12-mode one;
`bdsc_ascella_control.py --check` rebuilds the retained Ascella case, its
circuit byte for byte and its manifest within `CHECK_TOLERANCE` (the solved
parameters move by one ulp between BLAS kernels), and confirms the 24-mode
constructions are unchanged around it.

The scheduled maintenance window on the run receipts is
2026-10-22 07:30--11:00 UTC (00:30--04:00 America/Los_Angeles).
The scheduled end is not proof of a completed calibration or a healthy input
configuration. Record actual readiness and an acquisition-time calibration
identity. Preserve epoch 2 as a separate intervention/replication epoch; do
not pool across calibration changes merely because both batches completed.

## Crossed diagnostic result (2026-10-23)

The four jobs of the approved crossed diagnostic completed: block 1 on
2026-10-22 (c8d90a80, ef06045d) and block 2 on 2026-10-23 (a5a0d2cf, after
the first submission waited 7.6 hours and ended canceled before its start,
and 33499aec), 960000 samples each. The matched check found block 2 job 1's
returned circuits identical to block 1 job 2's before job 2 went in. The
resubmission continued past a stop condition with no amendment retained
before it ([protocol deviation](../../runbooks/bdsc-qualification-case.md#protocol-deviation-of-2026-10-23-block-2-job-1-was-resubmitted)),
so the readout's rule is the preregistered one and its reading is
descriptive. The readout
([bdsc_diagnostic_readout.json](../../../results/quandela/bdsc_diagnostic_readout.json),
claim `qd-belenos-bdsc-diagnostic-readout`, gate `core-647`) selects the
**stationarity** branch. Its standard errors and p-values are reference
values under independent Bernoulli trials: the provider contract leaves count
provenance and uncorrected observations unresolved, so they are uncalibrated
if the service reconstructs or correlates the returned counts.

- **Branch reading.** Matched requests changed between the blocks beyond
  their class means (heterogeneity 553 on 45 degrees of freedom, p 1e-88),
  while all 48 matched pairs returned identical compiled circuits and no
  instance leaked. The provider contract leaves returned-circuit semantics
  unresolved, so identical returns show that the service reported one
  nominal model; the change belongs to the device rather than the compiler
  only if a returned circuit describes the configuration that ran. The branch's disposition: address stationarity and
  provider calibration before any fixed-effect confirmation.
- **Support-conditioned rerun (no branch reads it).** On selected clicks over
  on-support clicks the matched requests' changes are homogeneous about their
  class means (45.8 on 45, p 0.44), so the instance-specific part of the
  block change lives in the clicks outside the target support, the dilution
  of unselected mode 5. A common on-support shift remains: the
  superpositions moved by -0.0048 (z -7.7). The template test stays resolved.
- **Calibration shift.** The g basis state moved by +0.0035 between blocks
  (z 11.6); f moved by +0.0003 (z 2.3) and the superpositions by -0.0015
  (z -2.5), both inconclusive.
- **Seeds.** Seed dispersion of the superpositions is resolved and
  state-specific in both readings (seed interaction 5542 on 36 raw, 4424 on
  36 support-conditioned). Within a block and template the seed slots split
  between the two jobs, so that statistic also carries a state-dependent
  change between jobs; restricted to seed slots that share a job, the
  interaction stays resolved (2406 on 24 raw, 1941 on 24 support-conditioned),
  so the state-specific seed effect stands apart from job identity.
- **Residuals.** All 32 sum-rule residuals lie beyond the 0.02 margin,
  between -0.14 and -0.24, with no position trend inside a job (rank
  correlations -0.13 to +0.36, p >= 0.17).

The next amendment therefore starts from stationarity: a design whose
contrasts compare matched requests within one acquisition window, measures
the off-support fraction per iteration as a calibrated nuisance and carries
the common on-support shift of the superpositions as its own term, before any
confirmation reads a fixed effect.

## Research grounding

The canonical BDSC source map is [bdsc_sources.md](bdsc_sources.md).
The registered detector-tomography and gate-set-tomography notes distinguish
known preparations from unknown measurements and joint identifiability:
[0807.2444](../papers/0807.2444.md) and
[2009.07301](../papers/2009.07301.md). Drift requires appropriately retained
time information: [1907.13608](../papers/1907.13608.md).

External primary sources used for the conditioning interpretation:

- Orsucci, Bancal, Sangouard and Sekatski, *How post-selection affects
  device-independent claims under the fair sampling assumption*, Quantum 4,
  238 (2020): https://quantum-journal.org/papers/q-2020-03-02-238/
- Perceval 1.3 error-mitigation contract:
  https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/index.html
- DetectorBalancing's declared purpose and model dependence:
  https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/detector_balancing.html

The source-map registration is not changed by this note. No new theorem of
sedenion algebra, altered likelihood, or physical detector correction is
claimed. The strongest current diagnosis is an identifiable acceptance
confound with a quantitatively relevant receipt-based prediction, plus a
reverse-template residual, a setting-specific 8-to-9 redistribution in the
MM reverse rows, and wrong-mode response whose mechanisms remain open.
