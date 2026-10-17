# galois

## NAME

galois 0.4.11 -- NumPy arrays over finite fields GF(p^m), with GF(2) linear
algebra, polynomials and BCH / Reed-Solomon codes (numba-compiled kernels).

## SYNOPSIS

```python
import galois, numpy as np
GF2 = galois.GF(2)
a = GF2([[1, 1, 0], [0, 1, 1], [1, 0, 1]])
np.linalg.matrix_rank(a); a.row_reduce(); a.null_space()
np.linalg.solve(a_invertible, b); np.linalg.inv(a_invertible)
a @ b   # matrix product over GF(2)
```

| Substrate | Status |
| --- | --- |
| Build host | python-galois 0.4.11 (Arch) with numba 0.68.0 |
| Kaggle | `galois==0.4.11` and `numba==0.68.0` in the `quantum-tools` group; both installed at their pins on the CPU kernel run `results/kaggle/2026-10-16T163552Z-gororoba-substrate-crossover-cpu` (`pin_groups.json`) |

## CAPABILITIES IN THIS REPOSITORY

- GF(2) linear algebra for Boolean ANF. The Moebius transform of
  `gororoba_quantum/boolean_anf.py` is multiplication by the n-fold Kronecker
  power of `[[1, 0], [1, 1]]` over GF(2); the example reproduces
  `anf_coefficients` for the dim-16 Cayley-Dickson sign function (8 variables)
  and shows the matrix is an involution. Rank, row reduction, null spaces and
  solves over GF(2) are the operations needed for the linear forms of the
  cubic normal form in `docs/evidence/ccz-reduction/normal_form.json`
  (independence of three linear forms is a GF(2) rank condition).
- Stabilizer and CNOT-network bookkeeping: the binary symplectic matrices of
  a Clifford (`stim.Tableau.to_numpy` returns boolean arrays; wrapping them in
  `GF2` was not run) would give exact rank, inverse and products
  ([stim.md](stim.md)).
- Phase-polynomial structure: the ANF masks that pyzx's TODD optimizer
  manipulates are GF(2) vectors ([pyzx.md](pyzx.md)).
- Codes: `galois.BCH`, `galois.ReedSolomon` and the LFSR classes
  (`FLFSR`, `GLFSR`, `berlekamp_massey`). Reed-Muller codes, which match the
  Reed-Muller bounds in the ccz-reduction evidence, are not in 0.4.11
  (`galois.ReedMuller` does not exist; see the gaps in the README).
- Extension fields `GF(2**m)` with `galois.Poly`, `irreducible_poly` and
  `primitive_poly` (introspected; not run).

## API ENTRY POINTS

`galois` public names (73), by introspection:

classes:

```text
  Array, BCH, FLFSR, FieldArray, GF2, GLFSR, Poly, ReedSolomon
```

functions:

```text
  Field, GF, are_coprime, berlekamp_massey, carmichael_lambda, conway_poly,
  crt, divisor_sigma, divisors, egcd, euler_phi, factors,
  fermat_primality_test, gcd, get_printoptions, ilog, intt, iroot,
  irreducible_poly, irreducible_polys, is_composite, is_cyclic,
  is_normal_element, is_perfect_power, is_powersmooth, is_prime,
  is_prime_power, is_primitive_element, is_primitive_root, is_smooth,
  is_square_free, isqrt, jacobi_symbol, kronecker_symbol, kth_prime,
  lagrange_poly, lcm, legendre_symbol, matlab_primitive_poly,
  mersenne_exponents, mersenne_primes, miller_rabin_primality_test, mobius,
  next_prime, normal_element, normal_elements, ntt, perfect_power,
  pollard_p1, pollard_rho, prev_prime, primes, primitive_element,
  primitive_elements, primitive_poly, primitive_polys, primitive_root,
  primitive_roots, printoptions, prod, random_prime, set_printoptions,
  totatives, trial_division
```

modules:

```text
  typing
```

## EXAMPLES

```python
import sys
sys.path.insert(0, "gororoba_quantum")
import numpy as np
import galois
import boolean_anf as ba
import cd_core

GF2 = galois.GF(2)
n = 8                                   # variables: p (bits 0-3) and q (bits 4-7) of the dim-16 product e_p e_q
truth = [0 if cd_core.cd_sign(16, v & 15, v >> 4) > 0 else 1 for v in range(2**n)]

# Moebius transform over GF(2): ANF = (kron of [[1,0],[1,1]]) @ truth table
m1 = GF2([[1, 0], [1, 1]])
moebius = GF2([[1]])
for _ in range(n):
    moebius = np.kron(moebius, m1)
anf = moebius @ GF2(truth)
masks = tuple(int(i) for i in np.nonzero(np.asarray(anf))[0])
print("galois ANF equals boolean_anf.anf_coefficients:", masks == ba.anf_coefficients(truth))
print("monomials by degree:", ba.anf_degree_histogram(masks), " degree", ba.anf_degree_from_coefficients(masks))
print("Moebius matrix is an involution over GF(2):", bool((moebius @ moebius == GF2.Identity(2**n)).all()))

# degree-2 monomials -> symmetric matrix B[a, b] = 1 for a monomial x_a x_b; its GF(2) rank
b = GF2.Zeros((n, n))
for mask in masks:
    bits = [i for i in range(n) if mask >> i & 1]
    if len(bits) == 2:
        b[bits[0], bits[1]] = b[bits[1], bits[0]] = 1
print("rank of the degree-2 monomial adjacency matrix:", np.linalg.matrix_rank(b))

# solve, null space, row reduction
a = GF2([[1, 1, 0], [0, 1, 1], [1, 0, 1]])
print("rank of a 3-cycle parity matrix:", np.linalg.matrix_rank(a), " null space:", a.null_space().tolist())
print("row_reduce:", a.row_reduce().tolist())
print("solve [1,1,1]:", np.linalg.solve(GF2([[1, 0, 0], [1, 1, 0], [0, 1, 1]]), GF2([1, 1, 1])).tolist())
```

Output:

```text
galois ANF equals boolean_anf.anf_coefficients: True
monomials by degree: {2: 10, 3: 12, 4: 7}  degree 4
Moebius matrix is an involution over GF(2): True
rank of the degree-2 monomial adjacency matrix: 8
rank of a 3-cycle parity matrix: 2  null space: [[1, 1, 1]]
row_reduce: [[1, 0, 1], [0, 1, 1], [0, 0, 0]]
solve [1,1,1]: [1, 0, 1]
```

## INTEROP WITH QISKIT

None in the package. The bridge is NumPy: `GF2(np.asarray(bits))` from any
0/1 array, `np.asarray(gf2_array)` back to `uint8`. Qiskit objects reach it
through Clifford tableaus (`qiskit.quantum_info.Clifford(...).tableau` is a
boolean array) or ANF masks of a truth table. Not run: building a `GF2` from
a `Clifford.tableau`.

## CPU AND GPU

CPU. Operations run through numba-compiled ufuncs (numba 0.68.0 is pinned
beside it in the group). A 200 x 200 GF(2) matrix product took 0.0004 s on a
repeat call on this host. No GPU path.

## TRAPS

- Operands must be field arrays. Adding a plain `numpy` array to a `GF2`
  array raises `TypeError: Operation 'add' requires both operands to be
  instances of <class 'galois.GF(2, ...)'>` and `@` raises `TypeError: Argument
  'B' must be an instance of ...` (observed); wrap both sides with `GF2(...)`.
- Index `i` of a truth table is the packed input (bit `k` is variable `k`),
  the convention of `boolean_anf.anf_coefficients`. The Kronecker power of the
  one matrix `[[1, 0], [1, 1]]` is the same for either bit order.
- The Moebius matrix has 2^n x 2^n entries; the matrix form is a check at
  n <= 12, and `boolean_anf.anf_coefficients` is the in-place O(n 2^n) route.

## LICENSE

MIT.
