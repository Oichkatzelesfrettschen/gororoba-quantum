# A5 rank witnesses and photonic experiment candidates

This note connects retained Ascella and Belenos records, four exact Cayley–Dickson A5 examples, and the dimension-six manuscript collection. The calculations characterize encoded operators and observed device response. They do not establish that a quantum processor implements a nonassociative algebra, or that a finite hardware run proves a universal theorem. New jobs require their own current provider, cost and execution case.

## Existing photonic evidence

- The [21-pair Ascella character atlas](../../../results/quandela/runs/2026-10-29T221537Z-qpu_ascella-ascella_associator_character-job-01/analysis_report.json) returns 840,000 events across 84 settings. Its mean conditional character contrast is 1.997448, while raw unconditional output fidelity ranges from 89.17% to 99.84%. The conditional contrast excludes other modes: a high contrast alone does not bound the missing mass. The [exact three-qubit twin and falsification boundary](../ascella-sim-twin-falsification/README.md) show that an associative quantum circuit reproduces the encoded sign observable.
- The [Ascella two-photon associator experiment](../../../results/quandela/runs/2026-10-29T192905Z-qpu_ascella-ascella_two_photon_associator-job-00/analysis.json) reports encoded-arm contrast 1.7237 with a reported standard error 0.0101 and an associative-control contrast -0.0064 with reported standard error 0.0107. The interpretation and the quoted errors retain their selected-event and noise-model assumptions. Operator composition itself is associative; the contrast compares two programmed operators derived from the algebraic sign table.
- The [Ascella target-slot job](../../../results/quandela/runs/2026-10-30T165953Z-qpu_ascella-ascella_predecessor-current-schema/results.json) returns all eight iterations and passes the case's circuit and input identity checks. Its [descriptive common and reversal norms](../ascella-predecessor-admission/current-source-qpu.json) are about 0.01099 and 0.01016. No sampling-contract confidence claim or physical predecessor attribution is admitted.
- The [Belenos single-chip teleportation rehearsal](../../../results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00/results.json) reaches its shot limits with zero accepted three-click events in all six settings. Its verdict is inconclusive; accepted-state fidelity is undefined. The [cross-device design](../../design/ascella-belenos-entanglement-teleportation.md) records that a physical Ascella–Belenos carrier path has not been established.

The separate 21-pair two-photon hardware atlas job `4c4f0273-6e69-4b52-af92-550a5e4356d8` is [canceled with zero shots](../../../results/quandela/cases/ascella_two_photon_character/job-01/results.json). Its [job-specific cancellation authority](../../../results/quandela/cases/ascella_two_photon_character/job-01/cancellation-authority.json) records the owner's direction. A replacement needs a separate case; the simulator atlas supplies no hardware result.

## A5 coefficient and spectral decomposition

For a doubly pure A5 element `y=(p,q)`, define `z_k=p_k+i q_k`, `u=(z_1,...,z_7)`, `mu=z_8`, `v=(z_9,...,z_15)`, and the complex-bilinear invariants

```
U = u.u,  V = v.v,  W = u.v
Q = U + mu^2 + V,  Delta = U V - W^2,  G = Q^2 - 4 Delta.
```

The [rank-strata record](../a5-zero-divisor-strata/README.md) gives `nullity_R(L_y)=28-2 rank_C(C_z)` and

```
chi_C(lambda) = lambda (lambda^2 + Q)^3
                (lambda^4 + 2 Q lambda^2 + G)^2.
```

The quartic contributes three independent coefficient terms: `1`, `2Q` and `G`. The equalities `Q=G=0` alone do not determine the kernel dimension. The [exact replay](replay.py) computes multiplication with `cd_core`, checks matrix ranks independently with FLINT and SymPy, and evaluates the invariants; these are four finite witnesses, not a new classification theorem.

| A5 input | Q | Delta | G | Nullity of L_y | Squared singular values and multiplicities |
| --- | ---: | ---: | ---: | ---: | --- |
| `e1 + e9` | 2 | 0 | 4 | 0 | `2` (32) |
| `e1 + e10` | 2 | 1 | 0 | 8 | `0` (8), `2` (16), `4` (8) |
| `e1 + e18` | 0 | 0 | 0 | 12 | `0` (12), `2` (8), `4` (12) |
| `e1 - e10 + e18 + e25` | 0 | 0 | 0 | 16 | `0` (16), `4` (8), `8` (4), `16` (4) |

Both last rows give `chi_C(lambda)=lambda^15`, but the nullity identity gives
`rank_C(C_z)=8` and `6`, respectively. The characteristic polynomial counts
algebraic multiplicity and does not determine the kernel dimension of these
complex skew matrices. Rank minors or equivalent kernel checks retain the
information that the polynomial loses.

The [spectrum replay](spectrum.py) computes the multiplicities from `L_y^T L_y`. For `y=sum_i c_i e_i` and any basis input `e_j`, XOR multiplication sends each coefficient to a distinct output coordinate, so

```
||L_y e_j||^2 = sum_i c_i^2.
```

For an LCU herald implementing `L_y / alpha`, with `alpha=sum_i |c_i|`, every basis input has ideal success probability `sum_i c_i^2 / alpha^2`. In particular, both `e1+e9` (nullity 0) and `e1+e10` (nullity 8) give probability 1/2 on every basis input. A basis-only success survey cannot distinguish these two kernels. Coherent kernel vectors, bright superposition controls and phase-sensitive sign mutations are necessary to test the distinction. This is an ideal operator identity, not a calibrated device prediction.

## A5 computation frontier

The separate A5 attachment worktree, branch `geometry/a5-kernel-attachments` at commit `da8e95994f24d8c7b0c508861e714c6883f6f6cd`, has local edits in its producer and compute runbook; this note reads its retained `docs/evidence/a5-kernel-attachments/README.md` and does not treat those edits as a finished result. That record reports 33 nullity-changing incidence rows and a structural partner-purity argument; its Rees-fiber result completes eight nullity-16 incidences and times out on ten modular-fiber rows. It explicitly leaves real fibers and attaching maps unresolved. A larger compute budget alone does not establish those missing objects.

## Math-source connection and bounded next cases

The local `openai/math` checkout is at `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`. Its dimension-six manuscript claims exclusion of four mutually unbiased bases under a specified binary64 computation, while its [Lean scope](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/266.md) explicitly states a weaker five-basis bound. The repository already records the three product bases and the relevant [transition-conformance design](../../design/quantum-experiment-conformance.md). The exact replay here independently checks all six pairwise overlap matrices and detects a qutrit-phase mutation; it does not replay or prove the manuscript's upper bound.

The following are design candidates, not approved submissions:

1. **A5 kernel-sensitive encoding.** Use exact kernel and bright superpositions for the four witnesses, compare the heralded LCU probabilities and a sign mutation, and retain the unconditional herald rate. A5 has 32 algebra basis coordinates; neither a 12-mode Ascella nor a 24-mode Belenos single-photon encoding directly holds all 32. A concrete compression, multi-photon encoding or five-qubit circuit needs an exact operator map and resource budget before hardware selection.
2. **Target-slot drift discrimination.** Develop the eight-target predecessor-label sequence `A,B,B,A,B,A,A,B`, randomized repetitions, target-sensitive references and a carryover model. The signed contrast cancels constant, linear and quadratic drift in equally spaced observation indices. Provider-supported physical chronology and actual timing remain separate requirements; a changed schedule is a new case.
3. **Atlas acceptance accounting.** Reanalyze the retained 21-pair data with unconditional predicted-mode probability, excluded-mode mass and conditional contrast reported together. Use the same declared denominators and a simultaneous uncertainty policy before comparing settings. Hardware follow-up needs a decision margin and a power and cost calculation rather than selecting the lowest observed-fidelity settings after the fact.

## Replay

With system Python selected as `PYTHON`, the project TLS setting and the recorded two-worker, single-BLAS-thread limits, run `"$PYTHON" docs/evidence/a5-photonic-crosschecks/replay.py --check` and `"$PYTHON" docs/evidence/a5-photonic-crosschecks/spectrum.py --check`. The records bind the producer and `cd_core` source digests. The mutation removes the qutrit phase and must fail the exact basis-overlap check.
