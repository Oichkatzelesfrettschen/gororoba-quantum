# A_5 exceptional-fiber ledger audit: codex-terra

**Scope and limitation.** This is an incomplete adversarial audit of the 242 ledger rows at commit `4635cc5a47de8458344196fc921a2953fe35d7ee`. The subject is commutative-algebra proofs, exact finite-field computation, retained rank certificates, and hardware-observation claims. I checked the structural ledger and registry commands and read the cited excerpts below; I did not independently replay every rank, upper bound, witness, proof, refutation, or hardware analysis. Consequently the table marks an unchecked scientific status `cannot check`, even when the checker accepts the row. A row marked `defect` has the specific defect explained below, which need not falsify the mathematical claim itself. The table is an inventory of review coverage, not 242 independent proofs. No random sample was drawn; no QRNG indices were used.

**Computed checks.** In `docs/evidence/a5-exceptional-fibers`, with `PYTHON=python3` and `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, `"$PYTHON" ledger.py --check --summary --open` exited 0 and returned 242 rows: certified 90, proved 32, survives 53, refuted 44, rejected 6, superseded 9, open 8. `"$PYTHON" build_registry.py --check d5-p2 degree-one n15-laptop n16-laptop n18-laptop d4-p2 xm-lown ../../local/a5-failed-runs iso-d6-n19-laptop vb-d6-laptop` exited 0 with `registry matches`. `sha256sum replay/engine/fiber_rank_v11.py` returned `7849cbc71ccf1787894c74182b6cd225ca8a485973f062d47f77c6b63ce12bbd`. The first attempt to invoke the ledger checker set `PYTHON` in the same shell command as expansion and exited 127; the separate assignment above succeeded. `ledger.py:74-103` validates schema, path existence and referenced IDs, rather than claims, digests or witness maps. Registry agreement means agreement with the builder's own scan, not independent replay. The 92/96 per-cell recount and registry-to-ledger semantic comparison remain unverified.

The three documents-repository `manifest.tsv` files were accessible; their contents and the referenced papers were not reviewed. The notes, evidence and logs cited below were read selectively, not exhaustively. No external web sources were consulted.

## Per-row verdicts

Each locator is `docs/evidence/a5-exceptional-fibers/ledger.tsv` at the indicated line. `cannot check` records the missing substantive verification; it is not a finding that the claim is false. The checker accepted every row's paths and schema.

| ID | Status under test | Verdict | Reason and ledger line |
|---|---|---|---|
| A5-001 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:2` |
| A5-002 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:3` |
| A5-003 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:4` |
| A5-004 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:5` |
| A5-005 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:6` |
| A5-006 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:7` |
| A5-007 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:8` |
| A5-008 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:9` |
| A5-009 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:10` |
| A5-010 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:11` |
| A5-011 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:12` |
| A5-012 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:13` |
| A5-013 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:14` |
| A5-014 | refuted | defect | Refutation explicitly depends on unestablished analytic spreads; finding 2. `ledger.tsv:15` |
| A5-015 | survives | defect | The cited degree-4 support certificate relies on unproved interpolation identification; finding 1. `ledger.tsv:16` |
| A5-016 | open | defect | A relation merely vanishing on the degree-4 component does not decide presence of the degree-3 component; finding 3. `ledger.tsv:17` |
| A5-017 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:18` |
| A5-018 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:19` |
| A5-019 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:20` |
| A5-020 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:21` |
| A5-021 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:22` |
| A5-022 | survives | defect | Claim names fiber support; basis establishes only candidate support; finding 4. `ledger.tsv:23` |
| A5-023 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:24` |
| A5-024 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:25` |
| A5-025 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:26` |
| A5-026 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:27` |
| A5-027 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:28` |
| A5-028 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:29` |
| A5-029 | open | cannot check | Deciding method, reachability and cost require substantive verification. `ledger.tsv:30` |
| A5-030 | survives | defect | Universal claim is supported only by a degree-4 component; finding 4. `ledger.tsv:31` |
| A5-031 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:32` |
| A5-032 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:33` |
| A5-033 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:34` |
| A5-034 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:35` |
| A5-035 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:36` |
| A5-036 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:37` |
| A5-037 | rejected | cannot check | Rejection argument requires substantive verification. `ledger.tsv:38` |
| A5-038 | rejected | cannot check | Rejection argument requires substantive verification. `ledger.tsv:39` |
| A5-039 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:40` |
| A5-040 | superseded | cannot check | Successor and coverage require substantive verification. `ledger.tsv:41` |
| A5-041 | refuted | defect | A stalled presentation cannot refute an unbounded cheap-verification claim; finding 5. `ledger.tsv:42` |
| A5-042 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:43` |
| A5-043 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:44` |
| A5-044 | superseded | cannot check | Successor and coverage require substantive verification. `ledger.tsv:45` |
| A5-045 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:46` |
| A5-046 | rejected | cannot check | Rejection argument requires substantive verification. `ledger.tsv:47` |
| A5-047 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:48` |
| A5-048 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:49` |
| A5-049 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:50` |
| A5-050 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:51` |
| A5-051 | rejected | cannot check | Rejection argument requires substantive verification. `ledger.tsv:52` |
| A5-052 | superseded | cannot check | Successor and coverage require substantive verification. `ledger.tsv:53` |
| A5-053 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:54` |
| A5-054 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:55` |
| A5-055 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:56` |
| A5-056 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:57` |
| A5-057 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:58` |
| A5-058 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:59` |
| A5-059 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:60` |
| A5-060 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:61` |
| A5-061 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:62` |
| A5-062 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:63` |
| A5-063 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:64` |
| A5-065 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:65` |
| A5-066 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:66` |
| A5-067 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:67` |
| A5-068 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:68` |
| A5-069 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:69` |
| A5-070 | refuted | defect | A 10 GiB address-space cap failure cannot establish failure at 11 GB; finding 5. `ledger.tsv:70` |
| A5-071 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:71` |
| A5-072 | superseded | cannot check | Successor and coverage require substantive verification. `ledger.tsv:72` |
| A5-073 | superseded | cannot check | Successor and coverage require substantive verification. `ledger.tsv:73` |
| A5-074 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:74` |
| A5-075 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:75` |
| A5-076 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:76` |
| A5-077 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:77` |
| A5-078 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:78` |
| A5-079 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:79` |
| A5-080 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:80` |
| A5-081 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:81` |
| A5-082 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:82` |
| A5-083 | open | cannot check | Deciding method, reachability and cost require substantive verification. `ledger.tsv:83` |
| A5-084 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:84` |
| A5-085 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:85` |
| A5-086 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:86` |
| A5-087 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:87` |
| A5-088 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:88` |
| A5-089 | open | cannot check | Deciding method, reachability and cost require substantive verification. `ledger.tsv:89` |
| A5-090 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:90` |
| A5-091 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:91` |
| A5-092 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:92` |
| A5-093 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:93` |
| A5-094 | superseded | cannot check | Successor and coverage require substantive verification. `ledger.tsv:94` |
| A5-095 | open | cannot check | Deciding method, reachability and cost require substantive verification. `ledger.tsv:95` |
| A5-096 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:96` |
| A5-097 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:97` |
| A5-098 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:98` |
| A5-099 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:99` |
| A5-100 | superseded | cannot check | Successor and coverage require substantive verification. `ledger.tsv:100` |
| A5-101 | open | cannot check | Deciding method, reachability and cost require substantive verification. `ledger.tsv:101` |
| A5-102 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:102` |
| A5-103 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:103` |
| A5-104 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:104` |
| A5-105 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:105` |
| A5-106 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:106` |
| A5-107 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:107` |
| A5-108 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:108` |
| A5-109 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:109` |
| A5-110 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:110` |
| A5-111 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:111` |
| A5-112 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:112` |
| A5-113 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:113` |
| A5-114 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:114` |
| A5-115 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:115` |
| A5-116 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:116` |
| A5-117 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:117` |
| A5-118 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:118` |
| A5-119 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:119` |
| A5-120 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:120` |
| A5-121 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:121` |
| A5-122 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:122` |
| A5-123 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:123` |
| A5-124 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:124` |
| A5-125 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:125` |
| A5-126 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:126` |
| A5-127 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:127` |
| A5-128 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:128` |
| A5-129 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:129` |
| A5-130 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:130` |
| A5-131 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:131` |
| A5-132 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:132` |
| A5-133 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:133` |
| A5-134 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:134` |
| A5-135 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:135` |
| A5-136 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:136` |
| A5-137 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:137` |
| A5-138 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:138` |
| A5-139 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:139` |
| A5-140 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:140` |
| A5-141 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:141` |
| A5-142 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:142` |
| A5-143 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:143` |
| A5-144 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:144` |
| A5-145 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:145` |
| A5-146 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:146` |
| A5-147 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:147` |
| A5-148 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:148` |
| A5-149 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:149` |
| A5-150 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:150` |
| A5-151 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:151` |
| A5-152 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:152` |
| A5-153 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:153` |
| A5-154 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:154` |
| A5-155 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:155` |
| A5-156 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:156` |
| A5-157 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:157` |
| A5-158 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:158` |
| A5-159 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:159` |
| A5-160 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:160` |
| A5-161 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:161` |
| A5-162 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:162` |
| A5-163 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:163` |
| A5-164 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:164` |
| A5-165 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:165` |
| A5-166 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:166` |
| A5-167 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:167` |
| A5-168 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:168` |
| A5-169 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:169` |
| A5-170 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:170` |
| A5-171 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:171` |
| A5-172 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:172` |
| A5-173 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:173` |
| A5-174 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:174` |
| A5-175 | rejected | cannot check | Rejection argument requires substantive verification. `ledger.tsv:175` |
| A5-176 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:176` |
| A5-177 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:177` |
| A5-178 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:178` |
| A5-179 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:179` |
| A5-180 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:180` |
| A5-181 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:181` |
| A5-182 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:182` |
| A5-183 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:183` |
| A5-184 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:184` |
| A5-185 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:185` |
| A5-186 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:186` |
| A5-187 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:187` |
| A5-188 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:188` |
| A5-189 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:189` |
| A5-190 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:190` |
| A5-191 | superseded | cannot check | Successor and coverage require substantive verification. `ledger.tsv:191` |
| A5-192 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:192` |
| A5-193 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:193` |
| A5-194 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:194` |
| A5-195 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:195` |
| A5-196 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:196` |
| A5-197 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:197` |
| A5-198 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:198` |
| A5-199 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:199` |
| A5-200 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:200` |
| A5-201 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:201` |
| A5-202 | open | cannot check | Deciding method, reachability and cost require substantive verification. `ledger.tsv:202` |
| A5-203 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:203` |
| A5-204 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:204` |
| A5-205 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:205` |
| A5-206 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:206` |
| A5-207 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:207` |
| A5-208 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:208` |
| A5-209 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:209` |
| A5-210 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:210` |
| A5-211 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:211` |
| A5-212 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:212` |
| A5-213 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:213` |
| A5-214 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:214` |
| A5-215 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:215` |
| A5-216 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:216` |
| A5-217 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:217` |
| A5-218 | rejected | cannot check | Rejection argument requires substantive verification. `ledger.tsv:218` |
| A5-219 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:219` |
| A5-220 | certified | cannot check | Rank, upper bound, digests and any transport require independent replay. `ledger.tsv:220` |
| A5-222 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:221` |
| A5-223 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:222` |
| A5-224 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:223` |
| A5-225 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:224` |
| A5-226 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:225` |
| A5-227 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:226` |
| A5-228 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:227` |
| A5-229 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:228` |
| A5-230 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:229` |
| A5-231 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:230` |
| A5-232 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:231` |
| A5-233 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:232` |
| A5-234 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:233` |
| A5-235 | refuted | cannot check | Counterexample and scope require substantive verification. `ledger.tsv:234` |
| A5-236 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:235` |
| A5-237 | superseded | defect | The supersedes field points to the live proof rather than the row it replaces; finding 6. `ledger.tsv:236` |
| A5-238 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:237` |
| A5-239 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:238` |
| A5-240 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:239` |
| A5-241 | survives | cannot check | Evidence scope and decisive falsifier require substantive verification. `ledger.tsv:240` |
| A5-242 | open | cannot check | Deciding method, reachability and cost require substantive verification. `ledger.tsv:241` |
| A5-243 | proved | cannot check | Proof and its field and geometric hypotheses require independent verification. `ledger.tsv:242` |
| A5-244 | survives | defect | The named cheapest next cell has already been measured; finding 6. `ledger.tsv:243` |

## Findings ranked by consequence for kernel-plane attaching data

1. **Serious, proof gap; computed and hypothesis.** The asserted E8-bar to VB degree-4 component support underlies the direction family on which kernel-plane limits would be taken. `working/build/arc/arc-report.md:7-10,28-32,43-47` states dominance and exact support for both Hensel branches, but the rational leading vector was interpolated from 48 numerical lifts and tested at eight further points; the symbolic lift did not finish. Polynomial identities and Jacobian rank of the interpolant establish facts about the interpolant. Without a proved degree bound and identification with the generic Hensel output, finite interpolation and holdouts do not establish an arc family. `ledger.tsv:16` calls the result certified and `status.md:71-72` plans kernel limits on that component. Remedy: verify the interpolant symbolically against the normalization relations and leading G coefficients over the parameter field, or prove a sufficient degree bound and use an exact interpolation certificate. The finite-field evidence may still be correct; the stated conclusion has not been established by the cited argument.

2. **Serious, conditional refutation; computed.** `ledger.tsv:15` labels the Cohen-Macaulay claim for X and E8-bar fibers `refuted` while the basis says the contradiction applies *if* analytic spreads are 4 and 5. The row itself names analytic spread as its falsifier. A conditional contradiction becomes an unconditional refutation only after those dimensions are established. Remedy: cite such proofs or downgrade to a conditional result. A wrong dimension assignment can alter which components and kernel limits the program pursues.

3. **Serious, inconclusive falsifier; proved by logic.** `ledger.tsv:17` proposes a relation of degree at least 5 vanishing on the degree-4 component as evidence against containment of the degree-3 component. A relation vanishing on both components is compatible with both being contained; the test must also show nonvanishing on the degree-3 component and prove membership in the fiber relation ideal. A dominant family into the latter gives a positive result, while a failed family does not give a negative one. `status.md:68` presents order-2 arcs as deciding the item, although an unsuccessful search is inconclusive. Remedy: add both membership and nonvanishing checks, and label an arc search as a positive-only test.

4. **Serious, scope overreach; computed.** `ledger.tsv:23` asserts the X- fiber support is an irreducible threefold while its own basis states only that V(K2) has the described support and the fiber may be a proper closed subset. `ledger.tsv:31` asserts normalized arcs certify every reduced component while the basis mentions one component; `arc-report.md:7-10` identifies another component as unreached. Replace these claims by the actual candidate-support and one-component statements, or provide dominance for the missing component. Such scope matters directly to which attaching limits remain to be computed.

5. **Moderate, resource observations promoted to refutations; measured.** `ledger.tsv:42` treats exceeding 3 GB in 14 minutes on one presentation as refuting cheap verification while acknowledging alternate presentations untested. `ledger.tsv:70` calls an 11 GB fit refuted using failures under 5 and 10 GiB `prlimit` address-space caps. `docs/runbooks/compute-flags.md:20-35` distinguishes virtual-address caps from resident memory. Neither experiment establishes the claimed failure for every presentation or at the stated 11 GB budget. Record the exact tested method, cap, time and outcome; classify broader feasibility as open.

6. **Moderate, ledger maintenance and semantics; computed.** `ledger.py:20,100-102` defines `supersedes` as IDs replaced by the current row and checks existence only. `ledger.tsv:236` instead places live proof A5-066 in the supersedes field of A5-237, reversing the intended direction. A scan of the nine superseded rows found only A5-094 and A5-100 referenced in successor `supersedes` fields; some other rows name successors in prose, and their coverage needs separate review. `ledger.tsv:243` presents X- degree 6 as the cheapest next test even though the same row and `xm-lown/README.md:40-70` report the completed test. Update the next falsifier and align edge direction with the schema.

7. **Moderate, wrong mathematical definition; proved by definition.** `docs/notes/topics/a5-exceptional-fiber-status.md:15-18` says h_d counts independent degree-d relations. The Hilbert function of F(I) counts dimensions of degree-d classes in the quotient; for a polynomial ring with s degree-one variables the relation-space dimension is binom(s+d-1,d) - h_d. The erroneous sentence reverses what a larger h_d means. Remedy: describe independent quotient classes, with relation counts as the complementary dimension.

8. **Moderate, limited field scope; computed.** `ledger.tsv:3-4,12-13,28-31` has rows labeled `any` or `all` whose bases name finite examples or tests, and `ledger.tsv:6-7` restricts prime fields to 32009 despite citing both. These are audit flags rather than a proof each result fails in other characteristics. Check hypotheses of every generic statement and align scope to proven specializations. `ledger.tsv:7` correctly names the same-sign X pairs.

## Patterns and forecasts

- **Computed from retained records, independently unreplayed:** `xm-lown/README.md:9-38,55-70` reports X- closing orders 4, 8, 11, 15, 18, 22 in degrees 1 through 6; degree 6 at both primes has r_21 = 496 and r_22 = 665 with final jump 169 split 49/42/39/39. The p=32009 plateau r_20 = r_21 is measured; p=32029 r_20 is unmeasured. `iso-d6-n19-laptop/README.md:11-29` reports Iso r_18 = 2253, r_19 = 2422 with the same jump and block split. The patterns are finite checks, not general laws. Engine v11's digest was checked, not every record's digest or every earlier engine's arithmetic.
- **Hypothesis, degree 7:** Iso and W8 close at N=22 by 3d+1; same-sign X closes at N=25 by floor(7d/2)+1. Test each predicted N and N-1 against its own K2 upper bound and block ranks; a lower rank at predicted N or equality already at N-1 falsifies the respective closing-order prediction. `forecasts/trends-2026-11-06.md:14` and `xm-lown/README.md:34-37` give the observed fitting basis. The E8-bar to VB degree-6 run at N=20 does not establish its closing N (`vb-d6-laptop/README.md:12-19`), so no degree-7 order is justified here.
- **Hypothesis, beyond the named fibers:** the square last-jump law fails outside Iso, W8 and X-. E8-bar to N- degree 5 has jump 81 rather than 121 (`ledger.tsv:243`); a generalization needs an explicit fiber-dependent formula. Cheapest next discriminating observation is an already-planned degree-6 E8 ladder adjacent to its eventual closing order, contingent on a feasible export; cost is unmeasured. Extrapolating 81 to higher degree is unsupported.
- **Hypothesis, E8-bar to VB:** the degree-3 component is present, but the order-1 arc ansatz misses it. Falsify presence with an exact fiber relation nonzero generically on the component, as in finding 3; test presence with a symbolically certified dominant higher-jet family. `arc-report.md:9-10,41,53-56` documents the limited search. A failed higher-jet search leaves the hypothesis open.
- **Hypothesis, E8-bar to N+- degree 6:** h_6 = 1666. `status.md:32,50-52` reports 1526 <= h_6 <= 1666 and a 140-dimensional quotient of radical relations modulo K2. Falsify by an exact degree-6 relation in the fiber ideal outside K2; certify equality by independent lower rank 1666 or exact nonmembership for the entire quotient. I did not independently verify either bound.
- **Hypothesis, characteristic zero:** the finite-field K2 values and selected equalities lift to Q(i) in favorable characteristics. Matching two primes alone does not establish a rational identity or exclude exceptional primes. Reconstruct candidates, verify exact characteristic-zero generators and ideal membership, then check the needed lower bound or geometric hypotheses over Q(i); `status.md:21-24,34` identifies the gap.

## Remaining open rows and resource evidence

Costs below are retained measurements or unknown, not fresh benchmarks. Host capacity is the brief's budget; a workload with unknown peak has an unverified fit. Kaggle and paid VM cases require separate approval.

| Open rows | Cheapest meaningful test and outcome | Cost, peak, host |
|---|---|---|
| A5-016 | Symbolic verification of an arc family into the degree-3 component; for a negative decision prove a fiber relation nonzero on that component. | Unknown for the decisive computation. `findings.md:520` records chart 5 at 359 s, without a matching peak for the proposed higher-jet calculation; build host or laptop fit is unverified. |
| A5-029 | Compute and specialize a basis of the kernel of left multiplication along one certified arc, take a Grassmannian/Plucker limit, check rank and generic nullity, then extend across the desired family. One successful arc does not decide all fibers. | `findings.md:524` proposes a one-arc pilot and supplies no time or peak; laptop fit unverified. |
| A5-083, A5-089, A5-095, A5-101 | Pilot membership in the 91-dimensional degree-5 radical quotient; apply a validated method to all 140 degree-6 forms at both primes, with sign transport independently checked. | Pilot cost and peak unknown; W8 degree-2 receipt 5,619 s and 6.7 GB is a different workload (`findings.md:522`). Laptop is proposed, fit unverified. Direct rank degree-5 comparison: 118,427 s, 35.4 GiB; degree-6 cost unknown (`findings.md:526`), paid VM requires approved case. |
| A5-202 | Preregister a fresh-seed increment test against the efficiency-only model and use an independent hardware acquisition. | Shots, credits, wall time and peak unknown; provider case and approval required (`ledger.tsv:202`). |
| A5-242 | Preregister a phase-qubit relocation with paired contrasts and adequate power, or an equivalent decisive design. | Shots, QPU seconds and peak unknown; IBM case and approval required (`ledger.tsv:241`). |

The retained E8-bar to VB degree-6 runs took 10,696-10,796 s and 1.65-1.71 GiB per prime (`vb-d6-laptop/README.md:12-15`); they are a reference, not a resource forecast for the higher-jet or characteristic-zero computations. The Iso degree-6 run took 1,900.6 s and 19.6 GiB (`iso-d6-n19-laptop/README.md:3-7`); degree 7 has unknown peak and requires a preflight before assigning a host. OCI A1's Singular-only surface cannot run a Sage-only arc pilot unchanged. A decisive complete cost and host assignment for each open item remains outstanding.

## Steelman and verdict

The retained workflow distinguishes exact lower and upper bounds, records plateau failures, and maintains field-specific evidence; the registry builder reproduces its stored view. The central attaching question remains open, and this review did not independently establish the certification inventory or the W8 all-degree proof. The highest-priority review action is to close or explicitly bound the E8-bar to VB arc-interpolation gap, then compute kernel-plane limits with exact checks. The remaining rows need source-by-source review before the requested full audit can be called complete.
