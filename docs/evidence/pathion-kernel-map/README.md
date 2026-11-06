# Pathion kernel map: the A_5 sign network on hardware

Left multiplication by a two-term operand e_i + t e_j of the 32-dimensional Cayley-Dickson algebra A_5 pairs the 32
basis states into 16 XOR pairs {k, k XOR m}, m = i XOR j, and its nullity N is the number of pairs on which the
signed permutation K = L_i^T (t L_j) carries equal signs (`gororoba_quantum/pathion_kernel_map.py`; N = 0, 4, 8, 12
for two-term operands, among the A_5 annihilator dimensions 0, 4, 8, 12, 16 of Biss, Dugger and Isaksen,
math/0511691, Theorem 1.2; Skiouris, Aphanics at the Pathion Level, Proposition 2.2, gives 12 and 4 for the pairs
with i < 16 < j). The pairs' outputs are disjoint, so the operator splits over the cosets of
any subgroup V of (Z/2)^5 that contains m, and N is the sum of the coset blocks' nullities.

## What a hardware run can test

A QPU cannot re-prove an exact F_p or integer rank faster than elimination: rank testing over F_q needs Omega(n)
quantum matrix-vector queries (Childs, Hung and Li, arXiv:2102.11349), and distinguishing full rank from nullity one
needs Omega(n) quantum queries even for linear functions (van Apeldoorn and Gribling, arXiv:1810.12030); both bound
query access to an unknown matrix, and the kernel map compiles a known one, so they frame the claim rather than limit
the circuit. A run tests the device's realization of the exactly known sign network. Two design rules follow:

- A test whose input lies on two basis states touches only the four cocycle signs of one pair, whatever the
  dimension; a 32-dimensional claim needs one compiled operator acting on many pairs and a readout that resolves them.
- A diagonal sign applied immediately before a computational-basis measurement is unobservable, and IBM implements a
  diagonal Z as an exact virtual frame change; arms that differ only by such a sign test nothing.

## Package agreement

`scripts/pathion_kernel_map_packages.py` (build host `$PYTHON`) compares hypercomplex, hyprat and hypercomplex-engine
with cd_core on all 1024 basis pairs under the identity map, then recomputes each operand's nullity (python-flint
fmpz_mat rank) and aligned-pair count through each package: `packages.json`, every package 1024/1024 and every operand
equal to `pathion_kernel_map.nullity`.

## Program across platforms

| Platform | Object | State on 2026-11-06 | Record |
|---|---|---|---|
| IBM Heron r2 | the full map: one compiled A_5 SELECT on all 16 pairs, six operands of nullity 0 to 12, twins, mutations, six replicas | case written, awaiting approval; binding dry run on ibm_fez, about 15 s | `results/live/2026-11-06T175157.605255Z/CASE.md` |
| Quantum Inspire Tuna-17 | two-term coset blocks: 4 XOR pairs (16 SELECT signs) on 3 data qubits and the selector, 20 to 22 CZ; the full map routes to 116 to 144 CZ and does not resolve at the measured 0.955 retention per CZ | design only; the account's refresh token needs `qi login --force` | session report, not retained |
| Quandela Ascella | four-term operands, whose 4 x 4 coset blocks include classes absent below dimension 32 | design only; Ascella running, Belenos unreachable since 2026-11-01 | session report, not retained |

Every two-term pair block on these operands is one of the 16 sign matrices Belenos already measured in all 32
configurations (2026-10-30); a photonic two-term kernel map would repeat retained data, which is why the photonic
candidate moves to four-term blocks.
