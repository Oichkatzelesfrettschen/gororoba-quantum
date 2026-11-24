-- Invariants of a quadric ideal over Q(i), recomputed in Macaulay2 from relation lines dumped by
-- weight_slice_fiber_relations.py. Hilbert data in R = Q(i)[y]; minimal primes and primary components over QQ in
-- L = QQ[jj, y] modulo jj^2 + 1, which is isomorphic to R, then mapped to R for dimension, degree and linear forms.
-- The control adds the square of the first variable; the driver also checks a copy with one relation removed.
-- Usage: M2 --script qi_invariants.m2 NAME FILE
name = scriptCommandLine#1; path0 = scriptCommandLine#2;
lns = lines get path0;
n = value (separate(" ", lns#0))#1;
polys = drop(lns, 1);
F = toField(QQ[jj]/(jj^2+1));
R = F[y_1..y_n];
L = QQ[jj, y_1..y_n];
conv = s -> replace("y\\(([0-9]+)\\)", "y_\\1", replace("i", "jj", s));
use L; KL0 = ideal apply(polys, p -> value conv p); KL = KL0 + ideal(jj^2+1);
toR = map(R, L, {promote(F_0, R)} | gens R);
K = toR KL0;
report = (label, I) -> print("RESULT " | name | " " | label | " generators " | toString numgens trim I | " dim " | toString dim I
    | " degree " | toString degree I | " numerator " | toString numerator reduceHilbert hilbertSeries I);
report("K", K); stdio << flush;
mpL = minimalPrimes KL; mp = apply(mpL, P -> trim toR P);
print("RESULT " | name | " minimal_primes " | toString sort apply(mp, P -> {dim P, degree P, #select(flatten entries mingens P, f -> first degree f == 1)}));
stdio << flush; Rad = intersect mp;
print("RESULT " | name | " radical_equal " | toString(Rad == K));
C = K + ideal(R_0^2);
print("RESULT " | name | " control dim " | toString dim C | " degree " | toString degree C | " differs "
    | toString(dim C != dim K or degree C != degree K));
stdio << flush;
pdL = primaryDecomposition(KL, Strategy => ShimoyamaYokoyama); pd = apply(pdL, Q -> trim toR Q);
rd = apply(pdL, Q -> trim toR radical Q);
print("RESULT " | name | " primary_components " | toString sort apply(#pd, k -> {dim pd#k, degree pd#k, dim rd#k, degree rd#k})
    | " intersect_equal " | toString(intersect pd == K));
print("DONE " | name);
