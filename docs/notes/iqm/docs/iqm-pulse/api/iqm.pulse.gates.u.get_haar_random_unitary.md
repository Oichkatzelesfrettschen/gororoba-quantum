> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_haar_random_unitary.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_haar_random_unitary.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3af9e21219a00e479e9ddde06cc2e7217a7c06b240c35bd84fef73ed63e47821.

# iqm.pulse.gates.u.get_haar_random_unitary

iqm.pulse.gates.u.get_haar_random_unitary(*d=2*, *rng=None*)  
Generates a random unitary matrix drawn uniformly from Haar measure.

Follows the procedure outlined in \[[2](https://docs.iqm.tech/4.7/iqm-pulse/references.html#id8 "Francesco Mezzadri. How to generate random matrices from the classical compact groups. Notices of the American Mathematical Society, 54(5):592–604, May 2007. URL: https://www.ams.org/notices/200705/fea-mezzadri-web.pdf, arXiv:math-ph/0609050.")\]:

1.  Generate a n x n matrix of complex numbers such that both real and imaginary parts of each number are drawn  
    independently from a normal distribution with mean 0 and variance 1.

2.  Perform a QR decomposition of this matrix, obtaining a unitary and upper triangular matrices.

3.  Normalize the unitary, multiplying each column by the sign of a corresponding diagonal entry in the upper  
    triangular matrix, which are guaranteed to be real.

The last step is necessary, because otherwise the non-uniqueness of the QR decomposition introduces bias to the sampling process.

Parameters:  
- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Dimension of the generated unitary.

- **rng** ([*Generator*](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)") *\|* *None*) – Random number generator object.

Returns:  
A random unitary matrix of requested dimension.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
