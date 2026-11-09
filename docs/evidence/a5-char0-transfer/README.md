# Good reduction of the fiber-track germ ideals (characteristic-0 transfer, check 1)

[`reduction_check.py`](reduction_check.py) tests, for each of the ten fiber-track pairs, the conjecture that the
presolved germ ideal J and the Nakayama generators G have good reduction at the two split primes the rank
certificates use: 32009 with i = 10754 and 32029 with i = 9115. It runs the producer that writes the rank engine's
headers (`../a5-kernel-attachments/nullity16_rees_fibers.py`, phase one, the path `fiber_inputs.py` specializes) once
over Q(i) (`ring (0,I)`, `minpoly=I2+1`) and once over each F_p, takes the monic reduced standard basis of J
(`option(redSB)`, `option(redTail)`, dp) and G reduced modulo J, reduces the Q(i) coefficients at the prime (i -> r),
and compares. It also computes the same basis and reduction of G from the retained header each rank certificate binds
(`../a5-exceptional-fibers/working/build/inputs/p<prime>-r<root>/<slug>.sing`) and requires an identical result
(`retained_header_equal` in each record).

Why it matters: [a5-char0-and-kernel-limits.md](../../notes/topics/a5-char0-and-kernel-limits.md) states three checks
under which every h_d certified modulo p holds over Q(i). This is check 1; it makes J over Z[i] localized at p
specialize to the header's J, which checks 2 (the degree-2 relations q(G) in J + m I^2 over Q(i)) and 3 (good reduction of J + m^N) build on.

Falsifier: a coefficient whose denominator is divisible by p, a presolve that eliminates different variables, or an
F_p basis of J (or list of G) that differs from the reduction of the Q(i) one. Mutation: adding 1 to one coefficient
of the Q(i) basis must break the equality; it does on every row.

| Pair | Basis of J over Q(i) (elements, terms) | Largest denominator | G | 32009 | 32029 | Q(i) run |
|---|---|---|---|---|---|---|
| X- -> N- | 12, 78 | 1 | 15 | equal | equal | 4.5 s |
| X+ -> N+ | 12, 78 | 1 | 15 | equal | equal | 4.6 s |
| X+ -> N- | 12, 93 | 1 | 3 | equal | equal | 5.1 s |
| X- -> N+ | 12, 93 | 1 | 3 | equal | equal | 3.9 s |
| Iso -> N- | 1, 5 | 1 | 17 | equal | equal | 2.0 s |
| Iso -> N+ | 1, 5 | 1 | 17 | equal | equal | 2.2 s |
| W8 -> N- | 1, 9 | 1 | 24 | equal | equal | 17.8 s |
| W8 -> N+ | 1, 9 | 1 | 24 | equal | equal | 16.6 s |
| E8-bar -> N- | 16, 148 | 1 | 21 | equal | equal | 59.5 s |
| E8-bar -> N+ | 16, 148 | 1 | 21 | equal | equal | 59.3 s |

Every basis has integer coefficients with no imaginary part, so J is defined over Q. The comparison certifies good
reduction at the two primes tested only: another prime can still change the producer's decomposition or presolve.
The G lists match as reduced forms, and every retained header gives the same basis and G. Verdict: the conjecture survives
on all ten pairs at both primes (ledger A5-247). Records: `reduction-<slug>.json`; logs and `/usr/bin/time -v`
measurements in [`logs/`](logs/) (the longest pair, E8-bar -> N+, 2 min 33 s wall for the three fields and the two headers, and 165 MiB peak
for the controller). Host: the build host, one pair at a time, each Singular call in the producer's 16 GiB cgroup
scope.

Run from the repository root: `"$PYTHON" docs/evidence/a5-char0-transfer/reduction_check.py --slug xm-nm` (slugs as
in `fiber_inputs.SPECS`).

Not covered here: E8-bar -> VB (its header comes from the Nakayama route, `fiber_inputs` slug `e8-vb`) and the radicality and decomposition steps of the W8 all-degree proof over Q(i).

## Checks 2 and 3, and the opposite-sign X fibers over Q(i)

- [`truncation_check.py`](truncation_check.py) (check 3): the monic reduced standard basis of J + m^N over Q(i), m the
  ideal of the seven slice variables (the producer's ring still carries the presolve-eliminated t3 and t8), against the
  same basis from the retained header at both primes. X- -> N- survives at N = 4, 8, 11 and 15, the closing orders of
  degrees 1 to 4: 91, 366, 775 and 1,696 elements, integer coefficients, equal at both primes, a corrupted coefficient
  detected (`truncation-xm-nm-n<N>.json`; ledger A5-249). A first revision took m from the producer ring and read
  refuted on a basis of 2,566 elements against 366; its records were overwritten by the fixed run.
  W8 -> N- survives at N = 4, 7, 10 and 13 (d = 1 to 4): 183, 1,257, 5,009 and 14,761 elements (ledger A5-277).
- [`quadric_lift.py`](quadric_lift.py) (check 2): the degree-2 relations {q : q(G) in J + m I^2} over Q(i) by the
  computation of the modular degree-2 receipts (`working/distribute/out/*/d2/d2-products.sing`), compared with the
  retained K2 at both primes (ledger A5-248, running). A first run took m from the nine-variable producer ring;
  that contracts to the same relation space but added 240 generators, and it was restarted on the slice variables.
- [`span_check.py`](span_check.py): over Q(i), every one of the 126 Pfaffian kernel coordinates reduces to 0 modulo
  J + m * FullF + (G), so G generates the kernel-coordinate ideal at the origin (Nakayama) and the fiber cone of (G)
  is the one the attaching data needs; dropping a generator leaves nonzero remainders (`span-<slug>.json`).
- [`x_opposite_qi.py`](x_opposite_qi.py): the arc certificate of X+ -> N- and X- -> N+ (`../a5-exceptional-fibers/arcs-x/`)
  replayed exactly over Q(i) in Singular: J smooth of dimension 4 at the origin, Phi on V(J) and a formal isomorphism,
  I = w (G'') with (G'') a smooth curve germ, so F(I) = Q(i)[y1, y2, y3] in every degree
  ([`x-opposite-qi.json`](x-opposite-qi.json); ledger A5-270). The first revision computed the gcd in sympy over
  Q(i) and stopped at its 20-minute limit; Singular takes 4 s per incidence.
