Verdict: the mathematical core of A5-530 through A5-536 survives, but the pull request is not merge-ready. One pinned type-check failure and four evidence/documentation defects remain. No counterexample to the central orbit-normal-form results was found.

## Findings, ranked by consequence

1. **SERIOUS — computed: the required type gate fails.**  
   `tests/test_a5_nullity4_orbit_normal_forms.py:97` multiplies a list by `forms.CERTIFICATE["entries"]`, whose inferred type is `object`. Pinned mypy 2.4.1 reports:
   ```text
   error: Unsupported operand types for * ("list[int]" and "object") [operator]
   Found 1 error in 1 file
   ```
   The certificate needs a typed structure, or the test must narrow `entries` to `int`.

2. **SERIOUS — computed: the retained-record test passes after record corruption.**  
   `tests/test_a5_nullity4_orbit_normal_forms.py:161-165` compares only `sorted(retained)` with `sorted(expected_record())`, hence only the JSON keys. Changing `complement_pfaffian_sign` from 1 to 0 produced:
   ```text
   record-key-test-after-value-mutation: True
   verdict-after-value-mutation: ['the Pfaffian of the complement block is not G']
   ```
   Thus `test_record_rules_accept_the_pinned_record` passes for the wrong reason. It should compare the complete record and call `forms.verdict(retained)`. The on-demand replay catches the defect, but pull-request tests do not.

3. **SERIOUS — proved: the producer overstates what its pass verdict establishes.**  
   `nullity4_orbit_normal_forms.py:22` says it checks items 1–7 exactly, while `:460-476` executes fifteen identities. It does not mechanize:

   - the \(G_2(\mathbb C)\)/\(SL_3\) orbit theorem in `:9-20`;
   - the binary-form factor cases in `:37-47`;
   - the semicontinuity and irreducibility argument in `:48-51`;
   - the reduction from the common-kernel equations to \(W=M_C(h)\Omega\) in `:56-65`.

   The identities support those prose arguments, but `pass: 15 identities...` is not a certificate of the complete items. The docstring should distinguish checked identities, finite-field observations, and prose lemmas.

4. **SLOPPY — proved: the README drops an essential hypothesis and states a false theorem.**  
   `docs/evidence/a5-kernel-bundles-residuals/README.md:393-396` says “a quartic of length 3 is irreducible.” The ledger correctly says “length 3 and no line” at `ledger.tsv:500`.  
   Counterexample: \(F=z(x^3+y^3+z^3)\) is reducible, and on the chart \(y=1\) its singular ideal is
   \[
   (z,\ x^3+1),
   \]
   of length 3. The README must restore “and contains no line.”

5. **SLOPPY — computed: a test comment gives a false boundary example.**  
   `tests/test_a5_nullity4_orbit_normal_forms.py:73-80` says the quartic at \(\rho=v_1=0\), \(\mu^2=-1\), vanishes on neither line. Exact factorization gives
   ```text
   (s - I*t)*(s + I*t)*(c0**2 + s**2 + t**2)
   ```
   so it contains two lines. This point is outside the claimed \(\rho\ne0\) normal form, so A5-531 survives; the comment should instead say that \(\rho\ne0\) is necessary.

## Proof audit

- **A5-530 — proved.** The complex \(G_2\) stabilizer theorem reduces a nondegenerate Gram plane to \(\langle e_1,e_2\rangle\); the two 120-degree rotations ensure \(u\cdot u\ne0\). The replay independently verifies block decoupling, Pfaffian \(G\), rotation covariance, and the double-cross-product identity (`nullity4_orbit_normal_forms.py:280-327,437-457`).

- **A5-531 — proved, with the producer-scope qualification above.** The binary-form factor analysis is complete. In the \(\epsilon=0\) case, \(\mu^2+\rho^2=0\) makes the tangent line equal to \(r=0\), already excluded by the \(-2\rho^2\) mixed coefficient. The exact probe confirmed this equality and found no factor at the fixed point \(v_1=\mu=i,\rho=1\).

- **A5-532 — proved.** The required lemma is the constant-rank kernel-bundle derivative:
  \[
  dK(d)=0\iff dA(d)\,P=0.
  \]
  The common-kernel argument gives \(C(P)=\mathbb Cz\). That line lies in the tangent space because \(C(P)\subset V(Q)\), while \(G(z)\ne0\). After quotienting the real scaling direction, the differential is injective. No tangent-space gap remains.

- **A5-533 — proved.** Good reduction at a rank-12 fixture makes the relative singular scheme finite near that fiber; upper semicontinuity of fiber length gives characteristic-zero length at most 3 from the length-3 special fiber. The base scheme supplies length at least 3. A reducible quartic without a line is two conics, whose intersection has Bézout length 4. The README alone omits the no-line hypothesis.

- **A5-534 — proved.** For \(K=\mathbb Cz\oplus l_z\), \(SL_2\) has the three stated projective orbits. A closed stable higher-zero-divisor locus missing \(z\) cannot meet the open orbit; A5-479 and A5-492 force every point of \(l_z\) to have rank at most 10.

- **A5-535 — proved.** The block equations imply \(M(a)l_z=0\), \(b\in l_z\), \(b\parallel p_2\), and \(M(z)a\parallel\nabla G(z)\). For each \(\sigma=\pm1\), the three unit ideals
  \[
  (W,\ R_\sigma,\ 1-y\rho,\ 1-wf)=(1),
  \quad f\in\{v_1,\mu,\rho-\sigma\},
  \]
  force a zero of \(W\) with \(\rho\ne0\) to be \((0,0,\sigma)\), the excluded rank-10 point. Both signs replayed successfully.

- **A5-536 — proved.** The quaternion stabilizer fixes \(O'\), while \(l_z\) is the standard \(SL_2\)-module. Schur’s lemma identifies \(M(a)|_{l_z}\) with a map \(\mathbb C^7\to\operatorname{Hom}_{SL_2}(V,4V)\cong\mathbb C^4\); its kernel has dimension at least 3, giving \(\dim L\ge6\).

- **A5-537–A5-540 — correctly open.** Their `32029` primes column and bases claim only finite-field samples, exact fixtures, or consequences of proved rows. None promotes the unproved universal rank, fiber-dimension, quaternion-orbit, discriminant-length, or irreducibility statements.

## Supersession conservation

- A5-433(a) continues as proved A5-536 plus open A5-539; (b) is A5-532; (c) continues as A5-538, retaining A5-436’s small-fiber control.
- A5-443’s no-line and \(\dim L=2\) clauses are A5-531 and A5-532.
- A5-444’s polar-line locus is A5-534; the only-if fiber criterion is A5-535; its remaining dimensions and orbit characterization are A5-538 and A5-539.
- A5-445’s proper closed subset is A5-533; its exact discriminant lengths and global irreducibility remain A5-540.

No clause was dropped.

## New conjectures

- **Hypothesis:** at a normal-form point,
  \[
  C(l_z)\cong 3\mathbf1\quad(\mu\ne0),\qquad
  C(l_z)\cong4\mathbf1\oplus V_2\quad(\mu=0)
  \]
  as an \(SL_2\)-module.  
  Falsifier: a symbolic stabilizer generator acts with another weight decomposition. Cheapest test: compute the nullspace and two \(sl_2\) generator matrices over the two normal-form function fields.

- **Hypothesis:** the singular-scheme length equals
  \[
  3+\deg\gcd(\chi,\chi')
  \]
  scheme-theoretically: 3 for simple roots, 4 for a double root, and 5 for a triple root.  
  Falsifier: a normal-form point whose Jacobian quotient length differs. Cheapest test: exact Singular saturation over the discriminant and subresultant strata.

- **Hypothesis:** after saturating by \(\rho\), the ideal generated by \(W\) and the normal-form relation is supported scheme-theoretically at \((v_1,\mu,\rho-\sigma)\), with no embedded component.  
  Falsifier: a nontrivial associated prime or multiplicity away from that maximal ideal. Cheapest test: exact saturation and primary decomposition for both signs.

## Executed checks

```text
producer --check: pass: 15 identities, 2 common-kernel certificates, 120 samples
pytest: 40 passed in 3.63s
ledger.py --check: exit 0
ruff check: All checks passed
ruff format --check: 2 files already formatted
mypy 2.4.1: 1 error in tests/test_a5_nullity4_orbit_normal_forms.py:97
git diff --check: clean
HEAD/status: d129e83a312d8d7a4ffc6b15333e69c1ff1b41b7, clean
```

No repository file was changed.

