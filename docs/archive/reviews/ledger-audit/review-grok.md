# Ledger audit, grok

Artifact: `docs/evidence/a5-exceptional-fibers/ledger.tsv`, 242 rows, detached HEAD `4635cc5a47de8458344196fc921a2953fe35d7ee`. Field: computational commutative algebra (graded fiber rings of the 32-dimensional Cayley-Dickson algebra), plus a hardware block this audit did not replay. The status under test is the status column. A row can hold as a number and still fail as a scope.

The kernel-plane attaching datum has not been computed. The direction table it would consume is in good shape: 92 of 96 degree-1-to-6 cells are certified or proved, the four open cells are E8-bar to N± degree 6, and the one all-degree proof is W8. The defects that can aim the limit badly are unfalsifiable survives rows and an unsized limit. The Hilbert numbers that were recomputed match.

## How this was checked

No seeded sample. `docs/evidence/anu_qrng/draw-2026-11-08T170257Z.json` is schema `anu-qrng-draw-v1`, 1024 values (indices 0-1023), `raw_sha256` `6efe7098bd9bc73929af4154f2e51e3926db9eb133bfe60a0d8f209de038352a`. The assigned grok indices 1300-1399 are absent. The pass is exhaustive on the ledger columns and on the bindings below, and a sample of proofs.

Recomputed here: status counts from the TSV are 90 certified, 32 proved, 53 survives, 44 refuted, 9 superseded, 6 rejected, 8 open. Every `h_d = N` row matches `claims.json` `k2_count` at that fiber, prime and degree. `sha256sum` of `replay/engine/fiber_rank_v11.py` begins `7849cbc71ccf1787`. `k2-cm.jsonl` was read: X± length 15 > degree 12 (not CM); E8-bar to N± length 20 > degree 11 (not CM); VB length 7 = degree 7; Iso length 23 = degree 23; W8 to N- length 50 = degree 50. `w8-n16-azure/p32029/w8d5-n16-p32029.out` has `r_N` 4116, blocks 1017/1005/1047/1047, engine `7849cbc71ccf1787`, header `20d00f15fd8f35c9`, 24 generators. `structure/w8-kp/k2-p32009-section1.log` line 1 is `vdim 50`; line 2 is eliminant degree 50 with every factor multiplicity 1 (degrees 1, 1, 1, 2, 5, 15, 25). `c30-plane-p32009-pt1.result` lines 5-13: K2 nonzero 0 of 144, K2:P nonzero 0 of 131, Jacobian rank 18, sweep rank 6. `arcs/e8nm-p32009/result.json` `hilbert_function_sqrt_K2` degree 6 is 1526. Measured walls from `.time` files: E8-bar N- degree 5 N=18 at 32009, 118426.83 s, maxrss 37072856 KiB; VB degree 6 N=20 at 32009, 10795.78 s, maxrss 1794996 KiB; X- degree 6 N=22 at 32009, 1700.36 s, maxrss 5944772 KiB.

Computed earlier in this audit, not re-run in the write-up pass: `ledger.py --check` and `build_registry.py --check` both exited 0 (`registry matches`). All 14 retained `k2-hilbert` relation sha256 values matched the files on disk. Singular, stdin closed, on the VB relation files at both primes: projdim 3, degree 7, 21 quadrics, Hilbert function 10, 34, 80, 155, 266, 420 for degrees 1 through 6. `doubling_automorphism.py`: 0 failing basis pairs at dimensions 8, 16 and 32. The three W8 degree-5 outs (receipt-bound, unreceipted, p=32029) share `r_N` 4116 and engine `7849cbc71ccf1787`; the 32009 headers match `w8-nm.sing` (`585a946d2d75073e`) and the 32029 header matches `20d00f15fd8f35c9`. A k2-span witness with `ok` true links the 32009 receipt relation prefix `ad37712c91be5cb6` to the Hilbert source prefix `31feaac8cace8050`. `git merge-base --is-ancestor 860a79e59 HEAD` exited 0.

`holds` means the status survives the test that was actually run. `defect` means the row as written fails that test. `cannot check` means the cited proof, shot record or counterexample was not re-derived. A clean path check is not a proof.

## Per-row verdicts

| id | status | verdict | reason |
|---|---|---|---|
| A5-001 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-002 | survives | holds | Falsifier is a germ tuple off the table. Scope is the recorded germs; char 0 is not claimed as proved. |
| A5-003 | survives | holds | Falsifier is a second prime through 0 or a residual of another dimension. base_locus.py was not re-run; the falsifier can still fire. |
| A5-004 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-005 | survives | defect | Survives through degree 6 is supported (h_6=420, recomputed). The primes column says 32009 while the basis uses both primes. A5-016 still blocks all degrees. |
| A5-006 | survives | defect | Fibers are the corrected 15-generator pair X+->N+, X-->N-. The primes column still says 32009 while degree 6 is cited at both primes. Falsifier (degree 7 or char 0) can decide. |
| A5-007 | survives | holds | Through degree 6 the certified cells match (h_6=2422). Falsifier is degree 7 or characteristic 0. All degrees remain open, which is what survives means. |
| A5-008 | proved | holds | All-degree W8 equality is A5-066 at both primes. This session re-read one of five plane logs and the 32009 section-1 log; the other logs were not reopened. |
| A5-009 | survives | holds | Through degree 5 the cells match, degree 6 is the open bracket. Fibers column repeats E8-bar->N+ once; N- is present. Falsifier can fire at degree 6. |
| A5-010 | survives | defect | k2-cm.jsonl length equals degree (VB 7, Iso 23, W8 50) at both primes. Falsifier 'none at either prime' cannot fire. k2_cm.py lines 3-6 need a general sop for the positive direction. |
| A5-011 | survives | defect | Falsifier 'none; an argument'. Primes column any. The spread-multiplicity iff is not a check that can fail on a retained record. |
| A5-012 | proved | defect | The iff is discharged at F_32009 and F_32029 by A5-066. The primes column says any. Radicality and CM are inputs at those two primes. |
| A5-013 | proved | holds | doubling_automorphism.py, rerun this audit: 0 failing basis pairs at dim 8, 16 and 32. Left-multiplication equivariance is that automorphism. |
| A5-014 | refuted | defect | Basis is conditional: refuted if the analytic spread is 4 and 5. The falsifier is that spread, so the refutation is not discharged. DRV was not opened. k[y]/K2 not CM does not refute CM of a further quotient F(I). |
| A5-015 | survives | holds | Degree-4 component in the VB fiber. Falsifier is a second-prime arc replay, which has not been cited as run. |
| A5-016 | open | holds | Open. Falsifier names jet-parameter arcs at t1=0 or the apex, or a degree >=5 relation on the degree-4 component. The '34 arcs' tally was not re-counted. |
| A5-017 | survives | holds | Reducedness of the VB fiber. Falsifier is an embedded or nilpotent relation in a later degree. |
| A5-018 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-019 | refuted | holds | k2-cm.jsonl: X- length 15 > degree 12, E8-bar->N- length 20 > degree 11, at 32009. A sop longer than the multiplicity is not Cohen-Macaulay. |
| A5-020 | survives | defect | Falsifier 'none'. k2-cm.jsonl has the VB join fields; those component spans were not re-checked this session, and nothing is left that can falsify the row. |
| A5-021 | survives | defect | Falsifier 'none; an argument' and primes any. The iff is not tied to a record that can fail. |
| A5-022 | survives | holds | One irreducible threefold of degree 12. Falsifier is an arc certificate inside the P^11. Not re-run. |
| A5-023 | survives | defect | Basis says proven for the inputs; status is survives; falsifier none. The coefficient check was not re-run, and the row names no remaining test. |
| A5-024 | survives | holds | Sign correspondence of E8-bar N+ and N-. Falsifier is a direct comparison of the Q(i) generators. |
| A5-025 | survives | defect | Same shape as A5-023 for W8 signs: survives, falsifier none, primes any. |
| A5-026 | survives | holds | Second prime agrees on the recorded degrees. Falsifier is a third prime or a higher degree at 32029. |
| A5-027 | survives | defect | Falsifier 'none; checked' and primes any, for radicality of J through the origin. No decisive test remains on the row. |
| A5-028 | survives | defect | Falsifier 'none; checked' and primes any, for the pivot being a nonzerodivisor modulo J. |
| A5-029 | open | defect | Open is the right science, and the falsifier is only the phrase 'the limit computation'. No sized test, no retained timing. |
| A5-030 | survives | holds | Method claim. Falsifier is a component no normalized arc reaches. |
| A5-031 | survives | holds | Method claim with a named control (W8 degree 3 at N=10..14 against 600). That control was not re-run. |
| A5-032 | survives | holds | Klein four-group of sign symmetries. Falsifier is an input regeneration that breaks span invariance. |
| A5-033 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-034 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-035 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-036 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-037 | rejected | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-038 | rejected | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-039 | refuted | holds | Operational claim that pivot saturation finishes. Six stalls, up to 12 h and 72 GB, refute that claim. A stall is the failure mode the row names. |
| A5-040 | superseded | defect | Basis says superseded and names no successor id. No other row's supersedes column lists A5-040. |
| A5-041 | refuted | holds | Scoped to one presentation of a candidate ideal on E8-bar->VB: std past 3 GB in 14 minutes. The row leaves a reduced presentation untested. |
| A5-042 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-043 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-044 | superseded | defect | Basis says superseded by a global-membership timing and names no id. Nothing points at A5-044. |
| A5-045 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-046 | rejected | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-047 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-048 | refuted | holds | Operational memory claim. cgroup OOM at 77.8 GiB resident after 61304 s refutes 'fits a 78 GB scope'. |
| A5-049 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-050 | refuted | holds | Operational memory claim. Kernel OOM at the 24 GB limit after 5449 s refutes the jet-std fit. |
| A5-051 | rejected | holds | A plateau of r_N below HF(k[y]/K2,d) is still a lower bound. Rejection matches the rank definition in fiber_rank_v11.py. |
| A5-052 | superseded | defect | Basis says superseded by stage times and names no id. Nothing points at A5-052. |
| A5-053 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-054 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-055 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-056 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-057 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-058 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-059 | proved | holds | k2-cm.jsonl: Iso dim 5, degree 23, length 23, CM true at both primes (two sources at 32009). The four explicit section forms in the chart logs were not re-read. |
| A5-060 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-061 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-062 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-063 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-065 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-066 | proved | holds | Writeup plus c30-plane-p32009-pt1.result: Jacobian rank 18, sweep rank 6, K2 nonzero 0/144, K2:P nonzero 0/131. Other four plane logs not reopened. |
| A5-067 | survives | holds | Fiber-cone saturation for Iso. Falsifier is a blowup-chart saturation that finishes; the row records that the dense chart did not. |
| A5-068 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-069 | survives | holds | QRNG section method. Falsifier is a non-squarefree eliminant on many draws. Section 1 at 32009 is squarefree of degree 50; the 'many draws' test was not repeated. |
| A5-070 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-071 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-072 | superseded | defect | Timeout (SIGTERM, radical unfinished) is correctly not a refutation of radicality. The basis points at the Iso radical row in prose. The column is empty and no row lists A5-072. |
| A5-073 | superseded | defect | Status superseded, and the basis points at the component proof. The supersedes column lists A5-063, which ledger.py:20 reads as 'this row replaces A5-063'. The proved row is the successor. |
| A5-074 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-075 | proved | holds | rank/2=12. 32009**12 = 1156818639392239146657426969191384755058789006503392481, about 1.2e54. The amplitude-amplification model was not re-derived from a reference. |
| A5-076 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-077 | proved | holds | README and the p32029 out: receipt-bound and unreceipted W8 N=16 both have r_16=4116. The receipt run is the cheaper of the two measured jobs. |
| A5-078 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-079 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-080 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-081 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-082 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-083 | open | holds | Open upper bound h_6<=1666 matches claims.json. Falsifier is a lower bound to 1666 or a degree-6 form outside K2. Arc floor 1526 is HF(k[y]/sqrt(K2),6) in arcs/e8nm-p32009/result.json. |
| A5-084 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-085 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-086 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-087 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-088 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-089 | open | holds | Open upper bound h_6<=1666 matches claims.json. Falsifier is a lower bound to 1666 or a degree-6 form outside K2. Arc floor 1526 is HF(k[y]/sqrt(K2),6) in arcs/e8nm-p32009/result.json. |
| A5-090 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-091 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-092 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-093 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-094 | superseded | holds | Superseded upper/lower bracket. A5-183 lists A5-094 in supersedes and certifies h_5=952. Column direction matches ledger.py:20. |
| A5-095 | open | holds | Open upper bound h_6<=1666 matches claims.json. Falsifier is a lower bound to 1666 or a degree-6 form outside K2. Arc floor 1526 is HF(k[y]/sqrt(K2),6) in arcs/e8nm-p32009/result.json. |
| A5-096 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-097 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-098 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-099 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-100 | superseded | holds | Same at 32029: A5-220 lists A5-100 and certifies h_5=952. |
| A5-101 | open | holds | Open upper bound h_6<=1666 matches claims.json. Falsifier is a lower bound to 1666 or a degree-6 form outside K2. Arc floor 1526 is HF(k[y]/sqrt(K2),6) in arcs/e8nm-p32009/result.json. |
| A5-102 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-103 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-104 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-105 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-106 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-107 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-108 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-109 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-110 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-111 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-112 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-113 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-114 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-115 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-116 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-117 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-118 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-119 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-120 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-121 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-122 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-123 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-124 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-125 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-126 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-127 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-128 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-129 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-130 | certified | holds | h_5=4116. sign transport of the N- run: w8-n16-azure outs have r_16=4116, blocks 1017/1005/1047/1047, engine 7849cbc71ccf1787. claims.json leaves the cell open. |
| A5-131 | proved | holds | h_6=8624 by A5-066, not by a rank. claims.json stays open because it is a rank registry. HF matches k2-hilbert. |
| A5-132 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-133 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-134 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-135 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-136 | certified | holds | h_5=4116. sign transport of the 32029 N- run: w8-n16-azure outs have r_16=4116, blocks 1017/1005/1047/1047, engine 7849cbc71ccf1787. claims.json leaves the cell open. |
| A5-137 | proved | holds | h_6=8624 by A5-066, not by a rank. claims.json stays open because it is a rank registry. HF matches k2-hilbert. |
| A5-138 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-139 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-140 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-141 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-142 | certified | holds | h_5=4116. direct N- run: w8-n16-azure outs have r_16=4116, blocks 1017/1005/1047/1047, engine 7849cbc71ccf1787. claims.json leaves the cell open. |
| A5-143 | proved | holds | h_6=8624 by A5-066, not by a rank. claims.json stays open because it is a rank registry. HF matches k2-hilbert. |
| A5-144 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-145 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-146 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-147 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-148 | certified | holds | h_5=4116. direct N- run at 32029: w8-n16-azure outs have r_16=4116, blocks 1017/1005/1047/1047, engine 7849cbc71ccf1787. claims.json leaves the cell open. |
| A5-149 | proved | holds | h_6=8624 by A5-066, not by a rank. claims.json stays open because it is a rank registry. HF matches k2-hilbert. |
| A5-150 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-151 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-152 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-153 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-154 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-155 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-156 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-157 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-158 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-159 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-160 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-161 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-162 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-163 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-164 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-165 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-166 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-167 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-168 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-169 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-170 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-171 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-172 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-173 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-174 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-175 | rejected | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-176 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-177 | certified | cannot check | Census identity for L_(e_i+t e_j); the count was not re-derived from cd_core. |
| A5-178 | certified | cannot check | 4x4 coset-class census; the 5-of-12 count was not re-derived. |
| A5-179 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-180 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-181 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-182 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-183 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-184 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-185 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-186 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-187 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-188 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-189 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-190 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-191 | superseded | defect | Basis describes the anchor comparison and names no successor id. Nothing points at A5-191. |
| A5-192 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-193 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-194 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-195 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-196 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-197 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-198 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-199 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-200 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-201 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-202 | open | holds | Open. Falsifier is a preregistered fresh-seed shifter-map test at alpha 0.005. It needs an approved hardware case. |
| A5-203 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-204 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-205 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-206 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-207 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-208 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-209 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-210 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-211 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-212 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-213 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-214 | survives | holds | t-space slice method at 32009. Falsifier is an on reading at k=3 or off at k=2 with a second form set. |
| A5-215 | survives | holds | Off at k=5 on Iso. Falsifier is an on reading with another form set or at 32029. |
| A5-216 | survives | holds | On at k=3. Falsifier is an off reading with a second form set. Arcs of A5-067 are cited for dim E0 >= 3. |
| A5-217 | survives | holds | k=4 on Iso at both primes. Falsifier is an off reading with the independent form family. |
| A5-218 | rejected | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-219 | survives | holds | Singular values along the measured W8 line. Falsifier is a symbolic evaluation in another monomial order. |
| A5-220 | certified | holds | h_d equals the claims.json k2_count for this fiber, prime and degree, and that cell is certified there. Certificate is the registry rescan, not a fresh Singular replay of this file. |
| A5-222 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-223 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-224 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-225 | survives | holds | Mixed basis-pair nullities at 32009. Falsifier is a point off those pairs. Not re-enumerated. |
| A5-226 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-227 | survives | holds | Sum relation for two generic points of V(J) on W8. Falsifier is a pair with n_32 off 8. |
| A5-228 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-229 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-230 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-231 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-232 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-233 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-234 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-235 | refuted | cannot check | The cited counterexample or closed job was not re-derived. A path check is not a refutation check. |
| A5-236 | survives | holds | Fiber-cone chart used by A5-066. Falsifier is a control the other way or a plane where the checks pass and K2 does not vanish. One plane log was re-read. |
| A5-237 | superseded | defect | The N=19 probe did not produce a rank (no standard basis in 900 s, exit 124). Supersession by A5-066 is right in the basis. The column lists A5-066, so the checker reads the failed row as replacing the proof. |
| A5-238 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-239 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-240 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-241 | survives | cannot check | Hardware or shot comparison was not replayed. The falsifier text is numeric; the record was not. |
| A5-242 | open | holds | Open. Falsifier is a full-map rerun that moves the orientation phase or flips the paired character gaps. Approved hardware case. |
| A5-243 | proved | cannot check | Cited proof or shot record was not re-read. ledger.py only checks that the evidence path exists. |
| A5-244 | survives | holds | Last jump (2d+1)^2 on Iso, W8->N- and X- through the measured range, including X- d=6 (r_21=496 to r_22=665). The falsifier's 'cheapest next cell' is still that finished X- d=6 run. |

Verdict counts: holds 136, defect 20, cannot check 86, of 242.

## Ranked findings

Ranked by what they do to the kernel-plane limits of `dimension32-global-topology` (status page, "The goal", lines 8-24). Layer 4 consumes directions of approach. A wrong Hilbert number would aim those limits along the wrong arcs. A missing falsifier wastes the next run. A column that points backward wastes a reader.

### 1. Serious. The attaching datum has no test

A5-029 (`ledger.tsv:30`) is the layer the goal consumes: kernel-plane limits along the arcs, generic nullity 8. Status open is right. The falsifier is the four words "the limit computation". That cannot fire, and it cannot be scheduled. The status page's own next-step table (lines 63-72) is more precise than the ledger: limits along the certified arc families, on the laptop, and the page says this can start before layers 2 and 3. No retained timing exists for that limit. Cost: not measured. Memory: not measured. Host: the page assigns the laptop; this audit did not size the job.

A5-036 says one limiting kernel per boundary point is already refuted, path-dependent, on the nullity-8 record's instances. That row is `cannot check`: the instances were not re-read. If it holds, the limit is a path invariant, not a point invariant, and a computation that returns one plane per boundary point is aimed at a dead claim. Reading `hardware-orbits` is not a substitute. The arc families are.

### 2. Serious. The direction set is unfinished in two places that change which arcs exist

Computed from the TSV. Sixteen fibers-and-primes, degrees 1 through 6: 92 cells certified or proved, 4 open, 0 missing, 0 in any other status. The four opens are A5-083, A5-089, A5-095, A5-101 (E8-bar to N+ and N-, both primes, degree 6). One of the five all-degree claims is proved (A5-008, by A5-066). A5-005, A5-006, A5-007 and A5-009 survive. No row proves F(I) = k[y]/K2 over Q(i), and A5-029 is the only kernel-plane row. The status-page counts hold.

E8-bar degree 6 is a bracket, not a value. `arcs/e8nm-p32009/result.json` gives HF(k[y]/sqrt(K2), 6) = 1526. `claims.json` gives HF(k[y]/K2, 6) = 1666. Gap 140. The page (lines 50-52) says a plane family only reproduces 1526 because K2 is not radical, and that h_6 is membership of those 140 forms, piloted on the 91 forms of degree 5. That route was not run here. A full truncated rank at degree 6 is the expensive alternative: the degree-5 N=18 job at 32009 already took 118426.83 s and 37072856 KiB (`n18-laptop/e8nm_d5_n18_p32009.time`), about 35.4 GiB of the laptop's 52.5 GB. A degree-6 rank is larger than that. Not measured. The membership pilot is the page's cheaper test; its wall time is not measured. Host for a rank that needs more than about 35 GiB: an approved paid VM. The laptop still fits a job of the degree-5 size, with little margin.

VB's all-degree claim (A5-005) is blocked by A5-016, the degree-3 component, not by h_6. This audit recomputed h_1 through h_6 at both primes as 10, 34, 80, 155, 266, 420 (Singular, projdim 3, degree 7, 21 quadrics). The page says 34 order-1 arcs on chart t7 land in the degree-4 component and none in the degree-3 component. That tally was not re-extracted from `working/build/arc/`. The falsifier of A5-016 is still a real computation: jet-parameter arcs at the plane t1 = 0 or the apex. The page assigns it to the build host, Sage, minutes per chart. That timing was not re-measured. Until it runs, a kernel limit along "the VB fiber" does not know whether the degree-3 component is a direction.

### 3. Serious. A5-014 records a conditional as a refutation

`ledger.tsv:15`. Claim: F(I) is Cohen-Macaulay for the opposite-sign X pair and for E8-bar to N±. Basis: "refuted if the analytic spread is 4 and 5 (negative D'Cruz-Raghavan-Verma numerators in certified degrees)." Falsifier: "the analytic spread". The status is refuted. The hypothesis of the refutation is the falsifier, so the row has not closed.

Separately, and unconditionally, k[y]/K2 is not Cohen-Macaulay for those fibers: length 15 against degree 12 for X, length 20 against degree 11 for E8-bar to N, at both primes (`k2-cm.jsonl`). `k2_cm.py` lines 3-6 state the easy direction: a system of parameters longer than the degree proves the quotient is not Cohen-Macaulay. That is A5-019's claim for X- and E8-bar to N- at 32009, and the same file extends it to both signs and both primes. It does not refute Cohen-Macaulayness of a further quotient F(I). Nilpotents or extra relations can repair depth. The DRV article body was not opened, so the numerators themselves are `cannot check`.

Consequence: medium. The status page already refuses an all-degree route for X+ because K2 is not Cohen-Macaulay (A5-019), which is the statement the file supports. Treating A5-014 as "F(I) is not Cohen-Macaulay" would be a stronger claim than either row.

### 4. Sloppy. Eight survives rows have a falsifier that cannot fire, and several primes columns say `any`

The survives test in the brief requires a decisive falsifier that has not fired. These rows say none:

| id | line | primes | what the file actually shows |
|---|---|---|---|
| A5-010 | 11 | both | length = degree for VB, Iso, W8 at both primes |
| A5-011 | 12 | any | an iff from CM plus geometric primeness |
| A5-020 | 21 | both | VB join, recorded in `k2-cm.jsonl`, spans not re-checked |
| A5-021 | 22 | any | an iff for the VB fiber |
| A5-023 | 24 | any | basis says the coefficient check is proven for the inputs |
| A5-025 | 26 | any | same, for W8 signs |
| A5-027 | 28 | any | "J is radical and prime through the origin", checked, no test left |
| A5-028 | 29 | any | pivot is a nonzerodivisor modulo J, same shape |

A5-010 is the one that matters for the W8 proof. The numbers support Cohen-Macaulayness at F_32009 and F_32029. The positive direction in `k2_cm.py` lines 3-6 needs the linear forms to be a system of parameters. The script uses one Vandermonde section, not a QRNG draw, and treats it as general. A second section with length above the degree would still falsify. "None at either prime" deletes that test. The honest status at the two primes is proved once the section is shown to be a sop, and survives until then. `any` is not the scope. A5-012 has the same scope bug in the other direction: status proved, primes `any`, while A5-066 discharges the criterion at two primes and uses radicality and CM as inputs.

A5-005 and A5-006 are different. Their falsifiers can fire (degree 7, characteristic 0, or the VB degree-3 component). The defect is the primes column. A5-006's fibers are the corrected 15-generator pair (`ledger.tsv:7`: X+ to N+, X- to N-; h_4 = 240, h_5 = 417, h_6 = 665). The primes column still says 32009 while the basis cites degree 6 at both primes. A5-005's column says 32009 and the basis says both primes. A5-009's fibers column lists E8-bar to N+ twice and does list N-; that duplicate is cosmetic and the verdict stays holds.

### 5. Sloppy. The supersedes column points backward on two rows and is empty on five

`ledger.py:20` defines `supersedes` as "ids this row replaces". The checker (lines 100-102) only rejects an unknown id. It accepts a backward pointer.

Correct: A5-183 (certified) lists A5-094; A5-220 lists A5-100. Both successors certify h_5 = 952.

Backward: A5-073 (`ledger.tsv:73`, superseded) lists A5-063 (proved). A5-237 (`ledger.tsv:236`, superseded) lists A5-066 (proved). The basis prose has the successor right. The column tells the checker that the old row replaces the proof.

Empty, and not named by any other row: A5-040, A5-044, A5-052, A5-072, A5-191. A5-072 is a timeout (SIGTERM, radical unfinished), correctly not used as a refutation; the basis points at the Iso radical row in words. A5-237 is a failed W8 degree-6 probe (no standard basis in 900 s, exit 124), correctly not used as a rank. h_6 stays the A5-066 value. A rank below 8624 would not falsify it. These are bookkeeping defects. They do not move a kernel plane.

The operational refutations that look like crashes are real refutations of operational claims. A5-039 (pivot saturation does not finish), A5-048 (78 GB scope, OOM at 77.8 GiB), A5-050 (24 GB scope, OOM) name the resource limit as the claim. A stall there is the result.

### 6. Sloppy. claims.json does not bind four W8 degree-5 certificates whose records check out

A5-130, A5-136, A5-142, A5-148 say h_5 = 4116. `claims.json` leaves W8 degree 5 and 6 open, with k2_count 4116 and 8624. Degree 6 is intentional: the proof is A5-066, and the registry is a rank registry. Degree 5 is a hole in the scanner.

`build_registry.py:199` ingests only `.json` and `.jsonl`. The W8 degree-5 records are `.out` files under `w8-n16-azure/`, which is not in the scan-root list (`README.md:39`). The p=32029 out, read this session, has r_N 4116, block ranks 1017, 1005, 1047, 1047, engine `7849cbc71ccf1787`, header `20d00f15fd8f35c9`, 24 generators. The 32009 receipt and the unreceipted run match the same rank and the same engine; their header is `585a946d2d75073e`, the canonical `w8-nm.sing`. Standard counts through degree 5 equal the Hilbert function. N+ is transport of those N- runs. The sign witness has no zero sign. The K2-span check did not run for W8: both primes have null K2 files in the witness rows. The generator map is checked; the ideal-span check is not. That is a limit on the transport, not a mismatch in the N- ranks.

`README.md:45` says the scan roots do not include `n16-laptop/`. `README.md:39` lists `n16-laptop` in the scan roots. The degree-5 record in that directory is a lower bound (r_16 = 742 against 952), so it cannot certify the cell even if it is scanned. The sentence on line 45 is stale relative to line 39. It does not change h_5.

### 7. Sloppy. A5-244 still sends the next run at a finished cell

The last-jump claim holds on the cells the basis reports, including the out-of-sample X- degree 6: r_21 = 496 to r_22 = 665, jump 169 = 49/42/39/39, closing N = 22. The falsifier's cheapest next cell is still "X- degree 6 at 32009", and it quotes 1 to 2 h and 10 to 21 GB. The retained timing for that cell is 1700.36 s and 5944772 KiB (`xm-lown/xmnm_d6_n22_p32009.time`), about 28 minutes and 5.7 GiB. The law's next falsifier is a new degree or a new fiber, not that rerun.

### 8. Sound. The load-bearing algebra that was re-checked holds

- Engine v11 digest matches the brief: `7849cbc71ccf1787`.
- VB Hilbert function, both primes, recomputed: 10, 34, 80, 155, 266, 420.
- W8 Cohen-Macaulay numbers: length 50 = degree 50, dimension 6, both primes.
- Section 1 at 32009: vdim 50, eliminant degree 50, all factor multiplicities 1. One of eight sections. Squarefree here means no repeated factor. A degree-25 factor of multiplicity 1 is still one orbit, which is why geometric irreducibility of C30 at 32009 needs section 2 (`A5-062`). That log was not reopened. Verdict on A5-061 and A5-062 stays `cannot check`.
- One C30 plane, `c30-plane-p32009-pt1.result`: the plane lies in V(K2) and in V(K2:P), off V(P), Jacobian rank 18, sweep rank 6. Four other `.result` files exist and were not opened. A5-066 and A5-008 hold on the writeup plus this one plane. The residual risk is those unread logs, not a contradiction in the log that was read.
- Sign automorphism: 0 failing basis pairs at dimensions 8, 16 and 32. A5-013's equivariance L_{φ(a)} = φ L_a φ^{-1} is that automorphism applied to left multiplication. The script checks the multiplication identity on basis pairs.
- A5-075's exponent is rank/2 = 12, and 32009^12 is 1.157×10^54, which the row rounds to about 1.2×10^54.
- A5-051's rejection is the rank contract: r_N is a lower bound, and only equality with HF(k[y]/K2, d) certifies.
- The status-page pin `860a79e59` is an ancestor of HEAD. The page's wording is "at commit 860a79e59 plus this change".

## Patterns

Marked proved, computed, measured or hypothesis.

Stated, and checked on the records this audit opened.

- Per-degree equality when a truncated rank meets HF(k[y]/K2, d). Computed: the 92 closed cells match `claims.json`. VB's six degrees were recomputed in Singular. W8 degree 5 was read off the `.out` files. W8 degree 6 is proved by A5-066, not measured by a rank.
- Closing N = 3d+1 for Iso through degree 6 and for W8 through degree 5, as A5-244 states. Iso degree 6 in the ledger basis: r_18 = 2253, r_19 = 2422. Those two JSON files were not reopened in the write-up pass. Hypothesis beyond the measured range.
- Closing N = floor(7d/2)+1 for X- through degree 6. Degree 6 is in the A5-244 basis (N = 22) and in the `.time` file named above. Degrees 1 through 5 were not re-extracted from each JSON this pass.
- Last jump (2d+1)^2 with the recorded block split, on Iso, W8 to N- and X-, including X- degree 6 and Iso degree 6. Computed from the basis text. The basis also says the split is not the parity count of k[x,y]/(x^{2d+1}, y^{2d+1}). The law is a predictor. No ring is identified. Hypothesis as algebra, computed as a fit.
- Sign transport of certified degrees. Computed on the witness rows read earlier in this audit (`ok` true, no zero signs). K2-span files are null for W8 at both primes and for X at 32009, so that half of the witness did not run.
- E8-bar degree-6 bracket 1526 ≤ h_6 ≤ 1666. Computed from the arc file and `claims.json`.
- W8 CM at both primes, length equal to degree. Computed from `k2-cm.jsonl`.

Shown by the rows, and not stated as a law.

- E8-bar closes later than 3d+1. A5-009's basis: degree 4 meets at N = 15 (and r_16), degree 5 meets at N = 18 (A5-183, A5-220). The N=18 JSON files store r_18 = 952 and do not store r_17, so the jump size is not in the closing record. Hypothesis: the Iso/W8 closing law does not govern E8-bar. Falsifier: the rung below the close.
- W8 degree 6 has no successful rank. The N=19 probe exited 1. A5-066 makes h_6 independent of that test. Computed from the superseded row, not a new computation.
- `claims.json` omits four W8 degree-5 cells whose `.out` records meet the certificate checks. Computed. Bookkeeping.

Stated more strongly than the evidence.

- A5-010, A5-011, A5-012, A5-020, A5-021, A5-023, A5-025, A5-027, A5-028: scope `any`, or a falsifier of none, against two-prime or input-only checks. Computed from the columns and from `k2-cm.jsonl`.
- A5-005 and A5-006: primes column 32009 against a both-primes basis. Computed from `ledger.tsv:6` and `:7`.
- A5-014: unconditional status, conditional basis.
- A5-004: "F(I) = k[y] exactly when the analytic spread equals s", primes any, evidence the findings note, falsifier "none; a theorem". Northcott-Rees 1954 was not opened. The dimension of the special fiber equals the analytic spread. Equality of the fiber ring with a polynomial ring also needs the relation ideal to be zero, which fails if a nilpotent keeps the dimension. Verdict `cannot check`. Consequence low: the row is not an input to A5-029.
- A5-073 and A5-237: column direction.

## Conjectures

Nothing below is a ledger row. Each has a falsifier and a cheapest test.

Degree 7 closing orders. Hypothesis. Iso and W8, if the measured law continues, close at N = 3·7+1 = 22. X- , if floor(7d/2)+1 continues, closes at N = 25. E8-bar, if it keeps closing later than 3d+1, is still open at N = 22. Falsifier: the truncated rank at that N and at one N below, against HF(k[y]/K2, 7). Cheapest measured neighbor is X- degree 6 at N = 22: 1700 s and 5.7 GiB. Degree 7 is larger. The degree-7 wall is not measured. Do not schedule it by multiplying 1700 s by a constant. Host: laptop for an X- or VB-sized job; a W8 or Iso degree-7 rank is in the class of the W8 degree-5 Azure runs (receipt peak 24.9 GiB, unreceipted peak 45.7 GiB, from `w8-n16-azure/README.md`, read earlier in this audit) and needs an approved VM if it exceeds the laptop.

Last-jump law past Iso, W8 and X-. Hypothesis, and already false as a universal law if E8-bar's closing N is the evidence above. The jump size for E8-bar is the missing datum. Falsifier: block ranks of the last step of an E8-bar ladder. Cheapest test: recover r_17 from a retained intermediate if one exists; the closing JSON does not have it. A fresh N=17 degree-5 rank is not cheaper in kind than the N=18 job (118427 s, 35.4 GiB). Not measured as its own run.

VB degree-3 component, A5-016. Hypothesis, favored by the Hilbert data and not shown. Falsifier is already on the row. Cheapest test is the page's order-2 jet arcs, build host, minutes per chart. That minute-scale figure is the page's, not a clock this audit ran. A kernel limit that includes the degree-3 component before those arcs return is guessing.

E8-bar degree 6, 1526 ≤ h_6 ≤ 1666. Hypothesis that equality holds at 1666, or at 1526, is not licensed. The bracket is computed. Falsifier: one of the 140 forms of sqrt(K2)_6 / K2_6 lies outside the fiber, or a lower bound reaches 1666. Cheapest test the page names: membership of the 91 degree-5 forms, where the value is already known, then the 140. Wall time not measured. Host: laptop, as the page assigns, unless the linear algebra exceeds the degree-5 memory. A full N-large rank is the expensive falsifier and should not be the first one. The page's claim that Singular export is 97 to 99 percent of E8, X- and VB wall time was not re-measured.

Characteristic 0. Hypothesis: the two-prime certificates specialize to Q(i). Nothing in the ledger proves a fiber equality there. A5-013 is characteristic-free and is only the sign automorphism. Falsifier: rational reconstruction of the degree-2 ideal from both primes produces a relation that fails exact membership over Q(i), or a reconstructed relation the mod-p fibers do not see. Cheapest test: the page's degree-2 pilot, laptop. Cost not measured. A characteristic-0 kernel plane before that pilot is a specialization assumption.

## Remaining work

| item | computation | cost and memory | evidence for the estimate | host |
|---|---|---|---|---|
| A5-029 | kernel-plane limit along one certified arc family | not measured | no retained timing; families already exist | laptop, as the status page assigns |
| A5-016 | order-2 jets at t1 = 0 and the apex | page says minutes per chart; not re-measured | status page line 68 | build host, Sage |
| A5-083, 089, 095, 101 | membership of 91 degree-5 forms, then 140 degree-6 forms | not measured | bracket 1526..1666 is measured; a degree-5 rank at N=18 is 93763.47 s at 32029 and 118426.83 s at 32009, both about 35.4 GiB, which is a different computation | laptop if the membership stays under that memory; paid VM, by approved case, for a full degree-6 rank |
| A5-007 degree 7 | Iso plane family, or a degree-7 rank | degree-6 N=19 at 32009 was 1900.64 s, maxrss 20525380 KiB, earlier in this audit | `iso-d6-n19-laptop/isonm_d6_n19_p32009.time`, not reopened this pass | plane family: OCI A1 or laptop, as the page says; a larger rank needs a look at memory first |
| A5-006 degree 7 | X- truncated rank near N = 25 | not measured; degree 6 N=22 was 1700 s and 5.7 GiB | `xmnm_d6_n22_p32009.time` | laptop |
| A5-005 | waits on A5-016 | see A5-016 | h_6 = 420 already recomputed | build host for the arcs |
| characteristic 0 | degree-2 reconstruction and exact membership | not measured | every current certificate is mod 32009 or 32029 | laptop |
| A5-202, A5-242 | the preregistered hardware falsifiers | credits not estimated | the falsifiers name the statistic and the sign | approved case; not a laptop algebra job |
| W8 degree-5 registry hole | teach the scanner to read `w8-n16-azure/*.out`, or store a `.json` copy | minutes, negligible RAM | the outs already match HF | laptop, local |
| A5-244 falsifier | point the next cell at a degree or fiber that has not been measured | none | the X- degree-6 cell is done | no host |

The build host (12 threads, 38.6 GiB, interactive) is the wrong place for an E8 degree-5-sized rank. OCI A1 (2 cores, 9.5 GiB, Singular only) fits the page's Iso plane-family assignment and does not fit the 19.6 GiB Iso degree-6 rank or the 35 GiB E8 rank. Kaggle is an approved-case host; nothing opened here is a 14-qubit simulation that defaults to it.

## What was not opened

Outside the worktree, unread on purpose: `AGENTS.md at the workspace root`, and the three documents repositories `gororoba-documents-public`, `-private`, `-technical`, including each `manifest.tsv`.

Prior art from the web, carried from the earlier pass of this audit: the HTML of arXiv 1907.00951 (the colength criterion used to read `k2_cm.py`). Not opened: Northcott-Rees 1954; the D'Cruz-Raghavan-Verma article; the body of Proc. AMS 2015, DOI 10.1090/S0002-9939-2015-12612-3 (an abstract was the part seen). Partial notes (Hamburg multiplicity notes, Bruns's Osnabrück notes, a JKV Theorem 2.10) are not substitutes for those papers.

Inside the worktree, not read or not finished: `docs/notes/topics/a5-exceptional-fiber-findings.md` as a full pass; `docs/archive/reviews/findings-deep/`; `docs/archive/reviews/cd-tower/report.md`; `forecasts/trends-2026-11-06.md`; the 2026-11-08 c30 review files; W8 section 2 and the squarefree check past section 1; the other four C30 plane `.result` files; engine prefixes `130f35904d21f5b4` and `a197799d97287b78` (absent from `replay/engine/`, not searched under failed runs, not called defects); the t7 arc logs for a 34-count; `hardware-orbits/result.json` and the other shot records behind the `cannot check` rows. `unbound.jsonl` records older missing engine bytes. Those lines are not the W8 degree-5 certificates.

## Steelman

The ledger is a status machine with teeth. Certified means a truncated rank met a quadric Hilbert number, the registry rescan agrees, and the relation hashes match the files. Proved, for W8, means a geometric argument with a log that names Jacobian ranks and vanishing counts, not a longer ladder. Refuted operational rows mean the job hit the limit the claim was about. The program knows that 92 of 96 cells are done, that E8-bar degree 6 is a gap of 140 forms, that VB's remaining question is one component, and that the kernel plane has not been computed. That is a better account than a single percentage.

## Verdict

The direction table is sound on the cells this audit recomputed or matched to `claims.json`. The goal's computation has not started, and A5-029 does not yet name it. Fix the falsifiers that cannot fire, the two backward `supersedes` pointers, and the W8 degree-5 scanner hole before treating the ledger as the schedule. Do not rerun X- degree 6. Do not read an OOM of a memory claim as a theorem, and do not read A5-014 as one either. Characteristic 0 and the degree-7 closing orders are hypotheses. The cheapest computation that changes the attaching datum is the kernel-plane limit along one certified arc, and its cost is still unmeasured.
