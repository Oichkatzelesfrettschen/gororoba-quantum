# Gurvits estimators, Fock marginals and Gaussian normalisation

This note separates exact finite identities, additive amplitude estimation and
full-distribution sampling. The implementation supplies the first two, not the
third. It is a numerical reference and testing surface, not a quantum-advantage
certificate or a machine-checked proof.

## Existing work and ownership

The retained [permanent probe](../../evidence/quandela/permanent-estimators/permanent_probe.py)
already benchmarks exqalibur's Gurvits estimator and exact Ryser/Glynn routines.
Its producer, output and QRNG allocations remain unchanged. The
[Ascella foundations](../quandela/ascella-foundations-and-architecture.md)
already contain the Fock/permanent convention and Hong-Ou-Mandel example.

The estimators live in `gororoba_quantum/`. The Rust workspace holds no copy,
the note touches no private infrastructure, and no paper bytes enter a
documents repository. Existing historical callers retain their
implementations until an individual, digest-aware migration is validated.

| Module | New surface | Boundary |
|---|---|---|
| [photonic_permanents.py](../../../gororoba_quantum/photonic_permanents.py) | Gray-code Ryser, Fock amplitudes, bounded sign/root estimators, complex confidence disks | complex128, numerical spectral norm; no relative guarantee |
| [photonic_marginals.py](../../../gororoba_quantum/photonic_marginals.py) | low-rank coefficient recurrence and selected-mode number marginals | collision-free Fock inputs; fixed number of observed modes |
| [photonic_gaussian.py](../../../gororoba_quantum/photonic_gaussian.py) | hafnian/loop-hafnian references, pure Gaussian PNR probabilities, Fock Husimi estimator | no general adaptive Gaussian circuit simulator |
| [test_photonic_gurvits.py](../../../tests/test_photonic_gurvits.py) | independent algebraic oracles, quadratures and refusal tests | deterministic tests, not empirical iid confidence coverage |

## Passive optical convention

`U[output_mode, input_mode]` acts on creation operators. For input occupation
`t`, output occupation `s`, and equal total photon number,

\[
 A_{s,t}=\frac{\operatorname{Per}(U[s,t])}
 {\sqrt{\prod_i s_i!\prod_j t_j!}}.
\]

Output occupations repeat rows; input occupations repeat columns. Both kinds
of collision are supported by the exact reference and amplitude estimators.
The vacuum amplitude is one; unequal photon numbers have amplitude zero.
The physical entry points require numerical unitarity within `atol`. They do
not renormalise loss away or interpret a nonunitary matrix as a conditional
experiment. A lossy device needs a separately specified dilation/model.

Gray-code Ryser uses O(n 2^n) arithmetic and O(n) scratch storage. Here "exact"
describes the finite combinatorial identity, not the floating-point result.
`max_photons` refuses an oversized exponential calculation before enumeration.

## Bounded complex estimates

For the ordinary sign estimator,

\[
 X(x)=\left(\prod_j x_j\right)\prod_i(Ax)_i,\qquad
 x_j\in\{-1,+1\},\qquad E[X]=\operatorname{Per}(A).
\]

The sample modulus obeys `|X| <= ||A||_2^n`. A two-coordinate Hoeffding/union
bound yields

\[
 \Pr(|\bar X-E X|>r)\le 4e^{-Nr^2/(4B^2)},\qquad
 r=2B\sqrt{\log(4/\delta)/N}.
\]

The implementation uses this complex disk, not an unmodified one-dimensional
interval. `sample_budget(epsilon, delta)` returns
`ceil(4 log(4/delta)/epsilon^2)` subject to its allocation limit.

For an n-by-k matrix B with column multiplicities s summing to n, draw each
x_j uniformly from the (s_j+1)-th roots of unity. Aaronson-Hance's estimator is

\[
 X(x)=
 \left(\prod_j\frac{s_j!}{s_j^{s_j/2}}\right)
 \left(\prod_j\bar x_j^{s_j}\right)
 \prod_i\left(\sum_j B_{ij}\sqrt{s_j}x_j\right).
\]

Its modulus bound is the prefactor times `||B||_2^n`. Zero multiplicities
are removed. Transposition supplies the row-repeat version. The physical
Fock estimator evaluates both deterministic row/column bounds, selects the
smaller one before drawing, and divides by the Fock factorial normaliser.
It supports collisions on both sides without promising a useful relative
bound in every case.

A disk `(z,r)` propagates to an interval for the squared modulus:

\[
 [\max(0,|z|-r)^2,\ (|z|+r)^2].
\]

The result is not clipped at one because the same record also represents
unnormalised permanents. Physical probabilities may intersect it with [0,1].
Squaring an unbiased amplitude estimate is generally biased.

The SVD used for the numerical norm adds dense linear-algebra cost: for a
square matrix, the implemented path is O(n^3 + N n^2), not solely
O(N n^2). This distinguishes the implementation from an abstract estimator
given a suitable norm bound.

## Fixed-mode marginals

For collision-free occupied input modes, the output-count generating function
on k selected modes is

\[
 G(z)=\operatorname{Per}\left(I+
 \sum_{a=1}^k(z_a-1)\bar u_a u_a^T\right).
\]

The correction has rank at most k. The implementation obtains its coefficients
from the bivariate product

\[
 \prod_{i=1}^{n}(1+(L_i\cdot x)(R_i\cdot y)),\qquad
 \operatorname{Per}(I+LR^T)=\sum_\alpha \alpha!\,\left[x^\alpha y^\alpha\right]\left(\cdots\right).
\]

It expands `(z_a-1)^alpha_a` to recover number probabilities. It does not sum
over every unmeasured Fock outcome. The coefficient state count is bounded by
`sum_d binom(d+k-1,k-1)^2`, giving n^O(k) arithmetic for fixed k, with a
conservative `max_work` preflight. Growing k removes that efficiency claim.

The marginal record retains raw mass error, largest imaginary residual and
clipped negative mass. It rejects excessive cancellation or aggregate
negative mass. It performs no final renormalisation. These diagnostics are
necessary checks, not a rigorous error enclosure: errors that preserve mass
and positivity can still escape them. Repeated input occupations are rejected
rather than silently applying the collision-free identity.

## Product-Fock Husimi estimator

The implemented specialization of Lim-Oh draws

\[
 |\alpha_i|^2\sim\Gamma(t_i+1,1),\quad
 \arg\alpha_i\sim\operatorname{Uniform}[0,2\pi),
\quad X(\alpha)=\frac{\langle s|U\alpha\rangle}{\langle t|\alpha\rangle}.
\]

For normalised states and an exactly unitary U, `E[X]=<s|U|t>` and
`E|X|^2 <= 1`. The Gaussian factors cancel. Log magnitudes and unit phases
avoid unnecessary product overflow.

These samples are unbounded. Their interval therefore uses median-of-means,
not bounded-sample Hoeffding. Blocks have at least `8/epsilon^2` samples;
an odd number of blocks is at least `8 log(2/delta)`. Chebyshev at coordinate
threshold `epsilon/sqrt(2)` and Hoeffding on independent blocks give a complex
disk of radius epsilon with failure probability at most delta. Coordinatewise
medians need not themselves be unbiased.

All draws precede parallel work. Independent kernels and block means use the
repository's order-preserving process map. No module creates or seeds an RNG.
A production caller must supply the existing QRNG-provenance-bound Generator.
Deterministic fixture streams are not evidence for statistical coverage.

## Hafnians and Gaussian states

The reference hafnian recursively pairs vertices with memoised subproblems.
Ordinary diagonal entries do not contribute; explicit singleton weights
supply the loop hafnian. Complex symmetry, not Hermitian symmetry, is required.
Ordinary odd-dimensional hafnians are zero without recursive enumeration.

For a zero-mean pure Gaussian state
`C exp(a^dagger B a^dagger/2)|vacuum>`, B is complex symmetric and a strict
contraction. The implemented PNR probability is

\[
 p(s)=\sqrt{\det(I-BB^\dagger)}
       \frac{|\operatorname{Haf}(B_s)|^2}{\prod_i s_i!}.
\]

Analytic checks include single-mode squeezing and
`B=[[0,q],[q,0]]`, for which `p(k,k)=(1-|q|^2)|q|^(2k)`.
These checks lock down the vacuum factor independently of any approximate
hafnian claim.

This is not the full Lim-Oh hafnian extension. A Gaussian coherent-state
proposal, its exact variance bound and published normalisation must be audited
together before adding that estimator. Displacement, mixed states, loss,
threshold detection and adaptive measurements are not implemented by this
pure-state formula.

## Numerical and execution boundaries

Inputs reject nonfinite matrices, invalid integral occupations, invalid
failure probabilities and malformed root points. The code refuses known
scale overflow/underflow and nonrepresentable squared interval upper bounds.
Real-component normalisation avoids a complex reciprocal overflow at
subnormal spectral norms.

Neither an SVD norm nor a complex128 result is an interval certificate.
Confidence bounds assume independent ideal draws and exact arithmetic;
`atol` is a numerical admission tolerance, not a systematic-error bound.
Exponentially small amplitudes can remain unresolved by an additive interval.
No full-output sampler or quantum-advantage inference follows.

The element/work limits bound requested problem sizes, not process RSS.
The enclosing runner still owns wall-time and memory limits. The exponential
methods, fixed-mode recurrence and all-at-once sample arrays have different
resource profiles.

## Native validation and remaining integration

Run the repository's pinned format, lint and type tools on the three modules
and test file, then run `"$PYTHON" -B -m pytest -q tests/test_photonic_gurvits.py`.
The `lint`, `types`, `tests` and `contracts` checks of the pull-request
workflow admit a change to these modules.

The modules make no hardware job, provider upload, QRNG call or
retained-acquisition rewrite. Call-site migration, empirical iid coverage and
formal proofs remain open work.

## Primary references

Citation status: the three sources marked "cited by identifier" below are not
registered in [SOURCES.json](../../SOURCES.json) and have no reading copy or
paper note in this repository, so their section and theorem locators are
unverified. The registered Aaronson and Arkhipov note records a reading scope
of the title page, abstract and contents only, so its locator is unverified too.

- Aaronson and Hance, *Generalizing and derandomizing Gurvits's approximation
  algorithm for the permanent*, QIC 14 (2014), 541-559;
  [arXiv:1212.0025](https://arxiv.org/abs/1212.0025) (cited by identifier).
  Repeated rows/columns and the roots-of-unity estimator.
- Aaronson and Arkhipov, *The Computational Complexity of Linear Optics*,
  Theory of Computing 9 (2013), 143-252; the preprint is registered as
  [arXiv 1011.3245](../papers/1011.3245.md).
  Section 12's Gurvits results, low-rank identity and fixed-mode marginals.
- Lim and Oh, *Classical algorithms for estimating expectation values in
  linear optical circuits*, [arXiv:2502.12882v3](https://arxiv.org/html/2502.12882v3)
  (cited by identifier). Theorem 2 and Supplement S4 for coherent-state overlap estimation.
  This implementation does not claim to implement every hafnian or adaptive extension.
- Hamilton et al., *Gaussian Boson Sampling*, PRL 119, 170501 (2017);
  [arXiv:1612.01199](https://arxiv.org/abs/1612.01199) (cited by identifier).
  Gaussian photon-count probabilities and hafnians.
