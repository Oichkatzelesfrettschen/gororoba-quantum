#!/usr/bin/env python3
"""Audit the reviewer's Cayley-Dickson quantum-circuit claims without QPU access.

Dependency: NumPy. No network access, repository imports, or quantum SDK needed.
Run: python audit.py --out audit_results.json

The integer recursive product implements the supplied convention:
    (a,b)(c,d) = (a*c - conjugate(d)*b, d*a + b*conjugate(c)).
A separately implemented iterative sign algorithm is cross-checked on every
basis pair. That iterative algorithm follows cd_core.py, blob
ccb51aa4b9e9bab6ab8675fa634d25cb77291cf1. Counts and matrix identities are exact
integer checks; normalized state-vector checks use double precision.
"""
from __future__ import annotations
import argparse
import json
from fractions import Fraction
from itertools import product, permutations
from pathlib import Path
import numpy as np


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def conjugate(x: np.ndarray) -> np.ndarray:
    z = x.copy()
    z[1:] *= -1
    return z


def cd_product(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    if x.ndim != 1 or x.shape != y.shape:
        raise ValueError('Operands must be equal-length vectors')
    n = x.size
    if n == 0 or n & (n - 1):
        raise ValueError('Dimension must be a positive power of two')
    if n == 1:
        return x * y
    h = n // 2
    a, b, c, d = x[:h], x[h:], y[:h], y[h:]
    return np.concatenate((cd_product(a, c)-cd_product(conjugate(d), b),
                           cd_product(d, a)+cd_product(b, conjugate(c))))


def iterative_sign(dim: int, p: int, q: int) -> int:
    sign = 1
    half = dim >> 1
    while half:
        ph, qh = p >= half, q >= half
        if not ph and not qh:
            pass
        elif not ph and qh:
            p, q = q-half, p
        elif ph and not qh:
            p -= half
            if q:
                sign = -sign
        else:
            qr, pr = q-half, p-half
            if qr == 0:
                return -sign
            p, q = qr, pr
        half >>= 1
    return sign


def sparse(v: np.ndarray) -> dict[str, int | float]:
    return {str(i): (int(z.real) if z.imag == 0 and z.real == int(z.real)
                    else float(z.real)) for i, z in enumerate(v.astype(complex)) if z != 0}


def main() -> dict:
    D = 16
    E = np.eye(D, dtype=np.int64)
    table = np.empty((D,D), dtype=np.int64)
    for i,j in product(range(D), repeat=2):
        z = cd_product(E[i],E[j])
        require(np.count_nonzero(z) == 1 and abs(z[i^j]) == 1, 'Signed XOR product failed')
        table[i,j] = z[i^j]
        require(int(table[i,j]) == iterative_sign(D,i,j), 'Conventions disagree')

    L = []
    for i in range(D):
        mat = np.stack([cd_product(E[i],E[j]) for j in range(D)], axis=1)
        require(np.array_equal(mat.T@mat,E), 'Basis multiplication not orthogonal')
        L.append(mat)

    counts = {'all':0,'ordered_distinct_imaginary':0}
    for i,j,k in product(range(D), repeat=3):
        ls = int(table[i,j]*table[i^j,k])
        rs = int(table[j,k]*table[i,j^k])
        counts['all'] += ls != rs
    counts['ordered_distinct_imaginary'] = sum(
        table[i,j]*table[i^j,k] != table[j,k]*table[i,j^k]
        for i,j,k in permutations(range(1,D),3))
    require(counts['all'] == counts['ordered_distinct_imaginary'] == 1848, 'Census mismatch')

    # Full extension of the reviewer's sign-register map is a permutation.
    permutation = []
    for i,j,s in product(range(D),range(D),range(2)):
        f = int(table[i,j] < 0)
        permutation.append((i*D+(i^j))*2+(s^f))
    require(len(set(permutation)) == 2*D*D, 'Reversible map not bijective')

    a_num = E[1]+E[10]
    proposed_y = E[2]-E[13]
    dark_y = E[4]-E[15]
    bright_y = E[4]+E[15]
    proposed_product = cd_product(a_num,proposed_y)
    require(np.array_equal(proposed_product,E[3]-E[12]+E[8]+E[7]), 'Proposed product mismatch')
    require(not np.any(cd_product(a_num,dark_y)), 'Corrected pair not zero')

    def tagged_data_law(y_num: np.ndarray) -> dict[str,float]:
        initial = np.zeros((D,D,2), complex)
        initial[:,:,0] = np.outer(a_num,y_num)/2
        output = np.zeros(initial.size, complex)
        output[np.asarray(permutation)] = initial.ravel()
        probs = np.sum(np.abs(output.reshape(D,D,2))**2, axis=(0,2))
        return {str(i):float(z) for i,z in enumerate(probs) if z>1e-14}

    # Universal coefficient contraction M, not a unitary multiplication gate.
    M = np.zeros((D,D*D),dtype=np.int64)
    for i,j in product(range(D),repeat=2):
        M[i^j,i*D+j] = table[i,j]
    require(np.array_equal(M@M.T,D*E), 'Contraction singular values mismatch')
    K = M/np.sqrt(D)
    for y in (proposed_y,dark_y,bright_y):
        got = K@np.kron(a_num/np.sqrt(2),y/np.sqrt(2))
        want = cd_product(a_num,y)/(2*np.sqrt(D))
        require(np.allclose(got,want,rtol=0,atol=1e-14),'Coefficient contraction failed')

    # Five-qubit fixed-operand LCU: ancilla high axis, four data qubits.
    H = np.array([[1,1],[1,-1]],dtype=float)/np.sqrt(2)
    select = np.zeros((2*D,2*D),dtype=float)
    select[:D,:D] = L[1]
    select[D:,D:] = L[10]
    full = np.kron(H,E)@select@np.kron(H,E)
    probs = {}
    for label,y in [('reviewer_pair',proposed_y),('corrected_dark',dark_y),('bright_control',bright_y)]:
        initial = np.concatenate((y/np.sqrt(2),np.zeros(D)))
        final = full@initial
        p0 = float(np.vdot(final[:D],final[:D]).real)
        exact = Fraction(int(np.dot(cd_product(a_num,y),cd_product(a_num,y))),8)
        require(abs(p0-float(exact))<1e-14,'LCU probability mismatch')
        require(abs(np.vdot(final,final).real-1)<1e-14,'LCU lost normalization')
        probs[label] = {'p_ancilla_zero':p0,'exact':str(exact)}

    # Fixed-pair associator, all basis pairs: UL=Lab, UR=La Lb.
    for i,j in product(range(D),repeat=2):
        UL = int(table[i,j])*L[i^j]
        UR = L[i]@L[j]
        expected = np.array([int(table[i,j]*table[i^j,k]*table[j,k]*table[i,j^k]) for k in range(D)])
        require(np.array_equal(UL.T@UR,np.diag(expected)), 'Associator witness mismatch')
    i,j,k=1,2,4
    left,right=int(table[i,j]*table[i^j,k]),int(table[j,k]*table[i,j^k])
    psi = np.concatenate((left*E[i^j^k], right*E[i^j^k]))/np.sqrt(2)
    X = np.array([[0,1],[1,0]])
    Z = np.diag([1,-1])
    psi_after=np.kron(H,E)@psi
    basis_check={
        'X_before_final_H':float(psi@np.kron(X,E)@psi),
        'Z_after_final_H':float(psi_after@np.kron(Z,E)@psi_after),
        'X_after_final_H_reviewer_literal':float(psi_after@np.kron(X,E)@psi_after),
    }
    require(abs(basis_check['X_before_final_H']+1)<1e-14,'Hadamard test failed')
    require(abs(basis_check['X_after_final_H_reviewer_literal'])<1e-14,'Basis mismatch not detected')

    # Complexified even associative subalgebra has zero divisors.
    xx=(E[0]+1j*E[1])/np.sqrt(2)
    yy=(E[0]-1j*E[1])/np.sqrt(2)
    require(np.max(np.abs(cd_product(xx,yy)))<1e-14,'Complexification counterexample failed')

    return {
        'scope':'CPU exact arithmetic and ideal statevectors; no QPU acquisition or routed resource estimate',
        'dimension':D,
        'basis_products_cross_checked':D*D,
        'convention':'(a,b)(c,d)=(ac-conj(d)b, da+b conj(c))',
        'operator_dimensions':{'complex':256,'hermitian_real':256,'density_trace_one_real':255,'off_diagonal_real':240,'probability_simplex_real':15},
        'basis_signs_for_reviewer_pair':{f'{i}*{j}':{'sign':int(table[i,j]),'index':i^j} for i,j in [(1,2),(1,13),(10,2),(10,13)]},
        'reviewer_normalized_product':{k:float(v)/2 for k,v in sparse(proposed_product).items()},
        'reviewer_normalized_product_norm_squared':float(np.dot(proposed_product,proposed_product))/4,
        'proposed_U_full_extension_bijective':True,
        'tagged_gate_output_marginal_for_reviewer_pair':tagged_data_law(proposed_y),
        'tagged_gate_output_marginal_for_true_zero_pair':tagged_data_law(dark_y),
        'universal_contraction_MMdagger':'16 I',
        'universal_contraction_success_for_reviewer_pair':'1/16',
        'universal_contraction_success_for_true_zero_pair':'0',
        'fixed_operand_LCU':probs,
        'nonassociating_triples':{k:int(v) for k,v in counts.items()},
        'uniform_all_triples_Hadamard_P1':str(Fraction(1848,4096)),
        'uniform_all_triples_witness_expectation':str(1-2*Fraction(1848,4096)),
        'Hadamard_basis_check':basis_check,
        'example_garbage_labels':{'left_before_cleanup':[1,3,7],'right':[1,2,7],'left_after_cleanup':[1,2,7]},
        'complexified_associative_zero_divisor_verified':True,
        'all_checks_passed':True,
    }

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    result=main()
    text=json.dumps(result,indent=2,sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text+'\n',encoding='utf-8')
    print(text)
