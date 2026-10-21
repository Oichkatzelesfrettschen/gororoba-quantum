# Belenos dark-subspace certificate

The certificate asks whether a physical one-photon measurement F on the
16-dimensional sedenion input space has a four-dimensional low-response
eigenspace within 10 degrees of the kernel of L_x, x = (e1 + e10)/sqrt2,
at joint confidence 0.95. The exact algebra is the reference, the
implemented effect is the object under test, and the confidence-qualified
subspace is the result. `gororoba_quantum/bdsc.py` holds the frame, the
reconstruction, the confidence radii and the certificate;
`scripts/bdsc_certificate.py` holds the exact layer and writes the records
under `docs/evidence/bdsc/`; `scripts/bdsc_packages.py` re-derives them
through Perceval, python-hypercomplex, hyprat, python-flint and sympy.
No acquisition, upload or cloud submission is authorized by these records.
[bdsc_sources.md](bdsc_sources.md) separates the established algebra, the
mathematical instrumentation and the statistical inference the certificate
rests on, with each source's registered copy.

## Target

E0 = L_x^T L_x / 2 = (L_e1 + L_e10)^T (L_e1 + L_e10) / 4 in the basis and
doubling of `cd_core` ((a, b)(c, d) = (ac - conj(d) b, da + b conj(c))).
L_e1^T L_e10 is a signed permutation pairing e_k with e_(k xor 11), so E0
splits into eight 2 x 2 blocks: [[1/2, s/2], [s/2, 1/2]] on the pairs
(7, 12), (6, 13), (5, 14), (4, 15) and diag(1/2, 1/2) on the other four.
Its spectrum is {0^4, (1/2)^8, 1^4}.

| Frame | Vectors | E0 eigenvalue |
|---|---|---|
| K | k_1..k_4 = (e7 + e12, e6 - e13, e5 + e14, e4 - e15)/sqrt2 | 0 |
| Q middle | f_1..f_8 = e0, e1, e2, e3, e8, e9, e10, e11 | 1/2 |
| Q bright | f_9..f_12 = (e7 - e12, e6 + e13, e5 - e14, e4 + e15)/sqrt2 | 1 |

`target.json` proves this in Fractions: E0 w = lambda w for all sixteen
integer frame vectors, mutual orthogonality, completeness of
sum w w^T / |w|^2, P^2 = P, Tr P = 4, E0 P = 0 and L_x k_j = 0, plus an
independent recursive doubling that reproduces `cd_core.cd_sign` on all 256
basis products. python-hypercomplex and hyprat rebuild E0 byte for byte
from their own products; python-flint reads rank E0 = 12,
rank(E0 - I/2) = 8, rank(E0 - I) = 12, the minimal polynomial and the
characteristic polynomial x^4 (x - 1/2)^8 (x - 1)^4; sympy reads the
eigenvalue multiplicities.

## Measurement

U24 sends k_j to a complement output D_j, the bright partner f_(8+j) to a
selected output A_j, each middle vector to (A + D)/sqrt2 and an ancilla to
(A - D)/sqrt2. Every entry lies in {0, +-1/sqrt2}; U24^T U24 = I and the
selected compression equals E0, exactly over Q(sqrt2) and again in sympy.
In Perceval the circuit is PERM_in, twelve BS.H on wire pairs (2j, 2j + 1)
and PERM_out with no phase shifter, because each output pair's 2 x 2 block
is BS.H itself. That describes the requested unitary; the served Belenos
mesh is the full compiled chip (M2 below).

The selected outputs are the twelve modes with the lowest receipt dark rate
in the qpu:belenos catalogue retrieved 2026-10-17 (12, 13, 16, 18, 19, 20, 21, 22, 23,
4, 6, 7), and the source is connected input 6, the highest receipt t_in.
Both are dated planning inputs. `inputs/receipt.json` freezes that catalogue entry
(retrieval 2026-10-17T17:53:31Z) with its digest, so a catalogue refresh
leaves the target unchanged; a target planned from a newer receipt is a new
target with a new `target_sha256`.

## Certificate

For any effect 0 <= F <= I with blocks A = V_K^T F V_K and
C = V_Q^T F V_Q, bounds lambda_max(A) <= a_U and C >= gamma_L I with
a_U < gamma_L give:

- lambda_4(F) <= a_U, by Courant-Fischer on span K;
- lambda_5(F) >= gamma_L, since every 5-space meets the 12-space Q;
- sin^2 theta_max <= a_U / gamma_L, by compressing
  F >= gamma_L (I - P~) onto K, where P~ projects on the four lowest
  eigenvectors.

The cross block never enters, and Tr A bounds lambda_max(A) as well. The
inequalities use F >= 0 alone. Under an acceptance bound
(1 - delta) tau I <= D <= (1 + delta) tau I the reconstructed effect
F = G_A / tau satisfies only F <= (1 + delta) I, so the a priori caps on a_U
and l_U are 1 + delta and 4 (1 + delta); the ratio a_U / gamma_L is
unchanged by a common scale. The self-test checks all three inequalities on 1024 effects. 1023 of them have
a < gamma, and a near-tight family reaches sin^2 theta / (a / gamma) =
0.997.

A record is certified when min(a_U, l_U) < gamma_L and the angle bound is
at most 10 degrees. Otherwise it reads alternative structure when the
complement's certified brightest response c_L is positive and either
gamma_U <= 0.1 c_L (a low-response direction inside the complement Q) or
a_L >= 0.1 c_L (a bright direction inside K, relative to the certified lower
reference c_L rather than to lambda_max(C) itself). Every other record
reads not certified, and one whose block estimate lies farther than its
radius outside [0, 1 + delta] reads inconsistent and carries no finding. A low complement direction does not by itself make a fifth low
eigenvalue of F: A = 0.09 I_4, C = diag(0.09, 1, ..., 1) and one cross
entry 0.09 between k_1 and that direction form a valid effect with spectrum
{0, 0.09^3, 0.18, 1^11}. Positivity gives |u^T B v|^2 <= (u^T A u)(v^T C v)
on the cross block B, so lambda_5(F) <= a_U + gamma_U is the global bound
such a record supports, tight on that example. The
ratios make a common scale, such as transmittance under an emitted-photon
denominator, change no exact disposition; at a fixed trial count the
confidence radii are not homogeneous, so the same scale can change what a
finite acquisition certifies.

### Spectral claims

The disposition is a compatibility summary. The census
(`bdsc.spectral_census`, schema `bdsc-spectral-findings-v1`) reports each
claim on the same confidence event, so a certified alignment never hides a
fifth low eigenvalue. With a = lambda_max(A) and mu_1 <= ... <= mu_12 the
eigenvalues of C,

    mu_j <= lambda_(4+j)(F) <= a + mu_j,   j = 1..12.

The lower bound is interlacing with the 12-dimensional compression. The
upper bound is min-max on span K plus the first j eigenvectors of C, where
positivity bounds the cross term by 2 sqrt(a mu_j) |u| |v|. The fifth
eigenvalue is the j = 1 case, lambda_5 <= a + mu_1, attained by the coupled
example. Weyl's inequality moves each eigenvalue of a block by at most the
block's operator-norm radius, so with a_* = min(a_U, l_U, L),
mu_jL = max(0, lambda_j(C^) - eps_C) and mu_jU = min(L, lambda_j(C^) + eps_C),
every lambda_(4+j) lies in [mu_jL, min(L, a_* + mu_jU)] on the one event
that bounds both blocks. U_5 = min(L, a_* + mu_1U) and L_6 = mu_2L. L is 1
for a binary effect and 1 + delta under approximate conditioning. Reporting
several of these consequences adds no multiplicity charge; adaptively
selected data or separately fitted models need their own.

Low means at most 0.1 lambda_max(C), an engineering definition fixed before
acquisition (`LOW_RATIO`); a finite threshold never establishes an exact
null. With c_L <= lambda_max(C) <= c_U, each finding reads supported,
refuted or inconclusive, and unavailable unless c_L > 0 and the census is
consistent:

| Finding | Supported when | Refuted when |
|---|---|---|
| target_alignment | the disposition is certified | never: an inconclusive bound is not misalignment evidence |
| complement_low | mu_1U <= 0.1 c_L | mu_1L > 0.1 c_U |
| at_least_five_low | U_5 <= 0.1 c_L | mu_1L > 0.1 c_U |
| exactly_five_low | U_5 <= 0.1 c_L and L_6 > 0.1 c_U | at_least_five_low refuted, or U_6 <= 0.1 c_L |
| target_bright | a_L >= 0.1 c_U | a_U < 0.1 c_L |
| target_bright_lower_reference | a_L >= 0.1 c_L | a_U < 0.1 c_L |

complement_low alone leaves lambda_5 above the threshold possible: the
coupled example has mu_1 = 0.09 and lambda_5 = 0.18. diag(0^4, 0.05, 1^11)
has the frozen kernel as its exact kernel and lambda_5 = 0.05, so
target_alignment and at_least_five_low both hold. `controls.json` carries
these fixtures twice: exact blocks at zero radius (`exact_census`, with
five and six designed low eigenvalues, a common scale and the range
L = 1.2) and sampled controls at the trial count that resolves them.

### Five-space witness

A targeted fifth-eigenvalue claim costs less than the full complement. For
a unit q in Q, S = P + |q><q| has rank five and

    lambda_5(F) <= lambda_max(S F S) <= Tr(S F) = 5 r_5,

where r_5 is the selected probability of a uniform ensemble over k_1..k_4
and q, each trial drawing its state independently. The witness measures
the whole five-space, not q's response alone. `bdsc.five_space_witness`
returns 5 times the one-sided Clopper-Pearson upper bound, scaled by
1 + delta and shifted by the bias bound under approximate conditioning.
Against a bright reference b_L = 0.9 and threshold 0.1 b_L = 0.09, zero
events in N = 204 trials at one-sided alpha 0.025 give lambda_5 <= 0.0896012
(`planning.json`, `five_space_witness`); that excludes the reference
acquisition, preparation calibration and qualification, and zero events on
qpu:belenos cannot be promised. q_R = (e1 - e2)/sqrt2 and
q_I = (e1 + i e2)/sqrt2 are the extra nulls of E_R and E_I, preregistered
adversarial directions; a direction found in exploratory data is frozen and
confirmed on fresh data, or its selection is covered by the simultaneous
confidence region. A failed witness excludes only that candidate, and an
exactly-five claim still needs L_6 or a floor outside the five-space.

## Preparation bank and estimator

Each block is reconstructed from basis states, real pairs
(f_i + f_j)/sqrt2 and imaginary pairs (f_i + i f_j)/sqrt2: 16 settings for
A and 144 for C, 160 in all. `bank.json` carries each setting's state, its
24-mode chip column U24 psi_s and its exact ideal selected probability.
`bank_sha256` binds each setting name to its state, and an acquisition
record carries it beside `target_sha256`. The real 88-setting bank is blind to E_I = E0 + (i/2)(|e1><e2| - |e2><e1|):
E_I and E0 differ on exactly one bank setting, C-imag-01-02, and E_R on
exactly C-real-01-02.

Each block's alpha splits evenly between two procedures, and the smaller
radius is reported. The first is Clopper-Pearson intervals with Bonferroni,
propagated to the operator norm by the Gershgorin row sum or the triangle
inequality. The second is matrix Bernstein. The handoff's complement radii
0.409805, 0.157552, 0.049664 and 0.015689 at 1500 to 10^6 trials are matrix
Bernstein at alpha_B = 0.0125 = alpha_C / 2 with m = 12. `planning.json`
reproduces them to six digits, and gate core-606 holds them.

## Synthetic controls

`controls.json` runs every control through `bdsc.evaluate` at 10^5 trials
per setting. Each expected disposition is met, and the true a and gamma lie
inside the bounds wherever a certificate is issued (64/64 coverage at 10^4
trials for E0 and for a 1 % background). The coverage runs are regression
evidence for the implementation; the 0.95 joint confidence rests on the
Clopper-Pearson, Bonferroni and matrix Bernstein bounds, not on them.

| Control | Disposition |
|---|---|
| E0; exact kernel with complement spectrum 0.3..0.9; rotation 5 degrees; background 0.002; F = 0.0606 E0 at 10^6 trials; diag(0^4, 0.05, 1^11), five and six designed low eigenvalues at 10^6 trials | certified |
| E_R, E_I (complex bank); rotation 30 degrees | alternative structure |
| the coupled example at 10^6 trials; diag(0^4, 0.05, 1^11) at 10^5 trials | not certified |
| E_I on the 88-setting bank with real_effect asserted | certified, uncovered: the false certificate the complex bank prevents |
| F = 0.0606 E0 at 10^5 trials; background 0.05; acceptance imbalance 0.8; preparation error 0.02 | not certified |
| block estimates outside [0, 1 + delta] by more than their radius | inconsistent |
| missing, duplicated or miscounted rows; changed mask; optional stopping; unbound target or bank digest; any unsupported premise | inadmissible |

The census findings sit beside each disposition, and every sampled control
with a known effect, apart from the forced real-bank control, keeps all
twelve true eigenvalues lambda_5..lambda_16 inside its intervals. Counts
that put a C eigenvalue near -1 read inconsistent with every finding
unavailable. E0 refutes a fifth low eigenvalue; E_R and E_I
support exactly five at 10^5 trials; diag(0^4, 0.05, 1^11) certifies the
alignment and supports exactly five at 10^6 trials and leaves both
inconclusive at 10^5, where eps_C near 0.05 does not resolve 0.05 against
0.1 c_L; six designed low eigenvalues refute exactly five; the coupled
example stays inconclusive at 10^6, since its mu_1 = 0.09 sits within eps_C
of the threshold. The self-test checks the twelve interval inequalities on
128 Haar-random effects (1536 indexed pairs) and Tr(S F) >= lambda_5 for
both candidate directions.
## Planning

- At expected counts, E0 first certifies at 5000 trials per setting
  (l_U = 0.0062733, gamma_L = 0.2767577, 8.659 degrees) under either alpha
  allocation. This is a deterministic evaluation at the ideal expected
  counts, not a probability that a 5000-trial run certifies.
- A background beta I raises a directly. beta = 0.002 needs 10^5 trials,
  0.005 needs 10^6, and 0.02 never certifies at the planning tiers.
- Systematics propagate as worst-case shifts through the |D_s| row sums,
  which amplify a per-setting bias about thirtyfold. At 10^5 trials the
  certificate tolerates a preparation bias bound of 0.0026 or an
  acceptance deviation delta of 0.014 per setting. Both are conditional on
  the ideal E0 spectrum, the outcome law and the normalization; a measured
  complement spectrum or calibration uncertainty moves them.
- The six-state consistency case of
  [bdsc-qualification.md](../../design/bdsc-qualification.md) needs 22080
  trials per setting at margin 0.05 and alpha 0.01 over eight cells
  (exact Clopper-Pearson at E0's expected counts); the conservative
  Hoeffding bound 8 log(12 / alpha) / m^2 reads 22689 at one cell.
- The zero-event trace route (n_min = 1086 at gamma_L = 0.45) needs zero
  selected events. Modes 0, 1 and 5, where Belenos's unmodeled off-cone
  clicks appear, are outside the selected set, so they do not refute the
  route; they show that the background and acquisition model is
  unqualified, and a zero-event outcome cannot be promised. No plan rests on
  this branch.
- Historical qpu:belenos rates (6.3 s per iteration plus 26 us per sample,
  32 iterations per job, 1 credit per job plus 1e-6 per billed shot) put
  the 160-setting bank at 5 jobs and about 6 credits for 10^5 trials, and
  18 jobs and 54 credits for 10^6. These rates belong to processed-output
  jobs under default mitigation; raw acquisition, disabled mitigation or
  added calibration needs a new plan.

## Qualification on qpu:belenos

| Milestone | Status | Evidence |
|---|---|---|
| M0 algebra | passed | `target.json`, `packages/packages.json` |
| M1 optical target | passed | U24 exact; Perceval native circuit and SLOS shares within 1e-9 on 184 settings |
| M2 native compilation | blocked | the tested routes preserve neither the requested full transformation nor a preparation-independent measurement stage: on sim:belenos the parameterized and numeric architecture forms (jobs 1d7160c1, e5b74123) came back with all 574 phases changed and only the occupied column kept, and on qpu:belenos the served mesh follows the body and the compilation seed (belenos_mesh job-02, job-07; strategy.md sections 2, 4 and 9). Whether another access mode preserves a requested transformation is a provider question ([qualification design](../../design/bdsc-qualification.md)) |
| M3 acquisition | blocked | DetectorBalancing is the default mitigation and assumes loss without dark counts and independent detectors; Perceval 1.3.1's probs_to_sample_count perturbs each probability by a normal draw, clips, renormalizes and rounds, so at n p = 1 its zero-count frequency sits near Phi(-1/2) = 0.3085: the local conversion record reads 0.305 against the binomial 0.368 (z = -18.3) and a mean of 1.079 against 1.000 at p = 1e-4, n = 10^4 over 20000 seeded draws. The record is a local 1.3.1 study and the frozen receipt names server Perceval 1.3.0. An explicit empty mitigation list is the documented request for no remote mitigation ([error_mitigation](perceval/reference/runtime/error_mitigation/index.md)), unverified on this account; the receipt t_out taken as efficiencies gives an acceptance deviation of 0.97; off-cone clicks have no model |
| M4 fixed effect | blocked | the compiled mesh, and with it the error channel, follows the target column, which follows the preparation label |
| M5 to M9 | not started | the pilot of `pilot.json` waits for an approved case |

The latest retained qpu:belenos reads (2026-10-20, `running` at 04:09 UTC
and `calibration` at 08:51 UTC) lack `specs.architecture`, so `qd_platform.py
plan` refuses a mesh-sensitive case before any of these milestones
([calibration.md](calibration.md)). The three provider contracts that M2 to
M4 need, and the qualification measurements that test them, are in
[bdsc-qualification.md](../../design/bdsc-qualification.md);
`provider_contract.json` records each capability's status and question, and
`qualification_case.json` the first case.

In Perceval, uniform NoiseModel transmittance cancels exactly under
`min_detected_photons` 1, and per-mode LC loss reproduces
Tr(G rho) / Tr(D rho) from `bdsc.acceptance` on every setting. A g2 of
0.01 puts 0.5 % of accepted events at two photons.

## Commands

```sh
"$PYTHON" scripts/bdsc_certificate.py --write docs/evidence/bdsc
"$PYTHON" scripts/bdsc_certificate.py --check docs/evidence/bdsc     # core-606
"$PYTHON" scripts/bdsc_certificate.py --self-test                    # core-607
"$PYTHON" scripts/bdsc_packages.py --write docs/evidence/bdsc/packages/packages.json
"$PYTHON" scripts/bdsc_packages.py --check docs/evidence/bdsc/packages/packages.json   # core-608
```

`bdsc_packages.py --check` replays the record with numpy alone where the
package stack is absent, as on CI, and re-derives it live where every
package imports at the recorded versions.
