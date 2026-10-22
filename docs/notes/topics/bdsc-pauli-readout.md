# BDSC effects as four-qubit Pauli sums

The binary-effect dark-subspace certificate (BDSC, [bdsc.md](../quandela/bdsc.md))
tests the effect E0 = L_x^T L_x / 2 of the sedenion zero divisor
x = (e1 + e10)/sqrt2 on C^16. Under the basis encoding e_j -> |j3 j2 j1 j0>,
j = 8 j3 + 4 j2 + 2 j1 + j0 (algebra index bit b on qubit b, Pauli words
written q3 q2 q1 q0), the whole sixteen-dimensional effect is a three-term
Pauli sum:

    E0 = I/2 - YIXY/4 + YZXY/4 = I/2 - (I - Z2) T / 4,   T = Y3 X1 Y0.

`scripts/bdsc_pauli.py` derives this from `cd_core.cd_sign` in exact integer
arithmetic, checks it against `bdsc.ideal_effect()` and `bdsc.projector()`,
and writes [pauli_form.json](../../evidence/bdsc/pauli/pauli_form.json); gate
`core-625` replays the record against a fresh derivation.

## Local readout of the target

Z2 and T commute, so one product basis diagonalizes E0: Y on q3, Z on q2, X on
q1, Y on q0, reached by `sdg` then `h` for each Y and `h` for X before a
computational-basis measurement. No entangling gate enters the readout.

| z2 | t = y3 x1 y0 | E0 eigenvalue | score g |
|---:|---:|---:|---:|
| +1 | either | 1/2 | 1/2 |
| -1 | +1 | 0 | 0 |
| -1 | -1 | 1 | 1 |

The score satisfies sum over outcomes of g Pi_outcome = E0, so its mean
estimates Tr(E0 rho). It takes the values 0, 1/2 and 1, so its sample mean
needs a bounded-mean confidence interval (Hoeffding or empirical Bernstein);
the Clopper-Pearson interface of `bdsc.clopper_pearson` takes integer counts
of a binary outcome and does not apply to it. The outcome z2 = -1, t = +1 is
the rank-four projector (I - Z2)(I + T)/4 onto the frozen kernel frame
`bdsc.kernel_frame()`, so the same four bits also give the kernel population.
The kernel is the stabilizer space of -Z2 and T; it has weight-one logical
operators and protects against no error.

## The blade bank

All 84 normalized blades (e_i + t e_j)/sqrt2 that occur as left factors of
`cd_core.sedenion_zero_divisor_corpus()` give effects of the same form,
I/2 + s1 P1 / 4 + s2 P2 / 4 with commuting words P1 and P2. A fair coin that
picks one of the two local tests (I + s P)/2 therefore realizes each effect
as a binary measurement, at the cost of the coin's variance.

For the 21 probes (e_i + e_{8+j})/sqrt2 with 1 <= i < j <= 7, which include
E0 at (i, j) = (1, 2):

| quantity | value |
|---|---:|
| probes whose two words are qubit-wise commuting (one local basis) | 12 |
| distinct non-identity words | 28 |
| full-support words | 13 |
| local product bases needed to read all 28 words | 13 |

A product basis reads a word when it matches every non-identity letter, so a
full-support word has exactly one reading basis, itself. Every cover holds the
13 full-support bases, and those 13 read all 28 words, so 13 is the minimum
over local product-basis readouts. It is no bound on entangled or collective
measurements. Probes sharing a basis share its shots, so a joint analysis
carries their covariance.

## Scope

The identities concern the ideal effect under an exact encoding. A transmon
run measures a physical effect shaped by preparation, readout assignment,
leakage, crosstalk and compilation; these identities define the target and
the estimator. They certify no device. The Belenos optical implementation
realizes a different physical map of the same target, and neither platform's
result qualifies the other.
