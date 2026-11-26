# PR 910 audit — `ed7ba5d781ae`

Base: `12da378d3180`. Read-only audit; the worktree remains clean.

## Ranked findings

1. **SERIOUS — [proved] Claim 9 is false: `check()` accepts records that depart from Claims 1–4.**

   `quadric_and_germ_probes.py:217` counts row kinds but never binds the expected `(kind, fiber, prime, input, pivot)` tuples. Lines 252–253 count colon forms but never establish that they are linear. The tests at `test_a5_quadric_and_germ_probes.py:40` mutate numeric/count fields only.

   Deterministic counterexamples:

   ```text
   pivot removed => []
   nonlinear colon form => []
   E8 N- germ replaced by duplicate => []
   32029 VB row relabeled 32009 => []
   ```

   Each empty list means acceptance. These mutations respectively remove Claim 2’s test, violate Claim 4’s linearity, remove a Claim 1 cell, and remove a Claim 3 prime.

   Remedy: require the exact 16 row identities without duplicates; bind input/relations paths and expected pivot indices; verify every recorded colon form has total degree one or equals the expected fixed list; add these four mutations to the test.

2. **SERIOUS — [proved] A5-542’s `proved/both` scope exceeds its cited computation by one cell.**

   `ledger.tsv:521` scopes A5-542 to both signs at both primes, while its basis and `quadric_and_germ_probes.py:62` cover X− at 32009 and 32029 and X+ only at 32029. The row itself says X+ at 32009 has no retained K2.

   The mathematical claim is recoverable without another computation: A5-013’s sign isomorphism transports X−→N− at 32009 to X+→N+ and preserves colon, double-colon, and Hilbert series under the induced coordinate automorphism. The present A5-542 basis does not invoke that theorem.

   Remedy: explicitly cite A5-013 and state this transport, or narrow A5-542 to the three retained K2 cells.

3. **SLOPPY — [computed] A5-027 and the README overstate what the retained record compares.**

   `ledger.tsv:28` and `structure/README.md:190` say each 32029 germ equals the 32009 text modulo 32029. For E8-bar→N−, `quadric_and_germ_probes.py:56` sets the comparison input to `None`, so its JSONL row has no `equals_32009_text`.

   The omitted comparison is true: my direct global-`dp` Singular check returned:

   ```text
   equals_32009_text 1
   radical 1
   minimal_primes 1
   through_origin 1
   ```

   This is a record-coverage defect, not a mathematical counterexample. Retain that comparison as the eleventh row’s explicit field.

## Claims 1–8

- **Claim 1 — [computed/proved] Sound.** The replay gives radical `1`, one minimal prime, and origin containment for all 11 cells. Radical plus one minimal prime makes `J` prime. Direct text extraction also found every tested `J` identical to its same-prime canonical header. Finding 3 applies only to the omitted cross-prime comparison.

- **Claim 2 — [computed/proved] Sound.** Each recorded pivot has nonzero normal form modulo prime `J`; hence it is a nonzerodivisor. I separately checked canonical G3 for E8-bar→VB and G16 for Iso where wrapper `G` text differs; both returned `pivot_in_J 0`.

- **Claim 3 — [computed/proved] Sound.** The absolute-primality step is valid by the regular-local-ring criterion and the smooth-rational-point criterion: a reduced zero-dimensional section at an Fp-point makes the three section forms generate the maximal ideal of the threefold local ring, hence the point is smooth. An integral variety over the perfect field Fp with a smooth rational point cannot split into a transitive family of geometric components. The component degrees, reduced plane intersection, orbit degrees, and Hilbert values replay exactly.

- **Claim 4 — [computed/proved] Sound on the three computed cells.** Singular’s `hilb(I,1)` manual states that it returns the numerator over `(1-t)^n` and that its final entry is metadata, confirming the code’s `[:-1]`. The exact sequence
  `0 → P/K2 → S/K2 → S/P → 0`
  and the verified numerator identity give
  `H(P/K2)=H(S/A)-1`; twelve independent linear generators make `S/A` a polynomial ring in three variables, yielding `C(d+2,2)` for every `d≥1`. Finding 2 applies to the fourth scoped cell.

- **Claim 5 — [proved] Sound.** A5-304 covers X− at both primes and X+ at 32029. A5-013 transports X−→N− to X+→N+ at 32009. No cell is missing.

- **Claim 6 — [proved] Sound.** The Unmixedness Theorem for Cohen–Macaulay graded rings gives full-dimensional associated primes for a nonzero ideal `L/K2`. Additivity of Hilbert polynomials in
  `0 → L/K2 → S/K2 → S/L → 0`
  then forces a positive multiplicity loss whenever `L/K2≠0`. Equal dimension and multiplicity therefore imply `L=K2`; the converse is immediate.

- **Claim 7 — [computed/proved] Sound.** A5-019’s 14-row replay confirms lengths `15>12` for same-sign X and `20>11` for E8-bar at both primes. A5-022 is supplied by the one-minimal-prime probe plus A5-304. A5-030 is carried by A5-015/A5-016 at both primes. A5-021 has both sides proved by A5-005/A5-010. The dated entries for A5-001, 012, 026, 031, and 033 stay within the cited rows’ scopes.

- **Claim 8 — [hypothesis] Properly open.** A5-543 states both the proposed Plücker-plane equality and a decisive comparison test. No evidence is represented as a result.

## New conjectures

- **[hypothesis] Rank-one square-zero rope principle.** For every nonreduced A5 quadratic fiber at a good odd characteristic, with `R=rad(K)` and `A=K:R`, one has `R²⊂K`, prime `A`, `K:A=R`, and `R/K` torsion-free of rank one over `S/A`, with `H_{R/K}=H_{S/A}-1`. A5-454 and A5-542 are the E8-bar and X instances.
  **Falsifier:** nonprime `A`, failed double colon, `R²⊄K`, or a broken numerator identity.
  **Cheapest test:** apply the existing colon/numerator probe to modular E8-bar→N± at 32029; no new random forms are needed.

- **[hypothesis] Reduced–Cohen–Macaulay dichotomy in the A5 quadratic family.** At every good odd prime, `S/K2` is Cohen–Macaulay exactly when `K2` is radical; the entire non-CM defect is the rope above. The first hundred rows give reduced/CM E8-bar→VB, Iso, W8 and nonreduced/non-CM same-sign X and E8-bar→N±.
  **Falsifier:** one reduced non-CM or nonreduced CM cell.
  **Cheapest test:** regenerate the existing finite list at a third fixed prime and run `radical(K2)` plus the deterministic `k2_cm.py` linear sections.

## Verification

- **[computed]** Probe replay: `16` rows, byte-identical SHA-256 `704d3212892c843d6c2bf7767b85c8a82b1faa18e4d6fb8e8790318a90017a71`.
- **[measured]** Probe replay: `22.03 s`, peak `59,836 KiB`, exit `0`.
- **[computed]** `k2_cm.py`: `14` rows, byte-identical SHA-256 `58fbdb559a15708de067ffca101e971eabb8922940ef21f4557eb690cde18c75`.
- **[measured]** CM replay: `9.36 s`, peak `21,160 KiB`, exit `0`.
- **[computed]** Focused pytest: `4 passed in 0.06s`; ledger check exited `0`.
- **[computed]** Ruff format/check and mypy: clean.
- **[computed]** `git diff --check`: clean; final tracked and staged diffs against HEAD are empty.

**Verdict — [proved]:** Claims 1–8 are mathematically sound, subject to the A5-542 citation/scope repair. Claim 9 is decisively refuted. The PR should correct the checker contract and tests before treating the JSONL as a fail-closed certificate.

