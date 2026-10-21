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
is BS.H itself.

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
self-test checks all three inequalities on 1024 effects. 1023 of them have
a < gamma, and a near-tight family reaches sin^2 theta / (a / gamma) =
0.997.

A record is certified when min(a_U, l_U) < gamma_L and the angle bound is
at most 10 degrees. Otherwise it reads alternative structure when the
complement's certified brightest response c_L is positive and either
gamma_U <= 0.1 c_L (a fifth low-response direction) or a_L >= 0.1 c_L (a
bright direction inside K). Every other record reads not certified. The
ratios make a common scale, such as transmittance under an emitted-photon
denominator, change no disposition.

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
trials for E0 and for a 1 % background).

| Control | Disposition |
|---|---|
| E0; exact kernel with complement spectrum 0.3..0.9; rotation 5 degrees; background 0.002; F = 0.0606 E0 at 10^6 trials | certified |
| E_R, E_I (complex bank); rotation 30 degrees | alternative structure |
| E_I on the 88-setting bank with real_effect asserted | certified, uncovered: the false certificate the complex bank prevents |
| F = 0.0606 E0 at 10^5 trials; background 0.05; acceptance imbalance 0.8; preparation error 0.02 | not certified |
| missing, duplicated or miscounted rows; changed mask; optional stopping; unbound target or bank digest; any unsupported premise | inadmissible |

## Planning

- At expected counts, E0 first certifies at 5000 trials per setting
  (8.7 degrees) under either alpha allocation.
- A background beta I raises a directly. beta = 0.002 needs 10^5 trials,
  0.005 needs 10^6, and 0.02 never certifies at the planning tiers.
- Systematics propagate as worst-case shifts through the |D_s| row sums,
  which amplify a per-setting bias about thirtyfold. At 10^5 trials the
  certificate tolerates a preparation bias bound of 0.0026 or an
  acceptance deviation delta of 0.014 per setting.
- The zero-event trace route (n_min = 1086 at gamma_L = 0.45) needs zero
  selected events. Belenos's off-cone clicks on modes 0, 1 and 5 make a
  zero-event record unplannable.
- Historical qpu:belenos rates (6.3 s per iteration plus 26 us per sample,
  32 iterations per job, 1 credit per job plus 1e-6 per billed shot) put
  the 160-setting bank at 5 jobs and about 6 credits for 10^5 trials, and
  18 jobs and 54 credits for 10^6.

## Qualification on qpu:belenos

| Milestone | Status | Evidence |
|---|---|---|
| M0 algebra | passed | `target.json`, `packages/packages.json` |
| M1 optical target | passed | U24 exact; Perceval native circuit and SLOS shares within 1e-9 on 184 settings |
| M2 native compilation | blocked | the service re-transpiles every circuit and keeps only the occupied column (jobs 1d7160c1, e5b74123; strategy.md sections 4 and 7), so no fixed measurement stage exists apart from the preparation |
| M3 acquisition | blocked | DetectorBalancing is the default mitigation; Perceval 1.3.1's probs_to_sample_count reads a zero-count frequency of 0.305 against the binomial 0.368 (z = -18.3) and a mean of 1.079 against 1.000 at p = 1e-4, n = 10^4 over 20000 seeded draws; the receipt t_out taken as efficiencies gives an acceptance deviation of 0.97; off-cone clicks have no model |
| M4 fixed effect | blocked | the compiled mesh, and with it the error channel, follows the target column, which follows the preparation label |
| M5 to M9 | not started | the pilot of `pilot.json` waits for an approved case |

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
