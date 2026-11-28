# The A_5 symmetry pattern at A_6: the acting group repeats, the stabilizer does not contain it

Ledger rows A5-259 (refuted as worded) and A5-672 (proved).
[`scripts/a5_a6_stabilizer.py`](../../../scripts/a5_a6_stabilizer.py) computes every number exactly, as ranks over Z
(python-flint `fmpz_mat`) and over Q(i) (SymPy), in 7 s at 79 MiB, with no random draw. Nothing in it is computed
modulo a prime.

## Statements, each checked by `--check`

1. **Derivations.** dim Der(A_n) over Q equals 3, 14, 14, 14 and 14 for n = 2, ..., 6, with the cd_core product
   e_p e_q = cd_sign(2^n, p, q) e_(p xor q). Each Leibniz equation for the pair (p, q) and output r involves only
   D[r][p xor q], D[r xor q][p] and D[p xor r][q], whose index differences all equal g = r xor p xor q. The system
   therefore splits into 2^n blocks of 2^n unknowns, one per g. For n >= 3, the blocks g = 1..7 carry two dimensions
   each and every other block carries none.
2. **Extension.** The 14 rational derivations of A_3, extended block-diagonally as D_n = diag(D_(n-1), D_(n-1)),
   satisfy the Leibniz rule of A_4, A_5 and A_6 at every basis pair (exact integers). The extension is an injective Lie
   homomorphism Der(A_3) -> Der(A_n), and by statement 1 it is an isomorphism: Der(A_6) = g_2.
3. **Action on the kernel coordinates.** The Im-block kernel matrix C_z[a][b] = cd_sign(2^(n-1), a xor b, b) z_(a xor b)
   satisfies C_(D z) = D C_z - C_z D for the 14 extended derivations at n = 5 and n = 6. It also satisfies
   C_(chi z) = D_chi C_z D_chi for every character of (Z/2)^4 and of (Z/2)^5. So G_2 and the (Z/2)^5 character group
   act on the A_6 kernel coordinates exactly as G_2 and (Z/2)^4 act at A_5.
4. **Stabilizers.**

| Point | Nullity of L_y | dim of the G_2 orbit | dim of the stabilizer in g_2 | Character stabilizer in (Z/2)^(n-1) x {+-1} |
|---|---|---|---|---|
| A_5, the N- point z0 | 16 | 6 | 8 | Klein: (0, 1), (1, -1), (4, 1), (5, -1) |
| A_6, the lift of z0 to coordinates 1..15 | 36 | 6 | 8 | Klein x {(0, 1), (16, 1)} (order 8) |
| A_6, the real doubling (y, 0) of the A_5 point | 32 | 11 | 3 | order 8, containing the Klein group |

The prediction written before the run was nullity 32 for both A_6 points. The lift reads 36, and only the real
doubling reads 32. The doubling identity L_((y, 0)) = diag(L_y, L_y) gives 32 by itself, so the lift is the point
whose kernel grows.

## Verdict on A5-259

The claim that the A_6 base-point stabilizer repeats "a G_2 factor and a (Z/2)^5 character group" holds for the group
that acts and fails for the stabilizer. G_2 = Der(A_6) and the (Z/2)^5 characters act on the kernel coordinates
(statements 2 and 3). Neither of the two points tested has a stabilizer containing G_2, since the orbit has dimension 6 or 11. The character stabilizer has
order 8, not 2^5 or 2^6. The repeated piece is the stabilizer subalgebra of g_2 at the lift, of dimension 8 at both
levels, together with the Klein group. This record does not test the A_5 boost and scaling (the SO(2, C) x C^* factor
of H) at A_6.

## Controls (`--self-test`)

- One negated table entry cd_sign(8, 1, 2) changes dim Der(A_3) from 14.
- One changed entry of an extended derivation fails the Leibniz rule of A_6.
- A sign map that negates coordinate 1 alone breaks C_(chi z) = D_chi C_z D_chi.
- Tower control: dim Der(A_2) = 3, so the value 14 belongs to n >= 3.

```sh
"$PYTHON" -B -W error scripts/a5_a6_stabilizer.py --check docs/evidence/a5-a6-stabilizer/result.json
"$PYTHON" -B -W error scripts/a5_a6_stabilizer.py --self-test
```
