# Hardware A_5 operands on the H-orbit diagram of the rank strata

[`hardware_orbits.py`](hardware_orbits.py) places every A_5 operand that a hardware case measured on the orbit diagram
of [the strata regularity record](../../a5-strata-regularity/README.md): the twelve H-orbits of nullity at least 8
(H = G_2(C) x SO(2, C) x C^*), the three nullity-4 strata and the nullity-0 stratum. [`result.json`](result.json) holds
the classification, the incidence search, the named arcs and the controls. [`table.tsv`](table.tsv) holds one row per
operand and case (64 readings: operand, case, backend, cd_core nullity, observable, measured value with its interval
where the retained record gives one, orbit, H-orbit dimension, closures, record path).

The fiber program studies how the nullity-8 closures (W8, E8-bar, Iso, X+, X-) attach to the nullity-12 and 16 orbits
(B9, V, VB, V^a+, V^a-, N+, N-). Six of the twelve orbits carry a measured operand: W8, E8-bar, B9, V, VB and N-. Iso,
X+, X-, V^a+, V^a- and N+ carry none.

## Result

Fifteen distinct operands enter. The cd_core nullity of every operand with nullity at least 8 equals the nullity of its
orbit, and its H-generator rank equals the orbit dimension. No mismatch occurred.

| Operand | Nullity | Stratum or orbit (dimension) | Measuring cases |
| --- | ---: | --- | --- |
| e1 + e17 (null operand) | 0 | S0, outside R_4 | IBM kernel map, coset map, parallel coset; Tuna-17 block b0 |
| e1 + e9 (control) | 0 | S0, outside R_4 | Ascella kernel slice |
| e1 + e26, e2 + e27, e17 - e10 (twin of e1 + e26) | 4 | S4, V(Q) only | IBM kernel map (all three); coset map and parallel coset (e1 + e26, e2 + e27); Tuna-17 block bb (e1 + e26) |
| rank path at t = 1/2 and t = 3/2 | 4 | S4, V(G) only | IBM rank-sector run |
| e1 + e10 | 8 | W8 (12) | IBM kernel map, coset map, parallel coset; Ascella kernel slice; rank path at t = 0 |
| e1 - e10 (mutation) | 8 | W8 (12) | Ascella kernel slice |
| C8 = e1 + e8 + e18 + e27 | 8 | E8-bar (11) | Ascella four-term, two-block and mesh-persistence jobs; IBM parallel coset (coset 5) |
| e1 + e24 | 12 | V (8) | IBM kernel map, coset map, parallel coset |
| e1 + e18 | 12 | VB (7) | IBM kernel map, coset map, parallel coset; Tuna-17 block ba; rank path at t = 1 |
| e17 - e2 (twin of e1 + e18) | 12 | VB (7) | IBM kernel map, coset map, parallel coset |
| B12 = e1 + e10 + e20 + e31 | 12 | B9 (9) | Ascella four-term, two-block and mesh-persistence jobs; IBM parallel coset (coset 2) |
| A16 = e1 + e10 + e18 - e25 | 16 | N- (6) | Ascella four-term job (anchor blocks), two-block and mesh-persistence jobs; rank path at t = 2 |

The case directories are listed in [`result.json`](result.json) under `cases` and in the `record` column of
[`table.tsv`](table.tsv); [the findings](../../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md) interpret the pathion
runs and `results/live/CAMPAIGN_FINDINGS.md` section 6 the rank-sector run. Three observations follow from the table.

- Nullity 12 does not separate orbits. e1 + e24 (V, dimension 8), e1 + e18 and e17 - e2 (VB, dimension 7) read
  N_hat = 12 on the kernel map and the coset blocks, so those readings cannot tell V from VB. B12 (B9, dimension 9) has
  the same nullity, and the hardware reads it through block levels and visibilities, not N_hat.
- The twins keep the orbit class of their primaries: e17 - e2 lies in VB with e1 + e18, and e17 - e10 lies in the same
  nullity-4 stratum as e1 + e26.
- The hardware has measured the opposite end of three incidences only through A16 (N-). The N+ end of E8-bar -> N+ and
  X- -> N+ has no measured operand.

## Method

The map from an operand a = sum a_i e_i to split coordinates is z_k = a_k + i a_(16+k) and
z'_k = i^(-popcount k) z_k for k = 1..15, which inverts `y_from_split` of the equations record and requires
a_0 = a_16 = 0. Every operand of this record is doubly pure. The script evaluates the generators of the twelve closures,
V(Q) and V(G) (`strata_regularity.closure_ideals`) exactly over Q(i), takes the nullity from
`rederive_strata_equations.nullity` (cd_core left multiplication, exact rank), and takes the orbit dimension as the rank
over Q(i) of the sixteen tangent vectors `strata_regularity.h_generators`. The orbit of a point of nullity at least 8 is
the one whose representative has the same membership pattern; the twelve patterns are distinct (strata record,
computation 3). Nullity 4 splits by membership in V(Q) and V(G), and nullity 0 lies in neither.

The map gate pushes each of the twelve representatives through `y_from_split` and back, requires the representative
again, the same pattern, the recorded nullity and the recorded orbit dimension, and runs before any operand. It guards
the one convention that nullity cannot check: the opposite phase direction i^(+popcount k) relabels exactly the three
sign pairs X+ and X-, V^a+ and V^a-, N+ and N-, and `--self-test` requires that relabeling. The N- label of A16
and the sign pairing of the incidence list rest on this convention.

The line search takes each measured operand a_Z of the orbit Z and tests a(s) = a_Z + s b for membership in the closure
of Y at nine values of s. The closure generators have degree at most 4 in z', so vanishing at nine values is
vanishing for every s; the script checks the degree bound and refuses a larger one. The directions b are the
coefficient vectors with entries -2 to 2 over each 2-flat that contains the support of a_Z (the four-term operands
the block designs realize) and every basis vector and basis pair e_k + sigma e_l (supports of up to six indices). A direction counts once per plane span(a_Z, b), because C^* maps the
line a_Z + s b to every other line of its plane. A kept plane reports the orbit of its generic point (majority over
seven values of s), its support, the nullity at s = 0, 1, 2, 1/2, -1, and the measured operands it contains. For each
incidence the script also tests the chord through a_Z and every other measured operand in the closure of Y.

## Incidences

| Incidence | Measured in the open orbit of Y | Measured in Z | Hardware arc probe candidate |
| --- | --- | --- | --- |
| W8 -> N- | e1 + e10, e1 - e10 | A16 | yes, four terms: arc 1 below |
| E8-bar -> N- | C8 | A16 | six terms only: the chord from A16 to C8 |
| E8-bar -> VB | C8 | e1 + e18, e17 - e2 | yes, four terms: arc 2 below |
| Iso -> N- | none | A16 | none among measured operands |
| X+ -> N- | none | A16 | none among measured operands |
| E8-bar -> N+ | C8 | none | not testable: no measured N+ operand |
| X- -> N+ | none | none | not testable: no measured N+ operand |

Arc 1, W8 to N-: a(beta) = e1 + e10 + beta (e18 - e25) on the 2-flat {1, 10, 18, 25}. It lies in the closure of W8 for
every beta. The nullity is 16 at beta = 1 (A16, orbit N-, measured), 8 at beta = 0 (e1 + e10, orbit W8, measured) and
at beta = -2, -1/2, 1/2, 2, 3 (open orbit of W8), and 16 at beta = -1, the operand e1 + e10 - e18 + e25 in the
orbit N+, which no hardware case measured. The plane is stable under the doubling automorphism
(a, b) -> (a, -b), which sends beta to -beta and A16 to that N+ operand. One four-term arc therefore joins a measured
W8 operand to a measured N- operand and to an unmeasured N+ operand.

Arc 2, E8-bar to VB: a(beta) = e1 + e18 + beta (e8 + e27) on the 2-flat {1, 8, 18, 27}. It lies in the closure of
E8-bar for every beta. The nullity is 12 at beta = 0 (e1 + e18, orbit VB, measured) and 8 at beta = 1 (C8, open orbit
of E8-bar, measured) and at beta = -2, -1, -1/2, 1/2, 2, 3. The line from e17 - e2 along e8 + e27 has the same shape and
its E8-bar end e17 - e2 + e8 + e27 is unmeasured. Each of e1 + e18 and e17 - e2 has four such planes with generic orbit
E8-bar (directions e8 +- e27 and e11 +- e24); the other directions in the flats of e1 + e18 and e17 - e2 stay in B9, V,
X+ or X-.

E8-bar -> N-: no line a(s) = A16 + s b with b a coefficient vector on the flat {1, 10, 18, 25} or a basis pair e_k +- e_l
has generic orbit E8-bar and a four-term support. Eight basis-pair planes through A16 (directions e3 +- e24,
e8 +- e19, e8 +- e27, e11 +- e24) have generic orbit E8-bar, and each has six indices. The chord a(s) = A16 + s (C8 - A16)
joins the two measured operands inside the closure of E8-bar: its support is {1, 8, 10, 18, 25, 27}, the nullity is 16
at s = 0 and 8 at s = -1, 1/2, 1 (C8) and 2, and its generic orbit is E8-bar. A six-term arc needs a block design with
three selector qubits; the four-term designs do not realize it.

Iso -> N- and X+ -> N-: the lines from A16 with generic orbit Iso (72 basis-pair planes, directions e3 +- e20, e3 +- e21,
e4 +- e19 and others) and X+ (two planes, e3 + e27 and e11 - e19) all carry six indices. The chords from A16 to the
measured operands e1 + e18 and e17 - e2 stay in VB, and the chord to B12 leaves both closures. No measured operand lies
in the open orbit of Iso or X+.

The chord from A16 to e1 - e10 leaves the closure of W8, so the measured W8 operand e1 - e10 does not lie on an arc
with A16. The chord from A16 to B12 stays in the closure of W8 with generic orbit W8 and six indices (nullity 16 at
s = 0, 12 at s = 1, 8 at s = -1, 1/2 and 2), while the chords from A16 and from e1 + e18 to B12 leave the closures of
E8-bar, Iso and X+. [`result.json`](result.json) lists every chord.

## Rank path

The IBM rank-sector run measured the polynomial path a(t) = e1 + (t-1)^2 e10 + t(3-t)/2 e18 - t(t-1)/2 e25
(`rank_attachments.path_coefficients`) at t = 0, 1/2, 1, 3/2, 2. The operands are e1 + e10 (W8), a nullity-4 point of
V(G) only, e1 + e18 (VB), a nullity-4 point of V(G) only, and A16 (N-). Every other t tested (-1, 1/3, 5/2, 3) has nullity
4 in V(G) only. The path joins three measured orbits through the nullity-4 stratum and lies in no closure of nullity at
least 8, so it probes no incidence of the fiber program; arc 1 and arc 2 do.

## Controls

Cocycle-free e1 + e10 and e1 + e18, the flipped e1 + e18, the skeleton, the readout-flip twins and the mutated four-term
arms are sign networks or arms of a block, not left multiplications of an element of A_5, so no H-orbit applies. Each
is listed under `controls` in [`result.json`](result.json) with its reason.

## Falsifiers

- An operand with nullity at least 8 whose cd_core nullity differs from the nullity of its orbit, whose membership
  pattern matches no representative, or whose H-generator rank differs from the orbit dimension. None occurred.
- A map gate that fails, or a self-test control that passes. The control is the opposite phase direction.
- A value of beta in arc 1 or arc 2 where a(beta) leaves the closure of W8 or E8-bar; the nine-value test decides every
  beta because the closure generators have degree at most 4.
- A line from A16 inside the closure of E8-bar with generic orbit E8-bar and a four-term support outside the searched
  families (coefficients -2 to 2 on the flat of A16, basis pairs): the absence is a bounded search, not a theorem.

## Scope

The record covers the A_5 operands of the pathion kernel map, the coset-block map, the parallel coset blocks, the IBM
rank-sector run, the Tuna-17 coset-block and coin series, the Ascella four-term, two-block and mesh-persistence jobs and
the Ascella kernel-slice job (the ibm_kingston rank-sector payloads were never submitted). Operands of the wide 64-dimensional and 128-dimensional case (A_6 and A_7) fall outside the
A_5 stratification. The Quantum Inspire emulator and the `sim:ascella` twins are not hardware. The one-CZ null blocks
of the Tuna-17 case (`scripts/qi_pathion_one_cz_null_cases.py`) have no retained run. The associator and zero-divisor
cases act in dimension 16 or measure trilinear data, not left multiplications of A_5 elements.

## Replay

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-exceptional-fibers/hardware-orbits/hardware_orbits.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-exceptional-fibers/hardware-orbits/hardware_orbits.py \
    --out docs/evidence/a5-exceptional-fibers/hardware-orbits
```

The run takes about 90 s on ten CPUs through `parallel.py`, and two runs give byte-identical `result.json` and
`table.tsv`. Python 3.14.7 and python-flint 0.9.0 ran it; Singular is not required.
