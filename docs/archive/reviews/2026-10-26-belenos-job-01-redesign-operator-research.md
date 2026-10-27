# Operator research: job-01 redesign questions

This note records the operator's own reading on the questions of
the consult brief (`2026-10-26-belenos-job-01-redesign-consult-goal.md`). It was written in parallel with the Codex
consult and without access to it.

**Superseded in part.** Section 1's primary bound at the intrinsic efficiency budget 1/18 does not survive review.
The classical device replaces everything from the input to the receiver's detector, so its budget is the end-to-end
acceptance per attempt, about 3e-6 in the job-00 model. That puts the bound at 3/4 or more, as the consult found.
The [disposition](2026-10-26-belenos-job-01-redesign-disposition.md) records the outcome.

## 1. Multiphoton contamination

**Source (verified).** Specht et al. 2011, "A Single-Atom Quantum Memory", arXiv:1103.1528, supplement section
"Classical memories and coherent input pulses", Eqs. 1-3: a measure-and-prepare (intercept-resend) memory reaches
F_MP(N) = (N+1)/(N+2) on N identical copies (Massar and Popescu). For a photon-number distribution p(N), the
benchmark is the p(N)-weighted average over N >= 1. The same section notes that a classical memory can "simulate
non-unity efficiencies": it emits only when the input photon number is high.

**Source (verified).** Gündoğan et al. 2012, "Quantum Storage of a Photonic Polarization Qubit in a Solid",
arXiv:1201.4149, Eq. 1 and Appendix A, Eqs. A2-A3. The classical device answers only for N >= N_min + 1, and with
probability gamma at N_min. N_min and gamma are fixed so that the device's efficiency equals the measured memory
efficiency eta_M. The benchmark is therefore a function of the observed efficiency, and it rises toward 1 as the
efficiency falls.

**Consequence for job-01 (inferred, computed).**
- Free postselection, the model of `qd_classical_benchmark._free_postselection_bound`, is the limit eta -> 0. Any
  multicopy share then gives the multicopy optimum, so (1 - c) B + c is no bound under that model.
- The literature's repair is the efficiency constraint: the competitor must match the experiment's absolute
  acceptance per input attempt, eta.
- With a two-copy share p_m of the input source, given emission, the constrained bound for eta > p_m is
  B(eta) = [p_m * 3/4 + (eta - p_m) * 2/3] / eta, and 3/4 for eta <= p_m. Computed values:

  | p_m | eta = 1/18 | eta = 1/36 | eta = 1/90 | eta = 0.0055 |
  |---|---|---|---|---|
  | 0.0055 | 0.6749 | 0.6832 | 0.7079 | 0.75 |
  | 0.011 | 0.6832 | 0.6997 | 0.7492 | 0.75 |

- The case turns on which losses the competitor may exploit. If the efficiency budget is the protocol's intrinsic
  1/18 (Ralph CNOT 1/9 times the analyzer's 1/2), the correction is below 0.01. If chip transmission losses count as
  well (Transmittance 5.5 % at the anchor read), eta falls below p_m and B reaches 3/4. F* would then have to exceed
  0.77 merely for decision power.
- The memory literature separates device efficiency, which the competitor may simulate, from detector efficiency,
  which it may not (Specht 2011, supplement "Definition of the storage efficiency" and "Photon detection
  efficiency"). The single-chip rehearsal has no such separation in the record: the service publishes one
  Transmittance figure and per-mode `t_out`, so the split between on-chip loss and detection loss is not observed.
- Only extra photons on the input source q carry input copies. An extra photon on a or b belongs to the resource the
  competitor replaces, and gives it no information about the input. So c (or p_m) is the q-source share alone,
  about 0.0055 at g2 1.1 % in Perceval's source model, not the 0.014 to 0.025 accepted share over all three sources.

**Recommendation (inferred).** Name the assumption, and also report the constrained bound at two efficiency budgets:
- the intrinsic 1/18, the primary bound under the preregistered assumption that chip and detection loss are not
  competitor-exploitable;
- the measured end-to-end acceptance, the worst case.

The verdict carries the first. The second is a preregistered secondary that states how much loss-exploiting
postselection would void the claim. The four-click `excess` rate cannot replace the attempt count: it measures
multiphoton occupation after loss, not the input copy number.

## 2. Input labels and per-input circuits

**Repository source (verified).** The design's Decision statistics section states that input-label access and a
changing channel each void the single-channel benchmark.

**Finding (inferred).** On one programmable chip, the preparation is part of each iteration's compiled unitary. The
"channel" from q to b is never physically separated from the preparation, and each iteration is compiled anew. No
iteration order, randomized or interleaved, hides the input from a device whose circuit encodes the input. The
six-state benchmark therefore applies only under a device model: the realized operation factorizes as an
input-specific preparation followed by one input-independent channel (Ralph CNOT, analyzer, receiver rotation). That
is what C1 local conformance means here. A changing channel across iterations violates the model, and so does a
compilation that depends on the preparation. The honest claim is conditional on that factorization, which the
service's per-iteration re-transpilation (`docs/notes/quandela/strategy.md` section 2) leaves untested.

## 3. Dependence

**Sources (verified by abstract).** Gill 2003, "Time, finite statistics, and Bell's fifth position",
arXiv:quant-ph/0301059; Zhang, Glancy and Knill 2011, arXiv:1108.2468 (PRA 84, 062118); Bierhorst, arXiv:1312.2999.
Under a null whose per-trial conditional success probability given the past is at most B, the centered success count
is a supermartingale. Azuma-Hoeffding then gives the same tail exp(-2 n t^2) as Hoeffding: memory in the null does
not invalidate the radius, provided the per-trial bound holds conditionally.

**Consequence (inferred).** The per-trial conditional bound needs the input to be unknown to the null at each trial.
Section 2 shows that a memoryful device could know it, so dependence reduces to the device-model assumption of
section 2: under that factorization, a fixed realized channel per block, Hoeffding (or Azuma) is valid for the
average fidelity of the realized channels. Replicate blocks then add a drift diagnostic, not validity. The reviewer's
perfect-correlation counterexample presupposes a null that conditions on the input, which the device model excludes.

## 4. Attempt box

**Argument (verified by inspection of the solver's objective).** For a fixed accepted instrument, the pooled
fidelity is sum_j pi_j s_j F_j / sum_j pi_j s_j, linear-fractional in the priors pi_j, and therefore quasi-linear.
The maximum over strategies of quasi-linear functions is quasi-convex. A quasi-convex function on a box attains its
maximum at a vertex, so 64 vertex solves give the exact maximum of `attempts_benchmark` over the box.

**Computed.** At job-00's modeled sample probabilities the bound is 0.6937 at r = 1, 0.7054 at 1.05, 0.7167 at 1.1,
0.7383 at 1.2 and 0.7936 at 1.5. The relative attempt profile moves by up to 9 % across the five noise variants. r is
model-internal, because the record describes the last published calibration and not the chip, so a preregistered
break-even r should accompany the verdict.

## 5. Feasibility (computed)

Under the redesign (attempt box r = 1.1, 0.02 allowance, 10 s of compilation per iteration), the lowest F* that fits
300 s is 0.82 with 12 iterations and 0.80 with 6. Replacing the (1 - c) B + c term with the efficiency-constrained
bound at 1/18 (p_m = 0.0055) moves B by +0.0083 instead of +0.0072, leaving the floor unchanged. At the end-to-end
efficiency, B = 3/4 and the floor rises above 0.86.

## Sources

- Specht et al., arXiv:1103.1528 (read: supplement, classical memories).
- Gündoğan et al., arXiv:1201.4149 (read: Eq. 1, Appendix A).
- Gill, arXiv:quant-ph/0301059; Zhang, Glancy and Knill, arXiv:1108.2468; Bierhorst, arXiv:1312.2999 (abstracts and
  search summaries only; derivations not read).
- Massar and Popescu 1995 (cited through Specht's Eq. 1; not opened).
