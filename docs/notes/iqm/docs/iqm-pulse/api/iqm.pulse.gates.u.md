> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cb2f58fc597f9dd12c453f790db6f5132fd556d720e80d74360a62b047786f0e.

# u

Full path: iqm.pulse.gates.u

Single-qubit SU(2) gate.

The SU(2) matrix in the computational basis is parametrized using Euler angles:

\\\begin{split}U(\theta, \phi, \lambda) = \begin{pmatrix} cos(\theta / 2) & -e^{i\lambda}\sin{\theta/2} \\ e^{i\phi}\sin{\theta/2} & e^{i(\lambda+\phi)}\cos{\theta/2} \end{pmatrix}\end{split}\\

where the angles \\\theta\\, \\\phi\\ and \\\lambda\\ are in radians. They are the angles of subsequent Z, Y and Z Euler rotations:

\\U(\theta, \phi, \lambda) = R_Z(\phi) \\ R_Y(\theta) \\ R_Z(\lambda)\\

It rotates the qubit state around an arbitrary axis on the Bloch sphere.

Some common single-qubit gates expressed as U gates:

\\\begin{split}X = U(\pi, -\pi/2, \pi/2)\\ Y = U(\pi, 0, 0)\\ Z = U(0, 0, \pi)\\ H = U(\pi / 2, 0, \pi)\\ S = U(0, \pi / 4, \pi / 4)\\ T = U(0, \pi / 8, \pi / 8) SH = C_XYZ = U(\pi / 2, 0, \pi /2)\\ HS^\dagger = C\_{ZYX} = U(\pi / 2, \pi / 2, \pi)\\\end{split}\\

References

[https://openqasm.com/language/gates.html#built-in-gates](https://openqasm.com/language/gates.html#built-in-gates)

Module Attributes

|  |  |
|----|----|
| [`PI_2`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.PI_2.html#iqm.pulse.gates.u.PI_2 "iqm.pulse.gates.u.PI_2") | Fundamental mathematical constant pi divided by two for performance. |
| [`CLIFFORDS_TO_EULER_DECOMPOSITION`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.CLIFFORDS_TO_EULER_DECOMPOSITION.html#iqm.pulse.gates.u.CLIFFORDS_TO_EULER_DECOMPOSITION "iqm.pulse.gates.u.CLIFFORDS_TO_EULER_DECOMPOSITION") | Mapping of names used to describe Clifford gates to the tuples \\\theta, \phi, \lambda\\ representing their ZYZ Euler angle decompositions. |
| [`ANGLE_THRESHOLD`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.ANGLE_THRESHOLD.html#iqm.pulse.gates.u.ANGLE_THRESHOLD "iqm.pulse.gates.u.ANGLE_THRESHOLD") | If the angle is below this threshold, it is understood to be zero. |

Functions

|  |  |
|----|----|
| [`get_haar_random_unitary`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_haar_random_unitary.html#iqm.pulse.gates.u.get_haar_random_unitary "iqm.pulse.gates.u.get_haar_random_unitary")(\[d, rng\]) | Generates a random unitary matrix drawn uniformly from Haar measure. |
| [`get_su2_params`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_su2_params.html#iqm.pulse.gates.u.get_su2_params "iqm.pulse.gates.u.get_su2_params")(unitary\[, threshold\]) | Calculate parameters for an SU(2) gate given its unitary. |
| [`get_unitary_u`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_unitary_u.html#iqm.pulse.gates.u.get_unitary_u "iqm.pulse.gates.u.get_unitary_u")(theta, phi, lam) | Unitary for an SU(2) gate. |

Classes

|  |  |
|----|----|
| [`UGate`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.UGate.html#iqm.pulse.gates.u.UGate "iqm.pulse.gates.u.UGate") | SU(2) gate implemented using PRX. |

Inheritance

![Inheritance diagram of iqm.pulse.gates.u](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-bd9d9766460dcb18638040404a9099e173453fe1.png)
