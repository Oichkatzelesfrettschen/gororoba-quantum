-- Invariants of a quadric ideal of a fiber cone, recomputed in Macaulay2 from a retained Singular ideal file.
-- Usage: M2 --script quadric_invariants.m2 NAME FILE VARIABLES
name = scriptCommandLine#1; path0 = scriptCommandLine#2; n = value scriptCommandLine#3;
R = ZZ/32009[y_1..y_n];
text = get path0;
text = replace("ideal K[AH]=", "", text);
text = replace(";", "", text);
text = replace("y\\(([0-9]+)\\)", "y_\\1", text);
K = ideal value ("{" | text | "}");
report = (label, I) -> (
    print("RESULT " | name | " " | label | " generators " | toString numgens trim I | " dim " | toString dim I
        | " degree " | toString degree I | " numerator " | toString numerator reduceHilbert hilbertSeries I));
report("K", K); stdio << flush;
mp = minimalPrimes K; stdio << flush;
print("RESULT " | name | " minimal_primes " | toString sort apply(mp, P -> {dim P, degree P, #select(flatten entries mingens P, f -> first degree f == 1)}));
stdio << flush; Rad = intersect mp;
print("RESULT " | name | " radical_equal " | toString(Rad == K));
if Rad != K then (
    A = K : Rad;
    report("A=K:rad", A);
    print("RESULT " | name | " A_prime " | toString isPrime A | " K:A_equals_rad " | toString((K : A) == Rad)
        | " rad_squared_in_K " | toString isSubset(Rad * Rad, K) | " nil_linear_forms "
        | toString(#select(flatten entries mingens Rad, f -> first degree f == 1)));
    );
C = K + ideal(y_1^2);
print("RESULT " | name | " control dim " | toString dim C | " degree " | toString degree C | " differs "
    | toString(dim C != dim K or degree C != degree K));
stdio << flush;
pd = primaryDecomposition(K, Strategy => ShimoyamaYokoyama);
print("RESULT " | name | " primary_components " | toString sort apply(pd, Q -> {dim Q, degree Q, dim radical Q, degree radical Q})
    | " intersect_equal " | toString(intersect pd == K));
print("DONE " | name);
