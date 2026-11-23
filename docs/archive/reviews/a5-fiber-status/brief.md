# Brief: A_5 exceptional-fiber program, state audit and fastest route to completion

Read first: the workspace AGENTS.md (workspace rules), then gororoba-quantum/AGENTS.md.
You are a read-only reviewer. Change no file, create no file, run no git write, no network job, no provider job.
Run no computation above 60 seconds or 2 GB (no Singular, no Sage, no test suite); reading files, grep and small
Python one-liners on the ledger are fine. Print the report as your final answer.

## Subject

A_5 is the 32-dimensional Cayley-Dickson algebra. The program determines how the zero-divisor strata (by nullity of
left multiplication) are glued: the open registry claim `dimension32-global-topology`. Four layers:
1 per-degree Hilbert function h_d of each fiber cone F(I); 2 all-degree F(I) = k[y]/K2; 3 characteristic 0 (Q(i));
4 the attaching datum (limits of kernel 8-planes, real arcs, two-sided real certificate).

Sources (paths relative to gororoba-quantum unless noted):
- docs/evidence/a5-exceptional-fibers/ledger.tsv: 570 claim rows A5-001..A5-592 (id, kind, fibers, primes, claim,
  status, basis, evidence, falsifier). Status counts today: structure 181 proved / 52 survives / 24 refuted / 8 open;
  equation 104 certified / 22 proved / 2 open; method 48 survives / 4 open; operational 9 stalled.
- docs/notes/topics/a5-exceptional-fiber-status.md (dated 2026-11-11, 313 rows then: likely stale),
  a5-exceptional-fiber-findings.md (Roadmap section), a5-char0-and-kernel-limits.md, a5-terms-for-outside-readers.md.
- docs/evidence/a5-exceptional-fibers/README.md and docs/evidence/a5-kernel-attachments/README.md.
- Newest results: docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v3-open-cells/README.md
  (A5-587 to A5-592): direct modular Rees fibers of E8-bar on the weight slice at all eight (sign, prime, root) cells,
  148 quadrics, dimension 5, multiplicity 11, L = K; modulo-colon method 2.4x faster than quotient; the conjugation
  map Phi (i -> -i, s4 -> -s5, s5 -> s4, s7 <-> s8) carrying N- data to N+; closed forms
  detB = -1024 (s2^2-1)^2 (s2 -+ i)^2 and unit polynomials (s2^2-1)^3 (s2 -+ r)^3 (exponent 4 on two generators).
- Proofs: gororoba-math (lean/GororobaMath/CayleyDickson/*.lean, rocq/quantum/*.v,
  rocq/open/theories/*.v). A5-specific Rocq today: A5W8ArcMatrixRanks.v, MatrixLeftInverseCertificate.v,
  MatrixSplittingCertificate.v, GaussianIntegerHom.v, the CdTower* family.

## The orchestrator's current reading (attack it)

C1. Layers 1 and 2 are complete at the primes 32009 and 32029 for every fiber class (VB, X same and opposite sign,
    Iso, W8, E8-bar -> N+-), and layer 3 holds over Q(i) on the weight slice for the ten incidences into N+-
    (A5-446, A5-448, A5-457, A5-474, A5-475, A5-270, A5-305).
C2. The remaining mathematics is: (a) A5-583, a linear change of the 21 generators identifying weight-slice K with
    header-slice K2 (two slices of one germ); (b) A5-571 and A5-577, receipts at the second root and missing record
    cells; (c) E8-bar -> VB in characteristic 0 and its degree-3 component (A5-016 lineage); (d) layer 4: A5-250,
    the real two-sided certificate, A5-389 nullity-4 kernel bundle classification, A5-254, A5-278, A5-458;
    (e) the 52 structure rows and 48 method rows with status survives, which are neither proved nor refuted.
C3. No machine-checked proof covers any fiber-cone statement; the Lean and Rocq trees cover the algebra (signs,
    nullity doubling, two-term nullity, G2 derivations) and matrix-rank certificates.
C4. Compute available: an Arm host with 4 cores (the E8-bar Rees runs took 6 to 7 h per cell there, one core each),
    a 16-core workstation, Kaggle CPU kernels under 12 h, and a cloud project whose launches need owner approval
    (account details stay in the private infrastructure repository).

## Deliver

1. Best results: the ten strongest results of the program, each with ledger ids, evidence class (proved in char 0,
   certified modular, survives) and why it ranks.
2. Completion matrix: one row per incidence or stratum pair, columns layer 1, 2, 3, 4 and machine-checked; each cell
   done / partial / open with the ledger id that decides it. Correct C1 and C2 where the ledger disagrees; name every
   stale statement in the status note.
3. Distance: what "A_5 fully solved" requires as a finite list of theorems, and which are missing. State the
   dependency order (a DAG in text).
4. Coefficient decomposition: analyze the retained numbers for structure not yet recorded. Candidates: the Hilbert
   numerators (for example Iso: 1, 0, -68, 452, -1485, 2948, -3630, 2376, 231, -2200, 2376, -1420, 517, -108, 10),
   multiplicities 7, 11, 12, 20+30, 23, the generator counts 3, 15, 17, 21, 24, the relation counts 68, 69, 144, 148,
   last-jump laws (2d+1), (2d+1)^2, closing orders floor(7d/2)+1 and 3d+1, detB = -1024 (s2^2-1)^2 (s2 -+ i)^2, the
   block splits. For each proposed structure give the derivation, a falsifier and the cheapest test. Mark every
   numerological coincidence as such; a pattern without a mechanism is a hypothesis.
5. Novel routes: at most eight concrete ideas that shorten the remaining path (for A5-583 for example: compare the
   two K by their GL_21 invariants, or construct the map from the slice change of coordinates directly). Each with
   mechanism, prediction, falsifier, cost estimate and host.
6. Proof targets: which statements belong in Rocq and which in Lean (gororoba-math), in build order, with the trusted
   base of each (for example an F_p rank checker for the degree-2 relation spaces; a verified Groebner or ideal
   membership certificate checker; the conjugation map Phi as a ring-automorphism lemma).
7. Compute plan: assign each remaining computation to a host from C4 with wall-time estimate from retained timings.
8. Red-team: the weakest links in the claims marked proved or certified (hidden premises, single-tool dependence on
   Singular 4.4.1, slice dependence, modular-to-char-0 transfer, "L = K given K inside L" conditions). Rank by risk.

Every claim cites a ledger id or a file path with line. Mark each finding confirmed (you read the source), likely,
or unproven. Length: at most 2,500 words.
