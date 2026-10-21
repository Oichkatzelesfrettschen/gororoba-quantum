# Sources of the dark-subspace certificate

The [dark-subspace certificate](bdsc.md) draws on three layers that carry
different kinds of authority. Established algebra fixes the target exactly.
Mathematical instrumentation supplies the optical dilation, the interferometer
and the concentration and perturbation theory. Physical statistical inference
connects counts from a characterized device to a confidence statement. The
target/complement certificate itself, sin^2 theta_max <= a_U / gamma_L from
bounds on the blocks A = V_K^T F V_K and C = V_Q^T F V_Q, follows from
Courant-Fischer and positivity alone (bdsc.md, Certificate). No source below
states it, and the repository asserts no literature priority for the complete
experimental architecture.

Every source is registered in [SOURCES.json](../../SOURCES.json). The arXiv
grant of most of them permits no rehosting, so their PDFs live in the ignored
`docs/local_source_cache/` and the verifier checks them where present. The
CC BY sources are retained under `docs/pdf/`.

## Established algebra

| Source | Repository copy | What the certificate takes | What the source does not supply |
|---|---|---|---|
| Biss, Christensen, Dugger, Isaksen, Eigentheory of Cayley-Dickson algebras, Forum Mathematicum 21 (2009), 833-851, DOI 10.1515/FORUM.2009.041 | [note](../0905.2987.md), arXiv 0905.2987v1, cache `0905.2987v1.pdf` | The spectrum and eigenspaces of E0 | Any measurement, optics or statistics |
| de Marrais, The 42 Assessors and the Box-Kites They Fly (2000) | [note](../papers/math-0011260.md), arXiv math/0011260v1, cache | The combinatorial setting of the zero-divisor diagonals | The physical certification theorem |
| de Marrais, Flying Higher Than a Box-Kite (2002) | [note](../papers/math-0207003.md), arXiv math/0207003v2, cache | The same patterns beyond the sedenions | The same |
| de Marrais, Box-Kites III (2004) | [note](../math-0403113.md), arXiv math/0403113v1, cache | Zero-divisor-suppressing structures | The same |

Biss et al. use the doubling (a, b)(c, d) = (ac - d* b, da + b c*) of
`cd_core` and M_a = L_(a*) L_a / |a|^2 (Definition 3.1, Lemma 2.3).
Proposition 7.4 gives, for a zero divisor (a, b) of A_4 with a, b orthogonal
imaginary octonions of equal norm, the eigenvalues 0, 1, 2 with multiplicities
4, 8, 4 and Eig_0 = {(y, -ab y / |ab|) : y in <<a, b>>^perp}. For
x = (e1 + e10)/sqrt2, a = e1/sqrt2 and b = e2/sqrt2, so E0 = M_x / 2 has the
spectrum {0^4, (1/2)^8, 1^4} of `target.json`. With e1 e2 = e3 from
`cd_core.cd_sign(8, 1, 2)`, the eigenspace formula over y = e4..e7 gives
e4 - e15, e5 + e14, e6 - e13 and e7 + e12, the kernel frame K exactly. `target.json`
proves the same spectrum and frame independently in Fractions.

The de Marrais manuscripts supply the vocabulary in which (e1 + e10) and the
four kernel vectors e_i +- e_j (i < 8 <= j) are zero-divisor diagonals and in
which the corpus witness (e1 + e10)(e4 - e15) = 0 sits. The certificate uses
none of their combinatorial results as a premise.

## Mathematical instrumentation

| Source | Repository copy | What the certificate takes |
|---|---|---|
| Tischler, Rockstuhl, Slowik, Quantum Optical Realization of Arbitrary Linear Transformations Allowing for Loss and Gain, Physical Review X 8 (2018), 021017 | [note](../papers/1712.01413.md), arXiv 1712.01413v2, cache | The dilation of the 12 x 16 Kraus compression into a passive 24-mode unitary |
| Clements, Humphreys, Metcalf, Kolthammer, Walmsley, Optimal design for universal multiport interferometers, Optica 3 (2016), 1460-1465 | [note](../papers/1603.08788.md), arXiv 1603.08788v2, cache | The mesh on which qpu:belenos realizes any unitary; balanced loss as a scalar |
| Tropp, User-friendly tail bounds for sums of random matrices, Foundations of Computational Mathematics 12 (2012), 389-434 | [note](../papers/1004.4389.md), arXiv 1004.4389v7, cache | Matrix Bernstein, Theorem 1.4: `bdsc.bernstein_radius` |
| Davis and Kahan, The rotation of eigenvectors by a perturbation. III, SIAM Journal on Numerical Analysis 7 (1970), 1-46, DOI 10.1137/0707001 | citation only; SIAM hosts the paper behind a subscription and no repository copy exists | The standard perturbation theory of spectral subspaces, for comparison |

Tischler's ancilla rule predicts U24's size. The selected compression T of U24
is 12 x 16 with squared singular values 1 (four) and 1/2 (eight), so the rule
asks for 16 - 12 = 4 output ancillas and one full ancilla per singular value
below 1, eight in all: 16 + 8 = 24 input modes, as `target.json` builds them.

Tropp's Theorem 1.4 with summands D_s (B - p_s)/n_s, R = max ||D_s|| / n_s,
sigma^2 = ||sum D_s^2 / (4 n_s)|| and the two-sided factor 2m gives the radius
R h/3 + sqrt((R h/3)^2 + 2 sigma^2 h), h = log(2m/alpha). The handoff's
complement radii reproduce at alpha = 0.0125 and m = 12 (`planning.json`).

The Davis-Kahan sin theta theorem bounds the angle between corresponding
spectral subspaces of a Hermitian operator and its perturbation by the
perturbation norm over a spectral gap. That statement is general background,
not a reading of the 1970 paper, which the repository does not hold. The
certificate needs no perturbation norm: it bounds the blocks of F directly
and uses gamma_L, a certified lower bound on the complement block, in the
role the gap plays in Davis-Kahan.

## Physical statistical inference

| Source | Repository copy | What the certificate takes |
|---|---|---|
| Lundeen et al., Tomography of quantum detectors, Nature Physics 5 (2009), 27-30, DOI 10.1038/nphys1133 | [note](../papers/0807.2444.md), arXiv 0807.2444v1 ("Measuring measurement"), cache | Detector tomography: known probe states reconstruct an unknown effect |
| Nielsen, Gamble, Rudinger, Scholten, Young, Blume-Kohout, Gate Set Tomography, Quantum 5 (2021), 557, DOI 10.22331/q-2021-10-05-557 | [note](../papers/2009.07301.md), `docs/pdf/2009.07301.pdf` (CC BY 4.0) | Why a known preparation frame is a premise and what removing it costs |
| Chen, Zeng, Zhao, Ma, Zhou, Quantum Subspace Verification for Error Correction Codes, PRX Quantum 6 (2025), 040353, DOI 10.1103/fyw6-lq1l | [note](../papers/2410.12551.md), `docs/pdf/2410.12551v1.pdf` (CC BY 4.0) | Subspace verification from spectral gaps and Bernoulli counts |

The certificate is detector tomography of one outcome restricted to two
blocks. The 160-setting bank is a tomographically complete probe set for A
and C in Lundeen's sense, and the linear reconstruction of `bdsc.reconstruct`
is their P = F Pi with confidence radii in place of a projection onto the
physical set.

Gate-set tomography explains the premise that reconstruction carries. State
and process tomography each assume one side of the experiment known, and GST
estimates both up to a gauge M. The certificate assumes the preparations
known up to `preparation_bias_bound` and the conditioning up to
`conditioning_delta`. Its M4 blocker on qpu:belenos, a compiled mesh that
follows the preparation label, is the case in which that premise fails and
only a self-consistent model of the kind GST builds could recover a common
effect.

Chen et al. solve the dual problem. They trust the measurement and certify
that a state lies near a known subspace, bounding Tr(Omega rho) through the
spectral gaps of a designed verification operator (Lemma 1). The certificate
trusts the preparations and certifies that an unknown effect has a
low-response eigenspace near span K, with gamma_L in the role of the gap.

## What remains the repository's own

- The choice of target E0 and frames K and Q, the 24-mode unitary and its
  native PERM, BS.H, PERM form (`target.json`, `packages/packages.json`).
- The target/complement theorem and its self-test on 1024 effects.
- The two-procedure confidence construction (Clopper-Pearson with Gershgorin
  or triangle propagation against matrix Bernstein, the smaller radius per
  block), the systematic weights and the disposition rule.
- The qpu:belenos qualification record, measured against
  [strategy.md](strategy.md).
