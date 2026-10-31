# Computer algebra orderings and local invariants

Exact replays compute in global monomial orderings (`dp`, `lp`). A local
invariant at a point p, such as a tangent cone, multiplicity or singularity
type, comes from the deformation to the normal cone: translate p to 0,
substitute t -> h t, take `sat(I, h)` (an ideal in Singular 4.4, not a list)
and set h = 0. The reduced germ at p is the intersection of the `minAssGTZ`
primes through p, with no prior `radical()`. Local orderings (`ds`,
`tangentcone`) on the A_5 strata ran past an hour at tens of GiB on the shared
host, while the global route takes seconds
([a5-strata-regularity](../evidence/a5-strata-regularity/README.md)). A long
Singular or msolve run follows the flag review in
[compute-flags.md](compute-flags.md).
